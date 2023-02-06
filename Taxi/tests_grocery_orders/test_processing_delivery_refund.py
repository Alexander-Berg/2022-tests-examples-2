import json

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from . import processing_refund
from .plugins import mock_grocery_payments


COMPENSATION_ID = 'a2ace908-5d18-4764-8593-192a1b535514'
X_YANDEX_LOGIN = 'yandex_login'


def _check_admin_action_in_history(order, is_success):
    order.check_order_history(
        'admin_action',
        {
            'to_action_type': 'delivery_refund',
            'status': 'success' if is_success else 'fail',
            'admin_info': {'x_yandex_login': X_YANDEX_LOGIN},
        },
    )


def _create_headers_with_yandex_login():
    headers_ = headers.DEFAULT_HEADERS
    headers_['X-Yandex-Login'] = X_YANDEX_LOGIN
    return headers_


@pytest.mark.parametrize(
    'expected_payment_response_code,'
    'expected_processing_response_code,'
    'expected_payload_error_code',
    [
        (None, 200, None),
        (400, 400, 'bad_request'),
        (404, 404, 'not_found'),
        (409, 500, None),
        (500, 500, None),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        processing,
        grocery_depots,
        expected_payment_response_code,
        expected_processing_response_code,
        expected_payload_error_code,
):
    order = models.Order(pgsql=pgsql, status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )
    if expected_payment_response_code is not None:
        grocery_payments.set_error_code(
            handler=mock_grocery_payments.REMOVE,
            code=expected_payment_response_code,
        )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_cart.set_order_conditions(delivery_cost='500')
    default_delivery_id = 'delivery'

    request_json = {
        'order_id': order.order_id,
        'compensation_id': COMPENSATION_ID,
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/delivery-refund',
        json=request_json,
        headers=headers_,
    )
    if expected_payment_response_code is not None:
        assert response.status_code == expected_processing_response_code
        _check_admin_action_in_history(order, False)
    else:
        assert response.status_code == 200
        _check_admin_action_in_history(order, True)
        order.check_order_history(
            'items_refund',
            {
                'refunded_items': [
                    {'item_id': default_delivery_id, 'quantity': '1'},
                ],
                'to_refund_type': 'delivery',
            },
        )
        order.check_order_history(
            'payment_status_change',
            {
                'to_operation_info': {
                    'items': [
                        {
                            'item_id': default_delivery_id,
                            'quantity': '1',
                            'item_type': 'delivery',
                        },
                    ],
                    'status': 'requested',
                    'operation_id': 'refund-123',
                    'operation_type': 'remove',
                },
            },
        )

    assert grocery_payments.times_remove_called() == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    # right now no pipeline starts
    assert not events
    if expected_payload_error_code:
        events_refund = list(
            processing.events(scope='grocery', queue='compensations'),
        )
        assert (
            events_refund[0].payload['error_code']
            == expected_payload_error_code
        )

    helpers.check_set_state_event(
        processing,
        order.order_id,
        COMPENSATION_ID,
        is_success=expected_payment_response_code is None,
    )


async def test_without_paid_delivery(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, processing,
):
    order = models.Order(pgsql=pgsql, status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    headers_ = _create_headers_with_yandex_login()
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers_}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_order_conditions(delivery_cost='0')

    request_json = {
        'order_id': order.order_id,
        'compensation_id': COMPENSATION_ID,
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/delivery-refund',
        json=request_json,
        headers=headers_,
    )
    assert response.status_code == 405
    _check_admin_action_in_history(order, False)
    helpers.check_set_state_event(
        processing, order.order_id, COMPENSATION_ID, False,
    )


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
        'reason': 'compensation_delivery_refund',
    }

    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)


async def test_stop_after(
        _run_with_error, _retry_after_error, processing, mocked_time,
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


@pytest.fixture
def _run_with_error(
        pgsql,
        grocery_depots,
        grocery_cart,
        taxi_grocery_orders,
        grocery_payments,
):
    async def _do(expected_code, event_policy):
        order = models.Order(pgsql=pgsql, status='closed')
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)
        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps(
                {'headers': _create_headers_with_yandex_login()},
            ),
        )
        grocery_cart.set_cart_data(cart_id=order.cart_id)

        grocery_cart.set_order_conditions(delivery_cost='500')

        grocery_payments.set_error_code(
            handler=mock_grocery_payments.REMOVE, code=500,
        )

        response = await taxi_grocery_orders.post(
            '/processing/v1/compensation/delivery-refund',
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
        '/processing/v1/compensation/delivery-refund',
        mocked_time,
        taxi_grocery_orders,
    )
