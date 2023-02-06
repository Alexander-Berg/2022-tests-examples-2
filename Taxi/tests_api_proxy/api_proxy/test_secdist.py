async def test_secdist_access(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('endpoint.yaml')
    await endpoints.safely_create_endpoint(
        '/tests/api-proxy/read-secdist', get_handler=handler_def,
    )
    resp = await taxi_api_proxy.get('/tests/api-proxy/read-secdist')
    assert resp.status_code == 200
    assert resp.json() == {'some-value': 'yep it is'}
