# pylint: disable=redefined-outer-name, protected-access
import asyncio

import aiohttp
import pytest

from taxi import config
from taxi import settings
from taxi.clients import integration_api
from taxi.clients import tvm


@pytest.fixture
async def client(loop, db, simple_secdist):
    session = aiohttp.ClientSession(loop=loop)
    yield integration_api.IntegrationAPIClient(
        session=session,
        settings=settings.Settings(),
        tvm_client=tvm.TVMClient(
            service_name='integration-api',
            secdist=simple_secdist,
            config=config.Config(db),
            session=session,
        ),
    )
    await session.close()


@pytest.mark.parametrize('retries', [1, 2])
async def test_make_request(
        client, patch_aiohttp_session, response_mock, retries,
):
    response_int_api = integration_api.APIResponse(
        status=200, data={'first': 'second'}, headers={},
    )

    @patch_aiohttp_session(client._baseurl, 'POST')
    def patch_request(method, url, **kwargs):
        return response_mock(json={'first': 'second'})

    response = await client._make_request(url='', retries=retries)
    assert response == response_int_api
    assert len(patch_request.calls) == 1


async def test_retry_timeout(client, patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(client._baseurl, 'POST')
    def patch_request(method, url, **kwargs):
        raise asyncio.TimeoutError()

    with pytest.raises(integration_api.ResponseError):
        await client._make_request(
            url='', data={}, retries=10, retry_interval=0, timeout=0,
        )

    assert len(patch_request.calls) == 10
