import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_role_capabilities(web_app_client):
    test_samples = [
        {
            'role': 'wrong_role',
            'params': {'capability': 'test_capability', 'type': 'allowed'},
            'response_status': 404,
        },
        {
            'role': 'super_admin',
            'params': {'capability': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'role': 'super_admin',
            'params': {'capability': '', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'role': 'super_admin',
            'params': {
                'capability': 'admin_capability_2',
                'type': 'wrong_type',
            },
            'response_status': 400,
        },
        {
            'role': 'super_admin',
            'params': {'capability': 'admin_capability_2', 'type': 'allowed'},
            'response_status': 200,
            'updated_capability': {
                'slug': 'admin_capability_2',
                'type': 'allowed',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.put(
            f'/v1/capabilities/role/{sample["role"]}', params=sample['params'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['updated_capability']

            response = await web_app_client.get(
                f'/v1/capabilities/role/{sample["role"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['updated_capability'] in response_json['capabilities']
            )
