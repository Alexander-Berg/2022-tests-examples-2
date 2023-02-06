from grabber.generated.service.swagger.models import api


async def test_create_task_with_order_id(web_app_client):
    driver_timeline_request = {
        'data_type': 'driver_timeline',
        'data_filter': {},
    }
    body = {
        'order_id': 'bf86862d4a2a50118be569e8ca683979',
        'data_requests': [driver_timeline_request],
    }
    response = await web_app_client.post(
        '/v1/tasks/', json=body, headers={'X-Yandex-Login': 'login'},
    )
    assert response.status == 200

    task = await get_task(response)
    assert task
    assert task.task_id
    assert task.order_id


async def test_create_task_with_driver_id(web_app_client):
    driver_timeline_request = {
        'data_type': 'driver_timeline',
        'data_filter': {},
    }
    body = {
        'driver_uuid': 'bf86862d4a2a50118be569e8ca683979',
        'start_time': '2020-04-16T16:44:19-0300',
        'end_time': '2020-04-16T16:44:19-0300',
        'data_requests': [driver_timeline_request],
    }
    response = await web_app_client.post(
        '/v1/tasks/', json=body, headers={'X-Yandex-Login': 'login'},
    )
    assert response.status == 200

    task = await get_task(response)
    assert task
    assert task.task_id
    assert task.driver_uuid
    assert task.start_time
    assert task.end_time


async def get_task(response) -> api.Task:
    task_json = await response.json()
    return api.Task.deserialize(task_json)
