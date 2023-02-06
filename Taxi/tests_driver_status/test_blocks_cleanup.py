import datetime

import pytest

import tests_driver_status.pg_helpers as pg_helpers


def _set_time(mocked_time, now, delta_sec):
    mocked_time.set(now + datetime.timedelta(seconds=delta_sec))


def _make_insert_blocks_queries(reason_id, timestamp, start, count):
    return [
        pg_helpers.make_drivers_insert_query(timestamp, start, count),
        pg_helpers.make_blocks_update_insert_query(timestamp, start, count),
        pg_helpers.make_blocks_insert_query(
            reason_id, timestamp, start, count,
        ),
    ]


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_blocks_cleanup(taxi_driver_status, pgsql, mocked_time):
    async def _run_worker():
        await taxi_driver_status.run_task('worker-blocks-cleanup.testsuite')

    reason_id = pg_helpers.check_blocked_reason_id(pgsql, 'driver_blacklist')

    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 0

    # 00:00:00
    # insert blocks drivers 0-99
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 0, 100),
    )

    # 00:00:01
    _set_time(mocked_time, now, 1)
    # check count
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 100

    # 00:20:00
    _set_time(mocked_time, now, 1200)
    # insert blocks for drivers 100-199
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 100, 100),
    )

    # 00:20:01
    _set_time(mocked_time, now, 1201)
    # check count
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 200

    # 00:40:00
    _set_time(mocked_time, now, 2400)
    # insert blocks for drivers 200-299
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 200, 100),
    )

    # 00:40:01
    _set_time(mocked_time, now, 2401)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 300

    # 01:00:00
    _set_time(mocked_time, now, 3600)
    # insert blocks for drivers 300-399
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 300, 100),
    )
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 400

    # 01:00:01
    _set_time(mocked_time, now, 3601)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 300

    # 01:20:01
    _set_time(mocked_time, now, 4801)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 200

    # 01:40:01
    _set_time(mocked_time, now, 6001)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 100

    # 02:00:01
    _set_time(mocked_time, now, 7201)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 0


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_blocks_cleanup_none(taxi_driver_status, pgsql, mocked_time):
    async def _run_worker():
        await taxi_driver_status.run_task(
            'worker-blocks-cleanup-none.testsuite',
        )

    reason_id = pg_helpers.check_blocked_reason_id(pgsql, 'none')

    now = datetime.datetime.now(datetime.timezone.utc)
    _set_time(mocked_time, now, 0)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 0

    # 00:00:00
    # insert blocks drivers 0-99
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 0, 100),
    )

    # 00:00:01
    _set_time(mocked_time, now, 1)
    # check count
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 100

    # 00:30:00
    _set_time(mocked_time, now, 1800)
    # insert blocks for drivers 100-199
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 100, 100),
    )

    # 00:30:01
    _set_time(mocked_time, now, 1801)
    # check count
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 200

    # 01:00:00
    _set_time(mocked_time, now, 3600)
    # insert blocks for drivers 200-299
    pg_helpers.run_in_transaction(
        pgsql,
        _make_insert_blocks_queries(reason_id, mocked_time.now(), 200, 100),
    )

    # 01:00:01
    _set_time(mocked_time, now, 3601)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 200

    # 01:30:01
    _set_time(mocked_time, now, 5401)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 100

    # 02:00:01
    _set_time(mocked_time, now, 7201)
    await _run_worker()
    assert pg_helpers.get_blocks_count(pgsql) == 0
