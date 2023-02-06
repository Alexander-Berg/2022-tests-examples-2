import dateutil.parser
import pytest

from testsuite import utils


DATE = '2018-01-22T00:00:00Z'
ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/fleet/'},
        'proxy': {'server-hosts': ['*']},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
    {
        'input': {'http-path-prefix': '/fleet/csrf_token'},
        'proxy': {
            'auth-type': 'session-csrf-token-generator',
            'server-hosts': ['*'],
        },
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]
FLEET_AUTHPROXY_CSRF_TOKEN_SETTINGS = {
    'validation-enabled': True,
    'max-age-seconds': 600,
    'delta-seconds': 10,
}
FLEET_AUTHPROXY_ACCESS_RULES = [
    {
        'prefix': '/fleet/',
        'access_rules': [{'path': '/fleet/v1/auth', 'method': 'POST'}],
    },
]
CSRF_TOKEN = 'KREK7iRRO0iOvBhm5H8CDM1U6KQ=:1516579200'
SESSION = {'uid': '100', 'scope': 'taxi-fleet:all'}
SESSION_HEADERS_TEAM = {
    'Cookie': 'Session_id=session1; yandexuid=123',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-CSRF-Token': CSRF_TOKEN,
}


@pytest.mark.passport_team_session(session1=SESSION)
@pytest.mark.config(
    FLEET_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    FLEET_AUTHPROXY_CSRF_TOKEN_SETTINGS=FLEET_AUTHPROXY_CSRF_TOKEN_SETTINGS,
    FLEET_AUTHPROXY_ACCESS_RULES=FLEET_AUTHPROXY_ACCESS_RULES,
)
async def test_csrf_token(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        mocked_time,
):
    now = utils.to_utc(dateutil.parser.parse(DATE))
    mocked_time.set(now)

    headers = SESSION_HEADERS_TEAM.copy()
    del headers['X-CSRF-Token']

    url_path = 'fleet/v1/auth'
    handler = _mock_remote(url_path=url_path)
    response = await _request(url_path=url_path, headers=headers)

    assert not handler.has_calls
    assert response.status_code == 401
    assert not response.cookies
    assert response.json()['code'] == 'INVALID_CSRF_TOKEN'

    response = await _request('fleet/csrf_token', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'sk': CSRF_TOKEN, 'max-age-seconds': 600}

    response = await _request(
        url_path=url_path,
        headers={**SESSION_HEADERS_TEAM, 'X-Park-Id': 'park'},
    )
    assert response.status_code == 200
