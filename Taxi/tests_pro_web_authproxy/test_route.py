# pylint: disable=import-error,wildcard-import
import json

import pytest


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_route_200(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        # No filtered headers
        assert 'Cookie' not in request.headers
        assert 'cookie' not in request.headers

        # Proxy headers added
        assert request.headers['X-Remote-IP'] == '1.2.3.4'

        # Auth headers
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}

        return {'id': '123'}

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1;b=1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


async def test_bad_sid(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    async def _test(request):
        assert False

    response = await taxi_pro_web_authproxy.post(
        'test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={'Cookie': 'Session_id=raise_500'},
    )
    assert response.status_code == 500


async def test_noauth(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        assert False

    response = await taxi_pro_web_authproxy.post(
        'test',
        data=json.dumps({}),
        headers={'Cookie': 'Session_id=noauth:xxx'},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'session_id_cookie', [None, 'auth_session_id_cookie', 'noauth:xxx'],
)
async def test_fail_rule(
        taxi_pro_web_authproxy,
        blackbox_service,
        mockserver,
        session_id_cookie,
):
    @mockserver.json_handler('/test/123')
    def _test(request):
        assert False

    headers = {}
    if session_id_cookie is not None:
        headers['Cookie'] = f'Session_id={session_id_cookie}'

    response = await taxi_pro_web_authproxy.post(
        'test/123', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_route_handler_timeout(
        taxi_pro_web_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/test')
    async def _test(request):
        raise mockserver.TimeoutError

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal server error',
    }


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_route_passport_timeout(taxi_pro_web_authproxy, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        return {'id': '123'}

    @mockserver.json_handler('/blackbox')
    async def _passport_timeout(request):
        raise mockserver.TimeoutError

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
        },
    )
    assert _test.times_called == 0
    assert response.status_code == 504
    assert response.json() == {
        'code': '504',
        'message': 'Internal error: network read timeout',
    }


async def test_cache_sid(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        assert request.json == {'x': {'y': 1, 'z': 456}}
        return {'id': '123'}

    blackbox_service.set_sessionid_info('session1', uid='100')

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    blackbox_service.set_sessionid_info('session1', uid='0')

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 2
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_parse_user_app_info(
        taxi_pro_web_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/test')
    def _test(request):
        assert 'X-Request-Application' in request.headers
        # TODO: what should we expect here?
        return {'id': '123'}

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data='{}',
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.parametrize(
    'accept_language,expected_locale',
    [('he-IL', 'en'), ('ru-RU', 'ru'), ('en-US, en;q=0.8,ru;q=0.6', 'en')],
)
async def test_parse_user_locale(
        taxi_pro_web_authproxy,
        blackbox_service,
        mockserver,
        accept_language,
        expected_locale,
):
    @mockserver.json_handler('/test')
    def _test(request):
        assert request.headers['X-Request-Language'] == expected_locale
        return {'id': '123'}

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data='{}',
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
            'Accept-Language': accept_language,
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200


@pytest.mark.routing_rules([])
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_noroute(taxi_pro_web_authproxy, blackbox_service, mockserver):
    response = await taxi_pro_web_authproxy.post(
        'test',
        data=json.dumps({}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'No route for URL'}


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_route_403_invalid_sid(
        taxi_pro_web_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/test401')
    def _test(request):
        # Auth headers
        assert 'X-Ya-User-Ticket' not in request.headers
        assert 'X-Ya-Service-Ticket' in request.headers

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}

        return mockserver.make_response('{"text": "invalid"}', status=403)

    response = await taxi_pro_web_authproxy.post(
        'test401',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=invalid',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 403

    # backend responded with custom json without code/message
    assert response.json() == {'text': 'invalid'}


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_route_403_no_sid(
        taxi_pro_web_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/test401')
    def _test(request):
        # Auth headers
        assert 'X-Ya-User-Ticket' not in request.headers
        assert 'X-Ya-Service-Ticket' in request.headers

        # Body is the same
        assert request.json == {'x': {'y': 1, 'z': 456}}
        return mockserver.make_response('{"text": "invalid"}', status=403)

    response = await taxi_pro_web_authproxy.post(
        'test401',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 403

    # backend responded with custom json without code/message
    assert response.json() == {'text': 'invalid'}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({224: 'PASSPORT_TICKET'})
async def test_route_tvm(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('test')
    def _test(request):
        service_ticket = '404_ticket_not_set_in_testsuite'
        assert request.headers['X-Ya-Service-Ticket'] == service_ticket
        assert request.headers['X-Ya-User-Ticket'] == 'USER_TICKET'

        return mockserver.make_response('{"text": "smth"}', status=201)

    blackbox_service.set_sessionid_info(
        'session1', uid='100', user_ticket='USER_TICKET',
    )

    response = await taxi_pro_web_authproxy.post(
        'test',
        data=json.dumps({}),
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 201
    assert response.json() == {'text': 'smth'}


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(PRO_WEB_AUTHPROXY_COOKIE_TO_PROXY=['cookie_to_proxy'])
async def test_cookie(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        assert request.headers['Cookie'] == 'cookie_to_proxy=123'
        return {'id': '123'}

    response = await taxi_pro_web_authproxy.post(
        '/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        headers={
            'Cookie': 'Session_id=session1;not_proxied=1;cookie_to_proxy=123',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
