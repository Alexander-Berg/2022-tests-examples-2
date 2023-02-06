import copy
import decimal
import json

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from .plugins import mock_grocery_payments

# pylint: disable=invalid-name
Decimal = decimal.Decimal

ITEM_PRICE = '10'
ITEM_QUANTITY = '1'
CART_ITEMS = [
    models.GroceryCartItem(
        item_id='item_id', price=ITEM_PRICE, quantity=ITEM_QUANTITY,
    ),
]

PAYMENT_METHOD = {'type': 'card', 'id': 'test_payment_method_id'}

ABSOLUTE_TIPS_AMOUNT = '13.45'
ABSOLUTE_TIPS = {'amount': ABSOLUTE_TIPS_AMOUNT, 'amount_type': 'absolute'}
NO_TIPS = -1

PERCENT_TIPS = {'amount': '10', 'amount_type': 'percent'}
PERCENT_TIPS_AMOUNT = str(
    Decimal(
        Decimal(ITEM_PRICE)
        * Decimal(ITEM_QUANTITY)
        * Decimal(PERCENT_TIPS['amount'])
        / Decimal(100),
    ),
)


HOLD_MONEY = 'hold_money'
CLOSE_MONEY = 'close_money'

TIPS_HOLDING = 'hold_pending'
TIPS_READY_TO_CLEAR = 'close_pending'
TIPS_PAID = 'paid'


def _tips_item(amount):
    return models.GroceryCartItem(item_id='tips', price=amount, quantity='1')


SUCCESS_FAIL = pytest.mark.parametrize('success', [True, False])


@pytest.fixture
def _prepare(pgsql, grocery_cart, grocery_depots):
    def _do(tips_payment_flow='with_order', tips=None, tips_status=None):
        if tips is None:
            tips = ABSOLUTE_TIPS

        if tips == NO_TIPS:
            tips = None

        if tips is not None:
            tips = {**tips, 'payment_flow': tips_payment_flow}

        state = models.OrderState()
        if tips_status is not None:
            state.tips_status = tips_status

        order = models.Order(
            pgsql=pgsql,
            status='checked_out',
            grocery_flow_version='grocery_flow_v3',
            state=state,
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_items(CART_ITEMS)
        grocery_cart.set_payment_method(PAYMENT_METHOD)
        grocery_cart.set_tips(tips)
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
        )

        return order

    return _do


@pytest.fixture(name='processing_reserve')
async def _processing_reserve(taxi_grocery_orders):
    async def _do(order, status_code=200):
        response = await taxi_grocery_orders.post(
            '/processing/v1/reserve',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'payload': {},
            },
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@pytest.fixture(name='processing_setstate')
async def _processing_setstate(taxi_grocery_orders):
    async def _do(order, state, success, status_code=200):
        response = await taxi_grocery_orders.post(
            '/processing/v1/set-state',
            json={
                'order_id': order.order_id,
                'state': state,
                'payload': helpers.make_set_state_payload(success),
            },
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@pytest.mark.parametrize(
    'tips, tips_amount',
    [
        (ABSOLUTE_TIPS, ABSOLUTE_TIPS_AMOUNT),
        (PERCENT_TIPS, PERCENT_TIPS_AMOUNT),
    ],
)
@consts.TIPS_FLOW_MARK
async def test_tips_with_order_reserve_request(
        processing_reserve,
        grocery_payments,
        _prepare,
        tips,
        tips_amount,
        tips_payment_flow,
):
    order = _prepare(tips_payment_flow=tips_payment_flow, tips=tips)

    items = copy.deepcopy(CART_ITEMS)
    if tips_payment_flow == consts.TIPS_WITH_ORDER_FLOW:
        items.append(_tips_item(tips_amount))

    grocery_payments.check_create(
        items_by_payment_types=[
            mock_grocery_payments.get_items_by_payment_type(
                items, PAYMENT_METHOD,
            ),
        ],
    )

    await processing_reserve(order)
    assert grocery_payments.times_create_called() == 1


@consts.TIPS_FLOW_MARK
async def test_tips_db_after_reserve(
        processing_reserve, _prepare, tips_payment_flow,
):
    order = _prepare(tips_payment_flow=tips_payment_flow)

    await processing_reserve(order)

    order.update()
    if tips_payment_flow == consts.TIPS_WITH_ORDER_FLOW:
        assert order.tips[0] == Decimal(ABSOLUTE_TIPS_AMOUNT)
        assert order.state.tips_status == TIPS_HOLDING
    else:
        assert order.tips[0] is None
        assert order.state.tips_status is None


async def test_no_tips_in_cart_reserve(processing_reserve, _prepare):
    order = _prepare(
        tips=NO_TIPS, tips_payment_flow=consts.TIPS_WITH_ORDER_FLOW,
    )

    await processing_reserve(order)

    order.update()
    assert order.tips[0] is None
    assert order.state.tips_status is None


@consts.TIPS_FLOW_MARK
@SUCCESS_FAIL
async def test_hold_callback(
        _prepare, processing_setstate, tips_payment_flow, success,
):
    init_tips_status = TIPS_HOLDING
    order = _prepare(
        tips_payment_flow=tips_payment_flow, tips_status=init_tips_status,
    )

    await processing_setstate(order, state=HOLD_MONEY, success=success)
    order.update()

    if tips_payment_flow != consts.TIPS_WITH_ORDER_FLOW:
        assert order.state.tips_status == init_tips_status
        return

    if success:
        assert order.state.tips_status == TIPS_READY_TO_CLEAR
    else:
        assert order.state.tips_status == 'failed'


@consts.TIPS_FLOW_MARK
@SUCCESS_FAIL
async def test_close_money_callback(
        _prepare, processing_setstate, tips_payment_flow, success,
):
    init_tips_status = TIPS_READY_TO_CLEAR
    order = _prepare(
        tips_payment_flow=tips_payment_flow, tips_status=init_tips_status,
    )

    await processing_setstate(order, state=CLOSE_MONEY, success=success)
    order.update()

    if tips_payment_flow != consts.TIPS_WITH_ORDER_FLOW:
        assert order.state.tips_status == init_tips_status
        return

    if success:
        assert order.state.tips_status == TIPS_PAID
    else:
        assert order.state.tips_status == 'failed'
