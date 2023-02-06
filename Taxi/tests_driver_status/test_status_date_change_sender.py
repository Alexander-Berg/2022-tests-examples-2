import json

import pytest


NOW = '2018-04-01T12:00:00Z'
NOW_REDIS = b'"2018-04-01T12:00:00.000000Z"'
SOME_ORDER_001 = 'order_001'
SOME_ORDER_002 = 'order_002'
PARK = 'parkid001'
YANDEX_PROVIDER = 2
SOME_PROVIDER = 1024

DRIVER_STATUS_DATE_CHANGE_PREFIX = 'DATECHANGE_STATUS_DRIVERS:'

STATUS_CHANGE_DATE_TTL_SECONDS = 7 * 24 * 60 * 60


def _check_redis_driver_status_date_change(redis_store, driver_id, park_id):
    redis_key = DRIVER_STATUS_DATE_CHANGE_PREFIX + park_id
    assert redis_store.hget(redis_key, driver_id) == NOW_REDIS
    assert redis_store.ttl(redis_key) == STATUS_CHANGE_DATE_TTL_SECONDS


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'status-date-change-sender': True,
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
        testpoint, taxi_driver_status, redis_store, params, taxi_config,
):
    @testpoint('status-date-change-sender-tp')
    def _redis_date_change_testpoint(request):
        return {}

    await taxi_driver_status.enable_testpoints()
    _redis_date_change_testpoint.flush()

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
    await _redis_date_change_testpoint.wait_call()

    _check_redis_driver_status_date_change(
        redis_store, params['driver']['uuid'], params['driver']['park_id'],
    )
