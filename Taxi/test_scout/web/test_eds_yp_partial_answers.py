import copy

import pytest

from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from test_scout.web import eds_utils


async def test_endpoints_nonexistent(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(
        discovery_stub, cluster='nonexistent',
    )
    eds_utils.Assert.endpoints_response_empty(response)


@pytest.mark.parametrize(
    'tvm_names_list',
    [['envoy-exp-alpha', 'nonexistent'], ['nonexistent', 'envoy-exp-alpha']],
)
async def test_endpointss_multiple_clusters_one_nonexist(
        taxi_scout_web_oneshot,
        yp_discovery_mock,
        grpc_scout_channel,
        tvm_names_list,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_endpoint_set(
        discovery_stub, tvm_names_list=tvm_names_list,
    )
    eds_utils.Assert.endpoints_response_single(
        response, yp_discovery_mock.alpha_endpoints_map,
    )


@pytest.mark.parametrize(
    'tvm_names_list',
    [
        ['envoy-exp-alpha', 'grpc_exception'],
        ['grpc_exception', 'envoy-exp-alpha'],
    ],
)
async def test_endpoints_multiple_clusters_one_alive(
        taxi_scout_web_oneshot,
        yp_discovery_mock,
        grpc_scout_channel,
        tvm_names_list,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_endpoint_set(
        discovery_stub, tvm_names_list=tvm_names_list,
    )

    eds_utils.Assert.endpoints_response_single(
        response, yp_discovery_mock.alpha_endpoints_map,
    )


@pytest.mark.parametrize(
    'dead_locations',
    [
        ['man'],
        ['sas'],
        ['vla'],
        ['man', 'sas'],
        ['sas', 'vla'],
        ['vla', 'man'],
    ],
)
async def test_endpoints_dead_locations(
        taxi_scout_web_oneshot,
        yp_discovery_mock,
        grpc_scout_channel,
        dead_locations,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(
        response, yp_discovery_mock.alpha_endpoints_map,
    )
    await taxi_scout_web_oneshot.invalidate_caches()

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    for location in new_map.keys():
        if location in dead_locations:
            continue
        new_map[location][0] = ('2a02:c1ffe:beef:beef:0:c0a:c0ffe:0', True)

    yp_map_with_deletions = copy.deepcopy(new_map)
    for location in dead_locations:
        del yp_map_with_deletions[location]

    yp_discovery_mock.alpha_endpoints_map = yp_map_with_deletions

    # scout must partially update the endpoints even if YP throws for
    # some locations
    await taxi_scout_web_oneshot.invalidate_caches()

    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(response, new_map)
