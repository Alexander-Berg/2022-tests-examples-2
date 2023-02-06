import json

import pytest

URL_PATH = '/partner/v1/auth/smth'
REMOTE_RESPONSE = {'sentinel': True}
UNAUTORIZED_RESPONSE = {
    'code': 'unauthorized',
    'message': 'Not authorized request',
}

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

HEADERS_AUTH_OK_4 = {
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
        'proxy': {'logins': ['login1', 'login2'], 'server-hosts': ['*']},
    },
]

CONFIG_2 = [
    {
        'input': {'http-path-prefix': URL_PATH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {'logins': ['login2'], 'server-hosts': ['*']},
    },
]

CONFIG_3 = [
    {
        'input': {'http-path-prefix': URL_PATH},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {'logins': [], 'server-hosts': ['*']},
    },
]

DISABLED_WHITELIST = [
    {'partner': 'login1'},
    {'partner': 'login2'},
    {'partner': 'login3'},
]

WHITELIST = [
    {'partner': 'login1', 'ip_addresses': ['192.168.40.2', '192.168.15.15']},
    {
        'partner': 'login2',
        'ip_addresses': [
            '2021:0301:cda1:22c4:b2b2:1c3d:2571:abcd',
            '1111:1314:2222:abcd:3333:4444:5555:6666',
        ],
    },
    {'partner': 'login3'},
]


@pytest.mark.config(
    PARTNER_AUTHPROXY_ROUTE_RULES=CONFIG,
    PARTNER_AUTHPROXY_IP_LISTS=DISABLED_WHITELIST,
)
@pytest.mark.parametrize(
    'headers', [HEADERS_AUTH_OK, HEADERS_AUTH_OK_2, HEADERS_AUTH_OK_3],
)
async def test_apikey_ok(
        mock_remote, request_post, taxi_partner_authproxy, headers,
):
    await taxi_partner_authproxy.invalidate_caches()

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


@pytest.mark.config(
    PARTNER_AUTHPROXY_ROUTE_RULES=CONFIG_2,
    PARTNER_AUTHPROXY_IP_LISTS=DISABLED_WHITELIST,
)
async def test_apikey_forbidden_login(
        mock_remote, request_post, taxi_partner_authproxy,
):
    await taxi_partner_authproxy.invalidate_caches()

    handler = mock_remote()
    response = await request_post(headers=HEADERS_AUTH_OK)

    assert not handler.has_calls

    assert response.json() == UNAUTORIZED_RESPONSE
    assert not response.cookies

    response = await request_post(headers=HEADERS_AUTH_OK_3)
    assert response.json() == REMOTE_RESPONSE
    assert response.status_code == 200


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
@pytest.mark.config(
    PARTNER_AUTHPROXY_ROUTE_RULES=CONFIG,
    PARTNER_AUTHPROXY_IP_LISTS=DISABLED_WHITELIST,
)
async def test_apikey_bad(
        mock_remote, request_post, taxi_partner_authproxy, headers,
):
    handler = mock_remote()
    response = await request_post(headers=headers)

    assert not handler.has_calls

    assert response.status_code == 401
    assert response.json() == UNAUTORIZED_RESPONSE
    assert not response.cookies


@pytest.mark.config(
    PARTNER_AUTHPROXY_ROUTE_RULES=CONFIG_3,
    PARTNER_AUTHPROXY_IP_LISTS=DISABLED_WHITELIST,
)
async def test_apikey_no_logins(
        mock_remote, request_post, taxi_partner_authproxy,
):
    await taxi_partner_authproxy.invalidate_caches()

    handler = mock_remote()
    response = await request_post(headers=HEADERS_AUTH_OK)

    assert not handler.has_calls

    assert response.json() == UNAUTORIZED_RESPONSE
    assert not response.cookies


@pytest.mark.config(
    PARTNER_AUTHPROXY_ROUTE_RULES=CONFIG,
    PARTNER_AUTHPROXY_IP_LISTS=DISABLED_WHITELIST,
)
async def test_metrics(
        mock_remote,
        request_post,
        taxi_partner_authproxy,
        taxi_partner_authproxy_monitor,
):
    await taxi_partner_authproxy.post(
        '/tests/control', data=json.dumps({'reset_metrics': True}),
    )

    handler = mock_remote()

    headers_array = [HEADERS_AUTH_OK, HEADERS_AUTH_OK_2, HEADERS_AUTH_OK_3]
    for headers in headers_array:
        response = await request_post(headers=headers)
        assert handler.has_calls
        assert response.status_code == 200

    metric = await taxi_partner_authproxy_monitor.get_metric('proxy')
    assert metric['auth-result']['apikey-ok'] == 3
    assert metric['auth-result']['apikey-fail'] == 0

    headers_array = [
        HEADERS_AUTH_BAD_NO_LOGIN,
        HEADERS_AUTH_BAD_NO_APIKEY,
        HEADERS_AUTH_BAD_NO_HEADERS,
        HEADERS_AUTH_BAD_WRONG_LOGIN,
        HEADERS_AUTH_BAD_FORBIDDEN_LOGIN,
    ]
    for headers in headers_array:
        response = await request_post(headers=headers)
        assert handler.has_calls
        assert response.status_code == 401

    metric = await taxi_partner_authproxy_monitor.get_metric('proxy')
    assert metric['auth-result']['apikey-ok'] == 3
    assert metric['auth-result']['apikey-fail'] == 5


@pytest.mark.config(
    PARTNER_AUTHPROXY_ROUTE_RULES=CONFIG, PARTNER_AUTHPROXY_IP_LISTS=WHITELIST,
)
async def test_apikey_whitelisting(
        mock_remote, request_post, taxi_partner_authproxy,
):
    await taxi_partner_authproxy.invalidate_caches()

    handler = mock_remote()
    headers = HEADERS_AUTH_OK

    headers.update({'X-Real-IP': '192.168.40.2'})
    response = await request_post(headers=headers)
    assert handler.has_calls
    assert response.status_code == 200

    headers.update({'X-Real-IP': '192.168.40.1'})
    response = await request_post(headers=headers)
    assert handler.has_calls
    assert response.status_code == 401

    headers.update({'X-Real-IP': '192.168.15.15'})
    response = await request_post(headers=headers)
    assert response.status_code == 200

    headers.update({'X-Real-IP': '192.168.16.15'})
    response = await request_post(headers=headers)
    assert response.status_code == 401

    headers.update({'X-Real-IP': '192.168.16.16'})
    response = await request_post(headers=headers)
    assert handler.has_calls
    assert response.status_code == 401

    headers = HEADERS_AUTH_OK_4
    headers.update({'X-Real-IP': '2021:0301:cda1:22c4:b2b2:1c3d:2571:abcd'})
    response = await request_post(headers=headers)
    assert response.status_code == 200

    headers.update({'X-Real-IP': '1111:0000:2222:7777:3333:4444:5555:6666'})
    response = await request_post(headers=headers)
    assert response.status_code == 401

    headers.update({'X-Real-IP': '1111:1314:2222:abcd:3333:4444:5555:6666'})
    response = await request_post(headers=headers)
    assert response.status_code == 200

    headers.update({'X-Real-IP': '1111:3333:2122:4567:3333:4444:5555:6666'})
    response = await request_post(headers=headers)
    assert handler.has_calls
    assert response.status_code == 401
