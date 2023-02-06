import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_project_capabilities(web_app_client):
    test_samples = [
        {
            'project_slug': 'wrong_project',
            'params': {'capability': 'test_capability', 'type': 'allowed'},
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'params': {'capability': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'params': {'capability': '', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'params': {'capability': 'test_capability', 'type': 'wrong_type'},
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'params': {
                'capability': 'project_capability_1',
                'type': 'blocked',
            },
            'response_status': 200,
            'updated_capability': {
                'slug': 'project_capability_1',
                'type': 'blocked',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.put(
            f'/v1/capabilities/project/{sample["project_slug"]}',
            params=sample['params'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['updated_capability']

            response = await web_app_client.get(
                f'/v1/capabilities/project/{sample["project_slug"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['updated_capability'] in response_json['capabilities']
            )
