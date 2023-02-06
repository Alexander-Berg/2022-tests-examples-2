import pytest

from taxi.clients import integration_api


@pytest.mark.parametrize(
    ['order_id', 'api_response', 'expected_status', 'expected_result'],
    [
        (
            'order_id_1',
            {
                'status': 200,
                'data': {
                    'orders': [
                        {
                            'vehicle': {'location': [10, 10]},
                            'time_left_raw': 200.0,
                        },
                    ],
                },
            },
            200,
            {
                'status': 'driving',
                'vehicle': {'location': [10, 10]},
                'time_left_raw': 200.0,
            },
        ),
        (
            'order_id_1',
            {
                'status': 200,
                'data': {'orders': [{'vehicle': {}, 'time_left_raw': 10.0}]},
            },
            200,
            {'status': 'driving', 'time_left_raw': 10.0},
        ),
        (
            'order_id_2',
            {'status': 200, 'data': {'orders': [{}]}},
            200,
            {'status': 'search'},
        ),
        (
            'order_id_1',
            {'status': 200, 'data': {}},
            404,
            {
                'errors': [{'text': 'Driver not found', 'code': 'GENERAL'}],
                'message': 'Driver not found',
                'code': 'GENERAL',
            },
        ),
        (
            'unknown_order',
            {'status': 200, 'data': {}},
            404,
            {
                'errors': [{'text': 'Order not found', 'code': 'GENERAL'}],
                'message': 'Order not found',
                'code': 'GENERAL',
            },
        ),
    ],
)
async def test_order_progress(
        taxi_corp_auth_client,
        patch,
        order_id,
        api_response,
        expected_status,
        expected_result,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_search')
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=api_response['status'],
            data=api_response['data'],
            headers=api_response.get('headers', {}),
        )

    response = await taxi_corp_auth_client.get(
        '/1.0/client/client_id/order/{}/progress'.format(order_id),
    )

    assert response.status == expected_status
    assert await response.json() == expected_result
