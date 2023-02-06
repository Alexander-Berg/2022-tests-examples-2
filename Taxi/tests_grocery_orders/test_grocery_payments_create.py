import copy
import json
import typing

# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
import pytest

from . import consts
from . import headers
from . import models
from . import payments
from .plugins import mock_grocery_payments


def _get_cart_items(currency='RUB'):
    return [
        models.GroceryCartItem(
            'item_id_1', price='10', quantity='2', currency=currency,
        ),
        models.GroceryCartItem(
            'item_id_2', price='100', quantity='1', currency=currency,
        ),
    ]


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


@consts.COUNTRIES
@pytest.mark.parametrize('autoclear', [True, False])
async def test_create_grocery_payments(
        taxi_grocery_orders,
        pgsql,
        experiments3,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        country,
        autoclear,
):
    billing_settings_version = 'settings_version'

    _grocery_order_payment_autoclear(experiments3, enabled=autoclear)

    order = models.Order(
        pgsql=pgsql,
        status='checked_out',
        billing_settings_version=billing_settings_version,
    )

    region_id = 2809
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        country_iso3=country.country_iso3,
        currency=country.currency,
        region_id=region_id,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    cart_items = _get_cart_items(country.currency)
    grocery_cart.set_items(cart_items)
    payment_method = {
        'type': 'card',
        'id': 'test_payment_method_id',
        'meta': {},
    }
    grocery_cart.set_payment_method(payment_method)

    service_fee = '20'
    grocery_cart.mock_response(
        mock_grocery_cart.Handler.retrieve_raw, service_fee=service_fee,
    )

    payment_items = copy.deepcopy(cart_items)
    payment_items.append(
        models.GroceryCartItem(
            'service_fee',
            price=service_fee,
            quantity='1',
            currency=country.currency,
        ),
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_payments.check_create(
        order_id=order.order_id,
        country_iso3=country.country_iso3,
        region_id=region_id,
        currency=country.currency,
        operation_id='1',
        items_by_payment_types=[
            mock_grocery_payments.get_items_by_payment_type(
                payment_items, payment_method,
            ),
        ],
        billing_settings_version=billing_settings_version,
        user_info=mock_grocery_payments.USER_INFO,
        autoclear=autoclear,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert grocery_payments.times_create_called() == 1

    order.update()
    payments.check_last_payment_operation(order, operation_type='create')


@pytest.mark.parametrize(
    'error_code, orders_status_code', [(400, 409), (409, 409), (500, 500)],
)
async def test_errors(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        error_code,
        orders_status_code,
):
    order = models.Order(pgsql=pgsql, status='checked_out')

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(_get_cart_items())
    payment_method = {'type': 'card', 'id': 'test_payment_method_id'}
    grocery_cart.set_payment_method(payment_method)

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.CREATE, code=error_code,
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == orders_status_code
    assert grocery_payments.times_create_called() == 1

    order.update()
    assert not order.payment_operations


async def test_zero_prices(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
):
    order = models.Order(pgsql=pgsql, status='checked_out')

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    item_id = 'item-id'
    sub_item_id = f'{item_id}_0'

    items = [
        models.GroceryCartItemV2(
            item_id=item_id,
            sub_items=[
                models.GroceryCartSubItem(
                    item_id=sub_item_id,
                    full_price='200',
                    price='0',
                    quantity='2',
                    paid_with_cashback='0',
                ),
            ],
        ),
    ]

    grocery_cart.set_items_v2(
        items=_set_shelf_store(
            items=items, item_id=item_id, shelf_store='store',
        ),
    )
    payment_method = {'type': 'card', 'id': 'test_payment_method_id'}
    grocery_cart.set_payment_method(payment_method)
    grocery_cart.set_personal_wallet_id(
        personal_wallet_id='personal_wallet_id',
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_payments.check_create(
        order_id=order.order_id,
        operation_id='1',
        items_by_payment_types=[
            {
                'items': [
                    {
                        'item_id': sub_item_id,
                        'item_type': 'product',
                        'price': '0',
                        'quantity': '2',
                    },
                ],
                'payment_method': {
                    'id': 'test_payment_method_id',
                    'type': 'card',
                },
            },
        ],
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
        },
    )

    assert response.status_code == 200
    assert grocery_payments.times_create_called() == 1


def _grocery_order_payment_autoclear(experiments3, enabled):
    experiments3.add_config(
        name='grocery_order_payment_autoclear',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': enabled},
    )
