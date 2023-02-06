import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_users_v2_get_users(web_app_client):
    expected_response = {
        'users': [
            {
                'id': 1,
                'username': 'test_user',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'test_provider',
                'provider_id': '123',
            },
            {
                'id': 2,
                'username': 'test_user_2',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '123',
            },
            {
                'id': 3,
                'username': 'admin',
                'is_active': True,
                'is_superadmin': True,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '234',
            },
            {
                'id': 4,
                'username': 'admin_2',
                'is_active': True,
                'is_superadmin': True,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '345',
            },
            {
                'id': 5,
                'username': 'admin_3',
                'is_active': True,
                'is_superadmin': True,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '456',
            },
            {
                'id': 6,
                'username': 'test_user_3',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'test_provider',
                'provider_id': '234',
            },
            {
                'id': 7,
                'username': 'test_user_4',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '567',
            },
            {
                'id': 8,
                'username': 'test_user_5',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'test_provider',
                'provider_id': '345',
            },
            {
                'id': 9,
                'username': 'test_user_6',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '678',
            },
            {
                'id': 10,
                'username': 'test_user_7',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '789',
            },
        ],
    }

    response = await web_app_client.get('/v2/users')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_users_v2_get_users_is_superadmin_filter(web_app_client):
    expected_response = {
        'users': [
            {
                'id': 3,
                'username': 'admin',
                'is_active': True,
                'is_superadmin': True,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '234',
            },
            {
                'id': 4,
                'username': 'admin_2',
                'is_active': True,
                'is_superadmin': True,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '345',
            },
            {
                'id': 5,
                'username': 'admin_3',
                'is_active': True,
                'is_superadmin': True,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '456',
            },
        ],
    }

    response = await web_app_client.get('/v2/users?is_superadmin=true')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
