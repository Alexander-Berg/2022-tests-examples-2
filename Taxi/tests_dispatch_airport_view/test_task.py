# pylint: disable=import-error
import datetime
import json

import pytest

import tests_dispatch_airport_view.utils as utils

DRIVERS_UPDATER = 'drivers-updater'

MAIN_AREA_NAME = 'main_area'
WAITING_AREA_NAME = 'waiting_area'
NOTIFICATION_AREA_NAME = 'notification_area'


def ekb_pin_point(allowed, classes_info=None, last_allowed=None):
    info = [
        {
            'airport_id': 'ekb',
            'pin_point': [60.80503137898187, 56.7454424257098],
            'state': utils.get_pin_state(allowed),
        },
    ]
    if classes_info:
        info[0]['class_wait_times'] = classes_info
    if last_allowed is not None:
        info[0]['last_allowed'] = last_allowed

    return json.dumps(info)


def get_etalon(etalon, candidates_failed, reposition_failed):
    if candidates_failed:
        for driver_id in (
                'dbid_uuid6',
                'dbid_uuid7',
                'dbid_uuid8',
                'dbid_uuid9',
        ):
            etalon.pop(driver_id, None)

        # reset old state
        etalon['dbid_uuid2'][0]['state'] = utils.get_pin_state(False)
        etalon['dbid_uuid3'][0]['state'] = utils.get_pin_state(True)
        etalon['dbid_uuid3'][0].pop('last_allowed')

        del etalon['dbid_uuid3'][0]['not_allowed_reason']

    if reposition_failed:
        etalon.pop('dbid_uuid6', None)
        etalon.pop('dbid_uuid7', None)
        etalon.pop('dbid_uuid9', None)

    return etalon


DRIVER_META = {
    'dbid_uuid0': {
        'updated_ts': '1000',
        'geobus_ts': '1000',
        'is_hidden': 'false',
    },
    'dbid_uuid1': {
        'updated_ts': '1001',
        'geobus_ts': '1001',
        'is_hidden': 'true',
    },
    'dbid_uuid2': {'updated_ts': '1002', 'geobus_ts': '1002'},
    'dbid_uuid3': {'updated_ts': '1003', 'geobus_ts': '1003'},
    'dbid_uuid4': {'updated_ts': '1004', 'geobus_ts': '1004'},
}


def sorted_redis_driver_ids(redis_store):
    cursor = 0
    pattern = 'dbid_uuid:*'
    ret = []
    while True:
        cursor, keys = redis_store.scan(cursor=cursor, match=pattern)
        ret += keys
        if cursor == 0:
            break
    return sorted([driver_id.decode('ascii') for driver_id in ret])


def assert_etalon_keys_equal_redis(etalon_keys, redis_store):
    assert etalon_keys == sorted_redis_driver_ids(redis_store)


def assert_etag_not_changed(etag, geobus_now):
    assert (
        abs(
            etag
            - geobus_now.replace(tzinfo=datetime.timezone.utc).timestamp(),
        )
        < 1
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {
            **DRIVER_META['dbid_uuid0'],
            'pins': ekb_pin_point(True, {'econom': 3000}),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            **DRIVER_META['dbid_uuid1'],
            'pins': ekb_pin_point(True, {'econom': 3000, 'comfortplus': 1000}),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid2'),
        {
            **DRIVER_META['dbid_uuid2'],
            'pins': ekb_pin_point(
                False,
                {'business': None},
                {
                    'state': int(utils.PinState.kAllowedOldMode),
                    'time': '2022-01-17T12:50:00+00:00',
                },
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid3'),
        {**DRIVER_META['dbid_uuid3'], 'pins': ekb_pin_point(True)},
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid4'),
        {**DRIVER_META['dbid_uuid4'], 'pins': ekb_pin_point(False)},
    ],
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid8',
            'order_id': 'order_id_8',
            'taxi_status': 3,
            'final_destination': {
                'lat': 56.39818246923726,
                'lon': 61.92396961914058,
            },
        },
        {
            'driver_id': 'dbid_uuid9',
            'order_id': 'order_id_9',
            'taxi_status': 3,
            'final_destination': {'lat': 10.0, 'lon': 10.0},
        },
    ],
)
@pytest.mark.parametrize(
    'candidates_failed,reposition_failed',
    [(False, False), (True, False), (False, True), (True, True)],
)
@pytest.mark.now('2022-01-17T13:00:00+00:00')
async def test_task(
        taxi_dispatch_airport_view,
        redis_store,
        testpoint,
        now,
        load_json,
        candidates_failed,
        reposition_failed,
        mockserver,
):
    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    await taxi_dispatch_airport_view.enable_testpoints()

    if candidates_failed:

        @mockserver.json_handler('/candidates/profiles')
        def _candidates(request):
            raise mockserver.TimeoutError()

    if reposition_failed:

        @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
        def _reposition_api(request):
            raise mockserver.TimeoutError()

    # geobus drivers:

    # existed drivers:
    # dbid_uuid0 - near ekb zone, allowed -> allowed
    # dbid_uuid1 - near ekb zone, allowed -> allowed
    # dbid_uuid2 - near ekb zone, not_allowed -> allowed,
    # last_allowed is preserved
    # dbid_uuid3 - near ekb zone, allowed -> not_allowed,
    # last_allowed is updated
    # dbid_uuid4 - near ekb zone, not_allowed -> not_allowed
    # dbid_uuid5 - out of all ports radius

    # new drivers:
    # dbid_uuid6 - new kamenskuralsky airport zone
    # dbid_uuid7 - new reposition driver (ekb + kamenskuralsky repo)
    # dbid_uuid8 - new driver (ekb + busy kamenskuralsky airport order)
    # dbid_uuid9 - new busy driver (not kamenskuralsky airport order)
    # dbid_uuid10 - ekb notification zone
    # dbid_uuid11 - ekb waiting zone
    # dbid_uuid12 - ekb main zone

    # scores
    # dbid_uuid5: min score

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid0': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid1': {
            'position': utils.NEAR_EKB_AIRPORT_2,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.NEAR_EKB_AIRPORT_2,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.OUT_EKB_RADIUS,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.NEAR_KAMENSKURALSK_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': utils.BETWEEN_EKB_KAMENSKURALSK,
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': utils.BETWEEN_EKB_KAMENSKURALSK,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.NEAR_KAMENSKURALSK_AIRPORT_2,
            'timestamp': geobus_now,
        },
        'dbid_uuid10': {
            'position': utils.NOTIFICATION_EKB_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid11': {
            'position': utils.WAITING_EKB_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid12': {
            'position': utils.AIRPORT_EKB_POSITION,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)

    await drivers_updater_finished.wait_call()
    etalon_driver_ids = set(
        {
            'dbid_uuid0',
            'dbid_uuid1',
            'dbid_uuid2',
            'dbid_uuid3',
            'dbid_uuid4',
            'dbid_uuid6',
            'dbid_uuid7',
            'dbid_uuid8',
            'dbid_uuid9',
        },
    )
    if candidates_failed:
        etalon_driver_ids.discard('dbid_uuid6')
        etalon_driver_ids.discard('dbid_uuid7')
        etalon_driver_ids.discard('dbid_uuid8')
        etalon_driver_ids.discard('dbid_uuid9')

    if reposition_failed:
        etalon_driver_ids.discard('dbid_uuid6')
        etalon_driver_ids.discard('dbid_uuid7')
        etalon_driver_ids.discard('dbid_uuid9')

    etalon_keys = sorted(
        [utils.driver_info_key(driver_id) for driver_id in etalon_driver_ids],
    )
    assert_etalon_keys_equal_redis(etalon_keys, redis_store)

    pins_answer = {}
    for driver_id in etalon_driver_ids:
        response = redis_store.hgetall(utils.driver_info_key(driver_id))
        etag = response.pop(b'updated_ts').decode('ascii')

        driver_meta = DRIVER_META.get(driver_id, None)
        if driver_meta:
            etalon_etag = driver_meta['updated_ts']
            if candidates_failed:
                assert etag == etalon_etag
            elif driver_id in ('dbid_uuid0', 'dbid_uuid1', 'dbid_uuid4'):
                assert etag == etalon_etag
            else:
                assert etag > etalon_etag

        pins_answer[driver_id] = json.loads(response.pop(b'pins'))
        pins_answer[driver_id].sort(key=lambda pin: pin['airport_id'])

    assert pins_answer == get_etalon(
        load_json('etalon.json'), candidates_failed, reposition_failed,
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('pin_info_enabled', [False, True, None])
@pytest.mark.now('2022-01-17T13:00:00+00:00')
async def test_task_different_pin_info_enabled(
        taxi_dispatch_airport_view,
        redis_store,
        testpoint,
        now,
        mockserver,
        load_json,
        taxi_config,
        pin_info_enabled,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    config['ekb']['pin_info_enabled'] = pin_info_enabled
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        assert sorted(request.json['driver_ids']) == ['dbid_uuid0']
        return load_json('ekb_candidates.json')

    await taxi_dispatch_airport_view.enable_testpoints()
    await taxi_dispatch_airport_view.invalidate_caches()

    # geobus drivers:
    # dbid_uuid0 - near ekb zone

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    driver_id = 'dbid_uuid0'
    geobus_drivers = {
        driver_id: {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)

    await drivers_updater_finished.wait_call()

    etalon_keys = []
    if pin_info_enabled is not False:
        etalon_keys = [utils.driver_info_key(driver_id)]
    assert_etalon_keys_equal_redis(etalon_keys, redis_store)

    if pin_info_enabled is not False:
        response = redis_store.hgetall(utils.driver_info_key(driver_id))
        etag = int(response.pop(b'updated_ts').decode('ascii'))
        assert_etag_not_changed(etag, now)

        pins_answer = json.loads(response.pop(b'pins'))
        assert pins_answer == [
            {
                'airport_id': 'ekb',
                'state': utils.get_pin_state(True),
                'pin_point': [60.80503137898187, 56.7454424257098],
                'class_wait_times': {'econom': 3000},
            },
        ]


# check follow driver categories:
# dbid_uuid0 - new busy driver (airport order in notification area)
# dbid_uuid7 - new busy driver (airport order in main area)
# dbid_uuid8 - new busy driver (airport order in waiting area)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid0',
            'order_id': 'order_id_0',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.NOTIFICATION_EKB_POSITION[1],
                'lon': utils.NOTIFICATION_EKB_POSITION[0],
            },
        },
        {
            'driver_id': 'dbid_uuid7',
            'order_id': 'order_id_7',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.AIRPORT_EKB_POSITION[1],
                'lon': utils.AIRPORT_EKB_POSITION[0],
            },
        },
        {
            'driver_id': 'dbid_uuid8',
            'order_id': 'order_id_8',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.WAITING_BUT_NOT_AIRPORT_EKB_POSITION[1],
                'lon': utils.WAITING_BUT_NOT_AIRPORT_EKB_POSITION[0],
            },
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'driver_for_check,allowed_airport_zones,expected_pin_is_allowed',
    [
        ('dbid_uuid0', None, True),
        ('dbid_uuid0', [], False),
        (
            'dbid_uuid0',
            [MAIN_AREA_NAME, WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            True,
        ),
        ('dbid_uuid0', [MAIN_AREA_NAME, NOTIFICATION_AREA_NAME], True),
        ('dbid_uuid0', [NOTIFICATION_AREA_NAME], True),
        ('dbid_uuid0', [MAIN_AREA_NAME, WAITING_AREA_NAME], False),
        ('dbid_uuid0', [MAIN_AREA_NAME], False),
        ('dbid_uuid7', None, True),
        ('dbid_uuid7', [], False),
        (
            'dbid_uuid7',
            [MAIN_AREA_NAME, WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            True,
        ),
        ('dbid_uuid7', [MAIN_AREA_NAME, WAITING_AREA_NAME], True),
        ('dbid_uuid7', [MAIN_AREA_NAME], True),
        ('dbid_uuid7', [WAITING_AREA_NAME, NOTIFICATION_AREA_NAME], False),
        ('dbid_uuid8', None, True),
        ('dbid_uuid8', [], False),
        (
            'dbid_uuid8',
            [MAIN_AREA_NAME, WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            True,
        ),
        ('dbid_uuid8', [MAIN_AREA_NAME, WAITING_AREA_NAME], True),
        ('dbid_uuid8', [WAITING_AREA_NAME], True),
        (
            'dbid_uuid8',
            [NOTIFICATION_AREA_NAME],
            # True because of waiting area is part of the
            # notification area
            True,
        ),
        ('dbid_uuid8', [MAIN_AREA_NAME], False),
    ],
)
@pytest.mark.now('2022-01-17T13:00:00+00:00')
async def test_task_allowed_airport_zones(
        taxi_dispatch_airport_view,
        redis_store,
        testpoint,
        now,
        mockserver,
        load_json,
        taxi_config,
        driver_for_check,
        allowed_airport_zones,
        expected_pin_is_allowed,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    ekb_config = zones_config['ekb']
    ekb_config['old_mode_enabled'] = False
    if allowed_airport_zones is not None:
        ekb_config['input_order_allowed_areas'] = allowed_airport_zones
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        assert request.json['driver_ids'] == [driver_for_check]
        return load_json('ekb_candidates.json')

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_api(request):
        return mockserver.make_response(
            response=utils.generate_reposition_drivers([]),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    await taxi_dispatch_airport_view.enable_testpoints()
    await taxi_dispatch_airport_view.invalidate_caches()

    # avoid couple seconds diff test flaps when compare redis and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    driver_id = driver_for_check
    geobus_drivers = {
        driver_id: {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)

    await drivers_updater_finished.wait_call()

    etalon_keys = [utils.driver_info_key(driver_id)]
    assert_etalon_keys_equal_redis(etalon_keys, redis_store)
    response = redis_store.hgetall(utils.driver_info_key(driver_id))
    etag = int(response.pop(b'updated_ts').decode('ascii'))
    assert_etag_not_changed(etag, now)

    etalon = [
        {
            'airport_id': 'ekb',
            'state': utils.get_pin_state(expected_pin_is_allowed),
            'pin_point': [60.80503137898187, 56.7454424257098],
            'class_wait_times': {'econom': 3000},
        },
    ]
    for pin in etalon:
        if pin['state'] == utils.PinState.kNotAllowed:
            pin['not_allowed_reason'] = 'full_queue_with_time'

    pins_answer = json.loads(response.pop(b'pins'))
    assert pins_answer == etalon


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid0',
            'order_id': 'order_id_0',
            'taxi_status': 3,
            'final_destination': {
                'lat': 56.39818246923726,
                'lon': 61.92396961914058,
            },
        },
    ],
)
@pytest.mark.parametrize('is_equal_group_id', [False, True])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2022-01-17T13:00:00+00:00')
async def test_task_with_group_id_zones(
        taxi_dispatch_airport_view,
        redis_store,
        testpoint,
        now,
        mockserver,
        taxi_config,
        is_equal_group_id,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    if is_equal_group_id:
        for airport_id in ('ekb', 'kamenskuralsky'):
            config[airport_id].update(
                {'old_mode_enabled': False, 'group_id': 'test_group_id'},
            )
    else:
        config['ekb'].update(
            {'old_mode_enabled': False, 'group_id': 'test_group_id_1'},
        )
        config['kamenskuralsky'].update(
            {'old_mode_enabled': False, 'group_id': 'test_group_id_2'},
        )
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert sorted(request.json['driver_ids']) == ['dbid_uuid0']
        return {
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid0',
                },
            ],
        }

    await taxi_dispatch_airport_view.enable_testpoints()
    await taxi_dispatch_airport_view.invalidate_caches()

    # geobus drivers:
    # dbid_uuid0 - busy driver between ekb and kamenskuralsk
    # (order to kamenskuralsk, equal group id)

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    driver_id = 'dbid_uuid0'
    geobus_drivers = {
        driver_id: {
            'position': utils.BETWEEN_EKB_KAMENSKURALSK,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)
    await drivers_updater_finished.wait_call()

    etalon_keys = [utils.driver_info_key(driver_id)]
    assert_etalon_keys_equal_redis(etalon_keys, redis_store)

    response = redis_store.hgetall(utils.driver_info_key(driver_id))
    etag = int(response.pop(b'updated_ts').decode('ascii'))
    assert_etag_not_changed(etag, now)

    etalon = [
        {
            'airport_id': 'ekb',
            'state': utils.get_pin_state(is_equal_group_id),
            'pin_point': [60.80503137898187, 56.7454424257098],
            'class_wait_times': {'econom': 3000},
        },
        {
            'airport_id': 'kamenskuralsky',
            'state': utils.get_pin_state(True),
            'pin_point': [61.92396961914058, 56.39818246923726],
            'class_wait_times': {'econom': 1000},
        },
    ]
    for pin in etalon:
        if pin['state'] == utils.PinState.kNotAllowed:
            pin['not_allowed_reason'] = 'wrong_input_order'

    pins_answer = json.loads(response.pop(b'pins'))
    pins_answer.sort(key=lambda x: x['airport_id'])
    assert pins_answer == etalon


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'demand, drivers_en_route, reposition_api_timeout',
    [
        (None, 0, False),
        (0, 1, False),
        (1, 0, False),
        (1, 0, True),
        (1, 1, True),
        (1, None, False),
    ],
)
async def test_pins_info_demand(
        taxi_dispatch_airport_view,
        mockserver,
        now,
        testpoint,
        redis_store,
        demand,
        drivers_en_route,
        reposition_api_timeout,
):
    if demand is not None:

        @mockserver.json_handler('/dispatch-airport/v1/pins_info')
        def _pins_info(_):
            return {
                'kamenskuralsky': [
                    {
                        'allowed_class': 'econom',
                        'expected_wait_time': 1000,
                        'demand': demand,
                    },
                ],
            }

    @mockserver.json_handler(
        '/reposition-api/v1/service/airport_queue/get_drivers_en_route',
    )
    def _reposition_api_drivers_en_route(request):
        if reposition_api_timeout:
            raise mockserver.TimeoutError()
        assert (
            request.args['airport_queue_id'] == 'kamenskuralsky'
            or demand is None
        )
        if drivers_en_route is None:
            raise mockserver.TimeoutError()
        return {'econom': drivers_en_route}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return {
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid1',
                },
            ],
        }

    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    await taxi_dispatch_airport_view.enable_testpoints()
    await taxi_dispatch_airport_view.invalidate_caches()

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NEAR_KAMENSKURALSK_AIRPORT_1,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)
    await drivers_updater_finished.wait_call()

    driver_id = 'dbid_uuid1'

    response = redis_store.hgetall(utils.driver_info_key(driver_id))
    pins_answer = json.loads(response.pop(b'pins'))
    available_drivers = (
        0
        if reposition_api_timeout or drivers_en_route is None
        else drivers_en_route
    )
    pin_available = demand is not None and demand > available_drivers
    etalon = [
        {
            'airport_id': 'kamenskuralsky',
            'class_wait_times': {'econom': 1000},
            'pin_point': [61.92396961914058, 56.39818246923726],
            'state': utils.get_pin_state(pin_available),
        },
    ]
    for pin in etalon:
        if pin['state'] == utils.PinState.kNotAllowed:
            pin['not_allowed_reason'] = 'full_queue_with_time'
    assert pins_answer == etalon
