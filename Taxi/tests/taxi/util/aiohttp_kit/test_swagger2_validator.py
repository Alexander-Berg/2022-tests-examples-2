# pylint: disable=invalid-name
# pylint: disable=protected-access
import io
import os

import aiohttp
from aiohttp import web
import pytest

from taxi import config
from taxi import web_app
from taxi.util.aiohttp_kit import swagger2_validator


@pytest.mark.parametrize(
    'params, expected_status',
    [
        ({'arg1': 'some_value'}, 200),
        ({'arg1': 'badvalue'}, 400),
        ({'arg1': 'loooooong_value'}, 400),
        ({'arg1': 'some_value', 'arg2': '123'}, 200),
        ({'arg1': 'some_value', 'arg2': '-123'}, 200),
        ({'arg1': 'some_value', 'arg2': '456'}, 400),
        ({'arg1': 'some_value', 'arg2': '-456'}, 400),
        ({'arg1': 'some_value', 'arg3': '123'}, 200),
        ({'arg1': 'some_value', 'arg3': '123.456'}, 200),
        ({'arg1': 'some_value', 'arg3': '-123.456'}, 200),
        ({'arg1': 'some_value', 'arg3': '.456'}, 200),
        ({'arg1': 'some_value', 'arg3': '123.'}, 200),
        ({'arg1': 'some_value', 'arg2': 'qwe'}, 400),
        ({'arg1': 'some_value', 'arg2': '-'}, 400),
        ({'arg1': 'some_value', 'arg2': ''}, 200),
        ({'arg1': 'some_value', 'arg3': 'qwe'}, 400),
        ({'arg1': 'some_value', 'arg3': '-.'}, 400),
        ({'arg1': 'some_value', 'arg3': ''}, 200),
        ({'arg1': 'some_value', 'arg4': 'one'}, 200),
        ({'arg1': 'some_value', 'arg4': 'two'}, 200),
        ({'arg1': 'some_value', 'arg4': 'three'}, 200),
        ({'arg1': 'some_value', 'arg4': 'four'}, 400),
        ({}, 400),
    ],
)
async def test_flex_validate_params(
        aiohttp_client, loop, db, simple_secdist, params, expected_status,
):
    def _dummy_handler(request):
        return web.json_response({'prop3': 'qwerty'})

    app = _create_app(loop, db, '/test/path/{id}', _dummy_handler)

    client = await aiohttp_client(app)
    response = await client.post(
        '/test/path/some_id', params=params, json={'prop2': 123},
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    'body, expected_status',
    [
        ({'prop2': 123}, 200),
        ({'prop1': '123', 'prop2': 123}, 200),
        ({'prop1': 'qwe', 'prop2': 123}, 400),
        ({'prop1': '123'}, 400),
        ({}, 400),
    ],
)
async def test_flex_validate_body(
        aiohttp_client, loop, db, simple_secdist, body, expected_status,
):
    def _dummy_handler(request):
        return web.json_response({'prop3': 'qwerty'})

    app = _create_app(loop, db, '/test/path/{id}', _dummy_handler)

    client = await aiohttp_client(app)
    response = await client.post(
        '/test/path/some_id', params={'arg1': 'some_value'}, json=body,
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'validation_enabled, url, response, expected_status',
    [
        (True, '/test/path/{id}', {'prop3': 'qwerty'}, 200),
        (True, '/test/path/{id}', {'prop4': 'qwerty'}, 500),
        (True, '/test/path/{id}', {}, 500),
        (False, '/test/path/{id}', {'prop4': 'qwerty'}, 200),
        (False, '/test/path/{id}', {}, 200),
        (True, '/test/array/response', {'prop3': [{'prop4': 'qwerty'}]}, 200),
        (True, '/test/array/response', [{'prop4': 'qwerty'}], 500),
    ],
)
async def test_flex_validate_response(
        aiohttp_client,
        loop,
        db,
        simple_secdist,
        monkeypatch,
        validation_enabled,
        url,
        response,
        expected_status,
):
    def _dummy_handler(request):
        return web.json_response(response)

    app = _create_app(loop, db, url, _dummy_handler)
    monkeypatch.setattr(app.settings, 'VALIDATE_RESPONSES', validation_enabled)

    client = await aiohttp_client(app)
    response = await client.post(
        url.replace('{id}', 'some_id'),
        params={'arg1': 'some_value'},
        json={'prop2': 123},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'body, expected_status',
    [
        ('some,field\nvalue1,value2\n', 200),
        ('some,field\nкириллица,эмодзи 🔥\n', 200),
    ],
)
async def test_flex_validate_csv_upload(
        aiohttp_client, loop, db, simple_secdist, body, expected_status,
):
    async def _dummy_handler(request):
        return web.json_response({})

    form_data = aiohttp.FormData()
    form_data.add_field(
        'csv_file',
        io.BytesIO(body.encode('utf8')),
        filename='test.csv',
        content_type='text/csv',
    )

    app = _create_app(loop, db, '/test/upload', _dummy_handler)

    client = await aiohttp_client(app)
    response = await client.post(
        '/test/upload',
        data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'skip_paths, test_request, response, expected_status',
    [
        (
            None,
            {'json': {'prop2': 123}, 'params': {'arg1': 'some_value'}},
            {'prop3': 'qwerty'},
            200,
        ),
        (None, {'json': {}}, {}, 400),
        ({'/test/path/{id}'}, {'json': {}}, {}, 200),
        (
            None,
            {'json': {'prop2': 123}, 'params': {'arg1': 'some_value'}},
            {},
            500,
        ),
        (
            {'/test/path/{id}'},
            {'json': {'prop2': 123}, 'params': {'arg1': 'some_value'}},
            {},
            200,
        ),
    ],
)
async def test_skip_paths(
        aiohttp_client,
        loop,
        db,
        simple_secdist,
        skip_paths,
        test_request,
        response,
        expected_status,
):
    def _dummy_handler(request):
        return web.json_response(response)

    app = _create_app(loop, db, '/test/path/{id}', _dummy_handler, skip_paths)

    client = await aiohttp_client(app)
    response = await client.post('/test/path/some_id', **test_request)
    assert response.status == expected_status


def _create_app(loop, db, path, handler, skip_paths=None):
    app = web_app.TaxiApplication(
        config_cls=config.Config, loop=loop, db=db, service_name='TEST',
    )
    app.router.add_post(path, handler)
    app.swagger2_validator = swagger2_validator.Swagger2Validator(
        os.path.join(
            os.path.dirname(__file__),
            'static',
            os.path.splitext(os.path.basename(__file__))[0],
            'test.yaml',
        ),
    )
    app.middlewares.append(
        swagger2_validator.swagger2_validation_middleware(skip_paths),
    )
    return app
