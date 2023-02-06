from generated.clients import resizer
from taxi.clients import mds_s3

from chatterbox_admin.stq import generate_preview


async def test_generate_preview(stq3_context, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.generate_download_url')
    async def _mds_s3_generate_download_url(*args, **kwargs):
        return 'http://test-url.net/key'

    @patch('generated.clients.resizer.ResizerClient.genurl')
    async def _mock_genurl(*args, **kwargs):
        return resizer.Genurl200(body='http://test-url.net/new_key')

    @patch('chatterbox_admin.stq.generate_preview._download_file')
    async def _check_preview(*args, **kwargs):
        return b'qwerty'

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_s3_mock(*args, **kwargs):
        return mds_s3.S3Object(Key='key', ETag=None)

    await generate_preview.task(stq3_context, mds_key='test')
    assert _mds_s3_generate_download_url.calls
    assert _mock_genurl.calls
    assert _check_preview.calls
    assert _mds_s3_mock.calls
