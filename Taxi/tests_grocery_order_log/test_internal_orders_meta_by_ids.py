from tests_grocery_order_log import models


async def test_basic(taxi_grocery_order_log, pgsql):
    order_ids = ['123456-123456', '111111-11111']

    order_1 = models.OrderLogIndex(
        pgsql=pgsql,
        order_id=order_ids[0],
        personal_phone_id='123',
        order_state='delivering',
        order_type='grocery',
    )
    order_1.update_db()

    order_2 = models.OrderLogIndex(
        pgsql=pgsql,
        order_id=order_ids[1],
        personal_phone_id='111',
        order_state='delivering',
        order_type='grocery',
    )
    order_2.update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/v1/order-log/v1/get-orders-meta-by-ids',
        json={'order_ids': order_ids},
    )
    assert response.status_code == 200
    assert (
        response.json()['orders_meta'][0]['personal_phone_id']
        == order_1.personal_phone_id
    )
    assert (
        response.json()['orders_meta'][1]['personal_phone_id']
        == order_2.personal_phone_id
    )
    assert response.json()['failed_order_ids'] == []


async def test_partial_success(taxi_grocery_order_log, pgsql):
    order_ids = ['123456-123456', '111111-11111']

    order = models.OrderLogIndex(
        pgsql=pgsql,
        order_id=order_ids[0],
        personal_phone_id='123',
        order_state='delivering',
        order_type='grocery',
    )
    order.update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/v1/order-log/v1/get-orders-meta-by-ids',
        json={'order_ids': order_ids},
    )

    assert response.status_code == 200
    assert (
        response.json()['orders_meta'][0]['personal_phone_id']
        == order.personal_phone_id
    )
    assert response.json()['failed_order_ids'] == [order_ids[1]]
