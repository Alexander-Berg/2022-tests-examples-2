import aiohttp

from taxi.clients import mds_s3


async def _exec_default_test_request(web_app_client):
    form = aiohttp.FormData()
    form.add_field(
        name='content', value=b'123123123', filename='test_audio.mp3',
    )
    form.add_field(name='type', value='audio')
    form.add_field(name='idempotency_key', value='token')
    return await web_app_client.post('/v1/upload', data=form)


async def test_audio_upload(web_app_client, simple_secdist, patch):
    @patch('uuid.uuid4')
    def _uuid4():
        class _uuid4:
            hex = 'aaaabbbb0000'

        return _uuid4()

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    response = await _exec_default_test_request(web_app_client)

    resp_data = await response.json()
    assert resp_data == {
        'id': 'mds-id',
        'url': 'https://audiolinks.s3.yandex.net/aaaabbbb0000.mp3',
    }

    _mds_upload_calls = _mds_upload.calls
    assert _mds_upload_calls[0]['kwargs']['key'] == 'aaaabbbb0000.mp3'


async def test_audio_upload_mds_fail(web_app_client, simple_secdist, patch):
    @patch('uuid.uuid4')
    def _uuid4():
        class _uuid4:
            hex = 'aaaabbbb0000'

        return _uuid4()

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        raise Exception('MDS exception')

    response = await _exec_default_test_request(web_app_client)

    assert response.status == 500
    assert await response.json() == {
        'code': 'INTERNAL_SERVER_ERROR',
        'details': {'reason': 'MDS exception'},
        'message': 'Internal server error',
    }
