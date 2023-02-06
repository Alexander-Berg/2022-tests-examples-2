import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_put_preset_capabilities(web_app_client):
    test_samples = [
        {
            'preset_slug': 'wrong_preset',
            'params': {'capability': 'test_capability', 'type': 'allowed'},
            'response_status': 404,
        },
        {
            'preset_slug': 'test_preset_1',
            'params': {'capability': 'wrong_capability', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'preset_slug': 'test_preset_1',
            'params': {'capability': '', 'type': 'allowed'},
            'response_status': 400,
        },
        {
            'preset_slug': 'test_preset_1',
            'params': {'capability': 'test_capability', 'type': 'wrong_type'},
            'response_status': 400,
        },
        {
            'preset_slug': 'test_preset_1',
            'params': {'capability': 'test_capability', 'type': 'blocked'},
            'response_status': 200,
            'updated_capability': {
                'slug': 'test_capability',
                'type': 'blocked',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.put(
            f'/v1/capabilities/preset/{sample["preset_slug"]}',
            params=sample['params'],
        )
        assert response.status == sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == sample['updated_capability']

            response = await web_app_client.get(
                f'/v1/capabilities/preset/{sample["preset_slug"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['updated_capability'] in response_json['capabilities']
            )
