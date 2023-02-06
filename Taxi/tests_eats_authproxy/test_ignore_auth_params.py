import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test_ignore_auth_params',
            'priority': 100,
            'rule_name': '/test_ignore_auth_params',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'no-auth',
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


@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_ignore_auth_params(
        mock_core_eater, mock_eater_authorizer, mockserver, request_proxy,
):
    @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
    def _mock_core_find_by_passport_uid(req):
        pass

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eaters_find_by_passport_uid(req):
        pass

    @mockserver.json_handler('/eats-core-eater/find-by-id')
    def _mock_core_find_by_id(req):
        pass

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters_find_by_id(req):
        pass

    @mockserver.json_handler('/test_ignore_auth_params')
    def _test_ignore_auth_params(request):
        assert 'PHPSESSID' not in request.cookies
        assert 'X-Eats-Session' not in request.headers
        assert 'Authorization' not in request.headers

    response = await request_proxy(
        auth_method='token', url='/test_ignore_auth_params',
    )
    assert response.status_code == 200

    assert _test_ignore_auth_params.times_called == 1

    assert _mock_core_find_by_passport_uid.times_called == 0
    assert _mock_eaters_find_by_passport_uid.times_called == 0
    assert _mock_core_find_by_id.times_called == 0
    assert _mock_eaters_find_by_id.times_called == 0
