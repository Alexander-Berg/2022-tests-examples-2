import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_preset_capabilities(web_app_client):
    test_samples = [
        {
            'preset_slug': 'test_preset_1',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'project_capability_2', 'type': 'blocked'},
                    {'slug': 'project_capability_3', 'type': 'allowed'},
                    {'slug': 'test_capability', 'type': 'allowed'},
                    {'slug': 'test_capability_3', 'type': 'allowed'},
                ],
            },
        },
        {
            'preset_slug': 'test_preset_2',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'project_capability_3', 'type': 'allowed'},
                    {'slug': 'test_capability_2', 'type': 'allowed'},
                    {'slug': 'test_capability_5', 'type': 'blocked'},
                ],
            },
        },
        {
            'preset_slug': 'test_preset_3',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'project_capability_1', 'type': 'allowed'},
                    {'slug': 'test_capability_3', 'type': 'allowed'},
                    {'slug': 'test_capability_4', 'type': 'blocked'},
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/capabilities/preset/{test_sample["preset_slug"]}',
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']
