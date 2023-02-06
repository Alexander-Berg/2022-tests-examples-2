import logging
from typing import Any
from typing import List
from typing import Union

# pylint: disable=import-error
from envoy.service.discovery.v3 import discovery_pb2 as proto
from envoy.service.route.v3 import rds_pb2_grpc as envoy_rds
from google.protobuf.internal import containers
import grpc

logger = logging.getLogger(__name__)

DYNAMIC_FORWARD_PROXY_CLUSTER = 'dynamic_forward_proxy_cluster'


async def stream_single_route_set(
        discovery_stub: envoy_rds.RouteDiscoveryServiceStub,
        version: str = '',
        tvm_name: str = 'envoy-exp-alpha',
) -> proto.DiscoveryResponse:
    direct_link = f'taxi_tst_{tvm_name}_testing'

    def make_routes_request():
        # suppress false positive pylint error
        # pylint: disable=no-member

        req = proto.DiscoveryRequest()
        req.type_url = '/some/toute/v3'
        req.node.cluster = direct_link
        req.resource_names.append('local_route')
        req.version_info = version
        yield req

    request = discovery_stub.StreamRoutes(make_routes_request())
    responses = [response async for response in request]
    logger.info(f'StreamRoutes response: {responses}')

    return assert_single(responses)


def assert_single(
        arr: Union[List, containers.RepeatedCompositeFieldContainer],
) -> Any:
    assert len(arr) == 1
    return arr[0]


async def assert_stream_route_throws(
        description: str,
        grpc_stub: envoy_rds.RouteDiscoveryServiceStub,
        version: str = '',
        cluster: str = 'envoy-exp-alpha',
) -> None:

    try:
        await stream_single_route_set(grpc_stub)
        assert False, f'No exception thrown at test "{description}"'
    except grpc.RpcError:
        pass
    except Exception as exc:  # pylint: disable=broad-except
        assert False, f'Unexpected exception at test "{description}": {exc}'


async def assert_cache_errors_metric(monitor, expected: int) -> None:
    metrics = await monitor.get_metric(metric_name='rds')
    assert metrics['empty-cache-errors'] == expected
