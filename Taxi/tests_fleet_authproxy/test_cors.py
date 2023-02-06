import pytest


ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/fleet/'},
        'proxy': {'server-hosts': ['*'], 'park-id-required': False},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]
SESSION = {'uid': '100', 'scope': 'taxi-fleet:all'}
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
SESSION_HEADERS_TEAM = {
    'Cookie': 'Session_id=session1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
}


@pytest.mark.passport_team_session(session1=SESSION)
@pytest.mark.config(
    FLEET_AUTHPROXY_ROUTE_RULES=ROUTE_RULES, FLEET_AUTHPROXY_CORS=CORS,
)
async def test_cors(
        taxi_fleet_authproxy, _request, _mock_remote, blackbox_service,
):
    await taxi_fleet_authproxy.invalidate_caches()

    url_path = 'fleet/v1/auth'
    handler = _mock_remote(url_path=url_path)

    response = await _request(url_path=url_path, headers=SESSION_HEADERS_TEAM)

    assert handler.has_calls
    assert response.status_code == 200
    validate_cors_headers(response)


@pytest.mark.parametrize('cors', [CORS_WITH_DISABLED, CORS_STAR])
@pytest.mark.parametrize('origin', ['example.net', None])
@pytest.mark.passport_team_session(session1=SESSION)
@pytest.mark.config(FLEET_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_cors_disabled(
        taxi_fleet_authproxy,
        _request,
        _mock_remote,
        blackbox_service,
        cors,
        taxi_config,
        origin,
):
    taxi_config.set_values({'FLEET_AUTHPROXY_CORS': cors})

    await taxi_fleet_authproxy.invalidate_caches()

    url_path = 'fleet/v1/auth'
    handler = _mock_remote(url_path=url_path)

    headers = SESSION_HEADERS_TEAM.copy()
    headers['X-Host'] = 'disabled'
    headers['Origin'] = origin
    response = await _request(url_path=url_path, headers=headers)

    assert handler.has_calls
    assert response.status_code == 200


@pytest.mark.passport_team_session(session1=SESSION)
@pytest.mark.config(
    FLEET_AUTHPROXY_ROUTE_RULES=ROUTE_RULES, FLEET_AUTHPROXY_CORS=CORS,
)
async def test_cors_failure(
        taxi_fleet_authproxy, _request, _mock_remote, blackbox_service,
):
    await taxi_fleet_authproxy.invalidate_caches()

    url_path = 'fleet/v1/auth'
    handler = _mock_remote(url_path=url_path)

    headers = SESSION_HEADERS_TEAM.copy()
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
