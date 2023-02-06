import re

import pytest


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'enabled': True,
            'fallbacks': ['resource.resource.fallback'],
            'service': 'api-proxy',
        },
    ],
)
async def test_resource_fallback_with_dynamic_value(
        taxi_api_proxy,
        resources,
        endpoints,
        statistics,
        mockserver,
        load_yaml,
):
    # create resource
    await resources.safely_create_resource(
        resource_id='resource', url=mockserver.url('service'), method='post',
    )

    # create an endpoint
    handler_def = load_yaml('handler_with_resource_fallback.yaml')
    path = '/tests/api-proxy/handler-with-fallback'
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # call the handler
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json()['fallback']
    uuid1 = response.json()['uuid']
    assert re.match(r'[a-f\d]{32}', uuid1)

    # call again, value shall change
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json()['fallback']
    uuid2 = response.json()['uuid']
    assert re.match(r'[a-f\d]{32}', uuid2)

    assert uuid1 != uuid2


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'enabled': True,
            'fallbacks': ['resource.resource1.fallback'],
            'service': 'api-proxy',
        },
    ],
)
async def test_fallback_source_deps(
        taxi_api_proxy,
        resources,
        endpoints,
        statistics,
        mockserver,
        load_yaml,
):
    # create resources
    await resources.safely_create_resource(
        resource_id='resource1',
        url=mockserver.url('service-url1'),
        method='post',
    )
    await resources.safely_create_resource(
        resource_id='resource2',
        url=mockserver.url('service-url2'),
        method='post',
    )

    # try to create an endpoint
    handler_def = load_yaml('handler_with_fallback_deps.yaml')
    path = '/tests/api-proxy/handler-with-fallback'
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.safely_create_endpoint(path, get_handler=handler_def)
    # validation fails because fallback depends on source2
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'validation_failed'


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'enabled': True,
            'fallbacks': ['resource.r.e.s.o.u.r.c.e.fallback'],
            'service': 'api-proxy',
        },
    ],
)
async def test_dotted_resource_fallback_response(
        taxi_api_proxy,
        resources,
        endpoints,
        statistics,
        mockserver,
        load_yaml,
):
    # create resource
    await resources.safely_create_resource(
        resource_id='r.e.s.o.u.r.c.e',
        url=mockserver.url('s.e.r.v.i.c.e'),
        method='post',
    )

    # create an endpoint
    handler_def = load_yaml('handler_with_dotted_resource_fallback.yaml')
    path = '/tests/api-proxy/handler-with-fallback'
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # call the handler
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'fallback': True}
