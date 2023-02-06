import pytest


@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'orders.sql'],
)
@pytest.mark.parametrize(
    ('headers', 'body', 'expected_status'),
    [
        ({'X-Yandex-Login': 'username'}, {'order_id': 'not found'}, 404),
        ({'X-Yandex-Login': 'username'}, {'order_id': 'order_1'}, 200),
        ({'X-Yandex-Login': 'username'}, {'order_id': 'order_2'}, 200),
        ({'X-Yandex-Login': 'username'}, {'order_id': 'order_3'}, 200),
    ],
)
async def test_admin_order_cancel(
        taxi_eats_corp_orders_web, headers, body, expected_status,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/admin/order/cancel', headers=headers, json=body,
    )
    assert response.status == expected_status
