# pylint: disable=import-only-modules
import pytest

import tests_contractor_status_history.utils as utils

# current table is event_000
DAY15 = utils.parse_date_str('2020-11-25 00:00:01.0+00')
DAY00 = utils.parse_date_str('2020-11-26 00:00:01.0+00')
DAY01 = utils.parse_date_str('2020-11-27 00:00:01.0+00')
DAY02 = utils.parse_date_str('2020-11-28 00:00:01.0+00')
DAY03 = utils.parse_date_str('2020-11-29 00:00:01.0+00')

# 2020-11-25
FILL_TABLE015 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_015 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(NOW(), \'online\', \'{}\')::event_tuple'
    ']);'
    'COMMIT;'
)

# 2020-11-26
FILL_TABLE000 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(NOW(), \'online\', \'{}\')::event_tuple'
    ']);'
    'COMMIT;'
)

# 2020-11-27
FILL_TABLE001 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_001 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(NOW(), \'online\', \'{}\')::event_tuple'
    ']);'
    'COMMIT;'
)

# 2020-11-28
FILL_TABLE002 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_002 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(NOW(), \'online\', \'{}\')::event_tuple'
    ']);'
    'COMMIT;'
)

FINISH_TABLE015 = 'UPDATE history.events_015 SET arch_finished = true;'

FINISH_TABLE000 = 'UPDATE history.events_000 SET arch_finished = true;'

FINISH_TABLE001 = 'UPDATE history.events_001 SET arch_finished = true;'

FINISH_TABLE002 = 'UPDATE history.events_002 SET arch_finished = true;'


async def _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
):
    _checker_testpoint.flush()

    await taxi_contractor_status_history.run_periodic_task(
        'tables-arch-checker',
    )
    result = await _checker_testpoint.wait_call()
    assert len(result['data']) == 16
    for i in range(0, len(result['data'])):
        # current table is always considered to be not finished
        if i in not_finished_tables:
            assert result['data'][i] is False
            continue
        assert result['data'][i] is True


@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_empty_tables(
        taxi_contractor_status_history, testpoint, mocked_time,
):
    @testpoint('table-arch-state-checker-tp')
    def _checker_testpoint(data):
        pass

    mocked_time.set(DAY15)

    await taxi_contractor_status_history.enable_testpoints()

    _checker_testpoint.flush()

    await taxi_contractor_status_history.run_periodic_task(
        'tables-arch-checker',
    )
    result = await _checker_testpoint.wait_call()
    assert len(result['data']) == 16
    # current table is always considered to be not finished
    for i in range(0, len(result['data'])):
        if i == 15:  # 2020-11-25
            assert result['data'][i] is False
            continue
        assert result['data'][i] is True


@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_checker(
        taxi_contractor_status_history, testpoint, mocked_time, pgsql,
):
    @testpoint('table-arch-state-checker-tp')
    def _checker_testpoint(data):
        pass

    cursor = pgsql['contractor_status_history'].cursor()

    not_finished_tables = set()

    # set today as 2020-11-25
    mocked_time.set(DAY15)
    not_finished_tables.add(15)

    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    cursor.execute(FILL_TABLE015)

    # set today as 2020-11-26
    mocked_time.set(DAY00)
    not_finished_tables.add(0)

    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    cursor.execute(FILL_TABLE000)

    # set today as 2020-11-27
    mocked_time.set(DAY01)
    not_finished_tables.add(1)

    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    cursor.execute(FILL_TABLE001)
    cursor.execute(FINISH_TABLE015)
    not_finished_tables.remove(15)

    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    # set today as 2020-11-28
    mocked_time.set(DAY02)
    not_finished_tables.add(2)

    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    cursor.execute(FILL_TABLE002)
    cursor.execute(FINISH_TABLE000)
    not_finished_tables.remove(0)

    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    cursor.execute(FINISH_TABLE001)
    not_finished_tables.remove(1)
    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    cursor.execute(FINISH_TABLE002)
    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )

    # set today as 2020-11-29
    mocked_time.set(DAY03)
    not_finished_tables.add(3)
    not_finished_tables.remove(2)
    await _check_arch_status(
        taxi_contractor_status_history,
        _checker_testpoint,
        not_finished_tables,
    )
