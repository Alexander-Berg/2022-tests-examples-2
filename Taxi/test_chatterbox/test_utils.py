# pylint: disable=unused-variable
import functools

from aiohttp import web
import pytest

from taxi.clients import passport
from taxi.clients import tvm

from chatterbox import utils
from chatterbox.api import rights
from chatterbox.internal import auth
from test_chatterbox import plugins as conftest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ('auth_groups', 'passport_raise_exception', 'expected_status'),
    [
        (
            ([tvm.auth_required], [passport.auth_required]),
            web.HTTPUnauthorized,
            401,
        ),
        (
            ([tvm.auth_required], [passport.auth_required]),
            web.HTTPForbidden,
            403,
        ),
        (([tvm.auth_required],), None, 403),
    ],
)
async def test_many_auth(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        auth_groups,
        passport_raise_exception,
        expected_status,
):
    @patch_aiohttp_session('https://tvm-api.yandex.net', 'GET')
    def _tvm_service_request(method, url, *args, **kwargs):
        assert method == 'get'
        assert 'tvm-api.yandex.net' in url

        return response_mock(status=500)

    passport_mock_called = False

    def _mock_passport(*args, **kwargs):
        def _wrap(*args, **kwargs):
            nonlocal passport_mock_called
            passport_mock_called = True
            raise passport_raise_exception

        return _wrap

    for group in auth_groups:
        for idx, auth_method in enumerate(group):
            if auth_method is passport.auth_required:
                group[idx] = _mock_passport

    class DummyRequest:
        superuser = False
        groups = ['group_1']
        app = cbox.app
        login = 'test_login'
        raw_headers = [(b'X-Ya-Service-Ticket', 'ticket_body_str')]

        def __getitem__(self, item):
            return {}

        def __setitem__(self, key, value):
            setattr(self, key, value)

    async def my_secret_handler(request):
        raise NotImplementedError

    request = DummyRequest()
    wrapped_handler = utils.many_auth(*auth_groups)(my_secret_handler)

    response = await wrapped_handler(request)

    assert response.status == expected_status

    assert _tvm_service_request.calls
    if passport_raise_exception:
        assert passport_mock_called


@pytest.mark.config(TVM_ENABLED=True)
async def test_many_auth_passport_auth_required(
        cbox: conftest.CboxWrap, patch_auth,
):
    patch_auth(superuser=False)
    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a1/')
    assert cbox.status == 403
    assert cbox.body_data == {
        'code': 'auth_error',
        'message': 'Forbidden',
        'status': 'error',
    }


@pytest.mark.config(TVM_ENABLED=True)
async def test_many_auth_need_reset_cookies(
        cbox: conftest.CboxWrap, patch_auth,
):
    patch_auth(need_reset_cookie=True)
    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a1/')
    assert cbox.status == 401
    assert cbox.body_data == {
        'code': 'auth_error',
        'message': 'Unauthorized',
        'status': 'error',
    }


@pytest.mark.config(
    CHATTERBOX_BANK_AUTH_CONFIG={
        'login_header': 'X-Login',
        'tvm_service_name': 'bank_service',
    },
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    (
        'auth_groups',
        'src_service_name',
        'login',
        'extra_headers',
        'expected_status',
    ),
    [
        (
            (
                auth.get_bank_auth(),
                auth.get_passport_auth(rights.CHATTERBOX_READONLY),
            ),
            'bad_service',
            'some_login_basic',
            {'X-Login': 'some_login_basic'},
            401,
        ),
        (
            (
                auth.get_bank_auth(),
                auth.get_passport_auth(rights.CHATTERBOX_READONLY),
            ),
            'bank_service',
            'some_login_basic',
            {'X-Login': 'some_login_basic'},
            200,
        ),
        (
            (auth.get_bank_auth(),),
            'bank_service',
            'wrong_login',
            {'X-Login': 'wrong_login'},
            403,
        ),
        (
            (auth.get_tvm_auth(),),
            'bank_service',
            'some_login_basic',
            {'X-Login': 'some_login_basic'},
            403,
        ),
    ],
)
async def test_bank_auth(
        patch,
        cbox,
        auth_groups,
        src_service_name,
        login,
        extra_headers,
        expected_status,
):
    def passport_auth_required(func, many_auth=False, strict=False):
        @functools.wraps(func)
        async def _wrap(request, *args, **kwargs):
            assert many_auth
            raise web.HTTPUnauthorized()

        return _wrap

    def tvm_auth_required(func, many_auth=False, strict=False):
        @functools.wraps(func)
        async def _wrap(request, *args, **kwargs):
            assert many_auth
            if src_service_name:
                request['src_service_name'] = src_service_name
            else:
                raise web.HTTPForbidden()
            return await func(request, *args, **kwargs)

        return _wrap

    for group in auth_groups:
        for idx, auth_method in enumerate(group):
            if auth_method is passport.auth_required:
                group[idx] = passport_auth_required
            if auth_method is tvm.auth_required:
                group[idx] = tvm_auth_required

    class DummyRequest:
        superuser = False
        app = cbox.app
        headers = extra_headers

        def __getitem__(self, item):
            return getattr(self, item, None)

        def __setitem__(self, key, value):
            setattr(self, key, value)

        def get(self, item):
            return self.__getitem__(item)

    request = DummyRequest()

    async def my_handler(request):
        assert request.login == login
        return web.json_response({})

    wrapped_handler = utils.many_auth(*auth_groups)(my_handler)

    response = await wrapped_handler(request)
    assert response.status == expected_status
