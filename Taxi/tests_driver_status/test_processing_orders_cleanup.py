# pylint: disable=import-only-modules
import datetime

import pytest

from tests_driver_status.enum_constants import ProcessingStatus
import tests_driver_status.pg_helpers as pg_helpers


def _set_time(mocked_time, now, delta_sec):
    mocked_time.set(now + datetime.timedelta(seconds=delta_sec))


async def _insert_processing_orders(
        pgsql,
        start,
        count,
        timepoint,
        event_index=0,
        processing_status=ProcessingStatus.kPending,
):
    data = {}
    for i in range(start, start + count):
        data[f'order_id_{i}'] = {
            'park_id': f'park_id_{i}',
            'driver_id': f'driver_id_{i}',
            'processing_status': processing_status,
            'event_updated_ts': timepoint,
            'updated_ts': timepoint,
            'event_index': event_index,
        }
    pg_helpers.upsert_processing_orders(pgsql, data)


def _get_processing_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.processing_orders')
    return cursor.fetchone()[0]


async def _run_stale_worker(taxi_driver_status):
    await taxi_driver_status.run_task(
        'worker-processing-orders-cleanup-stale.testsuite',
    )


async def _run_finished_worker(taxi_driver_status):
    await taxi_driver_status.run_task(
        'worker-processing-orders-cleanup-finished.testsuite',
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_orders_cleanup(
        taxi_driver_status, testpoint, pgsql, mocked_time,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 0

    # 00:00:00
    # insert orders 0-99
    await _insert_processing_orders(
        pgsql, 0, 100, mocked_time.now(), 0, ProcessingStatus.kPending,
    )

    # 00:00:01
    _set_time(mocked_time, now, 1)
    # check count
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 100

    # 00:20:00
    _set_time(mocked_time, now, 1200)
    # finish orders 0-99
    await _insert_processing_orders(
        pgsql, 0, 100, mocked_time.now(), 1, ProcessingStatus.kCancelled,
    )
    # insert orders 100-199
    await _insert_processing_orders(
        pgsql, 100, 100, mocked_time.now(), 0, ProcessingStatus.kAssigned,
    )

    # 00:20:01
    _set_time(mocked_time, now, 1201)
    # check count
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 200

    # 00:40:00
    _set_time(mocked_time, now, 2400)
    # finsh orders 100-199
    await _insert_processing_orders(
        pgsql, 100, 100, mocked_time.now(), 1, ProcessingStatus.kCancelled,
    )
    # insert orders 200-299
    await _insert_processing_orders(
        pgsql, 200, 100, mocked_time.now(), 0, ProcessingStatus.kAssigned,
    )

    # 00:40:01
    _set_time(mocked_time, now, 2401)
    # check count
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 300

    # 01:00:00
    _set_time(mocked_time, now, 3600)
    # finish orders 200-299
    await _insert_processing_orders(
        pgsql, 100, 100, mocked_time.now(), 2, ProcessingStatus.kFinished,
    )

    # 01:00:01
    _set_time(mocked_time, now, 3601)
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 300

    # 01:20:01
    _set_time(mocked_time, now, 4801)
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 200
    await _insert_processing_orders(
        pgsql, 200, 100, mocked_time.now(), 1, ProcessingStatus.kFinished,
    )

    # 02:01:00
    _set_time(mocked_time, now, 7260)
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 100

    # 02:21:00
    _set_time(mocked_time, now, 8460)
    await _run_finished_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 0

    # 02:21:05
    _set_time(mocked_time, now, 8465)
    # insert orders 0-99
    await _insert_processing_orders(
        pgsql, 0, 100, mocked_time.now(), 3, ProcessingStatus.kPending,
    )
    await _run_stale_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 100

    # 2 days 02:21:06
    _set_time(mocked_time, now, 9665)
    await _run_stale_worker(taxi_driver_status)
    assert _get_processing_orders_count(pgsql) == 100
