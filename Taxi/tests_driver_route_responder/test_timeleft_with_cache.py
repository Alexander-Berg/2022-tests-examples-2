# flake8: noqa
# pylint: disable=import-error,wildcard-import,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils

import route_entry_fbs as RouteEntryFbs

import pytest
import copy

TIMELEFTS_CHANNEL = 'channel:drw:timelefts'
TIMELEFTS_CHANNEL_NG = 'channel:drw:ng:timelefts'

POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
DRIVER_POS = [37.46611, 55.727179]
DRIVER_ID = 'dbid1_uuid1'
DRIVER_ID_DEBUG_CONTROL = {'dbid': 'dbid1', 'uuid': 'uuid1'}
ORDER_IDS = ['order_id_1', 'order_id_2']

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
            'service_id': 'processing:driving',
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
            'service_id': 'processing:driving',
            'order_id': ORDER_IDS[1],
        },
    ],
    'adjusted_segment_index': 0,
}

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
    DRIVER_ROUTE_RESPONDER_TIMELEFTS_PARSING_RATIO={
        'enabled': True,
        'numerator': 1,
        'divisor': 1,
    },
)
async def test_stop_parsing_timelefts_exp(
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

    @testpoint('skipped-timelefts')
    def skipped_timelefts(received_msg):
        pass

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1
    assert skipped_timelefts.times_called == 1

    request_body = {
        'driver': 'dbid1111_uuid1111',
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'mode': 'default',
        'order_id': ORDER_IDS[1],
    }

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
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
    DRIVER_ROUTE_RESPONDER_TIMELEFTS_PARSING_RATIO={
        'enabled': True,
        'numerator': 1,
        'divisor': 1,
        'lon_less': 37.3,
        'lon_more': 37.7,
        'lat_less': 55.6,
        'lat_more': 55.8,
    },
)
async def test_stop_parsing_timelefts_inside_borders(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = copy.deepcopy(TIMELEFTS)
    timelefts['contractor_id'] = 'dbid1111_uuid1111'
    timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
    expected_timelefts['contractor_id'] = 'dbid1111_uuid1111'
    expected_timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    @testpoint('skipped-timelefts')
    def skipped_timelefts(received_msg):
        pass

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1
    assert skipped_timelefts.times_called == 1


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
    DRIVER_ROUTE_RESPONDER_TIMELEFTS_PARSING_RATIO={
        'enabled': True,
        'numerator': 1,
        'divisor': 1,
        'lon_less': 37.3,
        'lon_more': 37.7,
        'lat_less': 55.6,
        'lat_more': 55.7,
    },
)
async def test_stop_parsing_timelefts_outside_borders(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = copy.deepcopy(TIMELEFTS)
    timelefts['contractor_id'] = 'dbid1111_uuid1111'
    timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
    expected_timelefts['contractor_id'] = 'dbid1111_uuid1111'
    expected_timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    @testpoint('skipped-timelefts')
    def skipped_timelefts(received_msg):
        pass

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1
    assert skipped_timelefts.times_called == 0


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_200(
        driver_route_responder_adv, mockserver, now, testpoint, statistics,
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

    drr_response = {
        'destination': POINTS[2],
        'position': DRIVER_POS,
        'distance_left': 5432,
        'time_left': 906,
        'service_id': 'processing:driving',
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
    assert response.json() == drr_response


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_200_ng(
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
        TIMELEFTS_CHANNEL_NG, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    drr_response = {
        'destination': POINTS[2],
        'position': DRIVER_POS,
        'distance_left': 5432,
        'time_left': 906,
        'service_id': 'processing:driving',
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

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': ORDER_IDS[1],
        'use_ng_cache': True,
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


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_200_unknown_destination(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = {
        'timestamp': int(utils.timestamp(now) * 1000),
        'update_timestamp': int(utils.timestamp(now) * 1000),
        'tracking_type': 'UnknownDestination',
        'contractor_id': DRIVER_ID,
        'route_id': '0',
        'adjusted_pos': DRIVER_POS,
        'timeleft_data': [
            {
                'destination_position': [0, 0],
                'service_id': 'processing:transporting',
                'order_id': ORDER_IDS[0],
            },
        ],
        'adjusted_segment_index': 0,
    }

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [timelefts]

    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    drr_response = {
        'destination': [0, 0],
        'position': DRIVER_POS,
        'distance_left': 0,
        'time_left': 0,
        'ignore_eta': True,
        'service_id': 'processing:transporting',
        'tracking_type': 'unknown_destination',
        'etas': [
            {
                'distance_left': 0,
                'point': [0, 0],
                'time_left': 0,
                'raw_distance_left': 0,
                'raw_time_left': 0,
            },
        ],
    }

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': ORDER_IDS[0],
    }

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        assert request.json == {
            'driver_id': DRIVER_ID_DEBUG_CONTROL,
            'order_id': ORDER_IDS[0],
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


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_200_for_first_order(
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

    drr_response = {
        'destination': POINTS[1],
        'position': DRIVER_POS,
        'distance_left': 2438,
        'time_left': 532,
        'service_id': 'processing:transporting',
        'tracking_type': 'route_tracking',
        'etas': [
            {
                'distance_left': 1233,
                'point': POINTS[0],
                'time_left': 231,
                'raw_distance_left': 1233,
                'raw_time_left': 231,
            },
            {
                'distance_left': 2438,
                'point': POINTS[1],
                'time_left': 532,
                'raw_distance_left': 2438,
                'raw_time_left': 532,
            },
        ],
    }

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': ORDER_IDS[0],
    }

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        assert request.json == {
            'driver_id': DRIVER_ID_DEBUG_CONTROL,
            'order_id': ORDER_IDS[0],
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


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_200_with_route(
        driver_route_responder_adv, mockserver, now, testpoint, redis_store,
):
    timelefts = copy.deepcopy(TIMELEFTS)
    timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['route_id'] = 'route_id_0'
    timelefts['adjusted_segment_index'] = 1

    expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
    expected_timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)
    expected_timelefts['route_id'] = 'route_id_0'
    expected_timelefts['adjusted_segment_index'] = 1

    message = {'timestamp': int(utils.timestamp(now)), 'payload': [timelefts]}

    @testpoint('received-timelefts')
    def recieved_timelefts(received_msg):
        assert received_msg['data'] == [expected_timelefts]

    # send message
    ser_mes = geobus.timelefts.serialize_message(message, now)
    await driver_route_responder_adv.sync_send_to_channel(
        TIMELEFTS_CHANNEL, ser_mes,
    )

    assert recieved_timelefts.times_called == 1

    # write route in redis
    redis_store.flushall()
    redis_store.hset('{route_id_0}', 'route', ROUTE_FBS)
    assert redis_store.hget('{route_id_0}', 'route') is not None

    # check timeleft
    drr_response = {
        'destination': POINTS[2],
        'position': DRIVER_POS,
        'distance_left': 5432,
        'time_left': 906,
        'service_id': 'processing:driving',
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
        'route': [DRIVER_POS, POINTS[1], [37.489579, 55.733567], POINTS[2]],
    }

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': True,
        'verbose_log': False,
        'mode': 'default',
        'order_id': ORDER_IDS[1],
    }

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

    redis_store.flushall()

    assert response.status_code == 200
    assert response.json() == drr_response


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_200_without_prev_order_id(
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
        'time_left': 906,
        'service_id': 'processing:driving',
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
        'parent_order': {'position': POINTS[0]},
    }

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'mode': 'default',
        'order_id': ORDER_IDS[1],
    }

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        resp = None
        if request.json['order_id'] == ORDER_IDS[1]:
            resp = ORDER_CORE_RESP_1
            resp['fields']['candidates'][0]['cp']['dest'] = POINTS[0]
        elif request.json['order_id'] == ORDER_IDS[0]:
            resp = ORDER_CORE_RESP_2
        assert resp is not None
        return mockserver.make_response(json=resp, status=200)

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == drr_response


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_404_suspicious_eta(
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
                'distance_left': 24380,
                'service_id': 'processing:driving',
                'order_id': ORDER_IDS[1],
                'time_left': 5320,
            },
            {
                'destination_position': POINTS[2],
                'distance_left': 54320,
                'service_id': 'processing:transporting',
                'order_id': ORDER_IDS[1],
                'time_left': 9060,
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
                'time_distance_left': {'distance': 24380, 'time': 5320},
                'service_id': 'processing:driving',
                'order_id': ORDER_IDS[1],
            },
            {
                'destination_position': POINTS[2],
                'time_distance_left': {'distance': 54320, 'time': 9060},
                'service_id': 'processing:transporting',
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
        del request
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {'taxi_status': 'driving', 'status': 'driving'},
                    'candidates': [{'time': 1, 'dist': 20}],
                    'candidate_index': 0,
                },
                'order_id': ORDER_IDS[1],
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_different_statuses(
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
        del request
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {
                        'taxi_status': 'transporting',
                        'status': 'transporting',
                    },
                    'candidates': [{'time': 906, 'dist': 5432}],
                    'candidate_index': 0,
                },
                'order_id': ORDER_IDS[1],
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_404_no_driver(
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
        'driver': 'dbid2_uuid2',
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': 'other_order_id',
    }

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        assert request.json == {
            'driver_id': {'dbid': 'dbid2', 'uuid': 'uuid2'},
            'order_id': 'other_order_id',
            'verbose_log': True,
        }
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        del request
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {'taxi_status': 'driving', 'status': 'driving'},
                    'candidates': [{'time': 906, 'dist': 5432}],
                    'candidate_index': 0,
                },
                'order_id': 'other_order_id',
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_404_no_order(
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
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': 'other_order_id',
    }

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        assert request.json == {
            'driver_id': DRIVER_ID_DEBUG_CONTROL,
            'order_id': 'other_order_id',
            'verbose_log': True,
        }
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        del request
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {'taxi_status': 'driving', 'status': 'driving'},
                    'candidates': [{'time': 906, 'dist': 5432}],
                    'candidate_index': 0,
                },
                'order_id': 'other_order_id',
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
)
async def test_timeleft_reposition(
        driver_route_responder_adv, mockserver, now, testpoint,
):
    timelefts = copy.deepcopy(TIMELEFTS)
    del timelefts['timeleft_data'][2]['order_id']
    timelefts['timeleft_data'][2]['service_id'] = 'reposition-watcher'
    timelefts['timestamp'] = int(utils.timestamp(now) * 1000)
    timelefts['update_timestamp'] = int(utils.timestamp(now) * 1000)

    expected_timelefts = copy.deepcopy(EXPECTED_TIMELEFTS)
    del expected_timelefts['timeleft_data'][2]['order_id']
    expected_timelefts['timeleft_data'][2]['service_id'] = 'reposition-watcher'
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

    request_body = {
        'driver': DRIVER_ID,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': False,
        'verbose_log': True,
        'mode': 'default',
        'order_id': 'reposition-uuid1',
    }

    @mockserver.json_handler('/driver-route-watcher/debug/control')
    def _mock_drw_log(request):
        assert request.json == {
            'driver_id': DRIVER_ID_DEBUG_CONTROL,
            'order_id': 'reposition-uuid1',
            'verbose_log': True,
        }
        return mockserver.make_response(status=200)

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == drr_response
