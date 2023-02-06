import json

import pytest


@pytest.mark.passport_token(token1={'uid': '100', 'login_id': 'test_login_id'})
async def test_x_yataxi_authorization(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1

        # No filtered headers
        assert 'X-YaTaxi-Authorization' not in request.headers
        assert 'Authorization' not in request.headers
        assert 'authorization' not in request.headers
        assert 'Cookie' not in request.headers
        assert 'cookie' not in request.headers

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'test_login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-YaTaxi-Authorization': 'Bearer token1',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_token(token1={'uid': '100', 'login_id': 'test_login_id'})
async def test_authorizations_prio_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1

        # No filtered headers
        assert 'X-YaTaxi-Authorization' not in request.headers
        assert 'Authorization' not in request.headers
        assert 'authorization' not in request.headers
        assert 'Cookie' not in request.headers
        assert 'cookie' not in request.headers

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'test_login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='token_invalid',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-YaTaxi-Authorization': 'Bearer token1',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_token(token1={'uid': '100', 'login_id': 'test_login_id'})
async def test_authorizations_prio_fail(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/test')
    def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='token1',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-YaTaxi-Authorization': 'Bearer token_invalid',
        },
    )
    assert response.status_code == 401
