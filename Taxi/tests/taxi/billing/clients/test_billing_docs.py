# pylint: disable=redefined-outer-name
import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.billing import clients as billing_clients
from taxi.billing.clients.models import billing_docs


@pytest.fixture
async def client(loop):
    class Config(config.Config):
        BILLING_DOCS_CLIENT_QOS = {
            '__default__': {'attempts': 5, 'timeout-ms': 500},
        }

    session = aiohttp.ClientSession(loop=loop)
    yield billing_clients.BillingDocsApiClient(
        service=discovery.find_service('billing_docs'),
        session=session,
        config=Config(),
        api_token='secret',
    )
    await session.close()


async def test_billing_docs_update_client(
        client, patch_aiohttp_session, response_mock,
):
    expected_response = {
        'created': '2018-09-10T07:07:52.019582+00:00',
        'data': {'reason': 'ok'},
        'doc_id': 20002,
        'event_at': '2018-09-10T07:07:52.019582+00:00',
        'external_event_ref': 'new->complete with details',
        'external_obj_id': 'queue_3',
        'kind': 'test',
        'process_at': '2018-09-10T07:07:52.019582+00:00',
        'service': 'billing-docs',
        'status': 'new',
        'tags': [],
    }

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def patch_request(method, url, headers, **kwargs):
        if 'docs/update' in url:
            return response_mock(json=expected_response)
        return None

    data = billing_docs.DocsUpdateRequest(
        doc_id=20002,
        data={'details': {'reason': 'ok'}},
        idempotency_key='change document state',
        status='new',
    )
    doc = await client.update(data)
    assert len(patch_request.calls) == 1
    assert str(doc) == str(billing_docs.Doc.from_json(expected_response))
