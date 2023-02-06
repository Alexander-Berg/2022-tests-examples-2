# pylint: disable=import-error,wildcard-import
import json

from client_blackbox.mock_blackbox import make_phone
import pytest


async def test_route_200(
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

        # Proxy headers added
        assert request.headers['X-Remote-IP'] == '1.2.3.4'

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'test_login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'
        assert (
            request.headers['X-YaTaxi-PhoneId'] == '102610261026102610261026'
        )
        assert request.headers['X-YaTaxi-Session'] == 'taxi:12345'

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}
        return {'id': '123'}

    blackbox_service.set_token_info(
        'test_token', uid='100', login_id='test_login_id',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


async def test_route_handler_timeout(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    async def _test(request):
        stats['call-test'] += 1
        raise mockserver.TimeoutError

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal server error',
    }


async def test_token_passport500(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/test')
    async def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='raise_500',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 500


async def test_token_session500(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/test')
    async def _test(request):
        assert False

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={'Cookie': 'Session_id=raise_500', 'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 500


async def test_route_passport_timeout(taxi_passenger_authorizer, mockserver):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1
        return {'id': '123'}

    @mockserver.json_handler('/blackbox')
    async def _passport_timeout(request):
        raise mockserver.TimeoutError

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
        },
    )
    assert stats['call-test'] == 0
    assert response.status_code == 504
    assert response.json() == {
        'code': '504',
        'message': 'Internal error: network read timeout',
    }


async def test_cache_token(
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

        # Proxy headers added
        assert request.headers['X-Remote-IP'] == '1.2.3.4'

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        assert 'X-Ya-Service-Ticket' in request.headers

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}
        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='0')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert stats['call-test'] == 2
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.parametrize(
    'handler,call_test,status_code',
    [('test', 1, 200), ('session_check_disabled', 0, 401)],
)
async def test_cache_sid_session_check_disabled(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        handler,
        call_test,
        status_code,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/' + handler)
    def _test(request):
        stats['call-test'] += 1
        return {'id': '123'}

    blackbox_service.set_sessionid_info('session_id_cookie', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/' + handler,
        data='{}',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert stats['call-test'] == call_test
    assert response.status_code == status_code


async def test_parse_user_app_info(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1

        assert 'X-Request-Application' in request.headers
        assert (
            dict(
                kv.split('=')
                for kv in request.headers['X-Request-Application'].split(',')
            )
            == {
                'app_brand': 'yauber',
                'app_name': 'mobileweb_uber_kz_android',
                'app_build': 'release',
                'platform_ver1': '9',
                'app_ver1': '3',
                'app_ver2': '85',
                'app_ver3': '1',
            }
        )

        return {'id': '123'}

    blackbox_service.set_sessionid_info('session_id_cookie', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data='{}',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
            'User-Agent': (
                'Mozilla/5.0 (Linux; Android 9; CLT-L29 Build/HUAWE'
                'ICLT-L29; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Version/4.0 Chrome/73.0.3683.90 Mobile Safari/537.36 '
                'uber-kz/3.85.1.72959 Android/9 (HUAWEI; CLT-L29)'
            ),
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'accept_language,expected_locale',
    [('he-IL', 'en'), ('ru-RU', 'ru'), ('en-US, en;q=0.8,ru;q=0.6', 'en')],
)
async def test_parse_user_locale(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        accept_language,
        expected_locale,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Request-Language'] == expected_locale

        return {'id': '123'}

    blackbox_service.set_sessionid_info('session_id_cookie', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data='{}',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
            'Accept-Language': accept_language,
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200


async def test_route_options_method(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.method == 'OPTIONS'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.options(
        '4.0/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={
            'Content-Type': 'application/json',
            'X-YaTaxi-UserId': '12345',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert stats['call-test'] == 1


async def test_route_401_default(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1
        return ''

    blackbox_service.set_token_info('invalid_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        bearer='test_token',
        data=json.dumps({}),
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert stats['call-test'] == 0
    assert response.status_code == 401
    assert response.json() == {
        'code': 'unauthorized',
        'message': 'Not authorized request',
    }


@pytest.mark.routing_rules([])
async def test_noroute(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    blackbox_service.set_token_info('invalid_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        bearer='test_token',
        data=json.dumps({}),
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'No route for URL'}


async def test_thishost_route(
        taxi_passenger_authorizer, blackbox_service, mockserver, taxi_config,
):
    blackbox_service.set_token_info('invalid_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        bearer='test_token',
        data=json.dumps({}),
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': 'unauthorized',
        'message': 'Not authorized request',
    }


async def test_route_403_invalid_token(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/route403/test')
    def _test(request):
        stats['call-test'] += 1

        # Auth headers
        assert 'X-Yandex-Login' not in request.headers
        assert 'X-Login-Id' not in request.headers
        assert 'X-Yandex-UID' not in request.headers
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-YaTaxi-UserId'] == '12345'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'credentials=token-bearer'
        )

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}
        return mockserver.make_response('{"text": "invalid"}', status=403)

    blackbox_service.set_token_info('test_token', uid='100')

    params = {}
    params['bearer'] = 'invalid_token'
    response = await taxi_passenger_authorizer.post(
        '4.0/route403/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Yandex-Login': 'login',
            'X-Yandex-Uid': '123',
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-YaTaxi-UserId': '12345',
        },
        **params,
    )
    assert stats['call-test'] == 1
    assert response.status_code == 403

    # backend responded with custom json without code/message
    assert response.json() == {'text': 'invalid'}


async def test_route_403_no_token(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/route403/test')
    def _test(request):
        stats['call-test'] += 1

        # Auth headers
        assert 'X-Yandex-Login' not in request.headers
        assert 'X-Login-Id' not in request.headers
        assert 'X-Yandex-UID' not in request.headers
        assert 'X-YaTaxi-Pass-Flags' not in request.headers
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}
        return mockserver.make_response('{"text": "invalid"}', status=403)

    blackbox_service.set_token_info('test_token', uid='100')

    params = {}
    response = await taxi_passenger_authorizer.post(
        '4.0/route403/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Yandex-Login': 'login',
            'X-Yandex-Uid': '123',
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-YaTaxi-UserId': '12345',
        },
        **params,
    )
    assert stats['call-test'] == 1
    assert response.status_code == 403

    # backend responded with custom json without code/message
    assert response.json() == {'text': 'invalid'}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({224: 'PASSPORT_TICKET'})
async def test_route_tvm(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/tvm/test')
    def _test(request):
        stats['call-test'] += 1

        service_ticket = '404_ticket_not_set_in_testsuite'
        assert request.headers['X-Ya-Service-Ticket'] == service_ticket
        assert request.headers['X-Ya-User-Ticket'] == 'USER_TICKET'
        assert request.headers['X-Yandex-UID'] == '100'
        assert 'X-YaTaxi-User' not in request.headers

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_token_info(
        'test_token', uid='100', user_ticket='USER_TICKET',
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/tvm/test',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


async def test_check_nosession(taxi_passenger_authorizer, blackbox_service):
    response = await taxi_passenger_authorizer.post(
        'check', data='{"id": "123"}',
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': False, 'is_timed_out': False}


@pytest.mark.passport_token(token1={'uid': '100'})
async def test_user_id_generator(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/launch/123')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert 'X-YaTaxi-UserId' not in request.headers
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/launch/123', bearer='token1', data=json.dumps({}),
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_user_id_generator_session(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/launch/123')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert 'X-YaTaxi-UserId' not in request.headers
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/launch/123',
        headers={'Cookie': 'Session_id=session1'},
        bearer='token1',
        data=json.dumps({}),
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_fallbacks_no(
        taxi_passenger_authorizer, blackbox_service, mockserver, statistics,
):
    @mockserver.json_handler('/4.0/fall-backs/1')
    def _test(request):
        raise mockserver.NetworkError()

    response = await taxi_passenger_authorizer.post(
        '/4.0/fall-backs/1',
        headers={'Cookie': 'Session_id=session1'},
        bearer='token1',
        data=json.dumps({}),
    )

    assert response.status_code == 500
    assert _test.times_called == 3


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_fallbacks_on(
        taxi_passenger_authorizer, blackbox_service, mockserver, statistics,
):
    statistics.fallbacks = ['handler.mock./4.0/fall-backs-post.fallback']

    @mockserver.json_handler('4.0/fall-backs/2')
    def _test(request):
        raise mockserver.NetworkError()

    response = await taxi_passenger_authorizer.post(
        '/4.0/fall-backs/2',
        headers={'Cookie': 'Session_id=session1'},
        bearer='token1',
        data=json.dumps({}),
    )

    assert response.status_code == 500
    assert _test.times_called == 1


@pytest.mark.passport_token(
    token1={
        'uid': '100',
        'login_id': 'test_login_id',
        'has_plus_cashback': '1',
    },
)
async def test_token_flag_cashback_plus(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/test')
    def _test(request):
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            ['phonish', 'credentials=token-bearer', 'cashback-plus'],
        )

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='token1',
        headers={
            'Cookie': 'b',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_session(
    session1={
        'uid': '100',
        'login_id': 'test_login_id',
        'has_plus_cashback': '1',
    },
)
async def test_session_flag_cashback_plus(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/test')
    def _test(request):
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            ['phonish', 'credentials=session', 'cashback-plus'],
        )

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


async def test_bank_flag(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/test')
    def _test(request):
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            ['phonish', 'credentials=session', 'bank-account'],
        )

        return {'id': '123'}

    blackbox_service.set_sessionid_info(
        sessionid='session1',
        uid='100',
        phones=[make_phone('+71111111111', is_bank=True)],
        strict_phone_attributes=True,
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


# Check that GROCERY_AUTHPROXY_MARKET_PASSPORT_SCOPES doesn't work for PA
@pytest.mark.passport_token(
    token={'uid': '100', 'scope': 'market:content-api mobile:all market:pay'},
)
@pytest.mark.config(
    GROCERY_AUTHPROXY_MARKET_PASSPORT_SCOPES=[
        'market:content-api',
        'mobile:all',
        'market:pay',
    ],
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
async def test_market_scope(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    response = await taxi_passenger_authorizer.post(
        '/4.0/test',
        data='123',
        bearer='token',
        headers={
            'Content-Type': 'application/json',
            'Origin': 'localhost',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': 'unauthorized',
        'message': 'Not authorized request',
    }
