import re

import aiohttp
import pytest


async def post_media(taxi_messenger, *, file_name=None):
    form = aiohttp.FormData()
    form.add_field(name='content', value=b'file binary \x00 data')
    form.add_field(name='content_type', value='application/octet-stream')
    form.add_field(name='media_type', value='document')
    form.add_field(
        name='content_file_name',
        value='some_file.ext' if file_name is None else file_name,
    )
    form.add_field(name='service', value='chatterbox')
    return await taxi_messenger.post('/v1/media/upload', data=form)


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_upload_media(taxi_messenger, mongodb, load_json):
    response = await post_media(taxi_messenger)

    media = next(mongodb.messenger_media.find({}))
    assert re.fullmatch(r'([0-9a-f]{32})', media['media_id'])
    assert media == dict(
        load_json('mongo_media.json')['uploaded'],
        **{'_id': media['_id'], 'media_id': media['media_id']},
    )

    assert response.status_code == 200
    assert response.json()['media_id'] == media['media_id']


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_upload_media_s3(taxi_messenger, mockserver):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        assert request.content_type == 'application/octet-stream'
        assert request.get_data() == b'file binary \x00 data'
        return mockserver.make_response('', 200)

    await post_media(taxi_messenger)


async def test_upload_media_storage_timeout(taxi_messenger, mockserver):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        raise mockserver.TimeoutError()

    response = await post_media(taxi_messenger)
    assert response.status_code == 504


async def test_upload_media_storage_invalid_input(taxi_messenger):
    response = await post_media(taxi_messenger, file_name='some_/file.ext')
    assert response.status_code == 400


async def test_upload_media_storage_error(taxi_messenger, mockserver):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        return mockserver.make_response('Some error', 500)

    response = await post_media(taxi_messenger)
    assert response.status_code == 502
