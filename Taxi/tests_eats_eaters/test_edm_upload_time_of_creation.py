import datetime
import logging


import pytest


import tests_eats_eaters.edm_utils as edm_utils


NOW_DATETIME = datetime.datetime(
    2020, 6, 15, 14, 0, 0, tzinfo=datetime.timezone.utc,
)


@pytest.mark.uservice_oneshot(
    config_hooks=[edm_utils.start_mode_patch_config(start_from_now=False)],
)
@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_send_time_of_creation(
        taxi_eats_eaters,
        mockserver,
        pgsql,
        mocked_time,
        testpoint,
        rewind_period,
):
    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        assert phase != 0
        if phase == 1:
            assert {
                'pairs': edm_utils.user_expected(
                    [
                        (1, '2016-06-15T13:01:00+00:00'),
                        (2, '2016-06-15T13:02:00+00:00'),
                    ],
                ),
            } == request.json
        if phase == 2:
            assert {
                'pairs': edm_utils.user_expected(
                    [
                        (3, '2016-06-15T13:03:00+00:00'),
                        (4, '2016-06-15T13:04:00+00:00'),
                    ],
                ),
            } == request.json
        if phase == 3:
            assert {
                'pairs': edm_utils.user_expected(
                    [
                        (5, '2016-06-15T13:05:00+00:00'),
                        (6, '2016-06-15T13:06:00+00:00'),
                    ],
                ),
            } == request.json
        return mockserver.make_response(status=204)

    mock_now_value = NOW_DATETIME

    @testpoint('testpoint_mock_now')
    def testpoint_mock_now(data):
        return edm_utils.mock_now(mock_now_value)

    psql_cursor = pgsql['eats_eaters'].cursor()

    # chunk 1
    edm_utils.insert_eater(
        psql_cursor,
        1,
        '2016-06-15T13:00:00+00:00',
        '2016-06-15T13:01:00+00:00',
    )
    edm_utils.insert_eater(
        psql_cursor,
        2,
        '2017-06-15T13:00:00+00:00',
        '2016-06-15T13:02:00+00:00',
    )

    # chunk 2
    edm_utils.insert_eater(
        psql_cursor,
        3,
        '2018-06-15T13:00:00+00:00',
        '2016-06-15T13:03:00+00:00',
    )
    edm_utils.insert_eater(
        psql_cursor,
        4,
        '2019-06-15T13:00:00+00:00',
        '2016-06-15T13:04:00+00:00',
    )

    # chunk 3
    edm_utils.insert_eater(
        psql_cursor,
        5,
        '2020-06-15T13:00:00+00:00',
        '2016-06-15T13:05:00+00:00',
    )
    edm_utils.insert_eater(
        psql_cursor,
        6,
        '2020-06-15T13:05:00+00:00',
        '2016-06-15T13:06:00+00:00',
    )

    mocked_time.set(NOW_DATETIME)
    await taxi_eats_eaters.invalidate_caches()

    # just init last iteration data
    phase = 0
    logging.info('==== Phase #%d ====', phase)
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 0
    assert testpoint_mock_now.times_called == 1

    phase = 1
    logging.info('==== Phase #%d ====', phase)
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1
    assert testpoint_mock_now.times_called == 4

    phase = 2
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 2
    assert testpoint_mock_now.times_called == 7

    phase = 3
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 3
    assert testpoint_mock_now.times_called == 10
