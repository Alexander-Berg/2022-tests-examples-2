import json

import pytest


DRIVER_CHECK_TTL_SECONDS = 7 * 24 * 60 * 60
PARK_ID = 'park0'
DRIVER_ID = 'driver0'
ORDER_YANDEX = 'order_yandex'
PROVIDER_YANDEX = 2
ORDER_UNKNOWN = 'order_unknown'


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'driver-check-sender': True,
    },
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
@pytest.mark.redis_store(
    [
        'hset',
        'Order:SetCar:Items:Providers:' + PARK_ID,
        ORDER_YANDEX,
        PROVIDER_YANDEX,
    ],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'status_in,order,status_out',
    [
        pytest.param('free', '', '2'),
        pytest.param('busy', '', '1'),
        pytest.param('free', ORDER_YANDEX, '3'),
        pytest.param('busy', ORDER_YANDEX, '4'),
        pytest.param('free', ORDER_UNKNOWN, '4'),
        pytest.param('busy', ORDER_UNKNOWN, '4'),
    ],
)
async def test_driver_check_sender(
        taxi_driver_status,
        testpoint,
        redis_store,
        status_in,
        order,
        status_out,
        taxi_config,
):
    @testpoint('driver-check-sender-tp')
    def _redis_driver_check_sender_testpoint(request):
        return {}

    await taxi_driver_status.enable_testpoints()
    _redis_driver_check_sender_testpoint.flush()

    response = await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        },
        data=json.dumps({'target_status': status_in, 'order': order}),
    )
    assert response.status_code == 200

    await _redis_driver_check_sender_testpoint.wait_call()

    redis_key = PARK_ID + ':STATUS_DRIVERS'
    assert redis_store.ttl(redis_key) == DRIVER_CHECK_TTL_SECONDS
    assert redis_store.hget(redis_key, DRIVER_ID).decode('utf-8') == status_out

    response = await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        },
        data=json.dumps({'target_status': 'offline'}),
    )
    assert response.status_code == 200

    await _redis_driver_check_sender_testpoint.wait_call()
    assert redis_store.hget(redis_key, DRIVER_ID) is None
