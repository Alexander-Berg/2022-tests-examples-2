import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_user_to_project_responses(web_app_client):
    test_samples = [
        {
            'project_slug': 'non_existing_project',
            'user_id': 1,
            'role': 'reader',
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'user_id': 42,
            'role': 'reader',
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'user_id': 2,
            'role': 'reader',
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'user_id': 1,
            'role': 'reader',
            'response_status': 204,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/projects/{test_sample["project_slug"]}/add-user'
            f'?user_id={test_sample["user_id"]}&role={test_sample["role"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_user_to_project_data(web_app_client):
    project_slug = 'test_project'
    user_id = 1
    role = 'admin'
    response_status = 204

    get_user_by_id_response_before = {
        'user': {
            'id': 1,
            'username': 'test_user',
            'is_active': True,
            'is_superadmin': False,
            'created_at': '2021-01-01',
            'provider': 'test_provider',
            'provider_id': '123',
        },
        'accesses': [],
    }

    get_user_by_id_response_after = {
        'user': {
            'id': 1,
            'username': 'test_user',
            'is_active': True,
            'is_superadmin': False,
            'created_at': '2021-01-01',
            'provider': 'test_provider',
            'provider_id': '123',
        },
        'accesses': [
            {
                'project_slug': 'test_project',
                'capabilities': [
                    'project_capability_1',
                    'project_capability_3',
                    'test_capability',
                    'test_capability_3',
                ],
                'role': 'admin',
                'permissions': ['read', 'write', 'modify'],
            },
        ],
    }

    response = await web_app_client.get(f'/v1/users/{user_id}')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_user_by_id_response_before

    response = await web_app_client.post(
        f'/v1/projects/{project_slug}/add-user'
        f'?user_id={user_id}&role={role}',
    )
    assert response.status == response_status

    response = await web_app_client.get(f'/v1/users/{user_id}')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_user_by_id_response_after


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_user_to_project_without_role_data(web_app_client):
    project_slug = 'test_project'
    user_id = 1
    response_status = 204

    get_user_by_id_response_before = {
        'user': {
            'id': 1,
            'username': 'test_user',
            'is_active': True,
            'is_superadmin': False,
            'created_at': '2021-01-01',
            'provider': 'test_provider',
            'provider_id': '123',
        },
        'accesses': [],
    }

    get_user_by_id_response_after = {
        'user': {
            'id': 1,
            'username': 'test_user',
            'is_active': True,
            'is_superadmin': False,
            'created_at': '2021-01-01',
            'provider': 'test_provider',
            'provider_id': '123',
        },
        'accesses': [
            {
                'project_slug': 'test_project',
                'capabilities': [
                    'project_capability_1',
                    'project_capability_3',
                    'test_capability',
                    'test_capability_3',
                ],
                'role': 'reader',
                'permissions': ['read'],
            },
        ],
    }

    response = await web_app_client.get(f'/v1/users/{user_id}')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_user_by_id_response_before

    response = await web_app_client.post(
        f'/v1/projects/{project_slug}/add-user?user_id={user_id}',
    )
    assert response.status == response_status

    response = await web_app_client.get(f'/v1/users/{user_id}')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_user_by_id_response_after
