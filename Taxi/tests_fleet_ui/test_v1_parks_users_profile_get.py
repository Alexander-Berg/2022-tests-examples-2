import pytest

from tests_fleet_ui import utils

ENDPOINT = '/fleet/ui/v1/parks/users/profile'

BRAND_PARAMS = [
    (
        'park_yandex',
        {
            'icon': 'yandex_icon',
            'logo': 'yandex_logo',
            'name_key': 'yandex',
            'name': 'yandex_ru_translate',
        },
    ),
    (
        'park_uber',
        {
            'icon': 'uber_icon',
            'logo': 'uber_logo',
            'name_key': 'uber',
            'name': 'uber_ru_translate',
        },
    ),
    (
        'park_aze',
        {
            'icon': 'yandex_aze_icon',
            'logo': 'yandex_aze_logo',
            'name_key': 'yandex_aze',
            'name': 'yandex_aze_ru_translate',
        },
    ),
    (
        'park_usa',
        {
            'icon': 'default_icon',
            'logo': 'default_logo',
            'name_key': 'default_name',
            'name': 'default_name_ru_translate',
        },
    ),
]


@pytest.mark.config(
    FLEET_UI_BRANDS={
        'default': {
            'icon': 'default_icon',
            'logo': 'default_logo',
            'tanker_key': 'default_name',
        },
        'brands': [
            {
                'tanker_key': 'yandex',
                'icon': 'yandex_icon',
                'logo': 'yandex_logo',
                'countries': ['rus', 'ukr'],
            },
            {
                'tanker_key': 'uber',
                'icon': 'uber_icon',
                'logo': 'uber_logo',
                'countries': ['rus'],
                'park_types': ['uberdriver'],
            },
            {
                'tanker_key': 'yandex_aze',
                'icon': 'yandex_aze_icon',
                'logo': 'yandex_aze_logo',
                'countries': ['aze'],
            },
        ],
    },
)
@pytest.mark.parametrize('park_id, expected_brand', BRAND_PARAMS)
async def test_brands(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        park_id,
        expected_brand,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id=park_id),
    )

    assert response.status_code == 200, response.text
    assert response.json()['brand'] == expected_brand


TEST_PARK_PARAMS = [
    (
        'yandex',
        None,
        {
            'city': {'id': 'New York', 'name': ''},
            'country': {'id': 'usa', 'name': 'США'},
            'currency': '',
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
            'id': 'park_usa',
            'locale': '',
            'name': 'Yellow Cabs',
            'timezone_offset': 0,
        },
    ),
    (
        'yandex',
        'park_yandex',
        {
            'city': {'id': 'Москва', 'name': ''},
            'country': {'id': 'rus', 'name': 'Россия'},
            'currency': 'RUB',
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
            'id': 'park_yandex',
            'locale': '',
            'name': 'Яндекс Парк',
            'timezone_offset': 0,
        },
    ),
    (
        'yandex_team',
        'park_inactive',
        {
            'city': {'id': 'Москва', 'name': ''},
            'country': {'id': 'rus', 'name': 'Россия'},
            'currency': 'RUB',
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
            'id': 'park_inactive',
            'locale': '',
            'name': 'Неактивный парк',
            'timezone_offset': 0,
        },
    ),
]


@pytest.mark.parametrize('provider, park_id, expected_park', TEST_PARK_PARAMS)
async def test_park(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        provider,
        park_id,
        expected_park,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    response = await taxi_fleet_ui.get(
        ENDPOINT,
        headers=utils.build_headers(provider=provider, park_id=park_id),
    )

    assert response.status_code == 200, response.text
    assert response.json()['park'] == expected_park


USERNAME_PARAMS = [('yandex', 'user'), ('yandex_team', 'Tech support')]


@pytest.mark.parametrize('provider, expected_username', USERNAME_PARAMS)
async def test_username(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        provider,
        expected_username,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    response = await taxi_fleet_ui.get(
        ENDPOINT,
        headers=utils.build_headers(provider=provider, park_id='park_yandex'),
    )

    assert response.status_code == 200, response.text
    assert response.json()['user']['name'] == expected_username


PERSONAL = {'74564564545': '456'}


@pytest.fixture(name='personal_phones_store')
def _mock_personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock(request):
        assert request.json['value'] in PERSONAL
        return {
            'id': PERSONAL[request.json['value']],
            'value': request.json['value'],
        }

    return _mock


@pytest.fixture(name='fleet_users_mock')
def _mock_fleet_users(mockserver):
    @mockserver.json_handler('/fleet-users/v1/users/parks/list')
    def _fleet_users_mock(request):
        return {'park_ids': ['parks_no_confirmed']}

    return _fleet_users_mock


@pytest.fixture(name='local_blackbox')
def _mock_blackbox(mockserver):
    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        assert request.query['phone_attributes'] == '102,108'
        return {
            'users': [
                {
                    'uid': {'value': utils.UID},
                    'login': utils.EMAIL,
                    'phones': [
                        {
                            'id': '45588690',
                            'attributes': {'102': '71231231212', '108': '0'},
                        },
                        {
                            'id': '45588691',
                            'attributes': {'102': '74564564545', '108': '1'},
                        },
                    ],
                    'aliases': {'21': 'neophonish'},
                },
            ],
        }


async def test_no_username(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mockserver,
        personal_phones_store,
        fleet_users_mock,
        local_blackbox,
):
    dispatcher_access_control.set_users([])

    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id=None),
    )

    assert response.status_code == 200, response.text
    assert response.json()['user']['name'] == ''


LOGIN_PARAMS = [('ticket1', 'user1@yandex.ru'), ('ticket2', 'user2@yandex.ru')]


@pytest.mark.parametrize('user_ticket, expected_login', LOGIN_PARAMS)
async def test_login(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        user_ticket,
        expected_login,
):
    blackbox_service.set_user_ticket_info(
        user_ticket='ticket1', uid='100', login='user1@yandex.ru',
    )
    blackbox_service.set_user_ticket_info(
        user_ticket='ticket2', uid='100', login='user2@yandex.ru',
    )
    response = await taxi_fleet_ui.get(
        ENDPOINT,
        headers=utils.build_headers(
            user_ticket=user_ticket, park_id='park_yandex',
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()['user']['login'] == expected_login


@pytest.mark.parametrize(
    'permissions, secured_phone, neophonish, park_id',
    [
        (
            [],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            '',
            'park_yandex',
        ),
        (
            ['p1'],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            '',
            'park_yandex',
        ),
        (
            ['p1', 'p2'],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            '',
            'park_yandex',
        ),
        (
            [],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            'neophonish',
            'park_yandex',
        ),
        (
            ['p1'],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            'neophonish',
            'park_yandex',
        ),
        (
            ['p1', 'p2'],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            'neophonish',
            'park_yandex',
        ),
        (
            [],
            {
                'id': '45588691',
                'attributes': {'102': '74564564545', '108': '1'},
            },
            'neophonish',
            None,
        ),
    ],
)
async def test_permissions(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        permissions,
        secured_phone,
        neophonish,
        park_id,
        mockserver,
        personal_phones_store,
        fleet_users_mock,
):
    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        return {
            'users': [
                {
                    'uid': {'value': utils.UID},
                    'login': utils.EMAIL,
                    'phones': [
                        {
                            'id': '45588690',
                            'attributes': {'102': '71231231212', '108': '0'},
                        },
                        secured_phone,
                    ],
                    'aliases': {'21': neophonish},
                },
            ],
        }

    dispatcher_access_control.set_permissions(permissions)

    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id=park_id),
    )

    assert response.status_code == 200, response.text
    assert response.json()['user']['permissions'] == permissions


PARKS_PARAMS = [
    (
        ['park_yandex'],
        [],
        [{'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'}],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        '',
        'portal',
    ),
    (
        ['park_yandex', 'park_uber', 'park_small_name'],
        [],
        [
            {
                'city': 'Москва',
                'id': 'park_small_name',
                'name': 'парк с маленькой буквы',
            },
            {'city': 'Казань', 'id': 'park_uber', 'name': 'Убер Парк'},
            {'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'},
        ],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        '',
        'portal',
    ),
    (
        ['park_yandex'],
        [],
        [{'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'}],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        'neophonish',
        '',
    ),
    (
        ['park_yandex'],
        ['park_no_confirmed'],
        [{'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'}],
        {'id': '45588691', 'attributes': {'102': '74564564545'}},
        'neophonish',
        '',
    ),
    (
        ['park_yandex'],
        ['park_no_confirmed'],
        [
            {'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'},
            {'city': 'Уфа', 'id': 'park_no_confirmed', 'name': 'Яндекс Парк'},
        ],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        'neophonish',
        '',
    ),
    (
        ['park_yandex'],
        ['park_no_confirmed'],
        [{'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'}],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        'neophonish',
        'portal',
    ),
    (
        [],
        ['park_no_confirmed'],
        [{'city': 'Уфа', 'id': 'park_no_confirmed', 'name': 'Яндекс Парк'}],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        'neophonish',
        '',
    ),
    (
        ['park_yandex', 'park_uber', 'park_small_name'],
        ['park_no_confirmed', 'park_no_confirmed_onemore'],
        [
            {
                'city': 'Москва',
                'id': 'park_small_name',
                'name': 'парк с маленькой буквы',
            },
            {'city': 'Казань', 'id': 'park_uber', 'name': 'Убер Парк'},
            {'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'},
            {
                'city': 'Саратов',
                'id': 'park_no_confirmed_onemore',
                'name': 'Яндекс Парк',
            },
            {'city': 'Уфа', 'id': 'park_no_confirmed', 'name': 'Яндекс Парк'},
        ],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        'neophonish',
        '',
    ),
    (
        ['park_yandex', 'park_uber', 'park_small_name'],
        ['park_no_confirmed', 'park_no_confirmed_onemore', 'park_uber'],
        [
            {
                'city': 'Москва',
                'id': 'park_small_name',
                'name': 'парк с маленькой буквы',
            },
            {'city': 'Казань', 'id': 'park_uber', 'name': 'Убер Парк'},
            {'city': 'Москва', 'id': 'park_yandex', 'name': 'Яндекс Парк'},
            {
                'city': 'Саратов',
                'id': 'park_no_confirmed_onemore',
                'name': 'Яндекс Парк',
            },
            {'city': 'Уфа', 'id': 'park_no_confirmed', 'name': 'Яндекс Парк'},
        ],
        {'id': '45588691', 'attributes': {'102': '74564564545', '108': '1'}},
        'neophonish',
        '',
    ),
]


@pytest.mark.parametrize(
    """parks_list, parks_list_no_confirmed,
    response_parks, secured_phone, neophonish, portal""",
    PARKS_PARAMS,
)
async def test_parks(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        parks_list,
        parks_list_no_confirmed,
        response_parks,
        neophonish,
        portal,
        secured_phone,
        mockserver,
        personal_phones_store,
):
    @mockserver.json_handler('/fleet-users/v1/users/parks/list')
    def _fleet_users_mock(request):
        return {'park_ids': parks_list_no_confirmed}

    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        return {
            'users': [
                {
                    'uid': {'value': utils.UID},
                    'login': utils.EMAIL,
                    'phones': [
                        {
                            'id': '45588690',
                            'attributes': {'102': '71231231212', '108': '0'},
                        },
                        secured_phone,
                    ],
                    'aliases': {'21': neophonish, '1': portal},
                },
            ],
        }

    dispatcher_access_control.set_parks(parks_list)

    response = await taxi_fleet_ui.get(ENDPOINT, headers=utils.build_headers())

    assert response.status_code == 200, response.text
    assert response.json()['user']['parks'] == response_parks


LANGUAGE_PARAMS = [
    (
        [{'id': 'ru', 'tanker_key': 'russian'}],
        [{'id': 'ru', 'name_key': 'russian'}],
    ),
    (
        [
            {'id': 'ru', 'tanker_key': 'russian'},
            {'id': 'en', 'tanker_key': 'english'},
        ],
        [
            {'id': 'ru', 'name_key': 'russian'},
            {'id': 'en', 'name_key': 'english'},
        ],
    ),
]


@pytest.mark.parametrize(
    'config_languages, expected_languages', LANGUAGE_PARAMS,
)
async def test_languages(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        taxi_config,
        config_languages,
        expected_languages,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    taxi_config.set(FLEET_UI_LANGUAGES=config_languages)

    response = await taxi_fleet_ui.get(ENDPOINT, headers=utils.build_headers())

    assert response.status_code == 200, response.text
    assert response.json()['languages'] == expected_languages


PRIMARY_MENU_PARAMS = [
    (
        [],
        'en',
        [
            {
                'title_key': 'staff',
                'icon': 'staff_icon_url',
                'items': [
                    {
                        'title_key': 'drivers',
                        'items': [
                            {
                                'title_key': 'drivers',
                                'target': 'new_tab',
                                'url': {
                                    'host': 'https://fleet.taxi.yandex.ru',
                                    'path': (
                                        '/drivers?park_id=park_usa&lang=en'
                                    ),
                                },
                            },
                        ],
                    },
                ],
            },
        ],
    ),
    (
        ['permission1'],
        None,
        [
            {
                'title_key': 'staff',
                'icon': 'staff_icon_url',
                'items': [
                    {
                        'title_key': 'drivers',
                        'items': [
                            {
                                'title_key': 'drivers',
                                'target': 'new_tab',
                                'url': {
                                    'host': 'https://fleet.taxi.yandex.ru',
                                    'path': (
                                        '/drivers?park_id=park_usa&lang=en-us'
                                    ),
                                },
                            },
                        ],
                    },
                    {
                        'title_key': 'segments',
                        'items': [
                            {
                                'title_key': 'segments',
                                'target': 'new_tab',
                                'url': {
                                    'host': 'https://fleet.taxi.yandex.ru',
                                    'path': (
                                        '/segments?country_id=usa'
                                        '&park_id=park_usa'
                                    ),
                                },
                                'permission': 'permission1',
                            },
                        ],
                    },
                ],
            },
        ],
    ),
]


@pytest.mark.config(
    FLEET_UI_MENU_ITEMS_PRIMARY=[
        {
            'title_key': 'staff',
            'icon': 'staff_icon_url',
            'items': [
                {
                    'title_key': 'drivers',
                    'items': [
                        {
                            'title_key': 'drivers',
                            'target': 'new_tab',
                            'url': {
                                'host': 'fleet_yandex',
                                'path': (
                                    '/drivers?park_id={park_id}&lang={lang}'
                                ),
                            },
                        },
                    ],
                },
                {
                    'title_key': 'segments',
                    'items': [
                        {
                            'title_key': 'segments',
                            'target': 'new_tab',
                            'url': {
                                'host': 'fleet_yandex',
                                'path': (
                                    '/segments?country_id={country_id}'
                                    '&park_id={park_id}'
                                ),
                            },
                            'permission': 'permission1',
                        },
                    ],
                },
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'permissions, accept_language, expected_menu', PRIMARY_MENU_PARAMS,
)
async def test_menu_primary(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        permissions,
        accept_language,
        expected_menu,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    dispatcher_access_control.set_permissions(permissions)

    response = await taxi_fleet_ui.get(
        ENDPOINT,
        headers=utils.build_headers(
            accept_language=accept_language, park_id='park_usa',
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()['menu']['primary'] == expected_menu


SECONDARY_MENU_PARAMS = [
    (
        [],
        [
            {
                'title_key': 'staff',
                'icon': 'staff_icon_url',
                'items': [
                    {
                        'title_key': 'drivers',
                        'items': [{'title_key': 'drivers', 'id': 'item_id'}],
                    },
                ],
            },
        ],
    ),
    (
        ['permission1'],
        [
            {
                'title_key': 'staff',
                'icon': 'staff_icon_url',
                'items': [
                    {
                        'title_key': 'drivers',
                        'items': [{'title_key': 'drivers', 'id': 'item_id'}],
                    },
                    {
                        'title_key': 'segments',
                        'items': [
                            {
                                'title_key': 'segments',
                                'id': 'item_id',
                                'permission': 'permission1',
                            },
                        ],
                    },
                ],
            },
        ],
    ),
]


@pytest.mark.config(
    FLEET_UI_MENU_ITEMS_SECONDARY=[
        {
            'title_key': 'staff',
            'icon': 'staff_icon_url',
            'items': [
                {
                    'title_key': 'drivers',
                    'items': [{'title_key': 'drivers', 'id': 'item_id'}],
                },
                {
                    'title_key': 'segments',
                    'items': [
                        {
                            'title_key': 'segments',
                            'id': 'item_id',
                            'permission': 'permission1',
                        },
                    ],
                },
            ],
        },
    ],
)
@pytest.mark.parametrize('permissions, expected_menu', SECONDARY_MENU_PARAMS)
async def test_menu_secondary(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        permissions,
        expected_menu,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    dispatcher_access_control.set_permissions(permissions)

    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id='park_yandex'),
    )

    assert response.status_code == 200, response.text
    assert response.json()['menu']['secondary'] == expected_menu


SETTINGS_MENU_PARAMS = [
    (
        [],
        {
            'icon': 'staff_icon_url',
            'items': [
                {
                    'title_key': 'drivers',
                    'items': [{'title_key': 'drivers', 'id': 'item_id'}],
                },
            ],
        },
    ),
    (
        ['permission1'],
        {
            'icon': 'staff_icon_url',
            'items': [
                {
                    'title_key': 'drivers',
                    'items': [{'title_key': 'drivers', 'id': 'item_id'}],
                },
                {
                    'title_key': 'segments',
                    'items': [
                        {
                            'title_key': 'segments',
                            'target': 'new_tab',
                            'url': {
                                'host': 'https://fleet.taxi.yandex.ru',
                                'path': (
                                    '/segments?'
                                    'country_id=usa&park_id=park_usa'
                                ),
                            },
                            'permission': 'permission1',
                        },
                    ],
                },
            ],
        },
    ),
]


@pytest.mark.config(
    FLEET_UI_MENU_ITEMS_SETTINGS={
        'icon': 'staff_icon_url',
        'items': [
            {
                'title_key': 'drivers',
                'items': [{'title_key': 'drivers', 'id': 'item_id'}],
            },
            {
                'title_key': 'segments',
                'items': [
                    {
                        'title_key': 'segments',
                        'target': 'new_tab',
                        'url': {
                            'host': 'fleet_yandex',
                            'path': (
                                '/segments?country_id={country_id}'
                                '&park_id={park_id}'
                            ),
                        },
                        'permission': 'permission1',
                    },
                ],
            },
        ],
    },
)
@pytest.mark.parametrize('permissions, expected_menu', SETTINGS_MENU_PARAMS)
async def test_menu_settings(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
        permissions,
        expected_menu,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    dispatcher_access_control.set_permissions(permissions)

    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id='park_usa'),
    )

    assert response.status_code == 200, response.text
    assert response.json()['menu']['settings'] == expected_menu


async def test_park_not_found(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id='invalid'),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': 'forbidden_park_id',
        'message': 'Forbidden park_id',
    }


async def test_park_id_yandex_team(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(provider='yandex_team'),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': 'park_id_must_be_provided',
        'message': 'Park id must be set for yandex_team user',
    }


async def test_empty_parks_list(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    dispatcher_access_control.set_parks([])

    response = await taxi_fleet_ui.get(ENDPOINT, headers=utils.build_headers())

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': 'empty_parks_list',
        'message': 'Empty parks list',
    }


async def test_no_such_user(
        taxi_fleet_ui,
        mock_fleet_parks_list,
        dispatcher_access_control,
        blackbox_service,
):
    blackbox_service.set_user_ticket_info(
        user_ticket=utils.USER_TICKET, uid=utils.UID, login=utils.EMAIL,
    )
    dispatcher_access_control.set_users([])

    response = await taxi_fleet_ui.get(
        ENDPOINT, headers=utils.build_headers(park_id='park_yandex'),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': 'forbidden_park_id',
        'message': 'No such user in park',
    }
