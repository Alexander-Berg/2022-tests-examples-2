import pytest


@pytest.mark.parametrize(
    'upstream_response, expected_status, expected_logs',
    [
        ({'foo': 'MYFOO', 'bar': {'result': 'MYBAR'}}, 200, 'all'),
        ({}, 200, 'static'),
        (500, 500, 'static'),
    ],
)
async def test_logging(
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        load_yaml,
        testpoint,
        upstream_response,
        expected_status,
        expected_logs,
):
    @mockserver.json_handler('/upstream')
    def mock_upstream(request):
        if isinstance(upstream_response, dict):
            return upstream_response
        return mockserver.make_response(status=upstream_response)

    @testpoint('agl-user-log')
    def trace_endpoint(request):
        pass

    await resources.safely_create_resource(
        resource_id='upstream',
        url=mockserver.url('/upstream'),
        method='get',
        max_retries=1,
    )
    await endpoints.safely_create_endpoint(
        '/ep', post_handler=load_yaml('handler.yaml'),
    )

    response = await taxi_api_proxy.post('/ep', json={'order_id': '123'})
    assert response.status_code == expected_status

    assert mock_upstream.times_called == 1
    assert trace_endpoint.next_call()['request'] == {
        'text': '',
        'tags': {'meta_order_id': '123'},
        'extra': {},
        'level': 'info',
    }
    assert trace_endpoint.next_call()['request'] == {
        'text': 'Start handling...',
        'tags': {},
        'extra': {'tag': '"MYTAG"'},
        'level': 'info',
    }
    assert trace_endpoint.next_call()['request'] == {
        'text': 'Test logging level',
        'tags': {},
        'extra': {},
        'level': 'warning',
    }

    if expected_logs == 'all':
        assert trace_endpoint.next_call()['request'] == {
            'text': 'Upstream returned foo=MYFOO, bar: MYBAR',
            'tags': {},
            'extra': {'bar': '{"result":"MYBAR"}'},
            'level': 'info',
        }
    assert trace_endpoint.times_called == 0, trace_endpoint.next_call()
