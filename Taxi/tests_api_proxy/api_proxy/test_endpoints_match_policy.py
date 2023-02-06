import yaml


async def test_basic_flow(taxi_api_proxy, load, endpoints, testpoint):
    post_endpoint, get_endpoint = yaml.load_all(load('basic_endpoints.yaml'))
    await endpoints.safely_create_endpoint(
        '/api.*', post_handler=post_endpoint, get_handler=get_endpoint,
    )
    assert (await taxi_api_proxy.get('/api/foo')).text == 'Basic Get'
    assert (await taxi_api_proxy.post('/api/foo')).text == 'Basic Post'
    assert (await taxi_api_proxy.patch('/api/foo')).status_code == 405

    post_foo, patch_foo = yaml.load_all(load('foo_endpoints.yaml'))
    await endpoints.safely_create_endpoint(
        '/api/foo',
        post_handler=post_foo,
        patch_handler=patch_foo,
        enabled=False,
    )
    assert (await taxi_api_proxy.get('/api/foo')).text == 'Basic Get'
    assert (await taxi_api_proxy.post('/api/foo')).text == 'Basic Post'
    assert (await taxi_api_proxy.patch('/api/foo')).status_code == 405

    await endpoints.safely_update_endpoint(
        '/api/foo',
        prestable=30,
        enabled=True,
        post_handler=post_foo,
        patch_handler=patch_foo,
    )
    for env, post_text, get_code, patch_code in [
            ('prestable', 'Foo Post', 405, 200),
            ('stable', 'Basic Post', 200, 405),
    ]:

        @testpoint('prestable_match_decision')
        def make_decision(request, env_=env):
            assert request['tag'] == '/api/foo'
            return {'decision': env_}

        get_response = await taxi_api_proxy.get('/api/foo')
        assert get_response.status_code == get_code
        if get_code == 200:
            assert get_response.text == 'Basic Get'
        assert (await taxi_api_proxy.post('/api/foo')).text == post_text
        assert (
            await taxi_api_proxy.patch('/api/foo')
        ).status_code == patch_code
        assert make_decision.times_called == 3

    await endpoints.finalize_endpoint_prestable(
        '/api/foo', resolution='release',
    )
    assert (await taxi_api_proxy.get('/api/foo')).status_code == 405
    assert (await taxi_api_proxy.post('/api/foo')).text == 'Foo Post'
    assert (await taxi_api_proxy.patch('/api/foo')).text == 'Foo Patch'
    assert (await taxi_api_proxy.post('/api/foo11')).text == 'Basic Post'
