# pylint: disable=redefined-outer-name
import aiohttp
import pytest

from taxi.clients import http_client

from taxi_corp.clients import crm


@pytest.fixture
async def mock_session(loop):
    session = http_client.HTTPClient(loop=loop)
    yield session
    await session.close()


MOCK_HOST = 'http://kinda_crm_host.x'
MOCK_AUTH_TOKEN = 'token'
MOCK_EXTERNAL_ID = '12345/67'


@pytest.mark.parametrize(
    'external_id, expected_result', [(MOCK_EXTERNAL_ID, {'result': 'OK'})],
)
async def test_get_manager_emails(
        aiohttp_client, patch, external_id, expected_result,
):
    @patch('taxi_corp.clients.crm.CRM._request')
    async def _dummy_request(*args, **kwargs):
        return {'result': 'OK'}

    crm_client = crm.CRM(MOCK_HOST, MOCK_AUTH_TOKEN, aiohttp_client)
    result = await crm_client.get_manager_emails(external_id)
    pathname = '/v1/manager-emails/search'
    send_data = {'external_id': external_id}
    expected_args = (pathname, send_data)

    assert result == expected_result
    request_call = _dummy_request.calls[0]
    assert request_call['args'] == expected_args


@pytest.mark.parametrize(
    ['external_id', 'server_error_status', 'exception'],
    [
        (MOCK_EXTERNAL_ID, 400, crm.CRMBadRequestFormatError),
        (MOCK_EXTERNAL_ID, 404, crm.CRMNotFoundError),
        (MOCK_EXTERNAL_ID, 504, crm.CRMBackendTimeout),
        (MOCK_EXTERNAL_ID, 500, aiohttp.ClientResponseError),
    ],
)
async def test_sender_fail(
        mock_session,
        response_mock,
        patch,
        external_id,
        server_error_status,
        exception,
):
    @patch('aiohttp.ClientSession.post')
    async def _patch_request(*args, **kwargs):
        return response_mock(status=server_error_status)

    crm_client = crm.CRM(MOCK_HOST, MOCK_AUTH_TOKEN, mock_session)
    with pytest.raises(exception):
        await crm_client.get_manager_emails(external_id)
