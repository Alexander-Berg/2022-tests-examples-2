import copy
import hashlib

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
    'Login_Error_PassportNotFound': {'ru': 'ID not found'},
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
    'step': 'login',
    'park_id': 'dbid',
    'token': 'token',
}


def _hash_string(s):  # pylint: disable=invalid-name
    return hashlib.sha256(
        f'{s}DRIVER_LOGIN_SECRET'.encode('utf-8'),
    ).hexdigest()


def _token_key(key):
    return f'Driver:AuthToken:{_hash_string("y" + key)}'


@pytest.fixture(autouse=True)
def _autouse_fixture(passport_login_step_fixtures):
    pass


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.now('2021-06-21T12:00:00.786Z')
@pytest.mark.parametrize(
    'parameter',
    [
        pytest.param('park_id', id='no park_id'),
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
@pytest.mark.now('2021-06-21T12:00:00.786Z')
async def test_empty_profiles(taxi_driver_login, redis_store, mock_parks):
    mock_parks.set_response({'profiles': []})
    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'puid not found',
        'message': 'ID not found',
        'details': {'user_message': 'ID not found'},
    }


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.now('2021-06-21T12:00:00.786Z')
@pytest.mark.config(
    TAXIMETER_PAY_SYSTEMS_INTEGRATION_SETTINGS={
        '__default__': '',
        'rus': 'http://kiwi',
    },
)
@pytest.mark.parametrize(
    'has_pay_systems_integration, has_got_udid',
    [
        pytest.param(
            True,
            True,
            marks=[
                pytest.mark.uservice_oneshot(
                    disable_first_update=['by-ids-cache'],
                ),
            ],
            id='oneshot',
        ),
        (True, True),
        (False, True),
        (True, False),
        (False, False),
        (True, None),
    ],
)
async def test_login_ok(
        taxi_driver_login,
        mockserver,
        load_json,
        pgsql,
        redis_store,
        mongodb,
        has_pay_systems_integration,
        has_got_udid,
):
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

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        response = load_json('parks_response.json')
        if has_pay_systems_integration is not None:
            response['profiles'][0]['park'][
                'has_pay_systems_integration'
            ] = has_pay_systems_integration
        return response

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    expected_content = load_json('login_ok.json')

    if not has_got_udid:
        expected_content.pop('support_answers')

    if has_pay_systems_integration:
        expected_content['pay_systems_link'] = 'http://kiwi'

    assert response.status_code == 200
    content = response.json()
    content.pop('token')
    assert content == {
        'login': expected_content,
        'step': 'login',
        'phone': '+72222222222',
    }

    assert mongodb.stats_login_stats.count() == 1
    mongo_entry = mongodb.stats_login_stats.find_one()
    assert mongo_entry['_id']
    assert mongo_entry['date']
    assert mongo_entry['db'] == 'dbid'
    assert mongo_entry['driver'] == 'uuid'
    assert mongo_entry['device_id'] == '12345'
    assert mongo_entry['metrica_id'] == 'uuid_12345'
    assert mongo_entry['metrica_device_id'] == '67890'

    workshift_time = redis_store.hget('Driver:WorkDateTimeStart:dbid', 'uuid')
    assert workshift_time == b'\"2021-06-21T12:00:00.786000Z\"'

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


@pytest.mark.config(DRIVER_LOGIN_AFFILIATION_FILTER_ENABLED=True)
@pytest.mark.parametrize('affiliation_state', ['active', 'new', 'rejected'])
@pytest.mark.parametrize('use_affiliations_cache', [True, False])
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.now('2021-06-21T12:00:00.786Z')
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
                    'created_at': '2021-06-01T00:00:00+03:00',
                    'modified_at': '2021-06-01T00:00:00+03:00',
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
                        'phone_pd_ids': ['+72222222222_id'],
                    },
                    'affiliation': {
                        'state': affiliation_state,
                        'partner_source': 'self_employed',
                    },
                },
            ],
        }

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )
    if affiliation_state == 'active':
        assert response.status_code == 400
        assert response.json() == {
            'code': 'puid not found',
            'message': 'ID not found',
            'details': {'user_message': 'ID not found'},
        }
    else:
        assert response.status_code == 200
        assert 'login' in response.json()

    assert (await compare_affiliations.wait_call())['data']['equal']


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
@pytest.mark.now('2021-06-21T12:00:00.786Z')
async def test_eats_courier_id(
        taxi_driver_login,
        redis_store,
        mockserver,
        eats_courier_id,
        orders_provider,
        eats_couriers_binding_retrieved,
):
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
                        'phone_pd_ids': ['+72222222222_id'],
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

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )
    assert response.status_code == 200
    content = response.json()
    assert content['step'] == 'login'
    assert 'login' in content
    assert _driver_profiles_eats_courier_binding.times_called == int(
        eats_couriers_binding_retrieved,
    )


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
@pytest.mark.now('2021-06-21T12:00:00.786Z')
async def test_driver_status_failure(
        taxi_driver_login, redis_store, mockserver, load_json, strategy,
):

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        response = load_json('parks_response.json')
        return response

    @mockserver.json_handler('/driver-status/v2/status/store')
    def _mock_status_store(request):
        raise mockserver.TimeoutError()

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    content = response.json()
    if strategy == 'force_busy':
        assert response.status_code == 200
        assert 'login' in content
        assert content['login']['enable_driver_status_v2']
        assert 'driver_status_info' in content['login']
        assert content['login']['driver_status_info']['value'] == 'busy'
    elif strategy == 'throw':
        assert response.status_code == 500
    elif strategy == 'return_null':
        assert response.status_code == 200
        assert 'login' in content
        assert content['login']['enable_driver_status_v2']
        assert 'driver_status_info' not in content['login']


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.now('2021-06-21T12:00:00.786Z')
@pytest.mark.parametrize(
    'do_store',
    [
        pytest.param(True, id='do store'),
        pytest.param(False, id='do not store'),
    ],
)
async def test_yagr_store(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        yagr_position_store,
        do_store,
):

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        response = load_json('parks_response.json')
        return response

    request = copy.deepcopy(REQUEST)
    if not do_store:
        del request['location_data']

    await taxi_driver_login.invalidate_caches()
    await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=request,
    )

    assert yagr_position_store.times_called == int(do_store)


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.now('2021-06-21T12:00:00.786Z')
@pytest.mark.parametrize(
    [
        'user_agent',
        'taximeter_version',
        'taximeter_brand',
        'taximeter_build_type',
        'taximeter_platform_version',
    ],
    [
        ('Taximeter 9.25 (2222)', '9.25 (2222)', 'yandex', None, None),
        ('Taximeter 10.03 (8517)', '10.03 (8517)', 'yandex', None, None),
        ('Taximeter-beta 9.25 (2222)', '9.25 (2222)', 'yandex', 'beta', None),
        ('Taximeter-Yango 9.25 (2222)', '9.25 (2222)', 'yango', None, None),
        (
            'app:pro brand:yandex version:12.12 build:55531 '
            'platform:ios platform_version:12.0 build_type:dev',
            '12.12 (55531)',
            'yandex',
            'dev',
            '12.0.0',
        ),
        (
            'app:pro brand:yandex version:9.25 build:2222 '
            'platform:ios platform_version:13.0 build_type:beta',
            '9.25 (2222)',
            'yandex',
            'beta',
            '13.0.0',
        ),
        (
            'app:pro brand:yandex version:10.03 build:8517 '
            'platform:ios platform_version:14.0 build_type:dev',
            '10.03 (8517)',
            'yandex',
            'dev',
            '14.0.0',
        ),
    ],
)
async def test_taximeter_version(
        taxi_driver_login,
        driver_profiles_info,
        mockserver,
        load_json,
        user_agent,
        taximeter_version,
        taximeter_brand,
        taximeter_build_type,
        taximeter_platform_version,
        redis_store,
):
    driver_profiles_info.set_taximeter_fields(
        taximeter_version,
        taximeter_brand,
        taximeter_build_type,
        taximeter_platform_version,
    )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(request):
        assert request.json == {'profile_id_in_set': ['dbid_uuid']}

        return {
            'uniques': (
                [
                    {
                        'park_driver_profile_id': 'dbid_uuid',
                        'data': {'unique_driver_id': 'udid'},
                    },
                ]
            ),
        }

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        response = load_json('parks_response.json')
        return response

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    await taxi_driver_login.invalidate_caches()
    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers={**HEADERS, 'User-Agent': user_agent},
        json=REQUEST,
    )

    expected_content = load_json('login_ok.json')

    assert response.status_code == 200
    content = response.json()
    content.pop('token')
    assert content == {
        'login': expected_content,
        'step': 'login',
        'phone': '+72222222222',
    }
