from aiohttp import web
import pytest

X_YATAXI_API_KEY = 'test_api_key'
X_REAL_IP = 'test_user_ip'


@pytest.mark.parametrize(
    'limit, skip, expected_response',
    [
        pytest.param(
            None,
            None,
            {
                'announcements': [
                    {
                        'announcement_id': '01234',
                        'announcement_type': 'news',
                        'triggers_in_sf': False,
                        'admin_title': 'Название в админке',
                        'title': 'Заголовок0',
                        'priority': 0,
                        'country': ['rus'],
                        'status': 'need_approval',
                        'created_at': '2019-08-18T18:30:27+03:00',
                        'approved_at': '2019-08-18T18:33:27+03:00',
                        'created_by': 'test',
                        'approved_by': 'test',
                        'base_image': {
                            'sizes': {
                                'orig': {
                                    'height': 456,
                                    'width': 123,
                                    'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                                },
                            },
                        },
                        'preview_image': {
                            'sizes': {
                                'orig': {
                                    'height': 456,
                                    'width': 123,
                                    'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_002/orig',  # noqa: E501 pylint: disable=line-too-long
                                },
                            },
                        },
                    },
                    {
                        'announcement_id': '12345',
                        'announcement_type': 'promo',
                        'triggers_in_sf': False,
                        'admin_title': 'Название в админке1',
                        'title': 'Заголовок1',
                        'priority': 1,
                        'country': ['rus'],
                        'status': 'need_approval',
                        'created_at': '2019-08-18T18:30:27+03:00',
                        'approved_at': '2019-08-18T18:33:27+03:00',
                        'created_by': 'test',
                        'approved_by': 'test',
                    },
                ],
            },
            id='all_records',
        ),
        pytest.param(
            1,
            1,
            {
                'announcements': [
                    {
                        'announcement_id': '12345',
                        'announcement_type': 'promo',
                        'triggers_in_sf': False,
                        'admin_title': 'Название в админке1',
                        'title': 'Заголовок1',
                        'priority': 1,
                        'country': ['rus'],
                        'status': 'need_approval',
                        'created_at': '2019-08-18T18:30:27+03:00',
                        'approved_at': '2019-08-18T18:33:27+03:00',
                        'created_by': 'test',
                        'approved_by': 'test',
                    },
                ],
            },
            id='slice_records',
        ),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_get_announcements_list(
        web_app_client, mockserver, limit, skip, expected_response,
):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def _request(*args, **kwargs):
        return web.json_response(
            {'users': [{'uid': {'value': '3000062912'}, 'login': 'test'}]},
        )

    params = {}
    if limit:
        params['limit'] = limit
    if skip:
        params['skip'] = skip

    response = await web_app_client.get(
        '/v1/admin/announcements/',
        headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY, 'X-Real-Ip': X_REAL_IP},
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.pgsql('corp_announcements')
async def test_get_empty_announcements_list(web_app_client):
    response = await web_app_client.get(
        '/v1/admin/announcements/',
        headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY, 'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'announcements': []}
