import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_delete_project_capabilities(web_app_client):
    test_samples = [
        {
            'project': 'wrong_project',
            'capability': 'test_capability',
            'response_status': 404,
        },
        {
            'project': 'test_project',
            'capability': 'wrong_capability',
            'response_status': 400,
        },
        {
            'project': 'test_project',
            'capability': 'project_capability_1',
            'response_status': 204,
            'deleted_capability': {
                'slug': 'project_capability_1',
                'type': 'allowed',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/capabilities/project/{sample["project"]}',
            params={'capability': sample['capability']},
        )
        assert response.status == sample['response_status']
        if response.status == 204:
            response = await web_app_client.get(
                f'/v1/capabilities/project/{sample["project"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['deleted_capability']
                not in response_json['capabilities']
            )
