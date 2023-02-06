import json


async def test_body_for_logging(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml, testpoint,
):
    @mockserver.json_handler('/resource1')
    def mock_upstream_resource1(request):
        return {'foo': 'MYFOO', 'bar': {'result': 'MYBAR'}}

    @mockserver.json_handler('/resource2')
    def mock_upstream_resource2(request):
        return {'result': {'foobar': ['foo', 'bar']}}

    @testpoint('agl-body-for-logging')
    def _trace_endpoint(request):
        log_data = json.loads(request['body-for-logging'])
        assert log_data == {
            'bar': {'result': 'MYBAR'},
            'foo': 'MYFOO',
            'result': {'foobar': ['foo', 'bar']},
            'testkey': 'testvalue',
        }

    await resources.safely_create_resource(
        resource_id='resource1',
        url=mockserver.url('/resource1'),
        method='get',
        max_retries=1,
    )
    await resources.safely_create_resource(
        resource_id='resource2',
        url=mockserver.url('/resource2'),
        method='get',
        max_retries=1,
    )
    await endpoints.safely_create_endpoint(
        '/ep', post_handler=load_yaml('handler.yaml'),
    )

    response = await taxi_api_proxy.post('/ep', json={'order_id': '123'})
    assert response.status_code == 200
    assert response.json() == {'foo': 'MYFOO', 'bar': {'result': 'MYBAR'}}

    assert mock_upstream_resource1.times_called == 1
    assert mock_upstream_resource2.times_called == 1


async def test_empty_body_for_logging(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml, testpoint,
):
    @mockserver.json_handler('/upstream')
    def mock_upstream(request):
        return {'foo': 'MYFOO', 'bar': {'result': 'MYBAR'}}

    @testpoint('agl-body-for-logging')
    def trace_endpoint(request):
        pass

    await resources.safely_create_resource(
        resource_id='upstream',
        url=mockserver.url('/upstream'),
        method='get',
        max_retries=1,
    )
    await endpoints.safely_create_endpoint(
        '/ep', post_handler=load_yaml('handler_empty_body_for_logging.yaml'),
    )

    response = await taxi_api_proxy.post('/ep', json={'order_id': '123'})
    assert response.status_code == 200
    assert response.json() == {'foo': 'MYFOO', 'bar': {'result': 'MYBAR'}}

    assert mock_upstream.times_called == 1
    assert trace_endpoint.times_called == 0
