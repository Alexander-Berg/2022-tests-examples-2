import json
import logging
from typing import List
from typing import Optional

import pytest

from envoy.config.cluster.v3 import cluster_pb2 as envoy_config_cluster
from envoy.service.cluster.v3 import cds_pb2_grpc as envoy_cds
from envoy.service.discovery.v3 import discovery_pb2 as proto

from scout import version_info
from scout.api import cds

logger = logging.getLogger(__name__)


async def stream_single_cluster(
        discovery_stub, *, tvm_name: str, version: str = '',
):
    # suppress false positive pylint error
    # pylint: disable=no-member
    direct_link = f'taxi_tst_{tvm_name}_testing'

    def make_clusters_request():
        req = proto.DiscoveryRequest()
        req.version_info = version
        req.node.cluster = direct_link
        req.type_url = cds.ClusterDiscoveryService.V3_CLUSTER
        yield req

    request = discovery_stub.StreamClusters(make_clusters_request())

    responses = [response async for response in request]
    logger.info(f'StreamClusters response: {responses}')

    assert len(responses) == 1
    return responses[0]


def assert_clusters_response(
        response,
        ethalon_tvm_names: List[str],
        *,
        meta_version: Optional[int] = None,
) -> None:
    # suppress false positive pylint error
    # pylint: disable=no-member

    assert response.version_info
    if meta_version is not None:
        json_version_info = json.loads(response.version_info)
        assert json_version_info['meta_version'] == meta_version

    assert len(response.resources) == len(
        ethalon_tvm_names,
    ), f'{response.resources} vs {ethalon_tvm_names}'
    for resource in response.resources:
        cluster = envoy_config_cluster.Cluster()
        resource.Unpack(cluster)
        assert cluster.name.startswith(f'taxi_tst_')
        assert cluster.name.endswith(f'_testing')
        assert (
            cluster.name.replace('taxi_tst_', '').replace('_testing', '')
            in ethalon_tvm_names
        )


@pytest.mark.parametrize(
    'tvm_name, neighbours_tvm_name',
    [
        ('envoy-exp-alpha', ['envoy-exp-bravo']),
        ('envoy-exp-bravo', ['envoy-exp-charlie', 'envoy-exp-delta']),
    ],
)
async def test_cds_basic(
        taxi_scout_web_oneshot,
        grpc_scout_channel,
        tvm_name,
        neighbours_tvm_name,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)
    response = await stream_single_cluster(discovery_stub, tvm_name=tvm_name)
    assert_clusters_response(response, neighbours_tvm_name)


@pytest.mark.config(
    SCOUT_REQUIRE_NETWORK_MACRO_EQ={'type': 'const', 'value': False},
)
@pytest.mark.parametrize(
    'tvm_name, neighbours_tvm_name',
    [
        ('envoy-exp-alpha', ['envoy-exp-bravo']),
        (
            'envoy-exp-bravo',
            [
                'envoy-exp-charlie',
                'envoy-exp-delta',
                'different-network',
                'no-network',
            ],
        ),
    ],
)
async def test_cds_no_network_checks(
        taxi_scout_web_oneshot,
        grpc_scout_channel,
        tvm_name,
        neighbours_tvm_name,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)
    response = await stream_single_cluster(discovery_stub, tvm_name=tvm_name)
    assert_clusters_response(response, neighbours_tvm_name)


@pytest.mark.parametrize(
    'cluster_tvm_name, neighbours_tvm_name',
    [
        ('envoy-exp-alpha', ['envoy-exp-delta']),
        ('envoy-exp-bravo', ['envoy-exp-alpha', 'envoy-exp-delta']),
        ('envoy-exp-delta', ['envoy-exp-alpha']),
        ('envoy-exp-charlie', []),
        ('nonexistent', []),
    ],
)
async def test_cds_update(
        taxi_scout_web_oneshot,
        grpc_scout_channel,
        cluster_tvm_name,
        neighbours_tvm_name,
        taxi_config,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)

    taxi_config.set_values(
        {
            'TVM_RULES': [
                {'src': 'envoy-exp-alpha', 'dst': 'envoy-exp-delta'},
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-alpha'},
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-delta'},
                {'src': 'envoy-exp-bravo', 'dst': 'multiple-endpointsets'},
                {'src': 'envoy-exp-bravo', 'dst': 'no-endpointsets'},
                {'src': 'envoy-exp-delta', 'dst': 'unknown-service'},
                {'src': 'envoy-exp-delta', 'dst': 'envoy-exp-alpha'},
                {'src': 'envoy-exp-charlie', 'dst': 'unknown-service'},
                {'src': 'envoy-exp-charlie', 'dst': 'lxc-service'},
                {'src': 'envoy-exp-charlie', 'dst': 'multiple-endpointsets'},
                {'src': 'envoy-exp-charlie', 'dst': 'no-endpointsets'},
            ],
        },
    )
    await taxi_scout_web_oneshot.invalidate_caches()

    response = await stream_single_cluster(
        discovery_stub, tvm_name=cluster_tvm_name,
    )
    assert_clusters_response(response, neighbours_tvm_name)


@pytest.mark.parametrize(
    'cluster_tvm_name, neighbours_tvm_name',
    [
        ('envoy-exp-alpha', ['envoy-exp-delta']),
        ('envoy-exp-bravo', ['envoy-exp-alpha', 'envoy-exp-delta']),
    ],
)
async def test_cds_update_no_duplicate_tvm(
        taxi_scout_web_oneshot,
        grpc_scout_channel,
        cluster_tvm_name,
        neighbours_tvm_name,
        taxi_config,
):
    # Envoy goes insane and keeps non-stop requesting CDS if CDS answers
    # with non-unique clusters.
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)

    taxi_config.set_values(
        {
            'TVM_RULES': [
                # alpha
                {'src': 'envoy-exp-alpha', 'dst': 'envoy-exp-delta'},
                # keep the duplicate!
                {'src': 'envoy-exp-alpha', 'dst': 'envoy-exp-delta'},
                # bravo
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-alpha'},
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-delta'},
                {'src': 'envoy-exp-bravo', 'dst': 'multiple-endpointsets'},
                {'src': 'envoy-exp-bravo', 'dst': 'no-endpointsets'},
                # keep the duplicates!
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-alpha'},
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-delta'},
                {'src': 'envoy-exp-bravo', 'dst': 'multiple-endpointsets'},
                {'src': 'envoy-exp-bravo', 'dst': 'no-endpointsets'},
            ],
        },
    )
    await taxi_scout_web_oneshot.invalidate_caches()

    response = await stream_single_cluster(
        discovery_stub, tvm_name=cluster_tvm_name,
    )
    assert_clusters_response(response, neighbours_tvm_name)


async def test_cds_to_nanny_and_back(
        taxi_scout_web_oneshot, grpc_scout_channel, mock_clowny_perforator,
):
    destinations_common = ['envoy-exp-charlie', 'envoy-exp-delta']

    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)
    response = await stream_single_cluster(
        discovery_stub, tvm_name='envoy-exp-bravo',
    )
    assert_clusters_response(response, destinations_common)

    mock_clowny_perforator.non_nany_services.pop()
    await taxi_scout_web_oneshot.invalidate_caches()

    response = await stream_single_cluster(
        discovery_stub, tvm_name='envoy-exp-bravo',
    )
    assert_clusters_response(response, destinations_common + ['lxc-service'])

    mock_clowny_perforator.non_nany_services.add(111)
    await taxi_scout_web_oneshot.invalidate_caches()

    response = await stream_single_cluster(
        discovery_stub, tvm_name='envoy-exp-bravo',
    )
    assert_clusters_response(response, destinations_common)


@pytest.mark.parametrize(
    ['tvm_name', 'neighbours_tvm_name'],
    [('envoy-exp-alpha', ['envoy-exp-bravo'])],
)
async def test_cds_meta_version_changed(
        taxi_scout_web_oneshot,
        grpc_scout_channel,
        taxi_config,
        tvm_name,
        neighbours_tvm_name,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)

    response = await stream_single_cluster(discovery_stub, tvm_name=tvm_name)
    assert_clusters_response(response, neighbours_tvm_name, meta_version=1)

    taxi_config.set_values({'SCOUT_XDS_META_VERSION': 2})
    await taxi_scout_web_oneshot.invalidate_caches()

    new_response = await stream_single_cluster(
        discovery_stub, tvm_name=tvm_name, version=response.version_info,
    )
    assert_clusters_response(new_response, neighbours_tvm_name, meta_version=2)


@pytest.mark.parametrize('tvm_name', ['envoy-exp-alpha'])
async def test_cds_meta_version_newer(
        taxi_scout_web_oneshot, grpc_scout_channel, taxi_config, tvm_name,
):
    discovery_stub = envoy_cds.ClusterDiscoveryServiceStub(grpc_scout_channel)

    try:
        await stream_single_cluster(
            discovery_stub,
            tvm_name=tvm_name,
            version=str(
                version_info.ServiceDestinationsVersion(
                    meta_version=2, data_version=0,
                ),
            ),
        )
    except Exception as exc:  # pylint: disable=broad-except
        assert (
            'client VersionStatus of "service_destinations_cache" is Newer'
            in str(exc)
        )
