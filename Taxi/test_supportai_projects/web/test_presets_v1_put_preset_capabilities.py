import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_preset_capabilities_response_codes(web_app_client):
    test_samples = [
        {
            'preset_slug': 'wrong_preset',
            'request_body': {'capabilities': []},
            'response': 404,
        },
        {
            'preset_slug': 'test_preset_1',
            'request_body': {'capabilities': ['wrong_capability']},
            'response': 400,
        },
        {
            'preset_slug': 'test_preset_1',
            'request_body': {'capabilities': []},
            'response': 200,
        },
        {
            'preset_slug': 'test_preset_1',
            'request_body': {'capabilities': ['test_capability']},
            'response': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/presets/{test_sample["preset_slug"]}/capabilities',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_preset_capabilities_data(web_app_client):
    test_samples = [
        {
            'preset_slug': 'test_preset_1',
            'get_response_before': {
                'capabilities': [
                    'test_capability',
                    'test_capability_3',
                    'test_capability_4',
                ],
            },
            'request_body': {'capabilities': []},
            'response_body': {'capabilities': []},
            'get_response_after': {'capabilities': []},
        },
        {
            'preset_slug': 'test_preset_2',
            'get_response_before': {
                'capabilities': [
                    'admin_capability_2',
                    'project_capability_1',
                    'test_capability_2',
                ],
            },
            'request_body': {
                'capabilities': [
                    'test_capability_4',
                    'project_capability_2',
                    'admin_capability',
                    'test_capability_5',
                ],
            },
            'response_body': {
                'capabilities': [
                    'admin_capability',
                    'project_capability_2',
                    'test_capability_4',
                    'test_capability_5',
                ],
            },
            'get_response_after': {
                'capabilities': [
                    'admin_capability',
                    'project_capability_2',
                    'test_capability_4',
                    'test_capability_5',
                ],
            },
        },
        {
            'preset_slug': 'test_preset_3',
            'get_response_before': {
                'capabilities': [
                    'admin_capability',
                    'project_capability_2',
                    'test_capability',
                    'test_capability_5',
                ],
            },
            'request_body': {
                'capabilities': [
                    'admin_capability_2',
                    'admin_capability_2',
                    'project_capability_3',
                    'project_capability_3',
                    'project_capability_3',
                    'test_capability_5',
                ],
            },
            'response_body': {
                'capabilities': [
                    'admin_capability_2',
                    'project_capability_3',
                    'test_capability_5',
                ],
            },
            'get_response_after': {
                'capabilities': [
                    'admin_capability_2',
                    'project_capability_3',
                    'test_capability_5',
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/presets/{test_sample["preset_slug"]}/capabilities',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['get_response_before']

        response = await web_app_client.put(
            f'/v1/presets/{test_sample["preset_slug"]}/capabilities',
            json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

        response = await web_app_client.get(
            f'/v1/presets/{test_sample["preset_slug"]}/capabilities',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['get_response_after']
