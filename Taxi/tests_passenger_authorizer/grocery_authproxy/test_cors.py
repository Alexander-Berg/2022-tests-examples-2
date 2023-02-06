import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/grocery/cookie',
            'priority': 100,
            'rule_name': 'with cookie',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 1000,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/cookie'},
        },
        'proxy': {
            'auth_type': 'oauth-or-session',
            'dbusers_authorization_allowed': False,
            'late_login_allowed': False,
            'parse_user_id_from_json_body': False,
            'webview_cookie_suffix': 'eats',
            'personal': {
                'bounded_uids': False,
                'eater_id': False,
                'eater_uuid': False,
                'staff_login': False,
                'eats_email_id': False,
                'eats_phone_id': False,
                'email_id': False,
                'phone_id': False,
            },
            'phone_validation': 'disabled',
            'proxy_401': False,
        },
        'rule_type': 'passenger-authorizer',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/grocery/',
            'priority': 100,
            'rule_name': '/grocery/',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 1000,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/prefix'},
        },
        'proxy': {
            'auth_type': 'oauth-or-session',
            'dbusers_authorization_allowed': False,
            'late_login_allowed': False,
            'parse_user_id_from_json_body': False,
            'personal': {
                'bounded_uids': False,
                'eater_id': False,
                'eater_uuid': False,
                'staff_login': False,
                'eats_email_id': False,
                'eats_phone_id': False,
                'email_id': False,
                'phone_id': False,
            },
            'phone_validation': 'disabled',
            'proxy_401': False,
        },
        'rule_type': 'passenger-authorizer',
    },
]
TOKEN = {'uid': '100'}
CORS = {
    'allowed-origins': ['localhost', 'example.com'],
    'allowed-origins-regex': ['other.*\\.com'],
    'allowed-headers': ['a', 'b'],
    'exposed-headers': ['d', 'e'],
    'cache-max-age-seconds': 66,
}
CORS_DISABLED = {**CORS, **{'disabled-hosts': ['*']}}


def validate_cors_headers(response, expected_origin):
    origin = response.headers['Access-Control-Allow-Origin']
    assert origin == expected_origin
    assert response.headers['Access-Control-Allow-Headers'] == 'a, b'
    assert response.headers['Access-Control-Expose-Headers'] == 'd, e'
    methods = set(response.headers['Access-Control-Allow-Methods'].split(', '))
    assert methods == set(
        ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'],
    )
    assert response.headers['Access-Control-Max-Age'] == '66'
    assert response.headers['Vary'] == 'Origin'


@pytest.mark.passport_token(token=TOKEN)
@pytest.mark.config(
    GROCERY_AUTHPROXY_CORS=CORS,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize(
    'origin', ['localhost', 'example.com', 'other.com', 'othersmth.com'],
)
async def test_cors(
        taxi_grocery_authproxy, blackbox_service, mockserver, origin,
):
    @mockserver.json_handler('/prefix/grocery/test')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    await taxi_grocery_authproxy.invalidate_caches()

    response = await taxi_grocery_authproxy.post(
        '/grocery/test',
        data='123',
        bearer='token',
        headers={
            'Content-Type': 'application/json',
            'Origin': origin,
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )

    assert response.status_code == 200
    assert _test.has_calls
    validate_cors_headers(response, origin)


AC_HEADERS = [
    'Access-Control-Allow-Origin',
    'Access-Control-Allow-Headers',
    'Access-Control-Expose-Headers',
    'Access-Control-Allow-Methods',
    'Access-Control-Max-Age',
]


@pytest.mark.passport_token(token=TOKEN)
@pytest.mark.config(
    GROCERY_AUTHPROXY_CORS=CORS,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize('cookies', [True, False])
async def test_cors_disabled(
        taxi_grocery_authproxy, blackbox_service, mockserver, cookies,
):
    @mockserver.json_handler('/prefix/grocery/test')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    await taxi_grocery_authproxy.invalidate_caches()

    headers = {
        'Content-Type': 'application/json',
        'X-YaTaxi-Skip-CORS-check': '1',
        'X-Forwarded-For': 'old-host',
        'X-YaTaxi-UserId': '12345',
        'X-Real-IP': '1.2.3.4',
        'Origin': 'localhost',
    }
    if cookies:
        headers['Cookie'] = 'webviewskipcorscheck=1'
    response = await taxi_grocery_authproxy.post(
        '/grocery/test', data='123', bearer='token', headers=headers,
    )

    assert response.status_code == 200
    assert _test.has_calls

    assert response.cookies == {}
    for header in AC_HEADERS:
        assert header not in response.headers


@pytest.mark.passport_token(token=TOKEN)
@pytest.mark.config(
    GROCERY_AUTHPROXY_CORS=CORS,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize('skip', [False, True])
async def test_cors_skip(
        taxi_grocery_authproxy, blackbox_service, mockserver, skip,
):
    @mockserver.json_handler('/cookie/grocery/cookie')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    await taxi_grocery_authproxy.invalidate_caches()

    headers = {
        'Content-Type': 'application/json',
        'X-Forwarded-For': 'old-host',
        'X-YaTaxi-UserId': '12345',
        'X-Real-IP': '1.2.3.4',
        'Origin': 'localhost',
    }
    if skip:
        headers['X-YaTaxi-Skip-CORS-check'] = '1'

    response = await taxi_grocery_authproxy.post(
        '/grocery/cookie', data='123', bearer='token', headers=headers,
    )

    assert response.status_code == 200
    assert _test.has_calls

    if skip:
        assert 'webviewskipcorscheck' in response.cookies
        for header in AC_HEADERS:
            assert header not in response.headers
    else:
        assert 'webviewskipcorscheck' not in response.cookies
        for header in AC_HEADERS:
            assert header in response.headers


@pytest.mark.parametrize('origin', ['sample.com', None, 'otherxcom'])
@pytest.mark.passport_token(token=TOKEN)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
    GROCERY_AUTHPROXY_CORS=CORS,
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors_other_origin(
        taxi_grocery_authproxy, blackbox_service, mockserver, origin,
):
    await taxi_grocery_authproxy.invalidate_caches()

    response = await taxi_grocery_authproxy.post(
        '/grocery/test',
        data='123',
        bearer='token',
        headers={
            'Content-Type': 'application/json',
            'Origin': origin,
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )

    assert response.status_code == 401
    assert 'Access-Control-Expose-Headers' not in response.headers
    assert 'Access-Control-Allow-Origin' not in response.headers
    assert 'Vary' not in response.headers


@pytest.mark.config(
    GROCERY_AUTHPROXY_CORS=CORS,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors_options(
        taxi_grocery_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/prefix/grocery/test')
    def _test(request):
        assert False

    await taxi_grocery_authproxy.invalidate_caches()

    # No token is passed
    response = await taxi_grocery_authproxy.options(
        '/grocery/test', headers={'Origin': 'localhost'},
    )

    assert not _test.has_calls
    assert response.status_code == 204
    validate_cors_headers(response, 'localhost')


@pytest.mark.config(GROCERY_AUTHPROXY_CORS=CORS_DISABLED)
async def test_no_origin(taxi_grocery_authproxy, mockserver):
    await taxi_grocery_authproxy.invalidate_caches()

    # No Origin
    response = await taxi_grocery_authproxy.get('/grocery/test')

    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'No route for URL'}
