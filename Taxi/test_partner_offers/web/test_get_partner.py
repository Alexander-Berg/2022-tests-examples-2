import pytest


@pytest.mark.pgsql(
    'partner_offers',
    queries=[
        """INSERT INTO partner
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
       );""",
    ],
)
async def test_ok(web_app_client):
    response = await web_app_client.get('/internal/v1/partners?partner_id=1')
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'id': '1',
        'name': 'Big zombie shop',
        'logo': 'https://example.com/image.jpg',
        'deals_related': {'category': 'food', 'comment': 'Some comment text'},
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
            'updated_by': 'valery',
            'updated_at': '2019-05-26T19:10:25+03:00',
            'created_by': 'valery',
            'created_at': '2019-05-26T19:10:25+03:00',
        },
    }


@pytest.mark.parametrize('stub_partner_id', ['1', 'sadf'])
async def test_not_found(web_app_client, stub_partner_id):
    response = await web_app_client.get(
        f'/internal/v1/partners?partner_id={stub_partner_id}',
    )
    assert response.status == 404, await response.text()
    assert await response.json() == {
        'code': 'not_found',
        'text': f'Not found partner with id {stub_partner_id}.',
    }
