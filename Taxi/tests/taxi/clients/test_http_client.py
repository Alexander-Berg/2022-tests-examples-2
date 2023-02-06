# pylint: disable=redefined-outer-name

import asyncio
import json
import logging

import aiohttp
import pytest

from taxi.clients import http_client

REQUEST_JSON = {'test': 'request'}
REQUEST_DATA = 'test request'
RESPONSE = {'test': 'response'}
REQUEST_TIMEOUT = 0.01


async def hello(request):
    return aiohttp.web.json_response(RESPONSE)


async def empty(request):
    return aiohttp.web.Response()


async def no_content_len(request):
    resp = aiohttp.web.Response(
        headers={'Content-Length': None, 'Content-Type': 'type/xml'},
    )
    return resp


async def bad_encoding(request):
    resp = aiohttp.web.Response(
        body='К+31',
        headers={
            'Content-Length': None,
            'Content-Type': 'type/xml; charset=VISCII',
        },
    )
    return resp


@pytest.fixture
def app():
    app = aiohttp.web.Application()
    app.router.add_post('/hello', hello)
    app.router.add_get('/empty', empty)
    app.router.add_post('/no_content_len', no_content_len)
    app.router.add_post('/bad_encoding', bad_encoding)
    return app


@pytest.fixture
async def server(aiohttp_server, app):
    return await aiohttp_server(app)


@pytest.fixture
def empty_url(server):
    return 'http://{}:{}/empty'.format(server.host, server.port)


@pytest.fixture
def hello_url(server):
    return 'http://{}:{}/hello'.format(server.host, server.port)


@pytest.fixture
def bad_encoding_url(server):
    return 'http://{}:{}/bad_encoding'.format(server.host, server.port)


@pytest.fixture
def invalid_url(server):
    return 'http://{}:1/hello'.format(server.host)


@pytest.fixture
def no_content_len_url(server):
    return 'http://{}:{}/no_content_len'.format(server.host, server.port)


@pytest.fixture
async def http_session(loop):
    from taxi.clients import http_client

    async with http_client.HTTPClient(loop=loop) as session:
        yield session


@pytest.fixture
def log_storage():
    return {logging.INFO: [], logging.WARNING: []}


@pytest.fixture
def log(log_storage):
    def _(level, msg, extra):
        log_storage[level].append(msg)

    return _


@pytest.fixture
def log_mock(monkeypatch, log):
    from taxi.clients import http_client
    monkeypatch.setattr(http_client.logger, 'log', log)


@pytest.mark.usefixtures('log_mock')
async def test_http_client_base(hello_url, http_session, log_storage):
    async with http_session.post(hello_url, json=REQUEST_JSON) as response:
        assert isinstance(response, aiohttp.ClientResponse)
        assert RESPONSE == await response.json()

        log = log_storage[logging.INFO][0]
        assert 'external POST {url} 200 19 20'.format(url=hello_url) in log
        assert 'request:' not in log
        assert 'response:' not in log


async def test_http_client_no_cm(hello_url, http_session):
    response = await http_session.post(hello_url, json=REQUEST_JSON)
    assert RESPONSE == await response.json()


async def test_http_client_no_content_len(
        patch, no_content_len_url, http_session,
):
    response = await http_session.post(
        no_content_len_url, headers={'Content-type': 'text/xml'},
    )
    assert response.status == 200


@pytest.mark.usefixtures('log_mock')
async def test_http_client_empty(empty_url, http_session, log_storage):
    async with http_session.get(empty_url):
        log = log_storage[logging.INFO][0]
        assert 'external GET {url} 200 0 0'.format(url=empty_url) in log


@pytest.mark.usefixtures('log_mock')
async def test_http_client_log_req_json(hello_url, http_session, log_storage):
    async with http_session.post(
            hello_url, json=REQUEST_JSON, log_request=True,
    ):
        log = log_storage[logging.INFO][0]
        assert 'external POST {url} 200 19 20'.format(url=hello_url) in log
        assert 'request: {}'.format(REQUEST_JSON) in log


@pytest.mark.usefixtures('log_mock')
async def test_http_client_log_req_data(hello_url, http_session, log_storage):
    async with http_session.post(
            hello_url, data=REQUEST_DATA, log_request=True,
    ):
        log = log_storage[logging.INFO][0]
        assert 'external POST {url} 200 12 20'.format(url=hello_url) in log
        assert 'request: {}'.format(REQUEST_DATA) in log


@pytest.mark.parametrize(
    'url, params_to_mask, expected_url',
    (
        (
            'http://some-url.net/path?param1=123&param2=456',
            ['param1', 'param2'],
            'http://some-url.net/path?param1=***&param2=***',
        ),
        (
            'http://some-url.net/path?param1=123&param2=456',
            ['param1'],
            'http://some-url.net/path?param1=***&param2=456',
        ),
        (
            'http://some-url.net/path?param1=123&param2=456',
            ['param2'],
            'http://some-url.net/path?param1=123&param2=***',
        ),
        (
            'http://some-url.net/path?param1=123&param2=456',
            [],
            'http://some-url.net/path?param1=123&param2=456',
        ),
        (
            'http://some-url.net/path?param1=123&param2=456',
            ['param3'],
            'http://some-url.net/path?param1=123&param2=456',
        ),
        (
            'http://some-url.net/param1/path',
            ['param1', 'param2'],
            'http://some-url.net/param1/path',
        ),
        (
            'http://param1-url.net/path',
            ['param1'],
            'http://param1-url.net/path',
        ),
        (
            'https://taxi.tel.yandex-team.ru/?/'
            'mod.cipt-admin/API/USER/production-callcenter/show/'
            'HASH&dauth=robot-taxi-tele-prod&dsign=sign',
            ['dauth', 'dsign'],
            'https://taxi.tel.yandex-team.ru/?/'
            'mod.cipt-admin/API/USER/production-callcenter/show/'
            'HASH=&dauth=***&dsign=***',
        ),
    ),
)
async def test_mask_url_params(url, params_to_mask, expected_url):
    masked_url = http_client.mask_url_params(url, params_to_mask)
    assert masked_url == expected_url


@pytest.mark.usefixtures('log_mock')
async def test_http_client_log_response(hello_url, http_session, log_storage):
    async with http_session.post(hello_url, log_response=True):
        log = log_storage[logging.INFO][0]
        assert 'response: {}'.format(json.dumps(RESPONSE)) in log


@pytest.mark.usefixtures('log_mock')
async def test_http_client_log_404(hello_url, http_session, log_storage):
    not_exists_url = '{}/not_exists'.format(hello_url)
    async with http_session.post(not_exists_url):
        log = log_storage[logging.INFO][0]
        assert '404' in log


@pytest.mark.usefixtures('log_mock')
async def test_http_client_error(invalid_url, http_session, log_storage):
    with pytest.raises(aiohttp.ClientError):
        async with http_session.post(invalid_url):
            pass

    log = log_storage[logging.WARNING][0]
    assert 'error: Cannot connect to host' in log


@pytest.mark.not_mock_request()
@pytest.mark.usefixtures('log_mock')
async def test_http_client_timeout(patch, http_session, log_storage):
    @patch('aiohttp.client.ClientSession._request')
    async def _request(*args, **kwargs):
        raise asyncio.TimeoutError()

    with pytest.raises(asyncio.TimeoutError):
        async with http_session.get('/', timeout=REQUEST_TIMEOUT):
            pass

    log = log_storage[logging.WARNING][0]
    assert 'timeout: {}s'.format(REQUEST_TIMEOUT) in log


@pytest.mark.usefixtures('log_mock')
async def test_request_log_lookup(bad_encoding_url, http_session):

    response = await http_session.post(bad_encoding_url)
    assert response.status == 200
