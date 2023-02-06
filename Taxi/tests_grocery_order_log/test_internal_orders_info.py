from tests_grocery_order_log import models


async def test_basic(taxi_grocery_order_log, pgsql):
    yandex_uid = '123'
    total_orders_count = 5

    created_orders = [
        models.OrderLogIndex(
            pgsql,
            order_id=str(order_id),
            order_state='created',
            yandex_uid=yandex_uid,
        )
        for order_id in range(total_orders_count)
    ]
    for order in created_orders:
        order.update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/orders-info',
        json={
            'user_identity': {
                'yandex_uid': yandex_uid,
                'bound_yandex_uids': [],
            },
        },
    )
    assert response.status_code == 200

    assert response.json()['not_canceled_orders_count'] == total_orders_count
