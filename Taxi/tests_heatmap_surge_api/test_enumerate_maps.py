import pytest


async def test_version(taxi_heatmap_surge_api, load_binary):
    response = await taxi_heatmap_surge_api.get('enumerate_maps')
    assert response.status_code == 200
    assert response.json() == {
        'default_key': 'taxi_surge/__default__/default',
        'content_keys': {
            'taxi_surge/__default__/default': {'description': 'Driver'},
            'taxi_surge_lightweight/__default__/default': {
                'description': 'Rider',
            },
            'taxi_surge_lightweight/__default__/default_baseline': {
                'description': 'Rider - baseline',
            },
            'taxi_surge_lightweight/econom/default': {
                'description': 'Rider - econom',
            },
        },
    }
    assert response.headers['Access-Control-Allow-Origin'] == '*'


@pytest.mark.config(HEATMAP_RENDERER_FETCH_MAPS_FROM_S3=True)
async def test_s3_enumerate(taxi_heatmap_surge_api):
    response = await taxi_heatmap_surge_api.get('enumerate_maps')
    assert response.status_code == 200

    assert response.json() == {
        'default_key': 'taxi_surge/__default__/default',
        'content_keys': {
            'taxi_surge/__default__/default': {'description': 'Driver'},
            'taxi_surge_lightweight/__default__/default': {
                'description': 'Rider',
            },
            'taxi_surge_lightweight/__default__/default_baseline': {
                'description': 'Rider - baseline',
            },
            'taxi_surge_lightweight/econom/default': {
                'description': 'Rider - econom',
            },
        },
    }
    assert response.headers['Access-Control-Allow-Origin'] == '*'
