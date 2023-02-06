import pytest


@pytest.mark.parametrize(
    'task_id, code',
    [('5GMix9mn36g1hlQtb40FoJ3DYsCZuYrk4', 200), ('wrong id', 404)],
)
async def test_get_task(
        web_app_client,
        mock_eats_core_internal_integrations,
        web_context,
        task_id,
        code,
):
    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):
        return {}

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert response.status == code
    assert not mock_integrations_post.has_calls
