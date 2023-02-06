import json
import socket

import pytest

import tests_driver_status.pg_helpers as helpers


HOSTNAME = socket.gethostname()
NOW_TICKS = 636581808000000000
NOW = '2018-04-01T12:00:00Z'
SOME_ORDER_001 = 'order_001'
SOME_ORDER_002 = 'order_002'
PARK = 'parkid001'
YANDEX_PROVIDER = 2
SOME_PROVIDER = 1024

LOG_STATUS_DRIVER_PREFIX = 'LOG_STATUS_DRIVER:'

DRIVER_STATUS_LOG_TTL_SECONDS = 8 * 24 * 60 * 60

STATUS_INT = {
    'offline': '0',
    'free': '2',
    'busy': '1',
    'in_order_free': '3',
    'in_order_busy': '4',
}


def _get_inner_status(status, provider):
    if status == 'offline':
        return 'offline'
    if provider == 'unknown':
        if status == 'online':
            return 'free'
        if status == 'busy':
            return status
    if provider == 'yandex':
        if status == 'online':
            return 'in_order_free'
        if status == 'busy':
            return 'in_order_busy'
    return 'in_order_busy'


def _get_pg_status_provider(pgsql, park_id, driver_id):
    statuses = helpers.get_pg_driver_statuses(pgsql)
    providers = helpers.get_pg_order_providers(pgsql, park_id, driver_id)
    if providers:
        assert len(providers) == 1
    return (
        statuses[(driver_id, park_id)]['status'],
        providers[0] if providers else 'unknown',
    )


def _check_redis_driver_status_log(
        redis_store, driver_id, park_id, status, comment,
):
    redis_key = LOG_STATUS_DRIVER_PREFIX + park_id + ':' + driver_id
    log_status = {
        'Data': {'Parameters': [], 'Type': 1},
        'i': HOSTNAME,
        's': STATUS_INT[status],
        't': NOW_TICKS,
    }
    if comment:
        log_status['c'] = comment
        log_status['Data']['Parameters'].append(comment)
    assert json.loads(redis_store.lindex(redis_key, 0)) == log_status
    assert redis_store.ttl(redis_key) == DRIVER_STATUS_LOG_TTL_SECONDS


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'status-log-sender': True,
    },
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
@pytest.mark.now(NOW)
@pytest.mark.redis_store(
    [
        'hset',
        'Order:SetCar:Items:Providers:' + PARK,
        SOME_ORDER_001,
        YANDEX_PROVIDER,
    ],
    [
        'hset',
        'Order:SetCar:Items:Providers:' + PARK,
        SOME_ORDER_002,
        SOME_PROVIDER,
    ],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'params',
    [
        # busy -> free
        (
            {
                'driver': {'park_id': PARK, 'uuid': 'driverid003'},
                'data': {'target_status': 'free'},
            }
        ),
        # busy (unknown provider) -> busy (unknown provider) + comment
        (
            {
                'driver': {'park_id': PARK, 'uuid': 'driverid005'},
                'data': {
                    'target_status': 'busy',
                    'order': SOME_ORDER_002,
                    'comment': 'meow!',
                },
            }
        ),
        # free -> busy + valid order
        (
            {
                'driver': {'park_id': PARK, 'uuid': 'driverid002'},
                'data': {'target_status': 'busy', 'order': SOME_ORDER_001},
            }
        ),
    ],
)
async def test_driver_post(
        testpoint, taxi_driver_status, pgsql, redis_store, params, taxi_config,
):
    @testpoint('status-log-sender-tp')
    def _redis_status_log_sender_testpoint(request):
        return {}

    await taxi_driver_status.enable_testpoints()
    _redis_status_log_sender_testpoint.flush()

    await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': params['driver']['park_id'],
            'X-YaTaxi-Driver-Profile-Id': params['driver']['uuid'],
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        },
        data=json.dumps(params['data']),
    )
    await _redis_status_log_sender_testpoint.wait_call()

    row = _get_pg_status_provider(
        pgsql, params['driver']['park_id'], params['driver']['uuid'],
    )

    inner_status = _get_inner_status(row[0], row[1])
    comment = params['data'].get('comment', None)

    _check_redis_driver_status_log(
        redis_store,
        params['driver']['uuid'],
        params['driver']['park_id'],
        inner_status,
        comment,
    )
