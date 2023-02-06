import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_preset_capabilities(web_app_client):
    test_samples = [
        {
            'preset_slug': 'test_preset_1',
            'response_body': {
                'capabilities': [
                    'test_capability',
                    'test_capability_3',
                    'test_capability_4',
                ],
            },
        },
        {
            'preset_slug': 'test_preset_2',
            'response_body': {
                'capabilities': [
                    'admin_capability_2',
                    'project_capability_1',
                    'test_capability_2',
                ],
            },
        },
        {
            'preset_slug': 'test_preset_3',
            'response_body': {
                'capabilities': [
                    'admin_capability',
                    'project_capability_2',
                    'test_capability',
                    'test_capability_5',
                ],
            },
        },
        {
            'preset_slug': 'test_preset_4',
            'response_body': {'capabilities': []},
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/presets/{test_sample["preset_slug"]}/capabilities',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_preset_capabilities_response_codes(web_app_client):
    test_samples = [
        {'slug': 'wrong_slug', 'response': 404},
        {'slug': 'test_preset_1', 'response': 200},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/presets/{test_sample["slug"]}/capabilities',
        )
        assert response.status == test_sample['response']
