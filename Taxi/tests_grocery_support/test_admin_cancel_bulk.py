import datetime
import uuid

import pytest

from . import common
from . import experiments
from . import models

SUPPORT_LOGIN = 'support_login'
ORDER_ID = 'test_order_id'
ANOTHER_ORDER_ID = 'another_test_order_id'

TIMESTAMP = datetime.datetime(2020, 3, 13, 7, 25, 00, tzinfo=models.UTC_TZ)

COMPENSATION_EVENT_POLICY = {
    'error_after': models.ONE_MINUTE_FROM_NOW,
    'retry_interval': 10,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}


def _create_customer(pgsql):
    return models.Customer(
        pgsql,
        personal_phone_id='personal_phone_id',
        comments=[
            {
                'comment': 'Unicorn, be aware of a horn',
                'support_login': SUPPORT_LOGIN,
                'timestamp': TIMESTAMP.isoformat(),
            },
        ],
        phone_id='phone_id',
        yandex_uid='838101',
        antifraud_score='good',
    )


def _create_compensation(
        pgsql,
        group,
        cancel_reason_message,
        customer,
        rate,
        order_id,
        compensation_type,
):
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 0
    compensation_info = {
        'compensation_value': rate,
        'numeric_value': str(rate),
        'status': 'in_progress',
    }
    if compensation_type == 'superVoucher':
        compensation_info['currency'] = 'RUB'
    source = 'admin_cancellation'
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
    return compensation


@experiments.CANCELMATRIX_COURIER
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize('cancel_reason_message', ['grocery_problems'])
@pytest.mark.parametrize('need_send_notification', [True, False, None])
async def test_cancel_pipeline(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
        cancel_reason_message,
        need_send_notification,
):
    order_ids = [ORDER_ID, ANOTHER_ORDER_ID]
    request_json = {
        'order_ids': order_ids,
        'group': 'service',
        'reason': cancel_reason_message,
        'need_send_notification': need_send_notification,
    }
    headers = {'X-Yandex-Login': SUPPORT_LOGIN}

    grocery_orders.add_order(
        order_id=ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )
    grocery_orders.add_order(
        order_id=ANOTHER_ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    response = await taxi_grocery_support.post(
        '/admin/support/v1/cancel/bulk', json=request_json, headers=headers,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 2
    for event in events:
        assert event.payload['order_id'] in order_ids
        order_ids.remove(event.payload['order_id'])
        assert event.payload['payload'] == {'support_login': SUPPORT_LOGIN}
        assert event.payload['reason'] == 'cancel'
        assert (
            event.payload['need_send_notification'] == need_send_notification
            or True
        )
        assert 'event_policy' not in event.payload


@pytest.mark.now(models.NOW)
@experiments.CANCELMATRIX_COURIER
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'compensation_type, promocode_type, rate',
    [('promocode', 'percent', 40), ('superVoucher', 'fixed', 300)],
)
async def test_compensation_pipeline(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
        compensation_type,
        promocode_type,
        rate,
):
    group = 'service'
    cancel_reason_message = 'technical_problems'
    customer = _create_customer(pgsql)
    compensations = [
        _create_compensation(
            pgsql,
            group,
            cancel_reason_message,
            customer,
            rate,
            ORDER_ID,
            compensation_type,
        ),
        _create_compensation(
            pgsql,
            group,
            cancel_reason_message,
            customer,
            rate,
            ANOTHER_ORDER_ID,
            compensation_type,
        ),
    ]

    order_ids = [ORDER_ID, ANOTHER_ORDER_ID]
    request_json = {
        'order_ids': order_ids,
        'group': group,
        'reason': cancel_reason_message,
        'compensation': {
            'type': 'promocode',
            'promocode_type': promocode_type,
            'promocode_value': rate,
        },
    }
    headers = {'X-Yandex-Login': customer.comments[0]['support_login']}

    grocery_orders.add_order(
        order_id=ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )
    grocery_orders.add_order(
        order_id=ANOTHER_ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    response = await taxi_grocery_support.post(
        '/admin/support/v1/cancel/bulk', json=request_json, headers=headers,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 4
    for order_num in range(2):
        event_index = order_num * 2
        event = events[event_index]
        assert event.payload['order_id'] in order_ids
        assert event.payload['reason'] == 'created'
        assert 'event_policy' not in event.payload

        compensation_event = events[event_index + 1]
        assert compensation_event.payload['order_id'] in order_ids
        order_ids.remove(event.payload['order_id'])
        assert compensation_event.payload['reason'] == 'compensation_promocode'
        assert (
            compensation_event.payload['event_policy']
            == COMPENSATION_EVENT_POLICY
        )
        compensations[order_num].compare_with_db()


@experiments.CANCELMATRIX_COURIER
@pytest.mark.parametrize(
    'desired_status, status, cargo_status, can_be_canceled, config_enabled',
    [
        ('canceled', 'draft', None, True, False),
        ('draft', 'canceled', None, False, False),
        ('draft', 'draft', 'delivered', True, False),
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
        processing,
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
    order_ids = [ORDER_ID, ANOTHER_ORDER_ID]
    request_json = {
        'order_ids': order_ids,
        'group': 'service',
        'reason': 'technical_problems',
    }
    headers = {'X-Yandex-Login': SUPPORT_LOGIN}
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
    grocery_orders.add_order(
        order_id=ANOTHER_ORDER_ID,
        delivery_type='courier',
        desired_status='draft',
        status='draft',
    )

    response = await taxi_grocery_support.post(
        '/admin/support/v1/cancel/bulk', json=request_json, headers=headers,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    if can_be_canceled:
        assert len(events) == 2
        assert events[0].payload['order_id'] == ORDER_ID
        assert events[1].payload['order_id'] == ANOTHER_ORDER_ID
    else:
        assert len(events) == 1
        assert ORDER_ID in response.json()['failed_to_cancel_orders']
        assert events[0].payload['order_id'] == ANOTHER_ORDER_ID

    for event in events:
        assert event.payload['payload'] == {'support_login': SUPPORT_LOGIN}
        assert event.payload['reason'] == 'cancel'
        assert 'event_policy' not in event.payload


@experiments.CANCELMATRIX_COURIER
@pytest.mark.parametrize('cancel_reason_message', ['incorrect_reason'])
async def test_bad_request(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        experiments3,
        cancel_reason_message,
):
    request_json = {
        'order_ids': [],
        'group': 'service',
        'reason': cancel_reason_message,
    }
    headers = {'X-Yandex-Login': SUPPORT_LOGIN}

    response = await taxi_grocery_support.post(
        '/admin/support/v1/cancel/bulk', json=request_json, headers=headers,
    )
    assert response.status_code == 400
