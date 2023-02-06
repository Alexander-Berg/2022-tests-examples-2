from grabber.generated.service.swagger.models import api


async def test_get_task(web_app_client):
    response_for_fake_id = await web_app_client.get('/v1/tasks/sdas')
    assert response_for_fake_id.status == 404

    driver_time_request = {'data_type': 'driver_timeline', 'data_filter': {}}
    body = {
        'order_id': 'bf86862d4a2a50118be569e8ca683979',
        'data_requests': [driver_time_request],
    }
    create_task_response = await web_app_client.post(
        '/v1/tasks/', json=body, headers={'X-Yandex-Login': 'login'},
    )
    assert create_task_response.status == 200

    task_json = await create_task_response.json()
    task = api.Task.deserialize(task_json)

    response_with_task = await web_app_client.get(f'/v1/tasks/{task.task_id}')
    assert response_with_task.status == 200
