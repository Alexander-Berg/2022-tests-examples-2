import pytest


POINT_WITH_TAG = {
    'position': {'lat': 37, 'lon': 55},
    'surge_data_by_category': {
        'econom': {
            'pins': 5,
            'pins_driver': 3,
            'pins_order': 4,
            'radius': 1000,
            'total': 6,
            'value_raw': 1.0,
            'value_smooth': 2.5,
        },
    },
}
POINT_WITHOUT_TAG = {
    'position': {'lat': 37.001, 'lon': 55.001},
    'surge_data_by_category': {
        'econom': {
            'pins': 6,
            'pins_driver': 3,
            'pins_order': 4,
            'radius': 1000,
            'total': 4,
            'value_raw': 2.0,
            'value_smooth': 2.5,
        },
    },
}

# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.config(SAMPLE_STORAGE_SELECTED_POINTS_TAGS=['some_tag'])
@pytest.mark.parametrize(
    'tags,expected_point',
    [
        ([], POINT_WITHOUT_TAG),
        (['some_tag'], POINT_WITH_TAG),
        (['unexpected_tag'], POINT_WITHOUT_TAG),
    ],
)
async def test_selected_points(
        taxi_heatmap_sample_storage, taxi_config, tags, expected_point,
):
    taxi_config.set_values({'SAMPLE_STORAGE_SELECTED_POINTS_TAGS': tags})
    response = await taxi_heatmap_sample_storage.get(
        'v1/selected_points?sparsity_radius_m=1000&point=55,37',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {'points': [expected_point]}
