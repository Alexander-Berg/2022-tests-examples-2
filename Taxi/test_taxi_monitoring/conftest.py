# pylint: disable=redefined-outer-name
import pytest

import taxi_monitoring.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['taxi_monitoring.generated.service.pytest_plugins']


@pytest.fixture
async def monitoring_app(web_app):
    return web_app


@pytest.fixture
def monitoring_client(web_app_client):
    return web_app_client
