import pytest


AM_RULE = {
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
}


@pytest.mark.passport_token(token={'uid': '100'})
@pytest.mark.config(APPLICATION_MAP_BRAND={'__default__': 'yataxi'})
@pytest.mark.routing_rules([AM_RULE])
async def test_happy_path(
        taxi_grocery_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/prefix/grocery/test')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    response = await taxi_grocery_authproxy.post(
        '/grocery/test',
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
    assert response.json() == {'id': '123'}

    assert _test.has_calls


@pytest.mark.passport_token(
    token={'uid': '100', 'scope': 'market:content-api mobile:all market:pay'},
)
@pytest.mark.config(
    GROCERY_AUTHPROXY_MARKET_PASSPORT_SCOPES=[
        'market:content-api',
        'mobile:all',
        'market:pay',
    ],
    APPLICATION_MAP_BRAND={'__default__': 'yataxi'},
)
@pytest.mark.routing_rules([AM_RULE])
async def test_market_scope(
        taxi_grocery_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/prefix/grocery/test')
    def _test(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        return {'id': '123'}

    response = await taxi_grocery_authproxy.post(
        '/grocery/test',
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
    assert response.json() == {'id': '123'}

    assert _test.has_calls
