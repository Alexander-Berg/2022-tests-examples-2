import copy
import json
import typing

import pytest

from . import consts
from . import headers
from . import models
from . import payments
from .plugins import mock_grocery_payments


BILLING_SETTINGS_VERSION = 'settings-version'


CART_ITEMS = [
    models.GroceryCartItem(item_id='item-id-1', price='100', quantity='3'),
    models.GroceryCartItem(item_id='item-id-2', price='200', quantity='2'),
    models.GroceryCartItem(item_id='item-id-3', price='300', quantity='1'),
]

CART_ITEMS_V2 = [
    models.GroceryCartItemV2(
        item_id='item-id-1',
        sub_items=[
            models.GroceryCartSubItem(
                item_id='item-id-1_0',
                full_price='100',
                price='100',
                quantity='3',
            ),
            models.GroceryCartSubItem(
                item_id='item-id-1_1',
                full_price='100',
                price='70',
                quantity='2',
            ),
            models.GroceryCartSubItem(
                item_id='item-id-1_2',
                full_price='100',
                price='50',
                quantity='2',
            ),
        ],
        refunded_quantity='2',
    ),
    models.GroceryCartItemV2(
        item_id='item-id-2',
        sub_items=[
            models.GroceryCartSubItem(
                item_id='item-id-2_0',
                full_price='200',
                price='200',
                quantity='2',
            ),
        ],
    ),
    models.GroceryCartItemV2(
        item_id='item-id-3',
        sub_items=[
            models.GroceryCartSubItem(
                item_id='item-id-3_0',
                full_price='300',
                price='300',
                quantity='1',
            ),
        ],
    ),
]

ITEM_ID_TO_REFUND = CART_ITEMS[0].item_id
ITEM_TO_REFUND = {'item_id': ITEM_ID_TO_REFUND, 'refund_quantity': '6'}


@pytest.fixture
def _prepare_order(
        pgsql,
        grocery_depots,
        grocery_cart,
        transactions_eda,
        transactions_lavka_isr,
):
    def _create(
            country: models.Country = models.Country.Russia,
            shelf_store='store',
    ):
        orderstate = models.OrderState(
            wms_reserve_status='success',
            hold_money_status='success',
            close_money_status='success',
        )

        order = models.Order(
            pgsql=pgsql,
            status='closed',
            state=orderstate,
            billing_settings_version=BILLING_SETTINGS_VERSION,
        )

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id, country_iso3=country.country_iso3,
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_items_v2(
            items=_set_shelf_store(
                items=CART_ITEMS_V2,
                item_id=ITEM_ID_TO_REFUND,
                shelf_store=shelf_store,
            ),
        )
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )

        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
        )

        return order

    return _create


def _set_shelf_store(
        items: typing.List[models.GroceryCartItemV2], item_id, shelf_store,
):
    res = []
    for item in items:
        res.append(item)
        if item.item_id != item_id:
            continue

        res[-1].shelf_type = shelf_store

    return res


@pytest.fixture
def _do_partial_refund(taxi_grocery_orders):
    async def _refund(order: models.Order, status_code=200, item_id=None):
        item = copy.deepcopy(ITEM_TO_REFUND)
        if item_id is not None:
            item['item_id'] = item_id

        response = await taxi_grocery_orders.post(
            '/admin/orders/v1/money/partial-refund',
            json={'order_id': order.order_id, 'items': [item]},
        )

        assert response.status_code == status_code

    return _refund


@pytest.mark.parametrize('shelf_store', ['store', 'markdown', 'parcel'])
async def test_shelf_store(
        grocery_payments, _prepare_order, _do_partial_refund, shelf_store,
):
    order = _prepare_order(shelf_store=shelf_store)

    item_id_to_refund = ITEM_ID_TO_REFUND + _add_suffix(shelf_store)
    await _do_partial_refund(order, item_id=item_id_to_refund)

    assert grocery_payments.times_remove_called() == 1


# first item in cart is split in 3 sub_items with quantities
# 3, 2, 2
# 2 items are already refunded and we request to refund 6, so
# resulting request to g-payments should consist of these ids:
# 1 1 1 2 2 3 3
#     . . . .
@consts.COUNTRIES
async def test_refund_request(
        grocery_payments, _prepare_order, _do_partial_refund, country,
):
    order = _prepare_order(country)

    refund_items_request = [
        {
            'item_id': ITEM_TO_REFUND['item_id'] + '_0',
            'quantity': '1',
            'item_type': 'product',
        },
        {
            'item_id': ITEM_TO_REFUND['item_id'] + '_1',
            'quantity': '2',
            'item_type': 'product',
        },
        {
            'item_id': ITEM_TO_REFUND['item_id'] + '_2',
            'quantity': '1',
            'item_type': 'product',
        },
    ]
    grocery_payments.check_remove(
        order_id=order.order_id,
        country_iso3=country.country_iso3,
        items=refund_items_request,
        billing_settings_version=BILLING_SETTINGS_VERSION,
        user_info=mock_grocery_payments.USER_INFO,
    )

    await _do_partial_refund(order)

    assert grocery_payments.times_remove_called() == 1

    order.update()
    payments.check_last_payment_operation(
        order,
        operation_type='remove',
        operation_id=mock_grocery_payments.DEFAULT_OPERATION_ID,
    )


@pytest.mark.parametrize(
    'error_code, orders_status_code',
    [(400, 500), (404, 404), (409, 500), (500, 500)],
)
async def test_errors(
        grocery_payments,
        _prepare_order,
        _do_partial_refund,
        error_code,
        orders_status_code,
):
    order = _prepare_order()

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.REMOVE, code=error_code,
    )

    await _do_partial_refund(order, orders_status_code)
    assert grocery_payments.times_remove_called() == 1

    order.update()
    assert not order.payment_operations


def _add_suffix(shelf_store):
    if shelf_store == 'store':
        return ''
    if shelf_store == 'markdown':
        return ':st-md'
    if shelf_store == 'parcel':
        return ':st-pa'
    assert False
    return None
