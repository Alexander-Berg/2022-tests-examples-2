import pytest


@pytest.mark.parametrize(
    'task_id, code_delete, code_get',
    [('task', 200, 404), ('wrong_id', 200, 404)],
)
async def test_clean_delete_task(
        web_app_client, web_context, task_id, code_delete, code_get,
):
    response = await web_app_client.delete(
        '/v2/tasks/clean', params={'task_id': task_id},
    )
    assert response.status == code_delete

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert response.status == code_get
