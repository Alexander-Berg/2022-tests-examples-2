# pylint: disable=import-error
from envoy.service.cluster.v3 import cds_pb2_grpc as envoy_cds
from envoy.service.discovery.v3 import discovery_pb2 as proto

from tests_envoy_xds_agent import xds_utils as xds


async def stream_single_cluster(
        discovery_stub,
        cluster_name: str = 'envoy-exp-alpha',
        version: str = '',
):
    # suppress false positive pylint error
    # pylint: disable=no-member

    def make_clusters_request():
        req = proto.DiscoveryRequest()
        req.node.cluster = cluster_name
        req.version_info = version
        req.type_url = '/some/clusters/type/url/v3'
        yield req

    request = discovery_stub.StreamClusters(make_clusters_request())

    responses = [response async for response in request]

    assert len(responses) == 1
    return responses[0]


async def test_get_proxy_clusters(
        taxi_envoy_xds_agent, grpc_exa_channel, scout_mock,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_exa_channel)
    response_that_must_be_cached = await stream_single_cluster(discovery_stub)
    assert response_that_must_be_cached.version_info

    await scout_mock.stop()

    response = await stream_single_cluster(discovery_stub)
    assert response == response_that_must_be_cached

    new_version = 'version_from_test_cds'
    assert response.version_info != new_version
    await scout_mock.restart()
    scout_mock.set_version(new_version)

    await xds.wait_for_new_version(
        new_version, lambda: stream_single_cluster(discovery_stub),
    )

    await xds.check_polling_for_new_version(
        async_job=lambda: stream_single_cluster(
            discovery_stub, version=new_version,
        ),
        set_new_version=lambda: scout_mock.set_version(new_version + '1'),
    )


async def test_get_two_proxy_clusters_in_a_row(
        taxi_envoy_xds_agent, grpc_exa_channel, scout_mock,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_exa_channel)

    # suppress false positive pylint error
    # pylint: disable=no-member
    def make_two_clusters_request():
        req = proto.DiscoveryRequest()
        req.node.cluster = 'first_cluster'
        req.version_info = ''
        req.type_url = '/some/clusters/type/url/v3'
        yield req
        req.node.cluster = 'second_cluster'
        req.type_url = '/some/clusters/type/url/v4'
        yield req

    request = discovery_stub.StreamClusters(make_two_clusters_request())
    scout_responses = [response async for response in request]

    assert len(scout_responses) == 2
    assert scout_responses[0].version_info == '1'
    assert scout_responses[1].version_info == '1'
    assert scout_responses[0].type_url == '/some/clusters/type/url/v3'
    assert scout_responses[1].type_url == '/some/clusters/type/url/v4'

    await scout_mock.stop()

    request = discovery_stub.StreamClusters(make_two_clusters_request())
    responses_from_cache = [response async for response in request]

    assert len(responses_from_cache) == 2
    assert scout_responses == responses_from_cache
