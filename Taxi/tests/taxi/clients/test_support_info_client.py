# pylint: disable=redefined-outer-name
import pytest

from taxi import discovery
from taxi.clients import support_info


@pytest.fixture
def mock_request(patch, response_mock):
    @patch('taxi.clients.support_info.SupportInfoApiClient._single_request')
    async def _dummy_request(*args, **kwargs):
        return response_mock(json='dummy result', status=200)

    return _dummy_request


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'data',
    [
        {
            'include_history': True,
            'owner': {'id': '5b4475296asdv6528b3f5afd', 'role': 'driver'},
            'type': 'all',
        },
    ],
)
async def test_takeout(
        data, aiohttp_client, mock_request, simple_secdist, unittest_settings,
):

    client = support_info.SupportInfoApiClient(
        discovery.find_service('support_info'),
        session=aiohttp_client,
        secdist=simple_secdist,
        api_role=unittest_settings.SUPPORT_INFO_DEFAULT_API_ROLE,
    )
    result = await client.takeout(data=data)

    assert result == 'dummy result'
    request_call = mock_request.calls[0]['kwargs']
    assert request_call['method'] == 'POST'
    assert request_call['url'] == '/v1/takeout'
    assert request_call['json'] == data
    assert request_call['headers'] == {
        'Content-Type': 'application/json',
        'YaTaxi-Api-Key': 'api-key',
    }
