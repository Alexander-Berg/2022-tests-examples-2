import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_preset_capabilities(web_app_client):
    test_samples = [
        {
            'preset_slug': 'test_preset_1',
            'request_body': {'slug': 'test_capability_4', 'type': 'blocked'},
            'response_status': 200,
            'response_body': {'slug': 'test_capability_4', 'type': 'blocked'},
        },
        {
            'preset_slug': 'test_preset_1',
            'request_body': {'slug': 'test_capability_4', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'preset_slug': 'test_preset_1',
            'request_body': {
                'slug': 'test_capability_5',
                'type': 'wrong_type',
            },
            'response_status': 400,
        },
        {
            'preset_slug': 'test_preset_1',
            'request_body': {'slug': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'preset_slug': 'wrong_preset',
            'request_body': {
                'slug': 'project_capability_2',
                'type': 'allowed',
            },
            'response_status': 404,
        },
    ]

    for sample in test_samples:
        response = await web_app_client.post(
            f'/v1/capabilities/preset/{sample["preset_slug"]}',
            json=sample['request_body'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['response_body']
            response = await web_app_client.get(
                f'/v1/capabilities/preset/{sample["preset_slug"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert sample['response_body'] in response_json['capabilities']
