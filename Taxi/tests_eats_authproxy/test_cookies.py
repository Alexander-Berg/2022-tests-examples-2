import json

import pytest

USER_AGENT_NATIVE = 'ios-eats(0.0.1)'
SESSION_TYPE_NATIVE = 'native'
APPLICATION_NAME_NATIVE = 'web'
BRAND_NATIVE = 'yataxi'
DEVICE_ID = 'default_device_id'


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/4.0/cookie',
            'priority': 100,
            'rule_name': '/4.0/cookie',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/4.0/cookie',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': True,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/4.0/cookie-suffix',
            'priority': 100,
            'rule_name': '/4.0/cookie-suffix',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/4.0/cookie-suffix',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': True,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={'id': '100'}, u100={'id': '100'})
@pytest.mark.config(
    EATS_AUTHPROXY_PASSPORT_MODE={
        'token-enabled': True,
        'session-enabled': True,
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_token(
        taxi_eats_authproxy,
        blackbox_service,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        request_proxy,
):
    @mockserver.json_handler('/4.0/cookie')
    def _test(request):
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '100'}

    blackbox_service.set_token_info('token', uid='100', scope='eats:all')

    response = await taxi_eats_authproxy.post(
        '/4.0/cookie',
        data=json.dumps({}),
        bearer='token',
        headers={'Cookie': 'PHPSESSID=outer', 'X-Eats-Session': 'outer'},
    )

    assert response.json() == {'id': '100'}
    assert response.status_code == 200

    expected_cookie_attributes = {
        'path': '/',
        'max-age': '60',
        'secure': True,
        'httponly': True,
    }
    _check_response_cookies(
        response, {'webviewtoken': ('token', expected_cookie_attributes)},
    )


@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={'id': '100'}, u100={'id': '100'})
@pytest.mark.config(
    EATS_AUTHPROXY_PASSPORT_MODE={
        'token-enabled': True,
        'session-enabled': True,
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_token_getting(
        taxi_eats_authproxy,
        blackbox_service,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        request_proxy,
):
    @mockserver.json_handler('/4.0/cookie')
    def _test(request):
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '100'}

    blackbox_service.set_token_info('token', uid='100', scope='eats:all')

    response = await taxi_eats_authproxy.post(
        '/4.0/cookie',
        data=json.dumps({}),
        headers={
            'Cookie': 'PHPSESSID=outer;webviewtoken=token',
            'X-Eats-Session': 'outer',
        },
    )

    assert response.json() == {'id': '100'}
    assert response.status_code == 200

    expected_cookie_attributes = {
        'path': '/',
        'max-age': '60',
        'secure': True,
        'httponly': True,
    }
    _check_response_cookies(
        response, {'webviewtoken': ('token', expected_cookie_attributes)},
    )


def _check_response_cookies(response, expected_cookies):
    for key, expected_cookie in expected_cookies.items():
        assert key in response.cookies
        value, attributes = expected_cookie
        cookie = response.cookies[key]
        assert cookie.value == value
        for attr_key, attr_val in attributes.items():
            assert cookie[attr_key] == attr_val
