import io

import PIL.Image
import pytest


CONTENT_KEY = 'some_content'

# due to some 3rd-party implementation-specific details we can get different
# pixels on hexagons borders (impossible to identify it by eye).
# So we use threshold to identify if images are quite equal
SIMILARITY_THRESHOLD = 0.995


# check if pixels are equal
def pixels_eq(px1, px2):
    assert len(px1) == len(px2) == 4
    # if pixels are fully transparent (alpha == 0)
    # then we should ignore its rgb values
    if px1[3] == px2[3] == 0:
        return True
    return px1 == px2


# calculates fraction of equal pixels
def images_similarity(img1, img2):
    assert img1.size == img2.size == (256, 256)
    assert img1.format == img2.format == 'PNG'
    img1 = img1.convert('RGBA')
    img2 = img2.convert('RGBA')

    cnt = 0
    for x in range(img1.size[0]):
        for y in range(img1.size[1]):
            px1 = img1.getpixel((x, y))
            px2 = img2.getpixel((x, y))
            cnt += 1 if pixels_eq(px1, px2) else 0
    return cnt / float(img1.size[0] * img1.size[1])


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY])
async def test_meta_and_tile(
        taxi_heatmap_renderer, heatmap_storage, get_file_path,
):
    heatmap_storage.add_map(
        CONTENT_KEY,
        2,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    meta_response = await taxi_heatmap_renderer.get(
        '/v2/meta?content={}&hash=ucfv12uxf'.format(CONTENT_KEY),
    )

    assert meta_response.status_code == 200

    assert meta_response.json() == {
        'legend_min': 0,
        'legend_max': 5,
        'version_id': '2',
        'legend': '0 - 5',
        'legend_measurement_units': 'RUR',
        'legend_precision': 0,
        'updated_epoch': 1546398000,
    }
    assert meta_response.headers['Access-Control-Allow-Origin'] == '*'

    tile_response = await taxi_heatmap_renderer.get(
        'tile?v=2&x=2476&y=1284&z=12',
    )

    assert tile_response.status_code == 200
    assert tile_response.headers['Access-Control-Allow-Origin'] == '*'
    response_image = PIL.Image.open(io.BytesIO(tile_response.content))
    expected_image = PIL.Image.open(get_file_path('tile.png'))
    assert (
        images_similarity(response_image, expected_image)
        >= SIMILARITY_THRESHOLD
    )

    # empty tile test
    empty_tile_response = await taxi_heatmap_renderer.get(
        'tile?v=2&x=2476&y=1282&z=12&content_required=true',
    )

    assert empty_tile_response.status_code == 200
    assert empty_tile_response.headers['Access-Control-Allow-Origin'] == '*'
    response_image = PIL.Image.open(io.BytesIO(empty_tile_response.content))
    expected_image = PIL.Image.open(get_file_path('empty_tile.png'))
    assert (
        images_similarity(response_image, expected_image)
        >= SIMILARITY_THRESHOLD
    )

    # no tile test
    empty_tile_response = await taxi_heatmap_renderer.get(
        'tile?v=2&x=148&y=777&z=12',
    )
    assert empty_tile_response.status_code == 204
    assert empty_tile_response.headers['Access-Control-Allow-Origin'] == '*'
    assert empty_tile_response.headers.get('Content-Length', '0') == '0'


EMPTY_MEASUREMENT_UNITS_MAP = {
    'grids': [
        {
            'hex_grid': {
                'cell_size_meter': 250,
                'envelope': {
                    'br': [38.077641704627929, 56.003460457113277],
                    'tl': [37.135591841918192, 55.472370163516132],
                },
                'min_value': 0.0,
                'max_value': 5.0,
                'legend': '0 - 5',
                'legend_measurement_units': '',
                'legend_precision': 0,
            },
            'values': [
                {'x': 182, 'y': 131, 'value': 5.0},
                {'x': 181, 'y': 131, 'value': 3.0},
                {'x': 180, 'y': 131, 'value': 2.0},
                {'x': 179, 'y': 131, 'value': 1.0},
                {'x': 178, 'y': 131, 'value': 0.0},
            ],
        },
    ],
}


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY])
async def test_meta_empty_legend_measurement_units(
        taxi_heatmap_renderer, heatmap_storage,
):
    heatmap_storage.add_map(
        CONTENT_KEY,
        2,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
        EMPTY_MEASUREMENT_UNITS_MAP,
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    meta_response = await taxi_heatmap_renderer.get(
        '/v2/meta?content={}&hash=ucfv12uxf'.format(CONTENT_KEY),
    )

    assert meta_response.status_code == 200

    assert meta_response.json() == {
        'legend_min': 0,
        'legend_max': 5,
        'version_id': '2',
        'legend': '0 - 5',
        'legend_precision': 0,
        'updated_epoch': 1546398000,
    }
    assert meta_response.headers['Access-Control-Allow-Origin'] == '*'


async def test_meta_client_error(taxi_heatmap_renderer):
    meta_response = await taxi_heatmap_renderer.get(
        '/v2/meta?content={}'.format(CONTENT_KEY),
    )

    assert meta_response.status_code == 400
