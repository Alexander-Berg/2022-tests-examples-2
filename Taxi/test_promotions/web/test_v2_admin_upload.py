import aiohttp
import pytest

from generated.clients import ocr_translate
from taxi.clients import mds_s3

V2_UPLOAD_URL = 'v2/admin/promotions/upload/'

_ADMIN_IMAGE_RESIZE_MODES = {
    'image': {
        'height_fit': [
            {'field': 'original', 'value': 0},
            {'field': 'screen_height', 'value': 1280},
            {'field': 'screen_height', 'value': 1920},
        ],
    },
}

PROMOTIONS_MEDIA_CONTENT_SIZE_LIMITS = {'file_size': 0.00001}


def create_form(
        file_data=b'123123123',
        field_value='screen_height',
        content_type='image/png',
        value='1280',
):
    form = aiohttp.FormData()
    form.add_field(
        name='content',
        value=file_data,
        filename='some_fielanme.png',
        content_type=content_type,
    )
    form.add_field(name='media_tag_id', value='1234-5678_media_tag_id')
    form.add_field(name='field', value=field_value)
    form.add_field(name='value', value=value)
    return form


def create_ocr_responce(text: str):
    return ocr_translate.Recognize200(
        ocr_translate.ocr_translate_module.Response(
            ocr_translate.ocr_translate_module.Data(
                aggregated_stat=0,
                imgsize=ocr_translate.ocr_translate_module.ImageSize(h=1, w=1),
                istext=1,
                lang='rus',
                rotate=0,
                time_limit=ocr_translate.ocr_translate_module.TimeLimit(
                    percent=0, stopped_by_timeout=False,
                ),
                fulltext=[
                    ocr_translate.ocr_translate_module.FullText(
                        confidence=0,
                        line_size_category=1,
                        text=text,
                        type='type',
                    ),
                ],
            ),
            '200',
        ),
    )


@pytest.mark.pgsql('promotions', files=['pg_v2_upload.sql'])
@pytest.mark.config(
    PROMOTIONS_IMAGES_URL_TEMPLATE='https://some-cool-url.ya/{}',
)
@pytest.mark.config(ADMIN_IMAGE_RESIZE_MODES=_ADMIN_IMAGE_RESIZE_MODES)
async def test_image_v2_upload(web_app_client, patch, pgsql):
    # pylint: disable=unused-variable
    @patch('uuid.uuid4')
    def uuid4():
        class _uuid4:
            hex = 'hex'

        return _uuid4()

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    @patch('generated.clients.ocr_translate.OcrTranslateClient.recognize')
    async def _ocr_recognition(*args, **kwargs):
        return create_ocr_responce(text='picture_text')

    response = await web_app_client.post(
        V2_UPLOAD_URL, data=create_form(field_value='original', value='0'),
    )

    assert response.status == 200
    resp_data = await response.json()
    assert resp_data == {
        'id': 'mds-id',
        'url': 'https://some-cool-url.ya/mds-id',
    }

    _mds_upload_calls = _mds_upload.calls
    assert _mds_upload_calls[0]['kwargs']['key'] == 'hex.png'

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT id, type, resize_mode, sizes FROM promotions.media_tags '
            f'WHERE id = \'1234-5678_media_tag_id\'',
        )
        assert cursor.fetchone() == (
            '1234-5678_media_tag_id',
            'image',
            'height_fit',
            {
                'sizes': [
                    {
                        'url': 'https://some-cool-url.ya/mds-id',
                        'field': 'original',
                        'value': 0,
                        'mds_id': 'mds-id',
                        'media_text': 'picture_text',
                    },
                ],
            },
        )


@pytest.mark.pgsql('promotions', files=['pg_v2_upload.sql'])
@pytest.mark.config(ADMIN_IMAGE_RESIZE_MODES=_ADMIN_IMAGE_RESIZE_MODES)
async def test_image_v2_upload_mds_fail(web_app_client, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        raise Exception('Something want wrong way')

    response = await web_app_client.post(V2_UPLOAD_URL, data=create_form())
    assert response.status == 500


@pytest.mark.config(
    PROMOTIONS_MEDIA_CONTENT_SIZE_LIMITS=PROMOTIONS_MEDIA_CONTENT_SIZE_LIMITS,
)
async def test_image_v2_upload_too_large_file_fail(web_app_client, patch):
    file = b'1234512345123451234512345'
    content_type = 'image/png'

    response = await web_app_client.post(
        V2_UPLOAD_URL,
        data=create_form(file_data=file, content_type=content_type),
    )
    assert response.status == 500

    response_data = await response.json()
    assert response_data == {
        'message': 'Internal server error',
        'code': 'INTERNAL_SERVER_ERROR',
        'details': {'reason': 'Too large mediafile uploaded'},
    }


@pytest.mark.pgsql('promotions', files=['pg_v2_upload.sql'])
@pytest.mark.config(ADMIN_IMAGE_RESIZE_MODES=_ADMIN_IMAGE_RESIZE_MODES)
async def test_image_v2_upload_client_size_not_found(web_app_client, patch):
    form = create_form(field_value='screen_width')

    response = await web_app_client.post(V2_UPLOAD_URL, data=form)
    assert response.status == 404


@pytest.mark.pgsql('promotions', files=['pg_v2_upload.sql'])
@pytest.mark.parametrize(
    'file, content_type, compressed_file, expected_uploaded_file, compress',
    [
        pytest.param(
            b'121212',
            'image/png',
            b'3434',
            b'3434',
            True,
            id='Succesful compress',
        ),
        pytest.param(
            b'121212',
            'image/png',
            b'3434',
            b'121212',
            False,
            id='Compress is unavailable',
        ),
        pytest.param(
            b'121212',
            'image/other',
            b'3434',
            b'121212',
            True,
            id='Try to compress with unknown content_type',
        ),
    ],
)
@pytest.mark.config(PROMOTIONS_IMAGE_COMPRESSION_V2={'png': {'enabled': True}})
async def test_image_v2_upload_with_compress(
        web_app_client,
        patch,
        mockserver,
        file,
        content_type,
        compressed_file,
        expected_uploaded_file,
        compress,
):
    @mockserver.handler('/taxi-admin-images/internal/compress-png')
    def _mock_compress(request):
        if compress:
            return aiohttp.web.Response(body=compressed_file)
        return aiohttp.web.HTTPInternalServerError()

    uploaded_data = None

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        nonlocal uploaded_data
        uploaded_data = kwargs['body']
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    response = await web_app_client.post(
        V2_UPLOAD_URL,
        data=create_form(file_data=file, content_type=content_type),
    )

    assert response.status == 200
    assert uploaded_data == expected_uploaded_file
