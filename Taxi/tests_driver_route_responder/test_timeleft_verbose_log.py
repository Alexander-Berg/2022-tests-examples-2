# flake8: noqa
# pylint: disable=import-error,wildcard-import
from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils
import pytest

TIMELEFTS_CHANNEL = 'channel:drw:timelefts'

POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
DRIVER_POS = [37.46611, 55.727179]
DRIVER_ID = 'dbid1_verboselog'
DRIVER_ID_DEBUG_CONTROL = {'dbid': 'dbid1', 'uuid': 'verboselog'}
ORDER_IDS = ['order_id_1', 'order_id_2']
ORDER_CORE_RESP_1 = {
    'fields': {
        'performer': {'candidate_index': 0},
        'order': {'taxi_status': 'driving', 'status': 'driving'},
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
async def test_timeleft_verbose_log(
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
    def received_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    timelefts_yt_msg_count = 0
    timelefts_yt_order_id = 0

    @testpoint('log-to-yt')
    def received_yt_msg(yt_msg):
        print(yt_msg)
        nonlocal timelefts_yt_msg_count
        nonlocal timelefts_yt_order_id
        if 'meta' in yt_msg and 'timelefts_struct' in yt_msg['meta']:
            timelefts_yt_msg_count += 1
        if 'meta_order_id' in yt_msg and yt_msg['meta_order_id']:
            timelefts_yt_order_id += 1

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert received_timelefts.times_called == 1

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': ORDER_IDS[1],
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
    assert received_yt_msg.times_called >= 1
    assert timelefts_yt_msg_count > 0
    assert timelefts_yt_order_id > 0
