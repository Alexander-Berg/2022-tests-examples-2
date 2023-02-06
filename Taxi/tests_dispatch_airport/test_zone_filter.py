import copy
import datetime

import pytest

import tests_dispatch_airport.utils as utils


ZONE_FILTER_NAME = 'zone-filter'


def get_new_iteration_etalon(etalon):
    new_etalon = copy.deepcopy(etalon)
    del new_etalon['dbid_uuid3']
    del new_etalon['dbid_uuid3_1']
    del new_etalon['dbid_uuid5']
    new_etalon['dbid_uuid7']['reason'] = utils.Reason.kOnAction

    for driver_id in ('dbid_uuid8', 'dbid_uuid9', 'dbid_uuid10'):
        driver = new_etalon[driver_id]
        driver['areas'] = [2]
        driver['left_queue_started_tp'] = driver_id == 'dbid_uuid9'
    return new_etalon


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid7',
            'order_id': 'order_id_7',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid8',
            'order_id': 'order_id_8',
            'taxi_status': 2,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid9',
            'order_id': 'order_id_9',
            'taxi_status': 2,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid10',
            'order_id': 'order_id_10',
            'taxi_status': 2,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.now('2020-05-01T21:00:00+0000')
async def test_zone_filter(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        now,
        redis_store,
        order_archive_mock,
        load_json,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(ZONE_FILTER_NAME + '-finished')
    def simulation_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    order_archive_mock.set_order_proc(
        [
            load_json('order_proc_uuid8.json'),
            load_json('order_proc_uuid9.json'),
            load_json('order_proc_uuid10.json'),
        ],
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - queued driver
    # dbid_uuid2 - queued driver left waiting zone (notification zone)
    # dbid_uuid3 - queued driver left waiting zone and allowed timeout expired
    # dbid_uuid3_1 - same as dbid_uuid3, but long ago had active order
    # dbid_uuid3_2 - same as dbid_uuid3, but recently had active order
    # dbid_uuid4 - queued_left_zone driver returned into waiting zone
    # dbid_uuid5 - stored driver left airport zone
    # dbid_uuid6 - queued driver left waiting zone previously and still didn't
    #              return (main zone only)
    # dbid_uuid7 - entered busy driver with airport order (just skip)
    # dbid_uuid8 - queued busy driver (airport order) left waiting zone
    # dbid_uuid9 - queued busy driver (not airport order) left waiting zone
    # dbid_uuid10 - queued busy driver (airport order, active timer)
    #              left waiting zone

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.OUT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # simulation-filter check
    response = (await simulation_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
            'left_queue_started_tp': False,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'left_queue_started_tp': True,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kFilterQueuedLeftZone,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'left_queue_started_tp': True,
        },
        'dbid_uuid3_1': {
            'driver_id': 'dbid_uuid3_1',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kFilterQueuedLeftZone,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'left_queue_started_tp': True,
        },
        'dbid_uuid3_2': {
            'driver_id': 'dbid_uuid3_2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'left_queue_started_tp': True,
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'left_queue_started_tp': False,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kLeftZone,
            'airport': 'ekb',
            'areas': [],
            'classes': ['econom'],
            'left_queue_started_tp': False,
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0],
            'classes': ['econom'],
            'left_queue_started_tp': True,
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'left_queue_started_tp': False,
            'input_order_id': 'order_id_7',
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1],
            'classes': ['econom'],
            'left_queue_started_tp': False,
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1],
            'classes': ['econom'],
            'left_queue_started_tp': False,
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0],
            'classes': ['econom'],
            'left_queue_started_tp': True,
        },
    }
    utils.check_filter_result(response, updated_etalons)
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    await taxi_dispatch_airport.invalidate_caches()
    geobus_now += datetime.timedelta(minutes=2)
    geobus_drivers = {
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
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # simulation-filter check
    response = (await simulation_filter_finished.wait_call())['data']
    utils.check_filter_result(
        response, get_new_iteration_etalon(updated_etalons),
    )
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid10',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid3_1',
        'dbid_uuid3_2',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
        'dbid_uuid8',
        'dbid_uuid9',
    ]
    assert not utils.get_driver_events(db)
