# pylint: disable=import-error,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils

TIMELEFTS_OUTPUT_CHANNEL = 'channel:drw:timelefts'


async def test_timelefts_listen(driver_route_responder_adv, now, testpoint):
    timelefts = {
        'timestamp': int(utils.timestamp(now) * 1000),
        'update_timestamp': int(utils.timestamp(now) * 1000),
        'tracking_type': 'RouteTracking',
        'contractor_id': 'dbid_uuid102',
        'route_id': '0',
        'adjusted_pos': [37.46611, 55.727179],
        'timeleft_data': [
            {
                'destination_position': [37.454099, 55.718486],
                'distance_left': 2438,
                'service_id': '',
                'order_id': 'order_id_1',
                'time_left': 231,
            },
        ],
        'adjusted_segment_index': 0,
    }

    expected_timelefts = {
        'timestamp': int(utils.timestamp(now) * 1000),
        'update_timestamp': int(utils.timestamp(now) * 1000),
        'tracking_type': 'RouteTracking',
        'contractor_id': 'dbid_uuid102',
        'route_id': '0',
        'adjusted_pos': [37.46611, 55.727179],
        'timeleft_data': [
            {
                'destination_position': [37.454099, 55.718486],
                'time_distance_left': {'distance': 2438, 'time': 231},
                'service_id': '',
                'order_id': 'order_id_1',
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
        TIMELEFTS_OUTPUT_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1
