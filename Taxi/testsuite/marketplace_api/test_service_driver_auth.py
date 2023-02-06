import json

import pytest


@pytest.fixture
def parks_request(mockserver):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_parks(request):
        data = json.loads(request.data)
        assert data['query']['driver']['phone'] == ['+7123456789']
        return {
            'profiles': [
                {
                    'driver': {
                        'id': '123',
                        'first_name': 'Насрулло',
                        'last_name': 'Ночмиклос',
                    },
                    'park': {'id': '321'},
                },
            ],
        }


@pytest.fixture
def service_driver_check_request(mockserver):
    @mockserver.json_handler('/driver-protocol/service/driver/check')
    def mock_driver_check(request):
        return {'can_take_orders': True, 'reasons': []}


@pytest.mark.now('2018-08-10T20:01:30+0300')
def test_service_driver_auth_base(
        taxi_marketplace_api, parks_request, service_driver_check_request,
):
    response = taxi_marketplace_api.post(
        '/v1/service/driver/auth',
        headers={'X-YaTaxi-API-Key': 'marketplace_api_key'},
        json={'identity': {'phone': '+7123456789'}},
    )
    assert response.status_code == 200
    code = response.json()['code']
    response = taxi_marketplace_api.post(
        '/v1/service/driver/auth',
        headers={'X-YaTaxi-API-Key': 'marketplace_api_key'},
        json={'identity': {'code': code}},
    )
    assert response.status_code == 200
    assert response.json() == {
        'first_name': 'Насрулло',
        'last_name': 'Ночмиклос',
        'phone': '+7123456789',
    }
    token = response.headers.get('X-Auth-Token')
    response = taxi_marketplace_api.post(
        '/v1/service/driver/auth',
        headers={'X-YaTaxi-API-Key': 'marketplace_api_key'},
        json={'identity': {'code': code}},
    )
    assert response.status_code == 403
    response = taxi_marketplace_api.post(
        '/v1/driver/auth',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'X-Real-Ip': '192.168.123.123',
            'Authorization': 'Bearer ' + token,
        },
        json={},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['first_name'] == 'Насрулло'
    assert data['last_name'] == 'Ночмиклос'


@pytest.fixture
def passport_internal_submit(mockserver):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def mock_passport_submit(request):
        return {
            'status': 'ok',
            'track_id': 'abc',
            'deny_resend_until': '2018-08-10T21:01:30+0300',
            'number': {'original': '+7123456789', 'e164': '+7123456789'},
        }


@pytest.fixture
def passport_internal_commit(mockserver):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def mock_passport_commit(request):
        return {
            'status': 'ok',
            'track_id': 'abc',
            'deny_resend_until': '2018-08-10T21:01:30+0300',
            'number': {'original': '7123456789', 'e164': '+7123456789'},
        }


@pytest.mark.now('2018-08-10T20:01:30+0300')
def test_service_driver_auth_without_confirmation(
        taxi_marketplace_api,
        parks_request,
        service_driver_check_request,
        passport_internal_submit,
        passport_internal_commit,
):
    # create passport track for confirmation
    response = taxi_marketplace_api.post(
        '/v1/driver/auth',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'X-Real-Ip': '192.168.123.123',
        },
        json={'identity': {'phone': '+7123456789'}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    # create authorization code with session
    response = taxi_marketplace_api.post(
        '/v1/service/driver/auth',
        headers={'X-YaTaxi-API-Key': 'marketplace_api_key'},
        json={'identity': {'phone': '+7123456789'}},
    )
    assert response.status_code == 200
    code = response.json()['code']
    # get confirmed session (generated at previous step)
    response = taxi_marketplace_api.post(
        '/v1/driver/auth',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'X-Real-Ip': '192.168.123.123',
        },
        json={'identity': {'phone': '+7123456789', 'sms_code': '1234'}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['first_name'] == 'Насрулло'
    assert data['last_name'] == 'Ночмиклос'
    token_confirmed = response.headers.get('X-Auth-Token')
    assert token_confirmed is not None
    # exchange authorization code for the session
    response = taxi_marketplace_api.post(
        '/v1/service/driver/auth',
        headers={'X-YaTaxi-API-Key': 'marketplace_api_key'},
        json={'identity': {'code': code}},
    )
    assert response.status_code == 200
    assert response.json() == {
        'first_name': 'Насрулло',
        'last_name': 'Ночмиклос',
        'phone': '+7123456789',
    }
    token = response.headers.get('X-Auth-Token')
    assert token == token_confirmed
    # try to use code again
    response = taxi_marketplace_api.post(
        '/v1/service/driver/auth',
        headers={'X-YaTaxi-API-Key': 'marketplace_api_key'},
        json={'identity': {'code': code}},
    )
    assert response.status_code == 403
    # try to auth with the session
    response = taxi_marketplace_api.post(
        '/v1/driver/auth',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'X-Real-Ip': '192.168.123.123',
            'Authorization': 'Bearer ' + token,
        },
        json={},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['first_name'] == 'Насрулло'
    assert data['last_name'] == 'Ночмиклос'
