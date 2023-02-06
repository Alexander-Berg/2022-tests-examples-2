import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_delete_preset_capabilities(web_app_client):
    test_samples = [
        {
            'preset': 'wrong_preset',
            'capability': 'test_capability',
            'response_status': 404,
        },
        {
            'preset': 'test_preset_1',
            'capability': 'wrong_capability',
            'response_status': 400,
        },
        {
            'preset': 'test_preset_1',
            'capability': 'test_capability',
            'response_status': 204,
            'deleted_capability': {
                'slug': 'test_capability',
                'type': 'allowed',
            },
        },
    ]

    for sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/capabilities/preset/{sample["preset"]}',
            params={'capability': sample['capability']},
        )
        assert response.status == sample['response_status']
        if response.status == 204:
            response = await web_app_client.get(
                f'/v1/capabilities/preset/{sample["preset"]}',
            )
            assert response.status == 200
            response_json = await response.json()
            assert (
                sample['deleted_capability']
                not in response_json['capabilities']
            )
