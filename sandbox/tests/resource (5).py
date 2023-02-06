import pytest

from sandbox import common
from sandbox.common import patterns
from sandbox.yasandbox import controller as ctrl


def _create_client(name, tags=None, alive=True):
    tags = tags or []
    return ctrl.ResourceLinks.Client(
        host=name,
        tags=tags,
        storage="STORAGE" in tags,
        info={"system": {"fileserver": "http://" + name}},
        alive=alive
    )


TEST_CLIENTS = [
    _create_client("client_a"),
    _create_client("client_b"),
    _create_client("storage_a", ["STORAGE"]),
    _create_client("storage_b", ["STORAGE"]),
    _create_client("dead", alive=False),
]


class Host(patterns.NamedTuple):
    __slots__ = ("host", "state")
    __defs__ = ("", "OK")


class Res(patterns.NamedTuple):
    __slots__ = ("id", "task_id", "hosts_states", "path")
    __defs__ = (0, 0, (), "")


TEST_RESOURCES = [
    Res(1, task_id=123, hosts_states=[Host("client_a"), Host("client_b")], path="a/b/c"),
    Res(5, task_id=456, hosts_states=[Host("client_b", "MARK_TO_DELETE"), Host("storage_a")], path="d/e/f"),
    Res(10, task_id=789, hosts_states=[Host("dead")], path="g/h/i"),
]


@pytest.fixture()
def mocked_clients_and_sources(monkeypatch):

    def create_from_hosts(_):
        return {c.host: c for c in TEST_CLIENTS}

    def all_sources(_):
        return {rid: [h.host for h in r.hosts_states if h.state == "OK"] for rid, r in _._resources.iteritems()}

    monkeypatch.setattr(ctrl.ResourceLinks, "_clients", property(create_from_hosts))
    monkeypatch.setattr(ctrl.ResourceLinks, "all_sources", property(all_sources))


@pytest.mark.usefixtures("mocked_clients_and_sources")
class TestResourceLinks(object):

    @staticmethod
    def _make_sets(sources):
        sources = sources.copy()
        for rid in sources:
            sources[rid] = set(sources[rid])
        return sources

    def test__sources(self):
        rl = ctrl.ResourceLinks(TEST_RESOURCES)
        sources = self._make_sets(rl.sources)
        assert sources == {1: {"client_a", "client_b"}, 5: {"storage_a"}, 10: {"dead"}}

    def test__source_grouped(self):
        resources = [Res(id=1, hosts_states=[Host("storage_b"), Host("client_b"), Host("client_a"), Host("storage_a")])]
        for _ in range(10):
            rl = ctrl.ResourceLinks(resources)
            sources = rl.sources[1]
            assert set(sources[:2]) == {"storage_a", "storage_b"}  # storages first
            assert set(sources[2:]) == {"client_a", "client_b"}  # then clients

    def test__http(self):
        rl = ctrl.ResourceLinks(TEST_RESOURCES)
        http = self._make_sets(rl.http)
        assert http == {
            1: {"http://client_a/3/2/123/a/b/c", "http://client_b/3/2/123/a/b/c"},
            5: {"http://storage_a/6/5/456/d/e/f"},
            10: set(),
        }

    def test__rsync(self):
        rl = ctrl.ResourceLinks(TEST_RESOURCES)
        rsync = self._make_sets(rl.rsync)
        assert rsync == {
            1: {"rsync://client_a/sandbox-tasks/3/2/123/a/b/c", "rsync://client_b/sandbox-tasks/3/2/123/a/b/c"},
            5: {"rsync://storage_a/sandbox-tasks/6/5/456/d/e/f"},
            10: set(),
        }

    def test__proxy_configured(self, monkeypatch):
        AD = common.collections.AttrDict
        monkeypatch.setattr(
            common.config.Registry().client.fileserver, "proxy",
            AD(scheme=AD(http="http"), host="mock-proxy")
        )
        rl = ctrl.ResourceLinks(TEST_RESOURCES)
        assert rl.proxy == {1: "http://mock-proxy/1", 5: "http://mock-proxy/5", 10: "http://mock-proxy/10"}

    def test__proxy_not_configured(self, monkeypatch):
        monkeypatch.setattr(common.config.Registry().client.fileserver, "proxy", common.collections.AttrDict(host=None))

        resources = [
            Res(1, task_id=123, hosts_states=[Host("client_a")], path="a/b/c"),
            Res(5, task_id=456, hosts_states=[Host("client_b", "MARK_TO_DELETE"), Host("storage_a")], path="d/e/f"),
            Res(10, task_id=789, hosts_states=[Host("dead")], path="g/h/i"),
        ]

        rl = ctrl.ResourceLinks(resources)
        assert rl.proxy == {
            1: "http://client_a/3/2/123/a/b/c",
            5: "http://storage_a/6/5/456/d/e/f",
            10: "http://dead/9/8/789/g/h/i"
        }
