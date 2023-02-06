import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_role_capabilities(web_app_client):
    test_samples = [
        {
            'role_slug': 'super_admin',
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 200,
            'response_body': {'slug': 'test_capability_4', 'type': 'allowed'},
        },
        {
            'role_slug': 'super_admin',
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'role_slug': 'super_admin',
            'request_body': {
                'slug': 'test_capability_5',
                'type': 'wrong_type',
            },
            'response_status': 400,
        },
        {
            'role_slug': 'super_admin',
            'request_body': {'slug': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'role_slug': 'wrong_role',
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 404,
        },
    ]

    for sample in test_samples:
        response = await web_app_client.post(
            f'/v1/capabilities/role/{sample["role_slug"]}',
            json=sample['request_body'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['response_body']
            response = await web_app_client.get(
                f'/v1/capabilities/role/{sample["role_slug"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert sample['response_body'] in response_json['capabilities']
