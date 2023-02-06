# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import flatbuffers
import pytest
from reposition.fbs.v1.service.bulk_state import (
    DriverBonus as BulkStateDriverBonus,
)
from reposition.fbs.v1.service.bulk_state import (
    DriverResponse as BulkStateDriverResponse,
)
from reposition.fbs.v1.service.bulk_state import GeoPoint as BulkStateGeoPoint
from reposition.fbs.v1.service.bulk_state import Request as BulkStateRequest
from reposition.fbs.v1.service.bulk_state import Response as BulkStateResponse
from reposition.fbs.v1.service.bulk_state import (
    RouterInfo as BulkStateRouterInfo,
)
from reposition_matcher.fbs.v1.service.match_orders_drivers import CheckRequest
from reposition_matcher.fbs.v1.service.match_orders_drivers import Driver
from reposition_matcher.fbs.v1.service.match_orders_drivers import GeoPoint
from reposition_matcher.fbs.v1.service.match_orders_drivers import OkResponse
from reposition_matcher.fbs.v1.service.match_orders_drivers import Order
from reposition_matcher.fbs.v1.service.match_orders_drivers import Request
from reposition_matcher.fbs.v1.service.match_orders_drivers import RouteInfo
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521
from yamaps_tools import (
    driving_matrix as yamaps_driving_matrix,
)  # noqa: F401 C5521

from reposition_matcher_plugins import *  # noqa: F403 F401


class Context:
    def __init__(self):
        self.data = None
        self.handler = None

    def set_data(self, data):
        self.data = data

    def times_called(self):
        return self.handler.times_called


@pytest.fixture(name='reposition_share_cache')
def reposition_share_cache(
        taxi_reposition_matcher, taxi_config, mockserver, testpoint,
):
    class CacheContext(Context):
        def __init__(self):
            Context.__init__(self)

            self.content = None
            self.testpoint = None

        async def update(self, zones, share, fallbacks=None):
            if not fallbacks:
                fallbacks = {
                    '__default__': {'__default__': {'threshold': 101}},
                }

            response = {'generic': {}, 'reposition': {}}

            value_total = 0
            share_count = 0

            for tariff, value in share.items():
                assert value <= 100

                generic = {
                    'free': 100,
                    'on_order': 0,
                    'free_chain': 0,
                    'total': 100,
                    'free_chain_groups': {'short': 0, 'medium': 0, 'long': 0},
                }
                reposition = {
                    'free': value,
                    'on_order': 0,
                    'free_chain': 0,
                    'total': value,
                    'free_chain_groups': {'short': 0, 'medium': 0, 'long': 0},
                }

                response['generic'][tariff] = generic
                response['reposition'][tariff] = reposition

                value_total += value
                share_count += 1

            Context.set_data(self, response)

            taxi_config.set_values(
                {
                    'REPOSITION_MATCHER_REPOSITION_SHARE_CACHE_CONFIG': {
                        'zones': zones,
                        'fallbacks': fallbacks,
                        'request_timeout_ms': 3000,
                        'request_attempts': 3,
                    },
                },
            )

            await taxi_reposition_matcher.invalidate_caches()
            await self.testpoint.wait_call()

            share_expected = {}

            for zone in zones:
                share_expected[zone] = {}

                for category, value in share.items():
                    share_expected[zone][category] = {
                        'reposition-free-of-total-free': {
                            'reposition-share-value': value,
                            'reposition-share-threshold-exceeded': 0,
                        },
                        'reposition-onorder-of-reposition-any': {
                            'reposition-share-value': 0,
                            'reposition-share-threshold-exceeded': 0,
                        },
                    }

                share_expected[zone]['__total__'] = {
                    'reposition-free-of-total-free': {
                        'reposition-share-value': value_total // share_count,
                        'reposition-share-threshold-exceeded': 0,
                    },
                    'reposition-onorder-of-reposition-any': {
                        'reposition-share-value': 0,
                        'reposition-share-threshold-exceeded': 0,
                    },
                }

            share_expected['__any__'] = {
                '__any__': {
                    'reposition-free-of-total-free': {
                        'reposition-share-threshold-exceeded': 0,
                    },
                    'reposition-onorder-of-reposition-any': {
                        'reposition-share-threshold-exceeded': 0,
                    },
                },
            }

            assert self.content == share_expected

    context = CacheContext()

    @mockserver.json_handler('/candidates/count-by-categories')
    def _mock_count_by_categories(request):
        nonlocal context

        return mockserver.make_response(
            status=200,
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json=context.data,
        )

    @testpoint('reposition-share-cache')
    def _tp_cache(content):
        nonlocal context

        context.content = content

    context.handler = _mock_count_by_categories
    context.testpoint = _tp_cache

    return context


@pytest.fixture(name='match_orders_drivers')
def match_orders_drivers(taxi_reposition_matcher):
    def _build_request(data):
        builder = flatbuffers.Builder(0)

        requests = []

        for request in data['check_requests']:
            pickup_route_info = None

            if 'pickup_route_info' in request:
                da_route = request['pickup_route_info']

                RouteInfo.RouteInfoStart(builder)
                RouteInfo.RouteInfoAddDistance(builder, da_route['distance'])
                RouteInfo.RouteInfoAddTime(builder, da_route['time'])
                pickup_route_info = RouteInfo.RouteInfoEnd(builder)

            CheckRequest.CheckRequestStart(builder)
            CheckRequest.CheckRequestAddOrderId(builder, request['order_id'])
            CheckRequest.CheckRequestAddDriverId(builder, request['driver_id'])

            if pickup_route_info:
                CheckRequest.CheckRequestAddPickupRouteInfo(
                    builder, pickup_route_info,
                )

            requests.append(CheckRequest.CheckRequestEnd(builder))

        Request.RequestStartCheckRequestsVector(builder, len(requests))

        for request in reversed(requests):
            builder.PrependUOffsetTRelative(request)

        requests = builder.EndVector(len(requests))

        drivers = []

        for driver in data['drivers']:
            dbid = builder.CreateString(driver['dbid'])
            uuid = builder.CreateString(driver['uuid'])

            Driver.DriverStart(builder)

            Driver.DriverAddDbid(builder, dbid)
            Driver.DriverAddUuid(builder, uuid)

            Driver.DriverAddPosition(
                builder,
                GeoPoint.CreateGeoPoint(
                    builder, driver['position'][1], driver['position'][0],
                ),
            )

            if 'chain_point' in driver:
                Driver.DriverAddChainPoint(
                    builder,
                    GeoPoint.CreateGeoPoint(
                        builder,
                        driver['chain_point'][1],
                        driver['chain_point'][0],
                    ),
                )

            drivers.append(Driver.DriverEnd(builder))

        Request.RequestStartDriversVector(builder, len(drivers))

        for driver in reversed(drivers):
            builder.PrependUOffsetTRelative(driver)

        drivers = builder.EndVector(len(drivers))

        orders = []

        for order in data['orders']:
            id_ = builder.CreateString(order['id'])
            zone = builder.CreateString(order['zone'])

            allowed_classes = [
                builder.CreateString(allowed_class)
                for allowed_class in order['allowed_classes']
            ]

            Order.OrderStartAllowedClassesVector(builder, len(allowed_classes))

            for allowed_class in allowed_classes:
                builder.PrependUOffsetTRelative(allowed_class)

            allowed_classes = builder.EndVector(len(allowed_classes))

            Order.OrderStart(builder)
            Order.OrderAddId(builder, id_)
            Order.OrderAddZone(builder, zone)
            Order.OrderAddAllowedClasses(builder, allowed_classes)
            Order.OrderAddPickup(
                builder,
                GeoPoint.CreateGeoPoint(
                    builder, order['pickup'][1], order['pickup'][0],
                ),
            )
            Order.OrderAddDestination(
                builder,
                GeoPoint.CreateGeoPoint(
                    builder, order['destination'][1], order['destination'][0],
                ),
            )

            orders.append(Order.OrderEnd(builder))

        Request.RequestStartOrdersVector(builder, len(orders))

        for order in reversed(orders):
            builder.PrependUOffsetTRelative(order)

        orders = builder.EndVector(len(orders))

        Request.RequestStart(builder)

        Request.RequestAddOrders(builder, orders)
        Request.RequestAddDrivers(builder, drivers)
        Request.RequestAddCheckRequests(builder, requests)

        request = Request.RequestEnd(builder)

        builder.Finish(request)

        return builder.Output()

    def _parse_response(data):
        response = OkResponse.OkResponse.GetRootAsOkResponse(data, 0)

        result = []

        for i in range(0, response.CheckResultsLength()):
            check_result = response.CheckResults(i)

            result.append(
                {
                    'driver_id': check_result.DriverId(),
                    'order_id': check_result.OrderId(),
                    'suitable': check_result.Suitable(),
                    'mode': (
                        check_result.Mode().decode('utf-8')
                        if check_result.Mode()
                        else None
                    ),
                    'score': check_result.Score(),
                },
            )

        return result

    async def _call(request):
        response = await taxi_reposition_matcher.post(
            '/v1/service/match_orders_drivers',
            headers={'Content-Type': 'application/x-flatbuffers'},
            data=_build_request(request),
        )

        assert response.status_code == 200

        return _parse_response(response.content)

    return _call


@pytest.fixture(name='mock_reposition_api_bulk_state')
def mock_reposition_api_bulk_state(mockserver):
    context = Context()

    def _parse_bulk_state_request(data):
        request = BulkStateRequest.Request.GetRootAsRequest(data, 0)

        drivers = []

        for idx in range(request.DriversLength()):
            driver = request.Drivers(idx)

            driver_profile_id = driver.DriverProfileId().decode('utf-8')
            park_db_id = driver.ParkDbId().decode('utf-8')

            drivers.append(
                {
                    'driver_profile_id': driver_profile_id,
                    'park_db_id': park_db_id,
                },
            )

        return {'drivers': drivers}

    def _build_bulk_state_response(data):
        builder = flatbuffers.Builder(0)

        states = []

        for state in data['states']:
            has_session = state['has_session']
            mode = builder.CreateString(state['mode'])

            submode = None
            if 'submode' in state and state['submode']:
                submode = builder.CreateString(state['submode'])

            active = state['active']

            bonus = None
            if 'bonus' in state and state['bonus']:
                BulkStateDriverBonus.DriverBonusStart(builder)
                BulkStateDriverBonus.DriverBonusAddUntil(
                    builder, state['bonus']['until'],
                )
                bonus = BulkStateDriverBonus.DriverBonusEnd(builder)

            area_radius = None
            if 'area_radius' in state and state['area_radius']:
                area_radius = state['area_radius']

            session_id = state['session_id']

            start_timestamp = None
            if 'start_timestamp' in state and state['start_timestamp']:
                start_timestamp = state['start_timestamp']

            start_router_info = None
            if 'start_router_info' in state and state['start_router_info']:
                BulkStateRouterInfo.RouterInfoStart(builder)
                BulkStateRouterInfo.RouterInfoAddTime(
                    builder, state['start_router_info']['time'],
                )
                BulkStateRouterInfo.RouterInfoAddDist(
                    builder, state['start_router_info']['dist'],
                )
                start_router_info = BulkStateRouterInfo.RouterInfoEnd(builder)

            BulkStateDriverResponse.DriverResponseStart(builder)

            BulkStateDriverResponse.DriverResponseAddHasSession(
                builder, has_session,
            )
            BulkStateDriverResponse.DriverResponseAddMode(builder, mode)
            if submode:
                BulkStateDriverResponse.DriverResponseAddSubmode(
                    builder, submode,
                )
            BulkStateDriverResponse.DriverResponseAddActive(builder, active)
            if bonus:
                BulkStateDriverResponse.DriverResponseAddBonus(builder, bonus)
            BulkStateDriverResponse.DriverResponseAddPoint(
                builder,
                BulkStateGeoPoint.CreateGeoPoint(
                    builder,
                    state['point']['latitude'],
                    state['point']['longitude'],
                ),
            )
            BulkStateDriverResponse.DriverResponseAddSessionId(
                builder, session_id,
            )
            BulkStateDriverResponse.DriverResponseAddStartPoint(
                builder,
                BulkStateGeoPoint.CreateGeoPoint(
                    builder,
                    state['start_point']['latitude'],
                    state['start_point']['longitude'],
                ),
            )
            if area_radius:
                BulkStateDriverResponse.DriverResponseAddAreaRadius(
                    builder, area_radius,
                )
            if start_timestamp:
                BulkStateDriverResponse.DriverResponseAddStartTimestamp(
                    builder, start_timestamp,
                )
            if start_router_info:
                BulkStateDriverResponse.DriverResponseAddStartRouterInfo(
                    builder, start_router_info,
                )

            states.append(BulkStateDriverResponse.DriverResponseEnd(builder))

        BulkStateResponse.ResponseStartStatesVector(builder, len(states))

        for state in reversed(states):
            builder.PrependUOffsetTRelative(state)
        states = builder.EndVector(len(states))

        BulkStateResponse.ResponseStart(builder)

        BulkStateResponse.ResponseAddStates(builder, states)

        response = BulkStateResponse.ResponseEnd(builder)

        builder.Finish(response)

        return builder.Output()

    @mockserver.handler('/reposition-api/v1/service/bulk_state')
    def _mock_bulk_state(request):
        nonlocal context

        return mockserver.make_response(
            status=200,
            content_type='application/x-flatbuffers',
            response=_build_bulk_state_response(context.data),
        )

    context.handler = _mock_bulk_state

    return context


@pytest.fixture(name='mock_router_regular')
def mock_router_regular(mockserver):
    context = Context()

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router_regular(request):
        nonlocal context

        assert context.data
        assert request.method == 'GET'

        segments = request.query.get('rll').split('~')

        fst = [float(e) for e in segments[0].split(',')]
        snd = [float(e) for e in segments[1].split(',')]

        assert len(fst) == 2 and len(snd) == 2

        k = round(snd[1], 2)

        time = context.data[k]['time']
        distance = context.data[k]['distance']

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=yamaps_driving.proto_driving_summary_time_distance(
                time=time, distance=distance,
            ),
        )

    context.handler = _mock_router_regular

    return context


@pytest.fixture(name='mock_router_matrix')
def mock_router_matrix(mockserver):
    context = Context()

    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_router_matrix(request):
        nonlocal context

        assert context.data
        assert request.method == 'GET'

        cnt = len(request.query.get('srcll').split('~'))
        cnt2 = len(request.query.get('dstll').split('~'))

        point_arg = 'dstll'

        if cnt == 1 and cnt2 > 1:
            point_arg = 'srcll'

        dst = request.query.get(point_arg)

        point = [float(e) for e in dst.split(',')]

        assert len(point) == 2

        k = round(point[1], 2)

        data = []
        for _ in range(0, cnt):
            data.append(context.data[k])

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=yamaps_driving_matrix.proto_matrix(data),
        )

    context.handler = _mock_router_matrix

    return context
