import datetime

import pytest

from tests_grocery_communications import consts

RETRY_DAYS_INTERVAL = 1
MAX_DAYS_RETRY_COUNT = 3
STOP_RETRY_AFTER_MINUTES = 2

NOTIFICATION_CLAUSES_LIST = [
    {
        'title': 'Receipts config',
        'predicate': {
            'init': {
                'set': [
                    'notification-send_payment_receipt',
                    'notification-send_refund_receipt',
                    'notification-send_tips_receipt',
                ],
                'arg_name': 'name',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
        },
        'value': {
            'retry_interval': {'hours': 24 * RETRY_DAYS_INTERVAL},
            'error_after': {'hours': 24 * MAX_DAYS_RETRY_COUNT},
        },
    },
    {
        'title': 'Push notification settings',
        'predicate': {
            'init': {
                'set': [
                    'notification-assembling',
                    'notification-ready_for_pickup',
                    'notification-ready_for_dispatch',
                    'notification-delivering',
                    'notification-accepted',
                    'notification-common_failure',
                    'notification-money_failure',
                ],
                'arg_name': 'name',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
        },
        'value': {'stop_retry_after': {'minutes': STOP_RETRY_AFTER_MINUTES}},
    },
]

NOTIFICATION_CONFIG = pytest.mark.experiments3(
    name='grocery_processing_events_policy',
    consumers=['grocery-orders/processing-policy'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=NOTIFICATION_CLAUSES_LIST,
    is_config=True,
)


def check_noncrit_event(processing, order_id, reason, idempotency_token=None):
    non_critical_events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    for event in non_critical_events:
        if (
                event.payload.get('order_id', None) == order_id
                and event.payload.get('reason', None) == reason
        ):
            if idempotency_token is not None:
                assert (
                    event.idempotency_token == idempotency_token
                ), event.idempotency_token

            return event.payload

    assert (
        idempotency_token is None
    ), 'idempotency token is not null and no events found'

    return None


def check_push_notification(result, expected):
    assert result['order_id'] == expected['order_id']
    assert result['code'] == expected['code']
    assert result['reason'] == expected['reason']
    assert result['payload'] == expected['payload']

    minutes = STOP_RETRY_AFTER_MINUTES
    stop_retry_after = consts.NOW_DT + datetime.timedelta(minutes=minutes)
    assert result['event_policy'] == {
        'retry_count': 1,
        'stop_retry_after': stop_retry_after.isoformat(),
    }
