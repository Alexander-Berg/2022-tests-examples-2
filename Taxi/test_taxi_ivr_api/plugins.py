# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def ivr_api_app_internal(web_app):
    return web_app


@pytest.fixture
def ivr_api_client(aiohttp_client, ivr_api_app_internal, loop):
    return loop.run_until_complete(aiohttp_client(ivr_api_app_internal))
