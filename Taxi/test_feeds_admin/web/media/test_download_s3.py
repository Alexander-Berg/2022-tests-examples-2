import pytest


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_s3.sql'])
async def test_download_s3_ok(web_app_client, patch, mockserver):
    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _mds_s3_mock(*args, **kwargs):
        assert kwargs['key'] == f'example/existed_video'
        assert kwargs['bucket_name'] == 'feeds-admin-media-example'
        return b'image binary \x00 data'

    response = await web_app_client.get(
        '/v1/media/download', params={'media_id': 'existed_video'},
    )
    assert response.status == 200
    get_content = await response.read()
    assert get_content == b'image binary \x00 data'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_s3.sql'])
async def test_download_s3_404(web_app_client, patch, mockserver):
    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _mds_s3_mock(*args, **kwargs):
        assert False

    response = await web_app_client.get(
        '/v1/media/download', params={'media_id': 'not_existed_video'},
    )
    assert response.status == 404
