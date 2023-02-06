import pytest


async def test_api_proxy_xget_request_default_value(
        taxi_api_proxy, endpoints, load_yaml,
):
    # build header def
    path = '/tests/api-proxy/xget-request-default-value'
    handler_def = load_yaml('xget-request-default-value.yaml')

    # create an endpoint
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # get parameters
    query_headers = {'Content-Type': 'foo/bar'}
    query_body = {'uuid': 'foo'}

    # call the endpoint
    response = await taxi_api_proxy.post(
        path, headers=query_headers, json=query_body,
    )
    assert response.status_code == 200
    assert response.json()['uuid'] == 'fallback'


async def test_api_proxy_xget_request(taxi_api_proxy, endpoints, load_yaml):
    # build header def
    path = '/tests/api-proxy/xget-request'
    handler_def = load_yaml('xget-request.yaml')

    # create an endpoint
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # get parameters
    query_params = {'query-param-foo': 'foo', 'query-param-bar': 'bar'}
    query_headers = {'X-TEST-HEADER': 'test'}
    query_body = {'foo': 'bar', 'baz': [{'k~y': 'value'}]}

    # call the endpoint
    response = await taxi_api_proxy.post(
        path, params=query_params, headers=query_headers, json=query_body,
    )
    assert response.status_code == 200
    resp_body = response.json()

    # check a
    assert resp_body['/request']['query'] == query_params
    assert resp_body['/request']['body'] == query_body
    assert {
        k: v
        for k, v in resp_body['/request']['headers'].items()
        if k in query_headers
    } == query_headers

    # check b
    assert resp_body['/request/query'] == query_params
    assert {
        k: v
        for k, v in resp_body['/request/headers'].items()
        if k in query_headers
    } == query_headers
    assert resp_body['/request/body'] == query_body

    # check c
    assert resp_body['/request/query/query-param-bar'] == 'bar'
    assert resp_body['/request/headers/X-TEST-HEADER'] == 'test'
    assert resp_body['/request/body/foo'] == query_body['foo']
    assert resp_body['/request/body/baz'] == query_body['baz']
    assert resp_body['/request/body/baz/0'] == query_body['baz'][0]
    assert resp_body['/request/body/baz/0/k~0y'] == query_body['baz'][0]['k~y']
    assert resp_body['not-exists'] == 'fallback'
    assert resp_body['out-of-bounds'] == 'fallback'


async def test_api_proxy_xget_sources(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml,
):
    source_response_body = {'foo': 'bar', 'bar': [{'key': 'value'}]}
    headers = {
        'Content-Length': '41',
        'Content-Type': 'application/json',
        'Response-Header-1': 'response-header-val-1',
        'Response-Header-2': 'response-header-val-2',
    }

    headers_whitelist = set(headers.keys())

    def filter_headers(hdr):
        for dropped_key in set(hdr.keys()) - headers_whitelist:
            hdr.pop(dropped_key)

    @mockserver.json_handler('/mock-me')
    def _mock_resource(request):
        resp_headers = {
            'Response-Header-1': 'response-header-val-1',
            'Response-Header-2': 'response-header-val-2',
        }
        return mockserver.make_response(
            status=200, json=source_response_body, headers=resp_headers,
        )

    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    path = '/tests/api-proxy/xget-sources'
    handler_def = load_yaml('xget-sources.yaml')
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.post(path)
    assert response.status_code == 200
    resp_body = response.json()

    filter_headers(resp_body['/sources']['foo']['response']['headers'])
    assert resp_body['/sources'] == {
        'foo': {
            'response': {
                'body': source_response_body,
                'status-code': 200,
                'headers': headers,
            },
            'enabled': True,
        },
    }
    filter_headers(resp_body['/sources/foo']['response']['headers'])
    assert resp_body['/sources/foo'] == {
        'response': {
            'body': source_response_body,
            'status-code': 200,
            'headers': headers,
        },
        'enabled': True,
    }
    filter_headers(resp_body['/sources/foo/response']['headers'])
    assert resp_body['/sources/foo/response'] == {
        'body': source_response_body,
        'status-code': 200,
        'headers': headers,
    }
    assert resp_body['/sources/foo/response/body'] == source_response_body
    assert resp_body['/sources/foo/response/code'] == 200
    assert (
        resp_body['/sources/foo/response/body/foo']
        == source_response_body['foo']
    )
    assert (
        resp_body['/sources/foo/response/body/bar']
        == source_response_body['bar']
    )
    assert (
        resp_body['/sources/foo/response/body/bar/0']
        == source_response_body['bar'][0]
    )
    assert (
        resp_body['/sources/foo/response/body/bar/0/key']
        == source_response_body['bar'][0]['key']
    )


async def test_api_proxy_xget_errors(taxi_api_proxy, endpoints, load_yaml):
    path = '/tests/api-proxy/xget-sources'
    handler_def = load_yaml('xget-bad-path.yaml')
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.safely_create_endpoint(path, post_handler=handler_def)
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'validation_failed'


async def test_api_proxy_xget_aliases_good(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml,
):
    mock_data = {'call_order': []}

    @mockserver.json_handler('/mock-me-one')
    def mock_resource_one(request):
        mock_data['call_order'].append('one')
        return mockserver.make_response(json={'foo_key_one': 'foo_val_one'})

    @mockserver.json_handler('/mock-me-two')
    def mock_resource_two(request):
        mock_data['call_order'].append('two')
        return mockserver.make_response(
            json={
                'bar_key_one': 'bar_val_one',
                'bar_key_two': 'bar_val_two',
                'bar_key_three': 'bar_val_three',
                'bar_key_four': True,
            },
        )

    await resources.safely_create_resource(
        resource_id='test-resource-one',
        url=mockserver.url('mock-me-one'),
        method='post',
    )

    await resources.safely_create_resource(
        resource_id='test-resource-two',
        url=mockserver.url('mock-me-two'),
        method='post',
    )

    path = '/tests/api-proxy/xget-aliases-good'
    handler_def = load_yaml('xget-aliases-good.yaml')
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    response = await taxi_api_proxy.post(path)
    assert mock_resource_one.times_called == 1
    assert mock_resource_two.times_called == 1
    assert mock_data['call_order'] == ['two', 'one']
    assert response.status_code == 200
    resp_body = response.json()

    assert resp_body['/aliases/alias1'] == 'some_alias_1'
    assert resp_body['/aliases/alias2'] == 'some_alias_1_some_alias_3'
    assert resp_body['/aliases/alias3'] == 'some_alias_3'
    assert resp_body['/aliases/alias4'] == 'foo_val_one'
    assert resp_body['/aliases/alias5'] == 'bar_val_one'
    assert resp_body['/aliases/alias6'] == 'foo_val_one_bar_val_one'
    assert resp_body['/aliases/alias7'] == 'bar_val_two'
    assert resp_body['/aliases/alias8'] == 'bar_val_three'
    assert resp_body['/aliases/alias9'] is True


async def test_api_proxy_xget_bad_circular_aliases(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml,
):
    @mockserver.json_handler('/mock-me-one')
    def mock_resource_one(request):
        return mockserver.make_response(json={'foo_key_one': 'foo_val_one'})

    await resources.safely_create_resource(
        resource_id='test-resource-one',
        url=mockserver.url('mock-me-one'),
        method='post',
    )

    handler_def = load_yaml('xget-aliases-bad-circular-aliases.yaml')
    path = '/tests/api-proxy/xget-aliases-bad-cycle'

    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.safely_create_endpoint(path, post_handler=handler_def)
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'validation_failed'
    assert exc.value.response.json()['details']['errors'][0][
        'message'
    ].startswith('recursive alias:')
    assert mock_resource_one.times_called == 0


async def test_api_proxy_xget_circular_sources(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml,
):
    @mockserver.json_handler('/mock-me-one')
    def mock_resource_one(request):
        return mockserver.make_response(json={'foo_key_one': 'foo_val_one'})

    @mockserver.json_handler('/mock-me-two')
    def mock_resource_two(request):
        return mockserver.make_response(json={'bar_key_one': 'bar_val_one'})

    await resources.safely_create_resource(
        resource_id='test-resource-one',
        url=mockserver.url('mock-me-one'),
        method='post',
    )

    await resources.safely_create_resource(
        resource_id='test-resource-two',
        url=mockserver.url('mock-me-two'),
        method='post',
    )

    handler_def = load_yaml('xget-aliases-bad-circular-sources.yaml')
    path = '/tests/api-proxy/xget-aliases-bad-src'
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.safely_create_endpoint(path, post_handler=handler_def)
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'validation_failed'
    assert (
        exc.value.response.json()['details']['errors'][0]['message']
        == 'circular dependency found: bar <- foo <- bar'
    )
    assert mock_resource_one.times_called == 0
    assert mock_resource_two.times_called == 0


async def test_api_proxy_xget_aliases_triple_path(
        taxi_api_proxy, endpoints, load_yaml,
):
    # build header def
    path = '/tests/api-proxy/xget-aliases-triple-path'
    handler_def = load_yaml('xget-aliases-triple-path.yaml')

    # create an endpoint
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # get parameters
    query_headers = {'Content-Type': 'application/json'}
    query_body = {'foo': {'bar': {'baz': 'success'}}}

    # call the endpoint
    response = await taxi_api_proxy.post(
        path, headers=query_headers, json=query_body,
    )
    assert response.status_code == 200
    assert response.json()['data'] == 'success'
