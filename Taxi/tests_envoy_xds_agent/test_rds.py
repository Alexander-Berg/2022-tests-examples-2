# pylint: disable=import-error
from envoy.service.route.v3 import rds_pb2_grpc as envoy_rds

from tests_envoy_xds_agent import rds_utils
from tests_envoy_xds_agent import xds_utils as xds


async def test_get_proxy_routes(
        taxi_envoy_xds_agent,
        grpc_exa_channel,
        scout_mock,
        taxi_envoy_xds_agent_monitor,
):
    await scout_mock.stop()
    await rds_utils.assert_cache_errors_metric(taxi_envoy_xds_agent_monitor, 0)

    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_exa_channel)

    await rds_utils.assert_stream_route_throws(
        description='empty cache', grpc_stub=discovery_stub,
    )

    await rds_utils.assert_cache_errors_metric(taxi_envoy_xds_agent_monitor, 1)
    await scout_mock.restart()

    response_that_must_be_cached = await rds_utils.stream_single_route_set(
        discovery_stub,
    )
    assert response_that_must_be_cached.version_info

    await scout_mock.stop()

    response = await rds_utils.stream_single_route_set(discovery_stub)
    assert response == response_that_must_be_cached
    await rds_utils.assert_cache_errors_metric(taxi_envoy_xds_agent_monitor, 1)

    new_version = 'version_from_test_rds'
    assert response.version_info != new_version
    await scout_mock.restart()
    scout_mock.set_version(new_version)

    await xds.wait_for_new_version(
        new_version, lambda: rds_utils.stream_single_route_set(discovery_stub),
    )

    await xds.check_polling_for_new_version(
        async_job=lambda: rds_utils.stream_single_route_set(
            discovery_stub, version=new_version,
        ),
        set_new_version=lambda: scout_mock.set_version(new_version + '1'),
    )
