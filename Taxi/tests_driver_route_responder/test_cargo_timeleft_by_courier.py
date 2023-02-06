# flake8: noqa
# pylint: disable=import-error,wildcard-import,too-many-lines
from driver_route_responder_plugins.generated_tests import *

from geobus_tools import geobus  # noqa: F401 C5521

import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
from tests_plugins import utils

import pytest
import copy

POSITIONS_CHANNEL = 'channel:yagr:position'
TIMELEFTS_CHANNEL = 'channel:drw:timelefts'
TIMELEFTS_CHANNEL_NG = 'channel:drw:ng:timelefts'

POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
DRIVER_POS = [37.46611, 55.727179]
DRIVER_ID = 'dbid1_uuid1'
ORDER_IDS = ['order_id_1', 'order_id_2']
POINT_IDS = ['point_id_1', 'point_id_2', 'point_id_3']
CARGO_ORDER_ID = '7feb24af-fc38-44de-bc38-04defc3804de'

TIMELEFTS = {
    'tracking_type': 'RouteTracking',
    'contractor_id': DRIVER_ID,
    'route_id': '0',
    'adjusted_pos': DRIVER_POS,
    'timeleft_data': [
        {
            'destination_position': POINTS[0],
            'distance_left': 1233,
            'service_id': 'cargo-dispatch',
            'order_id': ORDER_IDS[0],
            'point_id': POINT_IDS[0],
            'time_left': 231,
        },
        {
            'destination_position': POINTS[1],
            'distance_left': 2438,
            'service_id': 'cargo-dispatch',
            'order_id': ORDER_IDS[0],
            'point_id': POINT_IDS[1],
            'time_left': 532,
        },
        {
            'destination_position': POINTS[2],
            'distance_left': 5432,
            'service_id': 'cargo-dispatch',
            'order_id': ORDER_IDS[1],
            'point_id': POINT_IDS[2],
            'time_left': 906,
        },
    ],
    'adjusted_segment_index': 0,
}

EXPECTED_TIMELEFTS = {
    'tracking_type': 'RouteTracking',
    'contractor_id': DRIVER_ID,
    'route_id': '0',
    'adjusted_pos': DRIVER_POS,
    'timeleft_data': [
        {
            'destination_position': POINTS[0],
            'time_distance_left': {'distance': 1233, 'time': 231},
            'service_id': 'cargo-dispatch',
            'order_id': ORDER_IDS[0],
            'point_id': POINT_IDS[0],
        },
        {
            'destination_position': POINTS[1],
            'time_distance_left': {'distance': 2438, 'time': 532},
            'service_id': 'cargo-dispatch',
            'order_id': ORDER_IDS[0],
            'point_id': POINT_IDS[1],
        },
        {
            'destination_position': POINTS[2],
            'time_distance_left': {'distance': 5432, 'time': 906},
            'service_id': 'cargo-dispatch',
            'order_id': ORDER_IDS[1],
            'point_id': POINT_IDS[2],
        },
    ],
    'adjusted_segment_index': 0,
}

EXPECTED_REQUEST = {
    'courier': DRIVER_ID,
    'etas': [
        {
            'distance_left': 1233.0,
            'order_id': ORDER_IDS[0],
            'point': POINTS[0],
            'point_id': POINT_IDS[0],
            'raw_distance_left': 1233.0,
            'raw_time_left': 231.0,
            'time_left': 231.0,
        },
        {
            'distance_left': 2438.0,
            'order_id': ORDER_IDS[0],
            'point': POINTS[1],
            'point_id': POINT_IDS[1],
            'raw_distance_left': 2438.0,
            'raw_time_left': 532.0,
            'time_left': 532.0,
        },
        {
            'distance_left': 5432.0,
            'order_id': ORDER_IDS[1],
            'point': POINTS[2],
            'point_id': POINT_IDS[2],
            'raw_distance_left': 5432.0,
            'raw_time_left': 906.0,
            'time_left': 906.0,
        },
    ],
    'position': DRIVER_POS,
}


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


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.mark.servicetest
async def test_cargo_timeleft_by_courier_200(
        driver_route_responder_adv, mockserver, now, testpoint, statistics,
):
    async with statistics.capture(driver_route_responder_adv) as capture:
        timelefts = copy.deepcopy(TIMELEFTS)
        timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
        timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

        expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
        expected_timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
        expected_timelefts['update_timestamp'] = int(
            utils.timestamp(now) * 1000,
        )

        message = {
            'timestamp': int(utils.timestamp(now)),
            'payload': [timelefts],
        }

        @testpoint('received-timelefts')
        def recieved_timelefts(received_msg):
            assert received_msg['data'] == [expected_timelefts]

        ser_mes = geobus.timelefts.serialize_message(message, now)
        await driver_route_responder_adv.sync_send_to_channel(
            TIMELEFTS_CHANNEL, ser_mes,
        )

        assert recieved_timelefts.times_called == 1

        body = {
            'courier': DRIVER_ID,
            'verification_data': {'cargo_order_id': CARGO_ORDER_ID},
        }
        response = await driver_route_responder_adv.post(
            'cargo/timeleft-by-courier', json=body,
        )
        assert response.status_code == 200
        assert response.json() == EXPECTED_REQUEST

    assert (
        capture.statistics[
            'handler.contractor-transport./v1/transport-active/updates-get.success'
        ]
        == 1
    )


@pytest.mark.servicetest
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_route_responder_cargo_use_verification',
    consumers=['driver-route-responder/contractor'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'title': 'Условие segmentation',
            'value': {'enabled': True},
        },
    ],
)
async def test_cargo_timeleft_by_courier_with_verification_200(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    expected_request = copy.deepcopy(EXPECTED_REQUEST)
    expected_request['courier'] = 'dbid2_uuid2'

    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': 'dbid2_uuid2',
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

    await driver_route_responder_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/route-watch/info')
    def _mock_cargo_dispatch_route_watch_info(request):
        assert request.json['cargo_order_id'] == CARGO_ORDER_ID
        resp = {
            'path': [
                {
                    'point': POINTS[0],
                    'order_id': ORDER_IDS[0],
                    'point_id': POINT_IDS[0],
                },
                {
                    'point': POINTS[1],
                    'order_id': ORDER_IDS[0],
                    'point_id': POINT_IDS[1],
                },
                {
                    'point': POINTS[2],
                    'order_id': ORDER_IDS[1],
                    'point_id': POINT_IDS[2],
                },
            ],
            'transport_type': 'car',
        }
        return mockserver.make_response(json=resp, status=200)

    @mockserver.json_handler('/maps-router/v2/summary')
    def _mock_router_summary(request):
        rll = _rll_to_array(request.args['rll'])
        if rll == [DRIVER_POS, POINTS[0]]:
            return mockserver.make_response(
                response=_proto_driving_summary(231.0, 1233.0),
                status=200,
                content_type='application/x-protobuf',
            )
        if rll == [DRIVER_POS, POINTS[0], POINTS[1]]:
            return mockserver.make_response(
                response=_proto_driving_summary(532.0, 2438.0),
                status=200,
                content_type='application/x-protobuf',
            )
        if rll != [DRIVER_POS, POINTS[0], POINTS[1], POINTS[2]]:
            assert False
        return mockserver.make_response(
            response=_proto_driving_summary(906.0, 5432.0),
            status=200,
            content_type='application/x-protobuf',
        )

    body = {
        'courier': 'dbid2_uuid2',
        'verification_data': {'cargo_order_id': CARGO_ORDER_ID},
    }
    response = await driver_route_responder_adv.post(
        'cargo/timeleft-by-courier', json=body,
    )

    assert response.status_code == 200
    assert response.json() == expected_request


@pytest.mark.servicetest
async def test_cargo_timeleft_by_courier_404_no_courier(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    body = {
        'courier': 'dbid3_uuid3',
        'verification_data': {'cargo_order_id': CARGO_ORDER_ID},
    }
    response = await driver_route_responder_adv.post(
        'cargo/timeleft-by-courier', json=body,
    )

    assert response.status_code == 404


@pytest.mark.servicetest
async def test_cargo_timeleft_by_courier_404_no_cargo_points(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = copy.deepcopy(TIMELEFTS)
    timelefts['contractor_id'] = 'dbid4_uuid4'
    timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['timeleft_data'][0]['service_id'] = 'processing:transporting'
    timelefts['timeleft_data'][1]['service_id'] = 'processing:transporting'
    timelefts['timeleft_data'][2]['service_id'] = 'processing:driving'

    expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
    expected_timelefts['contractor_id'] = 'dbid4_uuid4'
    expected_timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['timeleft_data'][0][
        'service_id'
    ] = 'processing:transporting'
    expected_timelefts['timeleft_data'][1][
        'service_id'
    ] = 'processing:transporting'
    expected_timelefts['timeleft_data'][2]['service_id'] = 'processing:driving'

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    body = {
        'courier': 'dbid4_uuid4',
        'verification_data': {'cargo_order_id': CARGO_ORDER_ID},
    }
    response = await driver_route_responder_adv.post(
        'cargo/timeleft-by-courier', json=body,
    )

    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_route_responder_cargo_use_ng_cache',
    consumers=['driver-route-responder/contractor'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'title': 'Условие segmentation',
            'value': {'enabled': True, 'logging': True},
        },
    ],
)
async def test_cargo_timeleft_by_courier_200_ng(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = copy.deepcopy(TIMELEFTS)
    timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
    expected_timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    @testpoint('same_cargo_points')
    def same_cargo_points_timelefts(received_msg):
        pass

    @testpoint('not_same_cargo_points')
    def not_same_cargo_points_timelefts(received_msg):
        pass

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL_NG, ser_mes,
    )
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 2

    body = {
        'courier': DRIVER_ID,
        'verification_data': {'cargo_order_id': CARGO_ORDER_ID},
    }
    response = await driver_route_responder_adv.post(
        'cargo/timeleft-by-courier', json=body,
    )
    assert same_cargo_points_timelefts.times_called == 1
    assert not_same_cargo_points_timelefts.times_called == 0
    assert response.status_code == 200
    assert response.json() == EXPECTED_REQUEST
