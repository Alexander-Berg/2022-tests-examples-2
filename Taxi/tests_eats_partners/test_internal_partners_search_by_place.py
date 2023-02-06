import pytest


DATA_PERSONAL_BULK = {
    '111': 'partner1@partner.com',
    '222': 'partner2@partner.com',
    '333': 'partner3@partner.com',
    '444': 'partner4@partner.com',
    '555': 'partner5@partner.com',
    '666': 'partner6@partner.com',
    '777': 'partner7@partner.com',
    '888': 'partner8@partner.com',
    '999': 'partner9@partner.com',
    '000': 'partner10@partner.com',
}


PARTNERS = {
    1: {
        'country_code': 'RU',
        'email': 'partner1@partner.com',
        'personal_email_id': '111',
        'id': 1,
        'is_blocked': False,
        'is_fast_food': False,
        'name': '',
        'places': [100, 101, 102],
        'roles': [
            {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
            {'id': 2, 'slug': 'ROLE_LOL', 'title': 'lol'},
        ],
        'timezone': 'Europe/Moscow',
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
    },
    2: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'KZ',
        'email': 'partner2@partner.com',
        'personal_email_id': '222',
        'id': 2,
        'is_blocked': True,
        'is_fast_food': True,
        'name': '',
        'places': [100, 102],
        'roles': [
            {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
            {'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'},
        ],
        'timezone': 'Europe/Moscow',
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6333',
    },
    3: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'RU',
        'email': 'partner3@partner.com',
        'personal_email_id': '333',
        'id': 3,
        'is_blocked': False,
        'is_fast_food': True,
        'name': '',
        'places': [101, 102],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': 'Europe/Moscow',
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6334',
    },
    4: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'RU',
        'email': 'partner4@partner.com',
        'personal_email_id': '444',
        'id': 4,
        'is_blocked': False,
        'is_fast_food': True,
        'name': '',
        'places': [101],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': 'Europe/Moscow',
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6335',
    },
    5: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'KZ',
        'email': 'partner5@partner.com',
        'personal_email_id': '555',
        'id': 5,
        'is_blocked': True,
        'is_fast_food': False,
        'name': '',
        'places': [101, 102],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': 'Europe/Moscow',
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6336',
    },
    6: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'RU',
        'email': 'partner6@partner.com',
        'personal_email_id': '666',
        'id': 6,
        'is_blocked': False,
        'is_fast_food': False,
        'name': '',
        'places': [101],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': None,
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6337',
    },
    7: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'BY',
        'email': 'partner7@partner.com',
        'personal_email_id': '777',
        'id': 7,
        'is_blocked': False,
        'is_fast_food': False,
        'name': '',
        'places': [101],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': None,
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6338',
    },
    8: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'RU',
        'email': 'partner8@partner.com',
        'personal_email_id': '888',
        'id': 8,
        'is_blocked': True,
        'is_fast_food': True,
        'name': '',
        'places': [101, 102],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': None,
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6339',
    },
    9: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'RU',
        'email': 'partner9@partner.com',
        'personal_email_id': '999',
        'id': 9,
        'is_blocked': False,
        'is_fast_food': True,
        'name': '',
        'places': [101],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': None,
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6331',
    },
    10: {
        'blocked_at': '2021-05-05T08:00:00+00:00',
        'country_code': 'RU',
        'email': 'partner10@partner.com',
        'personal_email_id': '000',
        'id': 10,
        'is_blocked': False,
        'is_fast_food': False,
        'name': '',
        'places': [101],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': None,
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6330',
    },
}


async def test_bad_request(taxi_eats_partners):
    response = await taxi_eats_partners.get(
        '/internal/partners/v1/search_by_place',
    )

    assert response.status_code == 400


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'place_id,with_blocked,expected_partners',
    [
        ('100', True, [2, 1]),
        ('101', True, [10, 9, 8, 7, 6, 5, 4, 3, 1]),
        ('102', True, [8, 5, 3, 2, 1]),
        ('100', False, [1]),
        ('101', False, [10, 9, 7, 6, 4, 3, 1]),
        ('102', False, [3, 1]),
    ],
)
async def test_search_by_place(
        taxi_eats_partners,
        mockserver,
        place_id,
        with_blocked,
        expected_partners,
):
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _emails_bulk_retrieve(request):
        data = []
        for email_id in request.json['items']:
            assert email_id['id'] != ''
            data.append(
                {
                    'id': email_id['id'],
                    'value': DATA_PERSONAL_BULK[email_id['id']],
                },
            )
        return {'items': data}

    response = await taxi_eats_partners.get(
        '/internal/partners/v1/search_by_place?place_id='
        + place_id
        + '&limit=10&with_blocked='
        + ('true' if with_blocked else 'false'),
    )

    assert response.status_code == 200
    payload = []
    for index in expected_partners:
        payload.append(PARTNERS[index])
    assert response.json()['payload'] == payload
