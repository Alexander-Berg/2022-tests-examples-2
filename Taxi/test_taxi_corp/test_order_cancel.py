import pytest

from taxi.clients import integration_api


@pytest.mark.parametrize(
    'client, prefix',
    [
        ('taxi_corp_auth_client', '/1.0/client/client_id'),
        ('taxi_corp_tvm_client', '/internal/1.0'),
    ],
    indirect=['client'],
)
@pytest.mark.parametrize(
    'order_id, state, api_response, expected_status, expected_result',
    [
        (
            'order_id_1',
            'free',
            {'status': 200, 'data': ''},
            404,
            {
                'errors': [
                    {'text': 'Order is already finished', 'code': 'GENERAL'},
                ],
                'message': 'Order is already finished',
                'code': 'GENERAL',
            },
        ),
        (
            'order_id_2',
            'free',
            {'status': 200, 'data': {'status': 'cancelled'}},
            200,
            {'_id': 'order_id_2'},
        ),
        (
            'order_id_2',
            'paid',
            {'status': 409, 'data': {'cancel_rules': {'message': 'message'}}},
            409,
            {
                'errors': [{'text': 'message', 'code': 'GENERAL'}],
                'message': 'message',
                'code': 'GENERAL',
            },
        ),
        (
            'unknown_order',
            'paid',
            {'status': 200, 'data': ''},
            404,
            {
                'errors': [{'text': 'Order not found', 'code': 'GENERAL'}],
                'message': 'Order not found',
                'code': 'GENERAL',
            },
        ),
    ],
)
async def test_order_cancel(
        patch,
        client,
        prefix,
        order_id,
        state,
        api_response,
        expected_status,
        expected_result,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_cancel')
    async def _order_cancel(*args, **kwargs):
        return integration_api.APIResponse(
            status=api_response['status'],
            data=api_response['data'],
            headers=api_response.get('headers', {}),
        )

    response = await client.post(
        f'{prefix}/order/{order_id}/cancel', json={'state': state},
    )

    assert response.status == expected_status
    assert await response.json() == expected_result
