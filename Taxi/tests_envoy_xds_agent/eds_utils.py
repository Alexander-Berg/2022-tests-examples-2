import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

# pylint: disable=import-error
from envoy.service.discovery.v3 import discovery_pb2 as proto
from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds
from google.protobuf.internal import containers
import grpc

V3_ENDPOINT = (
    'type.googleapis.com/envoy.config.endpoint.v3.ClusterLoadAssignment'
)

logger = logging.getLogger(__name__)

EthalonEndpointsT = Dict[str, List[Tuple[str, bool]]]


def assert_single(
        arr: Union[List, containers.RepeatedCompositeFieldContainer],
) -> Any:
    assert len(arr) == 1
    return arr[0]


async def stream_endpoint_set(
        discovery_stub: envoy_eds.EndpointDiscoveryServiceStub,
        cluster_list: List[str],
        version: str = '',
) -> proto.DiscoveryResponse:
    def make_endpoints_request():
        # suppress false positive pylint error
        # pylint: disable=no-member

        req = proto.DiscoveryRequest()
        req.type_url = V3_ENDPOINT
        for cluster in cluster_list:
            req.resource_names.append(cluster)
        req.version_info = version
        yield req

    request = discovery_stub.StreamEndpoints(make_endpoints_request())

    responses = [response async for response in request]

    return assert_single(responses)


async def stream_single_endpoint_set(
        discovery_stub: envoy_eds.EndpointDiscoveryServiceStub,
        version: str = '',
        cluster: str = 'envoy-exp-alpha',
):
    return await stream_endpoint_set(
        discovery_stub, cluster_list=[cluster], version=version,
    )


async def assert_stream_endpoint_throws(
        description: str,
        grpc_stub: envoy_eds.EndpointDiscoveryServiceStub,
        version: str = '',
        cluster: str = 'envoy-exp-alpha',
) -> None:

    try:
        await stream_single_endpoint_set(grpc_stub, version, cluster)
        assert False, f'No exception thrown at test "{description}"'
    except grpc.RpcError:
        pass
    except Exception as exc:  # pylint: disable=broad-except
        assert False, f'Unexpected exception at test "{description}": {exc}'
