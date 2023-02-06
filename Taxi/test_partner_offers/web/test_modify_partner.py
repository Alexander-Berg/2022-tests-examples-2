import pytest

TRANSLATIONS = {'Food': {'ru': 'Еда', 'en': 'Food'}}

PARTNER_DEALS_PARTNER_CATEGORIES_STUB = [
    {
        'category': 'food',
        'name': 'Food',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
    },
    {
        'category': 'service',
        'name': 'invalid_key',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
    },
]

INSERT_QUERY = """INSERT INTO partner
     (category, name, logo, comment, created_by,
      created_at, updated_by, updated_at)
VALUES (
        'food',
        'Big zombie shop',
        'https://example.com/image.jpg',
        'Some comment text',
        'valery',
        '2019-05-26 19:10:25+3',
        'valery',
        '2019-05-26 19:10:25+3'
       );
INSERT INTO location(business_oid, partner_id, longitude,
 latitude, country, city, address, name, work_time_intervals, tz_offset)
VALUES (
        123456,
        (SELECT id FROM partner WHERE name = 'Big zombie shop'),
        40.5,
        80.4,
        'Russia',
        'Moscow',
        'Москва, Лубянка, 5',
        'Big zombie shop',
        '[]'::JSONB,
        0
       );"""


@pytest.mark.pgsql('partner_offers', queries=[INSERT_QUERY])
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'json',
    [
        {'category': 'service', 'comment': 'some other comment'},
        {'comment': 'some other other comment'},
    ],
)
async def test_modify_partner_ok(web_app_client, json):
    response = await web_app_client.put(
        '/internal/v1/partners/deal-related-fields?partner_id=1',
        json=json,
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 200, await response.text()
    response_json = await response.json()
    del response_json['changelog']['updated_at']
    assert response_json == {
        'id': '1',
        'name': 'Big zombie shop',
        'logo': 'https://example.com/image.jpg',
        'deals_related': json,
        'locations': [
            {
                'name': 'Russia, Moscow',
                'locations': [
                    {
                        'address': 'Москва, Лубянка, 5',
                        'name': 'Big zombie shop',
                        'id': '123456',
                        'map_link': f'https://yandex.ru/maps/?mode=search&ol=biz&oid=123456',  # noqa: E501
                    },
                ],
            },
        ],
        'changelog': {
            'updated_by': 'Piter',
            'created_by': 'valery',
            'created_at': '2019-05-26T19:10:25+03:00',
        },
    }


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_modify_partner_not_found(web_app_client):
    response = await web_app_client.put(
        '/internal/v1/partners/deal-related-fields?partner_id=1',
        json={'category': 'food', 'comment': 'some other comment'},
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 404, await response.text()
    assert await response.json() == {
        'code': 'not_found',
        'text': 'Not found partner with id 1.',
    }
