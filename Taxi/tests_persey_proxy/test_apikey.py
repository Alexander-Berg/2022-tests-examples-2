import pytest

URL_PATH = '/persey/v1/auth/smth'
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
        'proxy': {'proxy-401': False, 'server-hosts': ['*'], 'auth': 'apikey'},
    },
]


@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize(
    'headers', [HEADERS_AUTH_OK, HEADERS_AUTH_OK_2, HEADERS_AUTH_OK_3],
)
async def test_apikey_ok(
        mock_remote, request_post, taxi_persey_proxy, headers,
):
    await taxi_persey_proxy.invalidate_caches()

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


@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize('origin,ok_', [('localhost', True), ('evil', False)])
async def test_cors(mock_remote, request_post, taxi_persey_proxy, origin, ok_):
    await taxi_persey_proxy.invalidate_caches()

    headers = HEADERS_AUTH_OK.copy()
    headers['Origin'] = origin

    handler = mock_remote()
    response = await request_post(headers=headers)

    if ok_:
        assert handler.has_calls

        # CORS
        assert response.headers['Access-Control-Allow-Credentials'] == 'true'
        assert response.headers['Access-Control-Allow-Headers'] == ''
        assert response.headers['Access-Control-Allow-Origin'] == origin
        methods = set(
            response.headers['Access-Control-Allow-Methods'].split(', '),
        )
        assert methods == set(
            ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'],
        )
        assert response.headers['Access-Control-Max-Age'] == '60'
    else:
        assert not handler.has_calls
        assert response.status_code == 401


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
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=CONFIG)
async def test_apikey_bad(
        mock_remote, request_post, taxi_persey_proxy, headers,
):
    handler = mock_remote()
    response = await request_post(headers=headers)

    assert not handler.has_calls

    assert response.status_code == 401
    assert response.json() != REMOTE_RESPONSE
    assert not response.cookies

    # CORS
    assert response.headers['Access-Control-Allow-Credentials'] == 'true'
    assert response.headers['Access-Control-Allow-Headers'] == ''
    assert response.headers['Access-Control-Max-Age'] == '60'
