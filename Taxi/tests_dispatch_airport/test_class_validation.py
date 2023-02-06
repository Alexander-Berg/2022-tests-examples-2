import copy
import datetime

import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'dbid_uuid5', 'airport_queue_test_allow_tag')],
    topic_relations=[('airport_queue', 'airport_queue_test_allow_tag')],
)
@pytest.mark.now('2021-01-01T10:15:00+00:00')
async def test_class_validation_filter(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        mode,
):
    number_of_drivers = 9

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('adjust_classes_old_mode')
    def adjust_classes_old_mode(driver_id):
        return driver_id

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == number_of_drivers
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == number_of_drivers
        result = utils.generate_categories_response(
            [driver['driver_id'] for driver in request.json['drivers']],
            ['comfortplus', 'econom'],
        )
        result['drivers'][0]['categories'] = ['econom']
        result['drivers'][1]['categories'] = ['comfortplus']
        return result

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    @testpoint('old_queued_driver')
    def old_queued_driver(driver_id):
        return driver_id

    # dbid_uuid1 - no state->entered old_mode driver (only econom)
    # dbid_uuid2 - entered->queued new_mode driver with
    # on_reposition reason (only comfortplus)
    # dbid_uuid3 - entered mixed_mode driver with old_mode reason
    # dbid_uuid4 - entered->queued mixed_mode driver with old_mode reason
    # dbid_uuid5 - entered->queued mixed_mode driver on_tag reason
    # dbid_uuid6 - entered mixed_mode driver on_repeat_queue reason
    # dbid_uuid7 - queued mixed_mode driver on_action reason
    # at first in db classes are econom, comfortplus,
    # they are updated on queue_update
    # dbid_uuid8 - queued on_repo_old_mode driver
    # dbid_uuid9 - queued old_mode driver, was queued
    # before the switch from config

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_TAGS_QUEUING': {
                '__default__': {'allow': ['airport_queue_test_allow_tag']},
            },
        },
    )
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_OLD_MODE_DO_NOT_QUEUE_REASONS': {
                '__default__': [
                    'on_action',
                    'on_reposition',
                    'unknown_reposition',
                    'on_repeat_queue',
                ],
            },
        },
    )
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_MIXED_MODE_ALLOWED_DRIVERS': {
                'allowed_drivers': [],
                'enabled': False,
                'airport_switch_settings': {
                    'ekb': {
                        'allowed_for_all': True,
                        'switch_start_time': '2021-01-01T10:00:00+00:00',
                    },
                },
            },
        },
    )
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

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
        'dbid_uuid4': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    old_mode_enabled = utils.get_old_mode_enabled(mode)
    all_classes = ['comfortplus', 'econom']
    classes = copy.deepcopy(all_classes)
    if mode in ['mixed_base_old', 'mixed_base_new']:
        classes.remove('comfortplus')

    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': (
                utils.State.kEntered
                if mode != 'new'
                else utils.State.kFiltered
            ),
            'reason': (
                utils.Reason.kOldMode
                if mode != 'new'
                else utils.Reason.kFullQueue
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification'],
            'classes': ['econom'],
            'class_queued': None,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification', 'waiting'],
            'classes': ['comfortplus'],
            'class_queued': ['comfortplus'],
            'reposition_session_id': 'rsid2',
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification'],
            'classes': classes,
            'class_queued': None,
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification', 'waiting'],
            'classes': classes,
            'class_queued': all_classes,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnTag,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification', 'waiting'],
            'classes': all_classes,
            'class_queued': all_classes,
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnRepeatQueue,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification'],
            'classes': all_classes,
            'class_queued': None,
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification', 'waiting'],
            'classes': ['comfortplus', 'econom'],
            'class_queued': all_classes,
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnRepositionOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification', 'waiting'],
            'classes': classes,
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': ['notification', 'waiting'],
            'classes': all_classes,
        },
    }
    utils.check_drivers_queue(
        pgsql['dispatch_airport'], updated_etalons.values(),
    )
    if mode in ['old', 'new']:
        assert (
            utils.get_calls_sorted(
                adjust_classes_old_mode, 0, 'driver_id', None,
            )
            == []
        )
    else:
        assert utils.get_calls_sorted(
            adjust_classes_old_mode, 4, 'driver_id', None,
        ) == ['dbid_uuid1', 'dbid_uuid3', 'dbid_uuid4', 'dbid_uuid8']

        assert utils.get_calls_sorted(
            old_queued_driver, 1, 'driver_id', None,
        ) == ['dbid_uuid9']
