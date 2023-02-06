import io

import aiohttp
from PIL import Image
import pytest

from taxi.clients import mds_s3


@pytest.mark.config(
    AGENT_S3_FOLDER_SETTINGS={
        'news': {'allowed_types': ['any']},
        'shop': {'allowed_types': ['any', 'image']},
        'avatar': {'allowed_types': ['image']},
    },
)
@pytest.mark.parametrize(
    'url,login,content,code,expected_data',
    [
        ('/file/shop', 'webalex', 'test-data', 201, {}),
        (
            '/file/achievements',
            'justmark0',
            b'\x20\x21\x22',
            400,
            {'code': 'error_wrong_folder', 'message': 'General error'},
        ),
        ('/file/news', 'justmark0', b'\x20\x21\x22\x20\x21\x22', 201, {}),
        ('/file/avatar', 'justmark0', 'image', 201, {}),
        (
            '/file/avatar',
            'justmark0',
            b'\x20\x21\x22\x20\x21\x22',
            400,
            {
                'code': 'error_not_supported_file_type',
                'message': 'General error',
            },
        ),
    ],
)
async def test_save_file(
        web_app_client,
        web_context,
        patch,
        url,
        login,
        content,
        code,
        expected_data,
):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_s3_mock(*args, **kwargs):
        return mds_s3.S3Object(Key='key', ETag=None)

    if content == 'image':
        img_byte_arr = io.BytesIO()
        Image.new('RGB', (100, 100)).save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()

    form = aiohttp.FormData()
    form.add_field(name='file', value=content, filename='test_name')
    response = await web_app_client.post(
        url, data=form, headers={'X-Yandex-Login': login},
    )
    assert response.status == code
    if code == 201:
        content = await response.json()
        assert content['file_id']
        assert content['link']
    if code == 400:
        content = await response.json()
        assert content == expected_data
