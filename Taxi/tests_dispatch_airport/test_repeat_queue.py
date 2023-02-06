import datetime

import pytest

import tests_dispatch_airport.utils as utils

REPEAT_QUEUE_FILTER_NAME = 'repeat-queue'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.parametrize('use_repeat_queue', [True, False])
async def test_repeat_queue(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        mode,
        use_repeat_queue,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(REPEAT_QUEUE_FILTER_NAME + '-finished')
    def repeat_queue_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 11
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 11
        return load_json('categories.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['old_mode_enabled'] = utils.get_old_mode_enabled(mode)
    zones_config['ekb']['use_repeat_queue'] = use_repeat_queue
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})
    utils.set_mode_in_config(taxi_config, mode)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid0': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid1': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.WAITING_POSITION,
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
        'dbid_uuid14': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    # dbid_uuid0 - new driver in notification zone,
    #              has allowed entered_on_order event
    # dbid_uuid1 - new driver in waiting zone,
    #              has allowed entered_on_repo event
    # dbid_uuid2 - new driver in notification zone,
    #              has filtered_by_forbidden_reason event
    # dbid_uuid3 - new driver in waiting zone,
    #              has filtered_by_forbidden_reason event
    # dbid_uuid4 - new driver in waiting zone,
    #              has more than one events, last is allowed
    # dbid_uuid5 - new driver in waiting zone with allowed event
    #              without udid, ignored on this iteration
    #
    # dbid_uuid10 - stored queued driver in waiting zone,
    #               nothing changes
    # dbid_uuid11 - stored entered driver in notification zone,
    #               has allowed event and kOnRepeatQueueReason,
    #               nothing changes
    # dbid_uuid12 - stored entered driver with kOnRepeatQueueReason
    #               in waiting zone, doesn't have allowed event
    #               -> queued (in old mode nothing changes)
    # dbid_uuid13 - stored entered driver with kOnRepeatQueueReason
    #               in waiting zone, has allowed event -> queued
    #               (in old mode nothing changes)
    # dbid_uuid14 - new driver in waiting zone,
    #              has allowed entered_on_order_wrong_client event

    # repeat_queue filter now queues independently
    # of driver_mode
    driver_ignored = not use_repeat_queue

    old_mode_enabled = utils.get_old_mode_enabled(mode)

    etalon = {
        'dbid_uuid0': {
            'driver_id': 'dbid_uuid0',
            'state': utils.State.kEntered,
            'reason': ('' if driver_ignored else utils.Reason.kOnRepeatQueue),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': (
                utils.State.kEntered if driver_ignored else utils.State.kQueued
            ),
            'reason': ('' if driver_ignored else utils.Reason.kOnRepeatQueue),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': (
                utils.State.kEntered if driver_ignored else utils.State.kQueued
            ),
            'reason': ('' if driver_ignored else utils.Reason.kOnRepeatQueue),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'input_order_id': 'input_order_10',
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnRepeatQueue,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': (
                utils.State.kEntered if driver_ignored else utils.State.kQueued
            ),
            'reason': utils.Reason.kOnRepeatQueue,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': (
                utils.State.kEntered if driver_ignored else utils.State.kQueued
            ),
            'reason': utils.Reason.kOnRepeatQueue,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': (
                utils.State.kEntered if driver_ignored else utils.State.kQueued
            ),
            'reason': ('' if driver_ignored else utils.Reason.kOnRepeatQueue),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
    }

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await repeat_queue_filter_finished.wait_call())['data']

    assert len(response) == len(etalon)
    for driver in response:
        etalon_driver = etalon[driver['driver_id']]
        utils.check_drivers(driver, etalon_driver)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid0',
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
    ]
