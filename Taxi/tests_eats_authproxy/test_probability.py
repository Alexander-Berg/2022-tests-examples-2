import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test/route',
            'priority': 10,
            'rule_name': '/test/route',
            'probability': 30,
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test/route',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/30'},
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test/route',
            'priority': 20,
            'rule_name': '/test/route',
            'probability': 70,
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test/route',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/70'},
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test/route',
            'priority': 30,
            'rule_name': '/test/route',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test/route',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/undef'},
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_probability_percent_30_70(
        mock_core_eater, mock_eater_authorizer, mockserver, request_proxy,
):
    stats = {'call-test-30': 0, 'call-test-70': 0}

    @mockserver.json_handler('/30/test/route')
    def _test_30(request):
        stats['call-test-30'] += 1

    @mockserver.json_handler('/70/test/route')
    def _test_70(request):
        stats['call-test-70'] += 1

    for _ in range(200):
        response = await request_proxy(auth_method=None, url='test/route')
        assert response.status_code == 200

    assert stats['call-test-30'] > 0
    assert stats['call-test-70'] > 0
    assert stats['call-test-70'] + stats['call-test-30'] == 200
    assert stats['call-test-70'] > stats['call-test-30']


AM_ADDITIONAL_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/additional/test/route',
            'priority': 10,
            'rule_name': '/additional/test/route',
            'probability': 0,
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/additional/test/route',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/0'},
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/additional/test/route',
            'priority': 20,
            'rule_name': '/additional/test/route',
            'probability': 100,
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/additional/test/route',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/100'},
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/additional/test/route',
            'priority': 30,
            'rule_name': '/additional/test/route',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/additional/test/route',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': '/undef'},
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={'id': '100'})
@pytest.mark.routing_rules(AM_ADDITIONAL_ROUTE_RULES)
async def test_probability_percent_0_100(
        mock_core_eater, mock_eater_authorizer, mockserver, request_proxy,
):
    stats = {'call-test-0': 0, 'call-test-100': 0}

    @mockserver.json_handler('/0/additional/test/route')
    def _test_0(request):
        stats['call-test-0'] += 1

    @mockserver.json_handler('/100/additional/test/route')
    def _test_100(request):
        stats['call-test-100'] += 1

    for _ in range(100):
        response = await request_proxy(
            auth_method=None, url='additional/test/route',
        )
        assert response.status_code == 200

    assert stats['call-test-0'] == 0
    assert stats['call-test-100'] == 100
