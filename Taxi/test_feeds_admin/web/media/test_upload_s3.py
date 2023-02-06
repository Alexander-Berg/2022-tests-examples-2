import aiohttp
import pytest

from taxi.clients import mds_s3


@pytest.mark.config(
    TVM_RULES=[{'dst': 'avatars-mds', 'src': 'feeds-admin'}],
    FEEDS_ADMIN_SERVICE_GROUPS={
        '__default__': {
            'media_content_types': {
                'video/mp4': {'enabled': True, 'max_size': 1048576},
            },
        },
        'normal_group': {'s3_bucket_group': 'example-service'},
    },
    FEEDS_ADMIN_SERVICES={
        '__default__': {},
        'normal_service': {
            'description': 'Обычный сервис с заданными параметрами',
            'service_group': 'normal_group',
        },
    },
    FEEDS_ADMIN_MEDIA_CONTENT_TYPES={
        'video/mp4': {'description': 'test type', 'media_type': 'video'},
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    'media_id, content_type, query_params, mds_response, status',
    [
        pytest.param(
            'new_video',
            'video/mp4',
            {'service': 'normal_service'},
            {},
            200,
            id='upload_new_video',
        ),
    ],
)
async def test_upload_video(
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

    uploads = {}

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(key, body, *args, **kwargs):
        uploads[key] = body
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    @mock_feeds('/v1/media/register')
    async def handler_register(request):  # pylint: disable=W0612
        assert request.json['media_id'] == media_id
        assert request.json['media_type'] == 'video'
        assert request.json['storage_settings'] == {
            'bucket_name': 'feeds-admin-media-example-service',
            'service': 'default',
        }
        assert request.json['storage_type'] == 's3'
        return aiohttp.web.json_response({})

    form = aiohttp.FormData()
    form.add_field(
        name='content',
        value=b'video binary \x00 data',
        filename='filename',
        content_type=content_type,
    )
    response = await web_app_client.post(
        '/v1/media/upload', data=form, params=query_params,
    )

    assert response.status == status
    if status == 200:
        json_response = await response.json()
        assert json_response.get('media_id') == media_id
        assert json_response.get('media_type') == 'video'
