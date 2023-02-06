# pylint: disable=import-error
import datetime
import json

import pytest

import tests_dispatch_airport_view.utils as utils

DRIVERS_UPDATER = 'drivers-updater'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_VIEW_AIRPORT_PIN_SETTINGS={
        '__default__': {'radius_m': 10000},
        'ekb': {'radius_m': 50000},
    },
)
async def test_pins_config(
        taxi_dispatch_airport_view, redis_store, testpoint, now, mockserver,
):
    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return {
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid' + str(i),
                }
                for i in range(1, 6)
            ],
        }

    await taxi_dispatch_airport_view.enable_testpoints()

    # geobus drivers:
    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.OUT_EKB_RADIUS,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.NEAR_KAMENSKURALSK_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.BETWEEN_EKB_KAMENSKURALSK,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.WAITING_EKB_POSITION,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)
    await drivers_updater_finished.wait_call()

    for driver_id in ['dbid_uuid2', 'dbid_uuid5']:
        assert {} == redis_store.hgetall(utils.driver_info_key(driver_id))
    for driver_id in ['dbid_uuid1', 'dbid_uuid4']:
        assert (
            json.loads(
                redis_store.hgetall(utils.driver_info_key(driver_id))[b'pins'],
            )
            == [
                {
                    'airport_id': 'ekb',
                    'pin_point': [60.80503137898187, 56.7454424257098],
                    'state': 0,
                    'class_wait_times': {'econom': 3000},
                },
            ]
        )
    assert (
        json.loads(
            redis_store.hgetall(utils.driver_info_key('dbid_uuid3'))[b'pins'],
        )
        == [
            {
                'airport_id': 'kamenskuralsky',
                'pin_point': [61.92396961914058, 56.39818246923726],
                'state': 2,
                'class_wait_times': {'econom': 1000},
                'not_allowed_reason': 'full_queue_with_time',
            },
        ]
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_VIEW_AIRPORT_PIN_SETTINGS={
        '__default__': {'radius_m': 10000},
        'ekb': {'radius_m': 50000, 'enabled_in_airport': True},
    },
)
async def test_pins_config_enabled_in_airport(
        taxi_dispatch_airport_view, redis_store, testpoint, now, mockserver,
):
    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

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

    await taxi_dispatch_airport_view.enable_testpoints()

    # geobus drivers:
    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.WAITING_EKB_POSITION,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)
    await drivers_updater_finished.wait_call()

    pin_info = redis_store.hgetall(utils.driver_info_key('dbid_uuid1'))[
        b'pins'
    ]
    assert json.loads(pin_info) == [
        {
            'airport_id': 'ekb',
            'pin_point': [60.80503137898187, 56.7454424257098],
            'state': 0,
            'class_wait_times': {'econom': 3000},
        },
    ]


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_VIEW_AIRPORT_PIN_SETTINGS={
        '__default__': {'radius_m': 10000},
        'ekb': {
            'radius_m': 50000,
            'enabled_in_airport': True,
            'min_radius_m': 1000,
        },
    },
)
async def test_pins_config_min_radius(
        taxi_dispatch_airport_view, redis_store, testpoint, now, mockserver,
):
    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

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

    await taxi_dispatch_airport_view.enable_testpoints()

    # geobus drivers:
    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.WAITING_EKB_POSITION,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)
    await drivers_updater_finished.wait_call()

    assert {} == redis_store.hgetall(utils.driver_info_key('dbid_uuid1'))
