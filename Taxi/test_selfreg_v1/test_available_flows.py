import pytest

HEADERS = {'Accept-Language': 'ru_RU'}
TAXIMETER = 'Taximeter 9.61 (1234)'
UBERDRIVER = 'Taximeter-Uber 9.61 (1234)'

SELFREG_TRANSLATIONS = {
    'selfreg_courier_title': {'ru': 'Пеший курьер'},
    'selfreg_courier_subtitle': {'ru': 'Лол и кек'},
    'selfreg_eats_courier_title': {'ru': 'Курьер Еды'},
    'selfreg_eats_courier_subtitle': {'ru': 'Как пеший, только с едой'},
    'selfreg_employment_screen_description': {'ru': 'За деньги!'},
    'selfreg_employment_screen_title': {'ru': 'Го работать!'},
    'selfreg_without_auto_title': {'ru': 'Водитель без авто'},
    'selfreg_without_auto_subtitle': {'ru': 'Как пеший курьер без ног'},
    'selfreg_with_auto_title': {'ru': 'Водитель на своём авто'},
    'selfreg_with_auto_subtitle': {'ru': 'Наконец-то!'},
    'self_employment_title_default': {'ru': 'Станьте самозанятым'},
    'self_employment_subtitle_default': {'ru': '300 к/наносек'},
    'park_employment_title_default': {'ru': 'Работайте в парке'},
    'park_employment_subtitle_default': {'ru': '100 к/наносек'},
}

DEFAULT_FLOWS_SETTINGS_CONFIG = {
    'flows_ordering': [
        {'name': 'driver-without-auto'},
        {'name': 'driver-with-auto'},
        {'name': 'courier'},
        {'name': 'eats-courier'},
    ],
}

RESPONSE_UBERDRIVER = {
    'available_flows': [
        {
            'code': 'driver-without-auto',
            'qc_deeplink': '',
            'title': 'Водитель без авто',
            'subtitle': 'Как пеший курьер без ног',
        },
        {
            'code': 'driver-with-auto',
            'qc_deeplink': '',
            'title': 'Водитель на своём авто',
            'subtitle': 'Наконец-то!',
        },
    ],
    'employment_screen': {
        'can_be_selfemployed': False,
        'can_work_in_park': True,
        'title': 'Го работать!',
        'description': 'За деньги!',
        'park_employment_info': {
            'title': 'Работайте в парке',
            'subtitle': '100 к/наносек',
        },
    },
    'delivery_driver_allowed': False,
}

RESPONSE_2 = {
    'available_flows': [
        {
            'code': 'driver-without-auto',
            'qc_deeplink': '',
            'title': 'Водитель без авто',
            'subtitle': 'Как пеший курьер без ног',
        },
        {
            'code': 'driver-with-auto',
            'qc_deeplink': '',
            'title': 'Водитель на своём авто',
            'subtitle': 'Наконец-то!',
        },
        {
            'code': 'courier',
            'qc_deeplink': '',
            'title': 'Пеший курьер',
            'subtitle': 'Лол и кек',
        },
        {
            'code': 'eats-courier',
            'url': 'https://courier-selfreg-form.yandex',
            'qc_deeplink': '',
            'subtitle': 'Как пеший, только с едой',
            'title': 'Курьер Еды',
        },
    ],
    'employment_screen': {
        'can_be_selfemployed': False,
        'can_work_in_park': True,
        'title': 'Го работать!',
        'description': 'За деньги!',
        'park_employment_info': {
            'title': 'Работайте в парке',
            'subtitle': '100 к/наносек',
        },
    },
    'delivery_driver_allowed': True,
}
RESPONSE_1 = {
    'available_flows': [
        {
            'code': 'driver-without-auto',
            'qc_deeplink': '',
            'title': 'Водитель без авто',
            'subtitle': 'Как пеший курьер без ног',
        },
        {
            'code': 'driver-with-auto',
            'qc_deeplink': '',
            'title': 'Водитель на своём авто',
            'subtitle': 'Наконец-то!',
        },
    ],
    'employment_screen': {
        'can_be_selfemployed': True,
        'can_work_in_park': True,
        'title': 'Го работать!',
        'description': 'За деньги!',
        'self_employment_info': {
            'title': 'Станьте самозанятым',
            'subtitle': '300 к/наносек',
        },
        'park_employment_info': {
            'title': 'Работайте в парке',
            'subtitle': '100 к/наносек',
        },
    },
    'delivery_driver_allowed': False,
}

RESPONSE_3 = {
    'available_flows': [
        {
            'code': 'driver-without-auto',
            'qc_deeplink': '',
            'title': 'Водитель без авто',
            'subtitle': 'Как пеший курьер без ног',
        },
        {
            'code': 'driver-with-auto',
            'qc_deeplink': '',
            'title': 'Водитель на своём авто',
            'subtitle': 'Наконец-то!',
        },
    ],
    'employment_screen': {
        'can_be_selfemployed': True,
        'can_work_in_park': False,
        'title': 'Го работать!',
        'description': 'За деньги!',
        'self_employment_info': {
            'title': 'Станьте самозанятым',
            'subtitle': '300 к/наносек',
        },
    },
    'delivery_driver_allowed': False,
}

RESPONSE_4 = {
    'available_flows': [
        {
            'code': 'courier',
            'qc_deeplink': '',
            'title': 'Пеший курьер',
            'subtitle': 'Лол и кек',
        },
        {
            'code': 'eats-courier',
            'url': 'https://courier-selfreg-form.yandex',
            'qc_deeplink': '',
            'subtitle': 'Как пеший, только с едой',
            'title': 'Курьер Еды',
        },
    ],
}

RESPONSE_5 = {
    'available_flows': [
        {
            'code': 'courier',
            'qc_deeplink': '',
            'title': 'Пеший курьер',
            'subtitle': 'Лол и кек',
        },
    ],
}


@pytest.mark.translations(
    taximeter_backend_driver_messages=SELFREG_TRANSLATIONS,
)
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': ['Санкт-Петербург'],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_SELFREG_ON_FOOT_ENABLED={'enable': True, 'cities': ['Москва']},
)
@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
    SELFREG_EATS_COURIER_SETTINGS={
        'url': 'https://courier-selfreg-form.yandex',
    },
)
@pytest.mark.client_experiments3(
    consumer='selfreg',
    config_name='selfreg_v2_available_flows_settings',
    args=[],
    value=DEFAULT_FLOWS_SETTINGS_CONFIG,
)
@pytest.mark.parametrize(
    'token, user_agent, has_parks, eats_courier_cities, expected_response',
    [
        pytest.param(
            'token_piter',
            TAXIMETER,
            True,
            [],
            RESPONSE_1,
            id='self+parks enabled, all flows available, except courier/eats',
        ),
        pytest.param(
            'token_moscow',
            TAXIMETER,
            True,
            ['Москва'],
            RESPONSE_2,
            id='self no, parks yes, all flows',
        ),
        pytest.param(
            'token_piter',
            TAXIMETER,
            False,
            [],
            RESPONSE_3,
            id='self yes, no parks, all flows available, except courier/eats',
        ),
        pytest.param(
            'token_moscow',
            TAXIMETER,
            False,
            ['Москва'],
            RESPONSE_4,
            id='no self, no parks, but courier/eats available',
        ),
        pytest.param(
            'token_gomel',
            TAXIMETER,
            False,
            [],
            404,
            id='no self, no parks, no couriers',
        ),
    ],
)
async def test_available_flows(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        token,
        user_agent,
        has_parks,
        eats_courier_cities,
        expected_response,
):
    mock_hiring_forms_default.set_regions(eats_courier_cities)

    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': [] if not has_parks else ['lease', 'private']}

    headers = {'User-Agent': user_agent, **HEADERS}

    response = await taxi_selfreg.get(
        '/selfreg/v1/available-flows/',
        params={'token': token},
        headers=headers,
    )

    if expected_response == 404:
        assert response.status == 404
        assert _hiring_types.times_called == 0
    else:
        assert response.status == 200
        content = await response.json()
        assert content == expected_response
        assert _hiring_types.times_called == 1
    assert mock_hiring_forms_default.regions_handler.has_calls


@pytest.mark.translations(
    taximeter_backend_driver_messages=SELFREG_TRANSLATIONS,
)
@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.client_experiments3(
    consumer='selfreg',
    config_name='selfreg_v2_available_flows_settings',
    args=[],
    value=DEFAULT_FLOWS_SETTINGS_CONFIG,
)
@pytest.mark.parametrize(
    'is_uberdriver_allowed, expected_response',
    [(False, 404), (True, RESPONSE_UBERDRIVER)],
)
async def test_available_flows_uber(
        taxi_selfreg,
        mock_personal,
        mock_fleet_synchronizer,
        is_uberdriver_allowed,
        expected_response,
):
    mock_fleet_synchronizer.set_login_allowed(is_uberdriver_allowed)
    headers = {'User-Agent': UBERDRIVER, **HEADERS}

    response = await taxi_selfreg.get(
        '/selfreg/v1/available-flows/',
        params={'token': 'token_moscow'},
        headers=headers,
    )

    if expected_response == 404:
        assert response.status == 404
    else:
        assert response.status == 200
        content = await response.json()
        assert content == expected_response

    assert mock_fleet_synchronizer.check_login_city_park.times_called == 1
