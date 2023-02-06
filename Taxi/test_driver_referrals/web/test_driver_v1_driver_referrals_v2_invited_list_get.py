import typing

import pytest

from test_driver_referrals import conftest

PARKS_DRIVER = {
    'd2': {
        'first_name': 'Аа',
        'id': 'd2',
        'last_name': 'А',
        'phones': ['+70007198936'],
    },
    'd3': {
        'first_name': 'Ба',
        'id': 'd3',
        'last_name': 'Б',
        'phones': ['+70007198936'],
    },
    'd5': {
        'first_name': 'Га',
        'id': 'd5',
        'last_name': 'Г',
        'phones': ['+70007198936'],
    },
    'd4': {
        'first_name': 'Ва',
        'id': 'd4',
        'last_name': 'В',
        'phones': ['+70007198936'],
    },
    'd6': {
        'first_name': 'Да',
        'id': 'd6',
        'last_name': 'Д',
        'phones': ['+70007198936'],
    },
    'd7': {
        'first_name': 'Ее',
        'id': 'd7',
        'last_name': 'Е',
        'phones': ['+70007198936'],
    },
    'd8': {
        'first_name': 'Жж',
        'id': 'd8',
        'last_name': 'Ж',
        'phones': ['+70007198936'],
    },
    'd9': {
        'first_name': 'Зз',
        'id': 'd9',
        'last_name': 'З',
        'phones': ['+70007198936'],
    },
    'd-nor': {
        'first_name': 'Ии',
        'id': 'd-nor',
        'last_name': 'И',
        'phones': ['+70007198936'],
    },
}
PARKS_DRIVER_ZERO_ORDER = {
    'd11': {
        'first_name': 'Кк',
        'id': 'd11',
        'last_name': 'к',
        'phones': ['+70007198936'],
    },
    'd12': {
        'first_name': 'Лл',
        'id': 'd12',
        'last_name': 'Л',
        'phones': ['+70007198936'],
    },
}
PARKS = {'p-nor': {'id': 'p-nor', 'locale': 'nor', 'country_id': 'nor'}}
DRIVER_REFERRALS_PROXY_URLS_COUNTRY = {
    '__default__': {'taxi': 'test/?{code}', 'eda': 'test/?{code}'},
}

# для параметризации конфига
def mark_config_use_data_countries(countries):
    return pytest.mark.config(
        DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=countries,
    )


@pytest.mark.parametrize(
    ('items_number', 'expected_invited_list'),
    [
        pytest.param(
            8,
            'expected_invited_list_1.json',
            marks=mark_config_use_data_countries(['rus']),
            id='1',
        ),
        pytest.param(
            9,
            'expected_invited_list_2.json',
            marks=mark_config_use_data_countries(['rus', 'nor']),
            id='2',
        ),
    ],
)
@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
    geoareas=conftest.TRANSLATIONS_GEOAREAS,
    tariff=conftest.TRANSLATIONS_TARIFF,
    notify=conftest.TRANSLATIONS_NOTIFY,
)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY=DRIVER_REFERRALS_PROXY_URLS_COUNTRY,
    DRIVER_REFERRALS_TARIFFS_BY_ORDERS_PROVIDER={
        'taxi': ['econom', 'business', 'comfortplus', 'vip'],
        'eda': ['eda'],
    },
    DRIVER_REFERRALS_VACANCIES=[
        {
            'vacancy_id': 1,
            'vacancy_name': 'driver',
            'orders_provider': 'taxi',
            'show_tariffs': True,
            'image_url': 'https://logo/taxi/',
            'tanker_key_for_invitation_text': (
                'invitation_text_for_taxi_drivers'
            ),
            'tanker_key_for_reminder_text': 'reminder_text_for_taxi_drivers',
        },
    ],
    DRIVER_REFERRALS_COMBINED_VACANCIES=[
        {
            'vacancy_id': 10,
            'vacancy_name': 'courier',
            'components': ['eda_courier', 'lavka_courier'],
            'image_url': 'https://logo/eda/',
            'tanker_key_for_invitation_text': 'invitation_text_for_couriers',
            'tanker_key_for_reminder_text': ('reminder_text_for_couriers',),
        },
    ],
)
@pytest.mark.pgsql('driver_referrals', files=['driver_with_invites.sql'])
@pytest.mark.now('2019-04-25 15:00:00')
async def test_driver_v1_driver_referrals_invited_list_get(
        web_app_client,
        mockserver,
        load_json,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
        mock_parks_driver_profiles_search,
        mock_fleet_parks_v1_parks_list,
        items_number,
        expected_invited_list,
):
    mock_parks_driver_profiles_search(PARKS_DRIVER, PARKS)
    mock_fleet_parks_v1_parks_list(PARKS)

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    async def _driver_photos(request):
        return mockserver.make_response(
            status=200,
            json={
                'actual_photo': {
                    'avatar_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                    'portrait_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                },
            },
        )

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {'name': 'moscow', 'time_zone': 'Moscow', 'country': 'ru'},
                ],
            },
        )

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/v2/invited/list',
        params={'status': 'all', 'limit': 10, 'offset': 0},
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p1',
            'X-YaTaxi-Driver-Profile-Id': 'd1',
        },
    )
    assert response.status == 200

    content = await response.json()
    assert len(content['items']) == items_number
    assert content == load_json(expected_invited_list)


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
    geoareas=conftest.TRANSLATIONS_GEOAREAS,
    tariff=conftest.TRANSLATIONS_TARIFF,
    notify=conftest.TRANSLATIONS_NOTIFY,
)
@pytest.mark.config(
    DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=['rus'],
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY=DRIVER_REFERRALS_PROXY_URLS_COUNTRY,
    DRIVER_REFERRALS_TARIFFS_BY_ORDERS_PROVIDER={
        'taxi': ['econom', 'business', 'comfortplus', 'vip'],
        'eda': ['eda'],
    },
    DRIVER_REFERRALS_VACANCIES=[
        {
            'vacancy_id': 1,
            'vacancy_name': 'courier',
            'orders_provider': 'eda',
            'show_tariffs': True,
            'image_url': 'https://logo/eda/',
            'tanker_key_for_invitation_text': 'invitation_text_for_couriers',
            'tanker_key_for_reminder_text': 'reminder_text_for_couriers',
        },
    ],
)
@pytest.mark.client_experiments3(
    consumer='driver-referrals/couriers_referral_version',
    experiment_name='couriers_referral_platform',
    args=[
        {'name': 'courier_id', 'type': 'int', 'value': 11},
        {'name': 'orders_provider', 'type': 'string', 'value': 'eda'},
        {
            'name': 'driver_tags',
            'type': 'set_string',
            'value': ['default_tag'],
        },
    ],
    value={'taximeter': True},
)
@pytest.mark.pgsql(
    'driver_referrals', files=['driver_with_invites_zero_order.sql'],
)
@pytest.mark.now('2021-12-17 15:00:00')
@pytest.mark.parametrize(
    ('driver_zones', 'expected_json_path'),
    [
        pytest.param(
            {},
            'expected_invited_list_zero_order_no_rule.json',
            id='no rule because nothing is allowed in default config',
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ZERO_ORDER_RULE={
                    '__default__': {
                        'allow_child_position_tariff_zone': False,
                        'allow_parent_position_tariff_zone': False,
                        'allow_no_tariff_zone': False,
                    },
                    'eda': {},
                },
            ),
        ),
        pytest.param(
            {'p11_d11': 'moscow', 'p12_d12': 'moscow'},
            'expected_invited_list_zero_order_rule2.json',
            id='rule 2 chosen with no zone',
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ZERO_ORDER_RULE={
                    '__default__': {
                        'allow_child_position_tariff_zone': False,
                        'allow_parent_position_tariff_zone': False,
                        'allow_no_tariff_zone': True,
                    },
                    'eda': {},
                },
            ),
        ),
        pytest.param(
            {'p11_d11': 'moscow', 'p12_d12': 'moscow'},
            'expected_invited_list_zero_order_rule2.json',
            id='rule 2 chosen with no zone through orders provider config',
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ZERO_ORDER_RULE={
                    '__default__': {
                        'allow_child_position_tariff_zone': False,
                        'allow_parent_position_tariff_zone': False,
                        'allow_no_tariff_zone': False,
                    },
                    'eda': {'allow_no_tariff_zone': True},
                },
            ),
        ),
        pytest.param(
            {'p11_d11': 'kaluga', 'p12_d12': 'moscow'},
            'expected_invited_list_zero_order_rule1.json',
            id='rule 1 chosen with moscow child zone',
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ZERO_ORDER_RULE={
                    '__default__': {
                        'allow_child_position_tariff_zone': True,
                        'allow_parent_position_tariff_zone': True,
                        'allow_no_tariff_zone': False,
                    },
                    'eda': {},
                },
            ),
        ),
        pytest.param(
            {'p11_d11': 'moscow'},
            'expected_invited_list_zero_order_rule1.json',
            id='rule 1 chosen with moscow parent zone (child no pos)',
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ZERO_ORDER_RULE={
                    '__default__': {
                        'allow_child_position_tariff_zone': True,
                        'allow_parent_position_tariff_zone': True,
                        'allow_no_tariff_zone': False,
                    },
                    'eda': {},
                },
            ),
        ),
        pytest.param(
            {'p11_d11': 'moscow', 'p12_d12': 'kaluga'},
            'expected_invited_list_zero_order_rule1.json',
            id='rule 1 chosen with moscow parent zone (child no config)',
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ZERO_ORDER_RULE={
                    '__default__': {
                        'allow_child_position_tariff_zone': False,
                        'allow_parent_position_tariff_zone': True,
                        'allow_no_tariff_zone': False,
                    },
                    'eda': {},
                },
            ),
        ),
    ],
)
async def test_driver_v1_driver_referrals_invited_list_get_with_zero_order(
        driver_zones: typing.Dict[str, str],
        expected_json_path: str,
        web_app_client,
        mockserver,
        load_json,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
        mock_parks_driver_profiles_search,
        mock_driver_profiles_drivers_profiles,
        mock_driver_zones,
):
    mock_parks_driver_profiles_search(PARKS_DRIVER_ZERO_ORDER)
    mock_driver_profiles_drivers_profiles(eats_keys={'d11': 11, 'd12': 12})
    mock_driver_zones(driver_zones)

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    async def _driver_photos(request):
        return mockserver.make_response(
            status=200,
            json={
                'actual_photo': {
                    'avatar_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                    'portrait_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                },
            },
        )

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {'name': 'moscow', 'time_zone': 'Moscow', 'country': 'ru'},
                    {'name': 'kaluga', 'time_zone': 'Moscow', 'country': 'ru'},
                ],
            },
        )

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/v2/invited/list',
        params={'status': 'all', 'limit': 10, 'offset': 0},
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p11',
            'X-YaTaxi-Driver-Profile-Id': 'd11',
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == load_json(expected_json_path)


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
    geoareas=conftest.TRANSLATIONS_GEOAREAS,
    tariff=conftest.TRANSLATIONS_TARIFF,
    notify=conftest.TRANSLATIONS_NOTIFY,
)
@pytest.mark.config(
    DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=['rus'],
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY=DRIVER_REFERRALS_PROXY_URLS_COUNTRY,
    DRIVER_REFERRALS_TARIFFS_BY_ORDERS_PROVIDER={
        'taxi': ['econom', 'business', 'comfortplus', 'vip'],
        'eda': ['eda'],
    },
    DRIVER_REFERRALS_VACANCIES=[
        {
            'vacancy_id': 1,
            'vacancy_name': 'driver',
            'orders_provider': 'taxi',
            'show_tariffs': True,
            'image_url': 'https://logo/taxi/',
            'tanker_key_for_invitation_text': (
                'invitation_text_for_taxi_drivers'
            ),
            'tanker_key_for_reminder_text': 'reminder_text_for_taxi_drivers',
        },
    ],
    DRIVER_REFERRALS_COMBINED_VACANCIES=[
        {
            'vacancy_id': 10,
            'vacancy_name': 'courier',
            'components': ['eda_courier', 'lavka_courier'],
            'image_url': 'https://logo/eda/',
            'tanker_key_for_invitation_text': 'invitation_text_for_couriers',
            'tanker_key_for_reminder_text': ('reminder_text_for_couriers',),
        },
    ],
)
@pytest.mark.pgsql('driver_referrals', files=['driver_with_invites.sql'])
@pytest.mark.now('2019-04-25 15:00:00')
async def test_driver_v1_driver_referrals_invited_list_get_errors(
        web_app_client,
        mockserver,
        load_json,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
        mock_parks_driver_profiles_search,
        mock_fleet_parks_v1_parks_list,
):
    mock_parks_driver_profiles_search(PARKS_DRIVER, {}, None)
    mock_fleet_parks_v1_parks_list({}, None)

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    async def _driver_photos(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(status=500, json={})

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/v2/invited/list',
        params={'status': 'all', 'limit': 10, 'offset': 0},
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p1',
            'X-YaTaxi-Driver-Profile-Id': 'd1',
        },
    )
    assert response.status == 200

    content = await response.json()
    assert not content['items']
    assert content == load_json('expected_invited_list_all_errors.json')


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
    geoareas=conftest.TRANSLATIONS_GEOAREAS,
    tariff=conftest.TRANSLATIONS_TARIFF,
    notify=conftest.TRANSLATIONS_NOTIFY,
)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY=DRIVER_REFERRALS_PROXY_URLS_COUNTRY,
    DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=['rus'],
    DRIVER_REFERRALS_TARIFFS_BY_ORDERS_PROVIDER={
        'taxi': [
            'econom',
            'business',
            'comfortplus',
            'vip',
            'minivan',
            'ultimate',
            'maybach',
        ],
        'eda': ['eda'],
        'lavka': ['lavka'],
    },
    DRIVER_REFERRALS_VACANCIES=[
        {
            'vacancy_id': 1,
            'vacancy_name': 'driver',
            'orders_provider': 'taxi',
            'tariffs': [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'minivan',
                'ultimate',
                'maybach',
            ],
            'show_tariffs': True,
            'image_url': 'https://logo/taxi/',
            'tanker_key_for_invitation_text': (
                'invitation_text_for_taxi_drivers'
            ),
            'tanker_key_for_reminder_text': 'reminder_text_for_taxi_drivers',
        },
        {
            'vacancy_id': 2,
            'vacancy_name': 'eda_courier',
            'orders_provider': 'eda',
            'tariffs': ['eda'],
            'image_url': 'https://logo/eda/',
            'tanker_key_for_invitation_text': (
                'invitation_text_for_eda_couriers'
            ),
            'tanker_key_for_reminder_text': 'reminder_text_for_eda_couriers',
        },
        {
            'vacancy_id': 3,
            'vacancy_name': 'lavka_courier',
            'orders_provider': 'lavka',
            'tariffs': ['lavka'],
            'image_url': 'https://logo/lavka/',
            'tanker_key_for_invitation_text': (
                'invitation_text_for_lavka_couriers'
            ),
            'tanker_key_for_reminder_text': 'reminder_text_for_lavka_couriers',
        },
    ],
)
@pytest.mark.now('2019-04-25 15:00:00')
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals.sql'])
@pytest.mark.parametrize(
    'expected_response',
    (
        pytest.param(
            'expected_response_1.json',
            id='overshadowing + 3 rules',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_1.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_2.json',
            id='splitting of tariffs',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_2.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_3.json',
            id='same rewards for parks, different for selfemployed',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_3.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_4.json',
            id='expired',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_4.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_5.json',
            id='all tariffs, except ...',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_5.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_6.json',
            id='all tariffs',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_6.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_7.json',
            id='combined_vacancies',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_7.sql'],
                ),
                pytest.mark.config(
                    DRIVER_REFERRALS_COMBINED_VACANCIES=[
                        {
                            'vacancy_id': 10,
                            'vacancy_name': 'courier',
                            'components': ['eda_courier', 'lavka_courier'],
                            'image_url': 'https://logo/eda/',
                            'tanker_key_for_invitation_text': (
                                'invitation_text_for_couriers'
                            ),
                            'tanker_key_for_reminder_text': (
                                'reminder_text_for_couriers',
                            ),
                        },
                    ],
                ),
            ],
        ),
    ),
)
async def test_driver_no_invites(
        web_app_client,
        mockserver,
        load_json,
        expected_response,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {'name': 'moscow', 'time_zone': 'Moscow', 'country': 'ru'},
                ],
            },
        )

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/v2/invited/list',
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p',
            'X-YaTaxi-Driver-Profile-Id': 'd',
        },
        params={'type': 'all', 'limit': 10, 'offset': 0},
    )
    assert response.status == 200

    content = await response.json()
    assert content == load_json(expected_response)
