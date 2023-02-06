import os
import time
import random
import string
import signal
import shutil
import logging
import textwrap
import datetime as dt
import itertools as it
import subprocess as sp
import xml.dom.minidom

import yatest.common

import pytest
import requests
import kazoo.client

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.database.clickhouse import fields as orm_fields
from sandbox.yasandbox.database.clickhouse import database as orm_database

from sandbox.services.modules.statistics_processor.schemas import clickhouse as orm_schemas


ARCHIVE_NAME = "clickhouse-common-static_18.14.13_amd64"
BINARY_NAME = "clickhouse"
CONFIG_XML_NAME = "config.xml"
USERS_XML_NAME = "users.xml"
ZK_PORT_VAR = "RECIPE_ZK_PORT"


class ClickHouse(object):
    CH_CONNECT_ATTEMPTS = 100
    CH_ATTEMPT_TIMEOUT = 0.1

    def __init__(
        self, binary_path, base_config_xml, base_users_xml,
        template, host, tcp_port, http_port, interserver_http_port, shard_no
    ):
        self.binary_path = binary_path
        self.base_config_xml = base_config_xml
        self.base_users_xml = base_users_xml

        self.template = template
        self.host = host
        self.tcp_port = tcp_port
        self.http_port = http_port
        self.interserver_http_port = interserver_http_port
        self.shard_no = shard_no

        self.installation_dir = None
        self.base_config = None
        self.pid = None

    def __repr__(self):
        return "<{} on {}:{} (PID {})>".format(
            type(self).__name__, self.host, self.http_port, self.pid
        )

    def install(self):
        self.installation_dir = yatest.common.runtime.work_path("clickhouse_{}".format(self.http_port))
        os.mkdir(self.installation_dir)

        def copy_file(file_path):
            dst = os.path.join(self.installation_dir, os.path.basename(file_path))
            shutil.copyfile(file_path, dst)
            return dst

        def internal_dir(dirname):
            p = os.path.join(self.installation_dir, dirname)
            os.mkdir(p)
            return p

        self.base_config = copy_file(self.base_config_xml)
        copy_file(self.base_users_xml)

        conf_d_dir = internal_dir("conf.d")
        config = self.template.format(
            log_path=os.path.join(self.installation_dir, "clickhouse.log"),
            error_log_path=os.path.join(self.installation_dir, "clickhouse.err.log"),

            http_port=self.http_port,
            tcp_port=self.tcp_port,
            interserver_http_port=self.interserver_http_port,

            path=internal_dir("db"),
            tmp_path=internal_dir("tmp"),
            user_files_path=internal_dir("user_files"),
            format_schema_path=internal_dir("format_schema"),

            shard_name="shard{}".format(self.shard_no),
            replica_name="{}_{}".format(self.host, self.tcp_port),
        )

        config_path = os.path.join(conf_d_dir, "override.xml")
        with open(config_path, "w") as cfg:
            cfg.write(prettify_xml(config))

    def start(self):
        proc = sp.Popen(
            [
                self.binary_path,
                "server",
                "--config-file",
                self.base_config
            ]
        )
        self.pid = proc.pid
        logging.debug("%s process started", self)

        for _ in xrange(self.CH_CONNECT_ATTEMPTS):
            try:
                requests.get("http://{}:{}".format(self.host, self.http_port)).raise_for_status()
                return proc.pid
            except requests.ConnectionError:
                time.sleep(self.CH_ATTEMPT_TIMEOUT)

        raise RuntimeError(
            "{} failed to get up in {}s".format(self, self.CH_ATTEMPT_TIMEOUT * self.CH_CONNECT_ATTEMPTS)
        )

    def stop(self):
        try:
            os.kill(self.pid, signal.SIGTERM)
            for _ in xrange(self.CH_CONNECT_ATTEMPTS):
                try:
                    requests.get("http://{}:{}".format(self.host, self.http_port)).raise_for_status()
                    time.sleep(self.CH_ATTEMPT_TIMEOUT)
                except requests.ConnectionError:
                    return

            logging.error(
                "%s still responds after %ss, sending SIGKILL",
                self, self.CH_ATTEMPT_TIMEOUT * self.CH_CONNECT_ATTEMPTS
            )
            os.kill(self.pid, signal.SIGKILL)

        except OSError:
            logging.error("Unable to kill %s", self)

    def uninstall(self):
        shutil.rmtree(self.installation_dir)


class ClickHouseCluster(object):
    TEMPLATE = textwrap.dedent("""
        <yandex>
            <logger>
                <level>trace</level>
                <log>{{log_path}}</log>
                <errorlog>{{error_log_path}}</errorlog>
                <size>1000M</size>
                <count>10</count>
            </logger>

            <listen_host>::</listen_host>
            <http_port>{{http_port}}</http_port>
            <tcp_port>{{tcp_port}}</tcp_port>
            <interserver_http_port>{{interserver_http_port}}</interserver_http_port>

            <path>{{path}}</path>
            <tmp_path>{{tmp_path}}</tmp_path>
            <user_files_path>{{user_files_path}}</user_files_path>
            <format_schema_path>{{format_schema_path}}</format_schema_path>

            <macros>
                <shard>{{shard_name}}</shard>
                <replica>{{replica_name}}</replica>
            </macros>

            <default_database>{default_database}</default_database>
            <remote_servers>
                <{cluster_name}>
                    {shards_block}
                </{cluster_name}>
            </remote_servers>

            <zookeeper>
                {zk_blocks}
            </zookeeper>
        </yandex>
    """)

    def __init__(
        self, port_manager, binary_path, base_config_xml, base_users_xml,
        zk_host, zk_port, default_db_name, cluster_name, shard_count, replica_count
    ):
        self.pm = port_manager
        self.binary_path = binary_path
        self.base_config_xml = base_config_xml
        self.base_users_xml = base_users_xml

        self.zk_host = zk_host
        self.zk_port = zk_port
        self.default_db_name = default_db_name
        self.cluster_name = cluster_name
        self.shard_count = shard_count
        self.replica_count = replica_count

        self.__reserved_ports = []
        self.instances = []

    def __repr__(self):
        return "<{} ({})>".format(
            type(self).__name__, self.instances
        )

    @staticmethod
    def make_replica_block(host, port):
        return textwrap.dedent("""
            <replica>
                <host>{}</host>
                <port>{}</port>
            </replica>
        """.strip().format(host, port))

    @staticmethod
    def make_shard_block(data):
        return textwrap.dedent("""
            <shard>
                <internal_replication>true</internal_replication>
                {}
            </shard>
        """.strip().format("\n".join(it.starmap(ClickHouseCluster.make_replica_block, data))))

    @staticmethod
    def make_zk_block(host, port):
        return textwrap.dedent("""
            <node>
                <host>{}</host>
                <port>{}</port>
            </node>
        """.strip().format(host, port))

    def install(self):
        def n_ports(num):
            return [self.pm.get_port() for _ in xrange(num)]

        total_hosts = self.shard_count * self.replica_count
        tcp_ports, http_ports, interserver_http_ports = map(n_ports, (total_hosts,) * 3)
        self.__reserved_ports = tcp_ports + http_ports + interserver_http_ports

        clickhouse_hosts = [
            ("localhost", tcp_port)
            for tcp_port in tcp_ports
        ]

        # every replica_count hosts are grouped into a shard
        shard = {
            clickhouse_hosts[i]: i / self.replica_count
            for i in xrange(total_hosts)
        }

        zk_blocks = "\n".join(it.starmap(
            self.make_zk_block,
            (("localhost", self.zk_port),)
        ))

        # every shard block has replica_count replica hosts
        shards_block = "\n".join(map(
            self.make_shard_block,
            (
                clickhouse_hosts[self.replica_count * i: self.replica_count * (i + 1)]
                for i in xrange(self.shard_count)
            )
        ))

        common_template = self.TEMPLATE.format(
            default_database=self.default_db_name,
            shards_block=shards_block,
            zk_blocks=zk_blocks,
            cluster_name=self.cluster_name,
        )

        self.instances = [
            ClickHouse(
                self.binary_path, self.base_config_xml, self.base_users_xml,
                common_template, host, tcp_port, http_port, interserver_http_port, shard[(host, tcp_port)]
            )
            for ((host, tcp_port), http_port, interserver_http_port) in zip(
                clickhouse_hosts, http_ports, interserver_http_ports
            )
        ]
        map(ClickHouse.install, self.instances)

    def start(self):
        map(ClickHouse.start, self.instances)

    def stop(self):
        map(ClickHouse.stop, self.instances)

    def wipe_zk_data(self):
        logger = logging.getLogger("kazoo")
        logger.setLevel(logging.INFO)
        clt = kazoo.client.KazooClient(
            "{}:{}".format(self.zk_host, self.zk_port), logger=logger
        )

        clt.start()
        clt.delete("/clickhouse", recursive=True)
        clt.stop()

    def uninstall(self):
        self.stop()
        self.wipe_zk_data()

        mapping.AutoEnum.drop_collection()

        map(ClickHouse.uninstall, self.instances)
        map(self.pm.release_port, self.__reserved_ports)


def prettify_xml(config):
    indented = xml.dom.minidom.parseString(config).toprettyxml(indent=" " * 4, encoding="ascii")
    return "\n".join(line for line in indented.splitlines() if line.strip())


@pytest.fixture(scope="session")
def clickhouse_binary():
    arch_path = yatest.common.runtime.work_path("{}.tar.gz".format(ARCHIVE_NAME))
    sp.check_call(["tar", "-zxf", arch_path])
    bin_path = yatest.common.runtime.work_path(BINARY_NAME)
    os.chmod(bin_path, 0o777)
    return bin_path


@pytest.fixture(scope="session")
def clickhouse_base_config_xml(clickhouse_binary):
    return yatest.common.runtime.work_path(CONFIG_XML_NAME)


@pytest.fixture(scope="session")
def clickhouse_base_users_xml(clickhouse_binary):
    return yatest.common.runtime.work_path(USERS_XML_NAME)


@pytest.fixture(scope="session")
def zk_host():
    return "localhost"


@pytest.fixture(scope="session")
def zk_port():
    return os.environ[ZK_PORT_VAR]


@pytest.fixture(scope="session")
def default_db_name():
    return "test"


@pytest.fixture(scope="session")
def cluster_name():
    return "test_cluster"


@pytest.fixture(scope="session")
def mongo_connection(mongo_uri):
    mapping.ensure_connection(mongo_uri)


@pytest.fixture(scope="session")
def make_clickhouse_cluster(
    port_manager, zk_host, zk_port, default_db_name, cluster_name,
    clickhouse_binary, clickhouse_base_config_xml, clickhouse_base_users_xml
):
    def make_cluster(request, shard_count, replica_count):
        cluster = ClickHouseCluster(
            port_manager, clickhouse_binary, clickhouse_base_config_xml, clickhouse_base_users_xml,
            zk_host, zk_port, default_db_name, cluster_name, shard_count, replica_count
        )

        request.addfinalizer(cluster.uninstall)

        mapping.ensure_connection()

        cluster.install()
        cluster.start()
        return cluster

    return make_cluster


@pytest.fixture(scope="function")
def default_clickhouse_cluster(request, make_clickhouse_cluster, mongo_connection):
    return make_clickhouse_cluster(request, 2, 2)


def make_distributed_db(clickhouse_cluster, db_name, cluster_name, idx=None):
    if idx is None:
        instance = random.choice(clickhouse_cluster.instances)
    else:
        instance = clickhouse_cluster.instances[idx]

    connection_url = "http://{}:{}/".format(instance.host, instance.http_port)
    db = orm_database.DistributedDatabase(
        db_name,
        cluster_name,
        connection_url
    )
    db.create_database()

    return db


@pytest.fixture(scope="function")
def distributed_db(default_clickhouse_cluster, default_db_name, cluster_name):
    return make_distributed_db(default_clickhouse_cluster, default_db_name, cluster_name)


def test__cluster_is_up(default_clickhouse_cluster):
    instance = random.choice(default_clickhouse_cluster.instances)
    data = requests.get("http://{}:{}/?query=SELECT 1".format(instance.host, instance.http_port)).text.strip()
    assert int(data) == 1


def test__table_creation(distributed_db):
    model = random.choice(orm_schemas.SIGNAL_MODELS.values())
    distributed_db.create_table(model)

    for instance in distributed_db.instances:
        response = list(instance.select(
            "SELECT name FROM system.tables WHERE database = '{}'".format(distributed_db.db_name)
        ))
        assert len(response) == 2
        assert {_.name for _ in response} == {model.table_name(), model.underlying_table_name()}


@pytest.mark.xfail(run=False)
def test__auto_enums(distributed_db):
    model_class = orm_schemas.ApiUsage
    distributed_db.create_table(model_class)

    utcnow = dt.datetime.utcnow()
    distributed_db.insert([model_class(
        date=utcnow,
        timestamp=utcnow,
        login="black",
        quota=1
    )])

    colors = ("grey", "white")
    batch_sz = 10
    total_unique = 1 + len(colors) * batch_sz

    for color in colors:
        for quota in xrange(batch_sz):
            distributed_db.insert([model_class(
                date=utcnow,
                timestamp=utcnow,
                login="{}_{}".format(color, quota),
                quota=quota
            )])

    enum_field_name = "login"
    for instance in distributed_db.instances:
        for table_name in (model_class.table_name(), model_class.underlying_table_name()):
            query = instance.select(
                "DESCRIBE TABLE {}.{}".format(distributed_db.db_name, table_name)
            )
            enum_field_in_db = next(
                iter(filter(
                    lambda field: field.name == enum_field_name,
                    query
                )),
                None
            )
            enum_fields = orm_fields.AutoEnumField.parse_enum(enum_field_in_db.type)
            assert len(enum_fields.keys()) == total_unique, (instance.db_url, table_name, enum_field_in_db.type)

            full_name = ".".join((distributed_db.db_name, model_class.underlying_table_name(), enum_field_in_db.name))
            enum_state = mapping.AutoEnum.objects.with_id(full_name)
            assert enum_state.values == [name for name, _ in sorted(enum_fields.items())], full_name


def test__data_not_lost_on_replica_loss(default_clickhouse_cluster, default_db_name, cluster_name):
    db = make_distributed_db(default_clickhouse_cluster, default_db_name, cluster_name, idx=0)
    model_class = orm_schemas.QuotaMedian
    db.create_table(model_class)

    utcnow = dt.datetime.utcnow()
    db.insert([model_class(
        date=utcnow,
        timestamp=utcnow,
        purpose_tag="CORES0",
        median=1,
        ratio_median=1
    )])

    ch_instance = default_clickhouse_cluster.instances[1]
    ch_instance.stop()

    batch_sz = 30
    for i in xrange(batch_sz):
        db.insert([
            model_class(
                date=utcnow,
                timestamp=utcnow,
                purpose_tag="CORES_I{}{}".format(i, ch),
                median=i,
                ratio_median=i
            )
            for ch in string.ascii_uppercase
        ])

    ch_instance.start()

    # ensure that alters and inserts do not fail and no data is silently lost
    second_batch_sz = 10
    for i in xrange(second_batch_sz):
        db.insert([
            model_class(
                date=utcnow,
                timestamp=utcnow,
                purpose_tag="CORES_NEW_I{}{}".format(i, ch),
                median=123,
                ratio_median=123
            )
            for ch in string.ascii_uppercase
        ])

    total_rows = 0
    expected = 1 + (batch_sz + second_batch_sz) * len(string.ascii_uppercase)
    tries = 60
    for _ in xrange(tries):
        time.sleep(1)
        total_rows = int(db.raw("SELECT count() FROM {}.{}".format(db.db_name, model_class.table_name())))
        if total_rows == expected:
            return

    pytest.fail(
        "Data hasn't been fully distributed across the cluster in {} secs ({}/{})".format(
            tries, total_rows, expected
        )
    )
