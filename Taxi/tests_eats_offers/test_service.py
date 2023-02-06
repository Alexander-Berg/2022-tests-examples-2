# Feel free to provide your custom implementation to override generated tests.
import pytest

# pylint: disable=import-error,wildcard-import
from eats_offers_plugins.generated_tests import *  # noqa


HEADERS = {
    'X-Login-Id': '123',
    'X-Yandex-UID': 'uid1',
    'X-Eats-Session': 'sess1',
    'X-YaTaxi-Session': 'eats:sess1',
    'X-Eats-Session-Type': 'appclip',
    'X-YaTaxi-Pass-Flags': 'portal,no-login',
    'X-YaTaxi-User': 'personal_phone_id=1,personal_email_id=2,eats_user_id=3',
    'X-Eats-User': (
        'user_id=eater1,personal_phone_id=4,'
        'personal_email_id=5,partner_user_id=partner1,'
        'eater_uuid=yd7d8s9dud'
    ),
    'Cookie': 'PHPSESSID=123',
    'X-Remote-IP': '127.0.0.0',
    'X-Request-Language': 'ru',
    'X-Request-Application': (
        'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
    ),
}
AUTH_CONTEXT = {
    'inner_session': '123',
    'login_id': '123',
    'session_type': 'appclip',
    'yandex_uid': 'uid1',
    'eats_session': 'sess1',
    'taxi_session': 'eats:sess1',
    'taxi_personal': {'phone_id': '1', 'email_id': '2', 'eats_id': '3'},
    'eats_personal': {
        'phone_id': '4',
        'email_id': '5',
        'user_id': 'eater1',
        'partner_user_id': 'partner1',
        'eater_uuid': 'yd7d8s9dud',
    },
    'flags': {'portal': True, 'no-login': True},
    'locale': 'ru',
    'app_vars': {
        'x': 'y',
        'app_name': 'xxx',
        'app_ver1': '1',
        'app_ver2': '2',
        'app_brand': 'eats-clip',
    },
    'remote_ip': '127.0.0.0',
}


@pytest.mark.parametrize(
    'request_json,endpoint',
    [
        (
            {
                'session_id': 'new-session-id',
                'parameters': {
                    'location': [1.23, 2.34],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            '/v1/offer/set',
        ),
        (
            {
                'session_id': 'session-id-8',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            '/v1/offer/match',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
async def test_eap_auth_context(
        taxi_eats_offers, testpoint, request_json, endpoint,
):
    @testpoint('testpoint_auth_context')
    def testpoint_auth_context(data):
        assert data == AUTH_CONTEXT

    response = await taxi_eats_offers.post(
        endpoint, json=request_json, headers=HEADERS,
    )

    assert response.status_code == 200
    assert testpoint_auth_context.times_called == 1
