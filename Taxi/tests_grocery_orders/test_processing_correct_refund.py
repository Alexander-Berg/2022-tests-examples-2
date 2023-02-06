import json

import pytest

from . import headers
from . import models
from .plugins import mock_grocery_payments

ITEM_ID_1 = 'item_id_1'
NEW_QUANTITY_REMOVE = '1'
NEW_QUANTITY_ADD = '7'

OLD_QUANTITY = '4'

X_YANDEX_LOGIN = 'yandex_login'


def _get_new_quantity(correcting_type='remove'):
    if correcting_type == 'add':
        return NEW_QUANTITY_ADD
    return NEW_QUANTITY_REMOVE


def _create_headers_with_yandex_login():
    headers_ = headers.DEFAULT_HEADERS
    headers_['X-Yandex-Login'] = X_YANDEX_LOGIN
    return headers_


def _prepare(
        grocery_cart,
        grocery_wms_gateway,
        *,
        order,
        correcting_type='remove',
        reserve_timeout=None,
):
    item_id_2 = 'item_id_2'
    price = '100'

    items = [
        models.GroceryCartItem(
            item_id=ITEM_ID_1, quantity=OLD_QUANTITY, price=price,
        ),
        models.GroceryCartItem(
            item_id=item_id_2, quantity=OLD_QUANTITY, price=price,
        ),
    ]

    corrected_items = [
        models.GroceryCartItem(
            item_id=ITEM_ID_1,
            quantity=_get_new_quantity(correcting_type),
            price=price,
        ),
        models.GroceryCartItem(
            item_id=item_id_2, quantity=OLD_QUANTITY, price=price,
        ),
    ]

    grocery_cart.set_correcting_type(correcting_type=correcting_type)
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    grocery_cart.set_items(items)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    grocery_wms_gateway.check_reserve(
        items=corrected_items,
        full_sum='800',
        order=order,
        order_revision=str(order.order_revision + 1),
        reserve_timeout=reserve_timeout,
    )


async def test_basic_correct_refund(
        taxi_grocery_orders,
        pgsql,
        testpoint,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        grocery_payments,
):
    @testpoint('update_cart')
    def _update_cart(data):
        new_items = []
        cart_items = grocery_cart.get_items()

        for cart_item in cart_items:
            item_to_refund = next(
                (
                    it
                    for it in data['items']
                    if it['item_id'] == cart_item.item_id
                ),
                None,
            )
            if item_to_refund is None:
                new_items.append(cart_item)
            else:
                new_items.append(
                    models.GroceryCartItem(
                        item_id=item_to_refund['item_id'],
                        quantity=OLD_QUANTITY,
                        price='100',
                        refunded_quantity=item_to_refund['refunded_quantity'],
                    ),
                )
        grocery_cart.set_items(items=new_items)

    correcting_type = 'remove'
    order_status = 'closed'
    order = models.Order(
        pgsql=pgsql, status=order_status, edit_status='in_progress',
    )
    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    prev_cart_version = order.cart_version

    _prepare(
        grocery_cart,
        grocery_wms_gateway,
        order=order,
        correcting_type=correcting_type,
        reserve_timeout=7 * 60,
    )

    correcting_items = [
        {
            'item_id': ITEM_ID_1,
            'old_quantity': OLD_QUANTITY,
            'new_quantity': _get_new_quantity(correcting_type),
        },
    ]
    grocery_cart.set_correcting_items(correcting_items)

    request = {
        'order_id': order.order_id,
        'correcting_order_revision': order.order_revision,
        'correcting_cart_version': order.cart_version,
        'correcting_items': correcting_items,
        'payload': {},
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/refund', json=request, headers=headers_,
    )
    order.update()

    assert response.status_code == 200
    assert grocery_wms_gateway.times_reserve_called() == 1
    assert grocery_cart.refund_times_called() == 1
    assert grocery_cart.retrieve_times_called() == 2

    assert _update_cart.times_called == 1

    assert grocery_payments.times_remove_called() == 1

    assert order.edit_status == 'in_progress'
    assert prev_cart_version == order.cart_version


async def test_bad_revision_refund(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='closed', order_revision=1)

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )

    correcting_items = [
        {
            'item_id': ITEM_ID_1,
            'old_quantity': OLD_QUANTITY,
            'new_quantity': _get_new_quantity('remove'),
        },
    ]

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/refund',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': 0,
            'correcting_cart_version': order.cart_version,
            'correcting_items': correcting_items,
            'payload': {},
        },
        headers=headers_,
    )

    assert response.status_code == 409

    order.update()

    assert order.edit_status is None


async def test_no_cart_version_refund(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='closed', order_revision=1)

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    correcting_items = [
        {
            'item_id': ITEM_ID_1,
            'old_quantity': OLD_QUANTITY,
            'new_quantity': _get_new_quantity('remove'),
        },
    ]

    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/refund',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': 1,
            'correcting_items': correcting_items,
            'payload': {},
        },
        headers=headers_,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'error_code, orders_status_code',
    [(400, 500), (404, 404), (409, 500), (500, 500)],
)
async def test_payments_errors_refund(
        taxi_grocery_orders,
        pgsql,
        grocery_payments,
        grocery_depots,
        grocery_cart,
        grocery_wms_gateway,
        error_code,
        orders_status_code,
):
    order = models.Order(pgsql=pgsql, status='closed', order_revision=1)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.REMOVE, code=error_code,
    )

    correcting_items = [
        {
            'item_id': ITEM_ID_1,
            'old_quantity': OLD_QUANTITY,
            'new_quantity': _get_new_quantity('remove'),
        },
    ]

    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/refund',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': 1,
            'correcting_cart_version': order.cart_version,
            'correcting_items': correcting_items,
            'payload': {},
        },
        headers=headers_,
    )

    assert response.status_code == orders_status_code
    assert grocery_payments.times_remove_called() == 1

    order.update()
    assert not order.payment_operations


@pytest.mark.parametrize('error_code', [400, 409])
async def test_wms_fail_refund(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        error_code,
        grocery_depots,
):
    order = models.Order(pgsql=pgsql, status='closed')

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    grocery_wms_gateway.set_http_resp(
        resp='{"code": "WMS_400", "message": "Bad request"}', code=error_code,
    )

    correcting_items = [
        {
            'item_id': ITEM_ID_1,
            'old_quantity': OLD_QUANTITY,
            'new_quantity': _get_new_quantity('remove'),
        },
    ]

    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/refund',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': order.order_revision,
            'correcting_cart_version': order.cart_version,
            'correcting_items': correcting_items,
            'payload': {},
        },
        headers=headers_,
    )
    order.update()

    assert response.status_code == 409
    assert grocery_wms_gateway.times_reserve_called() == 1

    assert order.edit_status is None
