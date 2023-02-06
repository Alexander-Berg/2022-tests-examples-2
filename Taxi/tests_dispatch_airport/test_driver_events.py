import datetime

import pytest

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.parametrize('driver_events_psql_enabled', [False, True])
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid3_uuid3', 'airport_queue_kick_driver_cancel'),
        ('dbid_uuid', 'dbid4_uuid4', 'airport_queue_kick_user_cancel'),
    ],
    topic_relations=[
        ('airport_queue', 'airport_queue_kick_driver_cancel'),
        ('airport_queue', 'airport_queue_kick_user_cancel'),
    ],
)
async def test_driver_events(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
        mode,
        driver_events_psql_enabled,
):
    zones = utils.custom_config(utils.get_old_mode_enabled(mode))
    ekb_zone = zones['DISPATCH_AIRPORT_ZONES']['ekb']
    ekb_zone['new_mode_repeat_queue_forbidden_reasons'] = ['driver_cancel']
    taxi_config.set_values(
        {
            **zones,
            'DISPATCH_AIRPORT_DRIVER_EVENTS_PSQL_ENABLED': (
                driver_events_psql_enabled
            ),
        },
    )
    utils.set_mode_in_config(taxi_config, mode)

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('driver-event-was-inserted')
    def driver_event_was_inserted(_):
        pass

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow cases:
    # udid0 - queued on_action driver with existing entered_on_order event
    # udid1 - new entered_on_repo event
    # udid2 - stored stale entered_on_order event
    # udid3 - new driver event (forbidden filter reason)
    # udid4 - existed driver entered_on_repo event (allowed filter reason)
    # udid5 - queued on_reposition driver with stale entered_on_repo event

    # udid6 - stored stale filtered by forbiden reason event
    # udid6 - udid6 driver entered after forbidden kick

    # udid7 - existing driver event (forbidden filter reason)

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid0_uuid0',
        'dbid1_uuid1',
        'dbid3_uuid3',
        'dbid4_uuid4',
        'dbid5_uuid5',
        'dbid6_uuid6',
    ]

    etalon = {
        ('udid0', 'old_session_id0', 'entered_on_order'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid0_uuid0',
        },
        ('udid2', 'old_session_id2', 'entered_on_order'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid2_uuid2',
        },
        ('udid4', 'old_session_id4', 'entered_on_repo'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid4_uuid4',
        },
        ('udid5', 'old_session_id5', 'entered_on_repo'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid5_uuid5',
        },
        ('udid6', 'old_session_id6', 'filtered_by_forbidden_reason'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid6_uuid6',
        },
        ('udid6', 'new_session_id6', 'entered_on_order'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid6_uuid6',
        },
        ('udid7', 'old_session_id7', 'filtered_by_forbidden_reason'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid7_uuid7',
        },
    }
    if mode != 'old' and driver_events_psql_enabled:
        etalon[('udid1', 'old_session_id1', 'entered_on_repo')] = {
            'airport_id': 'ekb',
            'driver_id': 'dbid1_uuid1',
        }
        etalon[
            (
                'udid3',
                utils.get_driver_session_id(db, 'dbid3_uuid3'),
                'filtered_by_forbidden_reason',
            )
        ] = {'airport_id': 'ekb', 'driver_id': 'dbid3_uuid3'}
    driver_events = utils.get_driver_events(db)
    assert driver_events == etalon

    inserted_called_times = driver_event_was_inserted.times_called
    mocked_time.sleep(10)
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    new_inserted_called_times = driver_event_was_inserted.times_called

    assert inserted_called_times == new_inserted_called_times


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['position_drivers_queue.sql', 'position_driver_events.sql'],
)
@pytest.mark.parametrize('driver_events_psql_enabled', [False, True])
@pytest.mark.tags_v2_index(
    tags_list=[],
    topic_relations=[
        ('airport_queue', 'airport_queue_kick_driver_cancel'),
        ('airport_queue', 'airport_queue_kick_user_cancel'),
    ],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'ekb': {'enter_accumulation_period': 90, 'accounting_timeout': 20},
        'svo': {
            'enter_accumulation_period': 30,
            'accounting_timeout': 20,
            'maximum_events_allowed': 1,
        },
    },
)
@pytest.mark.now('2021-08-19T10:04:00+0000')
async def test_position_events(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
        now,
        redis_store,
        driver_events_psql_enabled,
        load_json,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        airport = request.json['zone_id']
        assert airport in ('ekb_home_zone', 'svo_home_zone')
        return load_json('candidates.json')[airport]

    # dbid_uuid1 - enters for the first time
    # dbid_uuid2 - enters for the second time after the limit
    # dbid_uuid3 - enters for the second time before the limit
    # dbid_uuid4 - enters for the second time after leaving before limit
    # dbid_uuid5 - enters for the second within the limit but
    # into different airport
    # dbid_uuid6 - leaves for the first time
    # dbid_uuid7 - leaves for the second time after the limit
    # dbid_uuid8 - leaves for the second time before the limit
    # dbid_uuid9 - leaves for the second within the limit but
    # from different airport
    # dbid_uuid12 - leaves for the second time after entering
    # dbid_uuid10 - entered too many times, error
    # dbid_uuid11 - left too many times, error
    # dbid_uuid13 - filtered -> filtered, enter doesn't count
    # dbid_uuid14 - no state -> filtered full-queue, enter doesn't count

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['old_mode_enabled'] = False
    zones_config['svo']['old_mode_enabled'] = False
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_ZONES': zones_config,
            'DISPATCH_AIRPORT_DRIVER_EVENTS_PSQL_ENABLED': (
                driver_events_psql_enabled
            ),
        },
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    old_events = utils.get_driver_events(pgsql['dispatch_airport'])
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.OUT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid10': {
            'position': utils.SVO_AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid11': {
            'position': utils.SVO_NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid12': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid13': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid14': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')
    await utils.wait_certain_testpoint('svo', queue_update_finished)

    #  check that all drivers except udid3, udid4, udid8, udid10, udid11
    #  have a new event of entry/leaving
    events = utils.get_driver_events(pgsql['dispatch_airport'])
    assert old_events.items() <= events.items()
    new_events = {
        key: value for key, value in events.items() if key not in old_events
    }
    if not driver_events_psql_enabled:
        assert not new_events
        return
    assert new_events == {
        ('udid1', 'old_session_id1_1629367440', 'entered_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid1',
        },
        ('udid2', 'old_session_id2_1629367440', 'entered_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid2',
        },
        ('udid5', 'old_session_id5_1629367440', 'entered_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid5',
        },
        ('udid6', 'old_session_id6_1629367440', 'left_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid6',
        },
        ('udid7', 'old_session_id7_1629367440', 'left_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid7',
        },
        ('udid9', 'old_session_id9_1629367440', 'left_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid9',
        },
        ('udid12', 'old_session_id12_1629367440', 'left_marked_area'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid12',
        },
    }
    #  after 35 minutes svo events need to be deleted, but not ekb events
    mocked_time.sleep(35 * 60)

    await taxi_dispatch_airport.run_task('distlock/psql-cleaner')
    remaining_events = utils.get_event_session_ids(
        utils.get_driver_events(pgsql['dispatch_airport']),
    )
    assert remaining_events == [
        'old_session_id12_1',
        'old_session_id12_1629367440',
        'old_session_id12_2',
        'old_session_id1_1629367440',
        'old_session_id2_1',
        'old_session_id2_1629367440',
        'old_session_id3_1',
        'old_session_id4_1',
        'old_session_id4_2',
        'old_session_id5_1629367440',
        'old_session_id6_1629367440',
        'old_session_id7_1',
        'old_session_id7_1629367440',
        'old_session_id8_1',
        'old_session_id9_1629367440',
    ]
    #  after 52 more minutes all old events need to be deleted
    mocked_time.sleep(52 * 60)

    await taxi_dispatch_airport.run_task('distlock/psql-cleaner')
    remaining_events = utils.get_event_session_ids(
        utils.get_driver_events(pgsql['dispatch_airport']),
    )
    assert remaining_events == [
        'old_session_id12_1629367440',
        'old_session_id1_1629367440',
        'old_session_id2_1629367440',
        'old_session_id5_1629367440',
        'old_session_id6_1629367440',
        'old_session_id7_1629367440',
        'old_session_id9_1629367440',
    ]

    #  after 5 more minutes database is empty
    mocked_time.sleep(5 * 60)

    await taxi_dispatch_airport.run_task('distlock/psql-cleaner')
    remaining_events = utils.get_event_session_ids(
        utils.get_driver_events(pgsql['dispatch_airport']),
    )
    assert not remaining_events


@pytest.mark.pgsql('dispatch_airport', files=['driver_events_fixed_time.sql'])
async def test_driver_events_cache(taxi_dispatch_airport, load_json):
    response = await taxi_dispatch_airport.get(
        '/internal/driver-events',
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )
    assert response.status_code == 200

    def key(x):
        return (x['udid'], x['event_id'])

    assert sorted(response.json(), key=key) == sorted(
        load_json('cache_etalon.json'), key=key,
    )
