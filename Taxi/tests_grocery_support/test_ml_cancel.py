import uuid

import pytest

from . import common
from . import experiments
from . import models

ORDER_ID = 'test_id'

COMPENSATION_EVENT_POLICY = {
    'error_after': models.ONE_MINUTE_FROM_NOW,
    'retry_interval': 10,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}


@pytest.mark.parametrize('cancel_reason_message', ['cant_wait'])
@experiments.CANCELMATRIX_COURIER
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
async def test_cancel_pipeline(
        taxi_grocery_support,
        cancel_reason_message,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
):
    request_json = {
        'order_id': ORDER_ID,
        'group': 'courier',
        'reason': cancel_reason_message,
    }

    grocery_orders.add_order(
        order_id=ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/cancel', json=request_json,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1

    event = events[0]
    assert event.payload['order_id'] == ORDER_ID
    assert event.payload['reason'] == 'cancel'
    assert 'event_policy' not in event.payload


@pytest.mark.now(models.NOW)
@pytest.mark.parametrize(
    'compensation_type, promocode_type, rate', [('promocode', 'percent', 10)],
)
@experiments.CANCELMATRIX_COURIER
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.now(models.NOW)
async def test_create_compensation(
        taxi_grocery_support,
        pgsql,
        compensation_type,
        promocode_type,
        rate,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
        now,
):
    cancel_reason_message = 'out_of_stock'
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 0
    customer = common.create_ml_customer(pgsql, now)
    compensation_info = {
        'compensation_value': rate,
        'numeric_value': str(rate),
        'status': 'in_progress',
    }
    if compensation_type == 'superVoucher':
        compensation_info['currency'] = 'RUB'
    source = 'ml'
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [],
        None,
        compensation_info,
        source,
        ORDER_ID,
        rate,
        cancel_reason_message,
        compensation_type,
    )

    request_json = {
        'order_id': ORDER_ID,
        'group': 'courier',
        'reason': cancel_reason_message,
    }

    grocery_orders.add_order(
        order_id=ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/cancel', json=request_json,
    )
    assert response.status_code == 201

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 2

    event = events[0]
    assert event.payload['order_id'] == ORDER_ID
    assert event.payload['reason'] == 'created'
    assert 'event_policy' not in event.payload

    compensation_event = events[1]
    assert compensation_event.payload['order_id'] == ORDER_ID
    assert compensation_event.payload['reason'] == 'compensation_promocode'
    assert (
        compensation_event.payload['event_policy'] == COMPENSATION_EVENT_POLICY
    )

    compensation.compare_with_db()


@pytest.mark.parametrize(
    'compensation_info, expected_code',
    [
        (
            {
                'generated_promo': 'test_promo',
                'compensation_value': 10,
                'status': 'success',
            },
            200,
        ),
        ({'compensation_value': 10, 'status': 'in_progress'}, 201),
    ],
)
@experiments.CANCELMATRIX_COURIER
@pytest.mark.now(models.NOW)
async def test_existing_compensation(
        taxi_grocery_support,
        pgsql,
        compensation_info,
        expected_code,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
        now,
):
    cancel_reason_message = 'out_of_stock'
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 0
    customer = common.create_ml_customer(pgsql, now)
    source = 'ml'
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [],
        None,
        compensation_info,
        source,
        ORDER_ID,
        cancel_reason=cancel_reason_message,
    )
    compensation.update_db()

    order = models.Order(pgsql, order_id=ORDER_ID)
    grocery_orders.add_order(
        order_id=order.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    request_json = {
        'order_id': order.order_id,
        'group': 'courier',
        'reason': cancel_reason_message,
    }

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/cancel', json=request_json,
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json()['compensation']['id'] == compensation.maas_id
        assert (
            response.json()['compensation']['type']
            == compensation.compensation_type
        )
        assert (
            response.json()['compensation']['promocode_info']
            == compensation_info
        )

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert not events

    compensation.compare_with_db()


@experiments.CANCELMATRIX_COURIER
@pytest.mark.parametrize(
    'desired_status, status, cargo_status, can_be_canceled, config_enabled',
    [
        ('canceled', 'draft', None, False, False),
        ('draft', 'canceled', None, False, False),
        ('draft', 'draft', 'delivered', False, False),
        ('draft', 'draft', 'delivered', True, True),
        (None, 'draft', 'delivered', True, True),
        ('draft', 'draft', 'new', True, False),
    ],
)
async def test_can_be_canceled(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        experiments3,
        taxi_config,
        desired_status,
        status,
        cargo_status,
        can_be_canceled,
        config_enabled,
):
    taxi_config.set_values(
        {'GROCERY_ORDERS_ALLOW_TO_CANCEL_DELIVERING_ORDERS': config_enabled},
    )
    await taxi_grocery_support.invalidate_caches()
    request_json = {
        'order_id': ORDER_ID,
        'group': 'courier',
        'reason': 'cant_wait',
    }
    dispatch_status_info = None
    if cargo_status:
        dispatch_status_info = {
            'dispatch_id': 'dispatch_id',
            'status': 'revoked',
            'cargo_status': cargo_status,
            'performer_info': {'driver_id': 'test-driver-id'},
        }

    grocery_orders.add_order(
        order_id=ORDER_ID,
        delivery_type='courier',
        desired_status=desired_status,
        status=status,
        dispatch_status_info=dispatch_status_info,
    )

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/cancel', json=request_json,
    )
    if can_be_canceled:
        assert response.status_code == 200
    else:
        assert response.status_code == 405


@pytest.mark.parametrize('cancel_reason_message', ['incorrect_reason'])
@experiments.CANCELMATRIX_COURIER
async def test_bad_request(
        taxi_grocery_support,
        cancel_reason_message,
        grocery_orders,
        grocery_cart,
        experiments3,
):
    request_json = {
        'order_id': ORDER_ID,
        'group': 'courier',
        'reason': cancel_reason_message,
    }

    grocery_orders.add_order(
        order_id=ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/cancel', json=request_json,
    )
    assert response.status_code == 400
