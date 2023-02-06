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
    'Login_Error_NotFound': {'ru': 'Driver Not Found'},
    'Login_Error_SmsInvalidCode': {'ru': 'Invalid Code'},
    'Login_Driver_Partner_Park_Name': {'ru': 'Login as Selfemployed'},
    'Login_Error_TaximeterVersionDisabled': {'ru': 'Update to {0}'},
    'Login_Error_BadRequest': {'ru': 'Bad request'},
}


@pytest.fixture
def parks_mock(mockserver):
    # FIXME: remove after TAXIMETERBACK-10292
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return {
            'profiles': [
                {
                    'park': {
                        'id': 'dbid',
                        'country_id': 'rus',
                        'city': 'Москва',
                        'is_active': True,
                        'name': 'Sea Bream',
                        'provider_config': {'yandex': {'clid': 'clid'}},
                    },
                    'driver': {
                        'id': 'uuid',
                        'car_id': 'car_id',
                        'first_name': 'John',
                        'middle_name': 'Howard',
                        'last_name': 'Doe',
                        'email': 'a@a.a',
                        'rule_id': 'rule',
                        'license_normalized': 'AABB101010',
                    },
                },
            ],
        }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize('disable_sms', [False, True])
@pytest.mark.parametrize('is_uberdriver', [False, True])
@pytest.mark.parametrize('check_fake_enabled', [False, True])
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_ok(
        taxi_driver_login,
        parks_mock,  # pylint: disable=redefined-outer-name
        mockserver,
        disable_sms,
        is_uberdriver,
        check_fake_enabled,
        taxi_config,
):

    phone = '+79991112233'

    taxi_config.set_values(
        {
            'CHECK_FAKE_PHONES': {
                'enabled': check_fake_enabled,
                'fake_numbers': [phone] if disable_sms else [],
            },
        },
    )

    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        assert request.form == {'track_type': 'authorize'}
        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        assert request.form == {
            'confirm_method': 'by_sms',
            'display_language': 'ru',
            'number': phone,
            'route': 'taxiauth',
            'track_id': 'track_id',
        }

        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'track_id': 'track_id', 'status': 'ok'}

    useragent = f'Taximeter{"-Uber" if is_uberdriver else ""} 9.22 (2000)'
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers={**HEADERS, 'User-Agent': useragent},
        data={'phone': phone, 'step': 'send_sms'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'login_start_options': {
            'typed_configs': {'items': {}, 'version': -1},
            'typed_experiments': {'items': {}, 'version': -1},
        },
        'step': 'sms_code',
        'sms_retry_timeout': 30,
    }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(CHECK_FAKE_PHONES={'enabled': False, 'fake_numbers': []})
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_fake_phone(
        taxi_driver_login,
        parks_mock,  # pylint: disable=redefined-outer-name
        mockserver,
        taxi_config,
):
    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        assert request.form == {'track_type': 'authorize'}
        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        assert request.form == {
            'confirm_method': 'by_sms',
            'display_language': 'ru',
            'number': '+70001112233',
            'route': 'taxiauth',
            'track_id': 'track_id',
        }

        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'track_id': 'track_id', 'status': 'ok'}

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={'phone': '+70001112233', 'step': 'send_sms'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'error': {'code': 400, 'message': 'Bad request'},
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'disabled': [],
            'feature_support': {'feature1': '9.00'},
            'min': '10.00',
        },
    },
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_old_taximeter(taxi_driver_login):
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={'phone': '+79991112233', 'step': 'send_sms'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'error': {'code': 99, 'message': 'Update to 10.00'},
    }


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.parametrize(
    'init_counter,result_counter,confirm_method,step',
    [
        [None, b'1', 'by_flash_call', 'phone_code'],
        [b'1', b'2', 'by_flash_call', 'phone_code'],
        [b'2', b'2', 'by_sms', 'sms_code'],
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_flash_call(
        taxi_driver_login,
        redis_store,
        parks_mock,  # pylint: disable=redefined-outer-name
        mockserver,
        init_counter,
        result_counter,
        confirm_method,
        step,
):

    if init_counter:
        redis_store.set(
            'Driver:FlashCallCounter:+79991112233_id', init_counter,
        )

    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        assert request.form == {'track_type': 'authorize'}
        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/validate/phone_number/',
    )
    def _pi_validate(request):
        assert request.form == {
            'phone_number': '+79991112233',
            'track_id': 'track_id',
            'validate_for_call': 'true',
        }

        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'status': 'ok', 'valid_for_flash_call': True}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        assert request.form == {
            'confirm_method': confirm_method,
            'display_language': 'ru',
            'number': '+79991112233',
            'route': 'taxiauth',
            'track_id': 'track_id',
        }

        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {
            'track_id': 'track_id',
            'status': 'ok',
            'calling_number_template': '+7 901 129-XX-XX',
        }

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': '+79991112233',
            'step': 'send_sms',
            'metricaDeviceId': 'aa',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['step'] == step
    if step == 'phone_code':
        assert content['phone_call_state'] == {
            'calling_number_template': '+7 901 129-XX-XX',
            'attempts_left': 2 - int(result_counter),
            'phone_call_timeout_s': 30,
        }

    counter = redis_store.get('Driver:FlashCallCounter:+79991112233_id')
    assert counter == result_counter


@pytest.mark.parametrize(
    'expect_step_sms_code',
    [
        pytest.param(False, id='Default, no selfreg experiment'),
        pytest.param(
            False,
            id='selfreg disabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'false'}, 'enabled': True},
                    name='selfreg_v2_in_login',
                    consumers=['driver_login/selfreg_v2'],
                    default_value={'selfreg_login_type': 'disabled'},
                ),
            ],
        ),
        pytest.param(
            True,
            id='selfreg enabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='selfreg_v2_in_login',
                    consumers=['driver_login/selfreg_v2'],
                    default_value={'selfreg_login_type': 'selfreg'},
                ),
            ],
        ),
        pytest.param(
            True,
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
        pytest.param(
            True,
            id='selfreg disabled after code',
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
    ],
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
async def test_send_code_no_profiles(
        mockserver, taxi_driver_login, expect_step_sms_code,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return {'profiles': []}

    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        assert request.form == {'track_type': 'authorize'}
        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        assert request.form == {
            'confirm_method': 'by_sms',
            'display_language': 'ru',
            'number': '+79991112233',
            'route': 'taxiauth',
            'track_id': 'track_id',
        }

        assert dict(request.query) == {'consumer': 'taxi-driver-login'}
        return {'track_id': 'track_id', 'status': 'ok'}

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': '+79991112233',
            'step': 'send_sms',
            'metricaDeviceId': 'aa',
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response.pop('login_start_options') == {
        'typed_configs': {'items': {}, 'version': -1},
        'typed_experiments': {'items': {}, 'version': -1},
    }
    if expect_step_sms_code:
        assert _pi_track.has_calls
        assert _pi_confirm_submit.has_calls
        assert response == {'step': 'sms_code', 'sms_retry_timeout': 30}
    else:
        assert not _pi_track.has_calls
        assert not _pi_confirm_submit.has_calls
        assert response == {
            'error': {'code': 404, 'message': 'Driver Not Found'},
        }
