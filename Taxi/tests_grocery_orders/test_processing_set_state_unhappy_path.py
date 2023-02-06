import json

import pytest

from . import consts
from . import headers
from . import helpers
from . import models


@pytest.mark.now(consts.NOW)
async def test_wms_accepting_fail(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_depots,
        grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': [1, 2, 3]},  # not empty problems
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.state == models.OrderState(wms_reserve_status='failed')

    assert grocery_wms_gateway.times_close_called() == 0

    basic_events = list(processing.events(scope='grocery', queue='processing'))
    assert len(basic_events) == 1
    assert basic_events[0].payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'failure',
        'payload': {
            'event_created': consts.NOW,
            'initial_event_created': consts.NOW,
        },
        'cancel_reason_message': 'reserve_failed',
        'times_called': 0,
    }


@pytest.mark.now(consts.NOW)
async def test_cancel_after_failed_wms_reserve(
        taxi_grocery_orders,
        pgsql,
        grocery_payments,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        processing,
):
    order = models.Order(pgsql=pgsql)
    order.upsert(state=models.OrderState(wms_reserve_status='failed'))
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    assert grocery_payments.times_cancel_called() == 0
    assert grocery_wms_gateway.times_close_called() == 0

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    assert events[0].payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'failure',
        'payload': {
            'event_created': consts.NOW,
            'initial_event_created': consts.NOW,
        },
        'cancel_reason_message': 'reserve_failed',
        'times_called': 0,
    }


async def test_money_cancel_on_canceled_order(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
):
    order = models.Order(pgsql=pgsql, status='canceled')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': helpers.make_set_state_payload(True),
        },
    )

    assert response.status_code == 200
    assert grocery_payments.times_cancel_called() == 1


async def test_money_refund_failed(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        processing,
):
    order_state = models.OrderState(hold_money_status='success')
    order = models.Order(pgsql=pgsql, status='canceled', state=order_state)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'refund_money',
            'payload': {
                'errors': [{'error_reason_code': 'refund_failed'}],
                'operation_id': 'some_id',
                'operation_type': 'cancel',
            },
        },
    )

    assert response.status_code == 200

    # We do not want to call cancel again after failed refund op
    assert grocery_payments.times_cancel_called() == 0
    basic_events = list(processing.events(scope='grocery', queue='processing'))
    assert not basic_events
