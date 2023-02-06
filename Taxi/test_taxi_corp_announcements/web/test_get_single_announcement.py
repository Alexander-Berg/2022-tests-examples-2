from aiohttp import web
import pytest

X_YATAXI_API_KEY = 'test_api_key'
X_REAL_IP = 'test_user_ip'


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_get_single_announcement(
        web_app_client, web_context, mockserver, patch,
):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def _request(*args, **kwargs):
        return web.json_response(
            {'users': [{'uid': {'value': '3000062912'}, 'login': 'test'}]},
        )

    announcement_id = '12345'
    expected_response = {
        'announcement_id': announcement_id,
        'announcement_type': 'news',
        'triggers_in_sf': False,
        'admin_title': 'Название в админке',
        'priority': 0,
        'title': 'Заголовок',
        'text': 'Текст новости',
        'cta_is_active': True,
        'cta_title': 'CTA button title',
        'cta_url': 'https://yandex.ru',
        'base_image': {
            'image_id': 'image_id_001',
            'name': 'kitten0.jpg',
            'created_by': 'test',
            'created_at': '2019-08-18T18:30:27+03:00',
            'sizes': {
                'orig': {
                    'width': 123,
                    'height': 456,
                    'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                },
            },
        },
        'preview_image': {
            'image_id': 'image_id_001',
            'name': 'kitten0.jpg',
            'created_by': 'test',
            'created_at': '2019-08-18T18:30:27+03:00',
            'sizes': {
                'orig': {
                    'width': 123,
                    'height': 456,
                    'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                },
            },
        },
        'display_conditions': [
            {
                'condition': 'clients',
                'values': [{'filter': 'client_id1'}, {'filter': 'client_id2'}],
            },
            {
                'condition': 'roles',
                'values': [
                    {'filter': 'manager'},
                    {'filter': 'department_manager'},
                ],
            },
            {'condition': 'country', 'values': [{'filter': 'rus'}]},
            {'condition': 'payment_type', 'values': [{'filter': 'prepaid'}]},
            {
                'condition': 'common_contract',
                'values': [{'filter': 'available_enabled'}],
            },
            {'condition': 'vat', 'values': [{'filter': 'with_vat'}]},
        ],
        'status': 'need_approval',
        'comment': 'some comment',
        'publish_at': '2019-07-24T13:30:00+03:00',
        'created_by': 'test',
        'approved_by': 'test',
    }

    response = await web_app_client.get(
        '/v1/admin/announcement/',
        params={'announcement_id': announcement_id},
        headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY, 'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_get_single_announcement_not_found(web_app_client, web_context):
    announcement_id = 'not_found'
    response = await web_app_client.get(
        '/v1/admin/announcement/',
        params={'announcement_id': announcement_id},
        headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY, 'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 404
    content = await response.json()
    assert content == {
        'code': 'invalid-input',
        'details': {},
        'message': 'announcement not found',
        'status': 'error',
    }


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_get_single_announcement_no_id(web_app_client, web_context):
    response = await web_app_client.get(
        '/v1/admin/announcement/',
        headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY, 'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {'reason': 'announcement_id is required parameter'},
    }
