# pylint: disable=import-error
from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from tests_envoy_xds_agent import eds_utils
from tests_envoy_xds_agent import xds_utils as xds


async def test_get_proxy_endpoints(
        taxi_envoy_xds_agent, grpc_exa_channel, scout_mock,
):
    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_exa_channel)
    response_that_must_be_cached = await eds_utils.stream_single_endpoint_set(
        discovery_stub,
    )
    assert response_that_must_be_cached.version_info

    await scout_mock.stop()

    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    assert response == response_that_must_be_cached
    current_version = response.version_info

    await eds_utils.assert_stream_endpoint_throws(
        description='current version',
        grpc_stub=discovery_stub,
        version=current_version,
    )

    await eds_utils.assert_stream_endpoint_throws(
        description='startup version and not-requested-previously-cluster',
        grpc_stub=discovery_stub,
        version='',
        cluster='not-requested-previously0',
    )

    await eds_utils.assert_stream_endpoint_throws(
        description='startup version and not-requested-previously-cluster',
        grpc_stub=discovery_stub,
        version=current_version,
        cluster='not-requested-previously1',
    )

    await eds_utils.assert_stream_endpoint_throws(
        description='unseen version and not-requested-previously-cluster',
        grpc_stub=discovery_stub,
        version='unseen-version',
        cluster='not-requested-previously2',
    )

    await scout_mock.restart()
    response = await eds_utils.stream_single_endpoint_set(discovery_stub)
    assert response.version_info

    new_version = 'version_from_test_eds'
    assert response.version_info != new_version
    await scout_mock.restart()
    scout_mock.set_version(new_version)

    await xds.wait_for_new_version(
        new_version=new_version,
        async_job=lambda: eds_utils.stream_single_endpoint_set(discovery_stub),
    )

    await xds.check_polling_for_new_version(
        async_job=lambda: eds_utils.stream_single_endpoint_set(
            discovery_stub, version=new_version,
        ),
        set_new_version=lambda: scout_mock.set_version(new_version + '1'),
    )
