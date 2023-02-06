# flake8: noqa
# pylint: disable=import-error,wildcard-import
from driver_route_responder_plugins.generated_tests import *
from geobus_tools import geobus  # noqa: F401 C5521

import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
from tests_plugins import utils

import pytest


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


POSITIONS_CHANNEL = 'channel:yagr:position'

POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
DRIVER_POS = [37.46611, 55.727179]
DRIVER_ID = 'dbid1_uuid1'
ORDER_IDS = ['order_id_1', 'order_id_2']
ORDER_CORE_RESP_1 = {
    'fields': {
        'performer': {'candidate_index': 0},
        'order': {
            'taxi_status': 'driving',
            'status': 'assigned',
            'request': {'source': {'geopoint': POINTS[2]}, 'destinations': []},
        },
        'candidates': [
            {
                'time': 100000,
                'dist': 2000000,
                'cp': {'id': ORDER_IDS[0], 'dest': POINTS[1]},
            },
        ],
    },
    'order_id': ORDER_IDS[1],
    'replica': 'master',
    'version': '5',
}

ORDER_CORE_RESP_2 = {
    'fields': {
        'performer': {'candidate_index': 0},
        'order': {'taxi_status': 'transporting', 'status': 'assigned'},
        'candidates': [{'time': 100000, 'dist': 2000000}],
        'candidate_index': 0,
    },
    'order_id': ORDER_IDS[0],
    'replica': 'master',
    'version': '5',
}


@pytest.mark.servicetest
async def test_timeleft_fallback_car_router(
        driver_route_responder_adv, mockserver, load_binary, now, statistics,
):
    transporting_points = [
        [37.451695, 55.723917],
        [37.473896, 55.728358],
        [37.518952, 55.736290],
    ]
    source = [37.4516, 55.7239]
    raw_position = [37.455596, 55.719463]
    destinations = transporting_points

    driver_id = 'driver0dbid_driver0uuid'
    order_id = 'orderid123'

    request_body = {
        'driver': driver_id,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': True,
        'verbose_log': False,
        'mode': 'sharedroute',
        'order_id': order_id,
    }

    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': raw_position,
            'direction': 45,
            'unix_time': timestamp * 1000,
            'speed': 11,
            'accuracy': 1,
            'source': 'AndroidGps',
            'timestamp': timestamp,
        },
    ]
    message = geobus.serialize_positions_v2(drivers, now)

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == [raw_position] + destinations
        return mockserver.make_response(
            response=load_binary(
                'maps_response-37.455596,55.719463'
                '~37.451695,55.723917~'
                '37.473896,55.728358~'
                '37.518952,55.73629.pb',
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        del request
        proc_destinations = [{'geopoint': x} for x in destinations]
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {
                        'taxi_status': 'transporting',
                        'status': 'assigned',
                        'request': {
                            'source': {'geopoint': source},
                            'destinations': proc_destinations,
                        },
                    },
                    'destinations_statuses': [False, False],
                },
                'order_id': order_id,
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    await driver_route_responder_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
@pytest.mark.parametrize(
    'alt_type,taxi_status,router_resp_filename,drr_resp_filename',
    [
        (
            'combo_order',
            'transporting',
            'router_transporting.pb',
            'drr_combo_transporting_resp.json',
        ),
        (
            'combo_inner',
            'transporting',
            'router_transporting.pb',
            'drr_combo_transporting_resp.json',
        ),
        (
            'combo_outer',
            'transporting',
            'router_transporting.pb',
            'drr_combo_transporting_resp.json',
        ),
        (
            'combo_order',
            'driving',
            'router_driving.pb',
            'drr_combo_driving_resp.json',
        ),
        (
            'combo_inner',
            'driving',
            'router_driving.pb',
            'drr_combo_driving_resp.json',
        ),
        (
            'combo_outer',
            'driving',
            'router_driving.pb',
            'drr_combo_driving_resp.json',
        ),
    ],
)
async def test_timeleft_combo_router_fallback(
        driver_route_responder_adv,
        mockserver,
        now,
        load_json,
        alt_type,
        taxi_status,
        router_resp_filename,
        drr_resp_filename,
):
    transporting_points = [
        [37.451695, 55.723917],
        [37.473896, 55.728358],
        [37.518952, 55.736290],
    ]
    source = [37.4516, 55.7239]
    raw_position = [37.455596, 55.719463]
    destinations = transporting_points

    driver_id = 'driver0dbid_driver0uuid'
    order_id = 'combo_order_id'
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': raw_position,
            'direction': 45,
            'unix_time': timestamp * 1000,
            'speed': 11,
            'accuracy': 1,
            'source': 'AndroidGps',
            'timestamp': timestamp,
        },
    ]
    message = geobus.serialize_positions_v2(drivers, now)

    request_body = {
        'driver': driver_id,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': order_id,
    }

    summary_results = {
        '37.451600,55.723900': (300, 1000),
        '37.451695,55.723917': (400, 1500),
        '37.473896,55.728358': (500, 2000),
        '37.518952,55.736290': (600, 3000),
    }

    @mockserver.json_handler('/maps-router/v2/summary')
    def _mock_router_summary(request):
        time, dist = summary_results[request.args['rll'].split('~')[-1]]
        return mockserver.make_response(
            response=_proto_driving_summary(time, dist),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        resp = None
        proc_destinations = [{'geopoint': x} for x in destinations]
        if request.json['order_id'] == order_id:
            resp = {
                'fields': {
                    'performer': {'candidate_index': 0},
                    'order': {
                        'request': {
                            'source': {'geopoint': source},
                            'destinations': proc_destinations,
                        },
                        'taxi_status': taxi_status,
                        'status': 'assigned',
                        'calc': {'alternative_type': alt_type},
                    },
                    'candidates': [{'time': 100000, 'dist': 2000000}],
                },
                'order_id': order_id,
                'replica': 'master',
                'version': '5',
            }
        assert resp is not None
        return mockserver.make_response(json=resp, status=200)

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        return mockserver.make_response(status=200)

    await driver_route_responder_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(drr_resp_filename)


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['berlin'], 'routers': ['google']},
    ],
    ROUTER_GOOGLE_ENABLED=True,
)
@pytest.mark.servicetest
async def test_timeleft_fallback_zone(
        driver_route_responder_adv, mockserver, load_json, now,
):
    """
    In this test, we check that fallbacks respect the zone of the order.
    We set google router for zone 'berlin', set same zone in order-core
    for this driver and then send request that is guaranteed to fallback.
    """
    transporting_points = [[37.451695, 55.723917], [37.473896, 55.728358]]
    source = [37.4516, 55.7239]
    raw_position = [37.455596, 55.719463]
    destinations = transporting_points

    driver_id = 'driver1dbid_driver1uuid'
    order_id = 'orderid123'

    request_body = {
        'driver': driver_id,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': True,
        'verbose_log': False,
        'mode': 'sharedroute',
        'order_id': order_id,
    }

    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': raw_position,
            'direction': 45,
            'unix_time': timestamp * 1000,
            'speed': 11,
            'accuracy': 1,
            'source': 'AndroidGps',
            'timestamp': timestamp,
        },
    ]
    message = geobus.serialize_positions_v2(drivers, now)

    @mockserver.json_handler(
        '/maps-google-router/google/maps/api/directions/json',
    )
    def _mock_google_router(request):
        del request
        return mockserver.make_response(
            json=load_json('router_google_response.json'), status=200,
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        del request
        proc_destinations = [{'geopoint': x} for x in destinations]
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {
                        'taxi_status': 'transporting',
                        'status': 'assigned',
                        'nz': 'berlin',
                        'request': {
                            'source': {
                                'geopoint': source,
                                'country': 'Germany',
                            },
                            'destinations': proc_destinations,
                        },
                    },
                    'destinations_statuses': [False, False],
                },
                'order_id': order_id,
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    await driver_route_responder_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert _mock_google_router.times_called > 0


@pytest.mark.servicetest
async def test_timeleft_fallback_in_driving_without_destination(
        driver_route_responder_adv, mockserver, load_binary, now,
):
    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': False,
        'order_id': ORDER_IDS[1],
    }

    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': DRIVER_ID,
            'position': DRIVER_POS,
            'direction': 45,
            'unix_time': timestamp * 1000,
            'speed': 11,
            'accuracy': 1,
            'source': 'AndroidGps',
            'timestamp': timestamp,
        },
    ]
    message = geobus.serialize_positions_v2(drivers, now)

    @mockserver.json_handler('/maps-router/v2/summary')
    def _mock_router_summary(request):
        rll = _rll_to_array(request.args['rll'])
        if rll not in (
                [DRIVER_POS, POINTS[1], POINTS[2]],
                [DRIVER_POS, POINTS[1]],
        ):
            assert False
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        resp = None
        if request.json['order_id'] == ORDER_IDS[1]:
            resp = ORDER_CORE_RESP_1
        elif request.json['order_id'] == ORDER_IDS[0]:
            resp = ORDER_CORE_RESP_2
        assert resp is not None
        return mockserver.make_response(json=resp, status=200)

    await driver_route_responder_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
