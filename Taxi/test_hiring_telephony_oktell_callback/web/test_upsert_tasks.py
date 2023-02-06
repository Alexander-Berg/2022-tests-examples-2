import json

import pytest

from hiring_telephony_oktell_callback.internal import constants

QUERY_GET_CALL_INTERVALS = """SELECT *
FROM "hiring_telephony_oktell_callback"."call_intervals"
ORDER BY "from" ASC
"""

QUERY_GET_TASKS = """SELECT  archived_at_dt, created_at_dt, data,
deleted_at_dt, expires_at_dt, extra, id, is_expired, is_rotten,
is_sent_to_recall, is_sent_to_sf, is_stopped, lead_id, line_id, priority,
result_data, rots_at_dt, script_id, skillset, task_id, task_name,
task_state, url
FROM "hiring_telephony_oktell_callback"."tasks"
ORDER BY "task_id" ASC
"""

EXPECTED_JSON_FIELDS = ['data', 'skillset', 'result_data', 'extra']


@pytest.mark.now('2021-12-20 00:00:00')
@pytest.mark.usefixtures('geobase')
@pytest.mark.parametrize(
    'name, expected_status, geobase_times_call',
    [('two_tasks', 200, 1), ('future_task', 200, 1)],
)
async def test_insert_and_update_tasks(
        load_json,
        name,
        expected_status,
        web_context,
        taxi_hiring_telephony_oktell_callback_web,
        geobase,
        geobase_times_call,
):
    mock_geobase = geobase()
    request = load_json('request_create_tasks.json')[name]
    expected_results = load_json('expected_results.json')[name]

    # insert
    response = await taxi_hiring_telephony_oktell_callback_web.post(
        constants.TASKS_UPSERT_URL, json={'tasks': request['tasks']},
    )
    assert response.status == expected_status
    data = await response.json()
    assert data == expected_results['insert']

    async with web_context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(QUERY_GET_CALL_INTERVALS)
        prepared_result = [_prepare_result(dict(result)) for result in results]
        assert prepared_result == expected_results['intervals']

    async with web_context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(QUERY_GET_TASKS)
        prepared_result = [_prepare_result(dict(result)) for result in results]
        assert prepared_result == expected_results['tasks']
    assert mock_geobase.times_called == geobase_times_call

    # update
    response = await taxi_hiring_telephony_oktell_callback_web.post(
        constants.TASKS_UPSERT_URL, json={'tasks': request['tasks']},
    )
    assert response.status == expected_status
    data = await response.json()
    assert data == expected_results['update']


def _prepare_result(result: dict):
    for dct in EXPECTED_JSON_FIELDS:
        if result.get(dct):
            result[dct] = json.loads(result[dct])
    return result
