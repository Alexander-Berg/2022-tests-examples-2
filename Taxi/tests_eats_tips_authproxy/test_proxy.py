# pylint: disable=unused-variable
import json

import dateutil.parser
import pytest

from testsuite import utils

NOW = '2018-01-22T00:00:00Z'

HEADERS = {'Cookie': 'Session_id=session1; yandexuid=123'}

RULES = [
    {
        'input': {'http-path-prefix': '/1.0/test/'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {'server-hosts': ['*']},
    },
    {
        'input': {'http-path-prefix': '/csrf_token'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {
            'proxy-401': True,
            'server-hosts': ['*'],
            'auth-type': 'session-csrf-token-generator',
        },
    },
]


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(EATS_TIPS_AUTHPROXY_ROUTE_RULES=RULES)
async def test_proxy(
        taxi_eats_tips_authproxy, mock_remote, mocked_time, blackbox_service,
):
    now = utils.to_utc(dateutil.parser.parse(NOW))
    mocked_time.set(now)
    response = await taxi_eats_tips_authproxy.post(
        '/csrf_token', headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'sk': 'KREK7iRRO0iOvBhm5H8CDM1U6KQ=:1516579200',
        'max-age-seconds': 600,
    }
    handler = mock_remote()
    # TODO: enable validation (see EASYT-375)
    # response = await taxi_eats_tips_authproxy.post(
    #     '/1.0/test/123',
    #     headers={
    #         **HEADERS,
    #     },
    #     data=json.dumps({}),
    # )
    # assert response.status_code == 401 # without CSRF token
    response = await taxi_eats_tips_authproxy.post(
        '/1.0/test/123',
        headers={**HEADERS, 'X-CSRF-Token': data['sk']},
        data=json.dumps({}),
    )
    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'
    assert response.status_code == 200
    assert response.json() == {'sentinel': True}


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(EATS_TIPS_AUTHPROXY_ROUTE_RULES=RULES)
async def test_is_yandex_staff(
        taxi_eats_tips_authproxy, mock_remote, mockserver,
):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '100'},
            'login': 'login',
            'login_id': 'login_id',
            'status': {'value': 'VALID'},
            'oauth': {
                'scope': 'yataxi:read yataxi:write yataxi:pay',
                'issue_time': '2018-05-30 12:34:56',
            },
            'aliases': {'16': 'uber_id', '10': 'phonish'},
            'dbfields': {'subscription.suid.669': '1'},  # means user is staff
            'emails': [],
            'user_ticket': 'test_user_ticket',
            'attributes': {'200': None, '1003': None, '1025': None},
        }

    handler = mock_remote()
    await taxi_eats_tips_authproxy.post(
        '/1.0/test/123',
        headers={
            **HEADERS,
            'X-CSRF-Token': 'KREK7iRRO0iOvBhm5H8CDM1U6KQ=:1516579200',
        },
        data=json.dumps({}),
    )
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Eats-Is-Yandex-Staff'] == '1'
