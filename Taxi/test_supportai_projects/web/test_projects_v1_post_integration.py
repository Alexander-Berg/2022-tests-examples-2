import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'project_slug': 'wrong_project',
            'request_body': {
                'integration_id': 1,
                'base_url': 'https://baseurl.com',
            },
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'request_body': {
                'integration_id': 100500,
                'base_url': 'https://baseurl.com',
            },
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'request_body': {
                'integration_id': 1,
                'base_url': 'https://baseurl.com',
            },
            'response_status': 400,
        },
        {
            'project_slug': 'test_project_3',
            'request_body': {
                'integration_id': 2,
                'base_url': 'https://baseurl.com',
            },
            'response_status': 400,
        },
        {
            'project_slug': 'test_project_3',
            'request_body': {
                'integration_id': 1,
                'base_url': 'https://baseurl.com',
            },
            'response_status': 200,
        },
        {
            'project_slug': 'test_project_3',
            'request_body': {
                'integration_id': 2,
                'signature_token': 'token-poken',
            },
            'response_status': 200,
        },
        {
            'project_slug': 'test_project_3',
            'request_body': {
                'integration_id': 3,
                'base_url': 'https://baseurl.com',
            },
            'response_status': 200,
        },
        {
            'project_slug': 'test_project_3',
            'request_body': {
                'integration_id': 4,
                'base_url': 'https://baseurl.com',
                'api_key': 'keykkkey',
                'signature_token': 'token-poken',
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/projects/{test_sample["project_slug"]}/integrations',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    project_slug = 'test_project_3'

    test_samples = [
        {
            'request_body': {
                'integration_id': 1,
                'base_url': 'https://baseurl.com',
            },
            'response_body': {
                'integration_id': 1,
                'integration_slug': 'test_integration_1',
                'base_url': 'https://baseurl.com',
            },
        },
        {
            'request_body': {
                'integration_id': 2,
                'signature_token': 'token-poken',
            },
            'response_body': {
                'integration_id': 2,
                'integration_slug': 'test_integration_2',
            },
        },
        {
            'request_body': {
                'integration_id': 3,
                'base_url': 'https://baseurl.com',
                'api_key': 'keykkkey',
            },
            'response_body': {
                'integration_id': 3,
                'integration_slug': 'test_integration_3',
                'base_url': 'https://baseurl.com',
            },
        },
        {
            'request_body': {
                'integration_id': 4,
                'base_url': 'https://baseurl.com',
                'api_key': 'keykkkey',
                'signature_token': 'token-poken',
            },
            'response_body': {
                'integration_id': 4,
                'integration_slug': 'test_integration_4',
                'base_url': 'https://baseurl.com',
            },
        },
    ]

    list_integrations_before = {
        'integrations': [
            {
                'integration_id': 5,
                'integration_slug': 'test_integration_5',
                'base_url': 'https://urlurl.com',
            },
        ],
    }

    list_integrations_after = {
        'integrations': [
            {
                'integration_id': 5,
                'integration_slug': 'test_integration_5',
                'base_url': 'https://urlurl.com',
            },
            {
                'integration_id': 1,
                'integration_slug': 'test_integration_1',
                'base_url': 'https://baseurl.com',
            },
            {'integration_id': 2, 'integration_slug': 'test_integration_2'},
            {
                'integration_id': 3,
                'integration_slug': 'test_integration_3',
                'base_url': 'https://baseurl.com',
            },
            {
                'integration_id': 4,
                'integration_slug': 'test_integration_4',
                'base_url': 'https://baseurl.com',
            },
        ],
    }

    response = await web_app_client.get(
        f'/v1/projects/{project_slug}/integrations',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_integrations_before

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/projects/{project_slug}/integrations',
            json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

    response = await web_app_client.get(
        f'/v1/projects/{project_slug}/integrations',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_integrations_after
