import datetime
import json

import pytest

import tests_dispatch_airport_view.utils as utils

DRIVERS_UPDATER = 'drivers-updater'


def ekb_pin_point(repo_available, timestamp, reason=None):
    pin = {
        'airport_id': 'ekb',
        'pin_point': [60.80503137898187, 56.7454424257098],
        'state': utils.get_pin_state(True),
        'reposition_availability_check': {
            'available': repo_available,
            'repo_check_time': timestamp,
        },
        'class_wait_times': {'econom': 3000},
    }
    if reason is not None:
        pin['not_allowed_reason'] = reason
    info = [pin]
    return json.dumps(info)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.redis_store(
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {
            'updated_ts': '1000',
            'geobus_ts': '1000',
            'pins': ekb_pin_point(True, '2022-01-17T13:00:00+00:00'),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            'updated_ts': '1000',
            'geobus_ts': '1000',
            'pins': ekb_pin_point(
                False, '2022-01-17T13:00:00+00:00', 'rfid_label_issue',
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid2'),
        {
            'updated_ts': '1000',
            'geobus_ts': '1000',
            'pins': ekb_pin_point(True, '2022-01-17T12:00:00+00:00'),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid3'),
        {
            'updated_ts': '1000',
            'geobus_ts': '1000',
            'pins': ekb_pin_point(False, '2022-01-17T12:00:00+00:00'),
        },
    ],
)
@pytest.mark.now('2022-01-17T13:00:01+00:00')
async def test_reposition_availability(
        taxi_dispatch_airport_view, redis_store, testpoint, now, mockserver,
):
    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return {
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid' + str(id),
                }
                for id in range(10)
            ],
        }

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def _da_reposition_availability(request):
        point = request.json['point']

        if point == utils.AIRPORT_KAMENSKURALSK:
            assert sorted(request.json['driver_ids']) == ['dbid_uuid6']
            return {'allowed': ['dbid_uuid6'], 'forbidden': []}

        assert point == utils.AIRPORT_EKB_POSITION
        assert sorted(request.json['driver_ids']) == [
            'dbid_uuid2',
            'dbid_uuid3',
            'dbid_uuid4',
            'dbid_uuid5',
            'dbid_uuid7',
            'dbid_uuid8',
            'dbid_uuid9',
        ]
        return {
            'allowed': ['dbid_uuid3', 'dbid_uuid5'],
            'forbidden': [
                {'driver_id': 'dbid_uuid2', 'reason': 'some_reason'},
                {'driver_id': 'dbid_uuid4', 'reason': 'WITHOUT_ACTIVE_LABEL'},
                {'driver_id': 'dbid_uuid7', 'reason': 'FORBIDDEN_BY_SCHEDULE'},
                {'driver_id': 'dbid_uuid8', 'reason': 'OUTDATED_ACTIVE_LABEL'},
                {
                    'driver_id': 'dbid_uuid9',
                    'reason': 'EXCEED_NUMBER_OF_ENTRIES',
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

    # dbid_uuid0: was available, check still valid
    # dbid_uuid1: was not available, check still not available
    # dbid_uuid2: was available, check not valid, now not available
    # dbid_uuid3: was not available, check not valid, now available
    # dbid_uuid4: no previous check, now not available
    # dbid_uuid5: no previous check, now available
    # dbid_uuid6: kamenskuralsky airport, no previous check, now available
    # dbid_uuid7: was available, check not valid, now not available
    # dbid_uuid8: was available, check not valid, now not available
    # dbid_uuid9: was available, check not valid, now not available

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid0': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid1': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.NEAR_KAMENSKURALSK_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)

    await drivers_updater_finished.wait_call()

    etalons = {
        'dbid_uuid0': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': True,
                    'repo_check_time': '2022-01-17T13:00:00+00:00',
                },
                'state': utils.get_pin_state(True),
            },
        ],
        'dbid_uuid1': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'last_allowed': {
                    'state': 0,
                    'time': '2022-01-17T13:00:01+00:00',
                },
                'reposition_availability_check': {
                    'available': False,
                    'repo_check_time': '2022-01-17T13:00:00+00:00',
                },
                'state': utils.get_pin_state(False),
                'not_allowed_reason': 'rfid_label_issue',
            },
        ],
        'dbid_uuid2': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'last_allowed': {
                    'state': 0,
                    'time': '2022-01-17T13:00:01+00:00',
                },
                'reposition_availability_check': {
                    'available': False,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(False),
            },
        ],
        'dbid_uuid3': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': True,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(True),
            },
        ],
        'dbid_uuid4': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': False,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(False),
                'not_allowed_reason': 'rfid_label_issue',
            },
        ],
        'dbid_uuid5': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': True,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(True),
            },
        ],
        'dbid_uuid6': [
            {
                'airport_id': 'kamenskuralsky',
                'class_wait_times': {'econom': 1000},
                'pin_point': utils.AIRPORT_KAMENSKURALSK,
                'reposition_availability_check': {
                    'available': True,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(False),
                'not_allowed_reason': 'full_queue_with_time',
            },
        ],
        'dbid_uuid7': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': False,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(False),
                'not_allowed_reason': 'rfid_label_issue',
            },
        ],
        'dbid_uuid8': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': False,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(False),
                'not_allowed_reason': 'rfid_label_issue',
            },
        ],
        'dbid_uuid9': [
            {
                'airport_id': 'ekb',
                'class_wait_times': {'econom': 3000},
                'pin_point': [60.80503137898187, 56.7454424257098],
                'reposition_availability_check': {
                    'available': False,
                    'repo_check_time': '2022-01-17T13:00:01+00:00',
                },
                'state': utils.get_pin_state(False),
                'not_allowed_reason': 'entry_limit_exceed',
            },
        ],
    }

    for driver_id, etalon in etalons.items():
        response_1 = redis_store.hgetall(utils.driver_info_key(driver_id))
        pins = json.loads(response_1.get(b'pins'))
        assert pins == etalon, driver_id
