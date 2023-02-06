import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_check_user(web_app_client):
    test_samples = [
        {
            'provider': 'test_provider',
            'provider_id': '123',
            'response_status': 200,
            'response_body': {
                'id': 1,
                'username': 'test_user',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'test_provider',
                'provider_id': '123',
            },
        },
        {
            'provider': 'supportai',
            'provider_id': '123',
            'response_status': 200,
            'response_body': {
                'id': 2,
                'username': 'test_user_2',
                'is_active': True,
                'is_superadmin': False,
                'created_at': '2021-01-01',
                'provider': 'supportai',
                'provider_id': '123',
            },
        },
        {
            'provider': 'fake_provider',
            'provider_id': '123',
            'response_status': 404,
        },
        {
            'provider': 'supportai',
            'provider_id': '12345',
            'response_status': 404,
        },
        {
            'provider': 'test_provider',
            'provider_id': '789',
            'response_status': 404,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/auth/user'
            f'?provider={test_sample["provider"]}'
            f'&provider_id={test_sample["provider_id"]}',
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']
