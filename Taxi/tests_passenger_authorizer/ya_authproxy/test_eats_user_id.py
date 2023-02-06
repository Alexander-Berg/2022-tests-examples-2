import pytest


AM_ROUTING_RULE = {
    'input': {
        'description': '(imported from taxi config)',
        'maintained_by': 'common_components',
        'prefix': '/4.0/proxy',
        'priority': 100,
        'rule_name': '/4.0/',
    },
    'output': {
        'attempts': 1,
        'timeout_ms': 1000,
        'tvm_service': 'mock',
        'upstream': {'$mockserver': '/upstream'},
    },
    'proxy': {
        'auth_type': 'oauth-or-session',
        'personal': {
            'eater_id': True,
            'eater_uuid': True,
            'staff_login': False,
            'eats_email_id': False,
            'eats_phone_id': False,
        },
    },
    'rule_type': 'passenger-authorizer',
}


@pytest.mark.routing_rules([AM_ROUTING_RULE])
@pytest.mark.passport_token(token={'uid': '100'})
@pytest.mark.parametrize(
    'eats_user_id,fallback_request_to_eats_core',
    [(None, True), ('eats-11', False)],
)
async def test_proxy_pa(
        taxi_ya_authproxy,
        blackbox_service,
        eats_user_id,
        fallback_request_to_eats_core,
        mockserver,
):
    @mockserver.json_handler('eats-core-eater/find-by-passport-uid')
    def mock_eats_core(request):
        if eats_user_id:
            return {
                'eater': {
                    'id': eats_user_id,
                    'uuid': 'abcdef',
                    'created_at': '2019-12-31T10:59:59+03:00',
                    'updated_at': '2019-12-31T10:59:59+03:00',
                },
            }
        return mockserver.make_response(
            headers={'X-YaTaxi-Error-Code': 'code'},
            json={'code': 'eater_not_found', 'message': 'not found'},
            status=404,
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def mock_eats_eaters(request):
        if eats_user_id:
            return {
                'eater': {
                    'id': eats_user_id,
                    'uuid': 'abcdef',
                    'created_at': '2019-12-31T10:59:59+03:00',
                    'updated_at': '2019-12-31T10:59:59+03:00',
                },
            }
        return mockserver.make_response(
            headers={'X-YaTaxi-Error-Code': 'code'},
            json={'code': 'eater_not_found', 'message': 'not found'},
            status=404,
        )

    @mockserver.json_handler('/upstream/4.0/proxy')
    def mock_upstream(request):
        flags = request.headers.get('X-YaTaxi-User', '')
        if eats_user_id is not None:
            assert f'eats_user_id={eats_user_id}' in flags
        else:
            assert 'eats_user_id' not in flags

        return {'id': '123'}

    response = await taxi_ya_authproxy.get(
        '/4.0/proxy',
        bearer='token',
        headers={'Origin': 'localhost', 'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert 'set-cookie' not in response.headers
    assert mock_upstream.times_called == 1

    fallback_times_called = 1 if fallback_request_to_eats_core else 0
    assert mock_eats_core.times_called == fallback_times_called
    assert mock_eats_eaters.times_called == 1
