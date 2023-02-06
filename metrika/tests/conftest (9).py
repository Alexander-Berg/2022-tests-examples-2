import logging
import os
import pytest
import yatest.common
import yatest.common.runtime_java

from kikimr.public.sdk.python.persqueue import grpc_pq_streaming_api as pqlib

import metrika.pylib.structures.dotdict as mdd
import metrika.pylib.clickhouse as mtch


class Columns(object):
    _columns = []
    _select_columns = []
    _group_columns = []
    _filter_out_columns = []

    @property
    def columns(self):
        return ' '.join(self._columns)

    @property
    def group_columns(self):
        return ' '.join(self._group_columns)

    @property
    def filter_out_columns(self):
        return ' '.join(self._filter_out_columns)

    @property
    def select_columns(self):
        return ', '.join(self._select_columns)

    @property
    def order_by_columns(self):
        return ', '.join(self._columns)


@pytest.fixture(scope="session")
def tab_crunch():
    return [
        yatest.common.runtime_java.get_java_path(yatest.common.binary_path("metrika/admin/jdk")),
        "-jar", yatest.common.build_path("metrika/qa/tab-crunch/tab-crunch-diff-tool.jar"),
    ]


def get_directories(out_root):
    dir_config = mdd.DotDict()

    TEST_OUT_ROOT = str(yatest.common.output_path(out_root))

    dir_config.out_root = TEST_OUT_ROOT
    dir_config.cache_dir = os.path.join(TEST_OUT_ROOT, "cache")
    dir_config.sender_base_dir = os.path.join(TEST_OUT_ROOT, "sender")
    dir_config.sender_tmp_dir = os.path.join(TEST_OUT_ROOT, "sender/tmp")
    dir_config.solomon_base_dir = os.path.join(TEST_OUT_ROOT, "solomon")
    dir_config.solomon_tmp_dir = os.path.join(TEST_OUT_ROOT, "solomon/tmp")
    dir_config.canon_dir = os.path.join(TEST_OUT_ROOT, "canon")
    dir_config.report_dir = os.path.join(TEST_OUT_ROOT, "reports")

    os.environ["CACHE_DIR"] = dir_config.cache_dir
    os.environ["SENDER_BASE_DIR"] = dir_config.sender_base_dir
    os.environ["SENDER_TMP_DIR"] = dir_config.sender_tmp_dir
    os.environ["SOLOMON_BASE_DIR"] = dir_config.solomon_base_dir
    os.environ["SOLOMON_TMP_DIR"] = dir_config.solomon_tmp_dir

    directories_for_create = (
        dir_config.cache_dir,
        dir_config.sender_tmp_dir,
        dir_config.solomon_tmp_dir,
        dir_config.canon_dir,
        dir_config.report_dir,
    )
    for directory in directories_for_create:
        if not os.path.isdir(directory):
            if os.path.exists(directory):
                raise Exception("%s exists but is not directory" % directory)
            else:
                os.makedirs(directory)

    return dir_config


@pytest.fixture
def mtmobproxy_simple_directories():
    yield get_directories("out")


@pytest.fixture
def qloud_simple_directories():
    yield get_directories("out_qloud")


@pytest.fixture
def mtmobproxy_columns():
    cols = Columns()
    cols._columns = (
        "ServerName",
        "DC",
        "RequestDate",
        "RequestDateTime",
        "ClientIP6",
        "VirtualHost",
        "Path",
        "BasePath",
        "Params.Keys",
        "Params.Values",
        "Code",
        "RequestLengthBytes",
        "FullRequestTime",
        "UpstreamResponseTime",
        "IsUpstreamRequest",
        "SSLHanshakeTime",
        "IsKeepalive",
        "StringHash",
        "HTTPMethod",
    )

    cols._select_columns = cols._columns

    cols._group_columns = (
        "RequestDateTime",
        "VirtualHost",
        "Path",
        "Code",
        "RequestLengthBytes",
        "HTTPMethod",
    )

    cols._filter_out_columns = (
        "ServerName",
        "StringHash",
    )

    yield cols


@pytest.fixture
def qloud_columns():
    cols = Columns()
    cols._columns = (
        "RequestDateTime",
        "ClientIP6",
        "VirtualHost",
        "Path",
        "BasePath",
        "Params.Keys",
        "Params.Values",
        "Code",
        "FullRequestTime",
        "UpstreamResponseTime",
        "Container",
    )

    cols._select_columns = (
        "RequestDate",
        "RequestDateTime",
        "ClientIP6",
        "ClientIP6String",
        "VirtualHost",
        "Path",
        "BasePath",
        "Params.Keys",
        "Params.Values",
        "Code",
        "FullRequestTime",
        "UpstreamResponseTime",
        "Container",
    )

    cols._group_columns = (
        "RequestDateTime",
        "VirtualHost",
        "Path",
        "Code",
        "FullRequestTime",
    )

    yield cols


@pytest.fixture(scope="session")
def clickhouse_client():
    client = mtch.ClickHouse(host=os.environ["RECIPE_CLICKHOUSE_HOST"], port=int(os.environ["RECIPE_CLICKHOUSE_HTTP_PORT"]))
    yield client


@pytest.fixture
def logbroker_server():
    api = pqlib.PQStreamingAPI("localhost", int(os.getenv('LOGBROKER_PORT')))
    api.start().result(timeout=5)
    yield api
    api.stop()


@pytest.fixture
def logbroker_qloud_data(logbroker_server):
    configurator = pqlib.ProducerConfigurator("qloud", "test_src")
    writer = logbroker_server.create_producer(configurator)  # type: pqlib.PQStreamingProducer
    result = writer.start().result(timeout=5)
    assert result.HasField("init")

    log_path = str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/qloud.log.gz"))

    with open(log_path, 'rb') as f:
        for i, b in enumerate((3062, 6932, 3275), start=1):
            data = f.read(b)
            write_res = writer.write(i, data).result(timeout=5)
            assert write_res.HasField("ack")
            logging.debug("Writed successfull, got response: %s", str(write_res))

        data = f.read()
        write_res = writer.write(i+1, data).result(timeout=5)
        assert write_res.HasField("ack")
        logging.debug("Writed successfull, got response: %s", str(write_res))

    yield logbroker_server
