import pytest

UPSTREAM_RESPONSE = """
<html>
    <head>
        <title>Hello, world!</head>
    <body>
        <marquee> Welcome to our web server!!</marquee>
</html>
"""


async def test_html_content_type(
        mockserver, resources, load_yaml, endpoints, taxi_api_proxy,
):
    @mockserver.handler('/upstream')
    async def mock_upstream(request):
        assert request.content_type == 'text/plain'
        return mockserver.make_response(
            UPSTREAM_RESPONSE, status=200, content_type='text/html',
        )

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='post',
    )
    await endpoints.safely_create_endpoint(
        '/endpoint', get_handler=load_yaml('endpoint.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get('/endpoint')
    assert response.status_code == 200
    assert response.content_type == 'text/html'
    assert response.text == UPSTREAM_RESPONSE

    assert mock_upstream.times_called == 1


async def test_json_content_type(
        mockserver, resources, load_yaml, endpoints, taxi_api_proxy,
):
    @mockserver.handler('/upstream')
    async def mock_upstream(request):
        return mockserver.make_response(
            '{"ok": true}',
            status=200,
            content_type='application/json',
            charset='utf-8',
        )

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='post',
    )
    await endpoints.safely_create_endpoint(
        '/endpoint', get_handler=load_yaml('endpoint_json_shortcut.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.get('/endpoint')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json() == {'ok': True}

    assert mock_upstream.times_called == 1


@pytest.mark.parametrize(
    'ep_name, expected_code, upstream_called',
    [
        ('endpoint_json_shortcut.yaml', 200, 1),
        (
            'endpoint_json_parse_response.yaml',
            400,  # todo: this actually looks like a bug,
            # because we should probably 500, if cannot parse upstream
            1,
        ),
        ('endpoint_json_parse_request.yaml', 400, 0),
    ],
)
async def test_invalid_json(
        mockserver,
        resources,
        load_yaml,
        endpoints,
        taxi_api_proxy,
        ep_name,
        expected_code,
        upstream_called,
):
    @mockserver.handler('/upstream')
    async def mock_upstream(request):
        return mockserver.make_response(
            '{"ok": true',
            status=200,
            content_type='application/json',
            charset='utf-8',
        )

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='post',
    )
    await endpoints.safely_create_endpoint(
        '/endpoint', post_handler=load_yaml(ep_name),
    )

    # call the endpoint with invalid json
    response = await taxi_api_proxy.post(
        '/endpoint', data='{12', headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == expected_code
    assert mock_upstream.times_called == upstream_called

    # call endpoint with empty body. Mock returns invalid json
    response = await taxi_api_proxy.post('/endpoint')
    assert response.status_code == expected_code
    assert mock_upstream.times_called == upstream_called + 1


async def test_empty_body_for_get(endpoints, load_yaml, taxi_api_proxy):
    await endpoints.safely_create_endpoint(
        '/test-endpoint', get_handler=load_yaml('test_endpoint.yaml'),
    )

    response = await taxi_api_proxy.get(
        '/test-endpoint', headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'request_content_type', ['text/plain', 'applicatoin/json'],
)
@pytest.mark.parametrize(
    'response_content_type', ['text/html', 'application/json'],
)
async def test_agl_content_type(
        mockserver,
        resources,
        load_yaml,
        endpoints,
        taxi_api_proxy,
        request_content_type,
        response_content_type,
):
    resp_content = {
        'application/json': {'resp': 'ok'},
        'text/html': UPSTREAM_RESPONSE,
    }

    @mockserver.handler('/upstream')
    async def mock_upstream(request):
        assert request.content_type == request_content_type
        if response_content_type == 'application/json':
            return mockserver.make_response(
                json=resp_content[response_content_type],
                status=200,
                content_type=response_content_type,
            )
        if response_content_type == 'text/html':
            return mockserver.make_response(
                resp_content[response_content_type],
                status=200,
                content_type=response_content_type,
            )
        assert False, 'response for this type is not defined in test'

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='post',
    )
    await endpoints.safely_create_endpoint(
        '/endpoint', post_handler=load_yaml('endpoint_agl.yaml'),
    )

    # call the endpoint
    response = await taxi_api_proxy.post(
        '/endpoint', headers={'Content-Type': request_content_type},
    )
    assert response.status_code == 200
    assert response.content_type == response_content_type

    if response_content_type == 'application/json':
        assert response.json() == resp_content[response_content_type]
    elif response_content_type == 'text/html':
        assert response.text == resp_content[response_content_type]
    else:
        assert False, 'response for this type is not defined in test'

    assert mock_upstream.times_called == 1
