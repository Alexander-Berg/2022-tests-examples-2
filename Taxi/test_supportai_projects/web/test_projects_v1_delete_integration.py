import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'project_slug': 'wrong_project',
            'integration_id': 1,
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'integration_id': 100500,
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'integration_id': 4,
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'integration_id': 1,
            'response_status': 204,
        },
    ]

    for test_sample in test_samples:
        respoonse = await web_app_client.delete(
            f'/v1/projects/{test_sample["project_slug"]}'
            f'/integrations/{test_sample["integration_id"]}',
        )
        assert respoonse.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    project_slug = 'test_project'
    integration_id = 1

    list_integrations_before = {
        'integrations': [
            {'integration_id': 1, 'integration_slug': 'test_integration_1'},
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
    }

    list_integrations_after = {
        'integrations': [
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
    }

    response = await web_app_client.get(
        f'/v1/projects/{project_slug}/integrations',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_integrations_before

    response = await web_app_client.delete(
        f'/v1/projects/{project_slug}/integrations/{integration_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/projects/{project_slug}/integrations',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_integrations_after
