import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_user_accesses_404(web_app_client):
    test_sample = {'user_id': 42, 'response_status': 404}

    response = await web_app_client.get(f'/v1/users/{test_sample["user_id"]}')
    assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_user_accesses_filter(web_app_client):
    test_samples = [
        {
            'user_id': 2,
            'project_slug': 'test_project',
            'response_body': {
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
                        'capabilities': [
                            'project_capability_1',
                            'project_capability_3',
                        ],
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
        },
        {
            'user_id': 2,
            'project_slug': 'test_project_2',
            'response_body': {
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
                        'project_slug': 'test_project_2',
                        'capabilities': ['project_capability_3'],
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/users/{test_sample["user_id"]}'
            f'?project_slug={test_sample["project_slug"]}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_user_accesses(web_app_client):
    test_samples = [
        {
            'user_id': 1,
            'response_body': {
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
        },
        {
            'user_id': 2,
            'response_body': {
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
                        'capabilities': [
                            'project_capability_1',
                            'project_capability_3',
                        ],
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'capabilities': ['project_capability_3'],
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
        },
        {
            'user_id': 3,
            'response_body': {
                'user': {
                    'id': 3,
                    'username': 'admin',
                    'is_active': True,
                    'is_superadmin': True,
                    'created_at': '2021-01-01',
                    'provider': 'supportai',
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
                            'test_capability',
                            'test_capability_3',
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
                            'test_capability',
                            'test_capability_3',
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
                            'test_capability',
                            'test_capability_3',
                        ],
                        'role': 'super_admin',
                        'permissions': [],
                    },
                ],
            },
        },
        {
            'user_id': 4,
            'response_body': {
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
            },
        },
        {
            'user_id': 6,
            'response_body': {
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
            },
        },
        {
            'user_id': 7,
            'response_body': {
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
                        'capabilities': [
                            'project_capability_1',
                            'project_capability_2',
                            'test_capability_3',
                            'test_capability_4',
                        ],
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                ],
            },
        },
        {
            'user_id': 8,
            'response_body': {
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
                        'capabilities': [
                            'project_capability_1',
                            'project_capability_2',
                            'test_capability_4',
                            'test_capability_5',
                        ],
                        'role': 'editor',
                        'permissions': ['read', 'write'],
                    },
                ],
            },
        },
        {
            'user_id': 9,
            'response_body': {
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
                        'capabilities': ['project_capability_3'],
                        'role': 'reader',
                        'permissions': ['read'],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'capabilities': [
                            'project_capability_1',
                            'project_capability_2',
                            'test_capability_4',
                            'test_capability_5',
                        ],
                        'role': 'editor',
                        'permissions': ['read', 'write'],
                    },
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/users/{test_sample["user_id"]}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
