# pylint: disable=redefined-outer-name

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.billing import clients as billing_clients


@pytest.fixture
async def client(loop):
    class Config(config.Config):
        BILLING_CALCULATORS_CLIENT_QOS = {
            '__default__': {'attempts': 5, 'timeout-ms': 500},
        }

    session = aiohttp.ClientSession(loop=loop)
    yield billing_clients.BillingCalculatorsApiClient(
        service=discovery.find_service('billing_calculators'),
        session=session,
        config=Config(),
        api_token='secret',
    )
    await session.close()


async def test_billing_calculators_client(
        client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def patch_request(method, url, headers, **kwargs):
        assert method == 'post'
        assert headers.get('YaTaxi-Api-Key') == 'secret'
        if 'process_doc' in url:
            return response_mock(json={'doc': {'id': 123}})
        return None

    doc = await client.process_doc(123, 'test')
    assert len(patch_request.calls) == 1
    assert doc == {'id': 123}
