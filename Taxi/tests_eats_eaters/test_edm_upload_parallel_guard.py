import datetime


import pytest


import tests_eats_eaters.edm_utils as edm_utils


def lock_db(pgsql):
    connection = pgsql['eats_eaters'].conn
    connection.autocommit = False
    connection.cursor().execute(
        'SELECT * '
        'FROM eats_eaters.edm_upload_state '
        'WHERE id = 1 FOR UPDATE;',
    )
    return connection


def unlock_db(connection):
    connection.rollback()
    connection.autocommit = True


@pytest.mark.now('2020-06-15T14:00:00+00:00')
@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_parallel_guard_db_lock(
        taxi_eats_eaters,
        taxi_eats_eaters_monitor,
        mockserver,
        pgsql,
        testpoint,
):
    await taxi_eats_eaters.tests_control(reset_metrics=True)

    # this testpoint indicates that task was cancelled due to db lock
    @testpoint('testpoint_task_blocked')
    def testpoint_task_blocked(data):
        pass

    # this testpoint indicates that task was cancelled because of
    # short time passed from previous run
    @testpoint('testpoint_task_run_is_too_early')
    def testpoint_task_run_is_too_early(data):
        pass

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        assert {'pairs': edm_utils.user_expected([1, 2])} == request.json
        return mockserver.make_response(status=204)

    psql_cursor = pgsql['eats_eaters'].cursor()

    edm_utils.initialize_meta_table(psql_cursor)

    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')
    edm_utils.insert_eater(psql_cursor, 2, '2020-06-15T13:01:00+00:00')

    last_updated_at = edm_utils.get_last_updated_at(psql_cursor)

    connection = lock_db(pgsql)

    # DB is locked - should be aborted -
    # see `testpoint_task_blocked` testpoint
    await edm_utils.run_task(taxi_eats_eaters)

    # last_updated_at must not change
    new_last_updated_at = edm_utils.get_last_updated_at(psql_cursor)
    assert last_updated_at == new_last_updated_at

    # no call of EDM because task was cancelled
    assert mock_edm_pairs.times_called == 0

    # this testpoint indicates that task was cancelled
    assert testpoint_task_blocked.times_called == 1
    assert testpoint_task_run_is_too_early.times_called == 0

    assert {
        'sent-data': 0,
        'interpolated-chunk-size': 0.0,
        'chunk-size-limit': 2,
        'data-to-send-in-minute-limit': 240.0,
        'sync-delay-real-sec': 0,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 500,
        'real-run-period-ms': 0,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    unlock_db(connection)

    # now everything is OK
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1
    assert testpoint_task_blocked.times_called == 1
    assert testpoint_task_run_is_too_early.times_called == 0

    assert (
        {
            'sent-data': 2,
            'interpolated-chunk-size': 1.0,
            'chunk-size-limit': 2,
            'data-to-send-in-minute-limit': 240.0,
            'sync-delay-real-sec': 3540,
            'sync-delay-offset-sec': 120,
            'run-period-ms': 500,
            'step-time-ms': 0,
        }
        == await edm_utils.get_metric(
            taxi_eats_eaters_monitor, with_real_run_period=False,
        )
    )


NOW_DATETIME = datetime.datetime(
    2020, 6, 15, 14, 0, 0, tzinfo=datetime.timezone.utc,
)


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_parallel_guard_too_early(
        taxi_eats_eaters,
        taxi_eats_eaters_monitor,
        mockserver,
        pgsql,
        testpoint,
        mocked_time,
        rewind_period,
):
    await taxi_eats_eaters.tests_control(reset_metrics=True)

    # this testpoint indicates that task was cancelled due to db lock
    @testpoint('testpoint_task_blocked')
    def testpoint_task_blocked(data):
        pass

    # this testpoint indicates that task was cancelled because of
    # short time passed from previous run
    @testpoint('testpoint_task_run_is_too_early')
    def testpoint_task_run_is_too_early(data):
        pass

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        assert {'pairs': edm_utils.user_expected([1, 2])} == request.json
        return mockserver.make_response(status=204)

    mock_now_value = NOW_DATETIME

    @testpoint('testpoint_mock_now')
    def testpoint_mock_now(data):
        return edm_utils.mock_now(mock_now_value)

    mocked_time.set(NOW_DATETIME)
    await taxi_eats_eaters.invalidate_caches()

    psql_cursor = pgsql['eats_eaters'].cursor()

    psql_cursor.execute(
        'INSERT INTO eats_eaters.edm_upload_state'
        '(id, last_updated_at, last_id, last_run_at)'
        'VALUES(1, \'2020-06-15T12:00:00+00:00\', 0,'
        '\'{}\')'.format(NOW_DATETIME.strftime('%Y-%m-%dT%H:%M:%S%z')),
    )

    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')
    edm_utils.insert_eater(psql_cursor, 2, '2020-06-15T13:01:00+00:00')

    last_updated_at = edm_utils.get_last_updated_at(psql_cursor)

    # DB is locked - should be aborted -
    # see `testpoint_task_blocked` testpoint
    await edm_utils.run_task(taxi_eats_eaters)

    assert testpoint_task_blocked.times_called == 0
    assert testpoint_task_run_is_too_early.times_called == 1
    assert testpoint_mock_now.times_called == 1

    # last_updated_at must not change
    new_last_updated_at = edm_utils.get_last_updated_at(psql_cursor)
    assert last_updated_at == new_last_updated_at

    # no call of EDM because task was cancelled
    assert mock_edm_pairs.times_called == 0

    assert {
        'sent-data': 0,
        'interpolated-chunk-size': 0.0,
        'chunk-size-limit': 2,
        'data-to-send-in-minute-limit': 240.0,
        'sync-delay-real-sec': 0,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 500,
        'real-run-period-ms': 0,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    mock_now_value = await rewind_period()

    # now everything is OK
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1

    assert testpoint_task_blocked.times_called == 0
    assert testpoint_task_run_is_too_early.times_called == 1

    assert testpoint_mock_now.times_called == 4

    assert (
        {
            'sent-data': 2,
            'interpolated-chunk-size': 1.0,
            'chunk-size-limit': 2,
            'data-to-send-in-minute-limit': 240.0,
            'sync-delay-real-sec': 3541,
            'sync-delay-offset-sec': 120,
            'run-period-ms': 500,
            'step-time-ms': 0,
        }
        == await edm_utils.get_metric(
            taxi_eats_eaters_monitor, with_real_run_period=False,
        )
    )
