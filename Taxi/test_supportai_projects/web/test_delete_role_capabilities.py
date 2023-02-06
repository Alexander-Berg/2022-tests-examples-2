import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_delete_role_capabilities(web_app_client):
    test_samples = [
        {
            'role': 'wrong_role',
            'capability': 'test_capability',
            'response_status': 404,
        },
        {
            'role': 'super_admin',
            'capability': 'wrong_capability',
            'response_status': 400,
        },
        {
            'role': 'super_admin',
            'capability': 'admin_capability',
            'response_status': 204,
            'deleted_capability': {
                'slug': 'admin_capability',
                'type': 'allowed',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/capabilities/role/{sample["role"]}',
            params={'capability': sample['capability']},
        )
        assert response.status == sample['response_status']
        if response.status == 204:
            response = await web_app_client.get(
                f'/v1/capabilities/role/{sample["role"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['deleted_capability']
                not in response_json['capabilities']
            )
