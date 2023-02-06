import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_project_users_response_statuses(web_app_client):
    test_samples = [
        {'project_slug': 'wrong_project', 'response_status': 404},
        {'project_slug': 'test_project', 'response_status': 200},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/users',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_project_users_data(web_app_client):
    test_samples = [
        {
            'project_slug': 'test_project',
            'response_body': {
                'users': [
                    {'id': 1, 'username': 'test_user', 'group': 'guest'},
                    {'id': 2, 'username': 'test_user_2', 'group': 'guest'},
                    {'id': 4, 'username': 'admin_2', 'group': 'standard'},
                    {'id': 6, 'username': 'test_user_3', 'group': 'standard'},
                    {'id': 7, 'username': 'test_user_4', 'group': 'admin'},
                ],
            },
        },
        {
            'project_slug': 'test_project_2',
            'response_body': {
                'users': [
                    {'id': 2, 'username': 'test_user_2', 'group': 'guest'},
                    {'id': 3, 'username': 'admin', 'group': 'standard'},
                    {'id': 5, 'username': 'admin_3', 'group': 'standard'},
                    {'id': 8, 'username': 'test_user_5', 'group': 'admin'},
                ],
            },
        },
        {'project_slug': 'test_project_3', 'response_body': {'users': []}},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/users',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
