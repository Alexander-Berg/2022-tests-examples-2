import asyncio
import pytest
from noc.grad.grad.lib.functions import HostResolver


def _arun(fn_obj):
    return asyncio.get_event_loop().run_until_complete(fn_obj)


def test_hosts():
    resolver = HostResolver()
    assert _arun(resolver.resolve("host1")) == [("host1", "host1")]
    assert _arun(resolver.resolve("host1:123")) == [("host1", "host1:123")]
    assert _arun(resolver.resolve("host1/10.0.0.1")) == [("host1", "10.0.0.1")]
    assert _arun(resolver.resolve("host1/10.0.0.1:123")) == [("host1", "10.0.0.1:123")]
    with pytest.raises(Exception):
        _arun(resolver.resolve("host1:124/10.0.0.1:123"))


def test_filter():
    resolver = HostResolver()
    assert _arun(resolver.resolve("host1")) == [("host1", "host1")]
    assert _arun(resolver.resolve(["host1", "host2", "host3"])) == [
        ("host1", "host1"),
        ("host2", "host2"),
        ("host3", "host3"),
    ]


def test_handler_dups():
    def handler(host_filter):
        return [(x, x) for x in host_filter]

    resolver = HostResolver()
    resolver.register_handler("olo", handler)
    # same
    resolver.register_handler("olo", handler)
    with pytest.raises(Exception):
        resolver.register_handler("olo", print)


def test_handler():
    def handler(host_filter):
        return [(x, x) for x in host_filter]

    async def ahandler(host_filter):
        return [(x.upper(), x.upper()) for x in host_filter]

    resolver = HostResolver()
    resolver.register_handler("olo", handler)
    resolver.register_handler("lol", ahandler)

    assert _arun(resolver.resolve("olo%abc")) == [("a", "a"), ("b", "b"), ("c", "c")]
    assert _arun(resolver.resolve("lol%abc")) == [("A", "A"), ("B", "B"), ("C", "C")]
    assert _arun(resolver.resolve(["telaviv/garage.telaviv.sdc.yandex.net"])) == [
        ("telaviv", "garage.telaviv.sdc.yandex.net")
    ]
    assert _arun(resolver.resolve(["a", ["b", "c"]])) == [("a", "a"), ("b", "b"), ("c", "c")]
