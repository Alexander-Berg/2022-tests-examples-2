import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/4.0/',
            'priority': 100,
            'rule_name': '/4.0/',
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
    'allowed-headers': ['a', 'b'],
    'exposed-headers': ['d', 'e'],
    'cache-max-age-seconds': 66,
}


def validate_cors_headers(response):
    origin = response.headers['Access-Control-Allow-Origin']
    assert origin == 'localhost'
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
    YA_AUTHPROXY_CORS=CORS, APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors(taxi_ya_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/prefix/4.0/test')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    await taxi_ya_authproxy.invalidate_caches()

    response = await taxi_ya_authproxy.post(
        '/4.0/test',
        data='123',
        bearer='token',
        headers={
            'Content-Type': 'application/json',
            'Origin': 'localhost',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )

    assert response.status_code == 200
    assert _test.has_calls
    validate_cors_headers(response)


TVM_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIlAMQZg:J8WYsLN9xPlsyTQ6vD8QtEVFsZ5y2'
    '--uZ09O1o6mUdFU_UfBeplkpHL6ZRtvPwV1-YarhTLggCZxTe0QqB1E2ALSsgqS'
    'ZA-76NYYhg0zmhlb0Tg5RGhWBPAaNZcWLRZ7h9s06YL9DPR27JYcJj0HVGLDtZE'
    'JRJeYfuExI78uwr8'
)


@pytest.mark.passport_token(token=TOKEN)
@pytest.mark.config(
    YA_AUTHPROXY_CORS=CORS, APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_cors_no_origin_with_tvm_service_ticket(
        taxi_ya_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/prefix/4.0/test')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    await taxi_ya_authproxy.invalidate_caches()

    response = await taxi_ya_authproxy.post(
        '/4.0/test',
        data='123',
        bearer='token',
        headers={
            # no Origin
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
            'X-Ya-Service-Ticket': TVM_SERVICE_TICKET,
        },
    )

    assert response.status_code == 200
    assert _test.has_calls
    assert 'Access-Control-Allow-Origin' not in response.headers
