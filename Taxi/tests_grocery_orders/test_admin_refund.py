import copy
import json

import pytest

from . import headers
from . import models
from . import order_log
from . import processing_noncrit
from .plugins import mock_grocery_payments


CART_ITEMS = [
    models.GroceryCartItem(item_id='item_id_1', price='100', quantity='3'),
    models.GroceryCartItem(item_id='item_id_2', price='200', quantity='2'),
    models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
]

COMPENSATION_ID = 'a2ace908-5d18-4764-8593-192a1b535514'


@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize(
    'handler',
    ['/admin/orders/v1/money/refund', '/processing/v1/compensation/refund'],
)
@pytest.mark.parametrize(
    'refunded_items',
    [
        {},
        {'item_id_2': '1'},
        {'item_id_2': '2'},
        {'item_id_2': '1', 'item_id_1': '1'},
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        handler,
        refunded_items,
        processing,
        grocery_depots,
        transactions_eda,
        experiments3,
):
    order = models.Order(pgsql=pgsql, status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    items = copy.deepcopy(CART_ITEMS)

    for item in items:
        if item.item_id in refunded_items:
            item.set_refunded_quantity(quantity=refunded_items[item.item_id])

    grocery_payments.set_cancel_operation_type('refund')
    grocery_cart.set_items(items=items)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(delivery_cost='500')
    grocery_cart.check_refunded_items()

    if handler == '/admin/orders/v1/money/refund':
        request_json = {
            'order_ids': [order.order_id],
            'reason': {'key': 'this is random json'},
        }
    else:
        request_json = {
            'order_id': order.order_id,
            'compensation_id': COMPENSATION_ID,
        }

    response = await taxi_grocery_orders.post(
        handler, json=request_json, headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    order.check_order_history(
        'admin_action',
        {'to_action_type': 'refund', 'status': 'success', 'admin_info': {}},
    )
    order.check_order_history('items_refund', {'to_refund_type': 'full'})

    assert grocery_payments.times_cancel_called() == 1
    assert grocery_cart.refund_times_called() == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 2
    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'order_edited'
    order_log.check_order_log_payload(
        event.payload, order, cart_items=items, depot=None,
    )

    event = events[1]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'order_notification'
    assert event.payload['code'] == 'compensation'

    compensation_id = None
    if handler == '/processing/v1/compensation/refund':
        compensation_id = COMPENSATION_ID
    order.update()
    order.check_payment_operation(
        (
            order.order_id,
            'refund-123',
            'remove',
            'requested',
            None,
            None,
            compensation_id,
        ),
    )


@pytest.mark.parametrize(
    'handler',
    ['/admin/orders/v1/money/refund', '/processing/v1/compensation/refund'],
)
@pytest.mark.parametrize(
    'error_code,expected_error',
    [
        (None, None),
        (400, 'BAD_REQUEST'),
        (409, 'TRANSACTIONS_INTERNAL_ERROR'),
        (500, 'TRANSACTIONS_INTERNAL_ERROR'),
        (404, 'NOT_FOUND'),
    ],
)
async def test_status_response(
        taxi_grocery_orders,
        pgsql,
        grocery_payments,
        grocery_cart,
        grocery_depots,
        handler,
        error_code,
        expected_error,
):
    if expected_error is not None:
        grocery_payments.set_error_code(
            mock_grocery_payments.CANCEL, error_code,
        )
    order = models.Order(pgsql, order_id='111', status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    if handler == '/admin/orders/v1/money/refund':
        request_json = {
            'order_ids': ['111'],
            'reason': {'key': 'this is random json'},
        }
    else:
        request_json = {'order_id': '111', 'compensation_id': COMPENSATION_ID}

    response = await taxi_grocery_orders.post(
        handler, json=request_json, headers=headers.DEFAULT_HEADERS,
    )
    order.update()

    if expected_error is not None:
        order.check_order_history(
            'admin_action',
            {'to_action_type': 'refund', 'status': 'fail', 'admin_info': {}},
        )
        assert 'errors' in response.json()
        assert len(response.json()['errors']) == 1
        assert 'code' in response.json()['errors'][0]
        assert response.json()['errors'][0]['code'] == expected_error
    else:
        order.check_order_history(
            'admin_action',
            {
                'to_action_type': 'refund',
                'status': 'success',
                'admin_info': {},
            },
        )
    assert grocery_payments.times_cancel_called() == 1


async def test_bulk_refund(taxi_grocery_orders):
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/money/refund',
        json={
            'order_ids': ['111', '222', '333'],
            'reason': {'key': 'this is random json'},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'handler',
    ['/admin/orders/v1/money/refund', '/processing/v1/compensation/refund'],
)
async def test_billing_flow_cancel_all(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        handler,
):
    order = models.Order(
        pgsql,
        status='closed',
        state=models.OrderState(close_money_status='success'),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_payments.set_cancel_operation_type('refund')

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    if handler == '/admin/orders/v1/money/refund':
        request_json = {
            'order_ids': [order.order_id],
            'reason': {'key': 'this is random json'},
        }
    else:
        request_json = {
            'order_id': order.order_id,
            'compensation_id': COMPENSATION_ID,
        }

    response = await taxi_grocery_orders.post(
        handler, json=request_json, headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert 'errors' not in response.json()

    assert grocery_cart.refund_times_called() == 1
    assert grocery_payments.times_cancel_called() == 1


@pytest.mark.parametrize(
    'expected_error, threshold, refund_sum, is_expensive_order',
    [
        ('BAD_REQUEST', 5000, 4000, True),
        ('BAD_REQUEST', 5000, 5000, False),
        (None, None, 4000, True),
        (None, None, 5000, False),
        (None, 5000, 4000, False),
        (None, 5000, 5000, True),
    ],
)
async def test_dynamic_permission(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        taxi_config,
        expected_error,
        threshold,
        refund_sum,
        is_expensive_order,
):
    threshold_config_name = 'GROCERY_ORDERS_PERMISSION_SETTINGS'
    threshold_config = taxi_config.get(threshold_config_name)
    threshold_config['expensive_order_threshold_rus'] = threshold
    taxi_config.set_values({threshold_config_name: threshold_config})

    order = models.Order(pgsql=pgsql, status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    items = [
        models.GroceryCartItem(
            item_id='item_id_1', price=str(refund_sum), quantity='1',
        ),
    ]
    grocery_cart.set_items(items)
    request_json = {
        'order_ids': [order.order_id],
        'reason': {'key': 'this is random json'},
        'is_expensive_order': is_expensive_order,
    }
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/money/refund',
        json=request_json,
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    if expected_error:
        assert 'errors' in response.json()
        assert len(response.json()['errors']) == 1
        assert response.json()['errors'][0]['code'] == expected_error
    else:
        assert 'errors' not in response.json()
