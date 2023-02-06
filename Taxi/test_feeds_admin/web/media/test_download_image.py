import aiohttp
import pytest

from testsuite.utils import http


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    'media_id, is_exist, content, status',
    [
        pytest.param(
            'existed_image',
            True,
            b'image binary \x00 data',
            200,
            id='get_existed_image',
        ),
        pytest.param(
            'existed_image', False, None, 502, id='get_image_that_has_gone',
        ),
        pytest.param(
            'not_existed_image', None, None, 404, id='get_not_existed_image',
        ),
    ],
)
async def test_download_image(
        web_app_client, patch, mockserver, media_id, content, is_exist, status,
):
    @mockserver.handler('/mds_avatars/get-feeds-media', prefix=True)
    async def _mds_avatars_mock(request: http.Request):
        if is_exist:
            return aiohttp.web.Response(
                status=200,
                body=content,
                headers={'Content-Type': 'image/png'},
            )
        return aiohttp.web.Response(text='Gone', status=410)

    response = await web_app_client.get(
        '/v1/media/download', params={'media_id': media_id},
    )

    assert response.status == status
    if status == 200:
        get_content = await response.read()
        assert get_content == content
