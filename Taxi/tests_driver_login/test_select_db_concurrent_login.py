import hashlib
import uuid

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


@pytest.fixture(name='mock_dms')
def _mock_dms(mockserver):
    class Context:
        def __init__(self):
            self.mode_set = None

    context = Context()

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/set')
    def _driver_mode_subscription_set(request):
        return {
            'active_mode': 'uberdriver',
            'active_mode_type': 'uberdriver_type',
            'active_since': '2019-05-01T12:00:00+0300',
        }

    context.mode_set = _driver_mode_subscription_set
    return context


@pytest.fixture(name='mock_fleet_synchronizer')
def _fleet_synchronizer(mockserver):
    class Context:
        def __init__(self):
            self.login_bulk_check = None
            self.profile_create = None

    context = Context()

    @mockserver.json_handler(
        '/fleet-synchronizer/fleet-synchronizer/v1/parks/login-bulk-check',
    )
    def _mock_login_bulk_check(request):
        valid_parks = [
            park_id
            for park_id in request.json['park_ids']
            if not park_id.startswith('uber')
        ]
        return {
            'items': [
                {'park_id': park_id, 'mapped_park_id': 'uber_' + park_id}
                for park_id in valid_parks
            ],
        }

    @mockserver.json_handler('/fleet-synchronizer/v1/profile/create')
    def _mock_profile_create(request):
        return {
            'mapped_park_id': 'uber_' + request.json['park_id'],
            'mapped_driver_id': 'uber_' + request.json['driver_id'],
            'mapped_car_id': 'uber_' + request.json['car_id'],
            'already_existed': False,
        }

    context.login_bulk_check = _mock_login_bulk_check
    context.profile_create = _mock_profile_create
    return context


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
        requested_park = data['query'].get('park')
        if requested_park:
            return {
                'profiles': [
                    profile
                    for profile in profiles
                    if requested_park['id'][0] == profile['park']['id']
                ],
            }

        requested_phone = data['query']['driver'].get('phone')
        if requested_phone:
            return {
                'profiles': [
                    profile
                    for profile in profiles
                    if requested_phone[0] in profile['driver']['phones']
                ],
            }

        requested_puid = data['query']['driver'].get('platform_uid')
        if requested_puid:
            return {
                'profiles': [
                    profile
                    for profile in profiles
                    if requested_puid[0]
                    == profile['driver'].get('platform_uid')
                ],
            }

        requested_license = data['query']['driver']['license_normalized']
        return {
            'profiles': [
                profile
                for profile in profiles
                if requested_license[0]
                == profile['driver']['license_normalized']
            ],
        }

    context.profiles_search = _search
    return context


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.config(
    TAXIMETER_DENY_DRIVER_CONCURRENT_LOGIN={
        'enable': True,
        'phone_prefixes': [],
        'phone_suffixes': [],
        'require_prefix_and_suffix': False,
        'log_only': False,
    },
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    DRIVER_LOGIN_DELETE_COMMUNICATION_TOKENS_FOR_SIMILAR_PROFILES=True,
)
@pytest.mark.parametrize(
    'is_uberdriver, with_similar_profiles, da_response, fail_by',
    [
        pytest.param(
            False,
            False,
            None,
            None,
            id='single profile, no concurrent login check',
        ),
        pytest.param(
            False,
            True,
            'da_sessions_all_offline.json',
            None,
            id='allow login: all similar profiles are offline',
        ),
        pytest.param(
            False,
            True,
            'da_sessions_all_online.json',
            'license',
            id='forbid login: profiles with same license are online',
        ),
        pytest.param(
            False,
            True,
            'da_sessions_phone_online.json',
            None,
            id='allow login: profiles with same phone are online',
        ),
        pytest.param(
            False,
            True,
            'da_sessions_phone_online.json',
            'phone',
            id='forbid login: profiles with same phone are online + on order',
        ),
        pytest.param(
            False,
            True,
            'da_sessions_all_online_uber.json',
            None,
            id='allow cross-app login'
            '(similar profiles are online, but in another app family)',
        ),
        # same cases but for Uberdriver
        (True, False, None, None),
        (True, True, 'da_sessions_all_offline.json', None),
        (True, True, 'da_sessions_all_online_uber.json', 'license'),
        (True, True, 'da_sessions_phone_online_uber.json', None),
        (True, True, 'da_sessions_phone_online_uber.json', 'phone'),
        (True, True, 'da_sessions_all_online.json', None),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_concurrent_login(
        taxi_driver_login,
        redis_store,
        load_json,
        mockserver,
        mock_parks,
        mock_driver_order_misc,
        mock_driver_authorizer,
        mock_fleet_synchronizer,
        mock_dms,
        mock_client_notify,
        testpoint,
        is_uberdriver,
        with_similar_profiles,
        da_response,
        fail_by,
):
    if with_similar_profiles:
        expected_logged_in_drivers = (
            {
                ('uberdriver', 'uber_dbid_by_license', 'uber_uuid_by_license'),
                ('uberdriver', 'uber_dbid_by_phone', 'uber_uuid_by_phone'),
            }
            if is_uberdriver
            else {
                ('taximeter', 'dbid_by_license', 'uuid_by_license'),
                ('taximeter', 'dbid_by_phone', 'uuid_by_phone'),
                ('taximeter', 'dbid_by_puid', 'uuid_by_puid'),
            }
        )

        mock_driver_authorizer.set_expected_drivers(expected_logged_in_drivers)
        mock_driver_authorizer.set_sessions_response(load_json(da_response))

    parks_data = (
        load_json('parks_response_with_similar.json')
        if with_similar_profiles
        else load_json('parks_response.json')
    )
    mock_parks.set_parks(parks_data)

    mock_driver_order_misc.set_on_order(
        [
            {
                'park_id': 'dbid_by_phone',
                'driver_profile_id': 'uuid_by_phone',
                'on_order': (fail_by == 'phone'),
            },
        ],
    )

    phone = '+79991112233'
    phone_key = (phone + 'uberdriver') if is_uberdriver else phone
    redis_store.setex(_token_key(phone_key), 2600000, _hash_string('token'))

    headers = (
        {**HEADERS, 'User-Agent': 'Taximeter-Uber 9.22 (2000)'}
        if is_uberdriver
        else HEADERS
    )

    @testpoint('similar_profiles')
    async def similar_profiles(data):
        return data

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=headers,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
        },
    )
    assert response.status_code == 200

    assert mock_driver_authorizer.sessions_bulk_retrieve.times_called == int(
        with_similar_profiles,
    )

    assert mock_fleet_synchronizer.profile_create.times_called == int(
        is_uberdriver,
    )
    assert mock_fleet_synchronizer.login_bulk_check.times_called == int(
        is_uberdriver,
    )

    if is_uberdriver and not fail_by:
        assert mock_dms.mode_set.times_called == 1
    else:
        assert mock_dms.mode_set.times_called == 0

    content = response.json()
    if fail_by == 'license':
        assert content == {
            'error': {'code': 33, 'message': 'Concurrent License'},
        }
    elif fail_by in ('phone', 'puid'):
        assert content == {
            'error': {'code': 44, 'message': 'Concurrent Order'},
        }
    else:
        assert content['step'] == 'login'
        similar_profiles_count = int(
            (await similar_profiles.wait_call())['data']['count'],
        )
        assert mock_client_notify.times_called == similar_profiles_count


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.config(
    TAXIMETER_DENY_DRIVER_CONCURRENT_LOGIN={
        'enable': True,
        'phone_prefixes': [],
        'phone_suffixes': [],
        'require_prefix_and_suffix': False,
        'log_only': False,
    },
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    DRIVER_LOGIN_DELETE_COMMUNICATION_TOKENS_FOR_SIMILAR_PROFILES=True,
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_remove_tokens(
        taxi_driver_login, redis_store, load_json, mock_parks,
):
    mock_parks.set_parks(load_json('parks_response.json'))

    phone = '+79991112233'
    puid_key = 'y3000062912'
    redis_store.setex(_token_key(phone), 2600000, _hash_string('token'))
    redis_store.setex(_token_key(puid_key), 2600000, _hash_string('token'))

    headers = HEADERS

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=headers,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
        },
    )
    assert response.status_code == 200
    assert redis_store.get(_token_key(puid_key)) is None


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.config(
    TAXIMETER_DENY_DRIVER_CONCURRENT_LOGIN={
        'enable': True,
        'phone_prefixes': [],
        'phone_suffixes': [],
        'require_prefix_and_suffix': False,
        'log_only': False,
    },
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_concurrent_login_batches(
        taxi_driver_login,
        redis_store,
        load_json,
        mockserver,
        mock_driver_authorizer,
        mock_driver_order_misc,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        data = request.json
        if data['query'].get('park') is not None:
            # first request (with park_id)
            return load_json('parks_response.json')

        return {
            'profiles': [
                {
                    'driver': {
                        'id': uuid.uuid4().hex,
                        'license_normalized': 'AABB101010',
                        'work_status': 'working',
                    },
                    'park': {'id': uuid.uuid4().hex, 'is_active': True},
                }
                for _ in range(35)
            ],
        }

    phone = '+79991112233'
    redis_store.setex(_token_key(phone), 2600000, _hash_string('token'))

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
    assert content['step'] == 'login'
    assert mock_driver_authorizer.sessions_retrieve_count == 105
    assert mock_driver_authorizer.sessions_bulk_retrieve.times_called == 4


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.config(
    TAXIMETER_DENY_DRIVER_CONCURRENT_LOGIN={
        'enable': True,
        'phone_prefixes': [],
        'phone_suffixes': [],
        'require_prefix_and_suffix': False,
        'log_only': False,
    },
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_change_park(
        taxi_driver_login,
        redis_store,
        load_json,
        mockserver,
        mock_parks,
        mock_driver_order_misc,
        mock_driver_authorizer,
):
    expected_logged_in_drivers = {('taximeter', 'dbid1', 'uuid1')}
    da_response = {
        'sessions': [
            {
                'client_id': 'taximeter',
                'driver_app_profile_id': '',
                'park_id': 'dbid1',
                'status': 'ok',
                'uuid': 'uuid1',
            },
        ],
    }
    parks_data = {
        'profiles': [
            {
                'driver': {
                    'id': 'uuid',
                    'license_normalized': 'license',
                    'phone_pd_ids': ['+79991112233_id'],
                    'phones': ['+79991112233'],
                    'work_status': 'working',
                },
                'park': {
                    'city': 'Moscow',
                    'id': 'dbid',
                    'is_active': True,
                    'name': 'Red',
                },
            },
            {
                'driver': {
                    'id': 'uuid1',
                    'license_normalized': 'license',
                    'phone_pd_ids': ['+79991112233_id'],
                    'phones': ['+79991112233'],
                    'work_status': 'working',
                },
                'park': {
                    'city': 'Moscow',
                    'id': 'dbid1',
                    'is_active': True,
                    'name': 'Blue',
                },
            },
        ],
    }

    mock_driver_authorizer.set_expected_drivers(expected_logged_in_drivers)
    mock_driver_authorizer.set_sessions_response(da_response)
    mock_parks.set_parks(parks_data)

    mock_driver_order_misc.set_on_order(
        [
            {
                'park_id': 'dbid1',
                'driver_profile_id': 'uuid1',
                'on_order': False,
            },
        ],
    )

    phone = '+79991112233'
    redis_store.setex(_token_key(phone), 2600000, _hash_string('token'))

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid1_uuid1',
                    'data': {'unique_driver_id': 'udid1'},
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
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert 'step' in content
    assert content['step'] == 'login'


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.config(
    TAXIMETER_DENY_DRIVER_CONCURRENT_LOGIN={
        'enable': True,
        'phone_prefixes': [],
        'phone_suffixes': [],
        'require_prefix_and_suffix': False,
        'log_only': False,
    },
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    DRIVER_LOGIN_TRY_TO_LOGOUT_ON_EXCEPTION=True,
)
@pytest.mark.parametrize(
    'exception_location, params',
    [
        pytest.param(
            'driver-profiles',
            None,
            id='exception in /driver-profiles/v1/driver/login-info',
        ),
        pytest.param(
            'driver-status',
            ['busy'],
            marks=[
                pytest.mark.config(
                    DRIVER_LOGIN_DRIVER_STATUS_CLIENT_FAILURE_SETTINGS={
                        'strategy': 'throw',
                    },
                ),
            ],
            id='exception in /v2/status/store at login',
        ),
        pytest.param(
            'driver-status',
            ['busy', 'offline'],
            marks=[
                pytest.mark.config(
                    DRIVER_LOGIN_DRIVER_STATUS_CLIENT_FAILURE_SETTINGS={
                        'strategy': 'throw',
                    },
                ),
            ],
            id='exception in /v2/status/store at login and logout',
        ),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_false_concurrent_by_license(
        taxi_driver_login,
        redis_store,
        load_json,
        mockserver,
        mock_parks,
        mock_driver_authorizer,
        driver_profiles_info,
        driver_status,
        exception_location,
        params,
):
    parks_data = {
        'profiles': [
            {
                'driver': {
                    'id': 'uuid',
                    'license_normalized': 'license',
                    'phones': ['+79991112233'],
                    'work_status': 'working',
                },
                'park': {
                    'city': 'Moscow',
                    'id': 'dbid',
                    'is_active': True,
                    'name': 'Red',
                },
            },
            {
                'driver': {
                    'id': 'uuid1',
                    'license_normalized': 'license',
                    'phones': ['+75554443322'],
                    'work_status': 'working',
                },
                'park': {
                    'city': 'Moscow',
                    'id': 'dbid1',
                    'is_active': True,
                    'name': 'Blue',
                },
            },
        ],
    }

    @mockserver.json_handler('/driver-authorizer/driver/sessions')
    def _driver_authorizer(request):
        park_id = request.args['park_id']
        driver_id = request.args['uuid']
        if request.method == 'PUT':
            mock_driver_authorizer.set_expected_drivers(
                {('taximeter', park_id, uuid)},
            )
            mock_driver_authorizer.set_sessions_response(
                {
                    'sessions': [
                        {
                            'client_id': 'taximeter',
                            'driver_app_profile_id': '',
                            'park_id': park_id,
                            'status': 'ok',
                            'uuid': driver_id,
                        },
                    ],
                },
            )
        elif request.method == 'DELETE':
            mock_driver_authorizer.set_expected_drivers(set())
            mock_driver_authorizer.set_sessions_response({'sessions': []})
        return mockserver.make_response(
            '{}', headers={'X-Driver-Session': 'session'},
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid_uuid',
                    'data': {'unique_driver_id': 'udid'},
                },
            ],
        }

    mock_parks.set_parks(parks_data)

    redis_store.setex(
        _token_key('+75554443322'), 2600000, _hash_string('token'),
    )
    if exception_location == 'driver-profiles':
        driver_profiles_info.set_do_raise(True)
    elif exception_location == 'driver-status':
        driver_status.set_raise_on(params)
    else:
        assert False
    await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': '+75554443322',
            'step': 'select_db',
            'db': 'dbid1',
            'token': 'token',
        },
    )

    redis_store.setex(
        _token_key('+79991112233'), 2600000, _hash_string('token'),
    )
    driver_profiles_info.set_do_raise(False)
    driver_status.set_raise_on([])
    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': '+79991112233',
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert 'step' in content
    assert content['step'] == 'login'
