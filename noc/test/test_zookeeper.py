import os
import time
import logging
import uuid
import pytest

pytestmark = pytest.mark.skip
# https://archive.apache.org/dist/zookeeper/zookeeper-3.5.4-beta/zookeeper-3.5.4-beta.tar.gz
os.environ["ZOOKEEPER_PATH"] = "/home/gescheit/Downloads/zookeeper-3.5.4-beta"
os.environ["ZOOKEEPER_VERSION"] = "3.5.4-beta"


import kazoo.testing.harness
from kazoo.testing import KazooTestHarness
from kazoo.client import KazooClient
from kazoo.testing.common import ZookeeperCluster
from kazoo import python2atexit as atexit

from noc.grad.grad.lib.zk_functions import PartyHolder

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(filename)s:%(lineno)d %(threadName)s - %(funcName)s() - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)


# копия get_global_cluster для того чтобы поправить конфиг с таймаутами
def get_global_cluster():
    ZK_HOME = os.environ.get("ZOOKEEPER_PATH")
    ZK_CLASSPATH = os.environ.get("ZOOKEEPER_CLASSPATH")
    ZK_PORT_OFFSET = int(os.environ.get("ZOOKEEPER_PORT_OFFSET", 20000))
    ZK_CLUSTER_SIZE = int(os.environ.get("ZOOKEEPER_CLUSTER_SIZE", 3))
    ZK_VERSION = os.environ.get("ZOOKEEPER_VERSION")
    if '-' in ZK_VERSION:
        # Ignore pre-release markers like -alpha
        ZK_VERSION = ZK_VERSION.split('-')[0]
    ZK_VERSION = tuple([int(n) for n in ZK_VERSION.split('.')])

    ZK_OBSERVER_START_ID = int(os.environ.get("ZOOKEEPER_OBSERVER_START_ID", -1))

    assert ZK_HOME or ZK_CLASSPATH or ZK_VERSION, (
        "Either ZOOKEEPER_PATH or ZOOKEEPER_CLASSPATH or "
        "ZOOKEEPER_VERSION environment variable must be defined.\n"
        "For deb package installations this is /usr/share/java"
    )

    if ZK_VERSION >= (3, 5):
        additional_configuration_entries = [
            "4lw.commands.whitelist=*",
            "reconfigEnabled=true",
            "maxSessionTimeout=3000",  # закручиваем таймауты
            "tickTime=200",  # закручиваем таймауты
        ]
        # If defines, this sets the superuser password to "test"
        additional_java_system_properties = [
            "-Dzookeeper.DigestAuthenticationProvider.superDigest=" "super:D/InIHSb7yEEbrWz8b9l71RjZJU="
        ]
    else:
        additional_configuration_entries = []
        additional_java_system_properties = []
    CLUSTER = ZookeeperCluster(
        install_path=ZK_HOME,
        classpath=ZK_CLASSPATH,
        port_offset=ZK_PORT_OFFSET,
        size=ZK_CLUSTER_SIZE,
        observer_start_id=ZK_OBSERVER_START_ID,
        configuration_entries=additional_configuration_entries,
        java_system_properties=additional_java_system_properties,
    )
    atexit.register(lambda cluster: cluster.terminate(), CLUSTER)
    return CLUSTER


class PartyTest(KazooTestHarness):
    def setUp(self):
        new_cluster = get_global_cluster()
        kazoo.testing.harness.CLUSTER = new_cluster
        self.setup_zookeeper()
        self.tick_time = 200
        self.max_session_timeout = 500
        self.path = "/" + uuid.uuid4().hex

    def tearDown(self):
        try:
            self.teardown_zookeeper()
        except Exception:
            pass

    def _get_server(self, server_no):
        server = self.hosts.split("/")[0].split(",")[server_no] + "/" + self.hosts.split("/")[1]
        return server

    def _set_client(self, client):
        self._clients.append(client)

    def _get_client(self, server_no=-1, **kwargs):
        if server_no == -1:
            hosts = self.hosts
        else:
            hosts = self.hosts.split("/")[0].split(",")[server_no] + "/" + self.hosts.split("/")[1]
        c = KazooClient(hosts, **kwargs)
        self._set_client(c)
        if server_no != -1:
            assert len(c.hosts) == 1
        return c

    def _collect_party(self, party):
        res = {}
        for p in party:
            res[p.identifier] = p.get_comrades()
        _logger.debug("res %s", res)
        return res

    def _stop_cluster(self, server_no):
        _logger.debug("stop server %s", server_no)
        self.cluster[server_no].stop()

    def _start_cluster(self, server_no):
        _logger.debug("start server %s", server_no)
        self.cluster[server_no].run()

    def test_PartyHolder(self):
        clients = []
        party = []
        update_interval = 0.5
        for i in range(3):
            servers = self._get_server(i)
            p = PartyHolder(
                servers=servers, identifier="client_%s" % i, update_interval=update_interval, path=self.path
            )
            p.run()
            party.append(p)
            self._set_client(p.client)
            clients.append(p.client)

        time.sleep(1)

        assert self._collect_party(party) == {
            'client_0': ('client_0', 'client_1', 'client_2'),
            'client_1': ('client_0', 'client_1', 'client_2'),
            'client_2': ('client_0', 'client_1', 'client_2'),
        }

        self._stop_cluster(0)
        time.sleep(4)
        assert self._collect_party(party) == {
            'client_0': (),
            'client_1': ('client_1', 'client_2'),
            'client_2': ('client_1', 'client_2'),
        }

        self._start_cluster(0)
        time.sleep(4)
        assert self._collect_party(party) == {
            'client_0': ('client_0', 'client_1', 'client_2'),
            'client_1': ('client_0', 'client_1', 'client_2'),
            'client_2': ('client_0', 'client_1', 'client_2'),
        }

        party[1].client._connection._write_sock.close()

        time.sleep(6)
        assert self._collect_party(party) == {
            'client_0': ('client_0', 'client_1', 'client_2'),
            'client_1': ('client_0', 'client_1', 'client_2'),
            'client_2': ('client_0', 'client_1', 'client_2'),
        }
