import pytest


async def test_default_value_simple(
        taxi_api_proxy, endpoints, resources, load_yaml, mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource', url=mockserver.url('/resource'), method='get',
    )

    path = '/test/foo/bar'
    handler_def1 = load_yaml('handler_simple.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def1)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1


@pytest.mark.parametrize(
    'body,expected_response',
    [
        ('1', 'response-first'),
        ('2', 'response-second'),
        ('3', 'response-third'),
    ],
)
async def test_default_value_smarter(
        taxi_api_proxy,
        endpoints,
        resources,
        load_yaml,
        mockserver,
        body,
        expected_response,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': body}

    await resources.safely_create_resource(
        resource_id='resource', url=mockserver.url('/resource'), method='get',
    )

    path = '/test/foo/bar'
    handler_def1 = load_yaml('handler_smarter.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def1)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': expected_response}
    assert test_resource.times_called == 1
