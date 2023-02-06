# pylint: disable=broad-except

import datetime


import pytest


import tests_eats_eaters.edm_utils as edm_utils


NOW_DATETIME = datetime.datetime(
    2020, 6, 15, 14, 0, 0, tzinfo=datetime.timezone.utc,
)


LAST_UPDATED_AT = datetime.datetime(
    2020, 6, 15, 13, 1, 0, tzinfo=datetime.timezone.utc,
)

USER1_DATETIME = '2020-06-15T13:00:00+00:00'
USER2_DATETIME = LAST_UPDATED_AT.strftime('%Y-%m-%dT%H:%M:%S%z')
USER3_DATETIME = '2020-06-15T13:05:00+00:00'


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_fail_edm_send(
        taxi_eats_eaters, mockserver, pgsql, testpoint, rewind_period,
):
    # inject error or not flag
    edm_sent_fail = False

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        if edm_sent_fail:
            # inject error
            assert {'pairs': edm_utils.user_expected(3)} == request.json
            return mockserver.make_response('bad request', status=400)
        # else
        assert {'pairs': edm_utils.user_expected([1, 2])} == request.json
        return mockserver.make_response(status=204)

    mock_now_value = NOW_DATETIME

    @testpoint('testpoint_mock_now')
    def testpoint_mock_now(data):
        return edm_utils.mock_now(mock_now_value)

    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.initialize_meta_table(psql_cursor)

    # just some data - doesn't matter what
    edm_utils.insert_eater(psql_cursor, 1, USER1_DATETIME)
    edm_utils.insert_eater(psql_cursor, 2, USER2_DATETIME)
    edm_utils.insert_eater(psql_cursor, 3, USER3_DATETIME)

    # first time everithing should be fine
    await edm_utils.run_task(taxi_eats_eaters)

    last_updated_at = edm_utils.get_last_updated_at(psql_cursor)
    assert last_updated_at == LAST_UPDATED_AT

    # now we inject error in EDM
    # there have to be an exception in task
    # and `last_updated_at` should not be updated
    # but exception should be intercepted
    edm_sent_fail = True
    there_was_an_exception = False
    try:
        mock_now_value = await rewind_period()
        await edm_utils.run_task(taxi_eats_eaters)
    except Exception:
        there_was_an_exception = True

    # must have no exception
    # all exceptions should be intercepted
    assert not there_was_an_exception

    # should not been changed
    last_updated_at = edm_utils.get_last_updated_at(psql_cursor)
    assert last_updated_at == LAST_UPDATED_AT

    assert testpoint_mock_now.times_called == 5
    assert mock_edm_pairs.times_called == 2
