import pytest


@pytest.mark.pgsql('heatmap-storage', files=['maps.sql'])
async def test_enumerate(taxi_heatmap_storage, pgsql, load_binary):

    response = await taxi_heatmap_storage.get(
        'v1/enumerate_keys?content_type=taxi_surge',
    )

    assert response.status_code == 200
    assert response.json() == {
        'content_keys': ['taxi_surge/__default__', 'taxi_surge/uberX'],
    }


@pytest.mark.pgsql('heatmap-storage', files=['maps.sql'])
async def test_empty_response(taxi_heatmap_storage, pgsql, load_binary):

    response = await taxi_heatmap_storage.get(
        'v1/enumerate_keys?content_type=wrong_type',
    )

    assert response.status_code == 200
    assert response.json() == {'content_keys': []}
