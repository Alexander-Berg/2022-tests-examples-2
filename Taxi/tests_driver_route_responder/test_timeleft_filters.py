# flake8: noqa
# pylint: disable=import-error,wildcard-import
from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils

import route_entry_fbs as RouteEntryFbs

import pytest

TIMELEFTS_CHANNEL = 'channel:drw:timelefts'

POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
DRIVER_POS = [37.46611, 55.727179]
DRIVER_ID = 'dbid1_uuid1'
DRIVER_ID_DEBUG_CONTROL = {'dbid': 'dbid1', 'uuid': 'uuid1'}
ORDER_IDS = ['order_id_1', 'order_id_2']

ROUTE_FBS = RouteEntryFbs.serialize_route_entry(
    {
        'route': {
            'route': [
                {'position': POINTS[0], 'time': 331, 'distance': 2233},
                {
                    'position': [37.459634, 55.725879],
                    'time': 452,
                    'distance': 2785,
                },
                {'position': POINTS[1], 'time': 632, 'distance': 3438},
                {
                    'position': [37.489579, 55.733567],
                    'time': 893,
                    'distance': 4867,
                },
                {'position': POINTS[2], 'time': 1006, 'distance': 6432},
            ],
            'distance': 6432,
            'time': 1006,
            'closures': False,
            'dead_jams': False,
            'toll_roads': False,
            'legs': [
                {'segment_index': 0, 'segment_position': 0},
                {'segment_index': 2, 'segment_position': 0},
            ],
        },
        'timestamp': 1234567890,
    },
)

ORDER_CORE_RESP_1 = {
    'fields': {
        'performer': {'candidate_index': 0},
        'order': {'taxi_status': 'driving', 'status': 'assigned'},
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
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_filter(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = {
        'timestamp': int(utils.timestamp(now) * 1000),
        'update_timestamp': int(utils.timestamp(now) * 1000),
        'tracking_type': 'RouteTracking',
        'contractor_id': DRIVER_ID,
        'route_id': '0',
        'adjusted_pos': DRIVER_POS,
        'timeleft_data': [
            {
                'destination_position': POINTS[0],
                'distance_left': 1233,
                'service_id': 'processing:transporting',
                'order_id': ORDER_IDS[0],
                'time_left': 231,
            },
            {
                'destination_position': POINTS[1],
                'distance_left': 2438,
                'service_id': 'processing:transporting',
                'order_id': ORDER_IDS[0],
                'time_left': 532,
            },
            {
                'destination_position': POINTS[2],
                'distance_left': 5432,
                'service_id': 'processing:driving',
                'order_id': ORDER_IDS[1],
                'time_left': 906,
            },
        ],
        'adjusted_segment_index': 0,
    }

    expected_timelefts = {
        'timestamp': int(utils.timestamp(now) * 1000),
        'update_timestamp': int(utils.timestamp(now) * 1000),
        'tracking_type': 'RouteTracking',
        'contractor_id': DRIVER_ID,
        'route_id': '0',
        'adjusted_pos': DRIVER_POS,
        'timeleft_data': [
            {
                'destination_position': POINTS[0],
                'time_distance_left': {'distance': 1233, 'time': 231},
                'service_id': 'processing:transporting',
                'order_id': ORDER_IDS[0],
            },
            {
                'destination_position': POINTS[1],
                'time_distance_left': {'distance': 2438, 'time': 532},
                'service_id': 'processing:transporting',
                'order_id': ORDER_IDS[0],
            },
            {
                'destination_position': POINTS[2],
                'time_distance_left': {'distance': 5432, 'time': 906},
                'service_id': 'processing:driving',
                'order_id': ORDER_IDS[1],
            },
        ],
        'adjusted_segment_index': 0,
    }

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    drr_response = {
        'destination': POINTS[2],
        'position': DRIVER_POS,
        'distance_left': 5432,
        'time_left': 1000,  # because min_eta filter
        'service_id': 'processing:driving',
        'tracking_type': 'route_tracking',
        'etas': [
            {
                'distance_left': 5432,
                'point': POINTS[2],
                'time_left': 1000,  # because min_eta filter
                'raw_distance_left': 5432,
                'raw_time_left': 906,
            },
        ],
        'parent_order': {'position': POINTS[1]},
    }

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': ORDER_IDS[1],
        'filters': [{'filter': 'MinEta', 'min_eta': 1000}],
    }

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        assert request.json == {
            'driver_id': DRIVER_ID_DEBUG_CONTROL,
            'order_id': ORDER_IDS[1],
            'verbose_log': True,
        }
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        resp = None
        if request.json['order_id'] == ORDER_IDS[1]:
            resp = ORDER_CORE_RESP_1
        elif request.json['order_id'] == ORDER_IDS[0]:
            resp = ORDER_CORE_RESP_2
        assert resp is not None
        return mockserver.make_response(json=resp, status=200)

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == drr_response
