# pylint: disable=redefined-outer-name,no-self-use,unused-variable,invalid-name
# pylint: disable=too-many-arguments,no-member,protected-access
import collections
import http

import aiohttp
from aiohttp import web
import pytest
import ticket_parser2
import ticket_parser2.api.v1.exceptions as tvm_api_exceptions

from taxi import config
from taxi import memstorage
from taxi import settings
from taxi.clients import tvm
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
        'test': {'id': 1, 'secret': 'test-secret'},
    }
    test_taxi_app.config.TVM_SERVICES = {'test': 1, 'destination': 2}

    @tvm.auth_required
    async def handler(request):
        return web.Response()

    async def handler_strict(request):
        return web.Response()

    strict_decorated_handler = tvm.auth_required(handler_strict, strict=True)

    test_taxi_app.router.add_get('/test', handler)
    test_taxi_app.router.add_get('/test/strict_auth', strict_decorated_handler)
    test_taxi_app.middlewares.append(middleware.use_log_extra())
    return test_taxi_app


@pytest.fixture
async def client(app, aiohttp_client):
    return await aiohttp_client(app)


@pytest.fixture
def mongodb_collections():
    return ['localizations_meta']


async def test_default(client):
    resp = await client.get('/test')
    assert resp.status == http.HTTPStatus.OK


async def test_protected_access_without_ticket(app, client):
    app.config.TVM_ENABLED = True
    resp = await client.get('/test')
    assert resp.status == http.HTTPStatus.FORBIDDEN


@pytest.mark.parametrize(
    'has_valid_ticket, tvm_rules, service_check_disabled, get_keys_error, '
    'expected_status',
    [
        (True, [], False, False, http.HTTPStatus.FORBIDDEN),
        (False, [], False, False, http.HTTPStatus.FORBIDDEN),
        (
            True,
            [{'src': 'destination', 'dst': 'test'}],
            False,
            False,
            http.HTTPStatus.OK,
        ),
        (False, [], True, False, http.HTTPStatus.OK),
        (False, [], False, True, http.HTTPStatus.OK),
    ],
)
async def test_protected_access_with_ticket(
        app,
        client,
        has_valid_ticket,
        tvm_rules,
        expected_status,
        get_keys_error,
        service_check_disabled,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        stub,
        mock,
):
    service_id = 2
    service_secret = 'top-secret'
    app.secdist['settings_override']['TVM_SERVICES']['destination'] = {
        'secret': service_secret,
    }
    tvm_keys = '1:say-friend-and-enter'

    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def patch_get_keys(method, url, **kwargs):
        if get_keys_error:
            return response_mock(status=500)
        return response_mock(text=tvm_keys)

    class ServiceContextMock:
        def __init__(self, service_id, service_secret, tvm_keys):
            pass

        @staticmethod
        @mock
        def check(ticket_body):
            if has_valid_ticket:
                return stub(src=service_id, debug_info=lambda: 'valid_ticket')
            raise tvm_api_exceptions.TicketParsingException(
                'bad ticket: %s' % ticket_body, 'status', 'debug_info',
            )

    monkeypatch.setattr('taxi.memstorage._manager._cache', EmptyDict())

    monkeypatch.setattr(
        'ticket_parser2.api.v1.ServiceContext', ServiceContextMock,
    )

    app.config.TVM_ENABLED = True
    app.config.TVM_RULES = tvm_rules
    if service_check_disabled:
        app.config.TVM_DISABLE_CHECK = ['test']

    resp = await client.get('/test', headers={tvm.TVM_TICKET_HEADER: 'ticket'})
    assert resp.status == expected_status

    if not (service_check_disabled or get_keys_error):
        assert ServiceContextMock.check.calls == [{'ticket_body': b'ticket'}]
    else:
        assert ServiceContextMock.check.calls == []


async def test_get_ticket_for_not_registered_service(app):
    app.config.TVM_ENABLED = True
    service_name = 'not_registered_service'
    app.config.TVM_RULES = [{'src': app.service_name, 'dst': service_name}]
    with pytest.raises(tvm.ServiceNotFound) as excinfo:
        await app.tvm.get_ticket(service_name)
    assert excinfo.value.args == (
        'service %s not found in TVM_SERVICES' % service_name,
    )


async def test_get_ticket_no_rules(app):
    app.config.TVM_ENABLED = True
    ticket = await app.tvm.get_ticket('destination')
    assert ticket == ''


@pytest.mark.parametrize('status', [200, 400, 500])
async def test_get_keys(
        app, patch_aiohttp_session, response_mock, status, monkeypatch,
):
    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def patch_get_keys(method, url, **kwargs):
        return response_mock(text='keys-text', status=status)

    monkeypatch.setattr('taxi.memstorage._manager._cache', EmptyDict())

    if status == 200:
        assert (await app.tvm.get_keys()) == 'keys-text'
    else:
        with pytest.raises(tvm.TvmRequestError) as excinfo:
            await app.tvm._request('GET', 'some_url')
        assert excinfo.value.args == (
            'cannot perform request to some_url: code %s' % status,
        )


@pytest.mark.parametrize(
    'tvm_enabled, expected_ticket, key_in_cache',
    [
        (
            False,
            '',
            (
                '',
                (
                    'taxi.clients.tvm.TVMClient._get_ticket',
                    '(\'test\', \'destination\', False, ['
                    '{\'src\': \'test\', \'dst\': \'destination\'}])',
                ),
            ),
        ),
        (
            True,
            'some-ticket-value',
            (
                '',
                (
                    'taxi.clients.tvm.TVMClient._get_ticket',
                    '(\'test\', \'destination\', True, ['
                    '{\'src\': \'test\', \'dst\': \'destination\'}])',
                ),
            ),
        ),
    ],
)
async def test_get_ticket(
        app,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        tvm_enabled,
        expected_ticket,
        key_in_cache,
):
    memstorage._manager._cache = {}
    app.config.TVM_ENABLED = tvm_enabled
    app.config.TVM_RULES = [{'src': app.service_name, 'dst': 'destination'}]
    service_id = 2
    service_secret = 'do-not-tell-anyone'
    app.secdist['settings_override']['TVM_SERVICES']['destination'] = {
        'secret': service_secret,
    }

    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def patch_get_keys(method, url, **kwargs):
        return response_mock(text='tvm-keys')

    @patch_aiohttp_session(app.config.TVM_API_URL + '/2/ticket', 'POST')
    def patch_get_ticket(method, url, **kwargs):
        return response_mock(
            json={str(service_id): {'ticket': 'some-ticket-value'}},
        )

    class ServiceContextMock:
        def __init__(self, service_id, service_secret, tvm_keys):
            pass

        def sign(self, timestamp, dst_service_id):
            if dst_service_id == service_id:
                return b'sign'
            return None

    monkeypatch.setattr(
        'ticket_parser2.api.v1.ServiceContext', ServiceContextMock,
    )

    ticket = await app.tvm.get_ticket('destination')
    assert ticket == expected_ticket
    get_ticket_calls = patch_get_ticket.calls

    if tvm_enabled:
        assert len(get_ticket_calls) == 1
        data = get_ticket_calls[0]['kwargs']['data']
        data.pop('ts')
        assert data == {
            'grant_type': 'client_credentials',
            'src': '1',
            'dst': str(service_id),
            'sign': 'sign',
        }
    else:
        assert get_ticket_calls == []

    assert key_in_cache in memstorage._manager._cache


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'get_keys_error, get_ticket_error', ((True, False), (False, True)),
)
async def test_get_ticket_exception(
        app,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        get_keys_error,
        get_ticket_error,
):
    memstorage._manager._cache = {}
    app.config.TVM_RULES = [{'src': app.service_name, 'dst': 'destination'}]
    service_id = 2
    service_secret = 'do-not-tell-anyone'
    app.secdist['settings_override']['TVM_SERVICES']['destination'] = {
        'secret': service_secret,
    }

    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def patch_get_keys(method, url, **kwargs):
        if get_keys_error:
            return response_mock(status=400)
        return response_mock(text='tvm-keys')

    @patch_aiohttp_session(app.config.TVM_API_URL + '/2/ticket', 'POST')
    def patch_get_ticket(method, url, **kwargs):
        if get_ticket_error:
            return response_mock(status=400)
        return response_mock(
            json={str(service_id): {'ticket': 'some-ticket-value'}},
        )

    class ServiceContextMock:
        def __init__(self, service_id, service_secret, tvm_keys):
            pass

        def sign(self, timestamp, dst_service_id):
            if dst_service_id == service_id:
                return b'sign'
            return None

    monkeypatch.setattr(
        'ticket_parser2.api.v1.ServiceContext', ServiceContextMock,
    )

    ticket = await app.tvm.get_ticket('destination')
    assert ticket == ''
    if get_keys_error:
        assert not memstorage._manager._cache
    else:
        key_get_keys = ('', ('taxi.clients.tvm.TVMClient.get_keys', ''))
        assert key_get_keys in memstorage._manager._cache


@pytest.mark.parametrize(
    'is_strict, expected_status',
    [(True, http.HTTPStatus.FORBIDDEN), (False, http.HTTPStatus.OK)],
)
async def test_strict_auth(
        app,
        client,
        is_strict,
        expected_status,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    app.config.TVM_ENABLED = True

    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def patch_get_keys(method, url, **kwargs):
        return response_mock(status=500)

    monkeypatch.setattr('taxi.memstorage._manager._cache', EmptyDict())

    if not is_strict:
        url = '/test'
    else:
        url = '/test/strict_auth'
    resp = await client.get(url, headers={tvm.TVM_TICKET_HEADER: 'ticket'})
    assert resp.status == expected_status


@pytest.mark.parametrize(
    'secdist_id,configs_id,expected_exception,expected_args',
    [
        [1, 1, None, None],
        [
            1,
            111,
            tvm.TvmIdMismatch,
            (
                'Tvm id for service test from secdist doesn\'t match with'
                ' id from config.\nSecdist: 1\nConfig: 111\n',
            ),
        ],
        [
            None,
            1,
            tvm.ServiceNotFound,
            ('Service with name test wasn\'t found in secdist.',),
        ],
        [
            1,
            None,
            tvm.ServiceNotFound,
            ('service test not found in TVM_SERVICES',),
        ],
    ],
)
async def test_tvm_id_match(
        monkeypatch,
        simple_secdist,
        loop,
        secdist_id,
        configs_id,
        expected_exception,
        expected_args,
):
    simple_secdist['settings_override']['TVM_SERVICES'] = {
        'test': {'id': secdist_id},
    }
    configs = config.Config()
    configs.TVM_SERVICES = {'test': configs_id}
    async with aiohttp.ClientSession(loop=loop) as session:
        monkeypatch.setattr('taxi.settings.ENVIRONMENT', settings.UNSTABLE)
        tvm_client = tvm.TVMClient(
            service_name='test',
            secdist=simple_secdist,
            session=session,
            config=configs,
        )

        if expected_exception is not None:
            with pytest.raises(expected_exception) as exec_info:
                await tvm_client.on_startup()
            assert exec_info.value.args == expected_args
        else:
            await tvm_client.on_startup()
