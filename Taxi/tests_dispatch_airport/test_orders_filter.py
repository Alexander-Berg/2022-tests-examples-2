import datetime

import pytest
import pytz

import tests_dispatch_airport.utils as utils

ORDERS_FILTER_NAME = 'orders-filter'

MAIN_AREA_NAME = 'main_area'
WAITING_AREA_NAME = 'waiting_area'
NOTIFICATION_AREA_NAME = 'notification_area'

CLASSES = ['comfortplus', 'econom']


def get_input_order_finished_tp(cursor, driver_id):
    cursor.execute(
        f"""
        SELECT input_order_finished_tp
        FROM dispatch_airport.drivers_queue
        WHERE driver_id = '{driver_id}';
    """,
    )
    return list(cursor)[0][0].astimezone(pytz.utc)


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_2',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid6',
            'order_id': 'order_id_6',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid7',
            'order_id': 'order_id_7',
            'taxi_status': 3,
            'final_destination': {'lat': 2.0, 'lon': 2.0},
        },
        {
            'driver_id': 'dbid_uuid8',
            'order_id': 'order_id_8',
            'taxi_status': 3,
        },
        {
            'driver_id': 'dbid_uuid15',
            'order_id': 'order_id_15',
            'taxi_status': 2,
        },
        {
            'driver_id': 'dbid_uuid17',
            'order_id': 'order_id_17',
            'taxi_status': 3,
            'final_destination': {'lat': 16.0, 'lon': 66.0},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_orders_filter(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        order_archive_mock,
        now,
        load_json,
        taxi_config,
        mode,
):
    # orders filter is the same in mixed mode as in new mode
    old_mode_works = mode == 'old'
    old_mode_enabled = mode in ['old', 'mixed_base_old']

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(ORDERS_FILTER_NAME + '-finished')
    def orders_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 16
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 16
        return load_json('categories.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]

        expected_queued_drivers = [
            'dbid_uuid3',
            'dbid_uuid5',
            'dbid_uuid11',
            'dbid_uuid17',
        ]
        if old_mode_works:
            expected_queued_drivers.append('dbid_uuid4')
        expected_entered_drivers = [
            'dbid_uuid1',
            'dbid_uuid9',
            'dbid_uuid10',
            'dbid_uuid13',
            'dbid_uuid14',
            'dbid_uuid15',
        ]
        if old_mode_works:
            expected_entered_drivers += ['dbid_uuid8', 'dbid_uuid12']
        utils.check_airport_tags(
            append, expected_queued_drivers, expected_entered_drivers,
        )

        removed_entered_drivers = [
            'dbid_uuid3',
            'dbid_uuid4',
            'dbid_uuid5',
            'dbid_uuid11',
        ]
        if not old_mode_works:
            removed_entered_drivers += ['dbid_uuid12']
        utils.check_airport_tags(
            remove, ('dbid_uuid6', 'dbid_uuid7'), removed_entered_drivers,
        )

        return {}

    # retrieve setup
    order_archive_mock.set_order_proc(
        [
            load_json('order_proc_uuid3.json'),
            load_json('order_proc_uuid4.json'),
            load_json('order_proc_uuid5.json'),
            load_json('order_proc_uuid6.json'),
            load_json('order_proc_uuid7.json'),
            load_json('order_proc_uuid17.json'),
        ],
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new busy driver (airport order -> on_action)
    # dbid_uuid2 - new busy driver (not airport order -> filtered)
    # dbid_uuid3 - stored on_action driver (not busy -> valid cost -> queued)
    # dbid_uuid4 - stored on_action driver (not busy -> low cost -> filtered)
    # dbid_uuid5 - stored on_action driver (not busy -> no cost -> queued)
    # dbid_uuid6 - stored queued driver (busy -> airport order -> holded)
    # dbid_uuid7 - stored queued driver (busy -> outside order -> filtered)
    # dbid_uuid8 - new busy driver (no destination -> filtered)
    # dbid_uuid9 - stored entered (on_action -> on_action_order_finished)
    # dbid_uuid10 - stored driver (order finished -> in main -> on_action)
    # dbid_uuid11 - stored driver (order finished, in waiting -> queued)
    # dbid_uuid12 - stored driver (order finished, in main, expired)
    # dbid_uuid13 - stored driver (order finished, in main, but not expired)

    # dbid_uuid14 - just entered old_mode driver
    # dbid_uuid15 - entered driver (busy with waiting order status)
    # dbid_uuid17 - stored queued driver (busy -> outside order, but same as
    #               input order -> still queued). Also see dbid_uuid7.

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
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # orders-filter check
    response = (await orders_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': CLASSES,
            'input_order_id': 'order_id_1',
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kNotAirportInputOrder,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': CLASSES,
            'input_order_id': 'order_id_2',
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_3',
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': (
                utils.State.kQueued
                if old_mode_works
                else utils.State.kFiltered
            ),
            'reason': (
                utils.Reason.kOnAction
                if old_mode_works
                else utils.Reason.kLowOrderPrice
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_4',
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_5',
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kHolded,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongOutputOrder,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': (
                utils.State.kEntered
                if old_mode_works
                else utils.State.kFiltered
            ),
            'reason': (
                utils.Reason.kOnAction
                if old_mode_works
                else utils.Reason.kInputOrderWithoutDestination
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': CLASSES,
            'input_order_id': 'order_id_8',
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': CLASSES,
            'input_order_id': 'order_id_9',
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [0, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_10',
            'input_order_finished_tp': True,
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_11',
            'input_order_finished_tp': False,
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': (
                utils.State.kEntered
                if old_mode_works
                else utils.State.kFiltered
            ),
            'reason': (
                utils.Reason.kOnAction
                if old_mode_works
                else utils.Reason.kOnActionTooLate
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [0, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_12',
            'input_order_finished_tp': True,
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [0, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_13',
            'input_order_finished_tp': True,
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': CLASSES,
        },
        'dbid_uuid15': {
            'driver_id': 'dbid_uuid15',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': CLASSES,
            'input_order_id': 'order_id_15',
        },
        'dbid_uuid17': {
            'driver_id': 'dbid_uuid17',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': CLASSES,
            'input_order_id': 'order_id_17',
        },
    }
    if old_mode_works:
        updated_etalons['dbid_uuid8']['input_order_id'] = 'order_id_8'

    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    driver13_tp = get_input_order_finished_tp(db.cursor(), 'dbid_uuid13')
    assert driver13_tp < now.replace(tzinfo=pytz.UTC) - datetime.timedelta(
        minutes=58,
    )
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid10',
        'dbid_uuid11',
        'dbid_uuid12',
        'dbid_uuid13',
        'dbid_uuid14',
        'dbid_uuid15',
        'dbid_uuid17',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
        'dbid_uuid8',
        'dbid_uuid9',
    ]
    driver_events = utils.get_driver_events(db)
    if old_mode_works:
        assert not driver_events
    else:
        assert driver_events == {
            (
                'udid3',
                utils.get_driver_session_id(db, 'dbid_uuid3'),
                'entered_on_order',
            ): {'airport_id': 'ekb', 'driver_id': 'dbid_uuid3'},
            (
                'udid11',
                utils.get_driver_session_id(db, 'dbid_uuid11'),
                'entered_on_order',
            ): {'airport_id': 'ekb', 'driver_id': 'dbid_uuid11'},
            (
                'udid17',
                utils.get_driver_session_id(db, 'dbid_uuid17'),
                'entered_on_order',
            ): {'airport_id': 'ekb', 'driver_id': 'dbid_uuid17'},
            (
                'udid5',
                utils.get_driver_session_id(db, 'dbid_uuid5'),
                'entered_on_order',
            ): {'airport_id': 'ekb', 'driver_id': 'dbid_uuid5'},
        }


# check follow driver categories:
# dbid_uuid1 - new busy driver (airport order in notification area)
# dbid_uuid2 - new busy driver (airport order in main area)
# dbid_uuid3 - new busy driver (airport order in waiting area)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.NOTIFICATION_POSITION[1],
                'lon': utils.NOTIFICATION_POSITION[0],
            },
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_2',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.AIRPORT_POSITION[1],
                'lon': utils.AIRPORT_POSITION[0],
            },
        },
        {
            'driver_id': 'dbid_uuid3',
            'order_id': 'order_id_3',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.WAITING_POSITION[1],
                'lon': utils.WAITING_POSITION[0],
            },
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'driver_for_check,allowed_airport_zones,expected_driver_state_new_mode',
    [
        ('dbid_uuid1', None, utils.State.kEntered),
        ('dbid_uuid1', [], utils.State.kFiltered),
        (
            'dbid_uuid1',
            [MAIN_AREA_NAME, WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            utils.State.kEntered,
        ),
        (
            'dbid_uuid1',
            [MAIN_AREA_NAME, NOTIFICATION_AREA_NAME],
            utils.State.kEntered,
        ),
        ('dbid_uuid1', [NOTIFICATION_AREA_NAME], utils.State.kEntered),
        (
            'dbid_uuid1',
            [MAIN_AREA_NAME, WAITING_AREA_NAME],
            utils.State.kFiltered,
        ),
        ('dbid_uuid1', [MAIN_AREA_NAME], utils.State.kFiltered),
        ('dbid_uuid2', None, utils.State.kEntered),
        ('dbid_uuid2', [], utils.State.kFiltered),
        (
            'dbid_uuid2',
            [MAIN_AREA_NAME, WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            utils.State.kEntered,
        ),
        (
            'dbid_uuid2',
            [MAIN_AREA_NAME, WAITING_AREA_NAME],
            utils.State.kEntered,
        ),
        ('dbid_uuid2', [MAIN_AREA_NAME], utils.State.kEntered),
        (
            'dbid_uuid2',
            [WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            # Entered because of main area is part of the
            # waiting and notification
            utils.State.kEntered,
        ),
        ('dbid_uuid3', None, utils.State.kEntered),
        ('dbid_uuid3', [], utils.State.kFiltered),
        (
            'dbid_uuid3',
            [MAIN_AREA_NAME, WAITING_AREA_NAME, NOTIFICATION_AREA_NAME],
            utils.State.kEntered,
        ),
        (
            'dbid_uuid3',
            [MAIN_AREA_NAME, WAITING_AREA_NAME],
            utils.State.kEntered,
        ),
        ('dbid_uuid3', [WAITING_AREA_NAME], utils.State.kEntered),
        (
            'dbid_uuid3',
            [NOTIFICATION_AREA_NAME],
            # Entered because of waiting area is part of the
            # notification area
            utils.State.kEntered,
        ),
        ('dbid_uuid3', [MAIN_AREA_NAME], utils.State.kFiltered),
    ],
)
async def test_orders_filter_allowed_airport_zones(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        mode,
        driver_for_check,
        allowed_airport_zones,
        expected_driver_state_new_mode,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(ORDERS_FILTER_NAME + '-finished')
    def orders_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 1
        return load_json('candidates_allowed_airport_zones.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 1
        return load_json('categories_allowed_airport_zones.json')

    old_mode_works = mode == 'old'
    old_mode_enabled = mode in ['old', 'mixed_base_old']

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    ekb_config = zones_config['ekb']
    if allowed_airport_zones is not None:
        ekb_config['input_order_allowed_areas'] = allowed_airport_zones
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        driver_for_check: {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    driver_entered = (
        old_mode_works
        or expected_driver_state_new_mode == utils.State.kEntered
    )

    # orders-filter check
    response = (await orders_filter_finished.wait_call())['data']
    updated_etalons = {
        driver_for_check: {
            'driver_id': driver_for_check,
            'state': (
                utils.State.kEntered
                if driver_entered
                else expected_driver_state_new_mode
            ),
            'reason': (
                utils.Reason.kOnAction
                if driver_entered
                else utils.Reason.kNotAllowedAreaInputOrder
            ),
            'airport': 'ekb',
            'areas': [2],
            'classes': CLASSES,
            'old_mode_enabled': old_mode_enabled,
        },
    }

    updated_etalons[driver_for_check]['input_order_id'] = (
        'order_id_' + driver_for_check[-1]
    )

    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [driver_for_check]
    assert not utils.get_driver_events(db)


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {'lat': 16.0, 'lon': 66.0},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'svo_group_id', [None, 'another_group_id', 'test_group_id'],
)
async def test_orders_filter_with_groups(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        svo_group_id,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(ORDERS_FILTER_NAME + '-finished')
    def orders_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 1
        return load_json('candidates.json')

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['group_id'] = 'test_group_id'
    if svo_group_id is not None:
        zones_config['svo']['group_id'] = svo_group_id
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new busy driver (order to svo)

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # orders-filter check
    response = (await orders_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongGroupInputOrder,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [2],
            'classes': CLASSES,
            'input_order_id': 'order_id_1',
        },
    }
    if svo_group_id == 'test_group_id':
        updated_etalons['dbid_uuid1']['state'] = utils.State.kEntered
        updated_etalons['dbid_uuid1']['reason'] = utils.Reason.kOnAction

    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1']
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['drivers_queue_airport_changed_in_same_group.sql'],
)
@pytest.mark.config(DISPATCH_AIRPORT_MERGE_WITH_SAME_AIRPORT_GROUP=True)
async def test_airport_changed_in_same_group(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        mockserver,
        now,
        load_json,
        taxi_config,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(ORDERS_FILTER_NAME + '-finished')
    def orders_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 1
        return load_json('candidates.json')

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['group_id'] = 'test_group_id'
    zones_config['svo']['group_id'] = 'test_group_id'
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - driver entered on action to ekb, now in svo

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.SVO_NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')

    # orders-filter check
    response = (await orders_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'svo',
            'old_mode_enabled': True,
            'areas': [2],
            'classes': ['comfortplus'],
            'input_order_id': 'order_id_1',
        },
    }

    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await utils.wait_certain_testpoint('svo', queue_update_finished)


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_6',
            'taxi_status': 1,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_6',
            'taxi_status': 1,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue_order_from_airport.sql'],
)
@pytest.mark.now('2020-05-01T21:00:00+0000')
async def test_last_time_driver_had_order_from_airport(
        taxi_dispatch_airport,
        testpoint,
        order_archive_mock,
        mockserver,
        load_json,
):
    @testpoint(ORDERS_FILTER_NAME + '-finished')
    def orders_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    order_archive_mock.set_order_proc(
        [
            load_json('order_proc_uuid3.json'),
            load_json('order_proc_uuid4.json'),
            load_json('order_proc_uuid5.json'),
            load_json('order_proc_uuid6.json'),
            load_json('order_proc_uuid7.json'),
            load_json('order_proc_uuid17.json'),
        ],
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - has order, last_time_driver_had_order_from_airport is set
    # dbid_uuid2 - has order,
    #              last_time_driver_had_order_from_airport prolongated
    # dbid_uuid3 - last_time_driver_had_order_from_airport not prolongated
    # dbid_uuid4 - last_time_driver_had_order_from_airport not set

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # orders-filter check
    response = (await orders_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [1, 2],
            'classes': CLASSES,
            'last_time_driver_had_order_from_airport': (
                '2020-05-01T21:00:00+00:00'
            ),
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [1, 2],
            'classes': CLASSES,
            'last_time_driver_had_order_from_airport': (
                '2020-05-01T21:00:00+00:00'
            ),
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [1, 2],
            'classes': CLASSES,
            'last_time_driver_had_order_from_airport': (
                '2020-05-01T19:00:00+00:00'
            ),
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [1, 2],
            'classes': CLASSES,
            'last_time_driver_had_order_from_airport': None,
        },
    }

    utils.check_filter_result(response, updated_etalons)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
