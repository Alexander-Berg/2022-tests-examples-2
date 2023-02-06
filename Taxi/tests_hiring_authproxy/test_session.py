# pylint: disable=import-error
import dateutil.parser
import pytest

from client_blackbox import mock_blackbox  # noqa: F403 F401, I100, I202

from testsuite import utils

CSRF_TOKEN = 'KREK7iRRO0iOvBhm5H8CDM1U6KQ=:1516579200'
DATE = '2018-01-22T00:00:00Z'

SESSION_HEADERS = {
    'Cookie': 'Session_id=session1; yandexuid=123',
    'X-CSRF-Token': CSRF_TOKEN,
}

TEAM_SESSION_HEADERS = {
    'Cookie': 'Session_id=session1; yandexuid=123',
    'X-CSRF-Token': CSRF_TOKEN,
    'Host': 'hiring-api.yandex-team.ru',
}

ANON_CSRF_TOKEN = 'xGXjjRI03tqf6P01Nsnj4q+GaGc=:1516579200'

EMPTY_HEADERS = {'X-CSRF-Token': ANON_CSRF_TOKEN, 'Cookie': 'yandexuid=123'}

URL_AUTH = 'hiring/v1/auth'
URL_NOAUTH = 'hiring/v1/noauth'

REMOTE_RESPONSE = {'sentinel': True}

CONFIG = [
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
        'input': {'http-path-prefix': '/hiring/v1/int-api'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'server-hosts': ['*'],
            'auth': 'session',
            'path-rewrite-strict': '',
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

SESSION = {
    'uid': '100',
    'emails': [mock_blackbox.make_email('smth@drvrc.com')],
}


async def do_test_ok(
        mock_remote, request_post, url_path, headers, method='post',
):
    handler = mock_remote(url_path=url_path)
    response = await request_post(
        url_path=url_path, headers=headers, method=method,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


async def do_test_fail(mock_remote, request_post, url_path, headers):
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
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_ok(
        mock_remote, request_post, taxi_hiring_authproxy, blackbox_service,
):
    await do_test_ok(mock_remote, request_post, URL_AUTH, SESSION_HEADERS)


@pytest.mark.now(DATE)
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize(
    'headers',
    [
        pytest.param(
            SESSION_HEADERS,
            id='yandex',
            marks=pytest.mark.passport_session(session1=SESSION),
        ),
        pytest.param(
            TEAM_SESSION_HEADERS,
            id='yandex-team',
            marks=pytest.mark.passport_team_session(session1=SESSION),
        ),
    ],
)
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_delete_prefix_in_request(
        mock_remote,
        request_post,
        taxi_hiring_authproxy,
        blackbox_service,
        headers,
        mockserver,
):
    method = 'post'
    url_path = '/hiring/v1/int-api/v1/paymentmethods'

    handler = mock_remote(url_path='v1/paymentmethods')
    response = await request_post(
        url_path=url_path, headers=SESSION_HEADERS, method=method,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.now(DATE)
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_session_fail(
        mock_remote, request_post, taxi_hiring_authproxy, blackbox_service,
):
    await do_test_fail(mock_remote, request_post, URL_AUTH, SESSION_HEADERS)


@pytest.mark.now(DATE)
@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_csrf_token_noyandexuid(
        mock_remote,
        request_post,
        taxi_hiring_authproxy,
        blackbox_service,
        mocked_time,
):
    response = await taxi_hiring_authproxy.post(
        'csrf_token_noauth', headers={'origin': 'localhost'},
    )
    assert response.status_code == 200
    assert 'yandexuid' in response.cookies

    body = response.json()
    assert 'sk' in body


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_csrf_token(
        mock_remote,
        request_post,
        taxi_hiring_authproxy,
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

    response = await taxi_hiring_authproxy.post('csrf_token', headers=headers)
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
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_noauth_ok(mock_remote, request_post, taxi_hiring_authproxy):
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
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_noauth_fail(
        mock_remote, request_post, taxi_hiring_authproxy, blackbox_service,
):
    await do_test_fail(mock_remote, request_post, URL_AUTH, EMPTY_HEADERS)
