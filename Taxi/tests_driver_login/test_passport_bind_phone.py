import hashlib

import pytest

HEADERS = {
    'Authorization': 'Bearer AQAAAACvtHLOAAAIgerDQBbQVEi2qXMwUEDVnuC',
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

TRANSLATIONS = {
    'Login_Error_InvalidToken': {'ru': 'Bad Token'},
    'Login_Error_BadRequest': {'ru': 'Request error'},
    'Login_Error_PassportNotFound': {'ru': 'Passport not found'},
    'Login_Error_ConcurrentSimultaneous': {'ru': 'Something went wrong'},
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
    'Login_Driver_Partner_Park_Name': {'ru': 'Самозанятый'},
}

REQUEST = {
    'device_info': {
        'device_id': '12345',
        'device_model': 'ImaginaryDevice',
        'metrica_device_id': '67890',
        'metrica_uuid': 'uuid_12345',
        'network_operator': 'BestOfTheBest',
    },
    'location_data': {
        'positions': [
            {
                'lat': 50,
                'lon': 50,
                'source': 'Verified',
                'unix_timestamp': 164236000,
            },
        ],
    },
    'step': 'bind_phone',
    'phone': '+74444444444',
    'token': 'token',
}


def _hash_string(s):  # pylint: disable=invalid-name
    return hashlib.sha256(
        f'{s}DRIVER_LOGIN_SECRET'.encode('utf-8'),
    ).hexdigest()


def _token_key(key):
    return f'Driver:AuthToken:{_hash_string("y" + key)}'


@pytest.fixture(autouse=True)
def bind_phone_fixtures(
        load_json,
        blackbox,
        mock_fleet_parks_list,
        mock_parks,
        parks_certifications,
):
    pass


@pytest.fixture(name='mock_parks')
def _mock_parks(mockserver):
    class Context:
        def __init__(self):
            self.parks_data = {'profiles': []}
            self.profiles_search = None

        def set_parks(self, parks_data):
            self.parks_data = parks_data

    context = Context()

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _search(request):
        profiles = context.parks_data['profiles']
        data = request.json

        requested_phone = data['query']['driver'].get('phone')
        if requested_phone:
            requested_phone_id = requested_phone[0] + '_id'
            return {
                'profiles': [
                    profile
                    for profile in profiles
                    if requested_phone_id in profile['driver']['phone_pd_ids']
                ],
            }

        requested_puid = data['query']['driver'].get('platform_uid')
        if requested_puid:
            return {
                'profiles': [
                    profile
                    for profile in profiles
                    if 'platform_uid' in profile['driver']
                    and requested_puid[0] == profile['driver']['platform_uid']
                ],
            }
        return {'profiles': []}

    context.profiles_search = _search
    return context


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    'parameter',
    [
        pytest.param('phone', id='no phone'),
        pytest.param('token', id='no token'),
    ],
)
async def test_missing_parameter(taxi_driver_login, parameter):
    request = REQUEST.copy()
    del request[parameter]
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=request,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'missing parameter',
        'message': 'Request error',
        'details': {'user_message': 'Request error'},
    }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T09:31:00.786Z')
@pytest.mark.config(
    DRIVER_LOGIN_PASSPORT_PHONE_VALIDATION_SETTINGS={
        'login_validation_period_minutes': 20160,
        'bind_phone_validation_period_minutes': 15,
    },
)
async def test_validate_phone(taxi_driver_login, redis_store):
    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )
    assert response.status_code == 200
    content = response.json()
    content.pop('token')
    assert content == {'step': 'validate_phone', 'phone': '+74444444444'}


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T09:05:00.786Z')
@pytest.mark.parametrize(
    'with_passport_profiles, filtered_by',
    [
        pytest.param(False, None, id='phone only, success'),
        pytest.param(False, 'puid', id='phone only, filtered by puid'),
        pytest.param(False, 'dp', id='phone only, filtered by dp'),
        pytest.param(True, None, id='phone and passport, success'),
        pytest.param(True, 'park', id='phone and passport, filtered by park'),
        pytest.param(True, 'puid', id='phone and passport, filtered by puid'),
        pytest.param(True, 'dp', id='phone and passport, filtered by dp'),
    ],
)
async def test_profiles_list(
        taxi_driver_login,
        load_json,
        mock_parks,
        redis_store,
        driver_profiles_puid,
        with_passport_profiles,
        filtered_by,
):
    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    parks_response = load_json('parks_response.json')
    if not with_passport_profiles:
        del parks_response['profiles'][1]

    dp_response = {
        'profiles': [{'park_id': 'dbid1', 'driver_profile_id': 'uuid1'}],
    }

    profiles = parks_response['profiles']
    if filtered_by == 'park':
        profiles[1]['park']['id'] = 'dbid1'
        profiles[1]['driver']['phone_pd_ids'][0] = 'another_phone_id'
    if filtered_by == 'puid':
        profiles[0]['driver']['platform_uid'] = 'another_puid'
    if filtered_by == 'dp':
        dp_response['profiles'] = []

    mock_parks.set_parks(parks_response)
    driver_profiles_puid.set_response(dp_response)

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    assert response.status_code == 200
    content = response.json()
    assert content['step'] == 'profiles_list'

    if filtered_by:
        assert 'unbound_parks' in content
        assert len(content['unbound_parks']) == 1
        assert content['unbound_parks'][0]['id'] == 'dbid1'
        assert content['unbound_parks'][0]['label'] == 'Sea Bream 1'
    else:
        assert 'unbound_parks' not in content

    has_groups = with_passport_profiles or not filtered_by
    if has_groups:
        taxi_group = content['park_groups'][0]
        assert taxi_group['group_type'] == 'taxi_and_delivery'
        assert len(taxi_group['parks']) == int(with_passport_profiles) + int(
            not filtered_by,
        )


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T09:05:00.786Z')
async def test_fleet_filtering(
        taxi_driver_login, load_json, redis_store, mock_parks,
):
    parks_response = load_json('parks_response.json')
    profiles = parks_response['profiles']
    profiles[0]['park']['fleet_type'] = 'uberdriver'
    mock_parks.set_parks(parks_response)

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    assert response.status_code == 200
    content = response.json()
    assert content['step'] == 'profiles_list'
    assert 'unbound_parks' not in content
    assert len(content['park_groups']) == 1
    assert content['park_groups'][0]['parks'][0]['id'] == 'dbid2'


@pytest.mark.experiments3(filename='experiment_selfreg_2.json')
@pytest.mark.translations(
    taximeter_backend_api_controllers=TRANSLATIONS,
    cities={'Москва': {'ru': 'Москва Локализованная'}},
)
@pytest.mark.now('2021-06-21T09:05:00.786Z')
@pytest.mark.parametrize(
    'expect_selfreg, city_id, localized_city',
    [
        pytest.param(
            'selfreg',
            'No Localization City Id',
            'No Localization City Id',
            id='no_city',
        ),
        pytest.param(
            'selfreg', 'Москва', 'Москва Локализованная', id='city_ok',
        ),
        pytest.param(
            None,
            'No Localization City Id',
            'No Localization City Id',
            id='Selfreg experiment is hit but disabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='selfreg_v2_in_login',
                    consumers=['driver_login/selfreg_v2'],
                    default_value={'selfreg_login_type': 'disabled'},
                ),
            ],
        ),
        pytest.param(
            None,
            'No Localization City Id',
            'No Localization City Id',
            id='Selfreg experiment is hit but disabled (after code)',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='selfreg_v2_in_login',
                    consumers=['driver_login/selfreg_v2'],
                    default_value={
                        'selfreg_login_type': 'disabled_after_code',
                    },
                ),
            ],
        ),
        pytest.param(
            'selfreg_professions',
            'No Localization City Id',
            'No Localization City Id',
            id='selfreg_professions enabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='selfreg_v2_in_login',
                    consumers=['driver_login/selfreg_v2'],
                    default_value={
                        'selfreg_login_type': 'selfreg_professions',
                    },
                ),
            ],
        ),
    ],
)
async def test_selfreg(
        mockserver,
        taxi_driver_login,
        load_json,
        redis_store,
        expect_selfreg,
        city_id,
        localized_city,
):
    @mockserver.json_handler('/selfreg/internal/selfreg/v1/login/')
    def _taxi_selfreg(request):
        return {
            'city_id': city_id,
            'country_id': 'rus',
            'token': 'selfreg_token',
        }

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )
    content = response.json()
    if expect_selfreg:
        assert response.status_code == 200
        assert _taxi_selfreg.has_calls
        step_selfreg_experiments = content['selfreg_info'].pop('typed_options')
        if city_id == 'Москва':
            assert step_selfreg_experiments == {
                'typed_configs': {'items': {}, 'version': -1},
                'typed_experiments': {
                    'items': {
                        'some_selfreg_exp_for_taximeter': {'enabled': True},
                    },
                    'version': 111,
                },
            }
        else:
            assert step_selfreg_experiments == {
                'typed_configs': {'items': {}, 'version': -1},
                'typed_experiments': {'items': {}, 'version': 111},
            }
        assert 'selfreg_info' in content
        content['selfreg_info'].pop('country_code')
        content.pop('token')
        assert content == {
            'step': expect_selfreg,
            'selfreg_info': {
                'city': city_id,
                'localized_city': localized_city,
                'token': 'selfreg_token',
            },
            'personal_info': {'phone_pd_id': REQUEST['phone'] + '_id'},
            'phone': REQUEST['phone'],
        }
    else:
        assert response.status_code == 400
        assert content == {
            'code': 'puid not found',
            'message': 'Passport not found',
            'details': {'user_message': 'Passport not found'},
        }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T12:00:00.786Z')
@pytest.mark.parametrize(
    'phone, is_binding_allowed',
    [
        pytest.param(
            '+70001112233',
            True,
            marks=[
                pytest.mark.config(
                    CHECK_FAKE_PHONES={'enabled': True, 'fake_numbers': []},
                ),
            ],
            id='Fake phone, bind phone',
        ),
        pytest.param(
            '+79991112233',
            True,
            marks=[
                pytest.mark.config(
                    CHECK_FAKE_PHONES={
                        'enabled': True,
                        'fake_numbers': ['79991112233'],
                    },
                ),
            ],
            id='Fake phone in fake_numbers, bind phone',
        ),
        pytest.param(
            '+70001112233',
            False,
            marks=[
                pytest.mark.config(
                    CHECK_FAKE_PHONES={'enabled': False, 'fake_numbers': []},
                ),
            ],
            id='Fake phone, bad request',
        ),
    ],
)
async def test_fake_phone(
        taxi_driver_login,
        redis_store,
        mockserver,
        mock_parks,
        driver_profiles_puid,
        phone,
        is_binding_allowed,
):
    parks_response = {
        'profiles': [
            {
                'driver': {
                    'car_id': 'car_id',
                    'email': 'a@a.a',
                    'first_name': 'John',
                    'id': 'uuid1',
                    'last_name': 'Doe',
                    'license_normalized': 'AABB101010',
                    'middle_name': 'Howard',
                    'phone_pd_ids': [phone + '_id'],
                    'rule_id': 'rule',
                },
                'park': {
                    'city': 'Москва',
                    'country_id': 'rus',
                    'id': 'dbid1',
                    'is_active': True,
                    'name': 'Sea Bream',
                    'provider_config': {'yandex': {'clid': 'clid'}},
                },
            },
        ],
    }

    dp_response = {
        'profiles': [{'park_id': 'dbid1', 'driver_profile_id': 'uuid1'}],
    }

    mock_parks.set_parks(parks_response)
    driver_profiles_puid.set_response(dp_response)

    request = REQUEST.copy()
    request['phone'] = phone

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=request,
    )

    content = response.json()
    if is_binding_allowed:
        assert response.status_code == 200
        assert content['step'] == 'profiles_list'
    else:
        assert response.status_code == 400
        assert content == {
            'code': 'bad phone',
            'message': 'Request error',
            'details': {'user_message': 'Request error'},
        }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T12:00:00.786Z')
async def test_bad_token(taxi_driver_login, mockserver, redis_store):
    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    request = REQUEST.copy()
    request['token'] = 'bad token'

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=request,
    )

    assert response.status_code == 401
    assert response.json() == {
        'code': 'bad pro token',
        'message': 'Bad Token',
        'details': {'user_message': 'Bad Token'},
    }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T09:05:00.786Z')
async def test_simultaneous_binding(
        taxi_driver_login,
        load_json,
        redis_store,
        mock_parks,
        driver_profiles_puid,
        blackbox,
        testpoint,
):
    parks_response = load_json('parks_response.json')
    mock_parks.set_parks(parks_response)
    driver_profiles_puid.set_response(
        {'profiles': [{'park_id': 'dbid1', 'driver_profile_id': 'uuid1'}]},
    )

    @testpoint('simultaneous_binding')
    async def _simultaneous_binding(data):
        if data['passport_uid'] == '3000062912':
            blackbox.set_uid('1222233444')
            response = await taxi_driver_login.post(
                '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
            )
            assert response.status_code == 409
            assert response.json() == {
                'code': 'concurrent binding',
                'message': 'Something went wrong',
                'details': {'user_message': 'Something went wrong'},
            }
        return data

    for puid in ['3000062912', '1222233444']:
        redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    blackbox.set_uid('3000062912')
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    assert response.status_code == 200
    content = response.json()
    assert content['step'] == 'profiles_list'


@pytest.mark.experiments3(filename='experiment_selfreg_2.json')
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    ('has_passport_phones', 'is_validation_required', 'is_neophonish'),
    [
        pytest.param(
            False,
            True,
            False,
            marks=pytest.mark.now('2021-06-21T09:02:00.000Z'),
            id='no passport phones, ask for validation',
        ),
        pytest.param(
            True,
            True,
            False,
            marks=pytest.mark.now('2021-06-21T12:00:00.000Z'),
            id='has passport phones, stale phone validation',
        ),
        pytest.param(
            True,
            False,
            False,
            marks=pytest.mark.now('2021-06-21T09:02:00.000Z'),
            id='has passport phones, phone confirmed recently',
        ),
        pytest.param(
            True,
            True,
            True,
            marks=pytest.mark.now('2021-09-21T09:02:00.000Z'),
            id='neophonish, confirmed long ago',
        ),
        pytest.param(
            True,
            False,
            True,
            marks=pytest.mark.now('2021-06-21T09:02:00.000Z'),
            id='neophonish, just confirmed',
        ),
    ],
)
async def test_phone_validation(
        taxi_driver_login,
        mockserver,
        load_json,
        blackbox,
        mock_parks,
        redis_store,
        driver_profiles_puid,
        has_passport_phones,
        is_validation_required,
        is_neophonish,
):
    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    @mockserver.json_handler('/selfreg/internal/selfreg/v1/login/')
    def _taxi_selfreg(request):
        return {
            'city_id': 'Moscow',
            'country_id': 'rus',
            'token': 'selfreg_token',
        }

    parks_response = load_json('parks_response.json')
    mock_parks.set_parks(parks_response)
    driver_profiles_puid.set_response(
        {'profiles': [{'park_id': 'dbid1', 'driver_profile_id': 'uuid1'}]},
    )

    if is_neophonish:
        blackbox.set_neophonish()

    if not has_passport_phones:
        blackbox.clear_phones()

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    assert response.status_code == 200
    content = response.json()
    content.pop('token')
    if not has_passport_phones or is_validation_required:
        assert content == {'step': 'validate_phone', 'phone': '+74444444444'}
    else:
        assert content['step'] == 'profiles_list'


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize('is_market', [False, True])
async def test_uslugi_market(
        taxi_driver_login, load_json, blackbox, is_market,
):
    headers = HEADERS.copy()
    headers['User-Agent'] = f'Taximeter-embedded 9{int(is_market)}.25 (2222)'

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=headers, json=REQUEST,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'phone binding not allowed',
        'message': 'Request error',
        'details': {'user_message': 'Request error'},
    }
