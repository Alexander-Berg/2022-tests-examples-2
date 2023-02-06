import aiohttp

from taxi.clients import mds_s3


async def test_upload_download_file(web_app_client, patch, load_binary):
    file_cache = {}

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _upload_content(*args, **kwargs):
        file_cache[kwargs['key']] = kwargs['body']
        return mds_s3.S3Object(
            Key='mds-id', ETag=None, Size=len(kwargs['body']),
        )

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        assert kwargs['key'] in file_cache
        return file_cache[kwargs['key']]

    file_data = b'12345'
    file_name = 'test'

    form = aiohttp.FormData()
    form.add_field(
        name='file',
        value=file_data,
        filename=file_name,
        content_type='application/octet-stream',
    )

    response = await web_app_client.post(
        '/v1/files?user_id=34&project_slug=test', data=form,
    )

    assert response.status == 200
    response_json = await response.json()

    file_id = response_json['file']['id']

    response = await web_app_client.get(
        f'/v1/files/{file_id}?user_id=34&project_slug=test',
    )

    assert response.status == 200

    assert (await response.read()) == file_data
