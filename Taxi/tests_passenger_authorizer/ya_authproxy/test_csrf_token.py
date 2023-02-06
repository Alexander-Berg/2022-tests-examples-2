import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/4.0/startup',
            'priority': 100,
            'rule_name': '/4.0/startup',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 1000,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'user-id-generator',
            'dbusers_authorization_allowed': False,
            'late_login_allowed': True,
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
            'proxy_401': True,
        },
        'rule_type': 'passenger-authorizer',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/4.0/',
            'priority': 200,
            'rule_name': '/4.0/',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 1000,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
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
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/csrf_token',
            'priority': 300,
            'rule_name': '/csrf_token',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 1000,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'csrf-token-generator',
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


async def do_request(taxi_ya_authproxy, url, headers=None):
    final_headers = {
        'Cookie': 'Session_id=session1; yandexuid=123',
        'Content-Type': 'application/json',
        'X-Forwarded-For': 'old-host',
        'X-YaTaxi-UserId': '12345',
        'X-Real-IP': '1.2.3.4',
        'Origin': 'localhost',
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 9; CLT-L29 Build/HUAWE'
            'ICLT-L29; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Version/4.0 Chrome/73.0.3683.90 Mobile Safari/537.36 '
            'uber-kz/3.85.1.72959 Android/9 (HUAWEI; CLT-L29)'
        ),
    }
    if headers:
        final_headers.update(headers)
        for key, value in headers.items():
            if value is None:
                del final_headers[key]
    return await taxi_ya_authproxy.post(url, data='{}', headers=final_headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_no_csrf(taxi_ya_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/test')
    def _test(request):
        return 'xxx'

    response = await do_request(taxi_ya_authproxy, url='4.0/test')
    assert response.status_code == 200
    assert response.text == '"xxx"'


async def do_test_csrf(
        taxi_ya_authproxy, blackbox_service, mockserver, headers, url,
):
    @mockserver.json_handler('/' + url)
    def _test(request):
        return 'xxx'

    response = await do_request(taxi_ya_authproxy, url=url, headers=headers)
    assert response.status_code == 401
    assert response.json()['code'] == 'INVALID_CSRF_TOKEN'

    response = await do_request(
        taxi_ya_authproxy, url='csrf_token', headers=headers,
    )
    assert response.status_code == 200
    assert 'sk' in response.json()
    token = response.json()['sk']

    headers['X-Csrf-Token'] = token

    response = await do_request(taxi_ya_authproxy, url=url, headers=headers)
    assert response.status_code == 200
    assert response.json() == 'xxx'


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    YA_AUTHPROXY_CSRF_TOKEN_SETTINGS={
        'validation-enabled': True,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_csrf(taxi_ya_authproxy, blackbox_service, mockserver):
    await do_test_csrf(
        taxi_ya_authproxy, blackbox_service, mockserver, {}, '4.0/test',
    )


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    YA_AUTHPROXY_CSRF_TOKEN_SETTINGS={
        'validation-enabled': True,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_csrf_user_id_generator(
        taxi_ya_authproxy, blackbox_service, mockserver,
):
    await do_test_csrf(
        taxi_ya_authproxy,
        blackbox_service,
        mockserver,
        {'X-YaTaxi-UserId': None},
        '4.0/startup',
    )
