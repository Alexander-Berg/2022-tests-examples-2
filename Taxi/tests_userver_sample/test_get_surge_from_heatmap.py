import pytest


@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={'br': [32.15, 51.12], 'tl': [35.15, 58.12]},
    values=[{'x': 0, 'y': 1, 'surge': 11, 'weight': 1.0}],
)
async def test_get_surge_from_heatmap(
        taxi_userver_sample, mockserver, heatmap_storage_fixture,
):
    response = await taxi_userver_sample.get('/get-surge-from-heatmap')
    assert response.status_code == 200
    assert response.text == '11'
