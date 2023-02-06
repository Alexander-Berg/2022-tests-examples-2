import pytest

import utils


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
            'prefix': '/non_auth_launch',
            'priority': 100,
            'rule_name': '/non_auth_launch',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/non_auth_launch',
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
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_eater_id_generator_wo_passport_credentials(
        taxi_eats_authproxy,
        mock_core_eater,
        mock_eater_authorizer,
        request_proxy,
):
    response = await request_proxy(auth_method=None, url='launch')
    assert response.status_code == 401


@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_eater_id_generator_wo_passport_credentials_no_auth(
        mockserver, mock_core_eater, mock_eater_authorizer, request_proxy,
):
    @mockserver.json_handler('non_auth_launch')
    def _mock_backend(request):
        assert request.headers['X-YaTaxi-User'] == 'eats_user_id=100'
        assert request.headers['X-Eats-User'] == 'user_id=100'
        assert request.headers['X-Eats-Session'] == 'in'
        assert request.headers['X-YaTaxi-Session'] == 'eats:in'

        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == {
            'credentials=eats-session',
        }
        assert 'X-Ya-User-Ticket' not in request.headers
        assert 'X-Yandex-Login' not in request.headers
        assert 'X-Login-Id' not in request.headers
        assert 'X-Yandex-UID' not in request.headers

    response = await request_proxy(auth_method=None, url='non_auth_launch')
    assert response.status_code == 200


@pytest.mark.eater_session(__empty={'inner': 'anon'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_eater_id_generator_wo_any_credentials_no_auth(
        mockserver, mock_eater_authorizer, request_proxy,
):
    @mockserver.json_handler('non_auth_launch')
    def _mock_backend(request):
        assert 'X-YaTaxi-User' not in request.headers
        assert 'X-Eats-User' not in request.headers
        assert request.headers['X-Eats-Session'] == 'anon'
        assert request.headers['X-YaTaxi-Session'] == 'eats:anon'

        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == {
            'credentials=eats-session',
            'no-login',
        }
        assert 'X-Ya-User-Ticket' not in request.headers
        assert 'X-Yandex-Login' not in request.headers
        assert 'X-Login-Id' not in request.headers
        assert 'X-Yandex-UID' not in request.headers

    response = await request_proxy(
        auth_method=None, url='non_auth_launch', no_session=True,
    )
    assert response.status_code == 200


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_eater_id_generator_wo_any_credentials_no_auth_no_session(
        mockserver, request_proxy,
):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        return {
            'inner_session_id': 'inner',
            'outer_session_id': 'outer',
            'session_type': 'native',
        }

    @mockserver.json_handler('non_auth_launch')
    def _mock_backend(request):
        assert 'X-YaTaxi-User' not in request.headers
        assert 'X-Eats-User' not in request.headers
        assert 'X-Eats-Session' in request.headers
        assert 'X-YaTaxi-Session' in request.headers

        assert 'X-YaTaxi-Pass-Flags' in request.headers
        assert 'X-Ya-User-Ticket' not in request.headers
        assert 'X-Yandex-Login' not in request.headers
        assert 'X-Login-Id' not in request.headers
        assert 'X-Yandex-UID' not in request.headers

    response = await request_proxy(
        auth_method=None, url='non_auth_launch', no_session=True,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.eater(u100={})
@pytest.mark.eater_session(__empty={'inner': 'anon'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_generator_unknown_uid(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
):
    @mockserver.json_handler('launch')
    def _mock_backend(request):
        assert 'X-YaTaxi-User' not in request.headers
        assert 'X-Eats-User' not in request.headers
        assert request.headers['X-Eats-Session'] == 'anon'
        assert request.headers['X-YaTaxi-Session'] == 'eats:anon'

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
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-UID'] == '100'

    response = await request_proxy(
        auth_method,
        url='launch',
        no_session=True,
        headers={'Origin': 'yandex.ru'},
    )
    assert response.status_code == 200


@pytest.mark.parametrize('auth_method', ['token', 'session'])
@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.passport_session(session={'uid': '100'})
@pytest.mark.parametrize(
    ('eater_id_found_by_passport', 'is_eater_info_expected'),
    [
        pytest.param(None, False, marks=pytest.mark.eater(u100={}, i123={})),
        pytest.param(
            None,
            True,
            marks=pytest.mark.eater(
                u100={},
                i123={
                    'id': '123',
                    'personal_phone_id': '1-1-1',
                    'personal_email_id': 'a@a.a',
                },
            ),
        ),
        pytest.param(
            None,
            True,
            marks=pytest.mark.eater(
                u100={},
                i123={
                    'id': '123',
                    'passport_uid': '101',
                    'personal_phone_id': '1-1-1',
                    'personal_email_id': 'a@a.a',
                },
            ),
        ),
        pytest.param(
            '123',
            True,
            marks=pytest.mark.eater(
                u100={
                    'id': '123',
                    'passport_uid': '100',
                    'personal_phone_id': '1-1-1',
                    'personal_email_id': 'a@a.a',
                },
            ),
        ),
        pytest.param(
            '456',
            False,
            marks=pytest.mark.eater(u100={'id': '456', 'passport_uid': '100'}),
        ),
        pytest.param(
            '456',
            False,
            marks=pytest.mark.eater(
                u100={
                    'id': '456',
                    'passport_uid': '100',
                    'personal_phone_id': '4-4-4',
                    'personal_email_id': 'd@d.d',
                },
                i123={
                    'id': '123',
                    'personal_phone_id': '1-1-1',
                    'personal_email_id': 'a@a.a',
                },
            ),
        ),
        pytest.param(
            '456',
            False,
            marks=pytest.mark.eater(
                u100={
                    'id': '456',
                    'passport_uid': '100',
                    'personal_phone_id': '4-4-4',
                    'personal_email_id': 'd@d.d',
                },
                i123={
                    'id': '123',
                    'passport_uid': '101',
                    'personal_phone_id': '1-1-1',
                    'personal_email_id': 'a@a.a',
                },
            ),
        ),
    ],
)
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '123'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_generator_non_anonymous_session(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        auth_method,
        request_proxy,
        eater_id_found_by_passport,
        is_eater_info_expected,
):
    @mockserver.json_handler('launch')
    def _mock_backend(request):
        # X-YaTaxi-User and X-Eats-User always contain eater_id of EA session.
        # If the same eater is found in Core by passport_uid or by eater_id
        # then X-YaTaxi-User and X-Eats-User also include additional info.
        # X-Eats-Passport-Eater-Id contains eater_id found by passport_uid.

        if is_eater_info_expected:
            utils.assert_cskvs_are_equal(
                request.headers['X-YaTaxi-User'],
                'personal_phone_id=1-1-1,personal_email_id=a@a.a,'
                + 'eats_user_id=123',
                'Check X-YaTaxi-User',
            )
            utils.assert_cskvs_are_equal(
                request.headers['X-Eats-User'],
                'personal_phone_id=1-1-1,personal_email_id=a@a.a,'
                + 'eater_uuid=123,user_id=123',
                'Check X-Eats-User',
            )
        else:
            utils.assert_cskvs_are_equal(
                request.headers['X-YaTaxi-User'],
                'eats_user_id=123',
                'Check X-YaTaxi-User',
            )
            utils.assert_cskvs_are_equal(
                request.headers['X-Eats-User'],
                'user_id=123',
                'Check X-Eats-User',
            )

        if eater_id_found_by_passport:
            assert (
                request.headers['X-Eats-Passport-Eater-Id']
                == eater_id_found_by_passport
            )
        else:
            assert 'X-Eats-Passport-Eater-Id' not in request.headers

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
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-UID'] == '100'

    response = await request_proxy(
        auth_method, url='launch', headers={'Origin': 'yandex.ru'},
    )
    assert response.status_code == 200
