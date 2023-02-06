import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_presets(web_app_client):
    expected_response = {
        'presets': [
            {'id': 1, 'slug': 'test_preset_1', 'title': 'Test Preset 1'},
            {'id': 2, 'slug': 'test_preset_2', 'title': 'Test Preset 2'},
            {'id': 3, 'slug': 'test_preset_3', 'title': 'Test Preset 3'},
            {'id': 4, 'slug': 'test_preset_4', 'title': 'Test Preset 4'},
        ],
    }

    response = await web_app_client.get('/v1/presets')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
