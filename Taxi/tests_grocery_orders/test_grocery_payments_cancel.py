import json

import pytest

from . import consts
from . import headers
from . import models
from . import payments
from .plugins import mock_grocery_payments


BILLING_SETTINGS_VERSION = 'settings-version'


CART_ITEMS = [
    models.GroceryCartItem(item_id='item_id_1', price='100', quantity='3'),
    models.GroceryCartItem(item_id='item_id_2', price='200', quantity='2'),
    models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
]


@pytest.fixture
def _prepare_order(pgsql, grocery_depots, grocery_cart):
    def _create(
            country: models.Country = models.Country.Russia, status='reserved',
    ):
        orderstate = models.OrderState(
            wms_reserve_status='success', close_money_status='success',
        )

        order = models.Order(
            pgsql=pgsql,
            status=status,
            state=orderstate,
            billing_settings_version=BILLING_SETTINGS_VERSION,
        )

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id, country_iso3=country.country_iso3,
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_items(items=CART_ITEMS)
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


@pytest.fixture
def _close_order(taxi_grocery_orders):
    async def _close(order: models.Order, status_code=200):
        response = await taxi_grocery_orders.post(
            '/processing/v1/close',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'flow_version': 'grocery_flow_v1',
                'is_canceled': True,
                'times_called': 1,
                'payload': {},
            },
        )

        assert response.status_code == status_code

    return _close


@consts.COUNTRIES
async def test_cancel_request(
        grocery_payments, _prepare_order, _close_order, country,
):
    order = _prepare_order(country)

    grocery_payments.check_cancel(
        order_id=order.order_id,
        country_iso3=country.country_iso3,
        billing_settings_version=BILLING_SETTINGS_VERSION,
        user_info=mock_grocery_payments.USER_INFO,
    )

    await _close_order(order)

    assert grocery_payments.times_cancel_called() == 1

    order.update()

    payments.check_last_payment_operation(
        order,
        operation_type='cancel',
        operation_id=mock_grocery_payments.DEFAULT_OPERATION_ID,
    )


@consts.COUNTRIES
@pytest.mark.parametrize('operation_type', ['cancel', 'remove'])
async def test_cancel_request_refund(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        _prepare_order,
        _close_order,
        country,
        operation_type,
):
    order = _prepare_order(country, status='closed')

    grocery_payments.check_cancel(
        order_id=order.order_id, country_iso3=country.country_iso3,
    )

    grocery_payments.set_cancel_operation_type(
        'refund' if operation_type == 'remove' else operation_type,
    )

    grocery_cart.check_refunded_items()

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/money/refund',
        json={
            'order_ids': [order.order_id],
            'reason': {'key': 'this is random json'},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert grocery_payments.times_cancel_called() == 1

    order.update()

    payments.check_last_payment_operation(
        order,
        operation_type=operation_type,
        operation_id=mock_grocery_payments.DEFAULT_OPERATION_ID,
    )

    assert grocery_payments.times_cancel_called() == 1
    if operation_type == 'cancel':
        assert grocery_cart.refund_times_called() == 0
    elif operation_type == 'remove':
        assert grocery_cart.refund_times_called() == 1


@pytest.mark.parametrize(
    'error_code, orders_status_code',
    [(400, 500), (404, 200), (409, 500), (500, 500)],
)
async def test_errors(
        grocery_payments,
        _prepare_order,
        _close_order,
        error_code,
        orders_status_code,
):
    order = _prepare_order()

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.CANCEL, code=error_code,
    )

    await _close_order(order, orders_status_code)
    assert grocery_payments.times_cancel_called() == 1

    order.update()
    assert not order.payment_operations
