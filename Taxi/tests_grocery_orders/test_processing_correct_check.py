import uuid

import pytest

from . import models

ITEM_ID_1 = 'item_id_1'
NEW_QUANTITY_REMOVE = '1'
NEW_QUANTITY_ADD = '7'


def _get_new_quantity(correcting_type='remove'):
    if correcting_type == 'add':
        return NEW_QUANTITY_ADD
    return NEW_QUANTITY_REMOVE


def _prepare(
        grocery_cart,
        grocery_wms_gateway,
        *,
        order,
        correcting_type='remove',
        reserve_timeout=None,
):
    item_id_2 = 'item_id_2'
    quantity = '4'
    price = '100'
    full_sum_after_correct = '500'
    if correcting_type == 'add':
        full_sum_after_correct = '1100'
    child_cart_id = str(uuid.uuid4())

    items = [
        models.GroceryCartItem(
            item_id=ITEM_ID_1, quantity=quantity, price=price,
        ),
        models.GroceryCartItem(
            item_id=item_id_2, quantity=quantity, price=price,
        ),
    ]

    corrected_items = [
        models.GroceryCartItem(
            item_id=ITEM_ID_1,
            quantity=_get_new_quantity(correcting_type),
            price=price,
        ),
        models.GroceryCartItem(
            item_id=item_id_2, quantity=quantity, price=price,
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

    grocery_cart.set_items(corrected_items, cart_id=child_cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
        cart_id=child_cart_id,
    )
    grocery_cart.set_cart_version(
        cart_id=child_cart_id, cart_version=order.cart_version + 1,
    )

    grocery_cart.set_child_cart_id(child_cart_id=child_cart_id)

    grocery_wms_gateway.check_reserve(
        items=corrected_items,
        full_sum=full_sum_after_correct,
        order=order,
        order_revision=str(order.order_revision + 1),
        reserve_timeout=reserve_timeout,
    )


@pytest.mark.parametrize(
    'correcting_type, order_status',
    [
        (None, 'assembling'),
        (None, 'delivering'),
        ('remove', 'assembling'),
        ('remove', 'delivering'),
        ('add', 'assembling'),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        correcting_type,
        order_status,
        grocery_depots,
):
    order = models.Order(
        pgsql=pgsql, status=order_status, edit_status='in_progress',
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
            'new_quantity': _get_new_quantity(correcting_type),
        },
    ]
    grocery_cart.set_correcting_items(correcting_items)

    request = {
        'order_id': order.order_id,
        'correcting_order_revision': order.order_revision,
        'correcting_cart_version': order.cart_version,
        'correcting_items': correcting_items,
        'correcting_type': correcting_type,
        'payload': {},
    }

    if correcting_type is not None:
        request['correcting_type'] = correcting_type

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/check', json=request,
    )
    order.update()

    assert response.status_code == 200
    assert grocery_wms_gateway.times_reserve_called() == 1
    assert grocery_cart.correct_copy_times_called() == 1
    assert grocery_cart.retrieve_times_called() == 2
    assert order.edit_status == 'in_progress'

    assert prev_cart_version + 1 == order.cart_version


@pytest.mark.parametrize(
    'order_status, correcting_type',
    [
        ('assembled', 'add'),
        ('delivering', 'add'),
        ('pending_cancel', 'add'),
        ('canceled', 'add'),
        ('closed', 'add'),
        ('assembled', 'remove'),
    ],
)
async def test_bad_order_status(
        taxi_grocery_orders, pgsql, order_status, correcting_type,
):
    order = models.Order(pgsql, status=order_status, order_revision=0)
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/check',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': order.order_revision,
            'correcting_cart_version': order.cart_version,
            'correcting_type': correcting_type,
            'correcting_items': [],
            'payload': {},
        },
    )
    order.update()

    assert response.status_code == 409
    assert order.edit_status is None


async def test_bad_revision(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='assembling', order_revision=1)

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    correcting_items = [
        {'item_id': ITEM_ID_1, 'new_quantity': _get_new_quantity()},
    ]
    grocery_cart.set_correcting_items(correcting_items)

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/check',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': 0,
            'correcting_cart_version': order.cart_version,
            'correcting_items': correcting_items,
            'payload': {},
        },
    )

    assert response.status_code == 409

    order.update()

    assert order.edit_status is None


async def test_no_cart_version(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='assembling', order_revision=1)

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    correcting_items = [
        {'item_id': ITEM_ID_1, 'new_quantity': _get_new_quantity()},
    ]
    grocery_cart.set_correcting_items(correcting_items)

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/check',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': 1,
            'correcting_items': correcting_items,
            'payload': {},
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize('error_code', [500])
async def test_copy_cart_failed(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        error_code,
):
    order = models.Order(pgsql=pgsql, status='assembling')

    prev_cart_version = order.cart_version

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    grocery_cart.set_correct_copy_error(code=error_code)

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/check',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': order.order_revision,
            'correcting_cart_version': order.cart_version,
            'correcting_items': [
                {'item_id': ITEM_ID_1, 'new_quantity': _get_new_quantity()},
            ],
            'payload': {},
        },
    )
    order.update()

    if error_code == 500:
        assert response.status_code == 500
    else:
        assert response.status_code == 409
        assert prev_cart_version == order.cart_version
        assert order.edit_status == 'failed'

    assert grocery_wms_gateway.times_reserve_called() == 0


@pytest.mark.parametrize('error_code', [400, 409])
async def test_wms_fail(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        error_code,
        grocery_depots,
):
    order = models.Order(pgsql=pgsql, status='assembling')

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    prev_cart_version = order.cart_version

    _prepare(grocery_cart, grocery_wms_gateway, order=order)

    grocery_wms_gateway.set_http_resp(
        resp='{"code": "WMS_400", "message": "Bad request"}', code=error_code,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/check',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': order.order_revision,
            'correcting_cart_version': order.cart_version,
            'correcting_items': [
                {'item_id': ITEM_ID_1, 'new_quantity': _get_new_quantity()},
            ],
            'payload': {},
        },
    )
    order.update()

    assert response.status_code == 409
    assert grocery_wms_gateway.times_reserve_called() == 1
    assert prev_cart_version == order.cart_version - 1

    assert order.edit_status is None
