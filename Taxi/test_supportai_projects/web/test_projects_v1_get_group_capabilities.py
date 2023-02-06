import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_group_capabilities_response_codes(web_app_client):
    test_samples = [
        {'project_slug': 'wrong_project', 'response_status': 404},
        {'project_slug': 'test_project', 'response_status': 200},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/group-capabilities',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_group_capabilities_data(web_app_client):
    test_samples = [
        {
            'project_slug': 'test_project',
            'response_body': {
                'guest': ['test_capability', 'test_capability_4'],
                'standard': ['test_capability_3', 'test_capability_4'],
                'admin': [
                    'test_capability',
                    'test_capability_3',
                    'test_capability_4',
                ],
            },
        },
        {
            'project_slug': 'test_project_2',
            'response_body': {
                'guest': [],
                'standard': ['project_capability_1', 'test_capability_2'],
                'admin': [
                    'admin_capability_2',
                    'project_capability_1',
                    'test_capability_2',
                ],
            },
        },
        {
            'project_slug': 'test_project_3',
            'response_body': {
                'guest': ['test_capability'],
                'standard': [],
                'admin': ['admin_capability', 'project_capability_2'],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/group-capabilities',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
