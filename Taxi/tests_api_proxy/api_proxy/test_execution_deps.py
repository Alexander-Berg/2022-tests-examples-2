import pytest


@pytest.mark.parametrize(
    'ep_file',
    [
        'handlers/static.yaml',
        'handlers/static_if.yaml',
        'handlers/experiment.yaml',
        'handlers/request.yaml',
    ],
)
async def test_execution_deps(
        taxi_api_proxy, resources, endpoints, ep_file, mockserver, load_yaml,
):
    for resource in ['conditional', 'unconditional', 'dependency']:
        await resources.safely_create_resource(
            resource_id=resource,
            url=mockserver.url(resource),
            method='post',
            max_retries=1,
        )
    await endpoints.safely_create_endpoint(
        '/ep', post_handler=load_yaml(ep_file),
    )

    @mockserver.json_handler('/dependency')
    async def dependency_handler(request):
        pass

    @mockserver.json_handler('/conditional')
    async def conditional_handler(request):
        pass

    @mockserver.json_handler('/unconditional')
    async def unconditional_handler(request):
        await conditional_handler.wait_call()

    response = await taxi_api_proxy.post('/ep')
    assert response.status_code == 200
    assert unconditional_handler.times_called == 1
    assert dependency_handler.times_called == 0
