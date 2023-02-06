# flake8: noqa
# pylint: disable=import-error,wildcard-import,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils

import pytest
import copy


TIMELEFTS_CHANNEL = 'channel:drw:timelefts'

POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
DRIVER_POS = [37.46611, 55.727179]
DRIVER_ID = 'dbid1_uuid1'
ORDER_IDS = ['order_id_1', 'reposition-uuid1']

TIMELEFTS = {
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
            'service_id': 'reposition-watcher',
            'order_id': ORDER_IDS[1],
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
            'service_id': 'reposition-watcher',
            'order_id': ORDER_IDS[1],
        },
    ],
    'adjusted_segment_index': 0,
}


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_for_reposition_200(
        driver_route_responder_adv, now, testpoint,
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

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    request_body = {'driver': DRIVER_ID, 'order_id': ORDER_IDS[1]}

    drr_response = {
        'destination': POINTS[2],
        'position': DRIVER_POS,
        'distance_left': 5432,
        'time_left': 906,
        'service_id': 'reposition-watcher',
        'tracking_type': 'route_tracking',
        'etas': [
            {
                'distance_left': 5432,
                'point': POINTS[2],
                'time_left': 906,
                'raw_distance_left': 5432,
                'raw_time_left': 906,
            },
        ],
        'parent_order': {'position': POINTS[1]},
    }

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == drr_response


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=False,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_for_reposition_425(
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

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    request_body = {
        'driver': DRIVER_ID,
        'order_id': 'reposition-uuid1',
        'filters': [
            {
                'filter': 'CompareFirstServiceId',
                'service_id': 'reposition-watcher',
            },
        ],
    }

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 425
