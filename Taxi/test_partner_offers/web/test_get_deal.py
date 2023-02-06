import pytest

EXPECTED_RESPONSES = [
    {
        'id': '1',
        'partner_id': '1',
        'basic_data': {
            'title': 'First',
            'description_title': 'some',
            'kind': {
                'old_price': {'decimal_value': '5', 'currency': 'RUB'},
                'new_price': {'decimal_value': '4', 'currency': 'RUB'},
            },
            'is_enabled': True,
            'loyalty_statuses': [
                {'loyalty': 'bronze', 'is_enabled': False},
                {'loyalty': 'gold', 'is_enabled': False},
                {'loyalty': 'platinum', 'is_enabled': False},
                {'loyalty': 'silver', 'is_enabled': True},
            ],
            'begin_at': '2019-05-26T19:10:25+03:00',
        },
        'locations': [
            {
                'name': 'Russia, Moscow',
                'locations': [
                    {
                        'id': '101',
                        'name': 'Big zombie shop',
                        'is_enabled': True,
                        'address': 'Москва, Лубянка, 5',
                        'map_link': (
                            'https://yandex.ru/maps/'
                            '?mode=search&ol=biz&oid=101'
                        ),
                    },
                ],
            },
            {
                'name': 'Russia',
                'locations': [
                    {
                        'id': '102',
                        'name': 'Cataclyzm',
                        'is_enabled': True,
                        'address': 'Россия, Лубянка, 5',
                        'map_link': (
                            'https://yandex.ru/maps/'
                            '?mode=search&ol=biz&oid=102'
                        ),
                    },
                ],
            },
        ],
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ульянов'},
    },
    {
        'id': '2',
        'partner_id': '1',
        'basic_data': {
            'title': 'Second',
            'description_title': 'some',
            'kind': {
                'text': 'Hee',
                'price': {'decimal_value': '5', 'currency': 'RUB'},
            },
            'is_enabled': True,
            'loyalty_statuses': [
                {'loyalty': '1', 'is_enabled': True},
                {'loyalty': '2', 'is_enabled': False},
                {'loyalty': '3', 'is_enabled': True},
                {'loyalty': '4', 'is_enabled': False},
                {'loyalty': '5', 'is_enabled': True},
            ],
            'begin_at': '2019-05-26T19:10:25+03:00',
            'finish_at': '2020-05-26T19:10:25+03:00',
        },
        'locations': [
            {
                'name': 'Russia, Moscow',
                'locations': [
                    {
                        'id': '101',
                        'name': 'Big zombie shop',
                        'is_enabled': True,
                        'address': 'Москва, Лубянка, 5',
                        'map_link': (
                            'https://yandex.ru/maps/'
                            '?mode=search&ol=biz&oid=101'
                        ),
                    },
                ],
            },
            {
                'name': 'Russia',
                'locations': [
                    {
                        'id': '102',
                        'name': 'Cataclyzm',
                        'is_enabled': False,
                        'address': 'Россия, Лубянка, 5',
                        'map_link': (
                            'https://yandex.ru/maps/'
                            '?mode=search&ol=biz&oid=102'
                        ),
                    },
                ],
            },
        ],
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ульянов'},
    },
    {
        'id': '3',
        'partner_id': '2',
        'basic_data': {
            'title': 'First',
            'description_title': 'some',
            'kind': {'text': 'Some', 'decimal_percent': '10'},
            'is_enabled': True,
            'loyalty_statuses': [
                {'loyalty': 'bronze', 'is_enabled': True},
                {'loyalty': 'gold', 'is_enabled': False},
                {'loyalty': 'platinum', 'is_enabled': True},
                {'loyalty': 'silver', 'is_enabled': True},
            ],
            'begin_at': '2019-05-26T19:10:25+03:00',
            'comment': 'test comment',
            'contractor_merch_offer_id': '01234567890123456789012345678901',
        },
        'locations': [
            {
                'name': 'Moscow',
                'locations': [
                    {
                        'id': '103',
                        'name': 'Big zombie shop',
                        'is_enabled': True,
                        'address': 'Москва, Лубянка, 5',
                        'map_link': (
                            'https://yandex.ru/maps/'
                            '?mode=search&ol=biz&oid=103'
                        ),
                    },
                ],
            },
        ],
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ульянов'},
    },
]


@pytest.mark.pgsql('partner_offers', files=['pg_init.sql'])
@pytest.mark.parametrize(
    'deal_id,consumer', zip([1, 2, 3], ['driver', 'courier', 'driver']),
)
async def test_get_ok(web_app_client, deal_id, consumer):
    uri = f'/internal/v1/deals/{consumer}?deal_id={deal_id}'
    response = await web_app_client.get(uri)
    assert response.status == 200, await response.text()
    resp_json = await response.json()
    del resp_json['changelog']['created_at']
    del resp_json['changelog']['updated_at']
    assert resp_json == EXPECTED_RESPONSES[deal_id - 1]


@pytest.mark.pgsql('partner_offers', files=['pg_init.sql'])
@pytest.mark.parametrize(
    'deal_id,consumer',
    zip([1, 2, 5, 1], ['courier', 'driver', 'driver', 'invalid_consumer']),
)
async def test_get_not_found(web_app_client, deal_id, consumer):
    uri = f'/internal/v1/deals/{consumer}?deal_id={deal_id}'
    response = await web_app_client.get(uri)
    assert response.status == 404, await response.text()
