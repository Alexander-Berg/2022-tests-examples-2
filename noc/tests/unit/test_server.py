from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest
from sanic_testing import TestManager

from noc.traffic.dns.safedns.dnsl3r.dnsl3r import models, server


def get_server(counters):
    query_params = {
        "query_dn": "nonexistent",
        "rr_type": "AAAA",
        "query_period": 5.0,
        "query_timeout": 1.0,
        "dns_proto": None,
    }
    sanic_test_app = server.run_sanic_server(counters, query_params, "*", 15000, False, True)
    TestManager(sanic_test_app)
    return sanic_test_app


def make_counter(initial_value=0, status=False):
    counter = models.Counter(name="2001:db8:ffff::1")
    counter.counter = initial_value
    counter.status = status
    return counter


def test_run_sanic_server_bg_tasks():
    server_mock = MagicMock()
    query_params = {"query_period": 5.0, "query_timeout": 1.0, "query_fqdn": "$self", "rr_type": "AAAA"}
    ip_counters = {
        "192.0.2.15": models.Counter(name="192.0.2.15"),
        "2001:db8:ffff::1": models.Counter(name="2001:db8:ffff::1"),
        "192.0.2.22": models.Counter(name="192.0.2.22"),
        "2001:db8:ffff::f": models.Counter(name="2001:db8:ffff::f"),
    }
    patcher1 = patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.server.sanic.Sanic", return_value=server_mock)
    patcher1.start()
    server.run_sanic_server(ip_counters, query_params, "*", 80, False)
    patcher1.stop()

    assert server_mock.add_route.call_count == 4
    server_mock.add_route.assert_any_call(server.slb_check_handler, "/slb_check")
    assert server_mock.register_listener.call_count == 2
    assert server_mock.ctx.counters == ip_counters


# sanic_testing supports 2 types of tests: sync and async. Async tests is
# interesting because they do not require to start a server at all. But, for
# async tests there no way to control server hostname or IP address. That's why
# slb_check_handler tested using sync tests.
def test_ping_up():
    counters = {"127.0.0.1": make_counter(status=True), "::1": make_counter()}
    srv = get_server(counters)
    _, response = srv.test_client.get("/slb_check")
    assert response.body == b"UP"
    assert response.status == 200


def test_ping_down():
    counters = {"127.0.0.1": make_counter(), "::1": make_counter()}
    srv = get_server(counters)
    _, response = srv.test_client.get("/slb_check")
    assert response.body == b"DOWN"
    assert response.status == 503


def test_ping_unknown_ip():
    counters = {"127.0.0.127": make_counter(), "::1": make_counter()}
    srv = get_server(counters)
    _, response = srv.test_client.get("/slb_check")
    assert b"not enabled" in response.body
    assert response.status == 404


def test_ping_up_ipv6():
    counters = {"127.0.0.1": make_counter(), "::1": make_counter(status=True)}
    srv = get_server(counters)
    _, response = srv.test_client.get("/slb_check", host="::1")
    assert response.body == b"UP"
    assert response.status == 200


def test_stop_file():
    counters = {"127.0.0.1": make_counter(), "::1": make_counter(status=True)}
    path_exists_mock = Mock()
    with patch.object(Path, "exists", new=path_exists_mock):
        srv = get_server(counters)
        _, response = srv.test_client.get("/slb_check", host="::1")

    path_exists_mock.assert_called_once()
    assert response.body == b"DOWN"
    assert response.status == 503


# on the other hand ready_handler tested using async tests.
@pytest.mark.asyncio
async def test_ready_handler():
    srv = get_server({})
    _, response = await srv.asgi_client.get("/ready")

    assert response.body == b"OK"
    assert response.status == 200
