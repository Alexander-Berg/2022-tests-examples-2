async def test_fail_policy(
        taxi_api_proxy, resources, endpoints, mockserver, load_yaml,
):
    @mockserver.json_handler('/mock-me')
    def _mock_me(request):
        return mockserver.make_response(json={'some': 'data'}, status=409)

    # create resource
    await resources.safely_create_resource(
        resource_id='mock-me', url=mockserver.url('mock-me'), method='post',
    )

    # create an endpoint
    handler_def = load_yaml('fail_policy.yaml')
    path = '/tests/api-proxy/fail_policy'
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # call the handler
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 409
    assert response.json() == {'some': 'data'}
