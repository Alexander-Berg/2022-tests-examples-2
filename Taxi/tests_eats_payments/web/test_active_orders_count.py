from tests_eats_payments import consts

URL = 'v1/orders/active'

BASE_REQUEST = {'payment_methods': ['pm1', 'pm2', 'pm3']}


async def test_simple(
        taxi_eats_payments,
        upsert_order,
        upsert_order_payment,
        insert_operations,
):
    upsert_order('order_1')
    upsert_order('order_2')
    upsert_order('order_3', cancelled=True)
    upsert_order('order_4')
    upsert_order('order_5')

    upsert_order_payment('order_1', 'pm1', 'card')
    upsert_order_payment('order_2', 'pm1', 'card')
    upsert_order_payment('order_3', 'pm2', 'card')
    upsert_order_payment('order_4', 'pm2', 'card')
    upsert_order_payment('order_5', 'pm3', 'card')

    insert_operations(1, 'order_1', 'rev', 'prev_rev', 'create', 'done')
    insert_operations(2, 'order_1', 'rev', 'prev_rev', 'close', 'in_progress')
    insert_operations(3, 'order_2', 'rev', 'prev_rev', 'create', 'done')
    insert_operations(4, 'order_2', 'rev', 'prev_rev', 'close', 'in_progress')
    insert_operations(5, 'order_3', 'rev', 'prev_rev', 'create', 'done')
    insert_operations(6, 'order_4', 'rev', 'prev_rev', 'create', 'done')
    insert_operations(7, 'order_5', 'rev', 'prev_rev', 'create', 'done')
    insert_operations(8, 'order_5', 'rev', 'prev_rev', 'close', 'done')

    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers=consts.BASE_HEADERS,
    )

    assert response.status == 200
    assert response.json() == {
        'active_orders': [
            {'count': 2, 'id': 'pm1'},
            {'count': 1, 'id': 'pm2'},
        ],
    }


async def test_order_without_operations(
        taxi_eats_payments,
        upsert_order,
        upsert_order_payment,
        insert_operations,
):
    upsert_order('order_1')

    upsert_order_payment('order_1', 'pm1', 'card')

    insert_operations(2, 'order_1', 'rev', 'prev_rev', 'close', 'done')

    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers=consts.BASE_HEADERS,
    )

    assert response.status == 200
    assert response.json() == {'active_orders': []}
