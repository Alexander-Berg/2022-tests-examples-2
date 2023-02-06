from grabber.generated.service.swagger.models import api


async def test_create_task_with_order_id(web_app_client):
    driver_timeline_request = {
        'data_type': 'driver_timeline',
        'data_filter': {},
    }
    post_body = {
        'order_id': 'bf86862d4a2a50118be569e8ca683979',
        'data_requests': [driver_timeline_request],
    }
    post_response = await web_app_client.post(
        '/v1/tasks/', json=post_body, headers={'X-Yandex-Login': 'login'},
    )
    assert post_response.status == 200

    task = await get_task(post_response)

    put_body = {
        'order_id': 'bf86862d4a2a50118be569e8ca683979',
        'data_requests': [driver_timeline_request],
    }
    put_response = await web_app_client.put(
        '/v1/tasks/{task_id}'.format(task_id=task.task_id),
        json=put_body,
        headers={'X-Yandex-Login': 'login'},
    )
    assert put_response.status == 200


async def get_task(response) -> api.Task:
    task_json = await response.json()
    return api.Task.deserialize(task_json)
