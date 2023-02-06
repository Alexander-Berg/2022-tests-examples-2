# pylint: disable=import-error
import datetime

import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport.utils as utils

REPOSITION_FILTER_NAME = 'reposition-filter'
NON_AIRPORT_MODE = 'NonAirportMode'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize('timeout', [False, True])
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid10',
            'order_id': 'order_id_10',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
    ],
)
async def test_reposition_filter(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        timeout,
        mode,
):
    # without 16 which is filtered
    number_of_drivers = 13
    old_mode_enabled = utils.get_old_mode_enabled(mode)

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(REPOSITION_FILTER_NAME + '-finished')
    def reposition_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == number_of_drivers
        assert request.json['zone_id'] == 'ekb_home_zone'
        return utils.generate_candidates_response(
            request.json['driver_ids'], ['comfortplus', 'econom'],
        )

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == number_of_drivers
        return utils.generate_categories_response(
            [driver['driver_id'] for driver in request.json['drivers']],
            ['comfortplus', 'econom'],
        )

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() is None
        request_drivers = []
        for i in range(request.DriversLength()):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            request_drivers.append(f'{dbid}_{uuid}')
        assert sorted(request_drivers) == [
            'dbid_uuid1',
            'dbid_uuid10',
            'dbid_uuid11',
            'dbid_uuid12',
            'dbid_uuid13',
            'dbid_uuid14',
            'dbid_uuid15',
            'dbid_uuid2',
            'dbid_uuid3',
            'dbid_uuid6',
            'dbid_uuid7',
            'dbid_uuid8',
            'dbid_uuid9',
        ]

        if timeout:
            raise mockserver.TimeoutError()
        drivers = [
            {'dbid': 'dbid', 'uuid': 'uuid2', 'airport_id': 'ekb'},
            {'dbid': 'dbid', 'uuid': 'uuid7', 'airport_id': 'svo'},
            {'dbid': 'dbid', 'uuid': 'uuid8', 'airport_id': 'svo'},
            {'dbid': 'dbid', 'uuid': 'uuid9', 'airport_id': ''},
            {'dbid': 'dbid', 'uuid': 'uuid10', 'airport_id': 'svo'},
            {'dbid': 'dbid', 'uuid': 'uuid13', 'airport_id': 'ekb'},
            {
                'dbid': 'dbid',
                'uuid': 'uuid14',
                'airport_id': 'ekb',
                'is_dispatch_airport_pin': True,
            },
            {'dbid': 'dummy_dbid', 'uuid': 'dummy_uuid', 'airport_id': 'ekb'},
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]
        if mode != 'new' or timeout:
            utils.check_airport_tags(
                append,
                expected_queued=(
                    'dbid_uuid3',
                    'dbid_uuid6',
                    'dbid_uuid12',
                    'dbid_uuid15',
                ),
                expected_entered=(
                    'dbid_uuid1',
                    'dbid_uuid2',
                    'dbid_uuid7',
                    'dbid_uuid8',
                    'dbid_uuid9',
                    'dbid_uuid10',
                    'dbid_uuid11',
                    'dbid_uuid13',
                    'dbid_uuid14',
                ),
            )
            utils.check_airport_tags(
                remove, (), ('dbid_uuid3', 'dbid_uuid12', 'dbid_uuid15'),
            )
        else:
            utils.check_airport_tags(
                append,
                expected_queued=(
                    'dbid_uuid3',
                    'dbid_uuid6',
                    'dbid_uuid12',
                    'dbid_uuid15',
                ),
                expected_entered=(
                    'dbid_uuid2',
                    'dbid_uuid7',
                    'dbid_uuid10',
                    'dbid_uuid11',
                    'dbid_uuid13',
                    'dbid_uuid14',
                ),
            )
            utils.check_airport_tags(
                remove, (), ('dbid_uuid3', 'dbid_uuid12', 'dbid_uuid15'),
            )

        return {}

    taxi_config.set_values(utils.custom_config(old_mode_enabled))
    utils.set_mode_in_config(taxi_config, mode)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: notification zone (without reposition)
    # dbid_uuid2 - new driver: notification zone (with reposition)
    # dbid_uuid3 - stored driver: on reposition waiting zone
    # dbid_uuid6 - stored queued driver
    # dbid_uuid7 - stored entered driver in main zone (with reposition)
    # dbid_uuid8 - new driver: notification zone (reposition to other airport)
    # dbid_uuid9 - new driver: notification zone (non airport reposition)
    # dbid_uuid10 - new driver: airport order (another airport reposition)
    # dbid_uuid11 - stored driver: old_mode, without reposition
    # dbid_uuid12 - stored driver: with reposition (waiting)
    # dbid_uuid13 - stored driver: old_mode, without reposition (notification)
    # dbid_uuid14 - new driver, notification zone dispatch_airport_pin
    # flag in metadata
    # dbid_uuid15 - entered reposition_old_mode driver -> queued
    # dbid_uuid16 - just filtered

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid10': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid14': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid15': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # reposition-filter check
    response = (await reposition_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid2',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid3',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': 'old_mode',
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kEntered,
            'reason': 'on_reposition',
            'airport': 'ekb',
            'areas': [0],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid7',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': (
                utils.State.kEntered
                if mode != 'new'
                else utils.State.kFiltered
            ),
            'reason': (
                '' if mode != 'new' else utils.Reason.kNonAirportReposition
            ),
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'state': (
                utils.State.kEntered
                if mode != 'new'
                else utils.State.kFiltered
            ),
            'reason': (
                '' if mode != 'new' else utils.Reason.kNonAirportReposition
            ),
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'input_order_id': 'order_id_10',
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [0, 1],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid12',
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid13',
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnRepositionOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid14',
        },
        'dbid_uuid15': {
            'driver_id': 'dbid_uuid15',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnRepositionOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'rsid_15',
            'old_mode_enabled': old_mode_enabled,
        },
    }

    if timeout:
        if mode != 'old':
            driver = updated_etalons['dbid_uuid1']
            driver['reason'] = ''

            driver = updated_etalons['dbid_uuid2']
            driver['reason'] = ''
            del driver['reposition_session_id']

            driver = updated_etalons['dbid_uuid8']
            driver['state'] = utils.State.kEntered
            driver['reason'] = ''

            driver = updated_etalons['dbid_uuid9']
            driver['state'] = utils.State.kEntered
            driver['reason'] = ''

            driver = updated_etalons['dbid_uuid13']
            driver['reason'] = utils.Reason.kOldMode
            del driver['reposition_session_id']

            driver = updated_etalons['dbid_uuid14']
            driver['reason'] = ''
            del driver['reposition_session_id']
        else:
            driver = updated_etalons['dbid_uuid2']
            driver['reason'] = ''
            del driver['reposition_session_id']

            driver = updated_etalons['dbid_uuid8']
            driver['reason'] = ''

            driver = updated_etalons['dbid_uuid9']
            driver['reason'] = ''

            driver = updated_etalons['dbid_uuid13']
            driver['reason'] = utils.Reason.kOldMode
            del driver['reposition_session_id']

            driver = updated_etalons['dbid_uuid14']
            driver['reason'] = ''
            del driver['reposition_session_id']
    utils.check_filter_result(response, updated_etalons)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid10',
        'dbid_uuid11',
        'dbid_uuid12',
        'dbid_uuid13',
        'dbid_uuid14',
        'dbid_uuid15',
        'dbid_uuid16',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid6',
        'dbid_uuid7',
        'dbid_uuid8',
        'dbid_uuid9',
    ]
    # filtered driver is still in db
    updated_etalons['dbid_uuid16'] = {
        'driver_id': 'dbid_uuid16',
        'state': utils.State.kFiltered,
        'reason': utils.Reason.kUserCancel,
        'airport': 'ekb',
        'areas': ['main'],
        'classes': ['comfortplus', 'econom'],
        'old_mode_enabled': None,
    }
    # driver with order is entered on action
    if not timeout:
        updated_etalons['dbid_uuid10']['reason'] = utils.Reason.kOnAction

    if timeout:
        delayed_processing = [
            'dbid_uuid1',
            'dbid_uuid2',
            'dbid_uuid8',
            'dbid_uuid9',
            'dbid_uuid10',
            'dbid_uuid14',
        ]
    else:
        delayed_processing = ['dbid_uuid2']
    utils.update_etalons_by_simulation_old_queue_filter_processing(
        updated_etalons, mode, delayed_processing,
    )
    utils.check_drivers_queue(db, updated_etalons.values())

    driver_events = utils.get_driver_events(db)
    if mode == 'old':
        assert not driver_events
    else:
        if not timeout:
            assert (
                list(utils.get_driver_events(db, no_event_id=True).keys())
                == [
                    ('udid10', 'entered_on_order'),
                    ('udid12', 'entered_on_repo'),
                    ('udid13', 'entered_on_repo'),
                    ('udid2', 'entered_on_repo'),
                    ('udid3', 'entered_on_repo'),
                    ('udid7', 'entered_on_repo'),
                ]
            )
        else:
            assert (
                list(utils.get_driver_events(db, no_event_id=True).keys())
                == [
                    ('udid12', 'entered_on_repo'),
                    ('udid3', 'entered_on_repo'),
                    ('udid7', 'entered_on_repo'),
                ]
            )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['reposition_entered_driver_queue.sql', 'driver_events.sql'],
)
async def test_reposition_sintegro(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        mockserver,
        now,
        taxi_config,
        load_json,
        mode,
):
    stopped_sessions = []

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(REPOSITION_FILTER_NAME + '-finished')
    def reposition_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('reposition_driver_reset_reason')
    def reset_reason(driver_id):
        return driver_id

    @testpoint('wrong_queue_entered_on_reposition')
    def wrong_queue_entered(driver_id):
        return driver_id

    @testpoint('wrong_relocated_tariff')
    def wrong_relocated_tariff(data):
        return data

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 13
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('entered_changed_tariffs_candidates_response.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 13
        return load_json('reposition_sintegro_categories_response.json')

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() is None
        request_drivers = []
        for i in range(request.DriversLength()):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            request_drivers.append(f'{dbid}_{uuid}')
        assert sorted(request_drivers) == [
            'dbid_uuid10',
            'dbid_uuid11',
            'dbid_uuid12',
            'dbid_uuid13',
            'dbid_uuid14',
            'dbid_uuid15',
            'dbid_uuid16',
            'dbid_uuid17',
            'dbid_uuid18',
            'dbid_uuid19',
            'dbid_uuid20',
            'dbid_uuid21',
            'dbid_uuid22',
        ]

        drivers = [
            {
                'dbid': 'dbid',
                'uuid': 'uuid10',
                'airport_id': 'ekb',
                'mode': 'Sintegro',
            },
            {
                'dbid': 'dbid',
                'uuid': 'uuid11',
                'airport_id': 'ekb',
                'mode': 'Sintegro',
            },
            {
                'dbid': 'dbid',
                'uuid': 'uuid14',
                'airport_id': 'ekb',
                'mode': 'Sintegro',
            },
            {'dbid': 'dbid', 'uuid': 'uuid17', 'airport_id': 'svo'},
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        stopped_sessions.append(request.json['session_id'])
        return {}

    # changed tariffs
    # dbid_uuid10 - no state started reposition with econom, business,
    # but finished with only business
    # dbid_uuid11 - no state started reposition with econom,
    # but finished with econom, business
    # dbid_uuid12 - entered started reposition with econom, business,
    # but finished with only business
    # dbid_uuid13 - entered started reposition with econom,
    # but finished with econom, business
    # target_qiueue_airport_id
    # dbid_uuid14 - entered on reposition driver, waiting zone,
    # but sintegro reposition to a different airport
    # dbid_uuid15 - entered on reposition driver, but pathfinder has ended
    # dbid_uuid16 - entered on airport reposition driver, waiting zone,
    # but was sintegro reposition to a different airport
    # dbid_uuid17 - new driver -> entered on airport reposition
    # to a different airport
    # mixed mode new_mode_tariffs check
    # dbid_uuid18 - entered driver with Sintegro reposition
    # new_mode_tariffs = ['comfortplus']
    # dbid_uuid19 - entered driver with Sintegro reposition
    # new_mode_tariffs = ['econom']
    # dbid_uuid20 - entered driver with Sintegro reposition
    # new_mode_tariffs = []
    # dbid_uuid21 - entered driver with Sintegro reposition
    # new_mode_tariffs = ['comfortplus', 'econom']
    # dbid_uuid22 - entered driver with Sintegro reposition
    # new_mode_tariffs = None

    # new mode
    # taxi_config.set_values(utils.custom_config(False))
    old_mode_enabled = utils.get_old_mode_enabled(mode)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid10': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid11': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom', 'business'],
        },
        'dbid_uuid12': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid13': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom', 'business'],
        },
        'dbid_uuid14': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid15': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid16': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid17': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid18': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid19': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid20': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid21': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
        'dbid_uuid22': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
            'classes': ['econom'],
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await reposition_filter_finished.wait_call())['data']
    mixed_mode_enabled = mode in ['mixed_base_new', 'mixed_base_old']
    updated_etalons = {
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid10',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid11',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kChangeTariff,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid12',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid13',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid14',
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_mode': 'Sintegro',
        },
        'dbid_uuid15': {
            'driver_id': 'dbid_uuid15',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid16': {
            'driver_id': 'dbid_uuid16',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid16',
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_mode': 'Airport',
        },
        'dbid_uuid17': {
            'driver_id': 'dbid_uuid17',
            'state': (
                utils.State.kFiltered
                if not old_mode_enabled
                else utils.State.kEntered
            ),
            'reason': (
                utils.Reason.kNonAirportReposition
                if not old_mode_enabled
                else ''
            ),
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid18': {
            'driver_id': 'dbid_uuid18',
            'state': utils.State.kQueued,
            'reason': (
                utils.Reason.kOnRepositionOldMode
                if mixed_mode_enabled
                else utils.Reason.kOnReposition
            ),
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid18',
        },
        'dbid_uuid19': {
            'driver_id': 'dbid_uuid19',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid19',
        },
        'dbid_uuid20': {
            'driver_id': 'dbid_uuid20',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid20',
        },
        'dbid_uuid21': {
            'driver_id': 'dbid_uuid21',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid21',
        },
        'dbid_uuid22': {
            'driver_id': 'dbid_uuid22',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid22',
        },
    }
    utils.check_filter_result(response, updated_etalons)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    assert utils.get_calls_sorted(
        wrong_queue_entered, 1, 'driver_id', None,
    ) == ['dbid_uuid14']
    assert utils.get_calls_sorted(reset_reason, 1, 'driver_id', None) == [
        'dbid_uuid15',
    ]

    if not mixed_mode_enabled:
        assert (
            utils.get_calls_sorted(
                wrong_relocated_tariff, 0, 'data', 'driver_id',
            )
            == []
        )
    else:
        assert (
            utils.get_calls_sorted_two_keys(
                wrong_relocated_tariff, 4, 'data', 'driver_id', 'tariff',
            )
            == [
                {'driver_id': 'dbid_uuid19', 'tariff': 'comfortplus'},
                {'driver_id': 'dbid_uuid19', 'tariff': 'econom'},
                {'driver_id': 'dbid_uuid20', 'tariff': 'comfortplus'},
                {'driver_id': 'dbid_uuid21', 'tariff': 'econom'},
            ]
        )

    assert sorted(stopped_sessions) == [
        'session_dbid_uuid12',
        'session_dbid_uuid13',
        'session_dbid_uuid16',
        'session_dbid_uuid18',
        'session_dbid_uuid19',
        'session_dbid_uuid20',
        'session_dbid_uuid21',
        'session_dbid_uuid22',
    ]
