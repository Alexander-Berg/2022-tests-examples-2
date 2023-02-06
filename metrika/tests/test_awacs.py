import pytest

from infra.awacs.proto import model_pb2
from metrika.pylib import awacs
from nanny_rpc_client import exceptions


@pytest.fixture
def awacs_api():
    awacs_api = awacs.AwacsAPI("fake_token")
    yield awacs_api


def test_create_backend(awacs_api, monkeypatch):
    def mock_get_backend(*args, **kwargs):
        raise exceptions.NotFoundError("Not exists")

    def mock_create_backend(*args, **kwargs):
        pass

    monkeypatch.setattr(awacs_api.client, "get_backend", mock_get_backend)
    monkeypatch.setattr(awacs_api.client, "create_backend", mock_create_backend)

    awacs_api.update_backend("test_namespace", "test_backend", model_pb2.BackendSpec())


def test_update_backend(awacs_api, monkeypatch):
    def mock_get_backend(*args, **kwargs):
        return model_pb2.Backend()

    def mock_update_backend(*args, **kwargs):
        pass

    monkeypatch.setattr(awacs_api.client, "get_backend", mock_get_backend)
    monkeypatch.setattr(awacs_api.client, "update_backend", mock_update_backend)

    awacs_api.update_backend("test_namespace", "test_backend", model_pb2.BackendSpec())


def test_create_upstream(awacs_api, monkeypatch):
    def mock_get_upstream(*args, **kwargs):
        raise exceptions.NotFoundError("Not exists")

    def mock_create_upstream(*args, **kwargs):
        pass

    monkeypatch.setattr(awacs_api.client, "get_upstream", mock_get_upstream)
    monkeypatch.setattr(awacs_api.client, "create_upstream", mock_create_upstream)

    awacs_api.update_upstream("test_namespace", "test_upstream", "---")


def test_update_upstream(awacs_api, monkeypatch):
    def mock_get_upstream(*args, **kwargs):
        return model_pb2.Upstream()

    def mock_update_upstream(*args, **kwargs):
        pass

    monkeypatch.setattr(awacs_api.client, "get_upstream", mock_get_upstream)
    monkeypatch.setattr(awacs_api.client, "update_upstream", mock_update_upstream)

    awacs_api.update_upstream("test_namespace", "test_upstream", "---")
