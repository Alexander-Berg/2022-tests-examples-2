import pytest

AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/eats/',
            'priority': 100,
            'rule_name': '/eats/',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/eats/',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
]
SESSION = {'uid': '100'}
CORS = {
    'allowed-origins': ['localhost', 'example.com'],
    'allowed-headers': ['a', 'b'],
    'cache-max-age-seconds': 66,
}
CORS_WITH_DISABLED = {
    'allowed-origins': [],
    'allowed-headers': ['a', 'b'],
    'cache-max-age-seconds': 66,
    'disabled-hosts': ['disabled'],
}
CORS_STAR = {
    'allowed-origins': [],
    'allowed-headers': ['a', 'b'],
    'cache-max-age-seconds': 66,
    'disabled-hosts': ['*'],
}


@pytest.mark.passport_session(session=SESSION)
@pytest.mark.config(EATS_AUTHPROXY_CORS=CORS)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors(
        taxi_eats_authproxy,
        _request,
        _mock_remote,
        blackbox_service,
        mockserver,
):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        return {
            'inner_session_id': 'inner',
            'outer_session_id': 'outer',
            'session_type': 'native',
        }

    await taxi_eats_authproxy.invalidate_caches()

    url_path = 'eats/v1/auth'
    handler = _mock_remote(url_path=url_path)

    response = await _request(url_path=url_path)

    assert handler.has_calls
    assert response.status_code == 200
    validate_cors_headers(response)


@pytest.mark.parametrize('cors', [CORS_WITH_DISABLED, CORS_STAR])
@pytest.mark.parametrize('origin', ['example.net', None])
@pytest.mark.passport_session(session=SESSION)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors_disabled(
        taxi_eats_authproxy,
        _request,
        _mock_remote,
        blackbox_service,
        cors,
        taxi_config,
        origin,
        mockserver,
):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        return {
            'inner_session_id': 'inner',
            'outer_session_id': 'outer',
            'session_type': 'native',
        }

    taxi_config.set_values({'EATS_AUTHPROXY_CORS': cors})

    await taxi_eats_authproxy.invalidate_caches()

    url_path = 'eats/v1/auth'
    handler = _mock_remote(url_path=url_path)

    headers = {}
    headers['X-Host'] = 'disabled'
    headers['Origin'] = origin
    response = await _request(url_path=url_path, headers=headers)

    assert handler.has_calls
    assert response.status_code == 200


@pytest.mark.passport_session(session=SESSION)
@pytest.mark.config(EATS_AUTHPROXY_CORS=CORS)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors_failure(
        taxi_eats_authproxy, _request, _mock_remote, blackbox_service,
):
    await taxi_eats_authproxy.invalidate_caches()

    url_path = 'eats/v1/auth'
    handler = _mock_remote(url_path=url_path)

    headers = {}
    headers['X-Host'] = 'disabled'
    headers['Origin'] = 'example.net'
    response = await _request(url_path=url_path, headers=headers)

    assert not handler.has_calls
    assert response.status_code == 401


def validate_cors_headers(response):
    origin = response.headers['Access-Control-Allow-Origin']
    assert origin == 'localhost'
    assert response.headers['Access-Control-Allow-Headers'] == 'a, b'
    methods = set(response.headers['Access-Control-Allow-Methods'].split(', '))
    assert methods == set(
        ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'],
    )
    assert response.headers['Access-Control-Max-Age'] == '66'
