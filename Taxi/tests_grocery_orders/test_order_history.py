from . import headers
from . import models


async def test_order_history_statuses(
        taxi_grocery_orders, pgsql, grocery_cart,
):
    order_version = 0
    order = models.Order(pgsql=pgsql, order_version=order_version)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    statuses = [
        'checked_out',
        'canceled',
        'assembling',
        'delivering',
        'closed',
        'pending_cancel',
    ]
    for status in statuses:
        response = await taxi_grocery_orders.post(
            '/lavka/v1/orders/v1/set-status',
            json={
                'order_id': order.order_id,
                'order_version': order_version,
                'status': status,
            },
            headers=headers.DEFAULT_HEADERS,
        )
        assert response.status_code == 200
        order_version += 1

    history = order.fetch_history()
    assert len(history) == len(statuses)

    for (status, history_log) in zip(statuses, history):
        assert history_log == ('status_change', {'to': status})


async def test_order_history_states(taxi_grocery_orders, pgsql, grocery_cart):
    order = models.Order(pgsql=pgsql)
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': []},
        },
    )
    assert response.status_code == 200

    order.update()
    assert order.state == models.OrderState(wms_reserve_status='success')

    history = order.fetch_history()

    assert len(history) == 1
    assert history[0] == (
        'state_change',
        {'to': {'wms_reserve_status': 'success'}},
    )


async def test_order_history_cleanup(taxi_grocery_orders, pgsql, grocery_cart):
    order = models.Order(pgsql=pgsql)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/set-status',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'status': 'canceled',
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert len(order.fetch_history()) == 1

    order.remove()
    assert not order.fetch_history()


async def test_order_history_set_state_idempotency(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    order = models.Order(
        pgsql=pgsql,
        status='assembling',
        state=models.OrderState(
            wms_reserve_status='success', hold_money_status='success',
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_delivery_type('pickup')

    history_len = 2  # state + status

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )
    assert response.status_code == 200
    history = order.fetch_history()
    assert len(history) == history_len

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )
    assert response.status_code == 200
    history = order.fetch_history()
    assert len(history) == history_len
