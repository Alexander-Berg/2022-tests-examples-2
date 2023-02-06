import datetime
import json

import pytest

import tests_dispatch_airport.utils as utils


SIMULATION_FILTER_NAME = 'simulation-old-queue-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize(
    'new_mode_reasons, old_mode_reasons',
    [
        (None, ['offline']),
        (None, None),
        (['on_reposition'], []),
        (['on_reposition', 'offline'], None),
    ],
)
async def test_simulation_old_queue_filter(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        load_json,
        redis_store,
        taxi_config,
        mode,
        now,
        new_mode_reasons,
        old_mode_reasons,
):
    config = utils.custom_config(utils.get_old_mode_enabled(mode))
    if mode == 'new':
        config['DISPATCH_AIRPORT_ZONES']['ekb'][
            'offline_allowed_time_sec'
        ] = 10
    if new_mode_reasons is not None:
        config['DISPATCH_AIRPORT_NEW_MODE_ALLOWED_REASONS'] = {
            '__default': [],
            'ekb': new_mode_reasons,
        }
    if old_mode_reasons is not None:
        config['DISPATCH_AIRPORT_OLD_MODE_DO_NOT_QUEUE_REASONS'] = {
            '__default': [],
            'ekb': old_mode_reasons,
        }
    taxi_config.set_values(config)
    utils.set_mode_in_config(taxi_config, mode)

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(SIMULATION_FILTER_NAME + '-finished')
    def simulation_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 14
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 14
        return utils.generate_categories_response(
            [driver['driver_id'] for driver in request.json['drivers']],
            ['comfortplus', 'econom'],
        )

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        drivers = [
            {'dbid': 'dbid', 'uuid': 'uuid3', 'airport_id': 'ekb'},
            {
                'dbid': 'dbid',
                'uuid': 'uuid11',
                'airport_id': 'ekb',
                'session_id': 'rid11',
            },
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        req = json.loads(request.get_data())
        assert req['session_id'] in ('session_dbid_uuid4', 'rid12')
        return {}

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]
        if mode != 'new':
            append_queued = [
                'dbid_uuid13',
                'dbid_uuid14',
                'dbid_uuid2',
                'dbid_uuid4',
                'dbid_uuid6',
            ]
            append_entered = [
                'dbid_uuid1',
                'dbid_uuid3',
                'dbid_uuid5',
                'dbid_uuid7',
                'dbid_uuid8',
                'dbid_uuid9',
                'dbid_uuid10',
                'dbid_uuid11',
                'dbid_uuid12',
            ]
            remove_entered = [
                'dbid_uuid13',
                'dbid_uuid14',
                'dbid_uuid4',
                'dbid_uuid6',
            ]
            if (
                    old_mode_reasons is not None
                    and utils.Reason.kOffline in old_mode_reasons
            ):
                append_queued.remove('dbid_uuid14')
                append_entered.append('dbid_uuid14')
                remove_entered.remove('dbid_uuid14')
            utils.check_airport_tags(
                append,
                expected_queued=append_queued,
                expected_entered=append_entered,
            )
            utils.check_airport_tags(remove, (), remove_entered)
        else:
            append_entered = [
                'dbid_uuid3',
                'dbid_uuid5',
                'dbid_uuid10',
                'dbid_uuid11',
                'dbid_uuid12',
            ]
            remove_entered = [
                'dbid_uuid14',
                'dbid_uuid13',
                'dbid_uuid4',
                'dbid_uuid6',
                'dbid_uuid7',
            ]
            if (
                    new_mode_reasons is not None
                    and utils.Reason.kOffline in new_mode_reasons
            ):
                append_entered.append('dbid_uuid14')
                remove_entered.remove('dbid_uuid14')
            utils.check_airport_tags(
                append,
                expected_queued=('dbid_uuid4', 'dbid_uuid6', 'dbid_uuid13'),
                expected_entered=append_entered,
            )
            utils.check_airport_tags(remove, (), remove_entered)
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: notification zone
    # dbid_uuid2 - new driver: waiting zone
    # dbid_uuid3 - new driver: with reposition, notification zone
    # dbid_uuid4 - stored driver: on reposition, waiting zone
    # dbid_uuid5 - stored driver: old_mode, notification zone
    # dbid_uuid6 - stored driver: old_mode, waiting zone

    # (simulated via database, because of test zone structure)
    # dbid_uuid7 - new driver: like `dbid_uuid1`, but main only zone

    # dbid_uuid8 - new driver, notification area, offline
    # dbid_uuid9 - new driver, waiting area, offline
    # dbid_uuid10 - entered old_mode driver, notification area, offline
    # dbid_uuid11 - entered on reposition driver, notification area, offline
    # dbid_uuid12 - entered old_mode driver, waiting area, offline
    # dbid_uuid13 - entered on reposition driver, waiting area, offline
    # dbid_uuid14 - entered, waiting area, reason=offline (unknown for entered)
    # -> queued in old mode, filtered in new

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid10': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid11': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid12': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid13': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # simulation-filter check
    response = (await simulation_filter_finished.wait_call())['data']
    old_mode_enabled = utils.get_old_mode_enabled(mode)
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid3',
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid4',
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [0],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': (
                utils.State.kEntered
                if mode != 'new'
                else utils.State.kFiltered
            ),
            'reason': (
                'old_mode' if mode != 'new' else utils.Reason.kFullQueue
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'offline_started_tp': True,
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'state': (
                utils.State.kEntered
                if mode != 'new'
                else utils.State.kFiltered
            ),
            'reason': (
                'old_mode' if mode != 'new' else utils.Reason.kFullQueue
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'offline_started_tp': True,
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kEntered,
            'reason': 'old_mode',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'offline_started_tp': True,
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kEntered,
            'reason': 'on_reposition',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'rid11',
            'offline_started_tp': True,
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': utils.State.kEntered,
            'reason': 'old_mode',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'offline_started_tp': True,
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': utils.State.kQueued,
            'reason': 'on_reposition',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'rid12',
            'offline_started_tp': True,
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': (
                utils.State.kQueued if mode != 'new' else utils.State.kFiltered
            ),
            'reason': (
                'old_mode' if mode != 'new' else utils.Reason.kFullQueue
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [0, 1, 2],
            'classes': ['comfortplus', 'econom'],
            'offline_started_tp': False,
        },
    }
    if (
            mode != 'new'
            and old_mode_reasons is not None
            and utils.Reason.kOffline in old_mode_reasons
    ):
        updated_etalons['dbid_uuid14']['state'] = utils.State.kEntered
        updated_etalons['dbid_uuid14']['reason'] = utils.Reason.kOffline
    if mode == 'new':
        for driver_id in ('dbid_uuid1', 'dbid_uuid2', 'dbid_uuid7'):
            updated_etalons[driver_id]['state'] = utils.State.kFiltered
            updated_etalons[driver_id]['reason'] = utils.Reason.kFullQueue
        if (
                new_mode_reasons is not None
                and utils.Reason.kOffline in new_mode_reasons
        ):
            updated_etalons['dbid_uuid14']['state'] = utils.State.kEntered
            updated_etalons['dbid_uuid14']['reason'] = utils.Reason.kOffline

    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

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
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
        'dbid_uuid8',
        'dbid_uuid9',
    ]

    utils.update_etalons_by_simulation_old_queue_filter_processing(
        updated_etalons, mode,
    )
    utils.check_drivers_queue(db, updated_etalons.values())

    driver_events = utils.get_driver_events(db)
    if mode == 'old':
        assert not driver_events
    else:
        assert driver_events == {
            (
                'udid4',
                utils.get_driver_session_id(db, 'dbid_uuid4'),
                'entered_on_repo',
            ): {'airport_id': 'ekb', 'driver_id': 'dbid_uuid4'},
        }
