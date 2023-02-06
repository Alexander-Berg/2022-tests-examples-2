import sys
import types

import pytest

from sandbox.serviceq import state as qstate
from sandbox.serviceq import types as qtypes

from sandbox.serviceq.tests.server import utils as server_utils

__all__ = ["qserver", "qserver_with_quotas", "qserver_with_api_quotas", "qserver_with_data"]


def _patch_server(monkeypatch):
    for mod in ("serviceq.server", "serviceq.config", "qstate"):
        sys.modules.pop(mod, None)
    import gevent.monkey
    monkeypatch.setattr(gevent.monkey, "patch_all", lambda *args, **kws: None)
    from sandbox.common.joint.server import RPC, Server
    dummy_decorator = classmethod(types.MethodType(lambda _, __, method, ___=None: method, object))
    dummy_method = types.MethodType(lambda *_, **__: None, object)
    monkeypatch.setattr(RPC, "full", dummy_decorator)
    monkeypatch.setattr(RPC, "simple", dummy_decorator)
    monkeypatch.setattr(RPC, "generator", dummy_decorator)
    monkeypatch.setattr(RPC, "dupgenerator", dummy_decorator)
    monkeypatch.setattr(RPC, "__init__", dummy_method)
    monkeypatch.setattr(RPC, "get_connection_handler", dummy_method)
    monkeypatch.setattr(RPC, "counters", {})
    monkeypatch.setattr(Server, "__init__", dummy_method)
    monkeypatch.setattr(Server, "register_connection_handler", dummy_method)
    import sandbox.serviceq.server
    monkeypatch.setattr(sandbox.serviceq.server.Server, "_is_primary", True)
    monkeypatch.setattr(sandbox.serviceq.server.Server, "_Server__is_primary", True)
    monkeypatch.setattr(sandbox.serviceq.server.Server, "_wait_commit", lambda *_, **__: True)
    monkeypatch.setattr(qstate, "UNLIMITED_OWNER_MINIMUM_PRIORITY", 1000)


def _qserver(monkeypatch, tmpdir):
    _patch_server(monkeypatch)
    import sandbox.serviceq.server
    import sandbox.serviceq.config
    config = sandbox.serviceq.config.Registry()
    config.reload()
    monkeypatch.setattr(qstate, "EXTERNAL_SCALE", 1)
    monkeypatch.setattr(qtypes, "DEFAULT_QUOTA", qtypes.DEFAULT_QUOTA // 1000)
    monkeypatch.setattr(config.serviceq.server, "allow_reset", True)
    monkeypatch.setattr(config.common.dirs, "runtime", str(tmpdir))
    server = sandbox.serviceq.server.Server(config)
    monkeypatch.setattr(server, "_Server__running", True)
    monkeypatch.setattr(server, "_Server__replicating", True)
    monkeypatch.setattr(server, "_Server__snapshot_restored", True)
    return server


@pytest.fixture()
def qserver(monkeypatch, tmpdir):
    return _qserver(monkeypatch, tmpdir)


@pytest.fixture()
def qserver_with_quotas(monkeypatch, tmpdir):
    return _qserver(monkeypatch, tmpdir)


@pytest.fixture()
def qserver_with_api_quotas(monkeypatch, tmpdir):
    return _qserver(monkeypatch, tmpdir)


@pytest.fixture()
def qserver_with_data(qserver_with_quotas, test_queue):
    return server_utils.qserver_with_data_factory(qserver_with_quotas, test_queue)
