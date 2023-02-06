import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_project_user_response_statuses(web_app_client):
    test_samples = [
        {
            'project_slug': 'wrong_project',
            'request_body': {'id': 1, 'group': 'guest'},
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'request_body': {'id': 42, 'group': 'guest'},
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'request_body': {'id': 1, 'group': 'guest'},
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'request_body': {'id': 3, 'group': 'wrong_group'},
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'request_body': {'id': 3, 'group': 'guest'},
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/projects/{test_sample["project_slug"]}/users',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_project_user_data(web_app_client):
    project_slug = 'test_project'
    request_body = {'id': 3, 'group': 'guest'}
    response_body = {'id': 3, 'username': 'admin', 'group': 'guest'}

    users_response_before = {
        'users': [
            {'id': 1, 'username': 'test_user', 'group': 'guest'},
            {'id': 2, 'username': 'test_user_2', 'group': 'guest'},
            {'id': 4, 'username': 'admin_2', 'group': 'standard'},
            {'id': 6, 'username': 'test_user_3', 'group': 'standard'},
            {'id': 7, 'username': 'test_user_4', 'group': 'admin'},
        ],
    }

    users_response_after = {
        'users': [
            {'id': 1, 'username': 'test_user', 'group': 'guest'},
            {'id': 2, 'username': 'test_user_2', 'group': 'guest'},
            {'id': 3, 'username': 'admin', 'group': 'guest'},
            {'id': 4, 'username': 'admin_2', 'group': 'standard'},
            {'id': 6, 'username': 'test_user_3', 'group': 'standard'},
            {'id': 7, 'username': 'test_user_4', 'group': 'admin'},
        ],
    }

    response = await web_app_client.get(f'/v1/projects/{project_slug}/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == users_response_before

    response = await web_app_client.post(
        f'/v1/projects/{project_slug}/users', json=request_body,
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == response_body

    response = await web_app_client.get(f'/v1/projects/{project_slug}/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == users_response_after
