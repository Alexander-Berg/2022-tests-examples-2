# pylint: disable=protected-access,redefined-outer-name
import json
import logging
import uuid

from aiohttp import web
import pytest

from taxi import config
from taxi import web_app
from taxi.util.aiohttp_kit import middleware


UUID = 'b9ca3ae6562644bb9d1c9595ee4e3905'


@pytest.fixture
async def log_extra_tst(
        loop,
        db,
        simple_secdist,
        collected_logs_with_link,
        aiohttp_client,
        patch,
):
    log_settings = {
        'logger_names': ['taxi'],
        'ident': 'log_extra',
        'log_level': logging.INFO,
        'log_format': '',
    }

    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(UUID, version=4)

    app = web_app.TaxiApplication(
        config_cls=config.Config,
        log_settings=log_settings,
        loop=loop,
        db=db,
        service_name='LOG_EXTRA',
    )

    async def ok_handle(request):
        logger = logging.getLogger('taxi')
        logger.info('logs from inside', extra=request['log_extra'])
        return web.Response(status=200, text='ok_payload')

    async def forbidden_exc(request):
        raise web.HTTPForbidden(text='403_payload')

    async def http_exc(request):
        raise web.HTTPNotFound(text='404_payload')

    async def internal_exc(request):
        raise Exception('test_exc')

    async def variable_resource(request):
        return web.Response(status=200, text='ok_payload')

    app.router.add_get('/ok', ok_handle)
    app.router.add_get('/forbidden_exc', forbidden_exc)
    app.router.add_get('/http_exc', http_exc)
    app.router.add_get('/internal_exc', internal_exc)
    app.router.add_get('/resources', variable_resource)
    app.router.add_get('/resources/', variable_resource)
    app.router.add_get(r'/resource/{id:\w+}', variable_resource)
    app.router.add_get(r'/resource/{id:\w+}/', variable_resource)
    app.middlewares.append(middleware.use_log_extra())

    res = await aiohttp_client(
        app,
        headers={'User-Agent': 'toster', 'X-YaRequestId': 'x-ya-request-id'},
    )
    res.logs = collected_logs_with_link

    await web_app._logger_startup(app)
    yield res
    await web_app._logger_cleanup(app)


@pytest.fixture
def mongodb_collections():
    return ['localizations_meta']


async def test_log_extra_ok(log_extra_tst):
    resp = await log_extra_tst.get('/ok', data='test_payload')
    assert resp.status == 200
    assert (await resp.text()) == 'ok_payload'

    logs = log_extra_tst.logs
    _link = UUID

    expected_result = [
        {
            '_link': _link,
            'exc_info': False,
            'extdict': {},
            'level': 'INFO',
            'msg': 'log_extra app created',
        },
        {
            'level': 'INFO',
            '_link': _link,
            'msg': 'GET request for /ok',
            'extdict': {
                '_type': 'request',
                'method': 'GET',
                'uri': '/ok',
                'useragent': 'toster',
                'body': 'test_payload',
                'meta': [{'n': 'type', 'v': 'ok'}],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
        {
            'level': 'INFO',
            '_link': _link,
            'msg': 'logs from inside',
            'extdict': {
                'method': 'GET',
                'uri': '/ok',
                'meta': [{'n': 'type', 'v': 'ok'}],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
        {
            'level': 'INFO',
            '_link': _link,
            'msg': 'GET request to /ok finished with 200',
            'extdict': {
                '_type': 'response',
                'method': 'GET',
                'uri': '/ok',
                'body': 'ok_payload',
                'meta': [{'n': 'type', 'v': 'ok'}, {'n': 'code', 'v': 200}],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
    ]

    assert logs == expected_result


async def test_log_extra_http_exc(log_extra_tst):
    resp = await log_extra_tst.get('/http_exc', data='test_payload')
    assert resp.status == 404
    assert (await resp.text()) == '404_payload'

    logs = log_extra_tst.logs
    _link = UUID

    assert logs[2] == {
        'level': 'WARNING',
        '_link': _link,
        'msg': 'GET request to /http_exc finished with 404',
        'extdict': {
            '_type': 'response',
            'method': 'GET',
            'uri': '/http_exc',
            'body': '404_payload',
            'meta': [{'n': 'type', 'v': 'http_exc'}, {'n': 'code', 'v': 404}],
            'parent_link': 'x-ya-request-id',
        },
        'exc_info': False,
    }


async def test_log_extra_internal_exc(log_extra_tst):
    resp = await log_extra_tst.get('/internal_exc', data='test_payload')
    assert resp.status == 500
    body_data = {
        'message': 'Internal server error',
        'code': 'INTERNAL_SERVER_ERROR',
        'details': {'reason': 'test_exc'},
    }
    assert (await resp.json()) == body_data

    logs = log_extra_tst.logs
    _link = UUID

    assert json.loads(logs[2]['extdict'].pop('body')) == body_data
    assert logs[2] == {
        'level': 'ERROR',
        '_link': _link,
        'msg': 'GET request to /internal_exc finished with 500',
        'extdict': {
            '_type': 'response',
            'method': 'GET',
            'uri': '/internal_exc',
            'meta': [
                {'n': 'type', 'v': 'internal_exc'},
                {'n': 'code', 'v': 500},
            ],
            'parent_link': 'x-ya-request-id',
        },
        'exc_info': True,
    }


@pytest.mark.parametrize(
    'request_uri,request_body,expected_meta_type',
    [
        # for plain resources
        ('/resources', 'ok_payload', 'resources'),
        ('/resources/', 'ok_payload', 'resources'),
        # for dynamic resources
        ('/resource/9638b1c2d400', 'ok_payload', 'resource/{id}'),
        ('/resource/9638b1c2d400/', 'ok_payload', 'resource/{id}'),
    ],
)
async def test_log_extra_with_variable(
        log_extra_tst, request_uri, request_body, expected_meta_type,
):
    resp = await log_extra_tst.get(request_uri, data=request_body)
    assert resp.status == 200
    assert (await resp.text()) == request_body

    logs = log_extra_tst.logs
    _link = UUID

    expected_result = [
        {
            '_link': _link,
            'exc_info': False,
            'extdict': {},
            'level': 'INFO',
            'msg': 'log_extra app created',
        },
        {
            'level': 'INFO',
            '_link': _link,
            'msg': 'GET request for %s' % request_uri,
            'extdict': {
                '_type': 'request',
                'method': 'GET',
                'uri': request_uri,
                'useragent': 'toster',
                'body': request_body,
                'meta': [{'n': 'type', 'v': expected_meta_type}],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
        {
            'level': 'INFO',
            '_link': _link,
            'msg': 'GET request to %s finished with 200' % request_uri,
            'extdict': {
                '_type': 'response',
                'method': 'GET',
                'uri': request_uri,
                'body': request_body,
                'meta': [
                    {'n': 'type', 'v': expected_meta_type},
                    {'n': 'code', 'v': 200},
                ],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
    ]
    assert logs == expected_result


async def test_link_in_header(log_extra_tst):
    resp = await log_extra_tst.get('/ok')
    assert resp.status == 200
    assert 'X-YaRequestId' in resp.headers

    resp = await log_extra_tst.get('/forbidden_exc')
    assert resp.status == 403
    assert 'X-YaRequestId' in resp.headers

    resp = await log_extra_tst.get('/http_exc')
    assert resp.status == 404
    assert 'X-YaRequestId' in resp.headers

    resp = await log_extra_tst.get('/internal_exc')
    assert resp.status == 500
    assert 'X-YaRequestId' in resp.headers


@pytest.mark.parametrize(
    'request_uri,request_body,request_method,expected_body,expected_code',
    [
        ('/foobar', 'payload', 'get', '404: Not Found', 404),
        ('/ok', 'payload', 'post', '405: Method Not Allowed', 405),
    ],
)
async def test_log_extra_unmatched_url(
        log_extra_tst,
        request_uri,
        request_body,
        request_method,
        expected_body,
        expected_code,
):
    resp = await log_extra_tst.request(
        request_method, request_uri, data=request_body,
    )
    assert resp.status == expected_code

    logs = log_extra_tst.logs
    _link = UUID

    expected_result = [
        {
            '_link': _link,
            'exc_info': False,
            'extdict': {},
            'level': 'INFO',
            'msg': 'log_extra app created',
        },
        {
            'level': 'INFO',
            '_link': _link,
            'msg': '{0} request for {1}'.format(
                request_method.upper(), request_uri,
            ),
            'extdict': {
                '_type': 'request',
                'method': request_method.upper(),
                'uri': request_uri,
                'useragent': 'toster',
                'body': request_body,
                'meta': [],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
        {
            'level': 'WARNING',
            '_link': _link,
            'msg': '{0} request to {1} finished with {2}'.format(
                request_method.upper(), request_uri, expected_code,
            ),
            'extdict': {
                '_type': 'response',
                'method': request_method.upper(),
                'uri': request_uri,
                'body': expected_body,
                'meta': [{'n': 'code', 'v': expected_code}],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': False,
        },
    ]
    assert logs == expected_result
