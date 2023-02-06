import json

import pytest

from . import headers
from . import models

PROCESSING_URI_LIST = pytest.mark.parametrize(
    'uri,init_status,finish_status',
    [
        ('/processing/v1/reserve', 'checked_out', 'reserving'),
        ('/processing/v1/dispatch', 'assembled', 'assembled'),
        ('/processing/v1/close', 'draft', 'canceled'),
        ('/processing/v1/assemble', 'reserved', 'assembling'),
        ('/processing/v1/cancel', 'checked_out', 'pending_cancel'),
    ],
)


@PROCESSING_URI_LIST
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        uri,
        init_status,
        finish_status,
        grocery_depots,
        grocery_wms_gateway,
        stq,
):
    order = models.Order(pgsql=pgsql)
    order.upsert(status=init_status)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('pickup')

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version,
        'flow_version': 'grocery_flow_v1',
        'payload': {},
    }
    if uri == '/processing/v1/close':
        request['is_canceled'] = True
    if uri == '/processing/v1/cancel':
        request['cancel_reason_type'] = 'timeout'
    response = await taxi_grocery_orders.post(uri, json=request)

    assert response.status_code == 200

    order.update()
    assert order.status == finish_status


@PROCESSING_URI_LIST
async def test_order_not_found_by_order_id(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        uri,
        init_status,
        finish_status,
):
    order = models.Order(pgsql=pgsql)
    order.upsert(status=init_status)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    request = {
        'order_id': order.order_id + '-xxx',
        'order_version': order.order_version,
        'flow_version': 'grocery_flow_v1',
        'payload': {},
    }
    if uri == '/processing/v1/cancel':
        request['cancel_reason_type'] = 'timeout'

    response = await taxi_grocery_orders.post(uri, json=request)

    assert response.status_code == 404


@pytest.mark.config(GROCERY_ORDERS_CART_VERSION_ALERT=False)
@PROCESSING_URI_LIST
async def test_cart_version_mismatched_without_alert(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        uri,
        init_status,
        finish_status,
):
    if uri in ('/processing/v1/close', '/processing/v1/cancel'):
        # this handles don't retrieve cart
        return

    order = models.Order(pgsql=pgsql)
    order.upsert(status=init_status)

    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version + 1,
    )

    response = await taxi_grocery_orders.post(
        uri,
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 404


@pytest.mark.config(GROCERY_ORDERS_CART_VERSION_ALERT=True)
@PROCESSING_URI_LIST
async def test_cart_version_mismatched_with_alert(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        uri,
        init_status,
        finish_status,
):
    if uri in ('/processing/v1/close', '/processing/v1/cancel'):
        # this handles don't retrieve cart
        return

    order = models.Order(pgsql=pgsql)
    order.upsert(status=init_status)

    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version + 1,
    )

    response = await taxi_grocery_orders.post(
        uri,
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 500


@pytest.mark.config(GROCERY_ORDERS_CART_VERSION_ALERT=False)
@PROCESSING_URI_LIST
async def test_order_version_mismatched(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        uri,
        init_status,
        finish_status,
        grocery_depots,
):
    if uri in ('/processing/v1/close', '/processing/v1/cancel'):
        # this handles don't use order_version in request
        return

    order = models.Order(pgsql=pgsql, order_version=5, status=init_status)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version + 1,
        'flow_version': 'grocery_flow_v1',
        'payload': {},
    }

    response = await taxi_grocery_orders.post(uri, json=request)

    assert response.status_code == 500

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version - 1,
        'flow_version': 'grocery_flow_v1',
        'payload': {},
    }

    response = await taxi_grocery_orders.post(uri, json=request)

    assert response.status_code == 409


@pytest.mark.config(GROCERY_ORDERS_CART_VERSION_ALERT=False)
@PROCESSING_URI_LIST
async def test_idempotency(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        uri,
        init_status,
        finish_status,
):
    if uri in ('/processing/v1/close', '/processing/v1/cancel'):
        # this handles don't use order_version in request
        return

    order_version = 1
    order = models.Order(pgsql=pgsql)
    order.upsert(status=init_status, order_version=order_version + 1)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version,
        'flow_version': 'grocery_flow_v1',
        'payload': {},
    }

    response = await taxi_grocery_orders.post(uri, json=request)

    assert response.status_code == 200


@PROCESSING_URI_LIST
async def test_manual_update_enabled(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        uri,
        init_status,
        finish_status,
):
    order = models.Order(pgsql=pgsql, manual_update_enabled=True)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('pickup')

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version,
        'flow_version': 'grocery_flow_v1',
    }
    if uri == '/processing/v1/cancel':
        request['cancel_reason_type'] = 'timeout'

    response = await taxi_grocery_orders.post(uri, json=request)

    assert response.status_code == 200
