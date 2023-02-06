import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_login(web_app_client):
    test_samples = [
        {
            'request_body': {'username': 'test_user_2', 'password': 'test_pw'},
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
            'request_body': {
                'username': 'test_user_2',
                'password': 'wrong_pw',
            },
            'response_status': 403,
        },
        {
            'request_body': {'username': 'test_user', 'password': 'test_pw'},
            'response_status': 404,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/auth/login', json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']
