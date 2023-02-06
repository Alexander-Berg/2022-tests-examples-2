import pytest

from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints


async def test_validation_of_unreachable_source(
        taxi_api_proxy, endpoints, resources, load_yaml, mockserver,
):
    await resources.safely_create_resource(
        resource_id='unreachable',
        url=mockserver.url('/unreachable'),
        method='get',
        max_retries=1,
    )

    await resources.safely_create_resource(
        resource_id='failed',
        url=mockserver.url('failed'),
        method='get',
        max_retries=1,
    )

    with pytest.raises(utils_endpoints.Failure) as eggog:
        await endpoints.safely_create_endpoint(
            '/foo', get_handler=load_yaml('handler.yaml'),
        )

    assert eggog.value.response.status_code == 400
    body = eggog.value.response.json()
    assert body['code'] == 'validation_failed'
    assert (
        'usage-of-possiby-unreachable-source'
        in body['details']['errors'][0]['message']
    )


async def test_validation_of_unreachable_source_disable(
        taxi_api_proxy, endpoints, resources, load_yaml, mockserver,
):
    await resources.safely_create_resource(
        resource_id='unreachable',
        url=mockserver.url('/unreachable'),
        method='get',
        max_retries=1,
    )

    await resources.safely_create_resource(
        resource_id='failed',
        url=mockserver.url('failed'),
        method='get',
        max_retries=1,
    )

    await endpoints.safely_create_endpoint(
        '/foo', get_handler=load_yaml('handler-disable.yaml'),
    )

    # test succeed if safely_create_endpoint wont' raise an exception
