# pylint: disable=redefined-outer-name,no-self-use,unused-variable,invalid-name
# pylint: disable=too-many-arguments,no-member,protected-access
import collections
import http

from aiohttp import web
import pytest
import ticket_parser2

from taxi import config
from taxi.clients import tvm
from taxi.util import service_roles
from taxi.util.aiohttp_kit import middleware


TVM_KEYS_URL = '%s/2/keys?lib_version=%s' % (
    config.Config.TVM_API_URL,
    ticket_parser2.__version__.decode('utf-8'),
)


class EmptyDict(collections.UserDict):
    def get(self, key, default=None):
        return None


@pytest.fixture
async def app(test_taxi_app, simple_secdist, monkeypatch):
    simple_secdist['settings_override']['TVM_SERVICES'] = {
        'test': {'secret': 'test-secret'},
        'destination': {'secret': 'top-secret'},
        'wrong_source': {'secret': 'wrong-secret'},
    }
    test_taxi_app.config.TVM_SERVICES = {
        'test': 1,
        'destination': 2,
        'wrong_source': 3,
    }

    @tvm.auth_required
    async def handler(request):
        return web.Response()

    @tvm.auth_required
    @service_roles.service_role_required('test_role')
    async def protected_handler(request):
        return web.Response()

    test_taxi_app.router.add_get('/test', handler)
    test_taxi_app.router.add_get('/test/protected', protected_handler)
    test_taxi_app.middlewares.append(middleware.use_log_extra())
    return test_taxi_app


@pytest.fixture
async def client(app, aiohttp_client):
    return await aiohttp_client(app)


@pytest.mark.config(
    SERVICE_ROLES={'test': {'test_role': ['destination']}},
    SERVICE_ROLES_ENABLED=True,
)
@pytest.mark.parametrize(
    'path, src_service_id, expected_status',
    [
        ('/test', 2, http.HTTPStatus.OK),
        ('/test', 3, http.HTTPStatus.OK),
        ('/test/protected', 2, http.HTTPStatus.OK),
        ('/test/protected', 3, http.HTTPStatus.FORBIDDEN),
    ],
)
@pytest.mark.mongodb_collections('localizations_meta')
async def test_allowed_services(
        app,
        client,
        path,
        src_service_id,
        expected_status,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        stub,
        mock,
):
    tvm_keys = '1:say-friend-and-enter'

    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def patch_get_keys(method, url, **kwargs):
        return response_mock(text=tvm_keys)

    class ServiceContextMock:
        def __init__(self, service_id, service_secret, tvm_keys):
            pass

        @staticmethod
        @mock
        def check(ticket_body):
            return stub(src=src_service_id, debug_info=lambda: 'valid_ticket')

    monkeypatch.setattr('taxi.memstorage._manager._cache', EmptyDict())

    monkeypatch.setattr(
        'ticket_parser2.api.v1.ServiceContext', ServiceContextMock,
    )

    app.config.TVM_ENABLED = True
    app.config.TVM_RULES = [
        {'src': 'destination', 'dst': 'test'},
        {'src': 'wrong_source', 'dst': 'test'},
    ]

    resp = await client.get(path, headers={tvm.TVM_TICKET_HEADER: 'ticket'})
    assert resp.status == expected_status
