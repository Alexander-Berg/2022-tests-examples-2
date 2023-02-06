import datetime

import dateutil.parser
import pytest

from . import consts
from . import experiments
from . import helpers
from . import models

TIPS_DUE_DELAY = datetime.timedelta(minutes=1)

ABSOLUTE_TIPS = {'amount': '0.01', 'amount_type': 'absolute'}
PERCENT_TIPS = {'amount': '100', 'amount_type': 'percent'}
FAILED_PERCENT_TIPS = {'amount': '0', 'amount_type': 'percent'}
FAILED_ABSOLUTE_TIPS = {'amount': '-0.01', 'amount_type': 'absolute'}


@pytest.fixture(name='last_tips_processing_event')
def _last_tips_processing_event(processing):
    def _do(order):
        events = helpers.get_last_processing_events(
            processing, order.order_id, count=1, queue='processing_tips',
        )
        if not events:
            return None

        return events[0]

    return _do


@pytest.fixture(name='init_order')
def _init_order(pgsql, grocery_cart, grocery_depots):
    def _do(init_status, tips, delivery_type='eats_dispatch'):
        depot_id = '1234'
        order = models.Order(
            pgsql=pgsql,
            status=init_status,
            state=models.OrderState(close_money_status='success'),
            dispatch_status_info=models.DispatchStatusInfo(),
            depot_id=depot_id,
        )

        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_cart.set_delivery_type(delivery_type=delivery_type)
        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
        grocery_cart.set_tips(tips)

        return order

    return _do


@pytest.fixture(name='finish_order')
def _finish_order(pgsql, grocery_cart, grocery_depots, taxi_grocery_orders):
    async def _do(order):
        response = await taxi_grocery_orders.post(
            '/processing/v1/finish',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'flow_version': 'grocery_flow_v1',
                'payload': {},
            },
        )
        order.update()
        return response

    return _do


@pytest.mark.now(consts.NOW)
@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize(
    'tips, expected_tips_status',
    [
        (ABSOLUTE_TIPS, 'ok'),
        (PERCENT_TIPS, 'ok'),
        (FAILED_PERCENT_TIPS, 'fail'),
        (FAILED_ABSOLUTE_TIPS, 'fail'),
    ],
)
async def test_closed_orders(
        init_order,
        finish_order,
        last_tips_processing_event,
        tips,
        expected_tips_status,
):
    order = init_order('closed', tips=tips)

    response = await finish_order(order)

    assert response.status_code == 200

    if expected_tips_status == 'ok':
        processing_event = last_tips_processing_event(order)
        assert processing_event.payload == {
            'order_id': order.order_id,
            'reason': 'created',
        }
        assert (
            dateutil.parser.isoparse(processing_event.due)
            == consts.NOW_DT + TIPS_DUE_DELAY
        )
    else:
        assert last_tips_processing_event(order) is None


@experiments.TIPS_EXPERIMENT
async def test_canceled_orders(
        init_order, finish_order, last_tips_processing_event,
):
    order = init_order('canceled', tips=ABSOLUTE_TIPS)

    response = await finish_order(order)

    assert response.status_code == 200
    assert last_tips_processing_event(order) is None


@pytest.mark.now(consts.NOW)
@experiments.TIPS_EXPERIMENT
async def test_invalid_delivery_type_with_tips(
        init_order, finish_order, last_tips_processing_event,
):
    order = init_order('closed', tips=ABSOLUTE_TIPS, delivery_type='pickup')

    response = await finish_order(order)

    assert response.status_code == 200
    assert last_tips_processing_event(order) is None
