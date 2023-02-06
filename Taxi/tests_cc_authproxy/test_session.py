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
    'Host': 'cc-api.yandex-team.ru',
}

ANON_CSRF_TOKEN = 'xGXjjRI03tqf6P01Nsnj4q+GaGc=:1516579200'

EMPTY_HEADERS = {'X-CSRF-Token': ANON_CSRF_TOKEN, 'Cookie': 'yandexuid=123'}

URL_AUTH = 'cc/v1/auth'
URL_AUTH_NO_DOMAIN_RESTRICTION = 'cc/v1/auth-no-domain-restriction'
URL_NOAUTH = 'cc/v1/noauth'

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
        'input': {'http-path-prefix': '/cc/v1/int-api'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'server-hosts': ['*'],
            'auth': 'session',
            'path-rewrite-strict': '',
        },
    },
    {
        'input': {'http-path-prefix': '/' + URL_AUTH_NO_DOMAIN_RESTRICTION},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'server-hosts': ['*'],
            'auth': 'session-no-domain-restriction',
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

SESSION_BAD_EMAIL = {
    'uid': '100',
    'emails': [mock_blackbox.make_email('smth@dexample.com')],
}


async def do_test_ok(
        mock_remote,
        request_post,
        url_path,
        headers,
        default_response,
        method='post',
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
    assert response.json() == default_response
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
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
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
async def test_session_ok(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        default_response,
        headers,
):
    await do_test_ok(
        mock_remote, request_post, URL_AUTH, headers, default_response,
    )


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
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
async def test_delete_prefix_in_request(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        default_response,
        headers,
        mockserver,
):
    method = 'post'
    url_path = '/cc/v1/int-api/v1/paymentmethods'

    handler = mock_remote(url_path='v1/paymentmethods')
    response = await request_post(
        url_path=url_path, headers=headers, method=method,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'

    assert response.status_code == 200
    assert response.json() == default_response
    assert not response.cookies


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize(
    'headers',
    [
        pytest.param(SESSION_HEADERS, id='yandex'),
        pytest.param(TEAM_SESSION_HEADERS, id='yandex-team'),
        pytest.param(
            SESSION_HEADERS,
            id='yandex bad email',
            marks=pytest.mark.passport_session(session1=SESSION_BAD_EMAIL),
        ),
        pytest.param(
            TEAM_SESSION_HEADERS,
            id='yandex-team bad email',
            marks=pytest.mark.passport_team_session(
                session1=SESSION_BAD_EMAIL,
            ),
        ),
        pytest.param(
            SESSION_HEADERS,
            id='yandex, cross request',
            marks=pytest.mark.passport_team_session(session1=SESSION),
        ),
        pytest.param(
            TEAM_SESSION_HEADERS,
            id='yandex-team, cross request',
            marks=pytest.mark.passport_session(session1=SESSION),
        ),
    ],
)
async def test_session_bad_session(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        headers,
):
    await do_test_fail(mock_remote, request_post, URL_AUTH, headers)


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(session1=SESSION)
async def test_session_ok_ndr(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        default_response,
):
    await do_test_ok(
        mock_remote,
        request_post,
        URL_AUTH_NO_DOMAIN_RESTRICTION,
        SESSION_HEADERS,
        default_response,
    )


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_session_bad_session_ndr(
        mock_remote, request_post, taxi_cc_authproxy, blackbox_service,
):
    await do_test_fail(
        mock_remote,
        request_post,
        URL_AUTH_NO_DOMAIN_RESTRICTION,
        SESSION_HEADERS,
    )


@pytest.mark.now(DATE)
@pytest.mark.passport_session(session1=SESSION_BAD_EMAIL)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_session_bad_email_ndr(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        default_response,
):
    await do_test_ok(
        mock_remote,
        request_post,
        URL_AUTH_NO_DOMAIN_RESTRICTION,
        SESSION_HEADERS,
        default_response,
    )


@pytest.mark.now(DATE)
@pytest.mark.passport_session(session1=SESSION)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_csrf_token_noyandexuid(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        mocked_time,
):
    response = await taxi_cc_authproxy.post(
        'csrf_token_noauth', headers={'origin': 'localhost'},
    )
    assert response.status_code == 200
    assert 'yandexuid' in response.cookies

    body = response.json()
    assert 'sk' in body


@pytest.mark.passport_session(session1=SESSION)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_csrf_token(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        mocked_time,
        default_response,
):
    now = utils.to_utc(dateutil.parser.parse(DATE))
    mocked_time.set(now)

    headers = SESSION_HEADERS.copy()
    del headers['X-CSRF-Token']

    await do_test_fail_csrf(mock_remote, request_post, URL_AUTH, headers)

    await do_test_ok(
        mock_remote,
        request_post,
        URL_AUTH,
        headers,
        default_response,
        method='get',
    )

    response = await taxi_cc_authproxy.post('csrf_token', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'sk': CSRF_TOKEN, 'max-age-seconds': 600}
    resp_headers = response.headers
    assert resp_headers['Content-Type'] == 'application/json; charset=utf-8'
    assert resp_headers['X-Content-Type-Options'] == 'nosniff'
    assert resp_headers['X-Frame-Options'] == 'SAMEORIGIN'
    assert resp_headers['x-dns-prefetch-control'] == 'off'

    headers = SESSION_HEADERS
    await do_test_ok(
        mock_remote, request_post, URL_AUTH, headers, default_response,
    )

    mocked_time.sleep(-1)
    await do_test_ok(
        mock_remote, request_post, URL_AUTH, headers, default_response,
    )

    mocked_time.sleep(-20)
    await do_test_fail_csrf(mock_remote, request_post, URL_AUTH, headers)

    mocked_time.set(now)
    mocked_time.sleep(10)
    await do_test_ok(
        mock_remote, request_post, URL_AUTH, headers, default_response,
    )

    mocked_time.sleep(589)
    await do_test_ok(
        mock_remote, request_post, URL_AUTH, headers, default_response,
    )

    mocked_time.sleep(2)
    await do_test_fail_csrf(mock_remote, request_post, URL_AUTH, headers)


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_noauth_ok(
        mock_remote, request_post, taxi_cc_authproxy, default_response,
):
    handler = mock_remote(url_path=URL_NOAUTH)
    response = await request_post(url_path=URL_NOAUTH, headers=EMPTY_HEADERS)

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert 'X-Yandex-UID' not in response_headers
    assert 'X-Yandex-Login' not in response_headers

    assert response.status_code == 200
    assert response.json() == default_response
    assert not response.cookies


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_noauth_fail(
        mock_remote, request_post, taxi_cc_authproxy, blackbox_service,
):
    await do_test_fail(mock_remote, request_post, URL_AUTH, EMPTY_HEADERS)


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(session1=SESSION)
async def test_provider_headers(
        mock_remote,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        default_response,
):
    handler = mock_remote(url_path=URL_AUTH)
    response = await request_post(
        url_path=URL_AUTH, headers=SESSION_HEADERS, method='post',
    )

    assert handler.has_calls
    request_headers = handler.next_call()['request'].headers
    assert request_headers['X-Yandex-UID'] == '100'
    assert request_headers['X-Yandex-Login'] == 'login'
    assert request_headers['X-YaTaxi-Provider'] == 'yandex'
    assert request_headers['X-YaTaxi-ProviderUserId'] == '100'

    assert response.status_code == 200
    assert response.json() == default_response
    assert not response.cookies


@pytest.mark.now(DATE)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(session1=SESSION)
@pytest.mark.parametrize(
    ('response_code', 'response_body', 'expected_audit_request'),
    [
        pytest.param(
            404,
            {'a': 'b'},
            None,
            id='404',
            marks=pytest.mark.config(
                CC_AUTHPROXY_AUDIT_RULES={
                    'enabled': True,
                    'rules': [
                        {
                            'path': '/' + URL_AUTH,
                            'method': 'POST',
                            'action': 'auth_action',
                            'object_id_retrieve_settings': {
                                'path': 'a',
                                'storage': 'response',
                            },
                        },
                    ],
                    'system_name': 'cc-authproxy',
                },
            ),
        ),
        pytest.param(
            200,
            {'a': 'b'},
            None,
            id='no rule',
            marks=pytest.mark.config(
                CC_AUTHPROXY_AUDIT_RULES={
                    'enabled': True,
                    'rules': [],
                    'system_name': 'cc-authproxy',
                },
            ),
        ),
        pytest.param(
            200,
            {'a': 'b'},
            None,
            id='not enabled',
            marks=pytest.mark.config(
                CC_AUTHPROXY_AUDIT_RULES={
                    'enabled': False,
                    'rules': [
                        {
                            'path': '/' + URL_AUTH,
                            'method': 'POST',
                            'action': 'auth_action',
                            'object_id_retrieve_settings': {
                                'path': 'a',
                                'storage': 'response',
                            },
                        },
                    ],
                    'system_name': 'cc-authproxy',
                },
            ),
        ),
        pytest.param(
            200,
            {'a': 'b'},
            {
                'action': 'auth_action',
                'arguments': {
                    'data': '"123"',  # from DEFAULT_REQUEST
                    'request': {
                        'endpoint': '/cc/v1/auth',  # /URL_AUTH
                        'service_name': 'mock',  # tvm-service from CONFIG
                    },
                    'response': {'a': 'b'},  # response_body
                },
                'login': '100',  # from SESSION
                'object_id': 'b',  # from response_body
                'request_id': '122333',
                'system_name': 'cc-authproxy',  # from CC_AUTHPROXY_AUDIT_RULES
            },
            id='Audit - ok',
            marks=pytest.mark.config(
                CC_AUTHPROXY_AUDIT_RULES={
                    'enabled': True,
                    'rules': [
                        {
                            'path': '/' + URL_AUTH,
                            'method': 'POST',
                            'action': 'auth_action',
                            'object_id_retrieve_settings': {
                                'path': 'a',
                                'storage': 'response',
                            },
                        },
                    ],
                    'system_name': 'cc-authproxy',
                },
            ),
        ),
        pytest.param(
            200,
            {'a': 'b'},
            {
                'action': 'auth_action',
                'arguments': {
                    'data': '"123"',  # from DEFAULT_REQUEST
                    'request': {
                        'endpoint': '/cc/v1/auth',  # /URL_AUTH
                        'service_name': 'mock',  # tvm-service from CONFIG
                    },
                    'response': {'a': 'b'},  # response_body
                },
                'login': '100',  # from SESSION
                # 'object_id': 'b',  no object_id
                'request_id': '122333',
                'system_name': 'cc-authproxy',  # from CC_AUTHPROXY_AUDIT_RULES
            },
            id='no object_id',
            marks=pytest.mark.config(
                CC_AUTHPROXY_AUDIT_RULES={
                    'enabled': True,
                    'rules': [
                        {
                            'path': '/' + URL_AUTH,
                            'method': 'POST',
                            'action': 'auth_action',
                            'object_id_retrieve_settings': {
                                'path': 'nonexistent',
                                'storage': 'response',
                            },
                        },
                    ],
                    'system_name': 'cc-authproxy',
                },
            ),
        ),
    ],
)
async def test_audit(
        mock_remote,
        mock_audit,
        request_post,
        taxi_cc_authproxy,
        blackbox_service,
        response_code,
        response_body,
        expected_audit_request,
):
    audit_handler = mock_audit()
    remote_handler = mock_remote(
        url_path=URL_AUTH,
        response_code=response_code,
        response_body=response_body,
    )
    response = await request_post(
        url_path=URL_AUTH, headers=SESSION_HEADERS, method='post',
    )

    assert remote_handler.has_calls
    assert response.status_code == response_code
    assert response.json() == response_body

    if expected_audit_request is not None:
        assert audit_handler.has_calls
        audit_request = audit_handler.next_call()['request'].json
        del audit_request['timestamp']
        assert audit_request == expected_audit_request
    else:
        assert not audit_handler.has_calls
