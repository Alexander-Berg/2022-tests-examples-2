# pylint: disable=redefined-outer-name
import asyncio

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.clients import taximeter


@pytest.fixture
async def client(loop, db):
    class Config(config.Config):
        TAXIMETER_EXT_REQUEST_TIMEOUT = 1

    session = aiohttp.ClientSession(loop=loop)
    yield taximeter.TaximeterApiClient(
        service=discovery.find_service('taximeter'),
        session=session,
        config=Config(db),
        api_token='secret',
        eb_retries=5,
        eb_time=0,
    )
    await session.close()


async def test_taximeter_client(
        client, db, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'POST')
    def patch_request(method, url, headers, **kwargs):
        assert method == 'post'
        assert headers.get('YaTaxi-Api-Key') == 'secret'
        return response_mock(json=[])

    result, _ = await client.process_billing_events(
        events=[
            {
                'kind': 'subvention',
                'transaction_id': '85d04c7c83739bb0fd71cdf2',
                'event_at': '2018-12-05T14:08:44.591Z',
                'external_event_ref': 'subvention/85d04c7c83739bb0fd71cdf2',
                'data': {},
            },
        ],
    )
    assert len(patch_request.calls) == 1
    assert result == []


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
            return response_mock()

    @patch('random.randint')
    def _randint(a, b):
        # pylint: disable=invalid-name
        return 0

    try:
        await client.process_billing_events(
            events=[
                {
                    'kind': 'subvention',
                    'transaction_id': '85d04c7c83739bb0fd71cdf2',
                    'event_at': '2018-12-05T14:08:44.591Z',
                    'external_event_ref': (
                        'subvention/85d04c7c83739bb0fd71cdf2'
                    ),
                    'data': {},
                },
            ],
        )
        assert failed_number < 5
    except (asyncio.TimeoutError, aiohttp.ClientConnectionError):
        assert failed_number > 5
