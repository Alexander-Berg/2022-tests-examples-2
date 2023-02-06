import pytest
from httpx import AsyncClient

from taxi.robowarehouse.lib.api.app import app


@pytest.fixture(scope='session')
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
