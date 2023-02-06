import datetime
import logging


import pytest


import tests_eats_eaters.edm_utils as edm_utils


NOW_DATETIME = datetime.datetime(
    2020, 6, 15, 14, 0, 0, tzinfo=datetime.timezone.utc,
)


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_get_metrics(
        taxi_eats_eaters,
        taxi_eats_eaters_monitor,
        mockserver,
        pgsql,
        mocked_time,
        testpoint,
        taxi_config,
        rewind_period,
):
    await taxi_eats_eaters.tests_control(reset_metrics=True)

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        return mockserver.make_response(status=204)

    mock_now_value = NOW_DATETIME

    @testpoint('testpoint_mock_now')
    def testpoint_mock_now(data):
        return edm_utils.mock_now(mock_now_value)

    @testpoint('testpoint_step_time')
    async def testpoint_step_time(data):
        if phase == 7:
            mocked_time.sleep(1.123)
            await taxi_eats_eaters.invalidate_caches()
        return {}

    psql_cursor = pgsql['eats_eaters'].cursor()

    edm_utils.initialize_meta_table(psql_cursor)

    # chunk 1
    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')
    edm_utils.insert_eater(psql_cursor, 2, '2020-06-15T13:01:00+00:00')

    # chunk 2
    edm_utils.insert_eater(psql_cursor, 3, '2020-06-15T13:05:00+00:00')

    # chunk 3
    # nothing =)

    # rewind time here

    # chunk 4
    edm_utils.insert_eater(psql_cursor, 4, '2020-06-15T13:59:59+00:00')

    # rewind time here

    # chunk 5
    edm_utils.insert_eater(psql_cursor, 5, '2020-06-15T14:01:00+00:00')
    edm_utils.insert_eater(psql_cursor, 6, '2020-06-15T14:02:00+00:00')
    edm_utils.insert_eater(psql_cursor, 7, '2020-06-15T14:03:00+00:00')
    edm_utils.insert_eater(psql_cursor, 8, '2020-06-15T14:03:00+00:00')
    edm_utils.insert_eater(psql_cursor, 9, '2020-06-15T14:03:00+00:00')

    # chunk 6
    edm_utils.insert_eater(psql_cursor, 10, '2020-06-15T14:04:00+00:00')

    # chunk 7
    # nothing =)

    mocked_time.set(NOW_DATETIME)
    await taxi_eats_eaters.invalidate_caches()

    ########################################
    phase = 1
    logging.info('==== Phase #%d ====', phase)
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 1
    assert testpoint_mock_now.times_called == 3

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

    ########################################
    phase = 2
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 2
    assert testpoint_mock_now.times_called == 6
    assert testpoint_step_time.times_called == phase
    assert {
        'sent-data': 3,
        'interpolated-chunk-size': 1.5,
        'chunk-size-limit': 2,
        'data-to-send-in-minute-limit': 240.0,
        'sync-delay-real-sec': 3301,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 500,
        'real-run-period-ms': 1500,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    ########################################
    phase = 3
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 2
    assert testpoint_mock_now.times_called == 9
    assert testpoint_step_time.times_called == phase
    assert {
        'sent-data': 3,
        'interpolated-chunk-size': 1.5,
        'chunk-size-limit': 2,
        'data-to-send-in-minute-limit': 240.0,
        'sync-delay-real-sec': 120,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 500,
        'real-run-period-ms': 2000,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    ########################################
    phase = 4
    logging.info('==== Phase #%d ====', phase)
    mocked_time.sleep(120)
    await taxi_eats_eaters.invalidate_caches()
    mock_now_value = mocked_time.now()
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 3
    assert testpoint_mock_now.times_called == 12
    assert testpoint_step_time.times_called == phase
    assert {
        'sent-data': 4,
        'interpolated-chunk-size': 2,
        'chunk-size-limit': 2,
        'data-to-send-in-minute-limit': 240.0,
        'sync-delay-real-sec': 124,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 500,
        'real-run-period-ms': 120000,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    ########################################
    phase = 5
    logging.info('==== Phase #%d ====', phase)
    confing_value = edm_utils.get_default_config(5)
    confing_value['eats-eaters']['upload_period_ms'] = 2000
    taxi_config.set_values({'EATS_DATA_MAPPINGS_UPLOAD_PARAMS': confing_value})
    mocked_time.sleep(300)
    await taxi_eats_eaters.invalidate_caches()
    mock_now_value = mocked_time.now()
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 4
    assert testpoint_mock_now.times_called == 15
    assert testpoint_step_time.times_called == phase
    assert {
        'sent-data': 9,
        'interpolated-chunk-size': 12,
        'chunk-size-limit': 5,
        'data-to-send-in-minute-limit': 150.0,
        'sync-delay-real-sec': 243,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 2000,
        'real-run-period-ms': 300000,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    ########################################
    phase = 6
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 5
    assert testpoint_mock_now.times_called == 18
    assert testpoint_step_time.times_called == phase
    assert {
        'sent-data': 10,
        'interpolated-chunk-size': 14.0,
        'chunk-size-limit': 5,
        'data-to-send-in-minute-limit': 150.0,
        'sync-delay-real-sec': 186,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 2000,
        'real-run-period-ms': 3000,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

    ########################################
    phase = 7
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)

    assert mock_edm_pairs.times_called == 5
    assert testpoint_mock_now.times_called == 21
    assert testpoint_step_time.times_called == phase
    assert {
        'sent-data': 10,
        'interpolated-chunk-size': 14.0,
        'chunk-size-limit': 5,
        'data-to-send-in-minute-limit': 150.0,
        'sync-delay-real-sec': 120,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 2000,
        'real-run-period-ms': 4123,  # see testpoint_step_time
        # the only place this is tested, see testpoint_step_time
        'step-time-ms': 1123,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)
