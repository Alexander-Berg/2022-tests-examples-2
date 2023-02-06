# pylint: disable=redefined-outer-name

import aiohttp
import pytest

from taxi.billing.clients import _client
from taxi.billing.clients import exceptions


@pytest.fixture
async def client(loop):
    session = aiohttp.ClientSession(loop=loop)
    yield _client.HttpClient(
        service_name='my_awesome_service',
        base_url='http://my-asesome-service',
        session=session,
        api_token='secret',
        retries=5,
    )
    await session.close()


@pytest.mark.parametrize('failed_number', [4, 6])
async def test_connection_error(
        client, patch, patch_aiohttp_session, response_mock, failed_number,
):

    retries_count = 0

    @patch_aiohttp_session('http://my-asesome-service', 'POST')
    def _patch_request(*args, **kwargs):
        nonlocal retries_count
        if retries_count < failed_number:
            retries_count += 1
            raise aiohttp.ClientConnectionError
        else:
            return response_mock(json={'doc': {'id': 123}})

    try:
        await client.request('/', {}, timeout=0.25)
        assert failed_number < 5
    except exceptions.RequestRetriesExceeded:
        assert failed_number > 5
    assert len(_patch_request.calls) == 5
