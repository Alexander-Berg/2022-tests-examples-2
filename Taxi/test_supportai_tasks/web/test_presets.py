import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_capabilities_presets(web_app_client):
    response = await web_app_client.get(
        f'/v1/presets/capabilities', params={'user_id': '007'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'presets': [
            {
                'capabilities': [
                    {'slug': 'topics', 'type': 'allowed'},
                    {'slug': 'features', 'type': 'allowed'},
                ],
                'id': 1,
                'slug': 'test_preset',
                'title': 'Test Preset',
            },
            {
                'capabilities': [
                    {'slug': 'features', 'type': 'blocked'},
                    {'slug': 'user_based', 'type': 'allowed'},
                    {'slug': 'demo', 'type': 'blocked'},
                ],
                'id': 2,
                'slug': 'awesome_preset',
                'title': 'Awesome Preset',
            },
            {
                'capabilities': [
                    {'slug': 'topics', 'type': 'allowed'},
                    {'slug': 'user_based', 'type': 'allowed'},
                    {'slug': 'demo', 'type': 'blocked'},
                ],
                'id': 3,
                'slug': 'pretty_awesome_preset',
                'title': 'Pretty Awesome Preset',
            },
        ],
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_post_capabilities_presets(web_app_client):
    preset_params = {
        'slug': 'brand_new_preset',
        'title': 'Brand New Preset',
        'capabilities': [
            {'slug': 'topics', 'type': 'allowed'},
            {'slug': 'features', 'type': 'blocked'},
            {'slug': 'demo', 'type': 'allowed'},
        ],
    }

    response = await web_app_client.post(
        f'/v1/presets/capabilities',
        params={'user_id': '007'},
        json=preset_params,
    )
    assert response.status == 200
    response_json = await response.json()
    assert 'id' in response_json

    for param, value in preset_params.items():
        assert response_json[param] == value

    for capability in preset_params['capabilities']:
        assert capability in response_json['capabilities']

    response = await web_app_client.get(
        f'/v1/presets/capabilities', params={'user_id': '007'},
    )
    response_json = await response.json()
    assert len(response_json['presets']) == 4

    new_preset = [
        preset for preset in response_json['presets'] if preset['id'] == 4
    ][0]
    for param, value in preset_params.items():
        assert new_preset[param] == value

    for capability in preset_params['capabilities']:
        assert capability in new_preset['capabilities']
