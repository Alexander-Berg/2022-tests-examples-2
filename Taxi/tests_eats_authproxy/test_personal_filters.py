import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/only_eater_id',
            'priority': 100,
            'rule_name': '/only_eater_id',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/only_eater_id',
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
                'eater_uuid': False,
                'email_id': False,
                'phone_id': False,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/only_phone_id',
            'priority': 100,
            'rule_name': '/only_phone_id',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/only_phone_id',
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
                'eater_id': False,
                'eater_uuid': False,
                'email_id': False,
                'phone_id': True,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/only_email_id',
            'priority': 100,
            'rule_name': '/only_email_id',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/only_email_id',
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
                'eater_id': False,
                'eater_uuid': False,
                'email_id': True,
                'phone_id': False,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/only_uuid',
            'priority': 100,
            'rule_name': '/only_uuid',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/only_uuid',
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
                'eater_id': False,
                'eater_uuid': True,
                'email_id': False,
                'phone_id': False,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/no_personal',
            'priority': 100,
            'rule_name': '/no_personal',
        },
        'output': {
            'attempts': 1,
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
                'eater_id': False,
                'eater_uuid': False,
                'email_id': False,
                'phone_id': False,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
        'uuid': 'u100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize(
    'path,has_eater,has_phone,has_email,has_uuid',
    [
        pytest.param(
            '/only_eater_id', True, False, False, False, id='only_eater_id',
        ),
        pytest.param(
            '/only_phone_id', False, True, False, False, id='only_phone_id',
        ),
        pytest.param(
            '/only_email_id', False, False, True, False, id='only_email_id',
        ),
        pytest.param('/only_uuid', False, False, False, True, id='only_uuid'),
    ],
)
async def test_personal_filter(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        path,
        has_eater,
        has_phone,
        has_email,
        has_uuid,
):
    def check_request(request):
        assert 'X-Eats-User' in request.headers

        if has_eater:
            assert 'user_id=100' in request.headers['X-Eats-User']
        else:
            assert 'user_id' not in request.headers['X-Eats-User']

        if has_phone:
            assert 'personal_phone_id=p100' in request.headers['X-Eats-User']
        else:
            assert 'personal_phone_id' not in request.headers['X-Eats-User']

        if has_email:
            assert 'personal_email_id=e100' in request.headers['X-Eats-User']
        else:
            assert 'personal_email_id' not in request.headers['X-Eats-User']

        if has_uuid:
            assert 'eater_uuid=u100' in request.headers['X-Eats-User']
        else:
            assert 'eater_uuid' not in request.headers['X-Eats-User']

    @mockserver.json_handler('/only_eater_id')
    def _mock_only_eater_id(request):
        check_request(request)

    @mockserver.json_handler('/only_phone_id')
    def _mock_only_phone_id(request):
        check_request(request)

    @mockserver.json_handler('/only_email_id')
    def _mock_only_email_id(request):
        check_request(request)

    @mockserver.json_handler('/only_uuid')
    def _mock_only_uuid(request):
        check_request(request)

    response = await request_proxy('token', url=path)
    assert response.status_code == 200


@pytest.mark.eater_session(outer={'inner': 'in', 'partner_user_id': '100'})
@pytest.mark.eater(i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_partner_personal_filter(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
):
    @mockserver.json_handler('/only_eater_id')
    def _mock_only_eater_id(request):
        assert 'X-Eats-User' in request.headers
        assert 'partner_user_id=100' in request.headers['X-Eats-User']

    response = await request_proxy('legacy', url='/only_eater_id')
    assert response.status_code == 200


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_no_personal_filter(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        blackbox_service,
        request_proxy,
):
    @mockserver.json_handler('/no_personal')
    def _mock_only_eater_id(request):
        assert 'X-Eats-User' not in request.headers

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

    response = await request_proxy('token', url='/no_personal')
    assert response.status_code == 200

    assert _mock_core_find_by_passport_uid.times_called == 0
    assert _mock_eaters_find_by_passport_uid.times_called == 0
    assert _mock_core_find_by_id.times_called == 0
    assert _mock_eaters_find_by_id.times_called == 0


@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_no_personal_filter_no_eater(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        blackbox_service,
        request_proxy,
):
    @mockserver.json_handler('/no_personal')
    def _mock_only_eater_id(request):
        assert 'X-Eats-User' not in request.headers

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

    response = await request_proxy('token', url='/no_personal')
    assert response.status_code == 401

    assert _mock_core_find_by_passport_uid.times_called == 0
    assert _mock_eaters_find_by_passport_uid.times_called == 0
    assert _mock_core_find_by_id.times_called == 0
    assert _mock_eaters_find_by_id.times_called == 0
