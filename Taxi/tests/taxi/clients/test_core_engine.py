# pylint: disable=redefined-outer-name
import aiohttp
import pytest

from taxi import discovery
from taxi.clients import core_engine


@pytest.fixture
async def client(loop, db):
    return core_engine.CoreEngineApiClient(
        service_url=discovery.find_service('core-engine').url,
        session=aiohttp.ClientSession(loop=loop),
    )


async def test_core_engine_client(
        client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(discovery.find_service('core-engine').url, 'GET')
    # pylint: disable=unused-variable
    def patch_request(method, url, **kwargs):
        response = b"""<?xml version="1.0" encoding="utf-8"?>
            <Response>
                <Orderid>761e350004e4280da9c285d01dac43c9</Orderid>
                <Cost>206</Cost>
                <Status>complete</Status>
                <Timestamp>2019-04-25T10:07:37.929887Z</Timestamp>
            </Response>"""
        return response_mock(text=response)

    cost = await client.fetch_order_cost('random_alias_id', 'db_id')
    assert cost == 206

    await client._session.close()  # pylint: disable=W0212
