import json

import pytest


URL = '/4.0/late-login-generator/test'


def mix_dicts(dest: dict, source: dict):
    for key, value in source.items():
        if key not in dest:
            dest[key] = {}

        if isinstance(value, dict):
            dest[key].update(value)
        else:
            dest[key] = value


def make_flags(request: dict, phonish: bool, late_login: bool):
    flags = []
    if phonish:
        flags.append('phonish')
    if late_login:
        flags.append('no-login')

    if 'bearer' in request:
        flags.append('credentials=token-bearer')
    else:
        flags.append('credentials=session')
    return set(flags)


async def do_test_zuser_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request,
        phonish,
):
    stats = {'call-test': 0}

    flags = make_flags(request, phonish=phonish, late_login=True)

    @mockserver.json_handler(URL)
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-YaTaxi-Alleged-UserId'] == 'z123511593'
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == flags
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert 'X-YaTaxi-Session' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    req = {
        'data': json.dumps({}),
        'headers': {'X-YaTaxi-UserId': 'z123511593'},
    }
    mix_dicts(req, request)
    response = await taxi_passenger_authorizer.post(URL, **req)

    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


@pytest.mark.passport_token(token1={'uid': '100'})
async def test_zuser_token_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_zuser_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'bearer': 'token1'},
        phonish=True,
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_zuser_session_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_zuser_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'headers': {'Cookie': 'Session_id=session1'}},
        phonish=True,
    )


async def do_test_invalid_user(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request,
        phonish,
):
    stats = {'call-test': 0}

    flags = make_flags(request, phonish=phonish, late_login=False)

    @mockserver.json_handler(URL)
    def _test(request):
        stats['call-test'] += 1

        assert 'X-YaTaxi-Alleged-UserId' not in request.headers
        assert 'X-YaTaxi-UserId' not in request.headers
        assert 'X-YaTaxi-PhoneId' not in request.headers
        assert 'X-YaTaxi-User' not in request.headers
        assert 'X-YaTaxi-Bound-Uids' not in request.headers
        assert 'X-YaTaxi-Session' not in request.headers
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == flags

        return mockserver.make_response('{"text": "smth"}', status=201)

    req = {'data': json.dumps({}), 'headers': {'X-YaTaxi-UserId': '99999'}}
    mix_dicts(req, request)
    response = await taxi_passenger_authorizer.post(URL, **req)
    assert stats['call-test'] == 1
    assert response.status_code == 201


@pytest.mark.passport_token(token1={'uid': '100'})
async def test_invalid_user_token_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_invalid_user(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'bearer': 'token1'},
        phonish=True,
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_invalid_user_session_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_invalid_user(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'headers': {'Cookie': 'Session_id=session1'}},
        phonish=True,
    )


async def do_test_user_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request,
        phonish,
):
    stats = {'call-test': 0}

    flags = make_flags(request, phonish=phonish, late_login=False)

    @mockserver.json_handler(URL)
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-YaTaxi-UserId'] == '12345'
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == flags
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert request.headers['X-YaTaxi-Session'] == 'taxi:12345'

        return mockserver.make_response('{"text": "smth"}', status=201)

    req = {'data': json.dumps({}), 'headers': {'X-YaTaxi-UserId': '12345'}}
    mix_dicts(req, request)
    response = await taxi_passenger_authorizer.post(URL, **req)
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


@pytest.mark.passport_token(token1={'uid': '100'})
async def test_user_token_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_user_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'bearer': 'token1'},
        phonish=True,
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_user_session_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_user_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'headers': {'Cookie': 'Session_id=session1'}},
        phonish=True,
    )


async def do_test_other_user_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request,
        phonish,
):
    stats = {'call-test': 0}

    flags = make_flags(request, phonish=phonish, late_login=False)

    @mockserver.json_handler(URL)
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-YaTaxi-Alleged-UserId'] == '12345'
        assert 'X-YaTaxi-UserId' not in request.headers
        assert 'X-YaTaxi-Session' not in request.headers

        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '101'
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == flags
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert (
            request.headers['X-YaTaxi-PhoneId'] == '102610261026102610261026'
        )

        return mockserver.make_response('{"text": "smth"}', status=201)

    req = {'data': json.dumps({}), 'headers': {'X-YaTaxi-UserId': '12345'}}
    mix_dicts(req, request)
    response = await taxi_passenger_authorizer.post(URL, **req)
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


@pytest.mark.passport_token(token1={'uid': '101'})
async def test_other_user_token_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_other_user_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'bearer': 'token1'},
        phonish=True,
    )


@pytest.mark.passport_session(session1={'uid': '101'})
async def test_other_user_session_ok(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await do_test_other_user_ok(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        request={'headers': {'Cookie': 'Session_id=session1'}},
        phonish=True,
    )
