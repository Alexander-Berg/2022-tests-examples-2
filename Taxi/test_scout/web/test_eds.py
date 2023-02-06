import asyncio
import copy
import time

from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from scout import endpoints_cache
from scout import version_info
from test_scout.web import conftest
from test_scout.web import eds_utils


def test_version_from_timestamps():
    prev_version = endpoints_cache.version_from_timestamps([1, 5, 9])

    timestamps_list = [
        [2, 5, 9],
        [2, 6, 9],
        [9, 6, 9],
        [9, 10, 9],
        [10, 10, 9],
        [10, 10, 10],
        [11, 11, 11],
    ]

    for timestamps in timestamps_list:
        version = endpoints_cache.version_from_timestamps(timestamps)
        assert (
            version > prev_version
        ), f'Version must increment. Failed on {timestamps}'

        prev_version = version


async def test_get_alpha_endpoints(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(
        response, yp_discovery_mock.alpha_endpoints_map,
    )

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['vla'][0] = ('2a02:aaa:aaa:a2b:0:aaa:d338:0', True)
    yp_discovery_mock.alpha_endpoints_map = new_map

    await taxi_scout_web_oneshot.invalidate_caches()
    new_response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    assert (
        response.version_info != new_response.version_info
    ), 'Version did not change after data was updated'
    eds_utils.Assert.endpoints_response(new_response, new_map)


async def test_clowny_endpointes_non_default(
        scout_deps, yp_discovery_mock, grpc_scout_channel, mockserver,
):
    @mockserver.json_handler('/clownductor/v1/branches/')
    def clownductor_branches_handler(request):
        service_id = int(request.args.getone('service_id'))
        yp_cluster_name = 'envoy_exp_bravo'
        return conftest.Clownductor.form_branches_response(
            service_id,
            yp_cluster_name,
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

    assert clownductor_branches_handler.times_called >= 1


async def test_get_alpha_endpoints_yp_returns_outdated_data(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(
        response, yp_discovery_mock.alpha_endpoints_map,
    )

    prev_sas_value = yp_discovery_mock.alpha_endpoints_map['sas']

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['vla'][0] = ('2a02:0aa:aa0:a2b:0:c0a:d338:0', True)
    new_map['sas'][0] = ('2a02:a0a:a0a:a2b:0:b0b:d338:0', True)
    new_map['man'][0] = ('2a02:aa0:0aa:a2b:0:a0c:d338:0', True)
    yp_discovery_mock.alpha_timer = (
        lambda clust_name: time.monotonic_ns() if clust_name != 'sas' else 42
    )
    yp_discovery_mock.alpha_endpoints_map = new_map

    await taxi_scout_web_oneshot.invalidate_caches()
    new_response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    assert (
        response.version_info != new_response.version_info
    ), 'Version did not change after data was updated'
    ethalon = copy.deepcopy(new_map)
    ethalon['sas'] = prev_sas_value
    eds_utils.Assert.endpoints_response(new_response, ethalon)


async def test_get_alpha_endpoints_yp_small_version_change(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    version_base = 999999999999990
    versions = {
        'vla': version_base,
        'sas': version_base + 5,
        'man': version_base + 9,
    }

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['vla'][0] = ('2a02:0aa:aa0:a2b:0:c0a:d338:0', True)
    new_map['sas'][0] = ('2a02:a0a:a0a:a2b:0:b0b:d338:0', True)
    new_map['man'][0] = ('2a02:aa0:0aa:a2b:0:a0c:d338:0', True)
    yp_discovery_mock.alpha_timer = lambda clust_name: versions[clust_name]
    yp_discovery_mock.alpha_endpoints_map = new_map

    await taxi_scout_web_oneshot.invalidate_caches()

    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(response, new_map)

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['sas'][0] = ('2a02:a0a:a0a:a2b:0:b0b:d338:1', True)
    new_versions = copy.deepcopy(versions)
    new_versions['sas'] = version_base + 6
    yp_discovery_mock.alpha_timer = lambda clust_name: new_versions[clust_name]
    yp_discovery_mock.alpha_endpoints_map = new_map

    await taxi_scout_web_oneshot.invalidate_caches()
    new_response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    assert (
        response.version_info != new_response.version_info
    ), 'Version did not change after data was updated'
    eds_utils.Assert.endpoints_response(new_response, new_map)


async def test_get_alpha_endpoints_update_by_version(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(
        response, yp_discovery_mock.alpha_endpoints_map,
    )

    response_awaiter = asyncio.create_task(
        eds_utils.stream_single_endpoint_set(
            discovery_stub, version=response.version_info,
        ),
    )
    assert not response_awaiter.done()

    # Make sure that cache invalidations do not wake up polling connections
    # with old version
    for _ in range(10):
        await taxi_scout_web_oneshot.invalidate_caches()

    assert not response_awaiter.done()

    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['vla'][0] = ('2a02:fff:fff:a2b:0:aaa:d338:0', True)
    yp_discovery_mock.alpha_endpoints_map = new_map

    await taxi_scout_web_oneshot.invalidate_caches()
    new_response = await response_awaiter
    assert (
        response.version_info != new_response.version_info
    ), 'Version did not change after data was updated'
    eds_utils.Assert.endpoints_response(new_response, new_map)


async def test_get_alpha_endpoints_update_and_yp_dies(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    new_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    new_map['vla'][0] = ('2a02:aaa:aaa:a2b:0:c0a:d338:0', True)
    new_map['sas'][0] = ('2a02:aaa:aaa:a2b:0:b0b:d338:0', True)
    new_map['man'][0] = ('2a02:aaa:aaa:a2b:0:a0c:d338:0', True)
    yp_discovery_mock.alpha_endpoints_map = new_map

    await taxi_scout_web_oneshot.invalidate_caches()
    await eds_utils.stream_single_endpoint_set(discovery_stub)

    # Keep working on dead YP discovery
    await yp_discovery_mock.stop()
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(response, new_map)

    await taxi_scout_web_oneshot.invalidate_caches()
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(response, new_map)

    newest_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    newest_map['vla'][0] = ('2a02:c0ffe:beef:a2b:0:c0a:c0ffe:0', True)
    newest_map['sas'][0] = ('2a02:c0ffe:beef:a2b:0:b0b:c0ffe:0', True)
    newest_map['man'][0] = ('2a02:c0ffe:beef:a2b:0:a0c:c0ffe:0', True)
    yp_discovery_mock.alpha_endpoints_map = newest_map
    await taxi_scout_web_oneshot.invalidate_caches()
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    # YP is down, checking for "new_map", not "newest_map"
    eds_utils.Assert.endpoints_response(response, new_map)

    # Keep working on resurrected YP discovery
    await yp_discovery_mock.restart()
    newest_map = copy.deepcopy(yp_discovery_mock.alpha_endpoints_map)
    newest_map['vla'][0] = ('2a02:c0ffe:beef:a2b:0:c0a:d338:0', True)
    newest_map['sas'][0] = ('2a02:c0ffe:beef:a2b:0:b0b:d338:0', True)
    newest_map['man'][0] = ('2a02:c0ffe:beef:a2b:0:a0c:d338:0', True)
    yp_discovery_mock.alpha_endpoints_map = newest_map

    invoke_awaiter = yp_discovery_mock.wait_for_invoke()
    for _ in range(20):
        await taxi_scout_web_oneshot.invalidate_caches()
        if invoke_awaiter.done():
            break
        # It takes some time for gRPC to restore the connection
        await asyncio.sleep(0.5)
    assert invoke_awaiter.done()
    await invoke_awaiter

    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(response, newest_map)


async def test_bogus_links_mix(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)

    try:
        await eds_utils.stream_eds_by_direct_links(
            discovery_stub,
            direct_links_list=[
                'taxi_tst_envoy-exp-alpha_pre_stable',
                'taxi_tst_envoy-exp-bravo_testing',
                'taxi_tst_envoy-exp-alpha_testing',
            ],
        )
        assert False
    except Exception as exc:  # pylint: disable=broad-except
        assert 'same services' in str(exc)


async def test_meta_version_changed(
        taxi_scout_web_oneshot,
        yp_discovery_mock,
        grpc_scout_channel,
        taxi_config,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)

    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    eds_utils.Assert.endpoints_response(
        response, yp_discovery_mock.alpha_endpoints_map, meta_version=1,
    )

    taxi_config.set_values({'SCOUT_XDS_META_VERSION': 2})
    await taxi_scout_web_oneshot.invalidate_caches()

    new_response = await eds_utils.stream_single_endpoint_set(
        discovery_stub, version=response.version_info,
    )
    eds_utils.Assert.endpoints_response(
        new_response, yp_discovery_mock.alpha_endpoints_map, meta_version=2,
    )


async def test_meta_version_newer(
        taxi_scout_web_oneshot, grpc_scout_channel, taxi_config,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)

    try:
        await eds_utils.stream_single_endpoint_set(
            discovery_stub,
            version=str(
                version_info.EndpointVersion(meta_version=2, data_version={}),
            ),
        )
        assert False
    except Exception as exc:  # pylint: disable=broad-except
        assert 'client VersionStatus of "endpoints_cache" is Newer' in str(exc)
