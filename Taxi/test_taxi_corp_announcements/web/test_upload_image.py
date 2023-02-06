import datetime

import aiohttp
import pytest

from testsuite.utils import http

from taxi_corp_announcements.api.common import images_helper as helper
from taxi_corp_announcements.internal import base_context


UTC_NOW = datetime.datetime(2019, 1, 1, 7, 10, 0)
MOSCOW_NOW = '2019-01-01T10:10:00+03:00'


X_YANDEX_UID = '12345'


@pytest.mark.parametrize(
    'image_id, filename, mds_response, expected_response',
    [
        pytest.param(
            'abc123',
            'kitten.jpg',
            {
                'group-id': 555,
                'imagename': 'abc123',
                'meta': {
                    'crc64': 'C48CAD7438230F01',
                    'md5': 'e3654575e1049c081a1b05e50972e18e',
                    'modification-time': 1551452529,
                    'orig-animated': False,
                    'orig-format': 'JPEG',
                    'orig-orientation': '',
                    'orig-size': {'x': 123, 'y': 456},
                    'orig-size-bytes': 123456,
                    'processed_by_computer_vision': False,
                    'processed_by_computer_vision_description': (
                        'computer vision is disabled'
                    ),
                    'processing': 'finished',
                },
                'sizes': {
                    'orig': {
                        'height': 123,
                        'path': '/get-taxi_corp/555/abc123/orig',
                        'width': 456,
                    },
                    'img128x128': {
                        'height': 128,
                        'path': '/get-taxi_corp/555/abc123/img128x128',
                        'width': 128,
                    },
                },
            },
            {
                'image_id': 'abc123',
                'name': 'kitten.jpg',
                'created_by': 'test',
                'created_at': MOSCOW_NOW,
                'sizes': {
                    'orig': {
                        'height': 123,
                        'url': '$mockserver/mds_avatars/get-taxi_corp/555/abc123/orig',  # noqa: E501 pylint: disable=line-too-long
                        'width': 456,
                    },
                    'img128x128': {
                        'height': 128,
                        'url': '$mockserver/mds_avatars/get-taxi_corp/555/abc123/img128x128',  # noqa: E501 pylint: disable=line-too-long
                        'width': 128,
                    },
                },
            },
            id='upload_image',
        ),
    ],
)
@pytest.mark.now(MOSCOW_NOW)
async def test_upload_image(
        web_app_client,
        web_context,
        patch,
        mockserver,
        image_id,
        filename,
        mds_response,
        expected_response,
):
    @patch('taxi_corp_announcements.api.upload_image.create_id')
    def _create_id():
        return image_id

    @mockserver.json_handler('/passport-yateam/blackbox')
    async def _passport_yateam_mock(*args, **kwargs):
        return aiohttp.web.json_response(
            {
                'users': [
                    {'uid': {'value': str(X_YANDEX_UID)}, 'login': 'test'},
                ],
            },
        )

    @mockserver.handler('/mds_avatars/put-taxi_corp', prefix=True)
    async def _mds_avatars_mock(request: http.Request):
        assert request.path == '/mds_avatars/put-taxi_corp/{}'.format(image_id)
        return aiohttp.web.json_response(mds_response)

    form = aiohttp.FormData()
    form.add_field(
        name='file', value=b'image binary \x00 data', filename=filename,
    )
    response = await web_app_client.post(
        '/v1/admin/images/',
        data=form,
        headers={'X-Real-Ip': '1.2.3.4', 'X-Yandex-Uid': X_YANDEX_UID},
    )

    assert response.status == 200
    response_json = await response.json()

    assert response_json == expected_response

    ctx = base_context.Web(web_context, 'fetch_image_by_id')
    db_images = await helper.fetch_images_by_ids(ctx, [image_id])

    assert len(db_images) == 1
    db_image = db_images[0]
    assert db_image.image_id == image_id
    assert db_image.name == filename
    assert db_image.avatars_group_id == mds_response['group-id']
    assert db_image.created_by == int(X_YANDEX_UID)
    assert db_image.created_at == UTC_NOW
    assert (
        db_image.sizes.to_db()
        == '{"orig": {"width": 456, "height": 123}, "img128x128": '
        '{"width": 128, "height": 128}}'
    )  # noqa: E501 pylint: disable=line-too-long
