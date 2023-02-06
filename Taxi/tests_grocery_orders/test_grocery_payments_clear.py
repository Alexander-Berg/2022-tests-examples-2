import pytest

from . import consts
from . import models
from . import payments
from .plugins import mock_grocery_payments


CART_ITEMS = [
    models.GroceryCartItem(item_id='item_id_1', price='100', quantity='3'),
    models.GroceryCartItem(item_id='item_id_2', price='200', quantity='2'),
    models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
]


@pytest.fixture
def _check_nothing_called(billing_orders, grocery_wms_gateway):
    def _checker():
        assert billing_orders.process_async_times_called() == 0
        assert grocery_wms_gateway.times_update_invoices_called() == 0

    return _checker


@pytest.fixture
def _prepare_order(
        pgsql,
        grocery_depots,
        grocery_cart,
        transactions_eda,
        transactions_lavka_isr,
):
    def _create(country: models.Country = models.Country.Russia):
        orderstate = models.OrderState(
            wms_reserve_status='success', hold_money_status='success',
        )

        order = models.Order(pgsql=pgsql, status='closed', state=orderstate)

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id, country_iso3=country.country_iso3,
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_items(items=CART_ITEMS)
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
        transactions_eda.set_items(items=CART_ITEMS)
        transactions_lavka_isr.set_items(items=CART_ITEMS)

        return order

    return _create


@pytest.fixture
def _do_finish(taxi_grocery_orders):
    async def _finish(order: models.Order, status_code=200):
        response = await taxi_grocery_orders.post(
            '/processing/v1/finish',
            json={'order_id': order.order_id, 'payload': {}},
        )

        assert response.status_code == status_code

    return _finish


async def test_grocery_payments_flow(
        grocery_payments, _prepare_order, _do_finish, _check_nothing_called,
):
    order = _prepare_order()

    await _do_finish(order)

    assert grocery_payments.times_clear_called() == 1

    _check_nothing_called()

    order.update()
    payments.check_last_payment_operation(order, operation_type='clear')


@consts.COUNTRIES
async def test_clear_request(
        grocery_payments,
        _prepare_order,
        _do_finish,
        _check_nothing_called,
        country,
):

    order = _prepare_order()

    await _do_finish(order)

    grocery_payments.check_clear(
        order_id=order.order_id, country_iso3=country.country_iso3,
    )

    assert grocery_payments.times_clear_called() == 1

    _check_nothing_called()

    order.update()
    payments.check_last_payment_operation(order, operation_type='clear')


@pytest.mark.parametrize(
    'error_code, orders_status_code',
    [(400, 500), (404, 500), (409, 500), (500, 500)],
)
async def test_errors(
        grocery_payments,
        _prepare_order,
        _do_finish,
        _check_nothing_called,
        error_code,
        orders_status_code,
):
    order = _prepare_order()

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.CLEAR, code=error_code,
    )

    await _do_finish(order, orders_status_code)

    assert grocery_payments.times_clear_called() == 1

    _check_nothing_called()

    order.update()
    assert not order.payment_operations
