import datetime

import pytest


EVENTS_TABLES_COUNT = 16
EVENTS_STORE_DAYS = 2
ROWS_COUNT = 100

# corresponds to 2020-11-26, 2020-11-10
FILL_EVENTS_000 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(\'2020-11-10 15:00:00.0+03\', \'online\', \'{}\')::event_tuple]);'
    'COMMIT;'
)


def _make_table_name(i):
    return 'history.events_{:03d}'.format(i)


def _fill_events(pgsql, day_now):
    event_value = (
        'ARRAY[(now(), \'online\'::history.status,'
        '\'{}\')::history.event_tuple]'
    )
    rows = [
        f'(\'parkid{i}\', \'profile_id{i}\', {event_value})'
        for i in range(ROWS_COUNT)
    ]
    values = ','.join(rows)
    cursor = pgsql['contractor_status_history'].cursor()
    for i in range(EVENTS_STORE_DAYS + 1):
        idx = (EVENTS_TABLES_COUNT + day_now - i) % EVENTS_TABLES_COUNT
        table_name = _make_table_name(idx)
        cursor.execute(f'INSERT INTO {table_name} ' f'VALUES {values}')


def _get_events_count(pgsql):
    total = 0
    cursor = pgsql['contractor_status_history'].cursor()
    for i in range(EVENTS_TABLES_COUNT):
        table_name = _make_table_name(i)
        cursor.execute(
            'WITH status_events AS'
            '(SELECT park_id, profile_id, unnest(event_list) '
            f'FROM {table_name}) '
            f'SELECT count(*) FROM status_events;',
        )
        total += cursor.fetchone()[0]

    return total


def _set_time(mocked_time, now, delta_days):
    mocked_time.set(now + datetime.timedelta(days=delta_days))


async def test_events_table_cleanup_near_midnight(
        taxi_contractor_status_history, pgsql, mocked_time,
):
    # set base time to midnight
    now = datetime.datetime(2020, 11, 10)
    mocked_time.set(now)

    day_now = (now - datetime.datetime(1970, 1, 1)).days
    _fill_events(pgsql, day_now)
    total_events = _get_events_count(pgsql)
    assert total_events == (EVENTS_STORE_DAYS + 1) * ROWS_COUNT

    # 30 minutes before midnight
    mocked_time.set(now - datetime.timedelta(minutes=30))
    await taxi_contractor_status_history.run_task(
        'worker-events-table-cleaner.testsuite',
    )
    total_events = _get_events_count(pgsql)
    assert total_events == (EVENTS_STORE_DAYS + 1) * ROWS_COUNT

    # exactly midnight
    mocked_time.set(now)
    await taxi_contractor_status_history.run_task(
        'worker-events-table-cleaner.testsuite',
    )
    total_events = _get_events_count(pgsql)
    assert total_events == (EVENTS_STORE_DAYS + 1) * ROWS_COUNT

    # 30 minutes after midnight
    mocked_time.set(now + datetime.timedelta(minutes=30))
    await taxi_contractor_status_history.run_task(
        'worker-events-table-cleaner.testsuite',
    )
    total_events = _get_events_count(pgsql)
    assert total_events == (EVENTS_STORE_DAYS + 1) * ROWS_COUNT

    # 30 minutes after next day midnight
    mocked_time.set(now + datetime.timedelta(days=1, minutes=30))
    await taxi_contractor_status_history.run_task(
        'worker-events-table-cleaner.testsuite',
    )
    total_events = _get_events_count(pgsql)
    assert total_events == (EVENTS_STORE_DAYS + 1) * ROWS_COUNT


async def test_events_table_cleanup(
        taxi_contractor_status_history, pgsql, mocked_time,
):
    now = datetime.datetime(2020, 11, 10, 12, 0, 0)
    _set_time(mocked_time, now, 0)

    day_now = (now - datetime.datetime(1970, 1, 1)).days
    _fill_events(pgsql, day_now)
    total_events = _get_events_count(pgsql)
    assert total_events == (EVENTS_STORE_DAYS + 1) * ROWS_COUNT

    for i in range(EVENTS_STORE_DAYS + 1):
        _set_time(mocked_time, now, i)
        await taxi_contractor_status_history.run_task(
            'worker-events-table-cleaner.testsuite',
        )

        total_events = _get_events_count(pgsql)
        assert total_events == (EVENTS_STORE_DAYS + 1 - i) * ROWS_COUNT


@pytest.mark.parametrize('archiver_enabled', [False, True])
async def test_not_archived_cleanup(
        taxi_contractor_status_history,
        pgsql,
        mocked_time,
        taxi_config,
        archiver_enabled,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_STATUS_HISTORY_EVENTS_ARCHIVER': {
                'enabled': archiver_enabled,
                'jobs_check_period_min': 60,
                'retry_on_error_period_sec': 5,
                'assume_job_failed_after_sec': 60,
                'batch_size': 1,
                'batch_process_period_ms': 1000,
            },
        },
    )
    await taxi_contractor_status_history.invalidate_caches()

    now = datetime.datetime(2020, 12, 1, 12, 0, 0)
    _set_time(mocked_time, now, 0)

    cursor = pgsql['contractor_status_history'].cursor()
    cursor.execute(FILL_EVENTS_000)
    total_events = _get_events_count(pgsql)
    assert total_events == 1

    await taxi_contractor_status_history.run_task(
        'worker-events-table-cleaner.testsuite',
    )

    total_events = _get_events_count(pgsql)
    if archiver_enabled:
        assert total_events == 1
    else:
        assert total_events == 0


@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_ARCHIVER={
        'enabled': True,
        'jobs_check_period_min': 60,
        'retry_on_error_period_sec': 5,
        'assume_job_failed_after_sec': 60,
        'batch_size': 1,
        'batch_process_period_ms': 1000,
    },
)
@pytest.mark.pgsql('contractor_status_history', queries=[FILL_EVENTS_000])
async def test_not_archived_tomorrow(
        taxi_contractor_status_history, pgsql, mocked_time,
):
    now = datetime.datetime(2020, 11, 25, 12, 0, 0)
    _set_time(mocked_time, now, 0)

    total_events = _get_events_count(pgsql)
    assert total_events == 1

    await taxi_contractor_status_history.run_task(
        'worker-events-table-cleaner.testsuite',
    )

    total_events = _get_events_count(pgsql)
    assert total_events == 0
