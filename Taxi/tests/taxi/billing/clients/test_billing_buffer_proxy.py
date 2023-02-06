# pylint: disable=redefined-outer-name

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.billing import clients as billing_clients


@pytest.fixture
async def client(loop):
    class Config(config.Config):
        BUFFER_PROXY_EXT_REQUEST_TIMEOUT = 1
        BUFFER_PROXY_TAXIMETER_POLLING_RETRIES = 3
        BUFFER_PROXY_TAXIMETER_POLLING_INTERVAL = 0.5

    session = aiohttp.ClientSession(loop=loop)
    yield billing_clients.BillingBufferProxyApiClient(
        session=session, config=Config(), api_token='secret', retries=5,
    )
    await session.close()


async def test_taximeter_billing_events(
        client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(
        discovery.find_service('billing_buffer_proxy').url, 'POST',
    )
    def patch_request(method, url, headers, **kwargs):
        assert method == 'post'
        assert headers.get('YaTaxi-Api-Key') == 'secret'
        if 'push' in url:
            return response_mock(json={})
        if 'poll' in url:
            return response_mock(
                json={
                    'status': 'sent',
                    'response': {
                        'http_status': 200,
                        'json': {'quas': 'wex'},
                        'text': None,
                    },
                },
            )
        raise Exception('Unknown url')

    result = await client.process_billing_events(
        kind='taximeter_payment',
        transaction_id='abcdef12345679890',
        event_at='2019-01-31T00:00:00+03:00',
        external_event_ref='abcdef12345679890',
        data={'foo': 'bar'},
        request_id='taximeter_payment/abcdef12345679890',
    )
    assert len(patch_request.calls) == 2
    assert result == {'quas': 'wex'}
