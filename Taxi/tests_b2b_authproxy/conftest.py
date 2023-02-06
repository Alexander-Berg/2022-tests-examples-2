# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy


from b2b_authproxy_plugins import *  # noqa: F403 F401
from client_blackbox.mock_blackbox import make_phone
import pytest


from tests_b2b_authproxy import const


class BasicMock:
    def __init__(self):
        self.response_code = None
        self.response_json = None

        self.default_responses = {}

    def set_response_by_code(self, response_code):
        self.response_code = response_code
        self.response_json = self.default_responses.get(
            response_code, const.BAD_RESPONSE,
        )

    def set_response(self, response_code=200, response_json=None):
        self.response_code = response_code
        self.response_json = response_json

    def get_response(self):
        if self.response_code is None:
            self.set_response_by_code(response_code=200)
        return {'code': self.response_code, 'json': self.response_json}


@pytest.fixture(name='get_token_headers')
def _get_token_headers():
    def wrapper(is_b2b_header_set=False):
        headers = copy.deepcopy(const.IP_ORIGIN_HEADERS)
        if is_b2b_header_set:
            headers['X-B2B-Client-Id'] = const.CORP_CLIENT_ID
        return headers

    return wrapper


@pytest.fixture(name='get_session_headers')
def _get_session_headers():
    def wrapper(session=None, corp_client_id=None, is_b2b_header_set=False):
        headers = copy.deepcopy(const.IP_ORIGIN_HEADERS)
        if session is None:
            session = 'session_1'
        headers['Cookie'] = f'Session_id={session}'
        if corp_client_id or is_b2b_header_set:
            headers['X-B2B-Client-Id'] = corp_client_id or const.CORP_CLIENT_ID
        return headers

    return wrapper


@pytest.fixture(name='blackbox_phone_context')
def _blackbox_phone_context():
    class Context:
        def __init__(self):
            self.is_secured = False

        def make(self):
            return [make_phone('', secured=self.is_secured)]

    return Context()


@pytest.fixture(name='get_default_token')
def _get_default_token():
    return 'token_1'


def _get_default_blackbox_sessions():
    return [
        {
            'session_id': 'session_no_corp',
            'yandex_uid': '0000',
            'login': 'login0',
        },
        {'session_id': 'session_1', 'yandex_uid': '1111', 'login': 'login1'},
        {'session_id': 'session_2', 'yandex_uid': '2222', 'login': 'login2'},
        {'session_id': 'session_3', 'yandex_uid': '3333', 'login': 'login3'},
    ]


def _get_default_blackbox_tokens():
    return [
        {
            'token': 'token_no_corp',
            'yandex_uid': '0000',
            'scope': 'corptaxi:all',
            'login': 'login5',
        },
        {
            'token': 'token_1',
            'yandex_uid': '1111',
            'scope': 'corptaxi:all',
            'login': 'login1',
        },
        {
            'token': 'token_2',
            'yandex_uid': '2222',
            'scope': 'corptaxi:all',
            'login': 'login2',
        },
        {
            'token': 'token_3',
            'yandex_uid': '3333',
            'scope': 'corptaxi:all',
            'login': 'login3',
        },
    ]


@pytest.fixture(name='mock_taxicorp')
def _mock_taxicorp(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.client_id_by_uid = {
                '1111': const.CORP_CLIENT_ID,
                '2222': const.OTHER_CORP_CLIENT_ID,
            }

            self.default_responses = {
                200: {'corp_client_id': const.CORP_CLIENT_ID},
                404: const.NOT_FOUND,
            }

        def get_response_by_uid(self, yandex_uid=None):
            if self.response_code and self.response_json:
                return {'code': self.response_code, 'json': self.response_json}

            if yandex_uid not in self.client_id_by_uid:
                return {'code': 404, 'json': self.default_responses[404]}

            return {
                'code': 200,
                'json': {'corp_client_id': self.client_id_by_uid[yandex_uid]},
            }

        @property
        def times_called(self):
            return _taxi_corp_integration_handler.times_called

    context = Context()

    @mockserver.json_handler(
        'taxi-corp-integration/v1/authproxy/corp_client_id',
    )
    def _taxi_corp_integration_handler(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        yandex_uid = request.json.get('uid')
        assert yandex_uid

        response = context.get_response_by_uid(yandex_uid=yandex_uid)
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='mock_cargocorp')
def _mock_cargocorp(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {'is_employee': False, 'is_disabled': True},
            }

        def set_ok_response(self, is_employee=False, is_enabled=False):
            self.default_responses[200] = {
                'is_employee': is_employee,
                'is_disabled': not is_enabled,
            }

        @property
        def times_called(self):
            return _cargo_corp_employee_traits_handler.times_called

    context = Context()

    @mockserver.json_handler(
        'cargo-corp/internal/cargo-corp/v1/client/employee/traits',
    )
    def _cargo_corp_employee_traits_handler(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'

        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='mock_cargo_robot_client')
def _mock_cargo_robot_client(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {'corp_client': {'id': const.CORP_CLIENT_ID}},
                404: const.NOT_FOUND,
            }

        def set_ok_response(self, client):
            self.default_responses[200]['corp_client']['id'] = client

        @property
        def times_called(self):
            return _cargo_corp_employee_clients_handler.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/employee/corp-client/if-robot',
    )
    def _cargo_corp_employee_clients_handler(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'

        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='mock_cargo_corp_perms')
def _mock_cargo_corp_perms(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {'permission_ids': [{'id': 'some_perm'}]},
                404: const.NOT_FOUND,
            }

        def set_ok_response(self, perms):
            self.default_responses[200]['permission_ids'] = [
                {'id': perm} for perm in perms
            ]

        @property
        def times_called(self):
            return _cargo_corp_employee_perms_handler.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/employee/permission/list',
    )
    def _cargo_corp_employee_perms_handler(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'

        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='b2b_authproxy_post')
def _b2b_authproxy_post(
        taxi_b2b_authproxy,
        blackbox_service,
        mock_taxicorp,
        get_session_headers,
        get_token_headers,
        blackbox_phone_context,
):
    async def _wrapper(
            path,
            json,
            headers=None,
            bearer=None,
            session=None,
            blackbox_sessions=None,
            blackbox_tokens=None,
            drop_bearer=False,
            is_b2b_header_set=False,
    ):
        if headers is None:
            headers = (
                get_session_headers(
                    session=session, is_b2b_header_set=is_b2b_header_set,
                )
                if bearer is None
                else get_token_headers(is_b2b_header_set)
            )

        if blackbox_sessions is None:
            blackbox_sessions = _get_default_blackbox_sessions()

        if blackbox_tokens is None:
            blackbox_tokens = _get_default_blackbox_tokens()

        for blackbox_token_info in blackbox_tokens:
            blackbox_service.set_token_info(
                blackbox_token_info['token'],
                uid=blackbox_token_info['yandex_uid'],
                login=blackbox_token_info['login'],
                scope=blackbox_token_info['scope'],
            )
        for blackbox_session in blackbox_sessions:
            blackbox_service.set_sessionid_info(
                blackbox_session['session_id'],
                uid=blackbox_session['yandex_uid'],
                login=blackbox_session['login'],
                phones=blackbox_phone_context.make(),
            )
        if drop_bearer:
            bearer = None
        return await taxi_b2b_authproxy.post(
            path, json=json, bearer=bearer, headers=headers,
        )

    return _wrapper


@pytest.fixture(name='b2b_authproxy_post_with_cargo_init')
def _b2b_authproxy_post_with_cargo_init(
        b2b_authproxy_post, mock_cargocorp, mock_cargo_robot_client,
):
    async def _wrapper(
            path,
            json,
            headers=None,
            bearer=None,
            session=None,
            blackbox_sessions=None,
            blackbox_tokens=None,
            drop_bearer=False,
            is_b2b_header_set=False,
            cargo_corp_code=200,
            cargo_robot_code=404,
    ):
        mock_cargocorp.set_response_by_code(response_code=cargo_corp_code)
        mock_cargo_robot_client.set_response_by_code(
            response_code=cargo_robot_code,
        )

        response = await b2b_authproxy_post(
            path,
            json=json,
            headers=headers,
            bearer=bearer,
            session=session,
            blackbox_sessions=blackbox_sessions,
            blackbox_tokens=blackbox_tokens,
            drop_bearer=drop_bearer,
            is_b2b_header_set=is_b2b_header_set,
        )

        if not is_b2b_header_set:
            # old way auth does not use cargo_corp
            assert mock_cargocorp.times_called == 0

        return response

    return _wrapper


@pytest.fixture(name='test_handlers')
def _test_handlers(mockserver):
    def _test(request, expected_uid, expected_login):
        # No filtered headers
        assert 'Authorization' not in request.headers
        assert 'authorization' not in request.headers
        assert 'Cookie' not in request.headers
        assert 'cookie' not in request.headers

        # Proxy headers added
        assert request.headers['X-Remote-IP'] == '1.2.3.4'
        # tvm2
        service_ticket = '1000_ticket_not_set_in_testsuite'
        assert request.headers['X-Ya-Service-Ticket'] == service_ticket
        # Auth headers
        assert request.headers['X-B2B-Client-Id'] in const.CORPS
        assert 'X-B2B-Client-Storage' in request.headers
        if expected_uid:
            assert request.headers['X-Yandex-Uid'] == expected_uid
        if expected_login:
            assert request.headers['X-Yandex-Login'] == expected_login
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'

        # Body is the same
        assert request.json == const.DEFAULT_REQUEST
        return {'id': '123'}

    def _wrapper(path, expected_uid=None, expected_login=None):
        # pylint: disable=W0108
        return mockserver.json_handler(path)(
            lambda request: _test(request, expected_uid, expected_login),
        )

    return _wrapper


@pytest.fixture(name='test_handler')
def _test_handler(test_handlers):
    return test_handlers('/v1/cargo/test', '1111', 'login1')


@pytest.fixture(name='test_proxy_401_handlers')
def _test_proxy_401_handlers(mockserver):
    def _test(request, uid_expected=None, expected_b2b_header=None):
        # No filtered headers
        assert 'Authorization' not in request.headers
        assert 'authorization' not in request.headers
        assert 'Cookie' not in request.headers
        assert 'cookie' not in request.headers

        # Proxy headers added
        assert request.headers['X-Remote-IP'] == '1.2.3.4'

        # Auth headers
        if expected_b2b_header:
            assert request.headers['X-B2B-Client-Id'] == expected_b2b_header
            assert 'X-B2B-Client-Storage' in request.headers
        else:
            assert 'X-B2B-Client-Id' not in request.headers
            assert 'X-B2B-Client-Storage' not in request.headers

        if uid_expected:
            assert 'X-Yandex-Uid' in request.headers
            assert 'X-Ya-User-Ticket' in request.headers
        elif uid_expected is not None:
            assert 'X-Yandex-Uid' not in request.headers
            assert 'X-Ya-User-Ticket' not in request.headers

        # Body is the same
        assert request.json == const.DEFAULT_REQUEST
        return {'id': '123'}

    def _wrapper(path, uid_expected=None, expected_b2b_header=None):
        # pylint: disable=W0108
        return mockserver.json_handler(path)(
            lambda request: _test(request, uid_expected, expected_b2b_header),
        )

    return _wrapper
