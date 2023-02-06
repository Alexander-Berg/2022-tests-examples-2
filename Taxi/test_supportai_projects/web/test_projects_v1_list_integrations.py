import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {'project_slug': 'wrong_project', 'response_status': 404},
        {'project_slug': 'test_project', 'response_status': 200},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/integrations',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    test_samples = [
        {
            'project_slug': 'test_project',
            'response_body': {
                'integrations': [
                    {
                        'integration_id': 1,
                        'integration_slug': 'test_integration_1',
                    },
                    {
                        'integration_id': 2,
                        'integration_slug': 'test_integration_2',
                        'base_url': 'https://baseurl.com',
                    },
                    {
                        'integration_id': 3,
                        'integration_slug': 'test_integration_3',
                        'base_url': 'https://anotherawesomeurl.com',
                    },
                ],
            },
        },
        {
            'project_slug': 'test_project_2',
            'response_body': {
                'integrations': [
                    {
                        'integration_id': 4,
                        'integration_slug': 'test_integration_4',
                        'base_url': 'https://urlurlurl.com',
                    },
                ],
            },
        },
        {
            'project_slug': 'test_project_3',
            'response_body': {
                'integrations': [
                    {
                        'integration_id': 5,
                        'integration_slug': 'test_integration_5',
                        'base_url': 'https://urlurl.com',
                    },
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/integrations',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
