import pytest

ENDPOINT = 'fleet/users/v1/users/list'


def build_headers():
    return {
        'X-Park-ID': 'park_id1',
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '000',
    }


def build_request(
        is_enabled=None, search=None, cursor=None, limit=None, sort_by=None,
):
    return {
        'query': {'is_enabled': is_enabled, 'search': search},
        'cursor': cursor,
        'limit': limit,
        'sort_by': sort_by,
    }


@pytest.fixture(name='_dac_parks_users_list')
def _mock_dac_parks_users_list(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock(request):
        assert request.json['query']['park'] == {'id': 'park_id1'}
        return {
            'offset': 0,
            'users': [
                {
                    'id': 'user_dac_id1',
                    'park_id': 'park_id1',
                    'display_name': 'CUser Dac 1',
                    'email': 'user_dac_id1@yandex.ru',
                    'phone': '+71233213232',
                    'group_id': 'admin',
                    'group_name': 'Administrators',
                    'is_enabled': False,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                    'created_at': '2019-01-01T01:00:00+00:00',
                },
            ],
        }


LOCAL_USERS = [
    {
        'created_at': '2021-01-01T00:00:00+00:00',
        'name': 'AUser Name',
        'group_id': 'admin',
        'group_name': 'Administrators',
        'is_confirmed': False,
        'is_enabled': True,
        'is_multifactor_authentication_required': False,
        'phone': '+71231231212',
        'user_id': 'user_id1',
    },
    {
        'created_at': '2021-01-01T00:00:00+00:00',
        'name': 'BUser Super',
        'group_id': 'super',
        'group_name': 'Superusers',
        'is_confirmed': False,
        'is_enabled': True,
        'is_multifactor_authentication_required': False,
        'phone': '+74564564545',
        'user_id': 'user_id2',
    },
]

DAC_USERS = [
    {
        'user_id': 'user_dac_id1',
        'name': 'CUser Dac 1',
        'email': 'user_dac_id1@yandex.ru',
        'phone': '+71233213232',
        'group_id': 'admin',
        'group_name': 'Administrators',
        'is_enabled': False,
        'is_confirmed': True,
        'is_multifactor_authentication_required': True,
        'created_at': '2019-01-01T01:00:00+00:00',
    },
]


@pytest.mark.parametrize(
    'sort_by, response_users',
    [
        (None, [LOCAL_USERS[0], LOCAL_USERS[1], DAC_USERS[0]]),
        (
            [{'field': 'name', 'order': 'desc'}],
            [DAC_USERS[0], LOCAL_USERS[1], LOCAL_USERS[0]],
        ),
        (
            [{'field': 'group_name', 'order': 'asc'}],
            [LOCAL_USERS[0], DAC_USERS[0], LOCAL_USERS[1]],
        ),
        (
            [
                {'field': 'group_name', 'order': 'asc'},
                {'field': 'name', 'order': 'desc'},
            ],
            [DAC_USERS[0], LOCAL_USERS[0], LOCAL_USERS[1]],
        ),
        (
            [
                {'field': 'group_name', 'order': 'asc'},
                {'field': 'group_name', 'order': 'asc'},
            ],
            [LOCAL_USERS[0], DAC_USERS[0], LOCAL_USERS[1]],
        ),
        (
            [
                {'field': 'group_name', 'order': 'asc'},
                {'field': 'group_name', 'order': 'desc'},
            ],
            [LOCAL_USERS[0], DAC_USERS[0], LOCAL_USERS[1]],
        ),
    ],
)
async def test_sort(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        _dac_parks_users_list,
        sort_by,
        response_users,
):
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=build_request(sort_by=sort_by),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['users'] == response_users


@pytest.mark.parametrize(
    'is_enabled, response_users',
    [(True, LOCAL_USERS), (False, [DAC_USERS[0]])],
)
async def test_filter_is_enabled(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        _dac_parks_users_list,
        is_enabled,
        response_users,
):
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(is_enabled=is_enabled),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['users'] == response_users


@pytest.mark.parametrize(
    'search, response_users',
    [
        ('namE', [LOCAL_USERS[0]]),
        ('dac', [DAC_USERS[0]]),
        ('@yandex', [DAC_USERS[0]]),
        ('123', [LOCAL_USERS[0], DAC_USERS[0]]),
    ],
)
async def test_filter_search(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        _dac_parks_users_list,
        search,
        response_users,
):
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=build_request(search=search),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['users'] == response_users


async def test_cursor(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        mockserver,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock(request):
        assert request.json['query'] == {'park': {'id': 'park_id1'}}
        response_users = [
            {
                'id': 'user_dac_id1',
                'park_id': 'park_id1',
                'display_name': 'CUser Dac 1',
                'email': 'user_dac_id1@yandex.ru',
                'phone': '+71233213232',
                'group_id': 'admin',
                'group_name': 'Administrators',
                'is_enabled': False,
                'is_confirmed': True,
                'is_superuser': False,
                'is_multifactor_authentication_required': True,
                'is_usage_consent_accepted': False,
                'created_at': '2019-01-01T01:00:00+00:00',
            },
        ]
        if 'limit' in request.json and request.json['limit'] == 1:
            return {'offset': 0, 'users': response_users}
        response_users.append(
            {
                'id': 'user_dac_id2',
                'park_id': 'park_id1',
                'display_name': 'DUser Dac 2',
                'email': 'user_dac_id2@yandex.ru',
                'phone': '+76546546565',
                'group_id': 'admin',
                'group_name': 'Administrators',
                'is_enabled': False,
                'is_confirmed': False,
                'is_superuser': False,
                'is_multifactor_authentication_required': True,
                'is_usage_consent_accepted': False,
                'created_at': '2019-01-01T01:00:00+00:00',
            },
        )
        return {'offset': 0, 'users': response_users}

    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=build_request(limit=1),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == [LOCAL_USERS[0]]

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=1, cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == [LOCAL_USERS[1]]

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=1, cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == [DAC_USERS[0]]

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=1, cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == [
        {
            'user_id': 'user_dac_id2',
            'name': 'DUser Dac 2',
            'email': 'user_dac_id2@yandex.ru',
            'phone': '+76546546565',
            'group_id': 'admin',
            'group_name': 'Administrators',
            'is_enabled': False,
            'is_confirmed': True,
            'is_multifactor_authentication_required': True,
            'created_at': '2019-01-01T01:00:00+00:00',
        },
    ]

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=1, cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()


@pytest.mark.parametrize(
    'sort_by, response_users_first, response_users_second',
    [
        (None, [LOCAL_USERS[0], LOCAL_USERS[1]], [DAC_USERS[0]]),
        (
            [{'field': 'name', 'order': 'desc'}],
            [DAC_USERS[0], LOCAL_USERS[1]],
            [LOCAL_USERS[0]],
        ),
        (
            [{'field': 'group_name', 'order': 'asc'}],
            [LOCAL_USERS[0], DAC_USERS[0]],
            [LOCAL_USERS[1]],
        ),
        (
            [
                {'field': 'group_name', 'order': 'asc'},
                {'field': 'name', 'order': 'asc'},
            ],
            [LOCAL_USERS[0], DAC_USERS[0]],
            [LOCAL_USERS[1]],
        ),
    ],
)
async def test_sort_cursor(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        _dac_parks_users_list,
        sort_by,
        response_users_first,
        response_users_second,
):
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=2, sort_by=sort_by),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == response_users_first

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=2, cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['users'] == response_users_second


@pytest.mark.parametrize(
    'is_enabled, response_users_first, response_users_second',
    [(True, [LOCAL_USERS[0]], [LOCAL_USERS[1]])],
)
async def test_filter_is_enabled_cursor(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        _dac_parks_users_list,
        is_enabled,
        response_users_first,
        response_users_second,
):
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=1, is_enabled=is_enabled),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == response_users_first

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['users'] == response_users_second


@pytest.mark.parametrize(
    'search, response_users', [('namE', [LOCAL_USERS[0]])],
)
async def test_filter_search_cursor(
        taxi_fleet_users,
        personal_phones_retrieve,
        dac_parks_group_list,
        _dac_parks_users_list,
        search,
        response_users,
):
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(limit=1, search=search),
    )

    assert response.status_code == 200
    assert response.json()['cursor']
    assert response.json()['users'] == response_users

    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_request(cursor=response.json()['cursor']),
    )

    assert response.status_code == 200
    assert 'cursor' not in response.json()
    assert response.json()['users'] == []
