import json

import pytest


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
def test_auth_full(
        taxi_marketplace_api,
        passport_internal_submit,
        passport_internal_commit,
        parks_request,
        service_driver_check_request,
):
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
    token = response.headers.get('X-Auth-Token')
    assert token is not None

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


@pytest.mark.now('2018-08-10T20:01:30+0300')
def test_retry_denied(taxi_marketplace_api, passport_internal_submit):
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

    response = taxi_marketplace_api.post(
        '/v1/driver/auth',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'X-Real-Ip': '192.168.123.123',
        },
        json={'identity': {'phone': '+7123456789'}},
    )
    assert response.status_code == 403


@pytest.mark.now('2018-08-10T20:01:30+0300')
def test_session_ttl_expired(taxi_marketplace_api):
    response = taxi_marketplace_api.post(
        '/v1/driver/auth',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'X-Real-Ip': '192.168.123.123',
            'Authorization': 'Bearer test_session',
        },
        json={},
    )
    assert response.status_code == 403


@pytest.mark.now('2018-08-10T22:01:30+0300')
def test_auth_same_token_by_second_auth(
        taxi_marketplace_api,
        passport_internal_submit,
        passport_internal_commit,
        parks_request,
        service_driver_check_request,
):
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
    token = response.headers.get('X-Auth-Token')
    assert token is not None
    # second auth
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
    second_token = response.headers.get('X-Auth-Token')
    assert second_token is not None
    assert second_token == token
