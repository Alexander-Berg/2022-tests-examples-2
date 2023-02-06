import datetime
import io

import PIL.Image
import pytest

from tests_heatmap_renderer import common

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
@pytest.mark.parametrize(
    'opaque_version_mode', ['allow_plain', 'require_encoded'],
)
async def test_opaque_version_v2_meta(
        taxi_heatmap_renderer,
        heatmap_storage,
        taxi_config,
        opaque_version_mode,
):
    taxi_config.set(
        HEATMAP_RENDERER_VERSION_ENCODER_SETTINGS=opaque_version_mode,
    )

    await taxi_heatmap_renderer.invalidate_caches()

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
    opaque_version = meta_response.json()['version_id']
    assert opaque_version != '2'

    opaque_version_tile_response = await taxi_heatmap_renderer.get(
        f'tile?v={opaque_version}&x=2476&y=1284&z=12',
    )
    assert opaque_version_tile_response.status_code == 200
    plain_version_tile_response = await taxi_heatmap_renderer.get(
        'tile?v=2&x=2476&y=1284&z=12',
    )
    if opaque_version_mode == 'require_encoded':
        # plain version is forbidden
        assert plain_version_tile_response.status_code == 400
        return

    assert plain_version_tile_response.status_code == 200

    image_opaque = PIL.Image.open(
        io.BytesIO(opaque_version_tile_response.content),
    )
    image_plain = PIL.Image.open(
        io.BytesIO(plain_version_tile_response.content),
    )
    assert images_similarity(image_opaque, image_plain) >= SIMILARITY_THRESHOLD


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(
    HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY],
    HEATMAP_RENDERER_VERSION_ENCODER_SETTINGS='allow_plain',
)
async def test_opaque_version_v2_version(
        taxi_heatmap_renderer, heatmap_storage,
):
    heatmap_storage.add_map(
        CONTENT_KEY,
        2,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    version_response = await taxi_heatmap_renderer.get(
        '/v2/version?content={}'.format(CONTENT_KEY),
    )

    assert version_response.status_code == 200
    assert version_response.json()['version_id'] != '2'


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY])
@pytest.mark.parametrize(
    'opaque_version_mode', ['disable', 'allow_plain', 'require_encoded'],
)
async def test_expired_map(
        taxi_heatmap_renderer,
        heatmap_storage,
        taxi_config,
        mocked_time,
        opaque_version_mode,
):
    taxi_config.set(
        HEATMAP_RENDERER_VERSION_ENCODER_SETTINGS=opaque_version_mode,
    )

    await taxi_heatmap_renderer.invalidate_caches()

    heatmap_storage.add_map(
        CONTENT_KEY,
        3,
        '2019-01-01T03:00:00+0000',
        '2019-01-01T04:00:00+0000',
        'hex_grid',
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    meta_response = await taxi_heatmap_renderer.get(
        '/v2/meta?content={}&hash=ucfv12uxf'.format(CONTENT_KEY),
    )

    assert meta_response.status_code == 200
    version = meta_response.json()['version_id']

    mocked_time.set(
        datetime.datetime.fromisoformat('2019-01-01T05:00:00+00:00'),
    )
    tile_response = await taxi_heatmap_renderer.get(
        f'tile?v={version}&x=2476&y=1284&z=12',
    )
    if opaque_version_mode == 'disable':
        assert tile_response.status_code == 200
    else:
        assert tile_response.status_code == 410


@pytest.mark.config(
    HEATMAP_RENDERER_VERSION_ENCODER_SETTINGS='require_encoded',
)
async def test_bad_version(taxi_heatmap_renderer):
    bad_version = 'bad_version_id'
    tile_response = await taxi_heatmap_renderer.get(
        f'tile?v={bad_version}&x=2476&y=1284&z=12',
    )
    assert tile_response.status_code == 400
    response = await taxi_heatmap_renderer.get(
        f'heatmap?v={bad_version}&lon=37.6172&lat=55.7179',
    )
    assert response.status_code == 400


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(
    HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY],
    HEATMAP_RENDERER_FETCH_MAPS_FROM_S3=True,
)
async def test_bad_config_combination(
        taxi_heatmap_renderer, s3_heatmap_storage, taxi_config,
):
    taxi_config.set(HEATMAP_RENDERER_VERSION_ENCODER_SETTINGS='disable')

    await taxi_heatmap_renderer.invalidate_caches()

    s3_heatmap_storage.add_map(
        CONTENT_KEY,
        '2',
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
        common.build_hex_grid_fb(common.DEFAULT_HEX_MAP),
    )

    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    meta_response = await taxi_heatmap_renderer.get(
        '/v2/meta?content={}&hash=ucfv12uxf'.format(CONTENT_KEY),
    )

    assert meta_response.status_code == 200

    correct_meta = {
        'legend_min': 0,
        'legend_max': 5,
        'legend': '0 - 5',
        'legend_precision': 0,
        'updated_epoch': 1546398000,
    }

    for meta_key in correct_meta:
        assert meta_response.json()[meta_key] == correct_meta[meta_key]

    version = meta_response.json()['version_id']

    taxi_config.set(HEATMAP_RENDERER_VERSION_ENCODER_SETTINGS='allow_plain')

    await taxi_heatmap_renderer.invalidate_caches()

    tile_response = await taxi_heatmap_renderer.get(
        f'tile?v={version}&x=2476&y=1284&z=12',
    )

    assert tile_response.status_code == 400
