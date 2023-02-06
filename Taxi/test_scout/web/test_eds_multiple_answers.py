import copy

from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from test_scout.web import eds_utils


async def test_get_endpoints_multiple_in_one_go(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    await taxi_scout_web_oneshot.invalidate_caches()

    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_endpoint_set(
        discovery_stub, tvm_names_list=['envoy-exp-alpha', 'envoy-exp-bravo'],
    )
    eds_utils.Assert.endpoints_response_multiple(
        response,
        {
            'envoy-exp-alpha': yp_discovery_mock.alpha_endpoints_map,
            'envoy-exp-bravo': yp_discovery_mock.bravo_endpoints_map,
        },
    )


async def test_get_endpoints_multiple(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    await taxi_scout_web_oneshot.invalidate_caches()

    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_endpoint_set(
        discovery_stub, tvm_names_list=['envoy-exp-alpha'],
    )
    version = response.version_info
    response = await eds_utils.stream_endpoint_set(
        discovery_stub,
        tvm_names_list=['envoy-exp-alpha', 'envoy-exp-bravo'],
        version=version,
    )
    eds_utils.Assert.endpoints_response_multiple(
        response,
        {
            'envoy-exp-alpha': yp_discovery_mock.alpha_endpoints_map,
            'envoy-exp-bravo': yp_discovery_mock.bravo_endpoints_map,
        },
    )


async def test_get_endpoints_multiple_small_version_change(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    version_base = 999999999999990
    alpha_version = version_base + 3
    bravo_version = version_base + 6

    alpha_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    alpha_map['vla'][0] = ('0a02:0aa:aa0:a2b:0:c0fe:d338:bab1', True)
    yp_discovery_mock.alpha_timer = lambda clust_name: alpha_version
    yp_discovery_mock.alpha_endpoints_map = alpha_map

    bravo_map = copy.deepcopy(yp_discovery_mock.bravo_endpoints_map)
    bravo_map['vla'][0] = ('0a02:0aa:aa0:a2b:0:bab1:d338:c0fe', True)
    yp_discovery_mock.bravo_timer = lambda clust_name: bravo_version
    yp_discovery_mock.bravo_endpoints_map = bravo_map

    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_endpoint_set(
        discovery_stub, tvm_names_list=['envoy-exp-alpha'],
    )
    version = response.version_info
    response = await eds_utils.stream_endpoint_set(
        discovery_stub,
        tvm_names_list=['envoy-exp-alpha', 'envoy-exp-bravo'],
        version=version,
    )
    version = response.version_info
    eds_utils.Assert.endpoints_response_multiple(
        response, {'envoy-exp-alpha': alpha_map, 'envoy-exp-bravo': bravo_map},
    )

    alpha_version = version_base + 4
    alpha_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    alpha_map['vla'][0] = ('aa02:0aa:aa0:a2b:0:cafe:d338:baf1', True)
    yp_discovery_mock.alpha_timer = lambda clust_name: alpha_version
    yp_discovery_mock.alpha_endpoints_map = alpha_map

    await taxi_scout_web_oneshot.invalidate_caches()

    response = await eds_utils.stream_endpoint_set(
        discovery_stub,
        tvm_names_list=['envoy-exp-alpha', 'envoy-exp-bravo'],
        version=version,
    )

    eds_utils.Assert.endpoints_response_multiple(
        response, {'envoy-exp-alpha': alpha_map, 'envoy-exp-bravo': bravo_map},
    )
