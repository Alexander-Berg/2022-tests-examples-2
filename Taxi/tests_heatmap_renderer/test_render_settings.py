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
@pytest.mark.config(
    HEATMAP_RENDERER_TILE_SETTINGS={
        '__default__': {
            'colors': [
                {'a': 0.7, 'b': 150, 'g': 40, 'r': 220},
                {'a': 0.7, 'b': 40, 'g': 150, 'r': 220},
                {'a': 0.7, 'b': 150, 'g': 220, 'r': 40},
            ],
            'compression_rate': 3,
            'max_zoom': 16,
            'min_zoom': 8,
        },
        'content_type': {
            '__default__': {
                'colors': [{'a': 0.7, 'b': 150, 'g': 40, 'r': 220}],
                'compression_rate': 3,
                'max_zoom': 16,
                'min_zoom': 8,
            },
            'abs_scale': {
                '__default__': {
                    'colors': [
                        {'a': 0.7, 'b': 150, 'g': 40, 'r': 220},
                        {'a': 0.7, 'b': 40, 'g': 150, 'r': 220},
                        {'a': 0.7, 'b': 150, 'g': 220, 'r': 40},
                    ],
                    'compression_rate': 3,
                    'max_zoom': 16,
                    'min_zoom': 8,
                    'palette_caps': {'min_value': 0, 'max_value': 10},
                },
            },
            'max_zoom': {
                '__default__': {
                    'colors': [{'a': 0.7, 'b': 150, 'g': 40, 'r': 220}],
                    'compression_rate': 3,
                    'max_zoom': 16,
                    'min_zoom': 8,
                },
                'max_zoom': {
                    'colors': [
                        {'a': 0.7, 'b': 150, 'g': 40, 'r': 220},
                        {'a': 0.7, 'b': 40, 'g': 150, 'r': 220},
                        {'a': 0.7, 'b': 150, 'g': 220, 'r': 40},
                    ],
                    'compression_rate': 3,
                    'max_zoom': 10,
                    'min_zoom': 8,
                },
            },
        },
    },
)
@pytest.mark.parametrize(
    'content_key,map_id,tile_filename',
    [
        ('default/default', 2, 'tile.png'),
        ('content_type/abs_scale/default', 3, 'abs_palette_tile.png'),
        ('content_type/max_zoom/max_zoom', 4, 'empty_tile.png'),
    ],
)
async def test_meta_and_tile(
        taxi_heatmap_renderer,
        heatmap_storage,
        get_file_path,
        taxi_config,
        content_key,
        map_id,
        tile_filename,
):
    taxi_config.set_values(
        {'HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS': [content_key]},
    )
    heatmap_storage.add_map(
        content_key,
        map_id,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    tile_response = await taxi_heatmap_renderer.get(
        f'tile?v={map_id}&x=2476&y=1284&z=12&content_required=true',
    )
    assert tile_response.status_code == 200
    response_image = PIL.Image.open(io.BytesIO(tile_response.content))
    expected_image = PIL.Image.open(get_file_path(tile_filename))
    assert (
        images_similarity(response_image, expected_image)
        >= SIMILARITY_THRESHOLD
    )
