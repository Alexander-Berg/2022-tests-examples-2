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
@pytest.mark.translations(tariff={'currency_sign.rub': {'ru': 'r'}})
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_fallback(
        taxi_driver_login, driver_modes, redis_store, mockserver, taxi_config,
):

    phone = '+79991112233'
    token_ttl = 2600000
    redis_store.setex(_token_key(phone), token_ttl, _hash_string('token'))

    response = await taxi_driver_login.post(
        'v1/driver/login',
        headers=HEADERS,
        data={
            'phone': phone,
            'step': 'select_db',
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content['login']['active_mode_type'] == 'orders_type'
    assert content['login']['active_mode'] == 'orders_type'

    assert driver_modes.driver_ui_profile.has_calls is True
