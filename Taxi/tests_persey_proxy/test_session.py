import dateutil.parser
import pytest

from testsuite import utils

CSRF_TOKEN = 'KREK7iRRO0iOvBhm5H8CDM1U6KQ=:1516579200'
DATE = '2018-01-22T00:00:00Z'

SESSION_HEADERS = {
    'Cookie': 'Session_id=session1; yandexuid=123',
    'X-CSRF-Token': CSRF_TOKEN,
}

ANON_CSRF_TOKEN = 'xGXjjRI03tqf6P01Nsnj4q+GaGc=:1516579200'

EMPTY_HEADERS = {'X-CSRF-Token': ANON_CSRF_TOKEN, 'Cookie': 'yandexuid=123'}

URL_AUTH = 'persey/v1/auth'
URL_AUTH_ADMIN = 'persey/v1/auth-admin'
URL_NOAUTH = 'persey/v1/noauth'

REMOTE_RESPONSE = {'sentinel': True}

CONFIG = [
    {
        'input': {'http-path-prefix': '/' + URL_AUTH_ADMIN},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'server-hosts': ['*'],
            'auth': 'session-labs',
        },
    },
    {
        'input': {'http-path-prefix': '/' + URL_AUTH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'server-hosts': ['*'],
            'auth': 'session',
        },
    },
    {
        'input': {'http-path-prefix': '/' + URL_NOAUTH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {'proxy-401': True, 'server-hosts': ['*'], 'auth': 'session'},
    },
    {
        'input': {'http-path-prefix': '/csrf_token'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'server-hosts': ['*'],
            'auth': 'session-csrf-token-generator',
        },
    },
    {
        'input': {'http-path-prefix': '/csrf_token_noauth'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': True,
            'server-hosts': ['*'],
            'auth': 'session-csrf-token-generator',
        },
    },
]


async def do_test_ok(
        mock_remote,
        request_post,
        url_path,
        headers,
        method='post',
        exp_request_headers=None,
        **kwargs,
):
    handler = mock_remote(url_path=url_path)
    response = await request_post(
        url_path=url_path, headers=headers, method=method,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'

    if exp_request_headers:
        for key, value in exp_request_headers.items():
            assert response_headers[key] == value

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


async def do_test_fail(mock_remote, request_post, url_path, headers, **kwargs):
    handler = mock_remote(url_path=url_path)
    response = await request_post(url_path=url_path, headers=headers)

    assert not handler.has_calls
    assert response.status_code == 401
    assert not response.cookies


async def do_test_fail_csrf(mock_remote, request_post, url_path, headers):
    handler = mock_remote(url_path=url_path)
    response = await request_post(url_path=url_path, headers=headers)

    assert not handler.has_calls
    assert response.status_code == 401
    assert not response.cookies
    assert response.json()['code'] == 'INVALID_CSRF_TOKEN'


@pytest.mark.now(DATE)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_ok(
        mock_remote, request_post, taxi_persey_proxy, blackbox_service,
):
    await do_test_ok(mock_remote, request_post, URL_AUTH, SESSION_HEADERS)


@pytest.mark.now(DATE)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
async def test_session_fail(
        mock_remote, request_post, taxi_persey_proxy, blackbox_service,
):
    await do_test_fail(mock_remote, request_post, URL_AUTH, SESSION_HEADERS)


@pytest.mark.now(DATE)
@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
async def test_csrf_token_noyandexuid(
        mock_remote,
        request_post,
        taxi_persey_proxy,
        blackbox_service,
        mocked_time,
):
    response = await taxi_persey_proxy.post(
        'csrf_token_noauth', headers={'origin': 'localhost'},
    )
    assert response.status_code == 200
    assert 'yandexuid' in response.cookies

    body = response.json()
    assert 'sk' in body


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
async def test_csrf_token(
        mock_remote,
        request_post,
        taxi_persey_proxy,
        blackbox_service,
        mocked_time,
):
    now = utils.to_utc(dateutil.parser.parse(DATE))
    mocked_time.set(now)

    headers = SESSION_HEADERS.copy()
    del headers['X-CSRF-Token']

    await do_test_fail_csrf(mock_remote, request_post, URL_AUTH, headers)

    await do_test_ok(
        mock_remote, request_post, URL_AUTH, headers, method='get',
    )

    response = await taxi_persey_proxy.post('csrf_token', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'sk': CSRF_TOKEN, 'max-age-seconds': 600}
    resp_headers = response.headers
    assert resp_headers['Content-Type'] == 'application/json; charset=utf-8'
    assert resp_headers['X-Content-Type-Options'] == 'nosniff'
    assert resp_headers['X-Frame-Options'] == 'SAMEORIGIN'
    assert resp_headers['x-dns-prefetch-control'] == 'off'

    headers = SESSION_HEADERS
    await do_test_ok(mock_remote, request_post, URL_AUTH, headers)

    mocked_time.sleep(-1)
    await do_test_ok(mock_remote, request_post, URL_AUTH, headers)

    mocked_time.sleep(-20)
    await do_test_fail_csrf(mock_remote, request_post, URL_AUTH, headers)

    mocked_time.set(now)
    mocked_time.sleep(10)
    await do_test_ok(mock_remote, request_post, URL_AUTH, headers)

    mocked_time.sleep(589)
    await do_test_ok(mock_remote, request_post, URL_AUTH, headers)

    mocked_time.sleep(2)
    await do_test_fail_csrf(mock_remote, request_post, URL_AUTH, headers)


@pytest.mark.now(DATE)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
async def test_noauth_ok(mock_remote, request_post, taxi_persey_proxy):
    handler = mock_remote(url_path=URL_NOAUTH)
    response = await request_post(url_path=URL_NOAUTH, headers=EMPTY_HEADERS)

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    # 'X-Ya-User-Ticket-Provider' is ignored
    assert 'X-Yandex-UID' not in response_headers
    assert 'X-Yandex-Login' not in response_headers

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.now(DATE)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
async def test_noauth_fail(
        mock_remote, request_post, taxi_persey_proxy, blackbox_service,
):
    await do_test_fail(mock_remote, request_post, URL_AUTH, EMPTY_HEADERS)


@pytest.mark.parametrize('ok_', [True, False])
@pytest.mark.now(DATE)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_admin(
        mock_remote,
        request_post,
        taxi_persey_proxy,
        blackbox_service,
        mockserver,
        ok_,
):
    @mockserver.json_handler('/persey-labs/internal/v1/disp/user/check')
    def _mock_user_check(request):
        assert request.args['lab_entity_id'] == '123'
        assert request.args['login'] == 'login'

        return {'confirmed': ok_, 'labs': ['1', '2', '3']}

    if ok_:
        func = do_test_ok
    else:
        func = do_test_fail

    headers = SESSION_HEADERS.copy()
    headers['X-YaTaxi-Lab-Entity-Id'] = '123'

    await func(
        mock_remote,
        request_post,
        URL_AUTH_ADMIN,
        headers,
        exp_request_headers={
            'X-YaTaxi-Lab-Entity-Id': '123',
            'X-YaTaxi-Lab-Ids': '1,2,3',
        },
    )
