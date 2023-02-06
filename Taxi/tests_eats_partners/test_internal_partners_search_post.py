import pytest

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
        'places': [201, 202],
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
        'places': [301, 302],
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
        'places': [401],
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
        'places': [501, 502],
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
        'places': [601],
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
        'places': [701],
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
        'places': [801, 802],
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
        'places': [901],
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
        'places': [1001],
        'roles': [{'id': 3, 'slug': 'ROLE_ASD', 'title': 'asd'}],
        'timezone': None,
        'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6330',
    },
}


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'code, expected',
    [
        pytest.param(200, []),
        pytest.param(
            400,
            None,
            marks=pytest.mark.config(
                EATS_PARTNERS_SETTINGS={
                    'last_activity_sync_delay_ms': 600000,
                    'last_activity_yt_sync_delay_min': 10,
                    'last_activity_yt_path': (
                        '//home/eda/restapp/testing'
                        '/eats-partners/last_activity'
                    ),
                    'find_by_emails': True,
                    'return_error_empty_search': True,
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'limit,with_blocked',
    [(1, True), (2, True), (3, True), (5, True), (10, True), (15, True)],
)
async def test_internal_partners_empty_search(
        taxi_eats_partners,
        code,
        expected,
        limit,
        with_blocked,
        mock_personal_bulk_retrieve,
):
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?'
        'limit={}&cursor={}&with_blocked={}'.format(limit, 0, with_blocked),
        json={},
    )
    assert response.status_code == code
    if expected:
        assert response.json()['payload'] == expected


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'search_data',
    [
        (
            {
                'id': 2,
                'email': 'partner2@partner.com',
                'is_fast_food': True,
                'places': [201],
                'first_login_range': {
                    'from': '2019-07-19T11:00:00+00:00',
                    'to': '2019-07-19T12:00:00+00:00',
                },
            }
        ),
        ({'id': 2}),
        ({'personal_email_id': '222'}),
        ({'email': 'partner2@partner.com'}),
        ({'email': 'PARTNER2@PARTNER.COM'}),
        ({'places': [201]}),
        (
            {
                'first_login_range': {
                    'from': '2019-07-19T11:00:00+00:00',
                    'to': '2019-07-19T12:00:00+00:00',
                },
            }
        ),
    ],
)
async def test_internal_partners_2_search(
        taxi_eats_partners,
        search_data,
        mockserver,
        mock_personal_bulk_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'partners': [
                    {'partner_id': 2, 'login': 'partner2@partner.com'},
                ],
            },
        )

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?limit=10&with_blocked=true',
        json=search_data,
    )
    assert response.status_code == 200
    assert response.json()['meta'] == {
        'cursor': 2,
        'can_fetch_next': False,
        'count': 1,
    }
    assert response.json()['payload'] == [PARTNERS[2]]


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
async def test_internal_partners_diff_places_search(
        taxi_eats_partners, mock_personal_bulk_retrieve,
):
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?limit=10&cursor=0&with_blocked=true',
        json={'places': [301, 401, 501]},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        PARTNERS[5],
        PARTNERS[4],
        PARTNERS[3],
    ]
    assert response.json()['meta'] == {
        'can_fetch_next': False,
        'cursor': 3,
        'count': 3,
    }


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
async def test_internal_partner_all_fast_food_search(
        taxi_eats_partners, mock_personal_bulk_retrieve,
):
    limit = 4
    can_fetch_next = True
    cursor = 0

    while can_fetch_next:
        response = await taxi_eats_partners.post(
            '/internal/partners/v1/search?'
            'limit={}&cursor={}&with_blocked=true'.format(limit, cursor),
            json={
                'is_fast_food': True,
                'places': [101, 201, 301, 401, 501, 601, 701, 801, 901, 1001],
            },
        )

        assert response.status_code == 200
        meta = response.json()['meta']
        can_fetch_next = meta['can_fetch_next']
        cursor = meta['cursor']
        if can_fetch_next:
            assert response.json()['payload'] == [
                PARTNERS[9],
                PARTNERS[8],
                PARTNERS[4],
                PARTNERS[3],
            ]
            assert cursor == 3
        else:
            assert response.json()['payload'] == [PARTNERS[2]]
            assert cursor == 2


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'search_params,name',
    [
        (
            {
                'first_login_range': {
                    'from': '2018-07-19T11:00:00+00:00',
                    'to': '2021-07-19T12:00:00+00:00',
                },
            },
            'all',
        ),
        ({'first_login_range': {'from': '2018-07-19T11:00:00+00:00'}}, 'all'),
        ({'first_login_range': {'to': '2021-07-19T12:00:00+00:00'}}, 'all'),
        ({'first_login_range': {'from': '2022-07-19T11:00:00+00:00'}}, 'null'),
        ({'first_login_range': {'to': '2018-07-19T11:00:00+00:00'}}, 'null'),
    ],
)
async def test_internal_partners_range_search(
        taxi_eats_partners, search_params, name, mock_personal_bulk_retrieve,
):

    can_fetch_next = True
    limit = 5
    cursor = 0
    while can_fetch_next:
        response = await taxi_eats_partners.post(
            '/internal/partners/v1/search?'
            'limit={}&cursor={}&with_blocked=true'.format(limit, cursor),
            json=search_params,
        )

        assert response.status_code == 200
        meta = response.json()['meta']
        can_fetch_next = meta['can_fetch_next']
        payload = []
        count = len(response.json()['payload'])
        for i in range(int(1), int(count + 1)):
            payload.append(PARTNERS[(cursor or (len(PARTNERS) + 1)) - i])
        assert response.json()['payload'] == payload
        assert can_fetch_next is bool(limit <= count)
        cursor = meta['cursor']


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'with_blocked,cursor,limit,expected_partners',
    [
        (True, 0, 10, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        (False, 0, 10, [10, 9, 7, 6, 4, 3, 1]),
        (True, 6, 10, [5, 4, 3, 2, 1]),
        (False, 6, 10, [4, 3, 1]),
        (False, 0, 3, [10, 9, 7]),
        (False, 9, 2, [7, 6]),
        (True, 9, 2, [8, 7]),
    ],
)
async def test_internal_partners_with_blocked_search(
        taxi_eats_partners,
        with_blocked,
        cursor,
        limit,
        expected_partners,
        mock_personal_bulk_retrieve,
):
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?'
        'limit={}&cursor={}&with_blocked={}'.format(
            limit, cursor, with_blocked,
        ),
        json={'places': [101, 201, 301, 401, 501, 601, 701, 801, 901, 1001]},
    )

    assert response.status_code == 200
    payload = []
    for index in expected_partners:
        payload.append(PARTNERS[index])
    assert response.json()['payload'] == payload


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'offset, limit, expected_partners, count',
    [
        (0, 3, [PARTNERS[10], PARTNERS[9], PARTNERS[8]], 100000),
        (2, 1, [PARTNERS[8]], 100000),
        (9, 3, [PARTNERS[1]], 1),
    ],
)
async def test_offset_pagination(
        taxi_eats_partners,
        offset,
        limit,
        expected_partners,
        count,
        mock_personal_bulk_retrieve,
):
    search_params = {'first_login_range': {'to': '2025-01-01T12:00:00+00:00'}}
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?'
        'limit={}&offset={}&with_blocked=true'.format(limit, offset),
        json=search_params,
    )

    assert response.status_code == 200
    meta = response.json()['meta']
    assert meta['count'] == count
    payload = response.json()['payload']
    assert payload == expected_partners


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'with_blocked,cursor,limit,expected_partners',
    [
        (True, 0, 10, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        (False, 0, 10, [10, 9, 7, 6, 4, 3, 1]),
        (True, 6, 10, [5, 4, 3, 2, 1]),
        (False, 6, 10, [4, 3, 1]),
        (False, 0, 3, [10, 9, 7]),
        (False, 9, 2, [7, 6]),
        (True, 9, 2, [8, 7]),
    ],
)
async def test_internal_partners_search_with_personal(
        taxi_eats_partners,
        with_blocked,
        cursor,
        limit,
        expected_partners,
        mock_personal_bulk_retrieve,
):
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?'
        'limit={}&cursor={}&with_blocked={}'.format(
            limit, cursor, with_blocked,
        ),
        json={'places': [101, 201, 301, 401, 501, 601, 701, 801, 901, 1001]},
    )

    assert response.status_code == 200
    payload = []
    for index in expected_partners:
        payload.append(PARTNERS[index])
    assert response.json()['payload'] == payload


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'search_data, expected, authorizer_response',
    [
        pytest.param(
            {'email': 'partner2@partner.com'},
            [PARTNERS[2]],
            {'partners': [{'partner_id': 2, 'login': 'partner2@partner.com'}]},
        ),
        pytest.param(
            {'email': 'PARTNER2@partner.com'},
            [PARTNERS[2]],
            {'partners': [{'partner_id': 2, 'login': 'partner2@partner.com'}]},
        ),
        pytest.param(
            {'email': 'PARTNER2@partner.com'},
            [PARTNERS[2]],
            {'partners': [{'partner_id': 2, 'login': 'partner2@partner.com'}]},
        ),
        pytest.param(
            {'id': 2, 'email': 'PARTNER2@partner.com'},
            [PARTNERS[2]],
            {'partners': [{'partner_id': 2, 'login': 'partner2@partner.com'}]},
        ),
        pytest.param(
            {'id': 3, 'email': 'partner2@partner.com'},
            [],
            {'partners': [{'partner_id': 2, 'login': 'partner2@partner.com'}]},
        ),
        pytest.param(
            {'id': 2, 'email': 'partner2@partner.com'}, [], {'partners': []},
        ),
        pytest.param({'email': 'barabulka@email.com'}, [], {'partners': []}),
    ],
)
async def test_search_with_authorizer(
        taxi_eats_partners,
        search_data,
        expected,
        authorizer_response,
        mockserver,
        mock_personal_bulk_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_authorizer(request):
        return mockserver.make_response(status=200, json=authorizer_response)

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/search?limit=10&with_blocked=true',
        json=search_data,
    )
    assert response.status_code == 200
    assert response.json()['payload'] == expected
