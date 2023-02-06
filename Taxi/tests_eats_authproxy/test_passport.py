import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test401',
            'priority': 100,
            'rule_name': '/test401',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test401',
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
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
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
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/launch',
            'priority': 100,
            'rule_name': '/launch',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/launch',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session-eater-id-generator',
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
            'prefix': '/scopes_test',
            'priority': 100,
            'rule_name': '/scopes_test',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/scopes_test',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': ['has_rule'],
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
            'prefix': '/scopes_test2',
            'priority': 100,
            'rule_name': '/scopes_test2',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/scopes_test2',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': ['one_of_two', 'two_of_two'],
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


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={'id': '200'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_eater_id_mismatch(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert False

    response = await request_proxy(auth_method)
    assert response.status_code == 401


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={}, i100={})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_unknown_uid_unknown_eater_id(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert False

    response = await request_proxy(auth_method)
    assert response.status_code == 401


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(
    u100={},
    i100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_unknown_uid_known_eater_id(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        return 'ok'

    response = await request_proxy(
        auth_method, headers={'Origin': 'yandex.ru'},
    )
    assert response.status_code == 200
    assert response.json() == 'ok'


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_eater_locked(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
    def _mock_find_by_passport_uid(request):
        return mockserver.make_response(
            json={'code': 'eater_locked', 'message': 'eater not found'},
            headers={'X-YaTaxi-Error-Code': 'eater_locked'},
            status=404,
        )

    @mockserver.json_handler('launch')
    def _mock_backend(request):
        assert False

    response = await request_proxy(auth_method)
    assert response.status_code == 429


@pytest.mark.passport_token(token={'uid': '100', 'scope': 'bad-scope'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={'id': 'eater'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_bad_token_scope(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert False

    @mockserver.json_handler('/eater-authorizer/v1/eater/sessions/login')
    def _mock_login(request):
        return {}

    response = await request_proxy('token')
    assert response.status_code == 401


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.eater(u100={'id': 'eater'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_bad_auth(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert False

    response = await request_proxy(auth_method)
    assert response.status_code == 401


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_happy_path(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'in'
        assert request.headers['X-Eats-Session'] == 'in'
        assert request.headers['X-YaTaxi-Session'] == 'eats:in'

        if auth_method == 'session':
            flags = ['credentials=eats-passport-session']
        elif auth_method == 'token':
            flags = ['credentials=eats-passport-token']
        else:
            assert False
        flags.append('phonish')

        assert (
            set(x.strip() for x in request.headers['X-YaTaxi-User'].split(','))
            == set(
                [
                    'eats_user_id=100',
                    'personal_phone_id=p100',
                    'personal_email_id=e100',
                ],
            )
        )
        assert (
            set(x.strip() for x in request.headers['X-Eats-User'].split(','))
            == set(
                [
                    'user_id=100',
                    'personal_phone_id=p100',
                    'personal_email_id=e100',
                    'eater_uuid=100',
                ],
            )
        )
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            flags,
        )
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-UID'] == '100'

        return 'ok'

    response = await request_proxy(
        auth_method, headers={'Origin': 'yandex.ru'},
    )
    assert response.json() == 'ok'
    assert response.status_code == 200


def make_passport_marks(account_type):
    return (
        pytest.mark.passport_token(
            token={
                'uid': '100',
                'scope': 'eats:all',
                'account_type': account_type,
            },
        ),
        pytest.mark.passport_session(
            session={'uid': '100', 'account_type': account_type},
        ),
    )


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.parametrize(
    'account_type',
    [
        pytest.param(account_type, marks=make_passport_marks(account_type))
        for account_type in ['neophonish', 'lite', 'social', 'pdd']
    ],
)
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_account_type(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        account_type,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'in'
        assert request.headers['X-Eats-Session'] == 'in'
        assert request.headers['X-YaTaxi-Session'] == 'eats:in'

        if auth_method == 'session':
            flags = ['credentials=eats-passport-session']
        elif auth_method == 'token':
            flags = ['credentials=eats-passport-token']
        else:
            assert False
        flags.append(account_type)
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            flags,
        )
        return 'ok'

    response = await request_proxy(
        auth_method, headers={'Origin': 'yandex.ru'},
    )
    assert response.json() == 'ok'
    assert response.status_code == 200
    assert _mock_backend.next_call


@pytest.mark.passport_session(session={'uid': '100', 'account_type': 'narod'})
@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_unknown_account_type(
        taxi_eats_authproxy,
        blackbox_service,
        mock_eater_authorizer,
        mock_core_eater,
        request_proxy,
        mockserver,
):
    response = await request_proxy(auth_method='session')
    assert response.status_code == 401
    assert response.json()['code'] == 'unknown_passport_account_type'


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.config(
    EATS_AUTHPROXY_PASSPORT_MODE={
        'token-enabled': False,
        'session-enabled': False,
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_passport_disabled(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test401/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'in'
        assert request.headers['X-Eats-Session'] == 'in'
        assert request.headers['X-YaTaxi-Session'] == 'eats:in'

        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            ['credentials=eats-session', 'no-login'],
        )
        assert 'X-Ya-User-Ticket' not in request.headers
        assert 'X-Yandex-Login' not in request.headers
        assert 'X-Login-Id' not in request.headers
        assert 'X-Yandex-UID' not in request.headers

        return 'ok'

    response = await request_proxy(auth_method, url='test401/123')
    assert response.status_code == 200
    assert response.json() == 'ok'


@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.config(
    EATS_AUTHPROXY_PASSPORT_MODE={
        'token-enabled': False,
        'session-enabled': True,
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_header_flags_ignore_session(
        taxi_eats_authproxy, mockserver, mock_eater_authorizer, request_proxy,
):
    @mockserver.json_handler('test401/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'in'
        assert 'X-Yandex-UID' not in request.headers
        return {'id': '123'}

    response = await request_proxy(
        auth_method='session',
        headers={'X-YaTaxi-EAP-Flags': 'ignore-session'},
        url='test401/123',
    )
    assert response.status_code == 200

    assert _mock_backend.times_called == 1


@pytest.mark.parametrize(
    'passport_scopes,response_code',
    [(['has_rule'], 200), (['has_unlimited_access'], 200), (['no_rule'], 401)],
)
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={}, i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.config(
    EATS_AUTHPROXY_FEATURE_FLAGS={'use_new_access_scheme': False},
    EATS_AUTHPROXY_PASSPORT_SCOPES=['has_unlimited_access'],
)
async def test_passport_scopes_old(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        passport_scopes,
        response_code,
):
    blackbox_service.set_token_info(
        'token', uid='100', scope=' '.join(passport_scopes),
    )

    @mockserver.json_handler('scopes_test/123')
    def _mock_backend(request):
        return 'ok'

    response = await request_proxy(
        'token',
        headers={'X-Device-Id': 'some_device_id'},
        url='scopes_test/123',
    )

    assert response.status_code == response_code
    if response_code < 400:
        assert response.json() == 'ok'


@pytest.mark.parametrize(
    'passport_scopes,response_code',
    [(['has_rule'], 200), (['has_unlimited_access'], 200), (['no_rule'], 401)],
)
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={}, i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.config(
    EATS_AUTHPROXY_UNLIMITED_ACCESS_SCOPES=['has_unlimited_access'],
)
async def test_passport_scopes(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        taxi_config,
        passport_scopes,
        response_code,
):
    blackbox_service.set_token_info(
        'token', uid='100', scope=' '.join(passport_scopes),
    )

    @mockserver.json_handler('scopes_test/123')
    def _mock_backend(request):
        return 'ok'

    response = await request_proxy(
        'token',
        headers={'X-Device-Id': 'some_device_id'},
        url='scopes_test/123',
    )

    assert response.status_code == response_code
    if response_code < 400:
        assert response.json() == 'ok'


@pytest.mark.parametrize(
    'passport_scopes,response_code',
    [(['one_of_two'], 401), (['one_of_two', 'two_of_two'], 200)],
)
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={}, i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_passport_scopes_in_rules(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        taxi_config,
        passport_scopes,
        response_code,
):
    blackbox_service.set_token_info(
        'token', uid='100', scope=' '.join(passport_scopes),
    )

    @mockserver.json_handler('scopes_test2/123')
    def _mock_backend(request):
        return 'ok'

    response = await request_proxy(
        'token',
        headers={'X-Device-Id': 'some_device_id'},
        url='scopes_test2/123',
    )

    assert response.status_code == response_code
    if response_code < 400:
        assert response.json() == 'ok'


@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(u100={}, i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.config(
    EATS_AUTHPROXY_UNLIMITED_ACCESS_SCOPES=['has_unlimited_access'],
    EATS_AUTHPROXY_INTEGRATIONS_BLACK_LIST=['forbidden'],
)
async def test_passport_forbidden(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        taxi_config,
):
    blackbox_service.set_token_info(
        'token',
        uid='100',
        scope='has_unlimited_access',
        client_id='forbidden',
    )

    @mockserver.json_handler('scopes_test/123')
    def _mock_backend(request):
        return 'ok'

    response = await request_proxy(
        'token',
        headers={'X-Device-Id': 'some_device_id'},
        url='scopes_test/123',
    )

    assert response.status_code == 403


@pytest.mark.config(EATS_AUTHPROXY_FEATURE_FLAGS={'force_login_in_ea': False})
@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.eater(
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_empty_session_id(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'in'
        assert request.headers['X-Eats-Session'] == 'in'
        assert request.headers['X-YaTaxi-Session'] == 'eats:in'

        if auth_method == 'session':
            flags = ['credentials=eats-passport-session']
        elif auth_method == 'token':
            flags = ['credentials=eats-passport-token']
        else:
            assert False
        flags.append('phonish')
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == set(
            flags,
        )
        return 'ok'

    response = await request_proxy(auth_method)

    assert response.status_code == 401
