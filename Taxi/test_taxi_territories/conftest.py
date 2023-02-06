# pylint: disable=redefined-outer-name
import pytest

import taxi_territories.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_territories.generated.service.pytest_plugins']


@pytest.fixture
async def taxi_territories_app(web_app, monkeypatch):
    monkeypatch.setattr(web_app, 'api_token', 'secret')
    return web_app


@pytest.fixture
def taxi_territories_client(aiohttp_client, taxi_territories_app, loop):
    return loop.run_until_complete(aiohttp_client(taxi_territories_app))
