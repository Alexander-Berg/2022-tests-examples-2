import json

import pytest


@pytest.mark.parametrize('session_id_cookie', ['auth_session_id_cookie'])
async def test_auth_without_token_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        session_id_cookie,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/allow-dbusers-authorized/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-YaTaxi-UserId'] == '157612345'
        assert request.headers['X-YaTaxi-Pass-Flags'] == 'credentials=session'
        assert 'X-YaTaxi-Session' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    headers = {'X-YaTaxi-UserId': '157612345'}
    if session_id_cookie is not None:
        headers['Cookie'] = 'Session_id=' + session_id_cookie

    response = await taxi_passenger_authorizer.post(
        '4.0/allow-dbusers-authorized/test',
        data=json.dumps({}),
        headers=headers,
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


@pytest.mark.parametrize('session_id_cookie', ['noauth:xxx', None])
async def test_auth_without_token_no_session(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        session_id_cookie,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/allow-dbusers-authorized/test')
    def _test(request):
        stats['call-test'] += 1

        assert 'X-YaTaxi-Pass-Flags' not in request.headers
        assert request.headers['X-YaTaxi-UserId'] == '157612345'
        assert 'X-YaTaxi-Session' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    headers = {'X-YaTaxi-UserId': '157612345'}
    if session_id_cookie is not None:
        headers['Cookie'] = 'Session_id=' + session_id_cookie

    response = await taxi_passenger_authorizer.post(
        '4.0/allow-dbusers-authorized/test',
        data=json.dumps({}),
        headers=headers,
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


@pytest.mark.parametrize(
    'user_id', ['157612340', '157612341', '157612342', '157612344'],
)
@pytest.mark.parametrize(
    'session_id_cookie', [None, 'auth_session_id_cookie', 'noauth:xxx'],
)
async def test_auth_without_token_fail_user(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        user_id,
        session_id_cookie,
):
    @mockserver.json_handler('/4.0/allow-dbusers-authorized/test')
    def _test(request):
        assert False

    headers = {'X-YaTaxi-UserId': user_id}
    if session_id_cookie is not None:
        headers['Cookie'] = 'Session_id=' + session_id_cookie

    response = await taxi_passenger_authorizer.post(
        '4.0/allow-dbusers-authorized/test',
        data=json.dumps({}),
        headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'session_id_cookie', [None, 'auth_session_id_cookie', 'noauth:xxx'],
)
async def test_auth_without_token_fail_rule(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        session_id_cookie,
):
    @mockserver.json_handler('/4.0/123')
    def _test(request):
        assert False

    headers = {'X-YaTaxi-UserId': '157612345'}
    if session_id_cookie is not None:
        headers['Cookie'] = 'Session_id=' + session_id_cookie

    response = await taxi_passenger_authorizer.post(
        '4.0/123', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 401
