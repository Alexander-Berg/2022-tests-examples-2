import copy
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from google.protobuf.internal import containers

from envoy.config.route.v3 import route_pb2 as envoy_config_route
from envoy.service.discovery.v3 import discovery_pb2 as proto
from envoy.service.route.v3 import rds_pb2_grpc as envoy_rds

from scout.api import rds
from test_scout.web import conftest

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
        req.type_url = rds.RouteDiscoveryService.V3_ROUTE
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


def assert_routes_response(
        response: proto.DiscoveryResponse,
        ethalon: Dict[str, List[str]],
        *,
        meta_version: Optional[int] = None,
) -> None:
    # suppress false positive pylint error
    # pylint: disable=no-member

    assert response.version_info
    if meta_version is not None:
        json_version_info = json.loads(response.version_info)
        assert json_version_info['meta_version'] == meta_version

    ethalon = {
        f'taxi_tst_{key}_testing': value for key, value in ethalon.items()
    }

    routes = envoy_config_route.RouteConfiguration()
    assert_single(response.resources).Unpack(routes)

    for vhost in routes.virtual_hosts:
        assert vhost.response_headers_to_add
        header = vhost.response_headers_to_add[0].header
        assert (
            header.key == rds.HEADER_ENVOY_DST_VHOST
        ), f'Unexpected header.key = {header.key}'
        assert (
            header.value == vhost.name
        ), f'Unexpected header.value = {header.value}'

        assert vhost.routes, 'Route response without routes'
        for route in vhost.routes:
            assert route.route.cluster == vhost.name, (
                'Target cluster name missmatch virtual host name. '
                'Scout internal logic changed?'
            )

    routes_dict = {vhost.name: vhost.domains for vhost in routes.virtual_hosts}

    assert DYNAMIC_FORWARD_PROXY_CLUSTER in routes_dict
    assert routes_dict[DYNAMIC_FORWARD_PROXY_CLUSTER] == ['*']
    assert routes.virtual_hosts[-1].name == DYNAMIC_FORWARD_PROXY_CLUSTER, (
        'Envoy probably does not care about vhost orders. '
        'Double check that before removing the check'
    )
    del routes_dict[DYNAMIC_FORWARD_PROXY_CLUSTER]

    assert routes_dict == ethalon, f'{routes_dict} != {ethalon}'


# pylint: disable=invalid-name
def clownductor_service_values_handler_new_domains(request):
    service_id = int(request.args.getone('service_id'))
    assert service_id != 0

    new_data = copy.deepcopy(conftest.CLOWNDUCTOR_SERVICE_INFO[service_id])
    for x in new_data:
        if x['name'] != 'hostnames':
            continue
        for val in x['value'].values():
            val.append('new-' + val[0])
    return {
        'subsystems': [
            {'subsystem_name': 'service_info', 'parameters': new_data},
        ],
    }
