async def test_response_headers(
        taxi_api_proxy, resources, endpoints, testpoint, load_yaml, mockserver,
):
    @mockserver.json_handler('/mock-me')
    def mock_resource(request):
        resp_headers = {
            'test_header1': 'test_header_value',
            'Content-MD5': 'Q2h1Y2sgSW51ZwDIAXR5IQ==',
            'content-length': '18',
            'other_header': 'other_header_value',
        }
        return mockserver.make_response(
            status=200, json={'result': 'test'}, headers=resp_headers,
        )

    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    handler_def = load_yaml('headers_handler.yaml')
    path = '/test/foo/bar'
    endpoint_id = 'foo-bar'
    await endpoints.safely_create_endpoint(
        path, endpoint_id=endpoint_id, post_handler=handler_def,
    )

    response = await taxi_api_proxy.post(
        'test/foo/bar',
        json={'property': 'value'},
        headers={'content-type': 'application/json'},
    )
    assert mock_resource.times_called == 1
    assert response.status_code == 200

    # check headers
    assert len(response.headers) >= 10
    assert 'Server' in response.headers
    assert 'Date' in response.headers
    assert 'X-YaRequestId' in response.headers
    assert response.headers['X-YaTaxi-Api-OperationId'] == endpoint_id
    assert response.headers['Connection'] == 'keep-alive'
    assert response.headers['Content-Type'] == 'application/json'
    assert response.headers['test_header1'] == 'test_header_value'
    assert response.headers['other_header'] == 'other_header_value'

    # check body
    response = response.json()
    assert len(response['all_headers']) == 7
    response['all_headers'].pop('Date')
    response['all_headers'].pop('Server')
    assert response == {
        'single_header': 'test_header_value',
        'all_headers': {
            'Content-MD5': 'Q2h1Y2sgSW51ZwDIAXR5IQ==',
            'Content-Type': 'application/json',
            'content-length': '18',
            'test_header1': 'test_header_value',
            'other_header': 'other_header_value',
        },
    }
