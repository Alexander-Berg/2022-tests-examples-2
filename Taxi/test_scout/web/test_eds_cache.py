import copy

from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from test_scout.web import conftest
from test_scout.web import eds_utils


async def test_get_alpha_endpoints_no_yp(
        scout_deps, yp_discovery_mock, grpc_scout_channel,
):
    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.alpha_endpoints_map,
        )

    await yp_discovery_mock.stop()

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.alpha_endpoints_map,
        )


async def test_get_alpha_endpoints_yp_outdated_dump(
        scout_deps, yp_discovery_mock, grpc_scout_channel,
):
    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.alpha_endpoints_map,
        )

    await yp_discovery_mock.stop()

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['vla'][0] = ('2a02:aaa:aaa:a2b:c0ffe:c0a:d338:0', True)
    new_map['sas'][0] = ('2a02:aaa:aaa:a2b:c0ffe:b0b:d338:0', True)
    new_map['man'][0] = ('2a02:aaa:aaa:a2b:c0ffe:a0c:d338:0', True)
    yp_discovery_mock.alpha_endpoints_map = new_map

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        await yp_discovery_mock.restart()
        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.alpha_endpoints_map,
        )


async def test_get_alpha_endpoints_from_fallback(
        scout_deps, yp_discovery_mock, grpc_scout_channel,
):
    await yp_discovery_mock.stop()
    conftest.PersistentStorage.rewrite_to_default()

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.alpha_endpoints_map,
        )


async def test_clowny_endpointes_non_default_no_clownductor(
        scout_deps, yp_discovery_mock, grpc_scout_channel, mockserver,
):
    conftest.PersistentStorage.drop()
    is_clownductor_alive = True

    @mockserver.json_handler('/clownductor/v1/branches/')
    def clownductor_branches_handler(request):
        if not is_clownductor_alive:
            raise mockserver.NetworkError()
        service_id = int(request.args.getone('service_id'))
        replacement_tvm_name = 'envoy-exp-bravo'
        return conftest.Clownductor.form_branches_response(
            service_id,
            replacement_tvm_name,
            add_extra_endpointset=False,
            skip_endpointsets=False,
        )

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.bravo_endpoints_map,
        )

    is_clownductor_alive = False

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.bravo_endpoints_map,
        )

    assert clownductor_branches_handler.times_called >= 1


async def test_clowny_endpointes_fallback(
        scout_deps, yp_discovery_mock, grpc_scout_channel, mockserver,
):
    conftest.PersistentStorage.rewrite_to_default()

    @mockserver.json_handler('/clownductor/v1/branches/')
    def clownductor_branches_handler(request):
        raise mockserver.NetworkError()

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await eds_utils.stream_single_endpoint_set(discovery_stub)
        eds_utils.Assert.endpoints_response(
            response, yp_discovery_mock.alpha_endpoints_map,
        )

    assert clownductor_branches_handler.times_called >= 1
