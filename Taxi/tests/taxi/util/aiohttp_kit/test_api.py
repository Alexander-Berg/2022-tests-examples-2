# pylint: disable=protected-access,redefined-outer-name
import functools
import json
import logging
import os

from aiohttp import web
import pytest

from taxi import config
from taxi import web_app
from taxi.util.aiohttp_kit import api
from taxi.util.aiohttp_kit import middleware

TEST_OBJECT_REF = 'ref.yaml#/components/schemas/TestObject'


@pytest.fixture
async def app(test_taxi_app, simple_secdist, monkeypatch):
    @api.require_api_tokens
    async def handler(request):
        return web.Response()

    @api.require_api_tokens
    @api.require_role('admin')
    async def protected_handler(request):
        return web.Response()

    @api.require_api_token
    async def require_token_handler(request):
        return web.Response()

    @api.optional_api_token
    async def optional_token_handler(request):
        return web.Response()

    setattr(
        test_taxi_app,
        'api_roles_by_token',
        {'admin-api-token': 'admin', 'guest-api-token': 'guest'},
    )
    setattr(test_taxi_app, 'api_token', 'token')

    test_taxi_app.router.add_get('/test', handler)
    test_taxi_app.router.add_get('/test/protected', protected_handler)
    test_taxi_app.router.add_get('/test/require_token', require_token_handler)
    test_taxi_app.router.add_get('/test/optional', optional_token_handler)
    test_taxi_app.middlewares.append(middleware.use_log_extra())
    return test_taxi_app


@pytest.fixture
async def client(app, aiohttp_client):
    return await aiohttp_client(app)


@pytest.fixture
def schemes_path(search_path):
    static_path = next(search_path('ref.yaml'))
    return os.path.dirname(static_path)


@pytest.fixture
async def get_client(
        loop,
        db,
        simple_secdist,
        collected_logs_with_link,
        aiohttp_client,
        schemes_path,
):
    finalizers = []

    async def client(method, route, handler):
        log_settings = {
            'logger_names': ['taxi'],
            'ident': 'test',
            'log_level': logging.INFO,
            'log_format': '',
        }

        app = web_app.TaxiApplication(
            config_cls=config.Config,
            log_settings=log_settings,
            loop=loop,
            db=db,
            service_name='TEST',
            schemes_path=schemes_path,
        )
        app.router.add_route(method, route, handler)
        app.middlewares.append(middleware.use_log_extra())

        client = await aiohttp_client(
            app,
            headers={
                'User-Agent': 'toster',
                'X-YaRequestId': 'x-ya-request-id',
            },
        )
        client.logs = collected_logs_with_link

        finalizers.append(functools.partial(web_app._logger_cleanup, app))

        await web_app._logger_startup(app)
        return client

    yield client

    for finalize in finalizers:
        await finalize()


async def test_request_serialization(get_client):
    @api.json_serializer(request_ref=TEST_OBJECT_REF)
    async def handler(request):
        return await request.json()

    client = await get_client('POST', '/route', handler)

    resp = await client.post('/route', json={'price': 100})
    assert resp.status == 200


# pylint: disable=invalid-name
@pytest.mark.parametrize('verbose_errors', [True, False])
async def test_invalid_request_serialization(get_client, verbose_errors):
    @api.json_serializer(
        request_ref=TEST_OBJECT_REF, verbose_errors=verbose_errors,
    )
    async def handler(request):
        return await request.json()

    client = await get_client('POST', '/route', handler)
    resp = await client.post('/route', json={'price': 'xxx'})

    assert resp.status == 400

    if verbose_errors:
        assert await resp.json() == {
            'status': 'error',
            'message': 'Invalid input',
            'code': 'invalid-input',
            'details': {'price': ['\'xxx\' is not of type \'number\'']},
        }
    else:
        response_log = client.logs[2]
        _link = client.logs[2]['_link']
        expected_log = {
            'level': 'WARNING',
            '_link': _link,
            'extdict': {
                'uri': '/route',
                'method': 'POST',
                'meta': [{'n': 'type', 'v': 'route'}, {'n': 'code', 'v': 400}],
                '_type': 'response',
                'validation_error': (
                    '\'xxx\' is not of type \'number\'\n'
                    '\n'
                    'Failed validating \'type\' in '
                    'schema[\'properties\'][\'price\']:\n'
                    '    {\'type\': \'number\'}\n'
                    '\n'
                    'On instance[\'price\']:\n'
                    '    \'xxx\''
                ),
                'parent_link': 'x-ya-request-id',
            },
            'msg': 'POST request to /route finished with 400',
            'exc_info': False,
        }
        assert response_log == expected_log


async def test_response_serialization(get_client):
    @api.json_serializer(response_ref=TEST_OBJECT_REF)
    async def handler(request):
        return await request.json()

    client = await get_client('POST', '/route', handler)
    resp = await client.post('/route', json={'price': 100})
    assert resp.status == 200
    assert await resp.json() == {'price': 100}


# pylint: disable=invalid-name
@pytest.mark.parametrize('validate_responses', [True, False])
@pytest.mark.parametrize('verbose_errors', [True, False])
async def test_invalid_response_serialization(
        get_client, verbose_errors, validate_responses, monkeypatch,
):
    monkeypatch.setattr(
        'taxi.settings.Settings.VALIDATE_RESPONSES', validate_responses,
    )

    @api.json_serializer(
        response_ref=TEST_OBJECT_REF, verbose_errors=verbose_errors,
    )
    async def handler(request):
        return await request.json()

    client = await get_client('POST', '/route', handler)

    resp = await client.post('/route', json={'price': 'xxx'})

    if validate_responses:
        assert resp.status == 500
        body = {
            'message': 'Internal server error',
            'code': 'INTERNAL_SERVER_ERROR',
            'details': {
                'reason': (
                    """
'xxx' is not of type 'number'

Failed validating 'type' in schema['properties']['price']:
    {'type': 'number'}

On instance['price']:
    'xxx'
    """.strip()
                ),
            },
        }
        assert await resp.json() == body

        response_log = client.logs[2]
        _link = client.logs[1]['_link']

        assert json.loads(response_log['extdict'].pop('body')) == body
        assert response_log == {
            'level': 'ERROR',
            '_link': _link,
            'msg': 'POST request to /route finished with 500',
            'extdict': {
                '_type': 'response',
                'method': 'POST',
                'uri': '/route',
                'meta': [{'n': 'type', 'v': 'route'}, {'n': 'code', 'v': 500}],
                'parent_link': 'x-ya-request-id',
            },
            'exc_info': True,
        }
    else:
        assert resp.status == 200


def test_invalid_scheme_loading(schemes_path):
    store = api.JsonValidatorStore(schemes_path)
    with pytest.raises(TypeError) as excinfo:
        _ = store['invalid.yaml#/something']
    assert excinfo.value.args == ('Schema must be an instance of dict',)


@pytest.mark.parametrize(
    'path, apikey, expected_status',
    [
        ('/test', 'admin-api-token', 200),
        ('/test', 'guest-api-token', 200),
        ('/test', 'token', 403),
        ('/test', None, 403),
        ('/test/protected', 'admin-api-token', 200),
        ('/test/protected', 'guest-api-token', 403),
        ('/test/protected', 'token', 403),
        ('/test/protected', None, 403),
        ('/test/require_token', 'token', 200),
        ('/test/require_token', 'guest-api-token', 403),
        ('/test/require_token', None, 403),
        ('/test/optional', 'token', 200),
        ('/test/optional', 'guest-api-token', 403),
        ('/test/optional', None, 200),
    ],
)
async def test_require_role(client, path, apikey, expected_status):
    headers = {'X-YaTaxi-API-Key': apikey} if apikey else None
    resp = await client.get(path, headers=headers)
    assert resp.status == expected_status
