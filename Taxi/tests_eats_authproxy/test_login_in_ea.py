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


@pytest.mark.parametrize(
    'ea_login_answer', ['TimeoutError', 'NetworkError', 'Response403', 'OK'],
)
@pytest.mark.parametrize('try_to_use_eater_from_eaters', [True, False])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.eater(
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_login_in_ea(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        ea_login_answer,
        taxi_config,
        try_to_use_eater_from_eaters,
):
    config = taxi_config.get('EATS_AUTHPROXY_FEATURE_FLAGS')
    config['try_to_use_eater_from_eaters'] = try_to_use_eater_from_eaters
    taxi_config.set_values({'EATS_AUTHPROXY_FEATURE_FLAGS': config})
    await taxi_eats_authproxy.invalidate_caches()

    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        if try_to_use_eater_from_eaters:
            assert (
                set(
                    x.strip()
                    for x in request.headers['X-Eats-User'].split(',')
                )
                == set(
                    [
                        'user_id=100',
                        'personal_phone_id=p100',
                        'personal_email_id=e100',
                        'eater_uuid=100',
                    ],
                )
            )
        else:
            assert 'X-Eats-User' not in request.headers

    @mockserver.json_handler('/eater-authorizer/v1/eater/sessions/login')
    def _mock_login(request):
        assert request.json['eater_id'] == '100'
        assert request.json['inner_session_id'] == 'in'

        if ea_login_answer == 'TimeoutError':
            raise mockserver.TimeoutError()
        elif ea_login_answer == 'NetworkError':
            raise mockserver.NetworkError()
        elif ea_login_answer == 'Response403':
            return mockserver.make_response('bad request', status=403)
        elif ea_login_answer == 'OK':
            pass

        return 'ok'

    response = await request_proxy('token', headers={'Origin': 'yandex.ru'})
    assert response.status_code == 200
    assert _mock_backend.times_called == 1
    assert _mock_login.times_called > 0  # retries
