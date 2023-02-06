import pytest

URL_PATH = '/hiring/v1/auth/smth'
REMOTE_RESPONSE = {'sentinel': True}

HEADERS_AUTH_OK = {
    'X-External-API-Key': 'key1',
    'X-External-Service': 'login1',
}

HEADERS_AUTH_OK_2 = {
    'X-External-API-Key': 'key2',
    'X-External-Service': 'login1',
}

HEADERS_AUTH_OK_3 = {
    'X-External-API-Key': 'key3',
    'X-External-Service': 'login2',
}

HEADERS_AUTH_BAD_NO_HEADERS: dict = {}

HEADERS_AUTH_BAD_NO_LOGIN = {'X-External-API-Key': 'key3'}

HEADERS_AUTH_BAD_NO_APIKEY = {'X-External-Service': 'login2'}

HEADERS_AUTH_BAD_WRONG_LOGIN = {
    'X-External-API-Key': 'key3',
    'X-External-Service': 'login1',
}

HEADERS_AUTH_BAD_FORBIDDEN_LOGIN = {
    'X-External-API-Key': 'key4',
    'X-External-Service': 'login2',
}


CONFIG = [
    {
        'input': {'http-path-prefix': URL_PATH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'logins': ['login1', 'login2'],
            'server-hosts': ['*'],
        },
    },
]

CONFIG_2 = [
    {
        'input': {'http-path-prefix': URL_PATH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': False,
            'logins': ['login2'],
            'server-hosts': ['*'],
        },
    },
]

CONFIG_3 = [
    {
        'input': {'http-path-prefix': URL_PATH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {'proxy-401': False, 'logins': [], 'server-hosts': ['*']},
    },
]


@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize(
    'headers', [HEADERS_AUTH_OK, HEADERS_AUTH_OK_2, HEADERS_AUTH_OK_3],
)
async def test_apikey_ok(
        mock_remote, request_post, taxi_hiring_authproxy, headers,
):
    await taxi_hiring_authproxy.invalidate_caches()

    handler = mock_remote()
    response = await request_post(headers=headers)

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-External-Service'] == (
        headers['X-External-Service']
    )

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG_2)
async def test_apikey_forbidden_login(
        mock_remote, request_post, taxi_hiring_authproxy,
):
    await taxi_hiring_authproxy.invalidate_caches()

    handler = mock_remote()
    response = await request_post(headers=HEADERS_AUTH_OK)

    assert not handler.has_calls

    assert response.status_code == 401
    assert not response.cookies

    response2 = await request_post(headers=HEADERS_AUTH_OK_3)
    assert response2.status_code == 200


@pytest.mark.parametrize(
    'headers',
    [
        HEADERS_AUTH_BAD_NO_LOGIN,
        HEADERS_AUTH_BAD_NO_APIKEY,
        HEADERS_AUTH_BAD_NO_HEADERS,
        HEADERS_AUTH_BAD_WRONG_LOGIN,
        HEADERS_AUTH_BAD_FORBIDDEN_LOGIN,
    ],
)
@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_apikey_bad(
        mock_remote, request_post, taxi_hiring_authproxy, headers,
):
    handler = mock_remote()
    response = await request_post(headers=headers)

    assert not handler.has_calls

    assert response.status_code == 401
    assert response.json() != REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.config(HIRING_AUTHPROXY_ROUTE_RULES=CONFIG_3)
async def test_apikey_no_logins(
        mock_remote, request_post, taxi_hiring_authproxy,
):
    await taxi_hiring_authproxy.invalidate_caches()

    handler = mock_remote()
    response = await request_post(headers=HEADERS_AUTH_OK)

    assert not handler.has_calls

    assert response.status_code == 500
    assert not response.cookies
