import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_delete_project_users_response_statuses(web_app_client):
    test_samples = [
        {
            'project_slug': 'wrong_project',
            'user_id': 1,
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'user_id': 42,
            'response_status': 400,
        },
        {'project_slug': 'test_project', 'user_id': 1, 'response_status': 204},
    ]

    for test_sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/projects/{test_sample["project_slug"]}'
            f'/users/{test_sample["user_id"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_delete_project_users_data(web_app_client):
    project_slug = 'test_project'
    user_id = 1

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
            {'id': 2, 'username': 'test_user_2', 'group': 'guest'},
            {'id': 4, 'username': 'admin_2', 'group': 'standard'},
            {'id': 6, 'username': 'test_user_3', 'group': 'standard'},
            {'id': 7, 'username': 'test_user_4', 'group': 'admin'},
        ],
    }

    response = await web_app_client.get(f'/v1/projects/{project_slug}/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == users_response_before

    response = await web_app_client.delete(
        f'/v1/projects/{project_slug}/users/{user_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(f'/v1/projects/{project_slug}/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == users_response_after
