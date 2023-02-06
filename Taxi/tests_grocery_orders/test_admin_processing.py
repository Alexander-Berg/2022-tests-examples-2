import json

import pytest

from . import headers
from . import models

EXP3_GROCERY_ORDERS_ADMIN_PROCESSING = pytest.mark.experiments3(
    is_config=True,
    name='grocery_orders_admin_processing',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'by_phone_number',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': [headers.PERSONAL_PHONE_ID],
                    'arg_name': 'personal_phone_id',
                    'set_elem_type': 'string',
                },
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
)


@EXP3_GROCERY_ORDERS_ADMIN_PROCESSING
async def test_interception(taxi_grocery_orders, pgsql, grocery_cart):
    order = models.Order(pgsql=pgsql)

    order.update()
    assert order.state == models.OrderState()

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

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
    assert order.state == models.OrderState(wms_reserve_status=None)

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/processing/v1/state/list',
        json={'state': {'order_id': order.order_id}},
    )
    assert response.status_code == 200

    states = response.json()['states']
    assert len(states) == 1
    state = states[0]
    assert state == {
        'order_id': order.order_id,
        'state_index': 0,
        'source': 'default',
        'state': 'wms_accepting',
        'original_payload': {'problems': []},
        'payload': {'problems': []},
        'payload_version': 0,
        'is_set': False,
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/processing/v1/state/set', json={'state': state},
    )
    assert response.status_code == 200

    state['payload']['order_revision'] = 1
    state['payload_version'] = 1
    state['is_set'] = True
    assert response.json() == {'state': state}

    order.update()
    assert order.state == models.OrderState(wms_reserve_status='success')


@EXP3_GROCERY_ORDERS_ADMIN_PROCESSING
async def test_creation_and_edition(taxi_grocery_orders, pgsql, grocery_cart):
    order = models.Order(pgsql=pgsql)

    order.update()
    assert order.state == models.OrderState()

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    state = {
        'order_id': order.order_id,
        'state_index': 0,
        'source': 'default',
        'state': 'wms_accepting',
        'original_payload': {'problems': []},
        'payload': {'problems': []},
        'payload_version': 0,
        'is_set': False,
    }

    response = await taxi_grocery_orders.put(
        '/admin/orders/v1/processing/v1/state/create', json={'state': state},
    )
    assert response.status_code == 200

    assert response.json()['state'] == state

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/processing/v1/state/list',
        json={'state': {'order_id': order.order_id}},
    )
    assert response.status_code == 200

    assert response.json() == {'states': [state]}

    state['state'] = 'wms_accepting'

    response = await taxi_grocery_orders.patch(
        '/admin/orders/v1/processing/v1/state/update', json={'state': state},
    )
    assert response.status_code == 200

    state['payload_version'] = 1
    assert response.json() == {'state': state}

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/processing/v1/state/set', json={'state': state},
    )
    assert response.status_code == 200

    state['payload']['order_revision'] = 1
    state['payload_version'] = 2
    state['is_set'] = True
    assert response.json() == {'state': state}

    order.update()
    assert order.state == models.OrderState(wms_reserve_status='success')


@pytest.mark.experiments3(
    is_config=True,
    name='grocery_orders_admin_processing',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True, 'auto_accept_states': ['wms_accepting']},
)
async def test_auto_accept(taxi_grocery_orders, pgsql, grocery_cart):
    order = models.Order(pgsql=pgsql)

    order.update()
    assert order.state == models.OrderState()

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

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
