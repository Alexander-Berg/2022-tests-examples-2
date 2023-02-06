import asyncio

import pytest


def default_key(mockserver):
    return mockserver.base_url + 'resource:get'


API_CACHE_TESTSUITE_TIMEOUT = pytest.mark.config(
    API_CACHE_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 5000}},
)


@API_CACHE_TESTSUITE_TIMEOUT
async def test_simple_caching(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # cache is empty so api-proxy makes direct request to source
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1
    # wait for the end of asynchronous value caching request
    await api_cache.check_requests(default_key(mockserver), get=True, put=True)

    # cache contains value now, no request to source
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1
    await api_cache.check_requests(default_key(mockserver), get=True)


@API_CACHE_TESTSUITE_TIMEOUT
@pytest.mark.config(
    API_PROXY_ENVOY_PROXY_SETTINGS={
        'enabled': True,
        'localhost_port_proxy': 81,
    },
)
@pytest.mark.parametrize('caching_enabled', [True, False])
async def test_using_envoy(
        taxi_api_proxy,
        testpoint,
        endpoints,
        resources,
        api_cache,
        load_yaml,
        mockserver,
        caching_enabled,
):
    @testpoint('http_request_proxy')
    def http_request_proxy(data):
        assert data['proxy_localhost_url'] == 'http://localhost:81/'

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=caching_enabled,
        use_envoy=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # cache is empty so api-proxy makes direct request to source
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 500
    assert http_request_proxy.times_called == 1


@API_CACHE_TESTSUITE_TIMEOUT
async def test_source_caching_override(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=False,
    )

    path = '/test/foo/bar'
    # caching is turned on in handler source settings
    handler_def = load_yaml('handler_with_cache_settings_override.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # cache is empty so api-proxy makes direct request to source
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1
    # wait for the end of asynchronous value caching request
    await api_cache.check_requests(default_key(mockserver), get=True, put=True)

    # cache contains value now, no request to source
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1
    await api_cache.check_requests(default_key(mockserver), get=True)


@API_CACHE_TESTSUITE_TIMEOUT
async def test_caching_by_max_age(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'value': 'fresh-data'},
            # source sets ttl for response
            headers={'Cache-Control': 'max-age=60'},
        )

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'fresh-data'}
    assert test_resource.times_called == 1
    await api_cache.check_requests(default_key(mockserver), get=True, put=True)
    assert len(api_cache.storage) == 1
    key = list(api_cache.storage)[0]
    assert api_cache.storage[key].ttl == 60


@API_CACHE_TESTSUITE_TIMEOUT
async def test_no_cache_directive(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'value': 'fresh-data'},
            # source sets no-cache directive, max-age shall be ignored
            headers={'Cache-Control': 'max-age=5, no-cache'},
        )

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'fresh-data'}
    assert test_resource.times_called == 1
    await api_cache.check_requests(default_key(mockserver), get=True)


@API_CACHE_TESTSUITE_TIMEOUT
async def test_caching_header_parse_error(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def _test_resource(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'value': 'fresh-data'},
            # broken header
            headers={'Cache-Control': 'asdf'},
        )

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 400


@API_CACHE_TESTSUITE_TIMEOUT
async def test_deserialization_error(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return mockserver.make_response(json={'value': 'fresh-data'})

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    api_cache.insert_key('resource:' + default_key(mockserver), 'bad_data\0')
    # in this mode mock will raise an exception if it fails to find the key
    api_cache.exception_if_not_found = True

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'fresh-data'}
    # api-proxy shall take data from resource, since it fails to extract
    # cached value
    assert test_resource.times_called == 1
    await api_cache.check_requests(default_key(mockserver), get=True, put=True)


@API_CACHE_TESTSUITE_TIMEOUT
async def test_internal_headers_are_skipped(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    # compressed {'value': 'fresh-data'}
    gzip_body = (
        b'\x1f\x8b\x08\x00B6E_\x02\xff\xabV*K\xcc)MU\xb2RJ+J'
        b'-\xce\xd0MI,IT\xaa\x05\x00\x03*\xdb\xc4\x16\x00\x00\x00'
    )

    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            gzip_body,
            headers={
                'Content-Encoding': 'gzip',
                'Content-Type': 'application/json',
            },
        )

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_internal_headers.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'fresh-data'}
    await api_cache.check_requests(default_key(mockserver), get=True, put=True)

    key = 'resource:' + default_key(mockserver)
    assert b'Content-Type' in api_cache.storage[key].value
    assert b'Content-Encoding' in api_cache.storage[key].value
    assert b'X-YaSpanId' not in api_cache.storage[key].value

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'fresh-data'}
    await api_cache.check_requests(default_key(mockserver), get=True)
    assert test_resource.times_called == 1


@pytest.mark.disable_config_check
@pytest.mark.config(TEST_CONFIG='789')
@API_CACHE_TESTSUITE_TIMEOUT
async def test_caching_with_composite_key(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource1')
    def test_resource1(request):
        assert request.method == 'POST'
        value = ':'.join(
            (request.json['id'], request.json['uuid'], request.json['key']),
        )
        return {'value': value}

    @mockserver.json_handler('/resource2')
    def _test_resource2(request):
        return {'uuid': '456'}

    await resources.safely_create_resource(
        resource_id='resource1',
        url=mockserver.url('/resource1'),
        method='post',
    )

    await resources.safely_create_resource(
        resource_id='resource2',
        url=mockserver.url('/resource2'),
        method='get',
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_post_resource.yaml')
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    response = await taxi_api_proxy.post(path, json={'id': '123'})
    assert response.status_code == 200
    assert response.json() == {'result': '123:456:789'}
    assert test_resource1.times_called == 1
    # value caching is done asynchronously, wait until read and write are done
    await api_cache.check_requests('post:123:456:789', get=True, put=True)

    response = await taxi_api_proxy.post(path, json={'id': 'abc'})
    assert response.status_code == 200
    assert response.json() == {'result': 'abc:456:789'}
    assert test_resource1.times_called == 2
    await api_cache.check_requests('post:abc:456:789', get=True, put=True)

    response = await taxi_api_proxy.post(path, json={'id': '123'})
    assert response.status_code == 200
    assert response.json() == {'result': '123:456:789'}
    assert test_resource1.times_called == 2
    await api_cache.check_requests('post:123:456:789', get=True)

    response = await taxi_api_proxy.post(path, json={'id': 'abc'})
    assert response.status_code == 200
    assert response.json() == {'result': 'abc:456:789'}
    assert test_resource1.times_called == 2
    await api_cache.check_requests('post:abc:456:789', get=True)

    assert (
        b'123:456:789' in api_cache.storage['resource1:post:123:456:789'].value
    )
    assert (
        b'abc:456:789' in api_cache.storage['resource1:post:abc:456:789'].value
    )


@API_CACHE_TESTSUITE_TIMEOUT
async def test_api_cache_is_down(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # in this mode api-cache mock will raise timeout error
    api_cache.is_down = True

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1
    await api_cache.check_requests(get=True, put=True)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 2
    await api_cache.check_requests(get=True, put=True)


@API_CACHE_TESTSUITE_TIMEOUT
async def test_request_method_override(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_get_resource_and_body.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # if body is assinged to GET request, userver-http-client implicitly
    # converts request to POST. Check that it doesn't happen
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert test_resource.times_called == 1


@API_CACHE_TESTSUITE_TIMEOUT
async def test_async_save_with_delay(
        taxi_api_proxy,
        endpoints,
        resources,
        api_cache,
        load_yaml,
        mockserver,
        testpoint,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_cacheable_resource.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    task = None
    cond = asyncio.Condition()

    # make sure handler is complete when value saving in cache starts
    @testpoint('testpoint::async_save_response_in_cache')
    async def save_response_testpont(data):
        async with cond:
            await cond.wait_for(lambda: task is not None)
        response = await task
        assert response.status_code == 200
        assert test_resource.times_called == 1

    task = asyncio.create_task(taxi_api_proxy.get(path))
    async with cond:
        cond.notify()

    await api_cache.check_requests(default_key(mockserver), get=True, put=True)
    assert save_response_testpont.times_called == 1


@API_CACHE_TESTSUITE_TIMEOUT
async def test_default_key_with_query(
        taxi_api_proxy, endpoints, resources, api_cache, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': request.query['param']}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
    )

    def key(param):
        return mockserver.base_url + 'resource?param={}:get'.format(param)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_query_param.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    response = await taxi_api_proxy.get(path + '?param=1')
    assert response.status_code == 200
    assert response.json() == {'result': '1'}
    assert test_resource.times_called == 1
    await api_cache.check_requests(key(1), get=True, put=True)

    # cache contains value now, no request to source
    response = await taxi_api_proxy.get(path + '?param=2')
    assert response.status_code == 200
    assert response.json() == {'result': '2'}
    assert test_resource.times_called == 2
    await api_cache.check_requests(key(2), get=True, put=True)

    # param=1 is cached
    response = await taxi_api_proxy.get(path + '?param=1')
    assert response.status_code == 200
    assert response.json() == {'result': '1'}
    assert test_resource.times_called == 2
    await api_cache.check_requests(key(1), get=True)
