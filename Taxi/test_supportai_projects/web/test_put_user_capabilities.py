import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_user_capabilities(web_app_client):
    test_samples = [
        {
            'user_id': 11,
            'params': {'capability': 'test_capability', 'type': 'allowed'},
            'response_status': 404,
        },
        {
            'user_id': 1,
            'params': {'capability': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'user_id': 1,
            'params': {'capability': '', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'user_id': 1,
            'params': {
                'capability': 'test_capability_2',
                'type': 'wrong_type',
            },
            'response_status': 400,
        },
        {
            'user_id': 1,
            'params': {'capability': 'test_capability_2', 'type': 'allowed'},
            'response_status': 200,
            'updated_capability': {
                'slug': 'test_capability_2',
                'type': 'allowed',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.put(
            f'/v1/capabilities/user/{sample["user_id"]}',
            params=sample['params'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['updated_capability']

            response = await web_app_client.get(
                f'/v1/capabilities/user/{sample["user_id"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['updated_capability'] in response_json['capabilities']
            )
