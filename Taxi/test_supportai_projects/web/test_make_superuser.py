import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_make_superuser_404(web_app_client):
    user_id = 42
    expected_response_status = 404

    response = await web_app_client.post(f'/v1/users/{user_id}/make-superuser')
    assert response.status == expected_response_status


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_make_superuser_204(web_app_client):
    user_id = 6
    expected_response_status = 204

    get_user_response_before = {
        'user': {
            'id': 6,
            'username': 'test_user_3',
            'is_active': True,
            'is_superadmin': False,
            'created_at': '2021-01-01',
            'provider': 'test_provider',
            'provider_id': '234',
        },
        'accesses': [
            {
                'project_slug': 'test_project_3',
                'capabilities': [
                    'project_capability_1',
                    'project_capability_2',
                ],
                'role': 'reader',
                'permissions': ['read'],
            },
        ],
    }

    get_user_response_after = {
        'user': {
            'id': 6,
            'username': 'test_user_3',
            'is_active': True,
            'is_superadmin': True,
            'created_at': '2021-01-01',
            'provider': 'test_provider',
            'provider_id': '234',
        },
        'accesses': [
            {
                'project_slug': 'test_project',
                'capabilities': [
                    'admin_capability',
                    'admin_capability_3',
                    'project_capability_1',
                    'project_capability_3',
                ],
                'role': 'super_admin',
                'permissions': [],
            },
            {
                'project_slug': 'test_project_2',
                'capabilities': [
                    'admin_capability',
                    'admin_capability_3',
                    'project_capability_3',
                ],
                'role': 'super_admin',
                'permissions': [],
            },
            {
                'project_slug': 'test_project_3',
                'capabilities': [
                    'admin_capability',
                    'admin_capability_3',
                    'project_capability_1',
                    'project_capability_2',
                ],
                'role': 'reader',
                'permissions': ['read'],
            },
        ],
    }

    response = await web_app_client.get(f'/v1/users/{user_id}')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_user_response_before

    response = await web_app_client.post(f'/v1/users/{user_id}/make-superuser')
    assert response.status == expected_response_status

    response = await web_app_client.get(f'/v1/users/{user_id}')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_user_response_after
