# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dataclasses
import typing

import pytest
from united_dispatch_delivery_plugins import *  # noqa: F403 F401
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


@pytest.fixture(name='united_dispatch_unit')
def _united_dispatch_unit(taxi_united_dispatch_delivery):
    return taxi_united_dispatch_delivery


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


def _proto_car_summary(time, distance):
    data = {'time': time, 'distance': distance}
    return yamaps_driving.proto_driving_summary(data)


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


def _is_points_equal(point1, point2):
    eps = 0.0001

    if abs(point1[0] - point2[0]) > eps or abs(point1[1] - point2[1]) > eps:
        return False

    return True


def _is_routes_equal(route1, route2):
    if len(route1) != len(route2):
        return False

    for i, _ in enumerate(route1):
        if not _is_points_equal(route1[i], route2[i]):
            return False

    return True


@pytest.fixture(autouse=False, name='mock_maps')
def _mock_maps(mockserver):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_car_route(request):
        points = _rll_to_array(request.query['rll'])
        for route in context.routes:
            if _is_routes_equal(points, route.points):
                return mockserver.make_response(
                    response=_proto_car_summary(
                        time=route.car_time, distance=route.car_distance,
                    ),
                    status=200,
                    content_type='application/x-protobuf',
                )

        assert False, 'Could not find route %s' % request.query['rll']
        return mockserver.make_response(status=500)

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_route(request):
        points = _rll_to_array(request.query['rll'])
        for route in context.routes:
            if _is_routes_equal(points, route.points):
                return mockserver.make_response(
                    response=_proto_masstransit_summary(
                        time=route.pedestrian_time,
                        distance=route.pedestrian_distance,
                    ),
                    status=200,
                    content_type='application/x-protobuf',
                )

        assert False, 'Could not find route %s' % request.query['rll']
        return mockserver.make_response(status=500)

    @dataclasses.dataclass
    class RouterData:
        points: typing.List[typing.List[float]]
        car_time: float
        car_distance: float
        pedestrian_time: float
        pedestrian_distance: float

    class Context:
        routes: typing.List[RouterData]

        def __init__(self):
            self.routes = []

        def add_route(self, points, **kwargs):
            self.routes.append(RouterData(points, **kwargs))

            for point in points:
                self.routes.append(
                    RouterData(
                        points=[point, point],
                        car_time=0,
                        car_distance=0,
                        pedestrian_time=0,
                        pedestrian_distance=0,
                    ),
                )

    context = Context()
    return context
