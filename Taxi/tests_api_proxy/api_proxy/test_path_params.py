import pytest


async def test_path_params(
        mockserver, resources, load_yaml, endpoints, taxi_api_proxy,
):
    @mockserver.handler('/upstream/lafka/5')
    async def mock_upstream(request):
        assert request.content_type == 'application/json'
        assert request.json == ['lafka']
        return mockserver.make_response(
            'ok', status=200, content_type='text/html',
        )

    await resources.safely_create_resource(
        resource_id='upstream',
        url=mockserver.url('upstream/{name}/{id}'),
        method='post',
    )
    await endpoints.safely_create_endpoint(
        r'/endpoint/(?<name>\w+)', get_handler=load_yaml('endpoint.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get('/endpoint/lafka')
    assert response.status_code == 200
    assert response.text == 'ok'
    assert mock_upstream.times_called == 1


@pytest.mark.parametrize('reverse_endpoint_creation', [True, False])
@pytest.mark.parametrize(
    'url, expected_backend',
    [
        ('/endpoint/api/v1/catalog/moscow', 'catalog'),
        ('/endpoint/api/v1/catalog/ekb', 'catalog'),
        ('/endpoint/api/v1/catalog/moscow/', 'common'),  # slash!
        ('/endpoint/api/v1/menu/moscow', 'common'),
        ('/endpoint/api/v1/catalog/moscow/menu', 'common'),
        ('/endpoint/api/v2/catalog/moscow', 'common'),
    ],
)
async def test_path_prefix(
        mockserver,
        resources,
        load_yaml,
        endpoints,
        taxi_api_proxy,
        url,
        expected_backend,
        reverse_endpoint_creation,
):
    @mockserver.handler('/upstream')
    async def mock_upstream(request):
        assert request.content_type == 'application/json'
        assert request.json == {'path': url, 'backend': expected_backend}
        return mockserver.make_response(
            'ok', status=200, content_type='text/html',
        )

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='post',
    )
    endpoint_params = [
        {
            'path': r'/endpoint/api/v1/catalog/(?<name>\w+)',
            'get_handler': load_yaml('endpoint_catalog.yaml'),
        },
        {
            'path': r'/endpoint/api.*',
            'get_handler': load_yaml('endpoint_common.yaml'),
        },
    ]
    if reverse_endpoint_creation:
        endpoint_params = reversed(endpoint_params)
    for kwargs in endpoint_params:
        await endpoints.safely_create_endpoint(**kwargs)

    # call the endpoint
    response = await taxi_api_proxy.get(url)
    assert response.status_code == 200
    assert response.text == 'ok'
    assert mock_upstream.times_called == 1
