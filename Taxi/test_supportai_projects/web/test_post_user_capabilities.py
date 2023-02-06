import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_user_capabilities(web_app_client):
    test_samples = [
        {
            'user_id': 1,
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 200,
            'response_body': {'slug': 'test_capability_4', 'type': 'allowed'},
        },
        {
            'user_id': 1,
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'user_id': 1,
            'request_body': {
                'slug': 'test_capability_5',
                'type': 'wrong_type',
            },
            'response_status': 400,
        },
        {
            'user_id': 1,
            'request_body': {'slug': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'user_id': 11,
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 404,
        },
    ]

    for sample in test_samples:
        response = await web_app_client.post(
            f'/v1/capabilities/user/{sample["user_id"]}',
            json=sample['request_body'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['response_body']
            response = await web_app_client.get(
                f'/v1/capabilities/user/{sample["user_id"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert sample['response_body'] in response_json['capabilities']
