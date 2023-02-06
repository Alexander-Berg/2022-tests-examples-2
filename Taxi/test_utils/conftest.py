from unittest import mock

import asyncio

import pytest

from taxi.robowarehouse.lib.concepts import solomon
from taxi.robowarehouse.lib.config import settings


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
def override_settings_values(request):
    def _get_value(model, name: str):
        for key in name.split('.'):
            model = getattr(model, key)
        return model

    def _set_value(model, name: str, value):
        keys = name.rsplit('.', maxsplit=1)
        model = model if len(keys) == 1 else _get_value(model, keys[0])
        setattr(model, keys[-1], value)

    keys = [pair[0] for pair in request.param]
    values = [pair[1] for pair in request.param]

    old_values = [_get_value(settings, key) for key in keys]
    [_set_value(settings, key, value) for key, value in zip(keys, values)]
    yield request.param
    [_set_value(settings, key, value) for key, value in zip(keys, old_values)]


@pytest.fixture(scope='function')
async def solomon_client():
    with mock.patch.object(solomon.client.SolomonClient, 'send') as mock_send:
        mock_send.return_value = None
        client = await solomon.get_solomon_client()
        await client._clear_sensors()
        yield client
        await client._clear_sensors()
