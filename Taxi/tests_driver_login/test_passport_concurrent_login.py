import hashlib
import uuid

import pytest

HEADERS = {
    'Authorization': 'Bearer AQAAAACvtHLOAAAIgerDQBbQVEi2qXMwUEDVnuC',
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

TRANSLATIONS = {
    'Login_Error_BadRequest': {'ru': 'Request error'},
    'Login_Error_ConcurrentLicense': {'ru': 'Concurrent License'},
    'Login_Error_ConcurrentOrder_Passport': {'ru': 'Concurrent Order'},
    'Login_Error_ConcurrentOrder': {'ru': 'Concurrent Order'},
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


def _token_key_by_driver(key):
    return f'Driver:AuthToken:{_hash_string(key)}'


def _token_key(key):
    return _token_key_by_driver('y' + key)


def _token_key_phone(phone):
    return _token_key_by_driver(phone)


@pytest.fixture(autouse=True)
def concurrent_login_fixtures(
        load_json,
        blackbox,
        mock_fleet_parks_list,
        mock_parks,
        parks_certifications,
        fleet_vehicles,
        driver_protocol,
        driver_modes,
        driver_support,
        driver_profiles_info,
        unique_drivers,
        yagr_position_store,
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
    'with_similar_profiles, da_response, fail_by',
    [
        pytest.param(
            False, None, None, id='single profile, no concurrent login check',
        ),
        pytest.param(
            True,
            'da_sessions_all_offline.json',
            None,
            id='allow login: all similar profiles are offline',
        ),
        pytest.param(
            True,
            'da_sessions_all_online.json',
            'license',
            id='forbid login: profiles with same license are online',
        ),
        pytest.param(
            True,
            'da_sessions_puid_online.json',
            None,
            id='allow login: profiles with same puid are online',
        ),
        pytest.param(
            True,
            'da_sessions_puid_online.json',
            'puid',
            id='forbid login: profiles with same puid are online + on order',
        ),
        pytest.param(
            True,
            'da_sessions_phone_online.json',
            None,
            id='allow login: profiles with same phone are online',
        ),
        pytest.param(
            True,
            'da_sessions_phone_online.json',
            'phone',
            id='forbid login: profiles with same phone are online + on order',
        ),
    ],
)
@pytest.mark.now('2021-06-21T12:00:00.786Z')
async def test_concurrent_login(
        taxi_driver_login,
        load_json,
        redis_store,
        mockserver,
        mock_parks,
        mock_driver_order_misc,
        mock_driver_authorizer,
        mock_client_notify,
        testpoint,
        with_similar_profiles,
        da_response,
        fail_by,
):
    if with_similar_profiles:
        expected_logged_in_drivers = {
            ('taximeter', 'dbid_by_license', 'uuid_by_license'),
            ('taximeter', 'dbid_by_phone', 'uuid_by_phone'),
            ('taximeter', 'dbid_by_puid', 'uuid_by_puid'),
        }

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
                'park_id': 'dbid_by_puid',
                'driver_profile_id': 'uuid_by_puid',
                'on_order': (fail_by == 'puid'),
            },
        ],
    )

    @testpoint('similar_profiles')
    async def similar_profiles(data):
        return data

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    assert mock_driver_authorizer.sessions_bulk_retrieve.times_called == int(
        with_similar_profiles,
    )

    content = response.json()
    if fail_by == 'license':
        assert response.status_code == 409
        assert content == {
            'code': 'concurrent license',
            'message': 'Concurrent License',
            'details': {'user_message': 'Concurrent License'},
        }
    elif fail_by == 'puid':
        assert response.status_code == 409
        assert content == {
            'code': 'concurrent order',
            'message': 'Concurrent Order',
            'details': {'user_message': 'Concurrent Order'},
        }
    else:
        assert response.status_code == 200
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

    phone = '+72222222222'
    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))
    redis_store.set(_token_key_phone(phone), _hash_string('token'))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )
    assert response.status_code == 200
    assert redis_store.get(_token_key_phone(phone)) is None


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
@pytest.mark.now('2021-06-21T12:00:00.786Z')
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

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
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
                    'phone_pd_ids': ['+72222222222_id'],
                    'phones': ['+72222222222'],
                    'platform_uid': '3000062912',
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
                    'phone_pd_ids': ['+72222222222_id'],
                    'phones': ['+72222222222'],
                    'platform_uid': '3000062912',
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

    puid = '3000062912'
    redis_store.set(_token_key(puid), _hash_string(REQUEST['token']))

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport', headers=HEADERS, json=REQUEST,
    )

    assert response.status_code == 200
    content = response.json()
    assert 'step' in content
    assert content['step'] == 'login'
