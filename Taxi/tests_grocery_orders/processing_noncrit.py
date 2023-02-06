import datetime

import pytest

from . import consts

RETRY_DAYS_INTERVAL = 1
MAX_DAYS_RETRY_COUNT = 3
STOP_RETRY_AFTER_MINUTES = 2
RETRY_INTERVAL_MINUTES = 1
ERROR_AFTER_MINUTES = 5

NOTIFICATION_CLAUSES_LIST = [
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
    {
        'title': 'Notifications availability',
        'predicate': {
            'init': {
                'set': ['created_non_critical'],
                'arg_name': 'name',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
        },
        'value': {
            'retry_interval': {'minutes': RETRY_INTERVAL_MINUTES},
            'error_after': {'minutes': ERROR_AFTER_MINUTES},
            'stop_retry_after': {'minutes': STOP_RETRY_AFTER_MINUTES},
        },
    },
]

NOTIFICATION_CONFIG = pytest.mark.experiments3(
    name='grocery_processing_events_policy',
    consumers=[
        'grocery-orders/processing-policy',
        'grocery-processing/policy',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=NOTIFICATION_CLAUSES_LIST,
    is_config=True,
)


def check_noncrit_event(
        processing,
        order_id,
        reason,
        taxi_user_id=None,
        app_name=None,
        depot_id=None,
        idempotency_token=None,
        event_policy=None,
        check_auth_context=False,
):
    non_critical_events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    for event in non_critical_events:
        if (
                event.payload.get('order_id', None) == order_id
                and event.payload.get('reason', None) == reason
        ):
            assert event.payload.get('taxi_user_id', None) == taxi_user_id
            assert event.payload.get('app_name', None) == app_name
            if depot_id is not None:
                assert event.payload.get('depot_id', None) == depot_id
            if idempotency_token is not None:
                assert (
                    event.idempotency_token == idempotency_token
                ), event.idempotency_token
            if event_policy is not None:
                assert event.payload.get('event_policy', None) == event_policy
            if check_auth_context:
                auth_context = event.payload.get('auth_context', None)
                assert auth_context is not None
                assert auth_context['headers']['X-Yandex-UID'] is not None

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


def check_notification_order_info(result, expected, taxi_user=True):
    assert result['app_info'] == expected['app_info']
    assert result['yandex_uid'] == expected['yandex_uid']
    assert result['country_iso3'] == expected['country_iso3']
    assert result['currency_code'] == expected['currency_code']
    assert result['depot_id'] == expected['depot_id']
    assert result['eats_user_id'] == expected['eats_user_id']
    assert result['leave_at_door'] == expected['leave_at_door']
    assert result['locale'] == expected['locale']
    assert result['order_id'] == expected['order_id']
    assert result['personal_phone_id'] == expected['personal_phone_id']
    assert result['region_id'] == expected['region_id']
    if taxi_user:
        assert result['taxi_user_id'] == expected['taxi_user_id']
