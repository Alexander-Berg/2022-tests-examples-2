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


def _get_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.master_orders')
    return cursor.fetchone()[0]


async def _run_stale_worker(taxi_driver_status):
    await taxi_driver_status.run_task(
        'worker-master-orders-cleanup-stale.testsuite',
    )


async def _run_finished_worker(taxi_driver_status):
    await taxi_driver_status.run_task(
        'worker-master-orders-cleanup-finished.testsuite',
    )


async def _run_spoiled_worker(taxi_driver_status):
    await taxi_driver_status.run_task(
        'worker-master-orders-cleanup-spoiled.testsuite',
    )


@pytest.mark.config(
    DRIVER_STATUS_WORKER_TTL_CLEANER={
        '__default__': {'batch_size': 10, 'ttl_hours': 24},
        'worker-master-orders-cleanup-finished': {
            'batch_size': 10,
            'ttl_hours': 1,
        },
        'worker-master-orders-cleanup-stale': {
            'batch_size': 10,
            'ttl_hours': 3,
        },
    },
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_orders_cleanup(taxi_driver_status, pgsql, mocked_time):
    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)
    assert _get_orders_count(pgsql) == 0

    # 00:00:00
    # insert active orders 0-99
    await _insert_orders(taxi_driver_status, 0, 100, OrderStatus.kDriving)
    # insert complete orders 0-99
    await _insert_orders(taxi_driver_status, 100, 100, OrderStatus.kComplete)
    assert _get_orders_count(pgsql) == 200

    await _run_finished_worker(taxi_driver_status)
    await _run_stale_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 200

    # 02:00:00
    _set_time(mocked_time, now, 7200)
    await _run_finished_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 100
    await _run_stale_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 100

    # 04:00:00
    _set_time(mocked_time, now, 14400)
    await _run_finished_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 100
    await _run_stale_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 0


@pytest.mark.config(
    DRIVER_STATUS_MASTER_ORDERS_CLEANUP_SPOILED={
        'enabled': True,
        'min_age_minutes': 60,
    },
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_orders_cleanup_spoiled(taxi_driver_status, pgsql, mocked_time):
    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)
    assert _get_orders_count(pgsql) == 0

    # insert active orders 0-99
    await _insert_orders(taxi_driver_status, 0, 100, OrderStatus.kDriving)
    assert _get_orders_count(pgsql) == 100

    # 02:00:00
    _set_time(mocked_time, now, 7200)
    await _run_spoiled_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 0
