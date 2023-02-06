import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_user_v2_get_user_by_id_responses(web_app_client):
    test_samples = [
        {'user_id': 1, 'response_status': 200},
        {'user_id': 42, 'response_status': 404},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v2/users/{test_sample["user_id"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_user_v2_get_user_by_id_data(web_app_client):
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
                'accesses': [
                    {
                        'project_slug': 'test_project',
                        'capabilities': [
                            'test_capability',
                            'test_capability_4',
                        ],
                        'group': 'guest',
                        'permissions': ['read'],
                    },
                ],
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
                            'test_capability',
                            'test_capability_4',
                        ],
                        'group': 'guest',
                        'permissions': ['read'],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'capabilities': [],
                        'group': 'guest',
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
                            'test_capability',
                            'test_capability_3',
                            'test_capability_4',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'capabilities': [
                            'test_capability_2',
                            'admin_capability_2',
                            'project_capability_1',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'capabilities': [
                            'test_capability',
                            'test_capability_5',
                            'admin_capability',
                            'project_capability_2',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
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
                            'test_capability',
                            'test_capability_3',
                            'test_capability_4',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'capabilities': [
                            'test_capability_2',
                            'admin_capability_2',
                            'project_capability_1',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'capabilities': [
                            'test_capability',
                            'test_capability_5',
                            'admin_capability',
                            'project_capability_2',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                ],
            },
        },
        {
            'user_id': 5,
            'response_body': {
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
                        'capabilities': [
                            'test_capability',
                            'test_capability_3',
                            'test_capability_4',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                    {
                        'project_slug': 'test_project_2',
                        'capabilities': [
                            'test_capability_2',
                            'admin_capability_2',
                            'project_capability_1',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
                    },
                    {
                        'project_slug': 'test_project_3',
                        'capabilities': [
                            'test_capability',
                            'test_capability_5',
                            'admin_capability',
                            'project_capability_2',
                        ],
                        'group': 'superadmin',
                        'permissions': ['read', 'write', 'modify'],
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
                        'project_slug': 'test_project',
                        'capabilities': [
                            'test_capability_3',
                            'test_capability_4',
                        ],
                        'group': 'standard',
                        'permissions': ['read', 'write'],
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
                        'project_slug': 'test_project',
                        'capabilities': [
                            'test_capability',
                            'test_capability_3',
                            'test_capability_4',
                        ],
                        'group': 'admin',
                        'permissions': ['read', 'write', 'modify'],
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
                        'project_slug': 'test_project_2',
                        'capabilities': [
                            'test_capability_2',
                            'admin_capability_2',
                            'project_capability_1',
                        ],
                        'group': 'admin',
                        'permissions': ['read', 'write', 'modify'],
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
                'accesses': [],
            },
        },
        {
            'user_id': 10,
            'response_body': {
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
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v2/users/{test_sample["user_id"]}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
