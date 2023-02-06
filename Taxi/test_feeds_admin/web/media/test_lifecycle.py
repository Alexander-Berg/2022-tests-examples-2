import aiohttp
import pytest

from testsuite.utils import http

MEDIA_CONTENT_META_DATA = {
    'group-id': 555,
    'imagename': 'abc123',
    'meta': {},
    'sizes': {
        'orig': {
            'height': 123,
            'path': '/get-taxi_corp/555/abc123/orig',
            'width': 456,
        },
    },
}
CONTENT = b'image binary \x00 data'
MEDIA_ID = 'media_id'
LINK = '$mockserver/mds_avatars/get-feeds-media/555/media_id/orig'
TAGS = ['tag1', 'tag2', 'tag3', 'tag4']


@pytest.mark.config(
    FEEDS_ADMIN_MEDIA_CONTENT_TYPES={
        'image/png': {'description': 'test type', 'media_type': 'image'},
    },
    FEEDS_ADMIN_SERVICES={
        '__default__': {'description': 'Параметры по умолчанию'},
        'test_service': {
            'description': 'Обычный сервис',
            'service_group': 'test_group',
        },
    },
    FEEDS_ADMIN_SERVICE_GROUPS={
        '__default__': {
            'media_content_types': {
                'image/png': {'enabled': True, 'max_size': 1048576},
            },
        },
    },
)
async def test_upload_image(web_app_client, mock_feeds, patch, mockserver):
    @patch('feeds_admin.views.media._generate_media_id')
    def _generate_media_id(*args):
        return 'media_id'

    @mockserver.handler('/mds_avatars/put-feeds-media', prefix=True)
    async def _mds_put_avatars_mock(request: http.Request):
        assert request.path == f'/mds_avatars/put-feeds-media/{MEDIA_ID}'
        return aiohttp.web.json_response(MEDIA_CONTENT_META_DATA)

    @mockserver.handler('/mds_avatars/get-feeds-media', prefix=True)
    async def _mds_get_avatars_mock(request: http.Request):
        return aiohttp.web.Response(
            status=200, body=CONTENT, headers={'Content-Type': 'image/png'},
        )

    @mock_feeds('/v1/media/register')
    async def handler_register(request):  # pylint: disable=W0612
        assert request.json['media_id'] == MEDIA_ID
        assert request.json['media_type'] == 'image'
        assert request.json['storage_type'] == 'avatars'
        return aiohttp.web.json_response({})

    # First time upload
    first_form = aiohttp.FormData()
    first_form.add_field(
        name='content',
        value=CONTENT,
        filename='filename',
        content_type='image/png',
    )
    first_form.add_field(name='tags', value='some_tag,another_tag')
    first_upload_response = await web_app_client.post(
        '/v1/media/upload/',
        data=first_form,
        params={'service': 'test_service'},
    )
    assert first_upload_response.status == 200
    first_upload_content = await first_upload_response.json()
    assert first_upload_content.get('media_id') == MEDIA_ID
    assert first_upload_content.get('media_type') == 'image'

    # Second time upload
    second_form = aiohttp.FormData()
    second_form.add_field(
        name='content',
        value=CONTENT,
        filename='filename',
        content_type='image/png',
    )
    second_upload_response = await web_app_client.post(
        '/v1/media/upload/', data=second_form,
    )
    assert second_upload_response.status == 400

    # Update
    update_response = await web_app_client.post(
        '/v1/media/update', json={'media_id': MEDIA_ID, 'tags': TAGS},
    )
    assert update_response.status == 200

    # Download
    download_response = await web_app_client.get(
        '/v1/media/download', params={'media_id': MEDIA_ID},
    )
    assert download_response.status == 200
    download_content = await download_response.read()
    assert download_content == CONTENT

    # Get url
    get_urls_response = await web_app_client.post(
        '/v1/media/get-urls', json={'media_ids': [MEDIA_ID]},
    )
    assert get_urls_response.status == 200
    get_urls_content = await get_urls_response.json()
    assert get_urls_content == {
        'urls': [
            {
                'media_id': MEDIA_ID,
                'media_type': 'image',
                'media_url': LINK,
                'tags': TAGS,
            },
        ],
    }

    # List
    list_response = await web_app_client.post('/v1/media/list', json={})
    assert list_response.status == 200
    list_content = await list_response.json()
    assert list_content == {
        'total': 1,
        'limit': 50,
        'offset': 0,
        'items': [
            {
                'media_id': MEDIA_ID,
                'media_type': 'image',
                'media_url': LINK,
                'tags': TAGS,
            },
        ],
    }
