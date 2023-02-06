import datetime
import logging


import pytest


import tests_eats_eaters.edm_utils as edm_utils


NOW_DATETIME = datetime.datetime(
    2020, 6, 15, 14, 0, 0, tzinfo=datetime.timezone.utc,
)


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(5),
)
async def test_edm_task_chunk_size_is_5(
        taxi_eats_eaters,
        mockserver,
        pgsql,
        mocked_time,
        testpoint,
        rewind_period,
):
    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        if phase == 1:
            assert {
                'pairs': edm_utils.user_expected([1, 2, 3, 4, 5]),
            } == request.json
        if phase == 2:
            assert {
                'pairs': edm_utils.user_expected([6, 7, 8, 9, 10]),
            } == request.json
        if phase == 3:
            assert {
                'pairs': edm_utils.user_expected([11, 12, 13, 14, 15]),
            } == request.json
        if phase == 4:
            assert {'pairs': edm_utils.user_expected([16, 17])} == request.json
        assert phase != 5  # just nothing =)
        if phase == 6:
            assert {'pairs': edm_utils.user_expected(18)} == request.json
        return mockserver.make_response(status=204)

    mock_now_value = NOW_DATETIME

    @testpoint('testpoint_mock_now')
    def testpoint_mock_now(data):
        return edm_utils.mock_now(mock_now_value)

    psql_cursor = pgsql['eats_eaters'].cursor()

    edm_utils.initialize_meta_table(psql_cursor)

    # chunk 1
    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')
    edm_utils.insert_eater(psql_cursor, 2, '2020-06-15T13:01:00+00:00')  # 1
    edm_utils.insert_eater(psql_cursor, 3, '2020-06-15T13:01:00+00:00')  # 1
    edm_utils.insert_eater(psql_cursor, 4, '2020-06-15T13:01:00+00:00')  # 1
    edm_utils.insert_eater(psql_cursor, 5, '2020-06-15T13:01:00+00:00')  # 1

    # chunk 2
    edm_utils.insert_eater(psql_cursor, 6, '2020-06-15T13:01:00+00:00')  # 1
    edm_utils.insert_eater(psql_cursor, 7, '2020-06-15T13:01:00+00:00')  # 1
    edm_utils.insert_eater(psql_cursor, 8, '2020-06-15T13:02:00+00:00')  # 2
    edm_utils.insert_eater(psql_cursor, 9, '2020-06-15T13:02:00+00:00')  # 2
    edm_utils.insert_eater(psql_cursor, 10, '2020-06-15T13:02:00+00:00')  # 2

    # chunk 3
    edm_utils.insert_eater(psql_cursor, 11, '2020-06-15T13:02:00+00:00')  # 2
    edm_utils.insert_eater(psql_cursor, 12, '2020-06-15T13:02:00+00:00')  # 2
    edm_utils.insert_eater(psql_cursor, 13, '2020-06-15T13:02:00+00:00')  # 2
    edm_utils.insert_eater(psql_cursor, 14, '2020-06-15T13:02:00+00:00')  # 2
    edm_utils.insert_eater(psql_cursor, 15, '2020-06-15T13:02:00+00:00')  # 2

    # chunk 4
    edm_utils.insert_eater(psql_cursor, 16, '2020-06-15T13:07:00+00:00')  # 7
    edm_utils.insert_eater(psql_cursor, 17, '2020-06-15T13:07:00+00:00')  # 7

    # chunk 5
    # nothing =)

    # rewind time here

    # chunk 6
    edm_utils.insert_eater(psql_cursor, 18, '2020-06-15T13:59:59+00:00')

    mocked_time.set(NOW_DATETIME)
    await taxi_eats_eaters.invalidate_caches()

    phase = 1
    logging.info('==== Phase #%d ====', phase)
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1
    assert testpoint_mock_now.times_called == 3

    phase = 2
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 2
    assert testpoint_mock_now.times_called == 6

    phase = 3
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 3
    assert testpoint_mock_now.times_called == 9

    phase = 4
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 4
    assert testpoint_mock_now.times_called == 12

    phase = 5
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 4
    assert testpoint_mock_now.times_called == 15

    phase = 6
    logging.info('==== Phase #%d ====', phase)
    mocked_time.sleep(120)
    await taxi_eats_eaters.invalidate_caches()
    mock_now_value = mocked_time.now()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 5
    assert testpoint_mock_now.times_called == 18
