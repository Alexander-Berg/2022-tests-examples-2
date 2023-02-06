import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from google.protobuf.internal import containers

from envoy.config.endpoint.v3 import endpoint_pb2 as envoy_config_endpoint
from envoy.service.discovery.v3 import discovery_pb2 as proto
from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from scout.api import eds

logger = logging.getLogger(__name__)

EthalonEndpointsT = Dict[str, List[Tuple[str, bool]]]


def assert_single(
        arr: Union[List, containers.RepeatedCompositeFieldContainer],
) -> Any:
    assert len(arr) == 1
    return arr[0]


async def stream_eds_by_direct_links(
        discovery_stub: envoy_eds.EndpointDiscoveryServiceStub,
        direct_links_list: List[str],
        version: str = '',
) -> proto.DiscoveryResponse:
    def make_endpoints_request():
        # suppress false positive pylint error
        # pylint: disable=no-member

        req = proto.DiscoveryRequest()
        req.type_url = eds.EndpointDiscoveryService.V3_ENDPOINT
        for resource_name in direct_links_list:
            req.resource_names.append(resource_name)
        req.version_info = version
        yield req

    request = discovery_stub.StreamEndpoints(make_endpoints_request())

    responses = [response async for response in request]
    single_response = assert_single(responses)

    for resource in single_response.resources:
        endpoints = envoy_config_endpoint.ClusterLoadAssignment()
        resource.Unpack(endpoints)
        # suppress false positive pylint error:
        # Instance of 'ClusterLoadAssignment' has no 'cluster_name' member
        # pylint: disable=no-member
        assert endpoints.cluster_name in direct_links_list, (
            f'Resource "{endpoints.cluster_name}" not in a list of '
            f'requested resources {direct_links_list}'
        )
    return single_response


async def stream_endpoint_set(
        discovery_stub: envoy_eds.EndpointDiscoveryServiceStub,
        tvm_names_list: List[str],
        version: str = '',
) -> proto.DiscoveryResponse:
    direct_links_list = [
        f'taxi_tst_{tvm_name}_testing' for tvm_name in tvm_names_list
    ]

    return await stream_eds_by_direct_links(
        discovery_stub, direct_links_list, version,
    )


async def stream_single_endpoint_set(
        discovery_stub: envoy_eds.EndpointDiscoveryServiceStub,
        version: str = '',
        cluster: str = 'envoy-exp-alpha',
):
    return await stream_endpoint_set(
        discovery_stub, tvm_names_list=[cluster], version=version,
    )


class Assert:
    @staticmethod
    def endpoints_match_ethalon(
            endpoints: envoy_config_endpoint.ClusterLoadAssignment,
            ethalon_endpoints: EthalonEndpointsT,
    ) -> None:
        for endpoint in endpoints.endpoints:
            assert (
                endpoint.locality.zone in ethalon_endpoints
            ), f'{endpoints.endpoints} != {ethalon_endpoints}'

            yp_endpoints = [
                x[0] for x in ethalon_endpoints[endpoint.locality.zone]
            ]
            addresses = [
                x.endpoint.address.socket_address.address
                for x in endpoint.lb_endpoints
            ]

            assert addresses == yp_endpoints, f'{addresses} != {yp_endpoints}'

    @staticmethod
    def endpoints_response(
            response: proto.DiscoveryResponse,
            ethalon_endpoints: EthalonEndpointsT,
            meta_version: Optional[int] = None,
    ) -> None:
        assert response.version_info
        if meta_version is not None:
            json_version_info = json.loads(response.version_info)
            assert json_version_info['meta_version'] == meta_version

        endpoints = envoy_config_endpoint.ClusterLoadAssignment()
        assert_single(response.resources).Unpack(endpoints)
        Assert.endpoints_match_ethalon(endpoints, ethalon_endpoints)

    @staticmethod
    def endpoints_response_multiple(
            response: proto.DiscoveryResponse,
            ethalon_endpoints: Dict[str, EthalonEndpointsT],
    ) -> None:
        # suppress false positive pylint error
        # pylint: disable=no-member

        assert response.version_info

        ethalon_endpoints = {
            f'taxi_tst_{key}_testing': value
            for key, value in ethalon_endpoints.items()
        }

        endpoints = envoy_config_endpoint.ClusterLoadAssignment()
        for resource in response.resources:
            resource.Unpack(endpoints)
            Assert.endpoints_match_ethalon(
                endpoints, ethalon_endpoints[endpoints.cluster_name],
            )

    @staticmethod
    def endpoints_response_single(
            response: proto.DiscoveryResponse,
            ethalon_endpoints: EthalonEndpointsT,
    ) -> None:
        # suppress false positive pylint error
        # pylint: disable=no-member

        assert response.version_info

        nonempty_endpoints = None
        for res in response.resources:
            endpoints = envoy_config_endpoint.ClusterLoadAssignment()
            res.Unpack(endpoints)
            if endpoints.endpoints:
                assert (
                    nonempty_endpoints is None
                ), 'Must be only 1 nonempty set'
                nonempty_endpoints = endpoints
        assert nonempty_endpoints, 'No nonempy endoint found'
        Assert.endpoints_match_ethalon(nonempty_endpoints, ethalon_endpoints)

    @staticmethod
    def endpoints_response_empty(response: proto.DiscoveryResponse) -> None:
        # suppress false positive pylint error
        # pylint: disable=no-member

        assert response.version_info

        endpoints = envoy_config_endpoint.ClusterLoadAssignment()
        assert_single(response.resources).Unpack(endpoints)
        assert not endpoints.endpoints
