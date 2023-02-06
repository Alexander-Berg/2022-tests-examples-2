import pytest


@pytest.mark.parametrize('cube_name', ['NotificationsCubeLenta'])
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'enable_lenta_notifications': True})
async def test_post_notifications_cube_handles(
        web_app_client, cube_name, load_json, patch,
):
    @patch(
        'clownductor.generated.service.lenta_api.'
        'plugin.LentaClient.post_to_lenta',
    )
    async def _post_to_lenta(*args, **kwargs):
        return {}

    @patch('generated.clients.infra_events.InfraEventsClient.v1_events_post')
    async def _v1_events_post(*args, **kwargs):
        return {}

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
