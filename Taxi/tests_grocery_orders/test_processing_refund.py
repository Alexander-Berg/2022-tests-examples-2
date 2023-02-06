import copy
import json

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from . import processing_refund
from .plugins import mock_grocery_payments


CART_ITEMS = [
    models.GroceryCartItem(item_id='item_id_1', price='100', quantity='3'),
    models.GroceryCartItem(item_id='item_id_2', price='200', quantity='2'),
    models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
]

COMPENSATION_ID = 'a2ace908-5d18-4764-8593-192a1b535514'


@pytest.mark.now(consts.NOW)
async def test_retry_interval(processing, _run_with_error):
    retry_count = 2
    event_policy = {
        'retry_count': retry_count,
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
    }
    order = await _run_with_error(expected_code=200, event_policy=event_policy)

    events = list(processing.events(scope='grocery', queue='compensations'))

    event_policy['retry_count'] += 1
    assert len(events) == 1
    assert events[0].payload == {
        'event_policy': event_policy,
        'order_id': order.order_id,
        'compensation_id': COMPENSATION_ID,
        'reason': 'compensation_refund',
    }

    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)


async def test_stop_after(
        _run_with_error,
        _retry_after_error,
        processing,
        mocked_time,
        grocery_depots,
        grocery_cart,
        pgsql,
):
    mocked_time.set(consts.NOW_DT)
    order = await _run_with_error(
        expected_code=500,
        event_policy={
            'stop_retry_after': {'minutes': consts.STOP_AFTER_MINUTES},
        },
    )

    await _retry_after_error(
        order=order,
        compensation_id=COMPENSATION_ID,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy={
            'stop_retry_after': helpers.skip_minutes(
                consts.STOP_AFTER_MINUTES,
            ),
        },
        expected_code=200,
    )

    helpers.check_set_state_event(
        processing, order.order_id, COMPENSATION_ID, False,
    )


async def test_error_after(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    mocked_time.set(consts.NOW_DT)
    order = await _run_with_error(
        expected_code=429,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
    )

    await _retry_after_error(
        order=order,
        compensation_id=COMPENSATION_ID,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
        expected_code=500,
    )

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert not events


async def test_retry_after_error_behaviour(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }
    mocked_time.set(consts.NOW_DT)
    # With error after we don't want to see messages in alert chat, we want to
    # ignore problems until `error_after` happened.
    order = await _run_with_error(expected_code=200, event_policy=event_policy)

    events = list(processing.events(scope='grocery', queue='compensations'))

    events_after_first_retry = 1
    events_after_last_retry = 2

    assert len(events) == events_after_first_retry
    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)

    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }

    await _retry_after_error(
        order=order,
        compensation_id=COMPENSATION_ID,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=500,
    )

    await _retry_after_error(
        order=order,
        compensation_id=COMPENSATION_ID,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == events_after_last_retry


@pytest.mark.parametrize(
    'expected_refund_response_code,'
    'expected_refund_response_string,'
    'expected_payload_error_code',
    [
        (200, None, None),
        (400, 'BAD_REQUEST', 'bad_request'),
        (404, 'NOT_FOUND', 'not_found'),
        (409, None, None),
        (500, None, None),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        grocery_cart,
        processing,
        transactions_eda,
        grocery_payments,
        expected_refund_response_string,
        expected_refund_response_code,
        mocked_time,
        expected_payload_error_code,
):
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 0,
    }
    mocked_time.set(consts.NOW_DT)

    order = models.Order(pgsql=pgsql, status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    items = copy.deepcopy(CART_ITEMS)

    grocery_payments.set_cancel_operation_type('refund')
    grocery_cart.set_items(items=items)

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.CANCEL,
        code=expected_refund_response_code,
    )
    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/refund',
        json={
            'order_id': order.order_id,
            'compensation_id': COMPENSATION_ID,
            'event_policy': event_policy,
        },
    )
    if expected_refund_response_code not in (200, 500, 409):
        assert (
            response.json()['errors'][0]['code']
            == expected_refund_response_string
        )
    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 1
    assert response.status_code == 200
    if expected_payload_error_code:
        assert events[0].payload['error_code'] == expected_payload_error_code


@pytest.fixture
def _run_with_error(
        pgsql,
        grocery_depots,
        grocery_cart,
        taxi_grocery_orders,
        transactions_eda,
        grocery_payments,
):
    async def _do(expected_code, event_policy):
        order = models.Order(pgsql=pgsql, status='closed')
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)
        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
        )
        grocery_cart.set_cart_data(cart_id=order.cart_id)
        items = copy.deepcopy(CART_ITEMS)

        grocery_payments.set_cancel_operation_type('refund')
        grocery_cart.set_items(items=items)

        grocery_payments.set_error_code(
            handler=mock_grocery_payments.CANCEL, code=500,
        )

        response = await taxi_grocery_orders.post(
            '/processing/v1/compensation/refund',
            json={
                'order_id': order.order_id,
                'compensation_id': COMPENSATION_ID,
                'event_policy': event_policy,
            },
        )

        assert response.status_code == expected_code

        return order

    return _do


@pytest.fixture
def _retry_after_error(mocked_time, taxi_grocery_orders):
    return processing_refund.retry_processing(
        '/processing/v1/compensation/refund', mocked_time, taxi_grocery_orders,
    )
