# pylint: disable=redefined-outer-name, protected-access
import pytest

from taxi import discovery
from taxi.clients import eats_core_complaint


@pytest.fixture
def mock_request(patch):
    @patch(
        'taxi.clients.eats_core_complaint.EatsCoreComplaintApiClient._request',
    )
    async def _dummy_request(*args, params, **kwargs):
        if params.get('order_nr') == '123':
            return {'some': 'data'}
        if params.get('order_nr') == '321':
            return {'another': 'data'}
        raise eats_core_complaint.NotFoundError()

    return _dummy_request


@pytest.mark.parametrize(
    'method, url, kwargs, status, expected_response',
    [
        (
            'get',
            '/other_url',
            {'params': {'some': 'params'}},
            200,
            {'some': 'response'},
        ),
        ('get', '/some_url', {}, 200, {'some': 'response'}),
        ('get', '/error_url', {}, 400, {'some': 'response'}),
    ],
)
async def test_request(
        test_taxi_app,
        patch_aiohttp_session,
        response_mock,
        method,
        url,
        kwargs,
        status,
        expected_response,
):
    @patch_aiohttp_session(
        discovery.find_service(eats_core_complaint.SERVICE_NAME).url,
    )
    def _dummy_request(expected_method, expected_url, **kwargs):
        assert method == expected_method
        assert client.baseurl + url == expected_url
        return response_mock(json={'some': 'response'})

    client = eats_core_complaint.EatsCoreComplaintApiClient(
        session=test_taxi_app.session, tvm_client=test_taxi_app.tvm,
    )
    response = await client._request(url, method=method, **kwargs)
    assert response == expected_response
    assert _dummy_request.calls


@pytest.mark.parametrize(
    'order_nr,expected_result',
    [('123', {'some': 'data'}), ('321', {'another': 'data'})],
)
async def test_get_chat_order_meta(
        aiohttp_client, mock_request, order_nr, expected_result,
):
    client = eats_core_complaint.EatsCoreComplaintApiClient(
        session=aiohttp_client, tvm_client=None,
    )
    result = await client.get_order_meta(order_nr)
    assert result == expected_result
