import datetime
import json

import pytest


def _set_time(mocked_time, now, delta_sec):
    mocked_time.set(now + datetime.timedelta(seconds=delta_sec))


async def _insert_order(taxi_driver_status, suffix, status):
    response = await taxi_driver_status.post(
        'v1/internal/status',
        data=json.dumps(
            {
                'park_id': f'parkid{suffix}',
                'driver_id': f'driverid{suffix}',
                'status': status,
                'order_id': f'order_id_{suffix}',
            },
        ),
    )
    assert response.status_code == 200


async def _insert_orders(taxi_driver_status, start, count, status='free'):
    for i in range(start, start + count):
        await _insert_order(taxi_driver_status, i, status)


def _get_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.orders')
    return cursor.fetchone()[0]


async def _run_worker(taxi_driver_status):
    await taxi_driver_status.run_task('worker-orders-cleanup.testsuite')


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_orders_cleanup(taxi_driver_status, pgsql, mocked_time):
    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 0

    # 00:00:00
    # insert orders 0-99
    await _insert_orders(taxi_driver_status, 0, 100, 'free')

    # 00:00:01
    _set_time(mocked_time, now, 1)
    # check count
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 100

    # 00:20:00
    _set_time(mocked_time, now, 1200)
    # finish orders 0-99
    await _insert_orders(taxi_driver_status, 0, 100, 'offline')
    # insert orders 100-199
    await _insert_orders(taxi_driver_status, 100, 100, 'free')

    # 00:20:01
    _set_time(mocked_time, now, 1201)
    # check count
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 200

    # 00:40:00
    _set_time(mocked_time, now, 2400)
    # finsh orders 100-199
    await _insert_orders(taxi_driver_status, 100, 100, 'offline')
    # insert orders 200-299
    await _insert_orders(taxi_driver_status, 200, 100, 'free')

    # 00:40:01
    _set_time(mocked_time, now, 2401)
    # check count
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 300

    # 01:00:00
    _set_time(mocked_time, now, 3600)
    # finish orders 200-299
    await _insert_orders(taxi_driver_status, 200, 100, 'offline')

    # 01:00:01
    _set_time(mocked_time, now, 3601)
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 300

    # 01:20:01
    _set_time(mocked_time, now, 4801)
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 200

    # 01:40:01
    _set_time(mocked_time, now, 6001)
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 100

    # 02:00:01
    _set_time(mocked_time, now, 7201)
    await _run_worker(taxi_driver_status)
    assert _get_orders_count(pgsql) == 0
