import asyncio
import logging
from typing import AsyncGenerator


# pylint: disable=import-error
from envoy.config.cluster.v3 import cluster_pb2 as envoy_config_cluster
from envoy.config.core.v3 import base_pb2 as envoy_config_base
from envoy.config.endpoint.v3 import endpoint_pb2 as envoy_config_endpoint
from envoy.config.route.v3 import route_pb2 as envoy_config_route
from envoy.service.cluster.v3 import cds_pb2_grpc as envoy_cds
from envoy.service.discovery.v3 import discovery_pb2 as proto
from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds
from envoy.service.route.v3 import rds_pb2_grpc as envoy_rds
from google.protobuf import wrappers_pb2
import grpc
import pytest


SCOUT_GRPC_ADDRESS = 'localhost:12034'
EXF_GRPC_ADDRESS = 'localhost:12033'

HEADER_ENVOY_DST_VHOST = 'X-Taxi-EnvoyProxy-DstVhost'

logger = logging.getLogger(__name__)


class ScoutMock(
        envoy_cds.ClusterDiscoveryServiceServicer,
        envoy_eds.EndpointDiscoveryServiceServicer,
        envoy_rds.RouteDiscoveryServiceServicer,
):
    def __init__(self) -> None:
        super().__init__()
        self._grpc_server = None
        self._version = '1'
        self._on_version_changed = asyncio.Event()

    def set_version(self, version: str) -> None:
        self._version = version
        self._on_version_changed.set()
        self._on_version_changed.clear()

    async def wait_for_different_version(self, new_version: str) -> None:
        while new_version == self._version:
            await self._on_version_changed.wait()

    def _make_envoy_clusters(
            self, request: proto.DiscoveryRequest,
    ) -> envoy_config_cluster.Cluster:
        response = proto.DiscoveryResponse()
        response.type_url = request.type_url
        response.version_info = self._version
        for cluster_name in request.resource_names:
            # suppress false positive pylint error
            # pylint: disable=no-member
            cluster_config = envoy_config_cluster.Cluster()
            cluster_config.cluster_name = cluster_name
            response.resources.add().Pack(cluster_config)

        return response

    def _make_envoy_endpoints(
            self, request: proto.DiscoveryRequest,
    ) -> envoy_config_endpoint.ClusterLoadAssignment:
        response = proto.DiscoveryResponse()
        response.type_url = request.type_url
        response.version_info = self._version
        for cluster_name in request.resource_names:
            # suppress false positive pylint error
            # pylint: disable=no-member
            endpoint_config = envoy_config_endpoint.ClusterLoadAssignment()
            endpoint_config.cluster_name = cluster_name
            response.resources.add().Pack(endpoint_config)

        return response

    def _make_envoy_routes(
            self, request: proto.DiscoveryRequest,
    ) -> envoy_config_route.RouteConfiguration:
        response = proto.DiscoveryResponse()
        response.type_url = request.type_url
        response.version_info = self._version
        for cluster_name in request.resource_names:
            # suppress false positive pylint error
            # pylint: disable=no-member
            route_config = envoy_config_route.RouteConfiguration()
            route_config.name = cluster_name
            host = route_config.virtual_hosts.add()
            host.name = 'dynamic_forward_proxy_cluster'
            host.domains.extend(['*'])
            host.response_headers_to_add.add(
                header=envoy_config_base.HeaderValue(
                    key=HEADER_ENVOY_DST_VHOST, value=host.name,
                ),
                append=wrappers_pb2.BoolValue(value=False),
            )

            new_route = host.routes.add()
            new_route.match.prefix = '/'
            new_route.route.cluster = 'dynamic_forward_proxy_cluster'

            response.resources.add().Pack(route_config)

        return response

    # pylint: disable=invalid-name
    async def StreamClusters(
            self, request_iterator, context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[proto.DiscoveryResponse, proto.DiscoveryRequest]:
        async for request in request_iterator:
            await self.wait_for_different_version(request.version_info)
            yield self._make_envoy_clusters(request)

    # pylint: disable=invalid-name
    async def StreamEndpoints(
            self, request_iterator, context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[proto.DiscoveryResponse, proto.DiscoveryRequest]:
        async for request in request_iterator:
            await self.wait_for_different_version(request.version_info)
            yield self._make_envoy_endpoints(request)

    # pylint: disable=invalid-name
    async def StreamRoutes(
            self, request_iterator, context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[proto.DiscoveryResponse, proto.DiscoveryRequest]:
        async for request in request_iterator:
            await self.wait_for_different_version(request.version_info)
            yield self._make_envoy_routes(request)

    async def stop(self) -> None:
        if self._grpc_server:
            await self._grpc_server.stop(grace=None)
            self._grpc_server = None

    async def restart(self) -> None:
        await self.stop()

        self._grpc_server = grpc.aio.server()
        assert self._grpc_server

        self._grpc_server.add_insecure_port(SCOUT_GRPC_ADDRESS)
        envoy_cds.add_ClusterDiscoveryServiceServicer_to_server(
            self, self._grpc_server,
        )
        envoy_eds.add_EndpointDiscoveryServiceServicer_to_server(
            self, self._grpc_server,
        )
        envoy_rds.add_RouteDiscoveryServiceServicer_to_server(
            self, self._grpc_server,
        )
        await self._grpc_server.start()


@pytest.fixture(name='scout_mock')
async def _scout_mock():
    mock = ScoutMock()
    await mock.restart()
    logger.info('ScoutMock server started')
    try:
        yield mock
    finally:
        await mock.stop()
        logger.info('ScoutMock server stopped')


@pytest.fixture(name='grpc_exa_channel')
async def _grpc_exa_channel():
    async with grpc.aio.insecure_channel(EXF_GRPC_ADDRESS) as channel:
        logger.info('gRPC channel opened')

        done, _ = await asyncio.wait(
            [channel.channel_ready()],
            return_when=asyncio.FIRST_COMPLETED,
            timeout=15,
        )

        if not done:
            raise Exception(
                f'Failed to connect to remote gRPC server by '
                f'address {EXF_GRPC_ADDRESS}',
            )

        logger.info('gRPC channel ready')

        yield channel
    logger.info('gRPC channel closed')
