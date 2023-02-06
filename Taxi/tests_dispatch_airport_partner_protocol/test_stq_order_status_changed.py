import datetime

import bson
import pytest

ORDER_ID = 'order_id1'

PERFORMER_UNIQUE_DRIVER_ID = 'udid1'
HASHED_PERFORMER_UNIQUE_DRIVER_ID = (
    '0cddbf5490863b24960f31c04f00c9ccec98a4dee416b88d82a8da414ca21855'
)
PERFORMER_UUID = 'uuid1'
NEW_PERFORMER_UUID = 'uuid2'

ASSIGNING_KEY = 'handle_assigning'
DRIVING_KEY = 'handle_driving'
TRANSPORTING_KEY = 'handle_transporting'

FINISHED_STATUS = 'finished'
CANCELLED_STATUS = 'cancelled'
ASSIGNED_STATUS = 'assigned'
DRIVING_TAXI_STATUS = 'driving'
TRANSPORTING_TAXI_STATUS = 'transporting'
COMPLETE_TAXI_STATUS = 'complete'
EXPIRED_TAXI_STATUS = 'expired'

# Format: (lon, lat)
OUT_POSITION = [14, 9]
AIRPORT_POSITION = [26, 16]

SVO_AIRPORT_POSITION = [70, 20]
SVO_OUT_POSITION = [89, 89]

CHANGED_POINT_B_POSITION = [110, 110]

NOW = '2021-06-01T11:59:00Z'
ORDER_PROC_ETA_DATETIME_STR = '2021-06-01T12:00:00Z'
ORDER_PROC_ARRIVAL_TIME_STR = '2021-06-01T12:01:00Z'
ORDER_PROC_TIMELEFT = 60

DRR_DRIVING_TIMELEFT = 180
DRR_DRIVING_ARRIVAL_TIME_STR = '2021-06-01T12:02:00Z'
DRR_TRANSPORTING_TIMELEFT = 360
DRR_TRANSPORTING_ARRIVAL_TIME_STR = '2021-06-01T12:05:00Z'

CAR_NUMBER_LATIN = 'Y884OE750'
CAR_NUMBER_CYRILLIC = 'У884ОЕ750'

CAR_INFO = {
    'number': CAR_NUMBER_CYRILLIC,
    'model': 'LegacyOne',
    'mark': 'brand1',
    'color': 'black1',
    'year': 2001,
}

SHORT_RESCHEDULE_PERIOD = 30
REGULAR_RESCHEDULE_PERTIOD = 600
TIMELEFT_THRESHOLD = 100500


def stq_kwargs(event_key, point_a, point_b):
    return {
        'event_key': event_key,
        'order': {
            'id': ORDER_ID,
            'request': {'point_a': point_a, 'point_b': point_b},
        },
        'performer': {
            'dbid': 'dbid1',
            'uuid': PERFORMER_UUID,
            'udid': PERFORMER_UNIQUE_DRIVER_ID,
            'eta': ORDER_PROC_ETA_DATETIME_STR,
            'car_id': 'car_id1',
        },
        'trip_estimated_time': ORDER_PROC_TIMELEFT,
    }


def check_reschedule_for(stq_queue, now, delay_sec):
    next_call = stq_queue.next_call()
    eta = now + datetime.timedelta(seconds=delay_sec)
    assert next_call['kwargs'] is None
    assert next_call['eta'] == eta


def check_auth_header(request):
    assert (
        request.headers['Authorization']
        == 'Basic c29tZV9sb2dpbjpzb21lX3Bhc3N3b3Jk'
    )


@pytest.fixture(autouse=True)
def fleet_vehicles_mock(mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _fleet_vehicles(request):
        body = request.json
        assert body['id_in_set'] == ['dbid1_car_id1']
        assert body['projection'] == [
            'data.number',
            'data.year',
            'data.model',
            'data.brand',
            'data.color',
        ]
        return {
            'vehicles': [
                {
                    'data': {
                        'brand': CAR_INFO['mark'],
                        'color': CAR_INFO['color'],
                        'model': CAR_INFO['model'],
                        'number': CAR_NUMBER_LATIN,
                        'year': CAR_INFO['year'],
                    },
                    'park_id_car_id': 'dbid1_car_id1',
                    'revision': '0_1574328384_71',
                },
            ],
        }


def timeleft_handler(mockserver, request, event_key):
    body = request.json
    assert body == {
        'order_id': ORDER_ID,
        'mode': 'default',
        'driver': f'dbid1_{PERFORMER_UUID}',
    }
    json = {
        'position': [0, 0],
        'destination': [0, 0],
        'time_left': (
            DRR_DRIVING_TIMELEFT
            if event_key in (DRIVING_KEY, ASSIGNING_KEY)
            else DRR_TRANSPORTING_TIMELEFT
        ),
        'distance_left': 1000,
        'tracking_type': 'route_tracking',
        'service_id': '',
        'etas': [],
    }
    return mockserver.make_response(json=json, status=200)


def get_fields_handler(
        mockserver,
        request,
        order_status,
        taxi_status,
        performer_uuid,
        point_b,
):
    args = request.args
    body = bson.BSON.decode(request.get_data())
    assert args['order_id'] == ORDER_ID
    assert body == {
        'fields': [
            'order.status',
            'order.taxi_status',
            'order.performer.uuid',
            'order.request.destinations',
        ],
    }
    if point_b is None:
        destinations = None
    elif not point_b:
        destinations = []
    else:
        destinations = [
            {'geopoint': [111, 111]},
            {'geopoint': [112, 112]},
            {'geopoint': point_b},
        ]
    response_fields = {
        'document': {
            '_id': args['order_id'],
            'order': {
                'status': order_status,
                'taxi_status': taxi_status,
                'performer': {'uuid': performer_uuid},
                'request': {'destinations': destinations},
            },
        },
        'revision': {'processing.version': 1, 'order.version': 1},
    }
    return mockserver.make_response(
        status=200,
        content_type='application/bson',
        response=bson.BSON.encode(response_fields),
    )


def info_order_out_handler(
        mockserver, request, expected_polygon_id, expected_request,
):
    check_auth_header(request)
    body = request.json
    assert body == {
        'polygon_id': (
            expected_polygon_id if expected_polygon_id is not None else 'ekb'
        ),
        'order_id': ORDER_ID,
        'driver_id': HASHED_PERFORMER_UNIQUE_DRIVER_ID,
        'arrival_reason': expected_request['arrival_reason'],
        'arrival_time': expected_request['arrival_time'],
        'car': CAR_INFO,
    }
    json = {'status_permission': True, 'status_message': 'success'}
    return mockserver.make_response(json=json, status=200)


def dismiss_order_out_handler(mockserver, request, expected_reason_code):
    check_auth_header(request)
    body = request.json
    assert body == {
        'car_number': CAR_INFO['number'],
        'order_id': ORDER_ID,
        'driver_id': HASHED_PERFORMER_UNIQUE_DRIVER_ID,
        'reason_code': expected_reason_code,
    }
    return mockserver.make_response(json={}, status=200)


@pytest.mark.now(NOW)
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ORDER_STATUS_CHANGED_RESCHEDULE={
        'short_period': {
            'max_iterations': 1,
            'reschedule_seconds': SHORT_RESCHEDULE_PERIOD,
        },
        'regular_period': {'reschedule_seconds': REGULAR_RESCHEDULE_PERTIOD},
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ANTI_CAROUSEL={
        'allowed_airports': ['ekb'],
        'enabled': True,
        'allowed_zones': [],
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_SINTEGRO_V2={'__default__': True},
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('expected_polygon_id', ['polygon_id1', None])
@pytest.mark.parametrize('timeleft_threshold', [TIMELEFT_THRESHOLD, None])
@pytest.mark.parametrize('is_driving_key', [False, True])
@pytest.mark.parametrize(
    'event_key,point_a,point_b,use_timeleft,expected_result',
    [
        # assigning event inside airport
        (
            ASSIGNING_KEY,
            AIRPORT_POSITION,
            AIRPORT_POSITION,
            True,
            {
                'arrival_reason': 'pick_up',
                'arrival_time': DRR_DRIVING_ARRIVAL_TIME_STR,
            },
        ),
        # assigning event from airport
        (
            ASSIGNING_KEY,
            AIRPORT_POSITION,
            OUT_POSITION,
            True,
            {
                'arrival_reason': 'pick_up',
                'arrival_time': DRR_DRIVING_ARRIVAL_TIME_STR,
            },
        ),
        # transporting event from airport
        (TRANSPORTING_KEY, AIRPORT_POSITION, OUT_POSITION, True, None),
        # assigning event to airport
        (ASSIGNING_KEY, OUT_POSITION, AIRPORT_POSITION, True, None),
        # transporting event to airport
        (
            TRANSPORTING_KEY,
            OUT_POSITION,
            AIRPORT_POSITION,
            True,
            {
                'arrival_reason': 'drop',
                'arrival_time': DRR_TRANSPORTING_ARRIVAL_TIME_STR,
            },
        ),
        # not airport order
        (ASSIGNING_KEY, OUT_POSITION, OUT_POSITION, True, None),
        # not allowed airport order
        (ASSIGNING_KEY, SVO_AIRPORT_POSITION, SVO_OUT_POSITION, True, None),
        # assigning event from airport, don't use timeleft
        (
            ASSIGNING_KEY,
            AIRPORT_POSITION,
            OUT_POSITION,
            False,
            {
                'arrival_reason': 'pick_up',
                'arrival_time': ORDER_PROC_ETA_DATETIME_STR,
            },
        ),
        # transporting event to airport, don't use timeleft
        (
            TRANSPORTING_KEY,
            OUT_POSITION,
            AIRPORT_POSITION,
            False,
            {
                'arrival_reason': 'drop',
                'arrival_time': ORDER_PROC_ARRIVAL_TIME_STR,
            },
        ),
    ],
)
async def test_happy_path_first_iteration(
        taxi_dispatch_airport_partner_protocol,
        now,
        stq,
        stq_runner,
        mockserver,
        taxi_config,
        event_key,
        point_a,
        point_b,
        use_timeleft,
        timeleft_threshold,
        expected_polygon_id,
        expected_result,
        is_driving_key,
):
    if is_driving_key and event_key == ASSIGNING_KEY:
        event_key = DRIVING_KEY

    @mockserver.json_handler('sintegro/aes/hs/info_order_out')
    def info_order_out(request):
        return info_order_out_handler(
            mockserver,
            request,
            expected_polygon_id,
            expected_request=expected_result,
        )

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _timeleft(request):
        return timeleft_handler(mockserver, request, event_key)

    if timeleft_threshold is not None:
        reschedule_cfg = taxi_config.get(
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_ORDER_STATUS_CHANGED_RESCHEDULE',  # noqa
        )
        reschedule_cfg['short_period'][
            'timeleft_threshold'
        ] = timeleft_threshold
        taxi_config.set_values(
            {
                'DISPATCH_AIRPORT_PARTNER_PROTOCOL_ORDER_STATUS_CHANGED_RESCHEDULE': (  # noqa
                    reschedule_cfg
                ),
            },
        )
    if expected_polygon_id is not None:
        taxi_config.set_values(
            {
                'DISPATCH_AIRPORT_PARTNER_PROTOCOL_AIRPORT_ID_TO_POLYGON_ID': {
                    'ekb': expected_polygon_id,
                },
            },
        )
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_TIMELEFT': use_timeleft},
    )

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    stq_caller = (
        stq_runner.dispatch_airport_partner_protocol_order_status_changed
    )
    stq_queue = stq.dispatch_airport_partner_protocol_order_status_changed

    await stq_caller.call(
        task_id='task_id1',
        kwargs=stq_kwargs(
            event_key=event_key, point_a=point_a, point_b=point_b,
        ),
        expect_fail=False,
    )

    if expected_result is None:
        assert info_order_out.times_called == 0
        assert stq_queue.times_called == 0
    else:
        assert info_order_out.times_called == 1
        if timeleft_threshold is None:
            assert stq_queue.times_called == 1
            check_reschedule_for(stq_queue, now, SHORT_RESCHEDULE_PERIOD)
        else:
            assert stq_queue.times_called == 0


@pytest.mark.now(NOW)
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ORDER_STATUS_CHANGED_RESCHEDULE={
        'short_period': {
            'max_iterations': 1,
            'reschedule_seconds': SHORT_RESCHEDULE_PERIOD,
        },
        'regular_period': {'reschedule_seconds': REGULAR_RESCHEDULE_PERTIOD},
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ANTI_CAROUSEL={
        'allowed_airports': ['ekb'],
        'enabled': True,
        'allowed_zones': [],
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_SINTEGRO_V2={'__default__': True},
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_TIMELEFT=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('is_driving_key', [False, True])
@pytest.mark.parametrize(
    'event_key,order_status,taxi_status,'
    'performer_uuid,point_a,point_b,new_point_b,use_timeleft,'
    'expected_dismiss_reason_code,expected_result',
    [
        # case 0: assigning event from airport
        (
            ASSIGNING_KEY,
            ASSIGNED_STATUS,
            DRIVING_TAXI_STATUS,
            PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            True,
            None,
            {
                'arrival_reason': 'pick_up',
                'arrival_time': DRR_DRIVING_ARRIVAL_TIME_STR,
            },
        ),
        # case 1: assigning event from airport, order cancelled
        (
            ASSIGNING_KEY,
            CANCELLED_STATUS,
            DRIVING_TAXI_STATUS,
            PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            True,
            'order_cancelled',
            None,
        ),
        # case 2: assigning event from airport, driver is transporting
        (
            ASSIGNING_KEY,
            ASSIGNED_STATUS,
            TRANSPORTING_TAXI_STATUS,
            PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            True,
            None,
            None,
        ),
        # case 3: assigning event from airport, performer is changed
        (
            ASSIGNING_KEY,
            ASSIGNED_STATUS,
            DRIVING_TAXI_STATUS,
            NEW_PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            True,
            'driver_changed',
            None,
        ),
        # case 4: transporting event to airport
        (
            TRANSPORTING_KEY,
            ASSIGNED_STATUS,
            TRANSPORTING_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            AIRPORT_POSITION,
            True,
            None,
            {
                'arrival_reason': 'drop',
                'arrival_time': DRR_TRANSPORTING_ARRIVAL_TIME_STR,
            },
        ),
        # case 5: transporting event to airport, order cancelled
        (
            TRANSPORTING_KEY,
            CANCELLED_STATUS,
            TRANSPORTING_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            AIRPORT_POSITION,
            True,
            'order_cancelled',
            None,
        ),
        # case 6: transporting event to airport,
        # driver status is not transporting
        (
            TRANSPORTING_KEY,
            ASSIGNED_STATUS,
            EXPIRED_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            AIRPORT_POSITION,
            True,
            None,
            None,
        ),
        # case 7: transporting event to airport, performer is changed (wtf?)
        (
            TRANSPORTING_KEY,
            ASSIGNED_STATUS,
            TRANSPORTING_TAXI_STATUS,
            NEW_PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            AIRPORT_POSITION,
            True,
            'driver_changed',
            None,
        ),
        # case 8: assigning event from airport, don't use timeleft
        (
            ASSIGNING_KEY,
            ASSIGNED_STATUS,
            DRIVING_TAXI_STATUS,
            PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            False,
            None,
            None,
        ),
        # case 9: assigning event from airport, order completed
        (
            ASSIGNING_KEY,
            FINISHED_STATUS,
            COMPLETE_TAXI_STATUS,
            PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            True,
            None,
            None,
        ),
        # case 10: assigning event from airport, other dismiss reason
        (
            ASSIGNING_KEY,
            FINISHED_STATUS,
            EXPIRED_TAXI_STATUS,
            PERFORMER_UUID,
            AIRPORT_POSITION,
            OUT_POSITION,
            OUT_POSITION,
            True,
            'other',
            None,
        ),
        # case 11: transporting event to airport, order completed,
        # but point_b is not changed
        (
            TRANSPORTING_KEY,
            FINISHED_STATUS,
            COMPLETE_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            AIRPORT_POSITION,
            True,
            None,
            None,
        ),
        # case 12: transporting event to airport, order completed
        # point_b changed to some point
        (
            TRANSPORTING_KEY,
            FINISHED_STATUS,
            COMPLETE_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            CHANGED_POINT_B_POSITION,
            True,
            'order_completed',
            None,
        ),
        # case 13: transporting event to airport, order completed
        # destinations array changed to None
        (
            TRANSPORTING_KEY,
            FINISHED_STATUS,
            COMPLETE_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            None,
            True,
            'order_completed',
            None,
        ),
        # case 14: transporting event to airport, order completed
        # destinations array changed to []
        (
            TRANSPORTING_KEY,
            FINISHED_STATUS,
            COMPLETE_TAXI_STATUS,
            PERFORMER_UUID,
            OUT_POSITION,
            AIRPORT_POSITION,
            [],
            True,
            'order_completed',
            None,
        ),
    ],
)
async def test_happy_path_second_iteration(
        taxi_dispatch_airport_partner_protocol,
        now,
        stq,
        stq_runner,
        mockserver,
        taxi_config,
        event_key,
        order_status,
        taxi_status,
        performer_uuid,
        point_a,
        point_b,
        new_point_b,
        use_timeleft,
        expected_dismiss_reason_code,
        expected_result,
        is_driving_key,
):
    if is_driving_key and event_key == ASSIGNING_KEY:
        event_key = DRIVING_KEY

    @mockserver.json_handler('sintegro/aes/hs/info_order_out')
    def info_order_out(request):
        return info_order_out_handler(
            mockserver, request, None, expected_request=expected_result,
        )

    @mockserver.json_handler('sintegro/aes/hs/dismiss_order_out')
    def dismiss_order_out(request):
        return dismiss_order_out_handler(
            mockserver, request, expected_dismiss_reason_code,
        )

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def get_fields(request):
        return get_fields_handler(
            mockserver,
            request,
            order_status=order_status,
            taxi_status=taxi_status,
            performer_uuid=performer_uuid,
            point_b=new_point_b,
        )

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _timeleft(request):
        return timeleft_handler(mockserver, request, event_key)

    taxi_config.set_values(
        {'DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_TIMELEFT': use_timeleft},
    )

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    stq_caller = (
        stq_runner.dispatch_airport_partner_protocol_order_status_changed
    )
    stq_queue = stq.dispatch_airport_partner_protocol_order_status_changed

    await stq_caller.call(
        task_id='task_id1',
        reschedule_counter=1,
        kwargs=stq_kwargs(
            event_key=event_key, point_a=point_a, point_b=point_b,
        ),
        expect_fail=False,
    )

    assert get_fields.times_called == 1

    if expected_dismiss_reason_code is None:
        assert dismiss_order_out.times_called == 0
    else:
        assert dismiss_order_out.times_called == 1

    if expected_result is None:
        assert info_order_out.times_called == 0

        # If can't retrieve arrival time on second iteration then reschedule
        if use_timeleft:
            assert stq_queue.times_called == 0
        else:
            assert stq_queue.times_called == 1
            check_reschedule_for(stq_queue, now, REGULAR_RESCHEDULE_PERTIOD)
    else:
        assert info_order_out.times_called == 1
        assert stq_queue.times_called == 1
        check_reschedule_for(stq_queue, now, REGULAR_RESCHEDULE_PERTIOD)


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ANTI_CAROUSEL={
        'allowed_airports': ['ekb'],
        'enabled': True,
        'allowed_zones': [],
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_TIMELEFT=True,
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_SINTEGRO_V2={'__default__': False},
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('reschedule_counter', [0, 1])
@pytest.mark.parametrize('event_key', [ASSIGNING_KEY, DRIVING_KEY])
async def test_sintegro_disabled(
        stq_runner, mockserver, reschedule_counter, event_key,
):
    @mockserver.json_handler('sintegro/aes/hs/info_order_out')
    def info_order_out(_):
        assert False

    @mockserver.json_handler('sintegro/aes/hs/dismiss_order_out')
    def dismiss_order_out(_):
        assert False

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def timeleft(request):
        return timeleft_handler(mockserver, request, TRANSPORTING_KEY)

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(request):
        return get_fields_handler(
            mockserver,
            request,
            order_status=CANCELLED_STATUS,
            taxi_status=DRIVING_TAXI_STATUS,
            performer_uuid=PERFORMER_UUID,
            point_b=OUT_POSITION,
        )

    stq = stq_runner.dispatch_airport_partner_protocol_order_status_changed

    await stq.call(
        task_id='task_id1',
        reschedule_counter=reschedule_counter,
        kwargs=stq_kwargs(
            event_key=event_key,
            point_a=AIRPORT_POSITION,
            point_b=OUT_POSITION,
        ),
        expect_fail=False,
    )

    if not reschedule_counter:
        assert timeleft.times_called == 1
    else:
        assert timeleft.times_called == 0
    assert info_order_out.times_called == 0
    assert dismiss_order_out.times_called == 0


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ANTI_CAROUSEL={
        'allowed_airports': ['ekb'],
        'enabled': True,
        'allowed_zones': [],
    },
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_TIMELEFT=True,
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_SINTEGRO_V2={'__default__': True},
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('error_code', [400, 401, 403, 409, 429, 500])
@pytest.mark.parametrize('event_key', [ASSIGNING_KEY, DRIVING_KEY])
async def test_sintegro_error_codes(
        stq_runner, mockserver, error_code, event_key,
):
    @mockserver.json_handler('sintegro/aes/hs/info_order_out')
    def info_order_out(request):
        json = {
            'status_permission': False,
            'status_message': 'Some error information',
        }
        if error_code == 500:
            json = {}
        return mockserver.make_response(json=json, status=error_code)

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _timeleft(request):
        return timeleft_handler(mockserver, request, TRANSPORTING_KEY)

    stq = stq_runner.dispatch_airport_partner_protocol_order_status_changed

    await stq.call(
        task_id='task_id1',
        kwargs=stq_kwargs(
            event_key=event_key,
            point_a=AIRPORT_POSITION,
            point_b=OUT_POSITION,
        ),
        expect_fail=True,
    )

    assert info_order_out.times_called == 1


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_ORDER_STATUS_CHANGED_MAX_ATTEMPTS=3,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('event_key', [ASSIGNING_KEY, DRIVING_KEY])
async def test_stq_order_status_changed_max_attempts(
        taxi_dispatch_airport_partner_protocol,
        stq_runner,
        testpoint,
        event_key,
):
    @testpoint('dispatch_airport_partner_protocol_order_status_changed')
    def testpoint_call(_):
        return {'inject_error': True}

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    stq = stq_runner.dispatch_airport_partner_protocol_order_status_changed

    kwargs = stq_kwargs(event_key, OUT_POSITION, OUT_POSITION)

    await stq.call(task_id='task_id1', kwargs=kwargs, expect_fail=True)
    await stq.call(
        task_id='task_id1', kwargs=kwargs, expect_fail=False, exec_tries=3,
    )

    assert testpoint_call.times_called == 2
