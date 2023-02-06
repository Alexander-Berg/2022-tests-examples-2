import pytest


@pytest.mark.config(SURGE_DEFAULT_PIPELINE='test_pipeline_name')
@pytest.mark.parametrize(
    'layer_suffix', [pytest.param(''), pytest.param('_samples')],
)
@pytest.mark.parametrize(
    'point_a,categories,expected',
    [
        pytest.param(
            [32.151, 51.121],
            ['econom'],
            {'value': 11.0, 'is_default': False},
            id='correct point',
        ),
        pytest.param(
            [20.151, 51.121],
            ['econom'],
            {'value': 1.0, 'is_default': True},
            id='point without surge',
        ),
        pytest.param(
            [32.151, 51.121],
            ['vip'],
            {'value': 1.0, 'is_default': True},
            id='invalid category',
        ),
    ],
)
async def test_get_surge(
        taxi_surge_calculator,
        heatmap_storage,
        layer_suffix,
        point_a,
        categories,
        expected,
        taxi_config,
):
    taxi_config.set_values(
        {'ALL_CATEGORIES': categories, 'SURGE_MAP_LAYER_SUFFIX': layer_suffix},
    )

    heatmap_storage.set_layer_suffix(layer_suffix)
    heatmap_storage.build_and_set_surge_map(
        cell_size_meter=500.123,
        envelope={'br': [32.15, 51.12], 'tl': [35.15, 58.12]},
        values=[{'x': 0, 'y': 1, 'surge': 11, 'weight': 1.0}],
        grid_extra={'surge': 10},
    )
    await taxi_surge_calculator.invalidate_caches()

    request = {'point_a': point_a, 'classes': categories}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.json()
    data = response.json()
    actual = data['classes'][0]['calculation_meta']['smooth']['point_a']
    assert actual == expected

    expected_value_raw = 42 if actual['is_default'] else 10
    assert data['classes'][0]['value_raw'] == expected_value_raw
