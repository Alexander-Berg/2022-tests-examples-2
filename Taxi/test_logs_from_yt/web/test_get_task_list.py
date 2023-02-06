import pytest


@pytest.mark.parametrize(
    ['params', 'expected_task_id_set'],
    [
        ({'task_id': 'task_1'}, {'task_1'}),
        ({'author': 'user_2'}, {'task_2'}),
        ({'created_date': '2019-06-18'}, {'task_3'}),
        ({'filter_value': 'test_order_id_4'}, {'task_4'}),
        ({'limit': 3}, {'task_2', 'task_3', 'task_4'}),
        ({'offset': 3, 'limit': 1}, {'task_1'}),
    ],
)
async def test_get_task_list(web_app_client, params, expected_task_id_set):
    response = await web_app_client.get(
        '/v1/tasks/list/',
        headers={'X-YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    assert {
        task['task_id'] for task in (await response.json())['tasks']
    } == expected_task_id_set
