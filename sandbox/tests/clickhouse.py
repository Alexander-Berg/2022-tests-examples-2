import os
import socket
import tempfile

import pytest
import responses

from sandbox.deploy import base
from sandbox.deploy import utils
from sandbox.deploy import clickhouse


CONTOUR_KEY = 1


@pytest.fixture
def mocked_responses():
    # When set to True, this option shadows tracebacks, giving little to no information as to what has failed and why
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture(scope="session")
def tag():
    return clickhouse.ctag_for_key(CONTOUR_KEY)


@pytest.fixture(scope="session")
def shard_tag_prefix(tag):
    return "{}_s".format(tag)


@pytest.fixture(scope="session")
def ch_fqdns():
    return ["sandbox-clickhouse{:02}.search.yandex.net".format(i) for i in (5, 93, 45, 7)]


@pytest.fixture(scope="session")
def zk_fqdns():
    return ["sandbox-zk{:02}.search.yandex.net".format(i) for i in (1, 3, 5, 7, 9)]


@pytest.fixture(scope="session")
def host2shard(ch_fqdns):
    return {fqdn: i // 2 for i, fqdn in enumerate(ch_fqdns)}


@pytest.fixture
def clickhouse_hosts(ch_fqdns, host2shard, mocked_responses, tag, shard_tag_prefix):
    mocked_responses.add(
        responses.GET, os.path.join(utils.TAG2HOSTS_URL_BASE, tag),
        body="\n".join(ch_fqdns)
    )

    for i, fqdn in enumerate(ch_fqdns):
        mocked_responses.add(
            responses.GET, os.path.join(utils.HOST_TAGS_URL_BASE, fqdn),
            body="\n".join((tag, "{}{}".format(shard_tag_prefix, host2shard[fqdn])))
        )

    return ch_fqdns


@pytest.fixture
def zk_hosts(zk_fqdns, mocked_responses):
    mocked_responses.add(
        responses.GET, os.path.join(utils.TAG2HOSTS_URL_BASE, clickhouse.ZOOKEEPER_CTAG),
        body="\n".join(zk_fqdns)
    )

    return zk_fqdns


@pytest.fixture
def current_replica(clickhouse_hosts):
    return clickhouse_hosts[1]


@pytest.fixture
def servant(monkeypatch, tag, clickhouse_hosts, zk_hosts, current_replica):
    monkeypatch.setitem(
        clickhouse.ClickHouse.settings, CONTOUR_KEY,
        clickhouse.ClusterSettings(
            ctag=tag,
            hosts_expr=base.ctag(tag),
            default_db=utils.prefix_for_key(CONTOUR_KEY),
            cluster=utils.prefix_for_key(CONTOUR_KEY),
        )
    )

    with tempfile.NamedTemporaryFile(bufsize=0) as fileobj:
        fileobj.write("blahblah")
        monkeypatch.setattr(clickhouse.ClickHouse, "SU_PASSWORD_PATH", fileobj.name)
        servant = clickhouse.ClickHouse(
            CONTOUR_KEY, host_platform="", groups=set(), layout=None,
            dc="", solomon_descr="", tvminfo=None
        )
        yield servant


class TestClickHouse(object):
    def test__config_generation(self, servant, current_replica, monkeypatch):
        monkeypatch.setattr(socket, "getfqdn", lambda: current_replica)
        return servant.make_config()

    def test__users_generation(self, servant):
        return servant.make_users()

    def test__client_config_generation(self, servant):
        return servant.make_client_config()
