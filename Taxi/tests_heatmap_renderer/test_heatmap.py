import copy

import pytest

from tests_heatmap_renderer import common


CONTENT_KEY = 'heatmap_content'

HEX_MAP = {
    'grids': [
        {
            'hex_grid': {
                'cell_size_meter': 250,
                'envelope': {
                    'br': [38.077641704627929, 56.003460457113277],
                    'tl': [37.135591841918192, 55.472370163516132],
                },
                'min_value': 0.0,
                'max_value': 100.0,
                'legend': '0 - 100',
                'legend_measurement_units': 'RUR',
                'legend_precision': 0,
            },
            'values': [
                {'x': 182, 'y': 131, 'value': 5.0},
                {'x': 181, 'y': 131, 'value': 3.0},
                {'x': 180, 'y': 131, 'value': 2.0},
                {'x': 179, 'y': 131, 'value': 1.0},
            ],
        },
    ],
}


def round_heatmap(geojson_heatmap):
    result = copy.deepcopy(geojson_heatmap)
    result['features'] = sorted(
        result['features'], key=lambda x: x['properties']['surge'],
    )
    for feature in result['features']:
        coordinates = feature['geometry']['coordinates']
        coordinates[0] = round(coordinates[0], 3)
        coordinates[1] = round(coordinates[1], 3)
        properties = feature['properties']
        properties['surge'] = round(properties['surge'], 3)
    return result


@pytest.mark.config(HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY])
@pytest.mark.parametrize(
    'normalize_mode,map_id',
    [('no_norm', 7), ('relative', 8), ('absolute', 9)],
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
async def test_heatmap(
        taxi_heatmap_renderer,
        heatmap_storage,
        load_json,
        taxi_config,
        normalize_mode,
        map_id,
):
    if normalize_mode != 'no_norm':
        taxi_config.set_values(
            dict(HEATMAP_RENDERER_NORMALIZE_HEATMAP_VALUES=True),
        )
        if normalize_mode == 'absolute':
            taxi_config.set_values(
                dict(
                    HEATMAP_RENDERER_TILE_SETTINGS={
                        '__default__': {
                            'compression_rate': 3,
                            'max_zoom': 16,
                            'min_zoom': 8,
                            'colors': [
                                {'r': 150, 'g': 150, 'b': 150, 'a': 0.7},
                            ],
                            # set palette_caps with big max_value
                            'palette_caps': {'min_value': 0, 'max_value': 10},
                        },
                    },
                ),
            )

    heatmap_storage.add_map(
        CONTENT_KEY,
        map_id,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
        serialized_map=common.build_hex_grid_fb(HEX_MAP),
    )
    await taxi_heatmap_renderer.invalidate_caches()
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    heatmap_response = await taxi_heatmap_renderer.get(
        f'heatmap?v={map_id}&lat=55.751244&lon=37.618423',
    )

    assert heatmap_response.status_code == 200
    heatmap = round_heatmap(heatmap_response.json())
    assert heatmap == load_json(f'heatmap_{normalize_mode}.json')
