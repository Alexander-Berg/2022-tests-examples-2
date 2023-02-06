import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_role_capabilities(web_app_client):
    test_samples = [
        {
            'user_id': 1,
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'test_capability', 'type': 'allowed'},
                    {'slug': 'test_capability_2', 'type': 'blocked'},
                    {'slug': 'test_capability_3', 'type': 'allowed'},
                ],
            },
        },
        {
            'user_id': 3,
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'test_capability', 'type': 'allowed'},
                    {'slug': 'test_capability_2', 'type': 'blocked'},
                    {'slug': 'test_capability_3', 'type': 'allowed'},
                ],
            },
        },
        {
            'user_id': 7,
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'test_capability_3', 'type': 'allowed'},
                    {'slug': 'test_capability_4', 'type': 'allowed'},
                    {'slug': 'test_capability_5', 'type': 'blocked'},
                ],
            },
        },
        {
            'user_id': 6,
            'response_status': 200,
            'response_body': {'capabilities': []},
        },
        {'user_id': 11, 'response_status': 404},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/capabilities/user/{test_sample["user_id"]}',
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']
