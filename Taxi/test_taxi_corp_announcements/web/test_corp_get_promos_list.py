import pytest

CLIENT_ID = 'client_id'
YANDEX_UID = '56789'


@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_corp_get_announcements_list(web_app_client, mockserver):
    response = await web_app_client.get(
        '/v1/announcements/promos',
        params={'yandex_uid': YANDEX_UID, 'client_id': CLIENT_ID},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'announcements': [
            {
                'announcement_id': '54324',
                'announcement_type': 'promo',
                'base_image': {
                    'sizes': {
                        'orig': {
                            'height': 456,
                            'width': 123,
                            'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                        },
                    },
                },
                'publish_at': '2019-07-24T13:30:00+03:00',
                'status': 'not_read',
                'text': 'Текст новости6',
                'title': 'Заголовок6',
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
            },
            {
                'announcement_id': '54323',
                'announcement_type': 'promo',
                'base_image': {
                    'sizes': {
                        'orig': {
                            'height': 456,
                            'width': 123,
                            'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                        },
                    },
                },
                'publish_at': '2019-07-24T13:30:00+03:00',
                'status': 'not_read',
                'text': 'Текст новости5',
                'title': 'Заголовок5',
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
            },
            {
                'announcement_id': '54322',
                'announcement_type': 'promo',
                'base_image': {
                    'sizes': {
                        'orig': {
                            'height': 456,
                            'width': 123,
                            'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                        },
                    },
                },
                'publish_at': '2019-07-24T13:30:00+03:00',
                'status': 'not_read',
                'text': 'Текст новости4',
                'title': 'Заголовок4',
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
            },
            {
                'announcement_id': '54321',
                'announcement_type': 'promo',
                'base_image': {
                    'sizes': {
                        'orig': {
                            'height': 456,
                            'width': 123,
                            'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                        },
                    },
                },
                'publish_at': '2019-07-24T13:30:00+03:00',
                'status': 'not_read',
                'text': 'Текст новости3',
                'title': 'Заголовок3',
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
            },
        ],
    }


async def test_corp_get_announcements_empty_list(web_app_client):
    response = await web_app_client.get(
        '/v1/announcements/promos',
        params={'yandex_uid': YANDEX_UID, 'client_id': CLIENT_ID},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'announcements': []}
