import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_add_event_by_handle(web_app_client):
    request = {
        'type': 'create',
        'object_type': 'scenario',
        'object_id': '1',
        'object_description': 'Some scenario',
    }

    response = await web_app_client.post(
        '/supportai-tasks/v1/events?user_id=007&project_slug=ya_market',
        json=request,
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['user']['login'] == 'ya_user_4'
    assert response_json['type'] == request['type']
    assert response_json['object_type'] == request['object_type']
    assert response_json['object_id'] == request['object_id']
    assert response_json['object_description'] == request['object_description']

    response = await web_app_client.get(
        '/v1/events?user_id=007&project_id=1&limit=10',
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['events']


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'events.sql'],
)
async def test_get_events(web_app_client):
    response = await web_app_client.get(
        '/v1/events?user_id=34&project_id=1&limit=10',
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['events']) == 4

    response = await web_app_client.get(
        '/v1/events?user_id=34&project_id=1&user_login=ya_user_1&limit=10',
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['events']) == 3

    response = await web_app_client.get(
        '/v1/events?user_id=34&project_id=1&object_types=scenario&limit=10',
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['events']) == 3

    response = await web_app_client.get(
        '/v1/events?user_id=34&project_id=1&object_description=Some&limit=10',
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['events']) == 3
