import json

import pytest

from tests_api_proxy.api_proxy.utils import admin


async def test_request_headers_and_args(
        taxi_api_proxy, testpoint, load_yaml, mockserver,
):
    @mockserver.json_handler('/mock-me')
    def mock_resource(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        assert request.headers['X-Test-Header1'] == 'test1'
        assert request.headers['X-Test-Header2'] == 'test2'
        assert request.headers['X-Test-Header3'] == 'test3'
        # Check that internal headers are not forwarded
        assert request.headers['Content-Type'] == 'application/json'
        assert not request.headers.get('Content-Language')
        assert not request.headers.get('content-language')
        assert len(request.headers.getall('X-YaTraceId')) == 1
        assert len(request.headers.getall('X-YaSpanId')) == 1
        assert len(request.headers.getall('X-YaRequestId')) == 1
        assert request.args['arg1'] == '123'
        assert request.args['arg2'] == '456'
        assert request.args['arg3'] == '789'
        assert json.loads(request.get_data()) == {'property': 'value'}
        return {'result': 'test'}

    await admin.create_resource(
        taxi_api_proxy,
        testpoint,
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    handler_def = load_yaml('headers_handler.yaml')
    # disable validation
    handler_def['sources'][0]['validation'] = {}
    handler_def['validation'] = {}

    path = '/test/foo/bar'
    await admin.create_endpoint(
        taxi_api_proxy, testpoint, path, post_handler=handler_def,
    )

    response = await taxi_api_proxy.post(
        'test/foo/bar?arg1=123&arg2=456&arg3=789',
        json={'property': 'value'},
        headers={
            'X-Test-Header1': 'test1',
            'X-Test-Header2': 'test2',
            'X-Test-Header3': 'test3',
            'Content-Language': 'ru-RU',
            'content-language': 'en-EN',
            'content-type': 'application/json',
            'Content-type': 'application/json',
            'Content-Type': 'application/json',
            'X-YaTraceId': '1f07d799935b48f2ad75199414d35532',
            'X-YaSpanId': '21a767b74f88401bb7000ad5be49b928',
            'X-YaRequestId': 'eea9537abdcf446eac4e048fec5a8d87',
        },
    )
    assert mock_resource.times_called == 1
    assert response.status_code == 200
    assert json.loads(response.content) == {'data': 'test'}


async def test_request_headers_response_validation(
        taxi_api_proxy, testpoint, load_yaml, mockserver,
):
    @mockserver.json_handler('/mock-me-good')
    def mock_resource_good(request):
        return mockserver.make_response(
            json={'result': 'test'}, headers={'test-header': 'good_header'},
        )

    @mockserver.json_handler('/mock-me-bad')
    def mock_resource_bad(request):
        return mockserver.make_response(
            json={'result': 'test'}, headers={'Test-Header': 'bad_header'},
        )

    await admin.create_resource(
        taxi_api_proxy,
        testpoint,
        resource_id='test-resource-good',
        url=mockserver.url('mock-me-good'),
        method='post',
    )

    await admin.create_resource(
        taxi_api_proxy,
        testpoint,
        resource_id='test-resource-bad',
        url=mockserver.url('mock-me-bad'),
        method='post',
    )

    handler_def = load_yaml('headers_handler.yaml')
    # disable request validation
    handler_def['validation'] = {}

    # test correct header
    path = '/test/good'
    handler_def['sources'][0]['resource'] = 'test-resource-good'
    await admin.create_endpoint(
        taxi_api_proxy, testpoint, path, post_handler=handler_def,
    )
    response = await taxi_api_proxy.post(
        'test/good?arg1=123&arg2=456&arg3=789', json={'property': 'value'},
    )
    assert mock_resource_good.times_called == 1
    assert response.status_code == 200
    assert json.loads(response.content) == {'data': 'test'}

    # test bad header
    path = '/test/bad'
    handler_def['sources'][0]['resource'] = 'test-resource-bad'
    await admin.create_endpoint(
        taxi_api_proxy, testpoint, path, post_handler=handler_def,
    )
    response = await taxi_api_proxy.post(
        'test/bad?arg1=123&arg2=456&arg3=789', json={'property': 'value'},
    )
    assert mock_resource_bad.times_called == 1
    assert response.status_code == 200
    assert json.loads(response.content) == {'data': 'fallback'}

    # test content-type
    path = '/test/content_type'
    handler_def['sources'][0]['resource'] = 'test-resource-good'
    handler_def['sources'][0]['validation']['content-type'] = 'bad_mime'
    await admin.create_endpoint(
        taxi_api_proxy, testpoint, path, post_handler=handler_def,
    )
    response = await taxi_api_proxy.post(
        'test/content_type?arg1=123&arg2=456&arg3=789',
        json={'property': 'value'},
    )
    assert mock_resource_good.times_called == 2
    assert response.status_code == 200
    assert json.loads(response.content) == {'data': 'fallback'}


@pytest.mark.parametrize(
    'success,header,data',
    [
        (True, 'good_header', 'test'),
        (False, 'bad_header', 'request_validation_fallback'),
    ],
)
async def test_request_headers_request_validation(
        taxi_api_proxy,
        testpoint,
        mockserver,
        load_yaml,
        success,
        header,
        data,
):
    @mockserver.json_handler('/mock-me')
    def mock_resource(request):
        assert request.method == 'POST'
        # Check that internal headers are not forwarded
        assert request.headers['Content-Type'] == 'application/json'
        assert json.loads(request.get_data()) == {'property': 'value'}
        return {'result': 'test'}

    await admin.create_resource(
        taxi_api_proxy,
        testpoint,
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    handler_def = load_yaml('headers_handler.yaml')
    # disable response validation
    handler_def['sources'][0]['validation'] = {}

    path = '/test/foo/bar'
    await admin.create_endpoint(
        taxi_api_proxy, testpoint, path, post_handler=handler_def,
    )

    response = await taxi_api_proxy.post(
        'test/foo/bar?arg1=123&arg2=456&arg3=789',
        json={'property': 'value'},
        headers={'Content-Type': 'application/json', 'Test-Header': header},
    )

    expected_called = 1 if success else 0
    assert mock_resource.times_called == expected_called
    if success:
        assert response.status_code == 200
        assert json.loads(response.content) == {'data': data}
    else:
        assert response.status_code == 400


async def test_headers_search_is_case_insensitive(
        taxi_api_proxy, testpoint, load_yaml, mockserver,
):
    handler_def = load_yaml('headers_handler2.yaml')
    path = '/test/foo/bar'
    await admin.create_endpoint(
        taxi_api_proxy, testpoint, path, get_handler=handler_def,
    )

    response = await taxi_api_proxy.get(
        'test/foo/bar',
        headers={'X-TeSt-HeAdeR1': 'test', 'X-TEST-HEADER2': 'test'},
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {'key1': 'test', 'key2': True}
