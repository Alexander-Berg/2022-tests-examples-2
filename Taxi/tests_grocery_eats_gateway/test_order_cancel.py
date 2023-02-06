import pytest

from tests_grocery_eats_gateway import headers


@pytest.mark.parametrize(
    'yandex_uid,expected_order_id,expected_status',
    [
        pytest.param(
            headers.DEFAULT_HEADERS['X-Yandex-UID'],
            'good-order-id',
            200,
            id='Good params',
        ),
        pytest.param(
            headers.DEFAULT_HEADERS['X-Yandex-UID'],
            'bad-order-id',
            404,
            id='Good uid, bad order_id',
        ),
        pytest.param(
            'bad_uid', 'good-order-id', 404, id='bad uid, good order_id',
        ),
        pytest.param('bad_uid', 'bad-order-id', 400, id='bad params'),
    ],
)
async def test_basic(
        taxi_grocery_eats_gateway,
        grocery_orders,
        yandex_uid,
        expected_order_id,
        expected_status,
):
    request_order_id = 'good-order-id'
    grocery_orders.add_order_state(
        yandex_uid=yandex_uid, order_id=expected_order_id,
    )

    response = await taxi_grocery_eats_gateway.post(
        f'/orders/v1/cancel?order_id={request_order_id}',
        json={'reasonCode': 'client.self.accidentally_placed_order'},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        assert response.json() == {
            'payload': {'message': 'Successfully canceled'},
        }
