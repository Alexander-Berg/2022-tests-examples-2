from grabber.generated.service.swagger.models import api


async def test_get_tasks_by_empty_filter(web_app_client):
    await create_tasks(web_app_client)

    limit_param = 10
    params = {'limit': limit_param, 'offset': 0}
    response = await web_app_client.get('/v1/tasks/list', params=params)

    assert response.status == 200

    tasks_list_json = await response.json()
    tasks_list: api.TasksListResponse = api.TasksListResponse.deserialize(
        tasks_list_json,
    )
    assert len(tasks_list.data) == limit_param


async def test_get_tasks_by_filter(web_app_client):
    await create_tasks(web_app_client)

    limit_param = 10
    params = {'limit': limit_param, 'offset': 0, 'driver_uuid': 'driver-1'}
    response = await web_app_client.get('/v1/tasks/list', params=params)

    assert response.status == 200

    tasks_list_json = await response.json()
    tasks_list: api.TasksListResponse = api.TasksListResponse.deserialize(
        tasks_list_json,
    )
    assert len(tasks_list.data) == 1


async def create_tasks(web_app_client):
    driver_timeline_request = {
        'data_type': 'driver_timeline',
        'data_filter': {},
    }

    for i in range(1, 20):
        body = {
            'driver_uuid': f'driver-{i}',
            'start_time': '2020-04-16T16:44:19-0300',
            'end_time': '2020-04-16T16:44:19-0300',
            'data_requests': [driver_timeline_request],
        }

        await web_app_client.post(
            '/v1/tasks/', json=body, headers={'X-Yandex-Login': 'login'},
        )
