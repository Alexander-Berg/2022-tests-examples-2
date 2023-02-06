import json

import pytest


@pytest.mark.config(PASS_AUTH_COOKIE_PATHS={'eats': '/4.0/late-login'})
async def test_late_login_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/late-login/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-YaTaxi-UserId'] == 'z123511593'
        assert request.headers['X-YaTaxi-Pass-Flags'] == 'no-login'
        assert request.headers['X-YaTaxi-Session'] == 'taxi:z123511593'

        return mockserver.make_response('{"text": "smth"}', status=201)

    response = await taxi_passenger_authorizer.post(
        '4.0/late-login/test',
        data=json.dumps({}),
        headers={'X-YaTaxi-UserId': 'z123511593'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}

    assert set(response.cookies.keys()) == set(
        ['webviewuserid', 'webviewuserid_eats'],
    )

    cookie_userid = response.cookies['webviewuserid']
    assert cookie_userid['path'] == '/4.0/late-login'
    assert cookie_userid['max-age'] == '3600'
    assert cookie_userid['secure'] is True
    assert cookie_userid['httponly'] is True


async def test_late_login_stale_cookie_token(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/late-login/test')
    def _test(request):
        stats['call-test'] += 1
        return mockserver.make_response('{"text": "smth"}', status=201)

    response = await taxi_passenger_authorizer.post(
        '4.0/late-login/test',
        data=json.dumps({}),
        headers={
            'X-YaTaxi-UserId': 'z123511593',
            'Cookie': 'webviewtoken=12345',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201


async def test_late_login_header_token_forbidden(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/late-login/test')
    def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/late-login/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': 'z123511593'},
    )
    assert response.status_code == 401


async def test_late_login_session_forbidden(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/late-login/test')
    def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/late-login/test',
        data=json.dumps({}),
        headers={
            'X-YaTaxi-UserId': 'z123511593',
            'Cookie': 'Session_id=session1',
        },
    )
    assert response.status_code == 401


async def test_late_login_fail(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/123')
    def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/123',
        data=json.dumps({}),
        headers={'X-YaTaxi-UserId': 'z123511593'},
    )
    assert response.status_code == 401


@pytest.mark.passport_token(token={'uid': '1111592'})
async def test_bound_userids(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/123')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-YaTaxi-Bound-UserIds'] == 'z15921595'
        assert request.headers['X-YaTaxi-Bound-Sessions'] == 'taxi:z15921595'

        return mockserver.make_response('{"text": "smth"}', status=201)

    response = await taxi_passenger_authorizer.post(
        '4.0/123',
        data=json.dumps({}),
        bearer='token',
        headers={'X-YaTaxi-UserId': '123511594'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
