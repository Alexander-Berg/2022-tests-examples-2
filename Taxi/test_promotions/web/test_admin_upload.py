import aiohttp
import pytest

from taxi.clients import mds_s3

UPLOAD_URL = 'admin/promotions/upload/'


def create_form():
    form = aiohttp.FormData()
    form.add_field(
        name='content', value=b'123123123', filename='some_fielanme.png',
    )
    form.add_field(name='type', value='image')
    form.add_field(name='idempotency_key', value='token')
    return form


@pytest.mark.config(
    PROMOTIONS_IMAGES_URL_TEMPLATE='https://some-cool-url.ya/{}',
)
async def test_image_upload(web_app_client, patch):
    # pylint: disable=unused-variable
    @patch('uuid.uuid4')
    def uuid4():
        class _uuid4:
            hex = 'hex'

        return _uuid4()

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    response = await web_app_client.post(UPLOAD_URL, data=create_form())
    resp_data = await response.json()
    assert resp_data == {
        'id': 'mds-id',
        'url': 'https://some-cool-url.ya/mds-id',
    }

    _mds_upload_calls = _mds_upload.calls
    assert _mds_upload_calls[0]['kwargs']['key'] == 'hex.png'


async def test_image_upload_fail(web_app_client, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        raise Exception('Something want wrong way')

    response = await web_app_client.post(UPLOAD_URL, data=create_form())
    assert response.status == 500
