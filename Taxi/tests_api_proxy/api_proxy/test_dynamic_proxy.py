import collections
import json


async def test_dynamic_proxy_happy_path(
        taxi_api_proxy, mockserver, load_yaml, endpoints, resources,
):
    @mockserver.json_handler('/mock-me')
    def _mock_cardstorage_card(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        body = json.loads(request.get_data())
        assert body == {'foo': 'bar'}
        return {'data-from-ext-handler': 'Hello world!'}

    # create resource
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    # create endpoint
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(
        path, get_handler=load_yaml('happy_path.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert json.loads(response.content) == {'data': 'Hello world!'}

    # call the endpoint with HEAD req
    response = await taxi_api_proxy.request('head', path)
    assert response.status_code == 200
    assert not response.content

    # call the endpoint with OPTIONS req
    trace_id_header = 'X-YaTraceId'
    trace_id = 'test_trace_id'
    headers = {
        'X-Test-Header1': 'test1',
        'X-Test-Header2': 'test2',
        'X-Test-Header3': 'test3',
        trace_id_header: trace_id,
    }

    response = await taxi_api_proxy.options(path, headers)
    assert response.status_code == 200
    assert not response.content
    assert 'Allow' in response.headers
    assert response.headers[trace_id_header] == trace_id

    allow_methods = response.headers['Allow'].split(', ')
    http_methods = ['GET', 'HEAD', 'OPTIONS']
    assert collections.Counter(http_methods) == collections.Counter(
        allow_methods,
    )

    assert headers.items() <= response.headers.items()


async def test_dynamic_proxy_fallback(
        taxi_api_proxy, load_yaml, pgsql, testpoint, endpoints,
):
    # create endpoint
    path = '/test/fallback'
    await endpoints.safely_create_endpoint(
        path, get_handler=load_yaml('fallback.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert json.loads(response.content) == {'status': 'ok'}

    # break DB
    cursor = pgsql['api-proxy'].cursor()
    cursor.execute('ALTER SCHEMA api_proxy RENAME TO api_proxy_bak')

    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    # force switching to fallback (at least twice)
    for _ in range(2):
        while True:
            await taxi_api_proxy.post('/admin/v1/do-reload-configuration')
            tp_data = (await tp_handler.wait_call())['data']
            if tp_data.get('is_on_fallback', False):
                assert tp_data['state']['total_revision']
                break

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert json.loads(response.content) == {'status': 'ok'}

    # restore DB
    cursor = pgsql['api-proxy'].cursor()
    cursor.execute('ALTER SCHEMA api_proxy_bak RENAME TO api_proxy')


async def test_dynamic_proxy_bad_path_preserve_header(
        taxi_api_proxy, load_yaml, mockserver, endpoints, resources,
):
    @mockserver.json_handler('/mock-me')
    def _mock_cardstorage_card(request):
        return mockserver.make_response('bad request', status=500)

    # create resource
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    # create endpoint
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(
        path, get_handler=load_yaml('happy_path.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 500
    assert 'X-YaTaxi-Api-OperationId' in response.headers


async def test_dynamic_proxy_preserve_forbidden(
        taxi_api_proxy, load_yaml, mockserver, endpoints, resources,
):
    @mockserver.json_handler('/mock-me')
    def _mock_cardstorage_card(request):
        return mockserver.make_response('bad request', status=401)

    # create resource
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    # create endpoint
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(
        path, get_handler=load_yaml('forbidden_path.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 401
    assert 'X-YaTaxi-Api-OperationId' in response.headers
