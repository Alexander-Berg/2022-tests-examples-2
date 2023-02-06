import hashlib

import pytest


HEADERS = {
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

TRANSLATIONS = {
    'Login_Error_InternalServerError': {'ru': 'Internal Error'},
    'Login_Error_BadRequest': {'ru': 'Bad Request'},
    'Login_Error_InvalidToken': {'ru': 'Bad Token'},
    'Login_Error_NotFound': {'ru': 'Driver Not Found'},
    'Login_Error_DriverNoCar': {'ru': 'Driver No Car'},
    'Login_Error_ProfileNotReady': {'ru': 'Wait {0} minutes'},
    'Login_Error_ConcurrentLicense': {'ru': 'Concurrent License'},
    'Login_Error_ConcurrentOrder': {'ru': 'Concurrent Order'},
    'Login_Error_TaximeterVersionDisabled': {
        'ru': 'Taximeter Minimal Version {0}',
    },
}


def _hash_string(s):  # pylint: disable=invalid-name
    return hashlib.sha256(
        f'{s}DRIVER_LOGIN_SECRET'.encode('utf-8'),
    ).hexdigest()


def _token_key(phone):
    return f'Driver:AuthToken:{_hash_string(phone)}'


@pytest.fixture(autouse=True)
def _autouse_fixture(login_last_step_fixtures):
    pass


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_bad_token(taxi_driver_login, mockserver):
    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        return {'track_id': 'track_id', 'status': 'ok'}

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': '+79991112233',
            'step': 'select_db',
            'db': 'dbid',
            'token': 'nonexistent',
        },
    )
    assert response.status_code == 200
    assert response.json()['step'] == 'sms_code'


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_empty_parks_response(
        taxi_driver_login, redis_store, mockserver,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return {'profiles': []}

    phone = '+79991112233'
    redis_store.set(_token_key(phone), _hash_string('token'))

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'error': {'code': 404, 'message': 'Driver Not Found'},
    }


@pytest.mark.parametrize('platform', ['android', 'ios'])
@pytest.mark.parametrize(
    'is_version_old',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                TAXIMETER_VERSION_SETTINGS_BY_PARK={'dbid': {'min': '9.35'}},
            ),
            id='Too old version',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TAXIMETER_VERSION_SETTINGS_BY_PARK={'dbid': {'min': '9.15'}},
            ),
            id='Version is ok',
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_version_disabled_by_park(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        platform,
        is_version_old,
):

    phone = '+79991112233'
    token_ttl = 1000
    redis_store.setex(_token_key(phone), token_ttl, _hash_string('token'))
    headers = HEADERS.copy()
    if platform == 'ios':
        headers['User-Agent'] = 'Taximeter 1.68 (1234) ios'

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=headers,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200
    content = response.json()

    if is_version_old and platform == 'android':
        assert content['error'] == {
            'code': 99,
            'message': 'Taximeter Minimal Version 9.35',
        }

    else:
        assert content['step'] == 'login'
        assert content.get('token')


@pytest.mark.config(DRIVER_LOGIN_AFFILIATION_FILTER_ENABLED=True)
@pytest.mark.parametrize('affiliation_state', ['active', 'new', 'rejected'])
@pytest.mark.parametrize('use_affiliations_cache', [True, False])
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_login_affiliation_driver(
        taxi_driver_login,
        affiliation_state,
        use_affiliations_cache,
        taxi_config,
        redis_store,
        load_json,
        mockserver,
        testpoint,
):
    @testpoint('compare_affiliations')
    def compare_affiliations(data):
        return data

    await taxi_driver_login.enable_testpoints()

    taxi_config.set_values(
        {
            'DRIVER_LOGIN_AFFILIATION_CACHE_SETTINGS': {
                'limit': 1000,
                'use_cache': use_affiliations_cache,
            },
        },
    )

    @mockserver.json_handler('/driver-authorizer/driver/sessions')
    def _driver_authorizer(request):
        return mockserver.make_response(
            '{}', headers={'X-Driver-Session': 'session'},
        )

    @mockserver.json_handler('/fleet-rent/v1/sys/affiliations/all')
    def _fleet_rent(request):
        return {
            'records': [
                {
                    'record_id': 'id',
                    'park_id': 'dbid',
                    'local_driver_id': 'uuid',
                    'original_driver_park_id': 'id',
                    'original_driver_id': 'id',
                    'creator_uid': 'id',
                    'created_at': '2020-01-01T00:00:00+03:00',
                    'modified_at': '2020-01-01T00:00:00+03:00',
                    'state': affiliation_state,
                },
            ],
            'limit': 1,
            'cursor': '',
        }

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
                        'license_normalized': 'AABB101010',
                    },
                    'affiliation': {
                        'state': affiliation_state,
                        'partner_source': 'self_employed',
                    },
                },
            ],
        }

    phone = '+79991112233'
    redis_store.setex(_token_key(phone), 2600000, _hash_string('token'))

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
        },
    )

    assert response.status_code == 200
    content = response.json()
    if affiliation_state == 'active':
        assert 'error' in content, response.text
        assert content == {
            'error': {'code': 404, 'message': 'Driver Not Found'},
        }
    else:
        assert 'login' in content, response.text

    assert (await compare_affiliations.wait_call())['data']['equal']


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.config(
    TAXIMETER_PAY_SYSTEMS_INTEGRATION_SETTINGS={
        '__default__': '',
        'rus': 'http://kiwi',
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'is_token_retained, has_pay_systems_integration, are_lootboxes_enabled,'
    'has_got_udid, has_last_login_at',
    [
        pytest.param(
            True,
            True,
            True,
            True,
            True,
            marks=[
                pytest.mark.uservice_oneshot(
                    disable_first_update=['by-ids-cache'],
                ),
            ],
            id='oneshot',
        ),
        (True, True, True, True, True),
        (False, True, True, True, True),
        (True, False, True, True, True),
        (True, None, True, True, True),
        (True, True, False, True, True),
        (True, True, True, False, True),
        (True, True, True, None, True),
        (True, True, True, True, False),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_select_db_ok(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        is_token_retained,
        has_pay_systems_integration,
        are_lootboxes_enabled,
        has_got_udid,
        has_last_login_at,
        mongodb,
        contractor_random_bonus,
        experiments3,
        pgsql,
):

    phone = '+79991112233'
    token_ttl = 2600000 if is_token_retained else 1000
    redis_store.setex(_token_key(phone), token_ttl, _hash_string('token'))

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(request):
        assert request.json == {'profile_id_in_set': ['dbid_uuid']}

        if has_got_udid is None:
            raise mockserver.TimeoutError()
        return {
            'uniques': (
                [
                    {
                        'park_driver_profile_id': 'dbid_uuid',
                        'data': {'unique_driver_id': 'udid'},
                    },
                ]
                if has_got_udid
                else []
            ),
        }

    if has_last_login_at:
        with pgsql['driver-login-db'].cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO driver_login.table_by_ids
              (park_id, driver_profile_id, last_login_at, modified_at)
            VALUES ('dbid', 'uuid', NOW() - INTERVAL '7 days', NOW());
            """,
            )

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        response = load_json('parks_response.json')
        if has_pay_systems_integration is not None:
            response['profiles'][0]['park'][
                'has_pay_systems_integration'
            ] = has_pay_systems_integration
        return response

    if are_lootboxes_enabled:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='random_bonus_experiment',
            consumers=['driver_protocol/authorization_login_new'],
            clauses=[
                {
                    'title': 'all',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'arg_name': 'unique_driver_id',
                            'arg_type': 'string',
                            'value': 'udid',
                        },
                    },
                    'value': {'backend_lootboxes_enabled': True},
                },
            ],
            default_value={'backend_lootboxes_enabled': False},
        )

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert (content['token'] == 'token') == is_token_retained
    assert content['step'] == 'login'

    expected_content = load_json('login_ok_response.json')
    if not has_got_udid:
        expected_content.pop('support_answers')

    if has_pay_systems_integration:
        expected_content['pay_systems_link'] = 'http://kiwi'

    assert content['login'] == expected_content

    assert mongodb.stats_login_stats.count() == 1
    mongo_entry = mongodb.stats_login_stats.find_one()
    assert mongo_entry['_id']
    assert mongo_entry['date']
    assert mongo_entry['db'] == 'dbid'
    assert mongo_entry['driver'] == 'uuid'
    assert mongo_entry['device_id'] == '00001111'
    assert mongo_entry['metrica_id'] == 'metrica_uuid'
    assert (
        mongo_entry['metrica_device_id'] == '9c19ad8723c6a7e3f4f5709e8179d58b'
    )

    workshift_time = redis_store.hget('Driver:WorkDateTimeStart:dbid', 'uuid')
    assert workshift_time == b'\"2019-04-18T13:10:00.786000Z\"'

    assert contractor_random_bonus.times_called == int(
        are_lootboxes_enabled and (has_got_udid is True),
    )

    with pgsql['driver-login-db'].cursor() as cursor:
        cursor.execute(
            """
            SELECT last_login_at > NOW() - INTERVAL '1 day'
            FROM driver_login.table_by_ids
            WHERE park_id = 'dbid'
              AND driver_profile_id = 'uuid';
            """,
        )
        assert cursor.fetchone()[0] is True


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.parametrize('is_profile_ready', [True, False])
@pytest.mark.parametrize('request_park', ['dbid', 'uber_dbid'])
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_uberdriver(
        taxi_driver_login,
        redis_store,
        mockserver,
        is_profile_ready,
        driver_profiles_info,
        request_park,
        parks,
):
    driver_profiles_info.set_ids(park_id='uber_dbid', driver_id='uber_uuid')

    @mockserver.json_handler('/fleet-synchronizer/v1/profile/create')
    def _fleet_synchronizer_create(request):
        if not is_profile_ready:
            return {
                'mapped_park_id': 'uber_dbid',
                'mapped_driver_id': 'uber_uuid',
                'mapped_car_id': 'uber_car_id',
                'already_existed': False,
                'eta_minutes': 8,
            }
        return {
            'mapped_park_id': 'uber_dbid',
            'mapped_driver_id': 'uber_uuid',
            'mapped_car_id': 'uber_car_id',
            'already_existed': False,
        }

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/set')
    def _driver_mode_subscription_set(request):
        return {
            'active_mode': 'uberdriver',
            'active_mode_type': 'uberdriver_type',
            'active_since': '2019-05-01T12:00:00+0300',
        }

    phone = '+79991112233'
    redis_store.setex(
        _token_key(phone + 'uberdriver'), 2600000, _hash_string('token'),
    )

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers={**HEADERS, 'User-Agent': 'Taximeter-uber 9.22 (2000)'},
        data={
            'phone': phone,
            'step': 'select_db',
            'db': request_park,
            'token': 'token',
        },
    )
    assert response.status_code == 200

    content = response.json()
    if is_profile_ready:
        assert content['step'] == 'login'
        assert content['login']['db'] == 'uber_dbid'
        assert content['login']['guid'] == 'uber_uuid'
    else:
        assert content == {'error': {'code': 88, 'message': 'Wait 8 minutes'}}


def _get_switch_courier_exp(enabled):
    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'is_config': False,
        'name': 'switch_courier_app',
        'consumers': ['driver_login/switch_courier_app'],
        'clauses': [],
        'default_value': {'enabled': enabled},
    }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.parametrize(
    'called_expected',
    [
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'selfemployed': 'dbid',
                        'selfemployed_by_country': {'RU': 'dbid'},
                    },
                ),
                pytest.mark.experiments3(**_get_switch_courier_exp(True)),
            ],
            id='selfemployed courier service',
        ),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'courier_service': {'region': 'dbid'},
                    },
                ),
                pytest.mark.experiments3(**_get_switch_courier_exp(True)),
            ],
            id='common courier service',
        ),
        pytest.param(
            0,
            marks=pytest.mark.experiments3(**_get_switch_courier_exp(True)),
            id='without mapping',
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'selfemployed': 'dbid',
                        'selfemployed_by_country': {'RU': 'dbid'},
                    },
                ),
                pytest.mark.experiments3(**_get_switch_courier_exp(False)),
            ],
            id='exp disabled',
        ),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_switch_courier_app(
        load_json,
        mockserver,
        redis_store,
        taxi_config,
        taxi_driver_login,
        called_expected,
):

    phone = '+79991112233'
    redis_store.setex(_token_key(phone), 1000, _hash_string('token'))

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return load_json('parks_response.json')

    @mockserver.json_handler('/driver-profiles/v1/profile/courier-app')
    def _driver_profiles_set_app(request):
        return {}

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200
    content = response.json()
    expected_content = load_json('login_ok_response.json')

    assert content['step'] == 'login'
    assert content['login'] == expected_content
    assert _driver_profiles_set_app.times_called == called_expected


@pytest.mark.parametrize(
    'orders_provider,eats_couriers_binding_retrieved',
    [
        [None, False],
        [
            {
                'eda': False,
                'retail': False,
                'lavka': False,
                'taxi': True,
                'taxi_walking_courier': False,
            },
            False,
        ],
        [
            {
                'eda': True,
                'lavka': False,
                'taxi': False,
                'taxi_walking_courier': False,
            },
            True,
        ],
        [
            {
                'retail': True,
                'lavka': False,
                'taxi': False,
                'taxi_walking_courier': False,
            },
            True,
        ],
        [
            {
                'retail': True,
                'eda': False,
                'lavka': False,
                'taxi': False,
                'taxi_walking_courier': False,
            },
            True,
        ],
        [
            {
                'retail': False,
                'eda': True,
                'lavka': False,
                'taxi': False,
                'taxi_walking_courier': False,
            },
            True,
        ],
        [
            {
                'retail': False,
                'eda': False,
                'lavka': True,
                'taxi': False,
                'taxi_walking_courier': False,
            },
            True,
        ],
        [
            {
                'eda': False,
                'lavka': False,
                'taxi': False,
                'taxi_walking_courier': False,
                'cargo': True,
                'retail': False,
            },
            False,
        ],
    ],
)
@pytest.mark.parametrize('eats_courier_id', [None, '1122'])
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_eats_courier_id(
        taxi_driver_login,
        redis_store,
        mockserver,
        eats_courier_id,
        orders_provider,
        eats_couriers_binding_retrieved,
):

    phone = '+79991112233'
    token_ttl = 1000
    redis_store.setex(_token_key(phone), token_ttl, _hash_string('token'))

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
                        'orders_provider': orders_provider,
                    },
                    'affiliation': {
                        'state': 'active',
                        'partner_source': 'self_employed',
                    },
                },
            ],
        }

    @mockserver.json_handler('/driver-authorizer/driver/sessions')
    def _driver_authorizer(request):
        if request.method == 'PUT':
            if eats_couriers_binding_retrieved:
                assert request.args.get('eats_courier_id') == eats_courier_id
            else:
                assert 'eats_courier_id' not in request.args
        return mockserver.make_response(
            '{}', headers={'X-Driver-Session': 'session'},
        )

    @mockserver.json_handler(
        '/driver-profiles/v1/eats-couriers-binding'
        '/retrieve_by_park_driver_profile_id',
    )
    def _driver_profiles_eats_courier_binding(request):
        return {
            'binding': [
                {
                    'taxi_id': request.json['id_in_set'][0],
                    'eats_id': eats_courier_id,
                    'courier_app': 'taximeter',
                },
            ],
        }

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['step'] == 'login'
    assert content.get('token')
    assert _driver_profiles_eats_courier_binding.times_called == int(
        eats_couriers_binding_retrieved,
    )


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.parametrize(
    'strategy',
    [
        pytest.param(
            'force_busy',
            marks=[
                pytest.mark.config(
                    DRIVER_LOGIN_DRIVER_STATUS_CLIENT_FAILURE_SETTINGS={
                        'strategy': 'force_busy',
                    },
                ),
            ],
            id='force busy',
        ),
        pytest.param(
            'throw',
            marks=[
                pytest.mark.config(
                    DRIVER_LOGIN_DRIVER_STATUS_CLIENT_FAILURE_SETTINGS={
                        'strategy': 'throw',
                    },
                ),
            ],
            id='throw',
        ),
        pytest.param(
            'return_null',
            marks=[
                pytest.mark.config(
                    DRIVER_LOGIN_DRIVER_STATUS_CLIENT_FAILURE_SETTINGS={
                        'strategy': 'return_null',
                    },
                ),
            ],
            id='old behavior',
        ),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_driver_status_failure(
        taxi_driver_login, redis_store, mockserver, load_json, strategy,
):

    phone = '+79991112233'
    redis_store.set(_token_key(phone), _hash_string('token'))

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        response = load_json('parks_response.json')
        return response

    @mockserver.json_handler('/driver-status/v2/status/store')
    def _mock_status_store(request):
        raise mockserver.TimeoutError()

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200
    content = response.json()
    if strategy == 'force_busy':
        assert 'login' in content
        assert content['login']['enable_driver_status_v2']
        assert 'driver_status_info' in content['login']
        assert content['login']['driver_status_info']['value'] == 'busy'
    elif strategy == 'throw':
        content = {'error': {'code': 500, 'message': 'Internal Error'}}
    elif strategy == 'return_null':
        assert 'login' in content
        assert content['login']['enable_driver_status_v2']
        assert 'driver_status_info' not in content['login']


async def test_empty_dbid(taxi_driver_login, mockserver):
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': '+70001112233',
            'step': 'select_db',
            'db': '',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 400
