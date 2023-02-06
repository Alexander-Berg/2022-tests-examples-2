import pytest


@pytest.mark.pgsql('heatmap-storage', files=['maps.sql'])
async def test_get_meta(taxi_heatmap_storage, pgsql, load_binary):

    response = await taxi_heatmap_storage.get(
        'v1/get_actual_map_metadata?content_key=some_content',
    )

    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'heatmap_type': 'some_type',
        'created': '2019-01-02T00:00:00+0000',
        'expires': '2019-01-02T04:00:00+0000',
    }


@pytest.mark.pgsql('heatmap-storage', files=['maps.sql'])
async def test_wrong_content_key(taxi_heatmap_storage, pgsql, load_binary):

    response = await taxi_heatmap_storage.get(
        'v1/get_actual_map_metadata?content_key=wrong_key',
    )

    assert response.status_code == 404
