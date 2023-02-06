# pylint: disable=redefined-outer-name, import-error
import math
import uuid

import pytest
from yandex.maps.proto.common2 import response_pb2
from yandex.maps.proto.driving import route_pb2
from yandex.maps.proto.driving import section_pb2

from . import mocking_base


def _build_route(
        point_a,
        point_b,
        distance,
        time,
        londeltas,
        latdeltas,
        ways,
        blocked=False,
        has_toll_roads=False,
        traffic_jams_coeff=1.5,
):
    lon_a, lat_a = point_a
    lon_b, lat_b = point_b
    times = []
    for step in ways:
        times.append(round(step / 10))
    times.append(0)
    # checking correction of filled data
    lons = [lon_a]
    for dlon in londeltas:
        lons.append(lons[-1] + dlon / 1e6)
    assert math.isclose(lons[-1], lon_b)
    lats = [lat_a]
    for dlat in latdeltas:
        lats.append(lats[-1] + dlat / 1e6)
    assert math.isclose(lats[-1], lat_b)
    response = response_pb2.Response()
    main_geo = response.reply.geo_object.add()
    route_meta = main_geo.metadata.add()
    route = route_meta.Extensions[route_pb2.ROUTE_METADATA]
    route.route_id = str(uuid.uuid4())
    route.flags.blocked = blocked
    route.flags.has_tolls = has_toll_roads
    route.weight.time.value = time
    route.weight.time.text = ''
    route.weight.time_with_traffic.value = traffic_jams_coeff * time
    route.weight.time_with_traffic.text = ''
    route.weight.distance.value = distance
    route.weight.distance.text = ''
    point = route.route_point.add()
    point.position.lon = lon_a
    point.position.lat = lat_a
    point = route.route_point.add()
    point.position.lon = lon_b
    point.position.lat = lat_b
    path_geo = main_geo.geo_object.add()
    path_meta = path_geo.metadata.add()
    section = path_meta.Extensions[section_pb2.SECTION_METADATA]
    section.leg_index = 0
    section.weight.time.value = time
    section.weight.time.text = ''
    section.weight.time_with_traffic.value = traffic_jams_coeff * time
    section.weight.time_with_traffic.text = ''
    section.weight.distance.value = distance
    section.weight.distance.text = ''
    section.annotation.description = ''
    section.annotation.action_metadata.uturn_metadata.length = 0
    section.annotation.toponym = 'msk'
    geometry = path_geo.geometry.add()
    geometry.polyline.lons.first = int(lon_a * 1e6)
    for dlon in londeltas:
        geometry.polyline.lons.deltas.append(dlon)
    geometry.polyline.lats.first = int(lat_a * 1e6)
    for dlat in latdeltas:
        geometry.polyline.lats.deltas.append(dlat)
    return response


def _build_routes(
        builders, results_count, time_coefficient=1, distance_coefficient=1,
):
    response = response_pb2.Response()
    for i in range(0, results_count):
        if isinstance(builders, list):
            try:
                builder = builders[i]
            except IndexError:
                builder = builders[-1]
        else:
            builder = builders
        correction = 1.0 + i * 0.01
        route = builder(
            time_coefficient=time_coefficient * correction,
            distance_coefficient=distance_coefficient * correction,
        )
        response.reply.geo_object.append(route.reply.geo_object[0])
    return response


def _msk_easy_routes(
        results_count, time_coefficient=1, distance_coefficient=1,
):
    return _build_routes(
        _msk_easy_route, results_count, time_coefficient, distance_coefficient,
    )


def _msk_easy_route(time_coefficient=1, distance_coefficient=1):
    # от ТТК по Бакунинской, Спартаковской и Ст.Басманной до Садового
    return _build_route(
        point_a=(37.683, 55.774),
        point_b=(37.656, 55.764),
        time=205 * time_coefficient,
        distance=2046 * distance_coefficient,
        latdeltas=[-2000, -6000, -2000],
        londeltas=[-9000, -12000, -6000],
        ways=[605.2361, 1004.2539, 436.2784, 0],
    )


def _msk_blocked_routes(
        results_count,
        blocked_flags,
        time_coefficient=1,
        distance_coefficient=1,
):
    builders = []
    for i in range(0, results_count):
        if isinstance(blocked_flags, bool):
            flag = blocked_flags
        elif isinstance(blocked_flags, list):
            try:
                flag = blocked_flags[i]
            except IndexError:
                flag = blocked_flags[-1]
        else:
            raise Exception('unexpected argument type')
        builders.append(
            lambda time_coefficient, distance_coefficient, blocked=flag: (
                _msk_blocked_route(
                    blocked=blocked,
                    time_coefficient=time_coefficient,
                    distance_coefficient=distance_coefficient,
                )
            ),
        )
    return _build_routes(
        builders, results_count, time_coefficient, distance_coefficient,
    )


def _msk_blocked_route(
        blocked=True, time_coefficient=1, distance_coefficient=1,
):
    # от ТТК по Бакунинской, Спартаковской и Ст.Басманной до Садового
    return _build_route(
        point_a=(37.683, 55.774),
        point_b=(37.656, 55.764),
        time=205 * time_coefficient,
        distance=2046 * distance_coefficient,
        latdeltas=[-2000, -6000, -2000],
        londeltas=[-9000, -12000, -6000],
        ways=[605.2361, 1004.2539, 436.2784, 0],
        blocked=blocked,
    )


def _msk_route_with_toll_roads(time_coefficient=1):
    # от ТТК по Бакунинской, Спартаковской и Ст.Басманной до Садового
    return _build_route(
        point_a=(37.683, 55.774),
        point_b=(37.656, 55.764),
        time=205 * time_coefficient,
        distance=2046,
        latdeltas=[-2000, -6000, -2000],
        londeltas=[-9000, -12000, -6000],
        ways=[605.2361, 1004.2539, 436.2784, 0],
        blocked=False,
        has_toll_roads=True,
    )


def _long_route():
    # moscow --> spb
    return _build_route(
        point_a=(37.683, 55.774),
        point_b=(30.317992, 59.926419),
        time=11000,
        distance=634907,
        latdeltas=[4152419],
        londeltas=[-7365008],
        ways=[634907, 0],
    )


def _zero_delta_route():
    return _build_route(
        point_a=(37.683, 55.774),
        point_b=(37.683, 55.774),
        time=0,
        distance=0,
        latdeltas=[0],
        londeltas=[0],
        ways=[0],
        blocked=True,
    )


def _custom_time_distance_route(time, distance):
    return _build_route(
        point_a=(37.683, 55.774),
        point_b=(30.317992, 59.926419),
        time=time,
        distance=distance,
        latdeltas=[4152419],
        londeltas=[-7365008],
        ways=[634907, 0],
        traffic_jams_coeff=1,
    )


class CustomRouteDescriptor:
    def __init__(
            self,
            point_a,
            point_b,
            time,
            distance,
            latdeltas,
            londeltas,
            ways,
            traffic_jams_coeff,
    ):
        self.point_a = point_a
        self.point_b = point_b
        self.time = time
        self.distance = distance
        self.latdeltas = latdeltas
        self.londeltas = londeltas
        self.ways = ways
        self.traffic_jams_coeff = traffic_jams_coeff

    def __call__(self, time_coefficient, distance_coefficient):
        return _build_custom_route(
            self, time_coefficient, distance_coefficient,
        )


def _build_custom_route(
        route_descriptor, time_coefficient=1, distance_coefficient=1,
):
    return _build_route(
        point_a=route_descriptor.point_a,
        point_b=route_descriptor.point_b,
        time=route_descriptor.time,
        distance=route_descriptor.distance,
        latdeltas=route_descriptor.latdeltas,
        londeltas=route_descriptor.londeltas,
        ways=route_descriptor.ways,
        traffic_jams_coeff=route_descriptor.traffic_jams_coeff,
    )


def _build_custom_routes(
        route_descriptors, time_coefficient=1, distance_coefficient=1,
):
    return _build_routes(
        route_descriptors,
        len(route_descriptors),
        time_coefficient,
        distance_coefficient,
    )


def _build_voskresensks_custom_router_descriptors():
    descriptors = [
        CustomRouteDescriptor(
            point_a=(38.726549, 55.343154),
            point_b=(38.658536, 55.325139),
            time=923,
            distance=6474.137065649033,
            latdeltas=[-15054, 11100, 5700, 7400, 5000, -4600, -11600, -15961],
            londeltas=[
                -67249,
                16500,
                19500,
                26800,
                11300,
                6500,
                -9400,
                -71964,
            ],
            ways=[],
            traffic_jams_coeff=1,
        ),
        CustomRouteDescriptor(
            point_a=(38.726549, 55.343154),
            point_b=(38.658536, 55.325139),
            time=835,
            distance=9852.260175466537,
            latdeltas=[
                -1454,
                800,
                -1500,
                100,
                -7100,
                -7200,
                -1000,
                -2000,
                -54770549,
                54771888,
            ],
            londeltas=[
                -149,
                -5200,
                -800,
                -2200,
                -6600,
                300,
                -28100,
                -2300,
                -38294831,
                38271867,
            ],
            ways=[],
            traffic_jams_coeff=1,
        ),
    ]
    return descriptors


class YamapsRouterContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = _msk_easy_route()
        self.content_type = 'application/x-protobuf'
        self.tolls = False
        self.dtm = None
        self.rll = None
        self.user_id = None
        self.intent = 'ROUTESTATS'
        self.vehicle_type = 'taxi'
        self.use_manoeuvres = None

    def set_easy_msk_nojams(self, results_count=1):
        if results_count > 1:
            self.response = _msk_easy_routes(results_count)
        else:
            self.response = _msk_easy_route()

    def set_long_route(self):
        self.response = _long_route()

    def set_empty(self):
        self.response = response_pb2.Response()

    def set_blocked(self, results_count=1, routes_blocks=True):
        if results_count > 1:
            self.response = _msk_blocked_routes(results_count, routes_blocks)
        else:
            self.response = _msk_blocked_route()

    def set_voskresensks_custom_routes(self):
        self.response = _build_custom_routes(
            _build_voskresensks_custom_router_descriptors(),
        )

    def set_with_toll_roads(self):
        self.response = _msk_route_with_toll_roads()

    def set_zero_delta_route(self):
        self.response = _zero_delta_route()

    def set_custom_time_distance_route(self, time, distance):
        self.response = _custom_time_distance_route(time, distance)

    def set_tolls(self, tolls_bool):
        self.tolls = tolls_bool

    def set_dtm(self, dtm):
        self.dtm = dtm

    def set_rll(self, route):
        self.rll = route

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_intent(self, intent):
        self.intent = intent

    def set_vehicle_type(self, vehicle_type):
        self.vehicle_type = vehicle_type

    def set_use_manoeuvres(self, use_manoeuvres):
        self.use_manoeuvres = use_manoeuvres

    def check_request(self, request):
        params = request.args
        assert 'rll' in params
        assert (
            'vehicle_type' in params
            and params['vehicle_type'] == self.vehicle_type
        )

        if self.tolls:
            assert 'avoid' not in params or 'tolls' not in params['avoid']
        else:
            assert 'avoid' in params and 'tolls' in params['avoid']

        if self.dtm:
            assert params['dtm'] == str(self.dtm)
        else:
            assert 'dtm' not in params

        if self.rll is not None:
            assert params['rll'] == self.rll

        if self.user_id is not None:
            assert params['user_id'] == self.user_id

        if self.intent is not None:
            assert params['intent'] == self.intent

        if self.use_manoeuvres:
            assert (
                params['experimental_stopwatch_use_manoeuvre_id_jams']
                == self.use_manoeuvres
            )

        headers = request.headers
        assert 'Accept' in headers and headers['Accept'] == self.content_type


@pytest.fixture
def yamaps_router():
    return YamapsRouterContext()


class TigraphRouterContext(mocking_base.BasicMock):
    def check_request(self, request):
        pass

    def process(self, mockserver):
        raise mockserver.TimeoutError()


@pytest.fixture
def tigraph_router():
    return TigraphRouterContext()


@pytest.fixture
def mock_yamaps_router(mockserver, yamaps_router):
    @mockserver.handler('maps-router/v2/route')
    async def yamaps_router_handler(request):
        yamaps_router.check_request(request)
        return yamaps_router.process(mockserver)

    return yamaps_router_handler


@pytest.fixture
def mock_tigraph_router(mockserver, tigraph_router):
    @mockserver.handler('tigraph-router/route')
    async def tigraph_router_handler(request):
        tigraph_router.check_request(request)
        return tigraph_router.process(mockserver)

    return tigraph_router_handler
