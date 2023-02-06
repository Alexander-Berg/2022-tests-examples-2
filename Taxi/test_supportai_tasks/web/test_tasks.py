import datetime

import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_create_task(web_app_client):

    task_type = 'import'

    response = await web_app_client.post(
        '/v1/tasks?user_id=34&project_slug=ya_market',
        json={'type': task_type},
    )
    assert response.status == 200

    response_json = await response.json()

    assert response_json['user']['login'] == 'ya_user_1'
    assert response_json['type'] == task_type
    assert response_json['project_id'] == '1'
    assert response_json['status'] == 'created'

    response = await web_app_client.get(
        '/v1/events?user_id=34&project_id=1&limit=10',
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['events']) == 1


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'tasks.sql'],
)
async def test_get_tasks(web_app_client):
    response = await web_app_client.get(
        '/v1/tasks?user_id=34&project_slug=ya_market',
    )

    assert response.status == 200

    response_json = await response.json()

    tasks = response_json['tasks']
    assert len(tasks) == 8

    error_task = tasks[3]

    assert error_task['type'] == 'export'
    assert error_task['status'] == 'error'
    assert error_task['error_message']
    assert error_task['user']['login'] == 'ya_user_1'

    response = await web_app_client.get(
        '/v1/tasks?user_id=34&project_slug=ya_market'
        '&types=outgoing_calls_init,export',
    )
    assert response.status == 200
    response_json = await response.json()
    tasks = response_json['tasks']
    assert len(tasks) == 4

    response = await web_app_client.get(
        '/v1/tasks?user_id=34&project_slug=ya_market&ref_task_id=2',
    )
    assert response.status == 200
    response_json = await response.json()
    tasks = response_json['tasks']
    assert len(tasks) == 1

    response = await web_app_client.get(
        '/v1/tasks?user_id=34&project_slug=ya_market'
        '&types=outgoing_calls_init',
    )
    assert response.status == 200
    response_json = await response.json()
    tasks = response_json['tasks']
    assert len(tasks) == 3

    assert tasks[1]['name'] == 'calls_1'
    assert 'name' not in tasks[2]
    assert tasks[1]['user']['login'] == 'ya_user_1'
    assert 'user' not in tasks[2]

    older_than = (
        datetime.datetime.fromisoformat('2021-01-01T15:00:00').timestamp()
        * 1000
    )
    response = await web_app_client.get(
        f'/v1/tasks?user_id=34&project_slug=ya_market'
        f'&limit=5&older_than={int(older_than)}'
        f'&types=outgoing_calls_init,outgoing_calls_results',
    )
    assert response.status == 200
    response_json = await response.json()
    tasks = response_json['tasks']
    assert len(tasks) == 4

    response = await web_app_client.get(
        '/v1/tasks?user_id=34&project_slug=ya_market&ref_task_id=',
    )
    assert response.status == 200
    response_json = await response.json()
    tasks = response_json['tasks']
    assert len(tasks) == 1
    assert tasks[0]['id'] == '5'


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'tasks.sql'],
)
async def test_internal_get_task(web_app_client):
    response = await web_app_client.get('/supportai-tasks/v1/tasks/1')
    assert response.status == 200

    response_json = await response.json()

    assert response_json['type'] == 'export'


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'tasks.sql'],
)
async def test_internal_get_tasks_multiple(web_app_client):
    response = await web_app_client.post(
        'supportai-tasks/v1/tasks/get_multiple'
        '?project_slug=ya_market&type=outgoing_calls_init',
        json={'task_ids': ['1', '3', '4', '6']},
    )
    assert response.status == 200
    response_json = await response.json()
    task_ids = [task['id'] for task in response_json['tasks']]
    assert task_ids == ['3']

    response = await web_app_client.post(
        'supportai-tasks/v1/tasks/get_multiple'
        '?project_slug=ya_market&type=outgoing_calls_results',
        json={'task_ids': ['1', '3', '4', '6']},
    )
    assert response.status == 200
    response_json = await response.json()
    task_ids = [task['id'] for task in response_json['tasks']]
    assert task_ids == ['4']


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'tasks.sql'],
)
async def test_internal_update_task(web_app_client):
    response = await web_app_client.put(
        '/supportai-tasks/v1/tasks/2',
        json={
            'id': '2',
            'project_id': '1',
            'type': 'validation',
            'created': str(datetime.datetime.now()),
            'status': 'error',
            'error_message': 'test',
            'processing_state': 'error',
            'params': {'some_extra': 'value'},
        },
    )
    assert response.status == 200

    response_json = await response.json()

    assert response_json['status'] == 'error'
    assert response_json['error_message'] == 'test'
    assert response_json['type'] == 'outgoing_calls_init'


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_internal_create_task(web_app_client):

    task_type = 'import'

    response = await web_app_client.post(
        '/supportai-tasks/v1/tasks',
        json={'type': task_type, 'project_slug': 'ya_market'},
    )
    assert response.status == 200
