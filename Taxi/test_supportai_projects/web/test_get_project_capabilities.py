import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_project_capabilities(web_app_client):
    test_samples = [
        {
            'project_slug': 'test_project',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'project_capability_1', 'type': 'allowed'},
                    {'slug': 'project_capability_2', 'type': 'blocked'},
                    {'slug': 'project_capability_3', 'type': 'allowed'},
                ],
            },
        },
        {
            'project_slug': 'test_project_2',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'project_capability_1', 'type': 'blocked'},
                    {'slug': 'project_capability_2', 'type': 'blocked'},
                    {'slug': 'project_capability_3', 'type': 'allowed'},
                ],
            },
        },
        {
            'project_slug': 'test_project_3',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'project_capability_1', 'type': 'allowed'},
                    {'slug': 'project_capability_2', 'type': 'allowed'},
                    {'slug': 'project_capability_3', 'type': 'blocked'},
                ],
            },
        },
        {'project_slug': 'unexisting_project', 'response_status': 404},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/capabilities/project/{test_sample["project_slug"]}',
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']
