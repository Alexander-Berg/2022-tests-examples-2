import logging

import pytest

from envoy.service.route.v3 import rds_pb2_grpc as envoy_rds

from test_scout.web import conftest
from test_scout.web import rds_utils

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'perforator_alive, clownductor_alive',
    [(True, False), (False, True), (False, False)],
    ids=['Dead Clownducor', 'Dead Perforator', 'All dead'],
)
async def test_routes_alpha_start_no_clowns(
        scout_deps,
        mockserver,
        mock_clowny_perforator,
        grpc_scout_channel,
        perforator_alive,
        clownductor_alive,
):
    ethalon = {'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']}

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_rds.RouteDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await rds_utils.stream_single_route_set(discovery_stub)
        rds_utils.assert_routes_response(response, ethalon=ethalon)

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    def retrieve_handler(request):
        if not perforator_alive:
            raise mockserver.NetworkError()
        return conftest.ClownyPerforator.retrieve_handler(request)

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    def service_values_handler(request):
        if not clownductor_alive:
            raise mockserver.NetworkError()
        return conftest.Clownductor.service_values_handler(request)

    @mockserver.json_handler('/clownductor/v1/services/')
    def clownductor_services_handler(request):
        if not clownductor_alive:
            raise mockserver.NetworkError()
        return conftest.Clownductor.services_handler(request, {})

    @mockserver.json_handler('/clownductor/v1/branches/')
    def clownductor_branches_handler(request):
        if not clownductor_alive:
            raise mockserver.NetworkError()
        return conftest.Clownductor.branches_handler(request)

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_rds.RouteDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await rds_utils.stream_single_route_set(discovery_stub)
        rds_utils.assert_routes_response(response, ethalon=ethalon)

    assert (
        retrieve_handler.times_called >= 1
        or service_values_handler.times_called >= 1
        or clownductor_services_handler.times_called >= 1
        or clownductor_branches_handler.times_called >= 1
    )


@pytest.mark.parametrize(
    'perforator_alive, clownductor_alive',
    [(True, False), (False, True), (False, False)],
    ids=['Dead Clownducor', 'Dead Perforator', 'All dead'],
)
async def test_routes_alpha_start_from_fallback(
        scout_deps,
        mockserver,
        mock_clowny_perforator,
        grpc_scout_channel,
        perforator_alive,
        clownductor_alive,
):
    ethalon = {'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']}
    conftest.PersistentStorage.rewrite_to_default()

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    def retrieve_handler(request):
        if not perforator_alive:
            raise mockserver.NetworkError()
        return conftest.ClownyPerforator.retrieve_handler(request)

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    def service_values_handler(request):
        if not clownductor_alive:
            raise mockserver.NetworkError()
        return conftest.Clownductor.service_values_handler(request)

    @mockserver.json_handler('/clownductor/v1/services/')
    def clownductor_services_handler(request):
        if not clownductor_alive:
            raise mockserver.NetworkError()
        return conftest.Clownductor.services_handler(request, {})

    @mockserver.json_handler('/clownductor/v1/branches/')
    def clownductor_branches_handler(request):
        if not clownductor_alive:
            raise mockserver.NetworkError()
        return conftest.Clownductor.branches_handler(request)

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_rds.RouteDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await rds_utils.stream_single_route_set(discovery_stub)
        rds_utils.assert_routes_response(response, ethalon=ethalon)

    assert (
        retrieve_handler.times_called >= 1
        or service_values_handler.times_called >= 1
        or clownductor_services_handler.times_called >= 1
        or clownductor_branches_handler.times_called >= 1
    )


async def test_routes_alpha_start_outdated_dump(
        scout_deps, mockserver, grpc_scout_channel, mock_clowny_perforator,
):
    ethalon = {'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']}

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_rds.RouteDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await rds_utils.stream_single_route_set(discovery_stub)
        rds_utils.assert_routes_response(response, ethalon)

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    def retrieve_handler(request):
        return conftest.ClownyPerforator.retrieve_handler(request)

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    def service_values_handler(request):
        return rds_utils.clownductor_service_values_handler_new_domains(
            request,
        )

    ethalon = {
        'envoy-exp-bravo': [
            'envoy-exp-bravo.taxi.yandex.net',
            'new-envoy-exp-bravo.taxi.yandex.net',
        ],
    }

    async with conftest.scoped_scout(scout_deps) as scout:
        await scout_deps.ensure_daemon_started(scout)

        discovery_stub = envoy_rds.RouteDiscoveryServiceStub(
            grpc_scout_channel,
        )
        response = await rds_utils.stream_single_route_set(discovery_stub)
        rds_utils.assert_routes_response(response, ethalon)
    assert retrieve_handler.times_called == 1
    assert service_values_handler.times_called >= 1
