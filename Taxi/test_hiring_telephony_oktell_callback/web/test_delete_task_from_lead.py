import pytest


QUERY = """SELECT task_id, is_stopped, task_state
FROM "hiring_telephony_oktell_callback"."tasks"
WHERE
    "task_id" in ('%s')
"""


@pytest.mark.parametrize(
    'lead_id, expected_status, expected_result',
    [
        ('lead_id', 200, {'results': []}),
        (
            'lead_id_1',
            200,
            {
                'results': [
                    {'task_id': 'task_id_1', 'deleted': True, 'reason': ''},
                    {'task_id': 'task_id_3', 'deleted': True, 'reason': ''},
                    {'task_id': 'task_id_5', 'deleted': True, 'reason': ''},
                ],
            },
        ),
        (
            'lead_id_2',
            200,
            {
                'results': [
                    {'task_id': 'task_id_4', 'deleted': True, 'reason': ''},
                ],
            },
        ),
    ],
)
async def test_request(
        web_app_client, lead_id, expected_status, expected_result, web_context,
):
    response = await web_app_client.post(
        '/v1/tasks/delete', json={'lead': {'id': lead_id}},
    )
    assert response.status == expected_status
    result = await response.json()
    result['results'] = sorted(result['results'], key=lambda i: i['task_id'])
    assert result == expected_result
    task_ids = [item['task_id'] for item in result['results']]
    async with web_context.pg.master_pool.acquire() as conn:
        items = await conn.fetch(QUERY % '\',\''.join(task_ids))
        for item in items:
            assert item['is_stopped']
            assert item['task_state'] == 'processed'
