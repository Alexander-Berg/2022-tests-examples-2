# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import asyncio
import typing

import aiohttp
import pytest

from taxi import config
from taxi import settings as taxi_settings
from taxi.clients import http_client
from taxi.clients import passport_internal
from taxi.clients import tvm


@pytest.fixture
def response(request):
    return request.param if hasattr(request, 'param') else None


@pytest.fixture
def handler(response):
    async def base(request):
        status, resp, content_type = response
        kwargs = {'status': status, 'content_type': content_type}

        if content_type == 'application/json':
            kwargs['data'] = resp
        else:
            kwargs['body'] = resp
        return aiohttp.web.json_response(**kwargs)

    return base


@pytest.fixture
def register_url():
    return '/1/bundle/account/register/by_middleman/'


@pytest.fixture
def app(handler, register_url):
    app = aiohttp.web.Application()
    app.router.add_post('/test', handler)
    app.router.add_post(register_url, handler)
    return app


@pytest.fixture
async def server(aiohttp_server, app):
    return await aiohttp_server(app)


@pytest.fixture
def base_url(server):
    return 'http://{}:{}'.format(server.host, server.port)


@pytest.fixture
def consumer():
    return 'test'


@pytest.fixture
async def session() -> typing.AsyncGenerator[http_client.HTTPClient, None]:
    _session = http_client.HTTPClient()
    yield _session
    await _session.close()


@pytest.mark.usefixtures('get_auth_headers_mock')
@pytest.fixture
def tvm_client(simple_secdist, session, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='corp-cabinet',
        secdist=simple_secdist,
        config=config,
        session=session,
    )


@pytest.fixture
def client(base_url, consumer, session: http_client.HTTPClient, tvm_client):
    session = typing.cast(http_client.HTTPClient, session)

    settings = taxi_settings.Settings()
    settings.PASSPORT_INTERNAL_BASE_URL = base_url  # pylint: disable=C0103

    return passport_internal.PassportClient(
        settings=settings, session=session, tvm=tvm_client, consumer=consumer,
    )


@pytest.fixture
def client_response_mock():
    class ClientResponseMock:
        @property
        def status(self):
            return 200

        async def text(self):
            return '{"status": "ok"}'

    return ClientResponseMock


async def test_request_base(client, client_response_mock, consumer, patch):
    @patch('aiohttp.ClientSession.post')
    async def _post(*args, **kwargs):
        return client_response_mock()

    req = await client._request(
        url='/test', data={'test': 'data'}, log_extra={'_link': 'test'},
    )

    assert req == {'status': 'ok'}
    assert _post.calls == [
        {
            'args': (client.settings.PASSPORT_INTERNAL_BASE_URL + '/test',),
            'kwargs': {
                'data': {'test': 'data'},
                'headers': {
                    'X-Ya-Service-Ticket': 'ticket',
                    'Ya-Client-User-Agent': aiohttp.http.SERVER_SOFTWARE,
                    'Ya-Consumer-Client-Ip': client.consumer_ip,
                },
                'params': {'consumer': consumer},
                'timeout': client.settings.PASSPORT_TIMEOUT,
                'log_extra': {'_link': 'test'},
            },
        },
    ]


@pytest.mark.parametrize(
    'response',
    [(200, {'status': 'ok'}, 'application/json')],
    indirect=['response'],
)
async def test_request_ok(client, response):
    resp = await client._request(url='/test', data={})
    assert resp == response[1]


@pytest.mark.parametrize(
    'response', [(400, '<html></html>', 'text')], indirect=['response'],
)
async def test_request_bad_json(client):
    with pytest.raises(passport_internal.InternalError):
        await client._request(url='/test', data={})


@pytest.mark.parametrize(
    'response',
    [(403, {'errors': ['access.denied']}, 'application/json')],
    indirect=['response'],
)
async def test_request_deny(client):
    with pytest.raises(passport_internal.InternalError):
        await client._request(url='/test', data={})


@pytest.mark.parametrize(
    'response',
    [(500, {'status': 'error'}, 'application/json')],
    indirect=['response'],
)
async def test_request_not_200(client, response):
    with pytest.raises(passport_internal.InternalError) as exc:
        await client._request(url='/test', data={})
    msg = 'status_code: 500, content: {\'status\': \'error\'}'
    assert str(exc.value) == msg


@pytest.mark.parametrize(
    'response', [(200, {}, 'application/json')], indirect=['response'],
)
async def test_request_not_status(client, response):
    with pytest.raises(passport_internal.InternalError) as exc:
        await client._request(url='/test', data={})
    msg = 'status_code: 200, content: {}'
    assert str(exc.value) == msg


@pytest.mark.parametrize(
    'response',
    [(200, {'status': 'not_ok', 'errors': ['error']}, 'application/json')],
    indirect=['response'],
)
async def test_request_not_ok(client, response):
    with pytest.raises(passport_internal.PassportError) as exc:
        await client._request(url='/test', data={})
    assert exc.value.errors == ['error']


@pytest.mark.parametrize(
    'exc',
    [(aiohttp.client_exceptions.ClientError()), (asyncio.TimeoutError())],
)
async def test_request_exc(client, exc, session, monkeypatch):
    async def _post(*args, **kwargs):
        raise exc

    monkeypatch.setattr(session, 'post', _post)

    with pytest.raises(passport_internal.InternalError):
        await client._request(url='/base', data={})


async def test_register(client, register_url, patch):
    @patch('taxi.clients.passport_internal.PassportClient._request')
    async def _request(*args, **kwargs):
        pass

    params = {
        'login': 'vasya',
        'password': 'super_pass',
        'language': 'ru',
        'country': 'ru',
    }
    await client.register(**params, log_extra='12345')
    assert _request.calls == [
        {'args': (register_url, params), 'kwargs': {'log_extra': '12345'}},
    ]
