import json

import pytest

UPDATE = 'oktell_update_tasks.json'

QUERY = """
SELECT  "result_data", "csat"
FROM "hiring_telephony_oktell_callback"."tasks"
WHERE
    "task_id" = '{0}'
"""


@pytest.mark.parametrize(
    'type_, name, expected_status',
    [
        ('valid', 'one_update', 200),
        ('valid', 'check_csat', 200),
        ('valid_recall', 'one_update', 200),
        ('valid_recall_different_timezone', 'one_update', 200),
    ],
)
async def test_simple_request(
        load_json,
        create_tasks,
        web_app_client,
        ensure_results,
        web_context,
        type_,
        name,
        expected_status,
):
    if name:
        request = load_json('request_create_tasks.json')['valid']['two_tasks']
        response = await create_tasks(request)
        assert response.status == 200

    update = load_json(UPDATE)[type_][name]
    response = await web_app_client.post(
        '/v1/tasks/oktell/call-result', json={'results': update['results']},
    )
    assert response.status == expected_status
    async with web_context.pg.master_pool.acquire() as conn:
        task = await conn.fetch(QUERY.format(update['results'][0]['task_id']))
        csat = task[0].get('csat')
        if csat:
            assert csat == update['expected_csat']
        result_data = json.loads(task[0]['result_data'])
        expected_result_data = update['expected_result_data']
        assert (
            result_data['call_result'] == expected_result_data['call_result']
        )
        assert (
            result_data['call_result_dt']
            == expected_result_data['call_result_dt']
        )
        assert (
            result_data['operator_id'] == expected_result_data['operator_id']
        )
