import base64
import functools
import json

import pytest


def _calls(func):
    calls = []

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        calls.append({'args': args, 'kwargs': kwargs, 'result': result})
        return result

    wrapper.calls = calls

    return wrapper


@pytest.mark.parametrize(
    (
        'brand_id',
        'request_body',
        'request_json',
        'response_type',
        'response_body',
        'response_status',
        'response_content_type',
        'solomon_calls',
        'partner_data',
    ),
    [
        (
            None,
            '',
            None,
            'string',
            b'',
            200,
            'application/octet-stream',
            3,
            'has_port',
        ),
        (
            None,
            '',
            None,
            'string',
            b'',
            200,
            'application/octet-stream',
            3,
            'has_null_port',
        ),
        (None, '', None, 'string', b'', 200, 'text/plain', 3, 'has_port'),
        (None, '', None, 'string', b'', 200, 'text/plain', 3, 'has_null_port'),
        (None, '', None, 'json', b'', 400, 'text/plain', 3, 'has_port'),
        (None, '', None, 'json', b'', 400, 'text/plain', 3, 'has_null_port'),
        (
            None,
            '<b>request</b>',
            None,
            'string',
            b'{"response": "data"}',
            200,
            'text/plain',
            3,
            'has_port',
        ),
        (
            None,
            '<b>request</b>',
            None,
            'string',
            b'{"response": "data"}',
            200,
            'text/plain',
            3,
            'has_null_port',
        ),
        (
            None,
            '<b>request</b>',
            None,
            'json',
            b'{"response": "data"}',
            200,
            'application/json',
            3,
            'has_port',
        ),
        (
            None,
            '<b>request</b>',
            None,
            'json',
            b'{"response": "data"}',
            200,
            'application/json',
            3,
            'has_null_port',
        ),
        (
            None,
            None,
            {'request': ''},
            'json',
            b'{"response": "data"}',
            200,
            'application/json',
            3,
            'has_port',
        ),
        (
            None,
            None,
            {'request': ''},
            'json',
            b'{"response": "data"}',
            200,
            'application/json',
            3,
            'has_null_port',
        ),
        (
            'wrong_brand_id',
            '',
            None,
            'string',
            b'',
            404,
            'application/octet-stream',
            1,
            'has_port',
        ),
        (
            'wrong_brand_id',
            '',
            None,
            'string',
            b'',
            404,
            'application/octet-stream',
            1,
            'has_null_port',
        ),
    ],
)
async def test_proxy_post(
        web_app_client,
        mockserver,
        load_json,
        brand_id,
        request_body,
        request_json,
        response_body,
        response_type,
        response_status,
        response_content_type,
        web_app,
        solomon_calls,
        partner_data,
):
    partner_json = load_json('partner_data.json')[partner_data]
    response = await web_app_client.post('/partner', json=partner_json)
    assert response.status == 200

    @mockserver.handler('/test_path')
    def _get_test_path(request):
        return mockserver.make_response(
            response_body, response_status, content_type=response_content_type,
        )

    request_data = {
        'brand_id': partner_json['brand_id'],
        'slug': partner_json['slug'],
        'request': {
            'method': 'POST',
            'path': 'test_path',
            'params': {},
            'headers': {},
        },
        'response_type': response_type,
    }
    if request_body is not None:
        request_data['request']['data_base64'] = base64.b64encode(
            request_body.encode(),
        ).decode()
    if request_json is not None:
        request_data['request']['json'] = request_json
    if brand_id is not None:
        request_data['brand_id'] = brand_id

    await web_app['context'].update_cache.run()

    response = await web_app_client.post('/proxy', json=request_data)
    assert response.status == response_status

    if response_status == 200:
        content = json.loads((await response.read()).decode('utf-8')).get(
            'body', '',
        )
        if response_type == 'string':
            assert content == response_body.decode('utf-8')
        if response_type == 'json':
            assert content == json.loads(response_body.decode('utf-8'))


@pytest.mark.parametrize(
    (
        'request_params',
        'response_body',
        'response_status',
        'response_type',
        'response_content_type',
        'partner_data',
    ),
    [
        (
            {'login': 'login'},
            b'response text',
            200,
            'string',
            'application/octet-stream',
            'has_port',
        ),
        (
            {'login': 'login'},
            b'response text',
            200,
            'string',
            'application/octet-stream',
            'has_null_port',
        ),
        (
            {'login': 'login'},
            b'response text',
            200,
            'string',
            'text/plain',
            'has_port',
        ),
        (
            {'login': 'login'},
            b'response text',
            200,
            'string',
            'text/plain',
            'has_null_port',
        ),
        (
            {'login': 'login'},
            b'error text',
            400,
            'json',
            'text/plain',
            'has_port',
        ),
        (
            {'login': 'login'},
            b'error text',
            400,
            'json',
            'text/plain',
            'has_null_port',
        ),
        (
            {'login': 'login'},
            b'{"response": "text"}',
            200,
            'json',
            'application/json',
            'has_port',
        ),
        (
            {'login': 'login'},
            b'{"response": "text"}',
            200,
            'json',
            'application/json',
            'has_null_port',
        ),
    ],
)
async def test_proxy_get(
        web_app_client,
        mockserver,
        load_json,
        request_params,
        response_body,
        response_status,
        response_type,
        response_content_type,
        web_app,
        partner_data,
):
    partner_json = load_json('partner_data.json')[partner_data]
    response = await web_app_client.post('/partner', json=partner_json)
    assert response.status == 200

    @mockserver.handler('/test_path')
    def _get_test_path(request):
        return mockserver.make_response(
            response_body, response_status, content_type=response_content_type,
        )

    request_data = {
        'brand_id': partner_json['brand_id'],
        'slug': partner_json['slug'],
        'request': {
            'method': 'GET',
            'path': 'test_path',
            'params': {},
            'headers': {},
        },
        'response_type': response_type,
    }
    if request_params is not None:
        request_data['request']['params'].update(request_params)

    await web_app['context'].update_cache.run()

    response = await web_app_client.post('/proxy', json=request_data)

    assert response.status == response_status

    if response_status == 200:
        content = json.loads((await response.read()).decode('utf-8')).get(
            'body', '',
        )
        if response_type == 'string':
            assert content == response_body.decode('utf-8')
        if response_type == 'json':
            assert content == json.loads(response_body.decode('utf-8'))
