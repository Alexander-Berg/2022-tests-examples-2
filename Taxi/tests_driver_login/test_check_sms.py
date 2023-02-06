import pytest


HEADERS = {
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.22 (2222)',
}

TRANSLATIONS = {
    'Login_Error_InternalServerError': {'ru': 'Internal Error'},
    'Login_Error_SmsNoCode': {'ru': 'Sms No Code'},
    'Login_Error_SmsTooManyAttempts': {'ru': 'Too Many Attempts'},
    'Login_Error_SmsInvalidCode': {'ru': 'Invalid Code'},
    'Login_Driver_Partner_Park_Name': {'ru': 'Login as Selfemployed'},
    'Login_Error_NotFound': {'ru': 'Driver Not Found'},
    'Login_Error_UberDriver_Unregistered': {'ru': 'Uberdriver Unregistered'},
    'Login_Error_UberDriver_CallPark': {'ru': 'Uberdriver CallPark'},
}


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_no_track_id(taxi_driver_login, mockserver):

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={'phone': '+79991112233', 'step': 'sms_code', 'sms_code': '0000'},
    )
    assert response.status_code == 200
    assert response.json() == {'error': {'code': 10, 'message': 'Sms No Code'}}


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    'passport_response, driver_error_message',
    [
        [{'status': 'error'}, {'code': 500, 'message': 'Internal Error'}],
        [
            {'status': 'error', 'errors': []},
            {'code': 500, 'message': 'Internal Error'},
        ],
        [
            {'status': 'error', 'errors': ['confirmations_limit.exceeded']},
            {'code': 12, 'message': 'Too Many Attempts'},
        ],
        [
            {'status': 'error', 'errors': ['code.empty']},
            {'code': 11, 'message': 'Invalid Code'},
        ],
        [
            {'status': 'error', 'errors': ['code.invalid']},
            {'code': 11, 'message': 'Invalid Code'},
        ],
        [
            {'status': 'error', 'errors': ['sms.not_sent']},
            {'code': 10, 'message': 'Sms No Code'},
        ],
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_passport_internal_errors(
        taxi_driver_login,
        redis_store,
        mockserver,
        passport_response,
        driver_error_message,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        assert request.query == {'consumer': 'taxi-driver-login'}
        assert request.form == {'track_id': 'sms_track_id', 'code': '0000'}
        assert request.headers['Ya-Consumer-Client-Ip'] == '1.1.1.1'
        return passport_response

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={'phone': phone, 'step': 'sms_code', 'sms_code': '0000'},
    )
    assert response.status_code == 200
    assert response.json() == {'error': driver_error_message}


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True)
@pytest.mark.parametrize(
    'uberdriver_parks,response_indexes,has_potential_park',
    [
        pytest.param(None, None, False, id='not uberdriver'),
        pytest.param(['dbid1', 'dbid2'], [1, 2], False, id='uberdriver ok'),
        pytest.param([], [], False, id='uberdriver unregistered'),
        pytest.param(
            [],
            [],
            True,
            id='uberdriver callpark_by_city',
            marks=pytest.mark.config(
                PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
                    'uberdriver': {
                        'cities': ['Москва'],
                        'enabled': True,
                        'park_ids': [],
                    },
                },
            ),
        ),
        pytest.param(
            [],
            [],
            True,
            id='uberdriver callpark_both_empty',
            marks=pytest.mark.config(
                PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
                    'uberdriver': {
                        'cities': [],
                        'enabled': True,
                        'park_ids': [],
                    },
                },
            ),
        ),
        pytest.param(
            [],
            [],
            True,
            id='uberdriver callpark_by_park_id',
            marks=pytest.mark.config(
                PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
                    'uberdriver': {
                        'cities': [],
                        'enabled': True,
                        'park_ids': ['dbid_1'],
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_success(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        fleet_synchronizer,
        uberdriver_parks,
        response_indexes,
        has_potential_park,
        taxi_config,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        assert request.query == {'consumer': 'taxi-driver-login'}
        assert request.form == {'track_id': 'sms_track_id', 'code': '0000'}
        assert request.headers['Ya-Consumer-Client-Ip'] == '1.1.1.1'
        return {'status': 'ok'}

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return load_json('parks_response.json')

    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {
            'certifications': [
                {'park_id': 'dbid1', 'is_certified': False},
                {'park_id': 'dbid2', 'is_certified': True},
                {'park_id': 'dbid3', 'is_certified': False},
                {'park_id': 'dbid4', 'is_certified': False},
                {'park_id': 'dbid5', 'is_certified': False},
            ],
        }

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')

    if uberdriver_parks is not None:
        fleet_synchronizer.set_parks(uberdriver_parks)

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers={
            **HEADERS,
            **(
                {'User-Agent': 'Taximeter-Uber 9.22'}
                if uberdriver_parks is not None
                else {}
            ),
        },
        data={'phone': phone, 'step': 'sms_code', 'sms_code': '0000'},
    )
    assert response.status_code == 200

    content = response.json()
    parks = [
        {
            'city': '',
            'is_certified': False,
            'label': 'Login as Selfemployed',
            'id': 'dbid3',
            'self_employed': True,
        },
        {
            'city': '',
            # 'city': 'Москва',
            'is_certified': False,
            'label': 'Sea Bream',
            'id': 'dbid1',
            'self_employed': False,
        },
        {
            'city': '',
            # 'city': 'Таллин',
            'is_certified': True,
            'label': 'Килька',
            'id': 'dbid2',
            'self_employed': False,
        },
    ]
    if uberdriver_parks is None:
        assert content['step'] == 'select_db'
        assert content['domains'] == parks
        assert fleet_synchronizer.login_bulk_check.times_called == 0
    else:
        assert fleet_synchronizer.login_bulk_check.times_called == 1
        if response_indexes:
            assert content['step'] == 'select_db'
            assert content['domains'] == [parks[i] for i in response_indexes]
        elif has_potential_park:
            assert content == {
                'error': {'code': 57, 'message': 'Uberdriver CallPark'},
            }
        else:
            assert content == {
                'error': {'code': 55, 'message': 'Uberdriver Unregistered'},
            }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    'useragent, park_ids',
    [
        ['Taximeter 9.22 (2222)', ['dbid1', 'dbid2']],
        ['Taximeter-az 9.22 (2222)', ['dbid3', 'dbid4']],
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_aze(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        useragent,
        park_ids,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return load_json('parks_response_with_aze.json')

    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {'certifications': []}

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers={**HEADERS, 'User-Agent': useragent},
        data={'phone': phone, 'step': 'sms_code', 'sms_code': '0000'},
    )
    assert response.status_code == 200

    content = response.json()
    assert len(content['domains']) == 2
    assert [
        content['domains'][0]['id'],
        content['domains'][1]['id'],
    ] == park_ids


@pytest.mark.experiments3(filename='experiment_selfreg_2.json')
@pytest.mark.parametrize(
    'params, is_uberdriver, city_id, localized_city, step',
    [
        pytest.param(
            {},
            False,
            'No Localization City Id',
            'No Localization City Id',
            'selfreg',
            id='no_city',
        ),
        pytest.param(
            {'lat': 50.0, 'lon': 90.0},
            False,
            'Москва',
            'Москва Локализованная',
            'selfreg',
            id='city_ok',
        ),
        pytest.param(
            {'lat': 55.0, 'lon': 49.0},
            False,
            'Казань',
            'Казань Локализованная',
            'selfreg_professions',
            id='city_ok_v3',
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
        pytest.param(
            {'lat': 55.0, 'lon': 49.0},
            False,
            'Казань',
            'Казань Локализованная',
            None,
            id='selfreg disabled',
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
            {'lat': 55.0, 'lon': 49.0},
            False,
            'Казань',
            'Казань Локализованная',
            None,
            id='selfreg disabled (after code)',
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
            {'lat': 50.0, 'lon': 90.0},
            True,
            'Москва',
            'Москва Локализованная',
            'selfreg',
            id='uberdriver_ok',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='selfreg_v2_in_login',
                    consumers=['driver_login/selfreg_v2'],
                    clauses=[
                        {
                            'title': 'uberdriver',
                            'predicate': {
                                'init': {
                                    'value': 'uberdriver',
                                    'arg_name': 'application',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            'value': {'selfreg_login_type': 'selfreg'},
                        },
                    ],
                    default_value={'selfreg_login_type': 'disabled'},
                ),
            ],
        ),
    ],
)
@pytest.mark.translations(
    taximeter_backend_api_controllers=TRANSLATIONS,
    cities={
        'Москва': {'ru': 'Москва Локализованная'},
        'Казань': {'ru': 'Казань Локализованная'},
    },
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_selfreg(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        params,
        is_uberdriver,
        city_id,
        localized_city,
        step,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/selfreg/internal/selfreg/v1/login/')
    def _taxi_selfreg(request):
        request_json = request.json
        if params:
            assert request_json['lat'] == params['lat']
            assert request_json['lon'] == params['lon']
        return {
            'city_id': city_id,
            'country_id': 'rus',
            'token': 'selfreg_token',
        }

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return {'profiles': []}

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')

    headers = dict(HEADERS)
    headers['X-Remote-IP'] = '77.72.243.13'  # random Novosibirsk IP
    if is_uberdriver:
        headers['User-Agent'] = 'Taximeter-Uber 9.60 (12345)'

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params=params,
        headers=headers,
        data={'phone': phone, 'step': 'sms_code', 'sms_code': '0000'},
    )
    assert response.status_code == 200
    assert _confirm_commit.has_calls

    content = response.json()
    if not step:
        assert not _taxi_selfreg.has_calls
        assert content == {
            'error': {'code': 404, 'message': 'Driver Not Found'},
        }
        return

    assert _taxi_selfreg.has_calls

    assert content.pop('token')
    step_selfreg_experiments = content['selfreg_info'].pop('typed_options')
    if city_id == 'Москва':
        assert step_selfreg_experiments == {
            'typed_configs': {'items': {}, 'version': -1},
            'typed_experiments': {
                'items': {'some_selfreg_exp_for_taximeter': {'enabled': True}},
                'version': 111,
            },
        }
    else:
        assert step_selfreg_experiments == {
            'typed_configs': {'items': {}, 'version': -1},
            'typed_experiments': {'items': {}, 'version': 111},
        }
    assert content == {
        'step': step,
        'selfreg_info': {
            'city': city_id,
            'localized_city': localized_city,
            'country_code': 'RU',
            'token': 'selfreg_token',
        },
        'personal_info': {'phone_pd_id': phone + '_id'},
    }
