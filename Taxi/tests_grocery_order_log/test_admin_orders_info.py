import datetime

from tests_grocery_order_log import models


NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=models.UTC_TZ)


async def test_basic(taxi_grocery_order_log, pgsql):
    yandex_uid_1 = '123'
    yandex_uid_2 = '234'
    created_orders_count = 1
    closed_orders_count = 3
    canceled_orders_count = 2

    created_orders = [
        models.OrderLogIndex(
            pgsql,
            order_id=str(order_id),
            order_state='created',
            yandex_uid=yandex_uid_1 if order_id % 2 == 0 else yandex_uid_2,
        )
        for order_id in range(created_orders_count)
    ]
    for order in created_orders:
        order.update_db()

    closed_orders = [
        models.OrderLogIndex(
            pgsql,
            order_id=str(created_orders_count + order_id),
            order_state='closed',
            yandex_uid=yandex_uid_1 if order_id % 2 == 0 else yandex_uid_2,
        )
        for order_id in range(closed_orders_count)
    ]
    for order in closed_orders:
        order.update_db()

    canceled_orders = [
        models.OrderLogIndex(
            pgsql,
            order_id=str(
                created_orders_count + closed_orders_count + order_id,
            ),
            order_state='canceled',
            yandex_uid=yandex_uid_1 if order_id % 2 == 0 else yandex_uid_2,
        )
        for order_id in range(canceled_orders_count)
    ]
    for order in canceled_orders:
        order.update_db()

    response = await taxi_grocery_order_log.post(
        '/admin/v1/order-log/v1/orders-info',
        json={
            'user_identity': {
                'yandex_uid': yandex_uid_1,
                'bound_yandex_uids': [yandex_uid_2],
            },
        },
    )

    assert response.status_code == 200
    assert (
        response.json()['not_canceled_orders_count']
        == closed_orders_count + created_orders_count
    )
    assert response.json()['first_order_id'] is not None


async def test_first_order_id(taxi_grocery_order_log, pgsql):
    yandex_uid_1 = 'some_yandex_uid_1'
    yandex_uid_2 = 'some_yandex_uid_2'
    personal_phone_id = 'some_personal_phone_id'

    models.OrderLogIndex(
        pgsql,
        order_id='order_id_3',
        order_state='created',
        order_created_date=NOW_DT + datetime.timedelta(days=2),
        yandex_uid=yandex_uid_1,
        personal_phone_id=personal_phone_id,
    ).update_db()

    models.OrderLogIndex(
        pgsql,
        order_id='order_id_2',
        order_state='closed',
        order_created_date=NOW_DT + datetime.timedelta(days=1),
        yandex_uid=yandex_uid_2,
        personal_phone_id=personal_phone_id,
    ).update_db()

    models.OrderLogIndex(
        pgsql,
        order_id='order_id_1',
        order_state='canceled',
        order_created_date=NOW_DT,
        yandex_uid=yandex_uid_1,
        personal_phone_id=personal_phone_id,
    ).update_db()

    models.OrderLogIndex(
        pgsql,
        order_id='order_id_0',
        order_state='created',
        order_created_date=NOW_DT - datetime.timedelta(days=1),
        yandex_uid=yandex_uid_2,
    ).update_db()

    response = await taxi_grocery_order_log.post(
        '/admin/v1/order-log/v1/orders-info',
        json={
            'user_identity': {
                'yandex_uid': yandex_uid_1,
                'bound_yandex_uids': [],
                'personal_phone_id': personal_phone_id,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()['not_canceled_orders_count'] == 2
    assert response.json()['first_order_id'] == 'order_id_2'
