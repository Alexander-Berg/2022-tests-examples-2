import pytest


@pytest.mark.parametrize(
    'task_id, code',
    [('5GMix9mn36g1hlQtb40FoJ3DYsCZuYrk4', 200), ('wrong id', 404)],
)
async def test_get_task(web_app_client, web_context, task_id, code):
    response = await web_app_client.delete(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert response.status == code
