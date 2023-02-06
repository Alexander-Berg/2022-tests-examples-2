import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_users(web_app_client):
    expected_response = {
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

    response = await web_app_client.get('/v1/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_users_is_superadmin_filter(web_app_client):
    expected_response = {
        'user_accesses': [
            {
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
        ],
    }

    response = await web_app_client.get('/v1/users?is_superadmin=true')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_users_project_filter(web_app_client):
    test_samples = [
        {
            'project_slug': 'test_project',
            'expected_response': {
                'user_accesses': [
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
                        ],
                    },
                    {
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
                                'role': 'super_admin',
                                'permissions': [],
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
                        ],
                    },
                ],
            },
        },
        {
            'project_slug': 'test_project_2',
            'expected_response': {
                'user_accesses': [
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
                                'project_slug': 'test_project_2',
                                'role': 'reader',
                                'permissions': ['read'],
                            },
                        ],
                    },
                    {
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
                                'project_slug': 'test_project_2',
                                'role': 'super_admin',
                                'permissions': [],
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
                                'project_slug': 'test_project_2',
                                'role': 'super_admin',
                                'permissions': [],
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
                                'project_slug': 'test_project_2',
                                'role': 'super_admin',
                                'permissions': [],
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
                        ],
                    },
                ],
            },
        },
        {
            'project_slug': 'test_project_3',
            'expected_response': {
                'user_accesses': [
                    {
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
                                'project_slug': 'test_project_3',
                                'role': 'super_admin',
                                'permissions': [],
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
                                'project_slug': 'test_project_3',
                                'role': 'editor',
                                'permissions': ['read', 'write'],
                            },
                        ],
                    },
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/users?project_slug={test_sample["project_slug"]}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['expected_response']
