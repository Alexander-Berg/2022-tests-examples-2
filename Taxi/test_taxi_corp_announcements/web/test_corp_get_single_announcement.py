from aiohttp import web
import pytest

CLIENT_ID = 'client_id'
ANNOUNCEMENT_ID_NEWS = '12345'
ANNOUNCEMENT_ID_PROMO = '54321'
IMAGE_URL = '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig'


@pytest.mark.parametrize(
    'yandex_uid',
    [
        pytest.param('123456', id='announcement_for_client'),
        pytest.param('234567', id='announcement_for_manager'),
        pytest.param('345678', id='announcement_for_department_manager'),
        pytest.param('456789', id='announcement_for_department_secretary'),
    ],
)
@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_corp_get_single_announcement(
        web_app_client, web_context, mockserver, yandex_uid,
):
    @mockserver.json_handler('/passport/blackbox')
    async def _passport(request):
        return web.json_response({'users': [{'uid': {'value': yandex_uid}}]})

    response = await web_app_client.get(
        '/v1/announcement',
        params={
            'announcement_id': ANNOUNCEMENT_ID_NEWS,
            'yandex_uid': yandex_uid,
            'client_id': CLIENT_ID,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'announcement_id': '12345',
        'announcement_type': 'news',
        'base_image': {
            'sizes': {'orig': {'height': 456, 'width': 123, 'url': IMAGE_URL}},
        },
        'publish_at': '2019-07-24T13:30:00+03:00',
        'status': 'not_read',
        'text': 'Текст новости',
        'title': 'Заголовок',
        'cta_is_active': True,
        'cta_title': 'CTA button title',
        'cta_url': 'https://yandex.ru',
    }


@pytest.mark.parametrize(
    'yandex_uid',
    [
        pytest.param('123456', id='announcement_for_client'),
        pytest.param('234567', id='announcement_for_manager'),
        pytest.param('345678', id='announcement_for_department_manager'),
        pytest.param('456789', id='announcement_for_department_secretary'),
    ],
)
@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_corp_get_single_promo(
        web_app_client, web_context, mockserver, yandex_uid,
):
    @mockserver.json_handler('/passport/blackbox')
    async def _passport(request):
        return web.json_response({'users': [{'uid': {'value': yandex_uid}}]})

    response = await web_app_client.get(
        '/v1/announcement',
        params={
            'announcement_id': ANNOUNCEMENT_ID_PROMO,
            'yandex_uid': yandex_uid,
            'client_id': CLIENT_ID,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'announcement_id': '54321',
        'announcement_type': 'promo',
        'base_image': {
            'sizes': {'orig': {'height': 456, 'width': 123, 'url': IMAGE_URL}},
        },
        'publish_at': '2019-07-24T13:30:00+03:00',
        'status': 'not_read',
        'text': 'Текст новости3',
        'title': 'Заголовок3',
        'cta_is_active': False,
        'cta_title': '',
        'cta_url': '',
    }


@pytest.mark.parametrize(
    'yandex_uid',
    [
        pytest.param('123456', id='announcement_for_client'),
        pytest.param('234567', id='announcement_for_manager'),
        pytest.param('345678', id='announcement_for_department_manager'),
        pytest.param('456789', id='announcement_for_department_secretary'),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_corp_get_single_announcement_fail(
        web_app_client, web_context, mockserver, yandex_uid,
):
    @mockserver.json_handler('/passport/blackbox')
    async def _passport(request):
        return web.json_response({'users': [{'uid': {'value': yandex_uid}}]})

    response = await web_app_client.get(
        '/v1/announcement',
        params={
            'announcement_id': ANNOUNCEMENT_ID_NEWS,
            'yandex_uid': yandex_uid,
            'client_id': CLIENT_ID,
        },
    )
    assert response.status == 403
    content = await response.json()
    assert content == {
        'code': 'invalid-input',
        'details': {},
        'message': 'access denied',
        'status': 'error',
    }
