import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_delete_users(web_app_client):
    test_samples = [
        {'user_id': 42, 'response_status': 404},
        {'user_id': 3, 'response_status': 204},
    ]

    expected_list_response = {
        'user_accesses': [
            {
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
            },
            {
                'user': {
                    'id': 2,
                    'username': 'test_user_2',
                    'is_active': True,
                    'is_superadmin': False,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
                    'provider_id': '123',
                },
                'accesses': [
                    {
                        'project_slug': 'test_project',
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
            {
                'user': {
                    'id': 4,
                    'username': 'admin_2',
                    'is_active': True,
                    'is_superadmin': True,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
                    'provider_id': '345',
                },
                'accesses': [
                    {
                        'project_slug': 'test_project',
                        'role': 'super_admin',
                        'permissions': [],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'role': 'super_admin',
                        'permissions': [],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
            {
                'user': {
                    'id': 5,
                    'username': 'admin_3',
                    'is_active': True,
                    'is_superadmin': True,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
                    'provider_id': '456',
                },
                'accesses': [
                    {
                        'project_slug': 'test_project',
                        'role': 'super_admin',
                        'permissions': [],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'role': 'super_admin',
                        'permissions': [],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'role': 'super_admin',
                        'permissions': [],
                    },
                ],
            },
            {
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
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
            {
                'user': {
                    'id': 7,
                    'username': 'test_user_4',
                    'is_active': True,
                    'is_superadmin': False,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
                    'provider_id': '567',
                },
                'accesses': [
                    {
                        'project_slug': 'test_project_3',
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
            {
                'user': {
                    'id': 8,
                    'username': 'test_user_5',
                    'is_active': True,
                    'is_superadmin': False,
                    'created_at': '2021-01-01',
                    'provider': 'test_provider',
                    'provider_id': '345',
                },
                'accesses': [
                    {
                        'project_slug': 'test_project_3',
                        'role': 'editor',
                        'permissions': ['read', 'write'],
                    },
                ],
            },
            {
                'user': {
                    'id': 9,
                    'username': 'test_user_6',
                    'is_active': True,
                    'is_superadmin': False,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
                    'provider_id': '678',
                },
                'accesses': [
                    {
                        'project_slug': 'test_project_2',
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'role': 'editor',
                        'permissions': ['read', 'write'],
                    },
                ],
            },
            {
                'user': {
                    'id': 10,
                    'username': 'test_user_7',
                    'is_active': True,
                    'is_superadmin': False,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
                    'provider_id': '789',
                },
                'accesses': [],
            },
        ],
    }

    for test_sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/users/{test_sample["user_id"]}',
        )
        assert response.status == test_sample['response_status']

    response = await web_app_client.get(f'/v1/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_list_response
