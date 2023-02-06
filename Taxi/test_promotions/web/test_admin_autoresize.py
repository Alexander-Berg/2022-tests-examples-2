import dataclasses
import typing

import pytest

from taxi.clients import mds_s3

from promotions.generated.service.swagger.models import api


AUTORESIZE_URL = 'admin/promotions/autoresize/'
BYTES_IMAGE_PREFIX = b'Img'
CONFIG_PREFIX_ERROR = (
    'Error in ADMIN_IMAGE_RESIZE_MODES '
    'for type: "image", resize_mode: "height_fit". '
)
ORIGINAL_CONFIG_SIZE = {'field': 'original', 'value': 0}
ORIGINAL_SIZE = {
    'field': 'original',
    'value': 0,
    'mds_id': 'original_mds_id',
    'url': 'original_url',
}

IMAGE_COMPRESSION_JPEG_QUALITY = 85


def promotions_image_compression(
        enabled=True, minimal_compression_savings=0.1,
):
    if not enabled:
        return {'jpeg': {'enabled': enabled}}
    return {
        'jpeg': {
            'enabled': enabled,
            'jpeg_quality': IMAGE_COMPRESSION_JPEG_QUALITY,
            'minimal_compression_savings': minimal_compression_savings,
        },
    }


async def get_config_error_msg(web_app_client):
    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id=media_tag_ok_image_height_fit',
    )
    assert response.status == 400
    error_data = await response.json()
    return error_data['message']


def patch_autoresizer(patch, should_compress=False):
    """
    Patching crucial parts of autoresizer
    Logic of autoresizer:
    1) Download original (image)
    2) Resize it to necessary size
    3) if have compression try to compress
    4) if comression savings are ok save compressed
       else return simply resized file
    5) Save file in MDS-S3 storage
    """

    @dataclasses.dataclass
    class ImagePropertiesUrl:
        width: int
        height: int
        quality: typing.Optional[int] = None

        @classmethod
        def parse(cls, url) -> 'ImagePropertiesUrl':
            url_parts = url.split()
            return ImagePropertiesUrl(*map(int, url_parts))

        def __str__(self):
            res = f'{self.width} {self.height}'
            if self.quality:
                res += f' {self.quality}'
            return res

    @patch(
        'promotions.logic.admin.autoresizers.image_autoresizer.'
        'ImageAutoResizer._get_media_resolution',
    )
    async def _get_media_resolution(size: api.Size) -> api.Resolution:
        if size.url != 'original_url':
            prop = ImagePropertiesUrl.parse(size.url)
            width, height = prop.width, prop.height
        else:
            width, height = (1080, 1920)
        return api.Resolution(width=width, height=height)

    @patch('generated.clients.resizer.ResizerClient.genurl')
    async def _genurl(
            height: int, url: str, width: int, *args, quality=None, **kwargs,
    ):
        class Response:
            def __init__(self):
                self.body = str(ImagePropertiesUrl(width, height, quality))

        return Response()

    def get_image_prefix(quality=None):
        quality = quality or 100
        return b'Img' + b'$' * quality + b' '

    @patch(
        'promotions.logic.admin.autoresizers.base_autoresizer.AutoResizer'
        '._download_file',
    )
    async def _download_file(url) -> bytes:
        prop = ImagePropertiesUrl.parse(url)
        return get_image_prefix(prop.quality) + bytes(url, encoding='utf-8')

    def check_compressed(url):
        prop = ImagePropertiesUrl.parse(url)
        expected_quality = IMAGE_COMPRESSION_JPEG_QUALITY
        if should_compress:
            assert prop.quality == expected_quality
        else:
            assert prop.quality is None

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(key, body: bytes, *args, **kwargs):
        url = str(body.split(b' ', 1)[-1], encoding='utf-8')
        check_compressed(url)
        return mds_s3.S3Object(Key=url, ETag=None)


def assert_same_sizes(sizes, expected_sizes):
    assert sorted([tuple(size.values()) for size in sizes]) == sorted(
        [tuple(size.values()) for size in expected_sizes],
    )


async def get_sizes_after_resize(web_app_client, media_tag_id):
    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id={media_tag_id}',
    )
    assert response.status == 200

    view_response = await web_app_client.get(
        f'/admin/promotions/?promotion_id=banner_with_{media_tag_id}',
    )
    assert view_response.status == 200
    promo = await view_response.json()
    return promo['pages'][0]['backgrounds'][0]['sizes']


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'wrong_type': {'width_fit': [ORIGINAL_CONFIG_SIZE]},
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_media_type_not_in_config(web_app_client, patch):
    msg = 'media_type: "image" not found in config ADMIN_IMAGE_RESIZE_MODES'
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {'wrong_resize_mode': [ORIGINAL_CONFIG_SIZE]},
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_resize_mode_not_in_config(web_app_client):
    msg = (
        'resize_mode: "height_fit" not found in config '
        'ADMIN_IMAGE_RESIZE_MODES'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {'height_fit': [{'field': 'abracadabra', 'value': 0}]},
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_config_wrong_origina_field(web_app_client):
    msg = (
        CONFIG_PREFIX_ERROR
        + 'Cannot use size with field != original and value = 0.'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {'height_fit': [{'field': 'original', 'value': 777}]},
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_config_wrong_origina_value(web_app_client):
    msg = (
        CONFIG_PREFIX_ERROR
        + 'Cannot use size with field = original and value != 0.'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {'height_fit': [ORIGINAL_CONFIG_SIZE, ORIGINAL_CONFIG_SIZE]},
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_config_many_originals(web_app_client):
    msg = (
        CONFIG_PREFIX_ERROR
        + 'Too many of sizes with value=0 and field=original. Must be only 1.'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(ADMIN_IMAGE_RESIZE_MODES={'image': {'height_fit': []}})
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_config_no_sizes(web_app_client):
    msg = (
        'config ADMIN_IMAGE_RESIZE_MODES has no sizes '
        'for media_type: "image" '
        'and resize_mode: "height_fit"'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {'height_fit': [{'field': 'screen_height', 'value': 720}]},
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_config_no_original(web_app_client):
    msg = (
        CONFIG_PREFIX_ERROR
        + 'There is no size with value=0 and field=original (original size).'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={'image': {'height_fit': [ORIGINAL_CONFIG_SIZE]}},
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_config_no_sizes_except_original(web_app_client):
    msg = (
        CONFIG_PREFIX_ERROR + 'For autoresize there have to be at least '
        'one size except for original.'
    )
    assert msg == await get_config_error_msg(web_app_client)


@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_media_tag_type(web_app_client):
    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id=media_tag_wrong_type',
    )
    assert response.status == 400
    error_data = await response.json()
    msg = 'Unsupported for autoresize type:"wrong_type"'
    assert error_data['message'] == msg


@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_wrong_media_tag_has_no_original(web_app_client):
    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id=media_tag_without_original',
    )
    assert response.status == 404
    error_data = await response.json()
    msg = (
        'media_tag with id:media_tag_without_original '
        'does not contain original size'
    )
    assert error_data['message'] == msg


@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_cannot_download_original(web_app_client, patch):
    @patch(
        'promotions.logic.admin.autoresizers.base_autoresizer.AutoResizer'
        '._download_file',
    )
    async def _download_file(url):
        raise Exception('Cannot download any file')

    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id=media_tag_ok_image_height_fit',
    )
    assert response.status == 500


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {
            'height_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_height', 'value': 720},
            ],
        },
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_resizer_failed(web_app_client, patch):
    patch_autoresizer(patch)

    @patch('generated.clients.resizer.ResizerClient.genurl')
    async def _genurl(height: int, url: str, width: int):
        raise Exception('Something went wrong way')

    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id=media_tag_ok_image_height_fit',
    )
    assert response.status == 500


@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {
            'height_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_height', 'value': 640},
                {'field': 'screen_height', 'value': 720},
                {'field': 'screen_height', 'value': 960},
            ],
        },
    },
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_cannot_upload_resized_media_to_s3(web_app_client, patch):
    patch_autoresizer(patch)

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        raise Exception('Something went wrong way')

    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id=media_tag_ok_image_height_fit',
    )
    assert response.status == 500


@pytest.mark.config(PROMOTIONS_IMAGES_URL_TEMPLATE='{}')
@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {
            'height_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_height', 'value': 720},
                {'field': 'screen_height', 'value': 960},
                {'field': 'screen_height', 'value': 1440},
            ],
            'width_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_width', 'value': 480},
                {'field': 'screen_width', 'value': 640},
                {'field': 'screen_width', 'value': 800},
            ],
            'scale_factor': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'scale', 'value': 1.5},
                {'field': 'scale', 'value': 2},
                {'field': 'scale', 'value': 3},
            ],
        },
    },
)
@pytest.mark.parametrize(
    ['media_tag_id', 'expected_sizes'],
    [
        (
            'media_tag_ok_image_height_fit',
            (
                ORIGINAL_SIZE,
                {
                    'field': 'screen_height',
                    'value': 720,
                    'mds_id': '405 720',
                    'url': '405 720',
                },
                {
                    'field': 'screen_height',
                    'value': 960,
                    'mds_id': '540 960',
                    'url': '540 960',
                },
                {
                    'field': 'screen_height',
                    'value': 1440,
                    'mds_id': '810 1440',
                    'url': '810 1440',
                },
            ),
        ),
        (
            'media_tag_ok_image_width_fit',
            (
                ORIGINAL_SIZE,
                {
                    'field': 'screen_width',
                    'value': 480,
                    'mds_id': '480 853',
                    'url': '480 853',
                },
                {
                    'field': 'screen_width',
                    'value': 640,
                    'mds_id': '640 1138',
                    'url': '640 1138',
                },
                {
                    'field': 'screen_width',
                    'value': 800,
                    'mds_id': '800 1422',
                    'url': '800 1422',
                },
            ),
        ),
        (
            'media_tag_ok_image_scale_factor',
            (
                ORIGINAL_SIZE,
                {
                    'field': 'scale',
                    'value': 1.5,
                    'mds_id': '540 960',
                    'url': '540 960',
                },
                {
                    'field': 'scale',
                    'value': 2,
                    'mds_id': '720 1280',
                    'url': '720 1280',
                },
                {
                    'field': 'scale',
                    'value': 3,
                    'mds_id': '1080 1920',
                    'url': '1080 1920',
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_autoresize_ok(
        web_app_client, patch, media_tag_id, expected_sizes,
):
    patch_autoresizer(patch)
    sizes = await get_sizes_after_resize(web_app_client, media_tag_id)
    assert_same_sizes(sizes, expected_sizes)


@pytest.mark.config(PROMOTIONS_IMAGES_URL_TEMPLATE='{}')
@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {
            'height_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_height', 'value': 1440},
            ],
        },
    },
    PROMOTIONS_IMAGE_COMPRESSION_V2=promotions_image_compression(),
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_autoresize_and_compress_jpeg(web_app_client, patch):
    patch_autoresizer(patch, should_compress=True)
    media_tag_id = 'media_tag_ok_image_height_fit'

    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id={media_tag_id}',
    )
    assert response.status == 200


@pytest.mark.config(PROMOTIONS_IMAGES_URL_TEMPLATE='{}')
@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {
            'height_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_height', 'value': 1440},
            ],
        },
    },
    PROMOTIONS_IMAGE_COMPRESSION_V2=promotions_image_compression(
        enabled=False,
    ),
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_compression_disbled(web_app_client, patch):
    patch_autoresizer(patch, should_compress=False)
    media_tag_id = 'media_tag_ok_image_height_fit'

    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id={media_tag_id}',
    )
    assert response.status == 200


@pytest.mark.config(PROMOTIONS_IMAGES_URL_TEMPLATE='{}')
@pytest.mark.config(
    ADMIN_IMAGE_RESIZE_MODES={
        'image': {
            'height_fit': [
                ORIGINAL_CONFIG_SIZE,
                {'field': 'screen_height', 'value': 1440},
            ],
        },
    },
    PROMOTIONS_IMAGE_COMPRESSION_V2=promotions_image_compression(
        minimal_compression_savings=1.0,
    ),
)
@pytest.mark.pgsql('promotions', files=['pg_autoresize.sql'])
async def test_too_low_compression_savings(web_app_client, patch):
    patch_autoresizer(patch, should_compress=False)
    media_tag_id = 'media_tag_ok_image_height_fit'

    response = await web_app_client.post(
        f'{AUTORESIZE_URL}?media_tag_id={media_tag_id}',
    )
    assert response.status == 200
