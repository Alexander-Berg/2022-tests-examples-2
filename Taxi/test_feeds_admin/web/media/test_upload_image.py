import aiohttp
import pytest

from testsuite.utils import http

MEDIA_CONTENT_META_DATA = {
    'group-id': 555,
    'imagename': 'abc123',
    'meta': {
        'crc64': 'C48CAD7438230F01',
        'md5': 'e3654575e1049c081a1b05e50972e18e',
        'modification-time': 1551452529,
        'orig-animated': False,
        'orig-format': 'JPEG',
        'orig-orientation': '',
        'orig-size': {'x': 123, 'y': 456},
        'orig-size-bytes': 123456,
        'processed_by_computer_vision': False,
        'processed_by_computer_vision_description': (
            'computer vision is disabled'
        ),
        'processing': 'finished',
    },
    'sizes': {
        'orig': {
            'height': 123,
            'path': '/get-taxi_corp/555/abc123/orig',
            'width': 456,
        },
        'img128x128': {
            'height': 128,
            'path': '/get-taxi_corp/555/abc123/img128x128',
            'width': 128,
        },
    },
}


@pytest.mark.config(
    TVM_RULES=[{'dst': 'avatars-mds', 'src': 'feeds-admin'}],
    FEEDS_ADMIN_MEDIA_CONTENT_TYPES={
        'image/png': {'description': 'test type', 'media_type': 'image'},
    },
    FEEDS_ADMIN_SERVICE_GROUPS={
        '__default__': {
            'media_content_types': {
                'image/png': {'enabled': True, 'max_size': 1048576},
            },
        },
        'normal_group': {
            'media_content_types': {
                'image/png': {'enabled': True, 'max_size': 100},
            },
        },
        'short_data_group': {
            'media_content_types': {
                'image/png': {'enabled': True, 'max_size': 1},
            },
        },
    },
    FEEDS_ADMIN_SERVICES={
        '__default__': {},
        'normal_service': {
            'description': 'Обычный сервис с заданными параметрами',
            'service_group': 'normal_group',
        },
        'short_data_service': {
            'description': (
                'Сервис со слишком жёсткими ограничениями ' 'на медиа-контент'
            ),
            'service_group': 'short_data_group',
        },
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    'media_id, content_type, query_params, mds_response, status',
    [
        pytest.param(
            'new_image',
            'image/png',
            {},
            MEDIA_CONTENT_META_DATA,
            200,
            id='upload_new_image',
        ),
        pytest.param(
            'existed_image',
            'image/png',
            {},
            None,
            200,
            id='upload_existed_image',
        ),
        pytest.param(
            'net_content', 'image/bmp', {}, None, 400, id='unknown_type',
        ),
        pytest.param(
            'new_image',
            'image/png',
            {'service': 'normal_service'},
            MEDIA_CONTENT_META_DATA,
            200,
            id='upload_new_image_to_service',
        ),
        pytest.param(
            'new_image',
            'image/png',
            {'service': 'unsepcified_service'},
            MEDIA_CONTENT_META_DATA,
            200,
            id='upload_new_image_to_other_service',
        ),
        pytest.param(
            'new_image',
            'image/png',
            {'service': 'short_data_service'},
            MEDIA_CONTENT_META_DATA,
            400,
            id='upload_too_big_image',
        ),
    ],
)
async def test_upload_image(
        web_app_client,
        mock_feeds,
        patch,
        mockserver,
        media_id,
        content_type,
        query_params,
        mds_response,
        status,
):
    @patch('feeds_admin.views.media._generate_media_id')
    def _generate_media_id(*args):
        return media_id

    @mockserver.handler('/mds_avatars/put-feeds-media', prefix=True)
    async def _mds_avatars_mock(request: http.Request):
        assert request.path == f'/mds_avatars/put-feeds-media/{media_id}'
        return aiohttp.web.json_response(mds_response)

    @mock_feeds('/v1/media/register')
    async def handler_register(request):  # pylint: disable=W0612
        assert request.json['media_id'] == media_id
        assert request.json['media_type'] == 'image'
        assert request.json['storage_type'] == 'avatars'
        return aiohttp.web.json_response({})

    form = aiohttp.FormData()
    form.add_field(
        name='content',
        value=b'image binary \x00 data',
        filename='filename',
        content_type=content_type,
    )
    response = await web_app_client.post(
        '/v1/media/upload/', data=form, params=query_params,
    )

    assert response.status == status
    if status == 200:
        json_response = await response.json()
        assert json_response.get('media_id') == media_id
        assert json_response.get('media_type') == 'image'
