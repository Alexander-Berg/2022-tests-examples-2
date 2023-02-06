import copy

import pytest


HEADERS = {
    'Authorization': 'Bearer AQAAAACvtHLOAAAIgerDQBbQVEi2qXMwUEDVnuC',
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

TRANSLATIONS = {
    'Login_Error_TaximeterVersionDisabled': {'ru': 'Update to {0}'},
    'Login_Error_BadRequest': {'ru': 'Request error'},
    'Login_Error_InvalidToken': {'ru': 'Bad Token'},
    'Login_ParkList_ScreenTitle': {'ru': 'Вид деятельности'},
    'Login_ParkList_Groups_TaxiDelivery_Title': {'ru': 'Такси и Доставка'},
    'Login_ParkList_Groups_TaxiDelivery_Subtitle': {
        'ru': 'Выберите парк или партнера',
    },
    'Login_ParkList_Groups_EatsLavka_Title': {'ru': 'Еда и Лавка'},
    'Login_ParkList_Categories_Taxi_Title': {'ru': 'Такси'},
    'Login_ParkList_Categories_Delivery_Title': {'ru': 'Доставка'},
    'Login_ParkList_Categories_EatsCourier_Title': {
        'ru': 'Стать курьером Еды',
    },
    'Login_ParkList_Groups_Uslugi_Title': {'ru': 'Услуги'},
    'Login_ParkList_Groups_Market_Title': {'ru': 'Маркет'},
    'Login_Driver_Partner_Park_Name': {'ru': 'Самозанятый'},
    'Login_Error_PassportNotFound': {'ru': 'ID not found'},
}


@pytest.fixture(autouse=True)
def _autouse_fixture(passport_step_fixtures):
    pass


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    'authorized,bb_response',
    [
        pytest.param(True, {}, id='Blackbox ok, scopes ok'),
        pytest.param(
            False,
            {},
            marks=pytest.mark.config(
                DRIVER_AUTHPROXY_PASSPORT_SCOPES=['anohter-taxi-driver:all'],
            ),
            id='Blackbox ok, bad scopes',
        ),
        pytest.param(
            False,
            {
                'error': 'account is disabled',
                'status': {'id': 4, 'value': 'DISABLED'},
            },
            id='Blackbox internal error',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_blackbox_auth(
        taxi_driver_login, load_json, blackbox, authorized, bb_response,
):
    if bb_response:
        blackbox.set_response(bb_response)
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=HEADERS,
        json=load_json('basic_request.json'),
    )
    if authorized:
        assert response.status_code == 200
        content = response.json()
        content.pop('token')
        assert content == load_json('expected_response_only_taxi.json')
    else:
        assert response.status_code == 401
        if bb_response:
            assert response.json() == {
                'code': 'bad passport token',
                'message': 'Bad Token',
                'details': {'user_message': 'Bad Token'},
            }
        else:
            assert response.json() == {
                'code': 'bad scopes',
                'message': 'Bad Token',
                'details': {'user_message': 'Bad Token'},
            }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
async def test_bad_authorization_header(
        taxi_driver_login, load_json, blackbox,
):
    headers = HEADERS.copy()
    headers['Authorization'] = 'Bad'
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=headers,
        json=load_json('basic_request.json'),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad auth header',
        'message': 'Request error',
        'details': {'user_message': 'Request error'},
    }


@pytest.mark.parametrize(
    'is_version_old',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                TAXIMETER_VERSION_SETTINGS_BY_BUILD={
                    '__default__': {
                        'disabled': [],
                        'feature_support': {'passport_authorization': '9.35'},
                        'min': '9.35',
                    },
                },
            ),
            id='Too old version',
        ),
        pytest.param(False, id='Version is ok'),
    ],
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_version_disabled(
        taxi_driver_login, blackbox, load_json, is_version_old,
):
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=HEADERS,
        json=load_json('basic_request.json'),
    )

    if is_version_old:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'bad version',
            'message': 'Update to 9.35',
            'details': {'user_message': 'Update to 9.35'},
        }
    else:
        assert response.status_code == 200
        content = response.json()
        content.pop('token')
        assert content == load_json('expected_response_only_taxi.json')


@pytest.mark.parametrize(
    'is_allowed_app',
    [
        pytest.param(True, id='Allowed app'),
        pytest.param(
            False,
            id='Not allowed app',
            marks=pytest.mark.config(
                TAXIMETER_VERSION_SETTINGS_BY_BUILD={
                    '__default__': {
                        'disabled': [],
                        'feature_support': {'passport_authorization': '9.99'},
                        'min': '9.99',
                    },
                    'taximeter-uber': {
                        'current': '9.99',
                        'feature_support': {'passport_authorization': '99.99'},
                        'min': '9.99',
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_allowed_app(
        taxi_driver_login, blackbox, load_json, is_allowed_app,
):
    headers = HEADERS.copy()
    if not is_allowed_app:
        headers['User-Agent'] = 'Taximeter-Uber 9.99'

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=headers,
        json=load_json('basic_request.json'),
    )

    if is_allowed_app:
        assert response.status_code == 200
        content = response.json()
        content.pop('token')
        assert content == load_json('expected_response_only_taxi.json')
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'bad app',
            'message': 'Request error',
            'details': {'user_message': 'Request error'},
        }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    EATS_COURIER_SERVICE_MAPPING={
        'service1': {'id2': 'dbid2'},
        'selfemployed': 'dbid3',
        'selfemployed_by_country': {'RU': 'dbid3'},
    },
)
@pytest.mark.parametrize(
    ('parks_response', 'is_button_shown', 'expected_response_json'),
    [
        pytest.param(
            'parks_response.json',
            False,
            'expected_response_happy_path.json',
            id='happy_path',
            marks=[pytest.mark.experiments3(filename='exp3_enabled.json')],
        ),
        pytest.param(
            'parks_response.json',
            True,
            'expected_response_only_taxi.json',
            id='only taxi parks, show button',
            marks=[
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
                pytest.mark.experiments3(filename='exp3_enabled.json'),
            ],
        ),
        pytest.param(
            'parks_response.json',
            False,
            'expected_response_only_eda.json',
            id='only eda parks',
            marks=[
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'service1': {'id1': 'dbid1'},
                        'service2': {'id2': 'dbid2'},
                        'service3': {'id3': 'dbid3'},
                    },
                ),
                pytest.mark.experiments3(filename='exp3_enabled.json'),
            ],
        ),
        pytest.param(
            'parks_response_selfemployed.json',
            True,
            'expected_response_selfemployed.json',
            id='selfemployed, show button',
            marks=[
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
                pytest.mark.experiments3(filename='exp3_enabled.json'),
            ],
        ),
        pytest.param(
            'parks_response.json',
            False,
            'expected_response_only_taxi.json',
            id='only taxi parks, exp disabled',
            marks=[
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
                pytest.mark.experiments3(filename='exp3_disabled.json'),
            ],
        ),
        pytest.param(
            'parks_response.json',
            False,
            'expected_response_only_taxi.json',
            id='only taxi parks, no url',
            marks=[
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
                pytest.mark.experiments3(filename='exp3_without_url.json'),
            ],
        ),
        pytest.param(
            'parks_response.json',
            False,
            'expected_response_only_taxi.json',
            id='only taxi parks, no button',
            marks=[
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
                pytest.mark.experiments3(filename='exp3_without_button.json'),
            ],
        ),
    ],
)
async def test_profiles_list(
        taxi_driver_login,
        load_json,
        mock_parks,
        parks_response,
        is_button_shown,
        expected_response_json,
):
    mock_parks.set_response(load_json(parks_response))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=HEADERS,
        json=load_json('basic_request.json'),
    )

    assert response.status_code == 200
    content = response.json()
    content.pop('token')
    expected_content = load_json(expected_response_json)
    if not is_button_shown:
        ecc = copy.deepcopy(expected_content)
        for i, group in enumerate(ecc['park_groups']):
            if 'button' in group:
                del expected_content['park_groups'][i]
    assert content == expected_content


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True)
@pytest.mark.experiments3(filename='exp3_enabled_with_limit.json')
async def test_button_limit(taxi_driver_login, load_json, mock_parks):
    mock_parks.set_response(load_json('parks_response_selfemployed.json'))
    expected_content = load_json('expected_response_selfemployed.json')

    for is_button_shown in [True, True, False, False]:
        response = await taxi_driver_login.post(
            '/driver/v1/login/v2/passport',
            headers=HEADERS,
            json=load_json('basic_request.json'),
        )
        assert response.status_code == 200
        content = response.json()
        content.pop('token')
        ecc = copy.deepcopy(expected_content)
        if not is_button_shown:
            for i, group in enumerate(expected_content['park_groups']):
                if 'button' in group:
                    del ecc['park_groups'][i]
        assert content == ecc


@pytest.mark.experiments3(filename='experiment_selfreg_2.json')
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    (
        'has_passport_phones',
        'is_validation_required',
        'has_phone_profiles',
        'is_neophonish',
    ),
    [
        pytest.param(
            False,
            False,
            False,
            False,
            marks=pytest.mark.now('2021-06-21T09:02:00.000Z'),
            id='no passport phones, ask to add phone',
        ),
        pytest.param(
            True,
            True,
            False,
            False,
            marks=pytest.mark.now('2021-06-21T12:00:00.000Z'),
            id='has passport phones, validation required',
        ),
        pytest.param(
            True,
            False,
            False,
            False,
            marks=pytest.mark.now('2021-06-21T09:02:00.000Z'),
            id='has passport phones, no profiles',
        ),
        pytest.param(
            True,
            False,
            True,
            False,
            marks=pytest.mark.now('2021-06-21T09:02:00.000Z'),
            id='has passport phones, has profiles',
        ),
        pytest.param(
            True,
            False,
            True,
            True,
            marks=[
                pytest.mark.now('2021-09-21T09:02:00.000Z'),
                pytest.mark.config(
                    DRIVER_LOGIN_PASSPORT_PHONE_VALIDATION_SETTINGS={
                        'login_validation_period_minutes': 20160,
                        'bind_phone_validation_period_minutes': 30,
                        'neophonish_validation_skip_step_list': ['passport'],
                    },
                ),
            ],
            id='neophonish, has profiles, confirmed long ago',
        ),
        pytest.param(
            True,
            False,
            False,
            True,
            marks=[
                pytest.mark.now('2021-09-21T09:02:00.000Z'),
                pytest.mark.config(
                    DRIVER_LOGIN_PASSPORT_PHONE_VALIDATION_SETTINGS={
                        'login_validation_period_minutes': 20160,
                        'bind_phone_validation_period_minutes': 30,
                        'neophonish_validation_skip_step_list': ['passport'],
                    },
                ),
            ],
            id='neophonish, no profiles, confirmed long ago',
        ),
    ],
)
async def test_empty_profiles(
        taxi_driver_login,
        mockserver,
        load_json,
        blackbox,
        mock_parks,
        driver_profiles_puid,
        has_passport_phones,
        is_validation_required,
        has_phone_profiles,
        is_neophonish,
):
    @mockserver.json_handler('/selfreg/internal/selfreg/v1/login/')
    def _taxi_selfreg(request):
        return {
            'city_id': 'Moscow',
            'country_id': 'rus',
            'token': 'selfreg_token',
        }

    phone_profiles = [
        {
            'driver': {
                'id': 'uuid',
                'phone_pd_ids': ['+74444444444_id'],
                'license_normalized': 'license',
            },
            'park': {
                'id': 'dbid',
                'city': 'Moscow',
                'name': 'Sea Bream',
                'is_active': True,
            },
        },
    ]

    mock_parks.set_response(
        {'profiles': phone_profiles if has_phone_profiles else []},
    )

    if has_phone_profiles:
        driver_profiles_puid.set_response(
            {'profiles': [{'park_id': 'dbid', 'driver_profile_id': 'uuid'}]},
        )

    if is_neophonish:
        blackbox.set_neophonish()

    if not has_passport_phones:
        blackbox.clear_phones()

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=HEADERS,
        json=load_json('basic_request.json'),
    )

    assert response.status_code == 200
    content = response.json()
    content.pop('token')
    if has_passport_phones:
        if is_validation_required:
            assert content == {
                'step': 'bind_phone',
                'suggested_phone': '+74444444444',
            }
        else:
            if has_phone_profiles:
                assert content['step'] == 'profiles_list'
            else:
                assert content['step'] == 'selfreg'
                assert _taxi_selfreg.has_calls
    else:
        assert content == {'step': 'bind_phone'}


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'disabled': [],
            'feature_support': {
                'passport_authorization': '8.88',
                'passport_login_accept_license_step': '8.88',
            },
            'min': '8.88',
        },
    },
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    'expected_step, license_explicitly_accepted',
    [
        pytest.param('profiles_list', None, id='Eula is already accepted'),
        pytest.param(
            'profiles_list',
            False,
            id='Eula is already accepted, '
            'ignore license_explicitly_accepted=False',
        ),
        pytest.param(
            'accept_license',
            None,
            marks=[pytest.mark.pgsql('driver-login-db', queries=[])],
            id='Eula is not accepted',
        ),
        pytest.param(
            'accept_license',
            False,
            marks=[pytest.mark.pgsql('driver-login-db', queries=[])],
            id='Eula is not accepted, '
            'ignore license_explicitly_accepted=False',
        ),
        pytest.param(
            'profiles_list',
            True,
            marks=[pytest.mark.pgsql('driver-login-db', queries=[])],
            id='Eula is not accepted, accept explicitly',
        ),
        pytest.param(
            'profiles_list',
            None,
            marks=pytest.mark.config(
                TAXIMETER_VERSION_SETTINGS_BY_BUILD={
                    '__default__': {
                        'disabled': [],
                        'feature_support': {
                            'passport_authorization': '8.88',
                            'passport_login_accept_license_step': '10.15',
                        },
                        'min': '8.88',
                    },
                },
            ),
            id='Eula is not accepted, disabled by config',
        ),
    ],
)
async def test_eula(
        taxi_driver_login,
        load_json,
        expected_step,
        license_explicitly_accepted,
):
    body = load_json('basic_request.json')
    if license_explicitly_accepted is not None:
        body['license_explicitly_accepted'] = license_explicitly_accepted

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=body,
    )

    content = response.json()
    assert 'step' in content
    assert content['step'] == expected_step


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize('has_profiles', [True, False])
async def test_uslugi(taxi_driver_login, load_json, blackbox, has_profiles):
    headers = HEADERS.copy()
    headers['User-Agent'] = 'Taximeter-embedded 90.25 (2222)'
    if not has_profiles:
        blackbox.set_uid('80085')

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=headers,
        json=load_json('basic_request.json'),
    )

    content = response.json()
    if has_profiles:
        assert response.status_code == 200
        content.pop('token')
        assert content == {
            'park_groups': [
                {
                    'group_type': 'uslugi',
                    'icon_name': 'uslugi_park_group_icon',
                    'parks': [
                        {
                            'city': '',
                            'id': 'dbid4',
                            'is_certified': False,
                            'label': 'Sea Bream 4',
                            'self_employed': False,
                        },
                    ],
                    'title': 'Услуги',
                },
            ],
            'step': 'profiles_list',
            'title': 'Вид деятельности',
        }
    else:
        assert response.status_code == 400
        assert content == {
            'code': 'puid not found',
            'message': 'ID not found',
            'details': {'user_message': 'ID not found'},
        }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize('has_profiles', [True, False])
async def test_market(taxi_driver_login, load_json, blackbox, has_profiles):
    headers = HEADERS.copy()
    headers['User-Agent'] = 'Taximeter-embedded 91.25 (2222)'
    if not has_profiles:
        blackbox.set_uid('80085')

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=headers,
        json=load_json('basic_request.json'),
    )

    content = response.json()
    if has_profiles:
        assert response.status_code == 200
        content.pop('token')
        assert content == {
            'park_groups': [
                {
                    'group_type': 'market',
                    'icon_name': 'market_park_group_icon',
                    'parks': [
                        {
                            'city': '',
                            'id': 'dbid5',
                            'is_certified': True,
                            'label': 'Sea Bream 5',
                            'self_employed': False,
                        },
                    ],
                    'title': 'Маркет',
                },
            ],
            'step': 'profiles_list',
            'title': 'Вид деятельности',
        }
    else:
        assert response.status_code == 400
        assert content == {
            'code': 'puid not found',
            'message': 'ID not found',
            'details': {'user_message': 'ID not found'},
        }
