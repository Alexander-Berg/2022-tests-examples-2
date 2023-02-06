import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test_route',
            'priority': 100,
            'rule_name': '/test_route',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/some_other_path',
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
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_rewrite(
        mock_core_eater, mock_eater_authorizer, mockserver, request_proxy,
):
    @mockserver.json_handler('/test_route/secret_path')
    def test_secret(request):
        pass

    @mockserver.json_handler('/some_other_path/secret_path')
    def test_public(request):
        pass

    response = await request_proxy(
        auth_method=None, url='/test_route/secret_path',
    )
    assert response.status_code == 200

    assert test_secret.times_called == 0
    assert test_public.times_called == 1
