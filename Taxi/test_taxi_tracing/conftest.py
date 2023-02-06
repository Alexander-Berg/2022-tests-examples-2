# pylint: disable=redefined-outer-name
import uuid

import pytest

from taxi.pytest_plugins import service


from taxi_tracing import app


class _DummyUUID:
    hex = 'hex'


@pytest.fixture
def dummy_uuid4_hex(monkeypatch):
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)


service.install_service_local_fixtures(__name__)


@pytest.fixture
async def taxi_tracing_app(loop, db, simple_secdist):
    app_instance = app.create_app(loop=loop, db=db)
    app_instance.api_token = 'secret'
    yield app_instance
    for meth in app_instance.on_shutdown:
        await meth(app_instance)


@pytest.fixture
def taxi_tracing_client(aiohttp_client, taxi_tracing_app, loop):
    return loop.run_until_complete(aiohttp_client(taxi_tracing_app))
