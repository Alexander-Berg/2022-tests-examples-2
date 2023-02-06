import datetime
import json

import pytest


async def _run_worker(taxi_driver_status):
    await taxi_driver_status.run_task('worker-statuses-cleanup.testsuite')


async def _insert_status(taxi_driver_status, suffix):
    response = await taxi_driver_status.post(
        'v1/internal/status',
        data=json.dumps(
            {
                'park_id': f'parkid{suffix}',
                'driver_id': f'driverid{suffix}',
                'status': 'offline',
            },
        ),
    )
    assert response.status_code == 200


async def _insert_statuses(taxi_driver_status, start, count):
    for i in range(start, start + count):
        await _insert_status(taxi_driver_status, i)


def _get_statuses_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.statuses')
    return cursor.fetchone()[0]


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_statuses_cleanup(taxi_driver_status, pgsql, mocked_time):
    mocked_time.set(datetime.datetime.utcnow())

    await _insert_statuses(taxi_driver_status, 0, 100)
    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 100

    mocked_time.sleep(1201)  # 00:20:01 from start
    await _insert_statuses(taxi_driver_status, 100, 100)
    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 200

    mocked_time.sleep(1200)  # 00:40:01 from start
    await _insert_statuses(taxi_driver_status, 200, 100)
    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 300

    mocked_time.sleep(1200)  # 01:00:01 from start
    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 200

    mocked_time.sleep(3600)  # 02:00:01 from start
    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 0
