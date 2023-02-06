import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test',
            'priority': 100,
            'rule_name': '/test',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test',
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

FEATURE_FLAGS = {'eaters_fetch_strategy': 'eaters_with_fallback'}


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.config(EATS_AUTHPROXY_FEATURE_FLAGS=FEATURE_FLAGS)
@pytest.mark.eater(
    empty=False,
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.parametrize('use_fallback', [False, True])
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_find_eater_fallbacks(
        mockserver,
        taxi_eats_authproxy,
        mock_eater_authorizer,
        blackbox_service,
        mock_eaters_search,
        request_proxy,
        use_fallback,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        return {}

    @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
    def _mock_core_find_by_passport_uid(req):
        if not use_fallback:
            assert False

        return mock_eaters_search('u100')

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eaters_find_by_passport_uid(req):
        return mock_eaters_search('empty' if use_fallback else 'u100')

    @mockserver.json_handler('/eats-core-eater/find-by-id')
    def _mock_core_find_by_id(req):
        if not use_fallback:
            assert False

        return mock_eaters_search('u100')

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters_find_by_id(req):
        return mock_eaters_search('empty' if use_fallback else 'u100')

    response = await request_proxy('session', headers={'Origin': 'yandex.ru'})
    assert response.status_code == 200
