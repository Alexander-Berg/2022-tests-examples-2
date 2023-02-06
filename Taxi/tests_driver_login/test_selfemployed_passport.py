import hashlib

import pytest


HEADERS = {
    'Authorization': 'Bearer AQAAAACvtHLOAAAIgerDQBbQVEi2qXMwUEDVnuC',
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.25 (2222)',
}


def _hash_string(s):  # pylint: disable=invalid-name
    return hashlib.sha256(
        f'{s}DRIVER_LOGIN_SECRET'.encode('utf-8'),
    ).hexdigest()


def _token_key_by_driver(key):
    return f'Driver:AuthToken:{_hash_string(key)}'


def _token_key(key):
    return _token_key_by_driver('y' + key)


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
        return context.parks_data


@pytest.mark.experiments3(filename='experiment_selfemployed_passport_uid.json')
@pytest.mark.config(
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    EATS_COURIER_SERVICE_MAPPING={
        'service1': {'id2': 'dbid2'},
        'selfemployed': 'dbid3',
        'selfemployed_by_country': {'RU': 'dbid3'},
    },
)
@pytest.mark.parametrize('step', ['passport'])
async def test_selfemployed_passport_right_steps(
        taxi_driver_login, load_json, mockserver, blackbox, step,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_drafts(request):
        request_json = request.json
        assert 'status' in request_json
        assert request_json['status'] == 'draft'
        return {
            'profiles': [
                {
                    'park_id': 'park_id1',
                    'driver_id': 'driver_id1',
                    'profession': 'scooter',
                    'status': 'draft',
                    'city': 'Москва',
                },
                {
                    'park_id': 'park_id2',
                    'driver_id': 'driver_id1',
                    'profession': 'scooter',
                    'status': 'draft',
                    'city': 'Москва',
                },
            ],
        }

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=HEADERS,
        json={
            'device_info': {
                'device_id': '12345',
                'device_model': '12345',
                'metrica_device_id': '12345',
                'metrica_uuid': '12345',
                'network_operator': '12345',
            },
            'location_data': {
                'positions': [
                    {
                        'lat': 50.0,
                        'lon': 50.0,
                        'source': 'Verified',
                        'unix_timestamp': 1642360000,
                    },
                ],
            },
            'step': step,
        },
    )

    assert response.status_code == 200

    content = response.json()
    assert content.pop('token')

    assert content == {
        'step': 'selfemployed',
        'selfemployed_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'profession': 'scooter',
        },
    }


@pytest.mark.experiments3(filename='experiment_selfemployed_passport_uid.json')
@pytest.mark.translations(
    taximeter_backend_api_controllers={
        'Login_Error_InternalServerError': {'ru': 'Internal Error'},
        'Login_Error_BadRequest': {'ru': 'Bad Request'},
        'Login_Error_InvalidToken': {'ru': 'Bad Token'},
        'Login_Error_PassportNotFound': {'ru': 'Passport not found'},
    },
)
@pytest.mark.config(
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    EATS_COURIER_SERVICE_MAPPING={
        'service1': {'id2': 'dbid2'},
        'selfemployed': 'dbid3',
        'selfemployed_by_country': {'RU': 'dbid3'},
    },
    DRIVER_LOGIN_PASSPORT_PHONE_VALIDATION_SETTINGS={
        'login_validation_period_minutes': 20160,
        'bind_phone_validation_period_minutes': 15,
    },
)
@pytest.mark.parametrize(
    'login_params, expected_step',
    [
        pytest.param(
            {'step': 'bind_phone', 'phone': '+74444444444', 'token': 'token'},
            'validate_phone',
            id='selfemployed_passport_bind_phone',
        ),
        pytest.param(
            {'step': 'login', 'park_id': 'dbid', 'token': 'token'},
            'login',
            id='selfemployed_passport_login',
        ),
    ],
)
async def test_selfemployed_passport_other_step(
        taxi_driver_login,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        fleet_vehicles,
        driver_protocol,
        driver_modes,
        driver_support,
        driver_profiles_info,
        unique_drivers,
        yagr_position_store,
        blackbox,
        redis_store,
        login_params,
        expected_step,
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
                        'license_normalized': 'AABB101010',
                        'phone_pd_ids': ['+72222222222_id'],
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_drafts(request):
        return {'profiles': []}

    redis_store.set(
        _token_key('3000062912'), _hash_string(login_params['token']),
    )
    blackbox.set_uid('3000062912')

    response = await taxi_driver_login.post(
        '/driver/v1/login/v2/passport',
        headers=HEADERS,
        json={
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
            **login_params,
        },
    )

    assert response.status_code == 200
    assert response.json()['step'] == expected_step

    assert _find_drafts.times_called == 0
