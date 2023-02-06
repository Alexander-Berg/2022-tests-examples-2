import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_group_capabilities_response_statuses(web_app_client):
    test_samples = [
        {
            'project_slug': 'wrong_project',
            'request_body': {'guest': [], 'standard': [], 'admin': []},
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'request_body': {
                'guest': ['wrong_capability'],
                'standard': ['wrong_capability'],
                'admin': ['wrong_capability'],
            },
            'response_status': 200,
        },
        {
            'project_slug': 'test_project',
            'request_body': {'guest': [], 'standard': [], 'admin': []},
            'response_status': 200,
        },
        {
            'project_slug': 'test_project',
            'request_body': {
                'guest': [
                    'test_capability',
                    'test_capability',
                    'test_capability',
                    'admin_capability_2',
                    'admin_capability',
                    'test_capability_4',
                ],
                'standard': [
                    'test_capability',
                    'test_capability_3',
                    'test_capability_2',
                    'admin_capability_2',
                    'project_capability_1',
                    'project_capability_2',
                ],
                'admin': [
                    'test_capability_4',
                    'test_capability_3',
                    'test_capability_3',
                    'admin_capability',
                ],
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/projects/{test_sample["project_slug"]}/group-capabilities',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_group_capabilities_data(web_app_client):
    test_samples = [
        {
            'project_slug': 'test_project',
            'request_body': {
                'guest': [
                    'test_capability',
                    'test_capability',
                    'test_capability',
                    'admin_capability_2',
                    'admin_capability',
                    'test_capability_4',
                ],
                'standard': [
                    'test_capability',
                    'test_capability_3',
                    'test_capability_2',
                    'admin_capability_2',
                    'project_capability_1',
                    'project_capability_2',
                ],
                'admin': [
                    'test_capability_4',
                    'test_capability_3',
                    'test_capability_3',
                    'admin_capability',
                ],
            },
            'response_body': {
                'guest': ['test_capability', 'test_capability_4'],
                'standard': ['test_capability', 'test_capability_3'],
                'admin': ['test_capability_3', 'test_capability_4'],
            },
            'get_group_capabilities_response_before': {
                'guest': ['test_capability', 'test_capability_4'],
                'standard': ['test_capability_3', 'test_capability_4'],
                'admin': [
                    'test_capability',
                    'test_capability_3',
                    'test_capability_4',
                ],
            },
            'get_group_capabilities_response_after': {
                'guest': ['test_capability', 'test_capability_4'],
                'standard': ['test_capability', 'test_capability_3'],
                'admin': ['test_capability_3', 'test_capability_4'],
            },
        },
        {
            'project_slug': 'test_project_2',
            'request_body': {'guest': [], 'standard': [], 'admin': []},
            'response_body': {'guest': [], 'standard': [], 'admin': []},
            'get_group_capabilities_response_before': {
                'guest': [],
                'standard': ['project_capability_1', 'test_capability_2'],
                'admin': [
                    'admin_capability_2',
                    'project_capability_1',
                    'test_capability_2',
                ],
            },
            'get_group_capabilities_response_after': {
                'guest': [],
                'standard': [],
                'admin': [],
            },
        },
        {
            'project_slug': 'test_project_3',
            'request_body': {
                'guest': ['test_capability_3', 'test_capability_4'],
                'standard': ['admin_capability_2', 'project_capability_1'],
                'admin': [],
            },
            'response_body': {'guest': [], 'standard': [], 'admin': []},
            'get_group_capabilities_response_before': {
                'guest': ['test_capability'],
                'standard': [],
                'admin': ['admin_capability', 'project_capability_2'],
            },
            'get_group_capabilities_response_after': {
                'guest': [],
                'standard': [],
                'admin': [],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/group-capabilities',
        )
        assert response.status == 200
        response_json = await response.json()
        assert (
            response_json
            == test_sample['get_group_capabilities_response_before']
        )

        response = await web_app_client.put(
            f'/v1/projects/{test_sample["project_slug"]}/group-capabilities',
            json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

        response = await web_app_client.get(
            f'/v1/projects/{test_sample["project_slug"]}/group-capabilities',
        )
        assert response.status == 200
        response_json = await response.json()
        assert (
            response_json
            == test_sample['get_group_capabilities_response_after']
        )
