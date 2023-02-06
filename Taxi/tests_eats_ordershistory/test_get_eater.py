import pytest


@pytest.mark.parametrize(
    'request_json, response_code, expected_response',
    [
        pytest.param(
            {},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 1, path \'\': missing required '
                    'field \'order_nr\''
                ),
            },
            id='wrong request',
        ),
        pytest.param(
            {'order_nr': ''},
            404,
            {'code': 'NotFound', 'message': 'order not found'},
            id='order not found',
        ),
        pytest.param(
            {'order_nr': 'order-id-1'},
            200,
            {'eater_id': '1', 'yandex_uid': '2'},
            id='one order',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_one_order.sql'],
                ),
            ),
        ),
    ],
)
async def test_get_eater(
        taxi_eats_ordershistory,
        request_json,
        response_code,
        expected_response,
):
    response = await taxi_eats_ordershistory.post(
        '/internal/v1/get-eater', json=request_json,
    )

    assert response.status_code == response_code
    assert response.json() == expected_response
