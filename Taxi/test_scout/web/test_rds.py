import logging

import pytest

from envoy.service.route.v3 import rds_pb2_grpc as envoy_rds

from scout import version_info
from test_scout.web import conftest
from test_scout.web import rds_utils

logger = logging.getLogger(__name__)


async def test_routes_alpha(taxi_scout_web_oneshot, grpc_scout_channel):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)
    response = await rds_utils.stream_single_route_set(discovery_stub)
    rds_utils.assert_routes_response(
        response,
        ethalon={'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']},
    )


async def test_routes_bravo(taxi_scout_web_oneshot, grpc_scout_channel):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)
    response = await rds_utils.stream_single_route_set(
        discovery_stub, tvm_name='envoy-exp-bravo',
    )
    rds_utils.assert_routes_response(
        response,
        ethalon={
            'envoy-exp-charlie': ['envoy-exp-charlie.taxi.yandex.net'],
            'envoy-exp-delta': ['envoy-exp-delta.taxi.yandex.net'],
        },
    )


@pytest.mark.config(
    SCOUT_REQUIRE_NETWORK_MACRO_EQ={'type': 'const', 'value': False},
)
async def test_routes_bravo_no_network_checks(
        taxi_scout_web_oneshot, grpc_scout_channel,
):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)
    response = await rds_utils.stream_single_route_set(
        discovery_stub, tvm_name='envoy-exp-bravo',
    )
    rds_utils.assert_routes_response(
        response,
        ethalon={
            'envoy-exp-charlie': ['envoy-exp-charlie.taxi.yandex.net'],
            'envoy-exp-delta': ['envoy-exp-delta.taxi.yandex.net'],
            'no-network': ['no-network.taxi.yandex.net'],
            'different-network': ['different-network.taxi.yandex.net'],
        },
    )


async def test_routes_charlie(taxi_scout_web_oneshot, grpc_scout_channel):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)
    response = await rds_utils.stream_single_route_set(
        discovery_stub, tvm_name='envoy-exp-charlie',
    )
    rds_utils.assert_routes_response(response, ethalon={})


async def test_routes_nonexistent(taxi_scout_web_oneshot, grpc_scout_channel):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)
    response = await rds_utils.stream_single_route_set(
        discovery_stub, tvm_name=f'nonexistent',
    )
    rds_utils.assert_routes_response(response, ethalon={})


@pytest.mark.parametrize(
    'perforator_alive, clownductor_alive',
    [(True, False), (False, True), (False, False)],
    ids=['Dead Clownducor', 'Dead Perforator', 'All dead'],
)
async def test_routes_alpha_fallback(
        taxi_scout_web_oneshot,
        grpc_scout_channel,
        mockserver,
        perforator_alive,
        clownductor_alive,
):
    ethalon = {'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']}
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)

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

    await taxi_scout_web_oneshot.invalidate_caches()
    assert (
        retrieve_handler.times_called >= 1
        or service_values_handler.times_called >= 1
    )

    response = await rds_utils.stream_single_route_set(discovery_stub)
    rds_utils.assert_routes_response(response, ethalon=ethalon)


async def test_meta_version_changed(
        taxi_scout_web_oneshot, grpc_scout_channel, taxi_config,
):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)

    response = await rds_utils.stream_single_route_set(discovery_stub)
    rds_utils.assert_routes_response(
        response,
        ethalon={'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']},
        meta_version=1,
    )

    taxi_config.set_values({'SCOUT_XDS_META_VERSION': 2})
    await taxi_scout_web_oneshot.invalidate_caches()

    new_response = await rds_utils.stream_single_route_set(
        discovery_stub, version=response.version_info,
    )
    rds_utils.assert_routes_response(
        new_response,
        ethalon={'envoy-exp-bravo': ['envoy-exp-bravo.taxi.yandex.net']},
        meta_version=2,
    )


async def test_meta_version_newer(
        taxi_scout_web_oneshot, grpc_scout_channel, taxi_config,
):
    discovery_stub = envoy_rds.RouteDiscoveryServiceStub(grpc_scout_channel)

    try:
        await rds_utils.stream_single_route_set(
            discovery_stub,
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
