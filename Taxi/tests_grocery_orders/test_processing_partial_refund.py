import json

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from . import processing_refund
from .plugins import mock_grocery_payments


ITEMS_REFUND_REQUEST = [{'item_id': 'item_id_2', 'refund_quantity': '1'}]

COMPENSATION_ID = 'a2ace908-5d18-4764-8593-192a1b535514'


def _get_cart_items():
    return [
        models.GroceryCartItem(item_id='item_id_1', price='100', quantity='3'),
        models.GroceryCartItem(item_id='item_id_2', price='200', quantity='2'),
        models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
    ]


def _setup_order_and_cart(
        pgsql,
        grocery_cart,
        grocery_depots,
        transactions_eda,
        items,
        status='closed',
        hold_money_status='success',
        clear_money_status='success',
        grocery_flow='grocery_flow_v1',
        add_payment_method=True,
        country_iso3=models.Country.Russia.country_iso3,
        billing_settings_version=None,
):
    order = models.Order(
        pgsql=pgsql,
        status=status,
        state=models.OrderState(
            hold_money_status=hold_money_status,
            close_money_status=clear_money_status,
        ),
        grocery_flow_version=grocery_flow,
        billing_settings_version=billing_settings_version,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    if add_payment_method:
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
    grocery_cart.set_items(items=items)
    transactions_eda.set_items(items=items)

    grocery_cart.set_order_conditions(delivery_cost='500')

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country_iso3,
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    return order


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
        'items': ITEMS_REFUND_REQUEST,
        'compensation_id': COMPENSATION_ID,
        'reason': 'compensation_partial_refund',
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
        items=ITEMS_REFUND_REQUEST,
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
        items=ITEMS_REFUND_REQUEST,
        compensation_id=COMPENSATION_ID,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
        expected_code=500,
    )

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert not events


def _create_header_with_yandex_login():
    headers_ = headers.DEFAULT_HEADERS
    headers_['X-Yandex-Login'] = 'yandex_login'
    return headers_


def _check_admin_action_in_history(order, is_success):
    order.check_order_history(
        'partial-refund',
        {
            'compensation_id': COMPENSATION_ID,
            'items': _get_cart_items,
            'status': 'success' if is_success else 'fail',
        },
    )


@pytest.mark.parametrize(
    'expected_partial_refund_response_code,'
    'expected_processing_response_code,'
    'expected_payload_error_code',
    [
        (None, 200, None),
        (400, 400, 'bad_request'),
        (404, 404, 'not_allowed'),
        (409, 200, None),
        (500, 200, None),
    ],
)  # 500->200 and 409->200 because partial_refund throw RetryException
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        processing,
        transactions_eda,
        grocery_depots,
        expected_partial_refund_response_code,
        expected_processing_response_code,
        mocked_time,
        expected_payload_error_code,
):
    mocked_time.set(consts.NOW_DT)
    items = _get_cart_items()
    order = _setup_order_and_cart(
        pgsql,
        grocery_cart,
        grocery_depots,
        transactions_eda,
        items=items,
        status='closed',
    )
    if expected_partial_refund_response_code:
        grocery_payments.set_error_code(
            handler=mock_grocery_payments.REMOVE,
            code=expected_partial_refund_response_code,
        )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 0,
    }
    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/partial-refund',
        json={
            'order_id': order.order_id,
            'items': ITEMS_REFUND_REQUEST,
            'compensation_id': COMPENSATION_ID,
            'event_policy': event_policy,
        },
    )
    if expected_partial_refund_response_code:
        assert response.status_code == expected_processing_response_code

        if response.status_code == 400 or response.status_code == 200:
            events = list(
                processing.events(scope='grocery', queue='compensations'),
            )
            assert len(events) == 1
            if expected_payload_error_code is not None:
                assert (
                    events[0].payload['error_code']
                    == expected_payload_error_code
                )
    else:
        assert response.status_code == 200


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
        items=ITEMS_REFUND_REQUEST,
        compensation_id=COMPENSATION_ID,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=500,
    )

    await _retry_after_error(
        order=order,
        items=ITEMS_REFUND_REQUEST,
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
        transactions_eda,
        grocery_payments,
):
    async def _do(expected_code, event_policy):
        items = _get_cart_items()
        order = _setup_order_and_cart(
            pgsql,
            grocery_cart,
            grocery_depots,
            transactions_eda,
            items=items,
            status='closed',
        )

        grocery_payments.set_error_code(
            handler=mock_grocery_payments.REMOVE, code=500,
        )

        response = await taxi_grocery_orders.post(
            '/processing/v1/compensation/partial-refund',
            json={
                'order_id': order.order_id,
                'items': ITEMS_REFUND_REQUEST,
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
        '/processing/v1/compensation/partial-refund',
        mocked_time,
        taxi_grocery_orders,
    )
