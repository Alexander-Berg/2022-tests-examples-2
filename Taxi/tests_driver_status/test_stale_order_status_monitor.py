import datetime
import json

import pytest

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import OrderStatus


def _set_time(mocked_time, now, delta_sec):
    mocked_time.set(now + datetime.timedelta(seconds=delta_sec))


async def _insert_order(taxi_driver_status, suffix, status):
    response = await taxi_driver_status.post(
        'v2/order/store',
        data=json.dumps(
            {
                'alias_id': f'order_id_{suffix}',
                'park_id': f'parkid{suffix}',
                'profile_id': f'profileid{suffix}',
                'status': status,
            },
        ),
    )
    assert response.status_code == 200


async def _insert_orders(
        taxi_driver_status, start, count, status=OrderStatus.kDriving,
):
    for i in range(start, start + count):
        await _insert_order(taxi_driver_status, i, status)


async def _run_stale_orders_monitor(taxi_driver_status):
    await taxi_driver_status.run_periodic_task('stale-order-status-monitor')


@pytest.mark.parametrize('log_dump_max_count', [10, 5, 0])
@pytest.mark.parametrize('batch_size', [20, 10, 5, 2])
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_stale_order_status_monitor(
        taxi_driver_status,
        mocked_time,
        taxi_driver_status_monitor,
        testpoint,
        taxi_config,
        batch_size,
        log_dump_max_count,
):
    @testpoint('dump_stale_order_status')
    def handle_testpoint(data):
        return data

    taxi_config.set_values(
        {
            'DRIVER_STATUS_STALE_ORDER_STATUS_MONITOR_SETTINGS': {
                'repeat_interval_minutes': 10,
                'status_age_threshold_minutes': 180,
                'log_dump_batch_size': batch_size,
                'log_dump_max_count': log_dump_max_count,
            },
        },
    )

    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)

    # 00:00:00
    # insert active orders 0-99
    await _insert_orders(taxi_driver_status, 0, 10, OrderStatus.kDriving)
    await taxi_driver_status.invalidate_caches(clean_update=True)

    # 02:00:00
    _set_time(mocked_time, now, 7200)
    await _run_stale_orders_monitor(taxi_driver_status)
    metrics = await taxi_driver_status_monitor.get_metrics(
        'stale-order-status-monitor',
    )
    assert (
        metrics['stale-order-status-monitor']['orders-count'] == 0
    )  # no stale orders yet, only those from previous runs

    # 03:00:00
    _set_time(mocked_time, now, 10800)
    await _run_stale_orders_monitor(taxi_driver_status)
    metrics = await taxi_driver_status_monitor.get_metrics(
        'stale-order-status-monitor',
    )
    assert metrics['stale-order-status-monitor']['orders-count'] == 10
    if log_dump_max_count > 0:
        tp_response = await handle_testpoint.wait_call()
        log_limit = min(log_dump_max_count, batch_size)
        assert len(tp_response['data']) == log_limit if log_limit < 10 else 10
