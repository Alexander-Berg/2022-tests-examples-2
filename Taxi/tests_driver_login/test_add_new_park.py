import hashlib

import pytest


HEADERS = {
    'X-Remote-IP': '104.52.12.133',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 10.20 (2222)',
}

TRANSLATIONS = {
    'Login_Error_BadRequest': {'ru': 'Request error'},
    'Login_Error_NotFound': {'ru': 'Driver Not Found'},
}

BAD_REQUEST_RESPONSE_JSON = 'bad_request_response.json'
BAD_TOKEN_RESPONSE_JSON = 'bad_token_response.json'
HAPPY_PATH_RESPONSE_JSON = 'happy_path_response.json'
NOT_FOUND_RESPONSE_JSON = 'not_found_response.json'
PARKS_RESPONSE_JSON = 'parks_response.json'
SELFREG_BAD_RESPONSE_JSON = 'selfreg_bad_response.json'
SELFREG_HAPPY_RESPONSE_JSON = 'selfreg_happy_response.json'


def _hash_string(s):  # pylint: disable=invalid-name
    return hashlib.sha256(
        f'{s}DRIVER_LOGIN_SECRET'.encode('utf-8'),
    ).hexdigest()


def _token_key(key):
    return f'Driver:AuthToken:{_hash_string(key)}'


@pytest.fixture(autouse=True)
def passport_internal(mockserver):
    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        return {'track_id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        return {'status': 'ok'}


@pytest.fixture(name='make_parks_mock')
def _make_parks_mock(mockserver, load_json):
    def _make_mock(response=None):
        @mockserver.json_handler('/parks/driver-profiles/search')
        def _parks(request):
            return load_json(response) if response else {'profiles': []}

    return _make_mock


@pytest.fixture(name='make_selfreg_mock')
def _make_selfreg_mock(mockserver, load_json):
    def _make_mock(park_id, driver_id, response, status=200):
        @mockserver.json_handler('/selfreg/internal/selfreg/v1/change-park')
        def _selfreg(request):
            assert request.json.get('park_id') == park_id
            assert request.json.get('driver_profile_id') == driver_id
            return mockserver.make_response(
                json=load_json(response), status=status,
            )

    return _make_mock


@pytest.mark.now('2022-06-06T13:10:00.786Z')
@pytest.mark.parametrize('step', ['sms_code', 'phone_code', 'phone'])
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'park_list_with_button_response.json',
            marks=pytest.mark.experiments3(
                filename='exp3_add_new_park_allowed.json',
            ),
            id='show button',
        ),
        pytest.param(
            'park_list_without_button_response.json',
            marks=pytest.mark.experiments3(
                filename='exp3_add_new_park_disabled.json',
            ),
            id='no button, show button experiment disabled',
        ),
        pytest.param(
            'park_list_without_button_response.json',
            marks=pytest.mark.experiments3(
                filename='exp3_add_new_park_disallowed_by_selfreg.json',
            ),
            id='no button due to selfreg experiment',
        ),
        pytest.param(
            'park_list_without_button_response.json',
            marks=pytest.mark.experiments3(
                filename='exp3_add_new_park_disallowed_by_selfreg_type.json',
            ),
            id='no button due to incompatible selfreg type',
        ),
    ],
)
async def test_add_new_park_button(
        taxi_driver_login,
        redis_store,
        load_json,
        mockserver,
        step,
        expected_response,
):
    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {'certifications': []}

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')
    redis_store.set(_token_key(phone), _hash_string('token'))

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=HEADERS,
        data={'phone': phone, 'step': step, 'sms_code': '000000'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json.pop('token')
    assert json == load_json(expected_response)


@pytest.mark.now('2022-06-06T13:10:00.786Z')
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.experiments3(filename='exp3_add_new_park_disabled.json')
async def test_add_new_park_step_disabled(
        taxi_driver_login, redis_store, load_json,
):
    phone = '+79991112233'
    redis_store.set(_token_key(phone), _hash_string('token'))

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=HEADERS,
        data={'phone': phone, 'step': 'add_new_park'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json == load_json(BAD_REQUEST_RESPONSE_JSON)


@pytest.mark.now('2022-06-06T13:10:00.786Z')
@pytest.mark.experiments3(filename='exp3_add_new_park_allowed.json')
async def test_bad_token(taxi_driver_login, redis_store, load_json):
    phone = '+79991112233'

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=HEADERS,
        data={'phone': phone, 'step': 'add_new_park'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json == load_json(BAD_TOKEN_RESPONSE_JSON)


@pytest.mark.now('2022-06-06T13:10:00.786Z')
@pytest.mark.experiments3(filename='exp3_add_new_park_allowed.json')
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
async def test_no_profiles(
        taxi_driver_login, redis_store, load_json, make_parks_mock,
):
    phone = '+79991112233'
    redis_store.set(_token_key(phone), _hash_string('token'))
    make_parks_mock()

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=HEADERS,
        data={'phone': phone, 'step': 'add_new_park'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json == load_json(NOT_FOUND_RESPONSE_JSON)


@pytest.mark.now('2022-06-06T13:10:00.786Z')
@pytest.mark.experiments3(filename='exp3_add_new_park_allowed.json')
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
async def test_selfreg_bad_response(
        taxi_driver_login,
        redis_store,
        load_json,
        make_parks_mock,
        make_selfreg_mock,
):
    phone = '+71111111111'
    redis_store.set(_token_key(phone), _hash_string('token'))
    make_parks_mock(PARKS_RESPONSE_JSON)
    park_id = 'p2'
    driver_id = 'd2'
    make_selfreg_mock(park_id, driver_id, SELFREG_BAD_RESPONSE_JSON, 400)

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=HEADERS,
        data={'phone': phone, 'step': 'add_new_park'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json == load_json(BAD_REQUEST_RESPONSE_JSON)


@pytest.mark.now('2022-06-06T13:10:00.786Z')
@pytest.mark.experiments3(filename='exp3_add_new_park_allowed.json')
async def test_happy_path(
        taxi_driver_login,
        redis_store,
        load_json,
        make_parks_mock,
        make_selfreg_mock,
):
    phone = '+71111111111'
    redis_store.set(_token_key(phone), _hash_string('token'))
    make_parks_mock(PARKS_RESPONSE_JSON)
    park_id = 'p2'
    driver_id = 'd2'
    make_selfreg_mock(park_id, driver_id, SELFREG_HAPPY_RESPONSE_JSON)

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=HEADERS,
        data={'phone': phone, 'step': 'add_new_park'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json.pop('token')
    assert json == load_json(HAPPY_PATH_RESPONSE_JSON)
