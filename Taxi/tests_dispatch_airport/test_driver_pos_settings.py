import datetime

import pytest

import tests_dispatch_airport.utils as utils

OLD_MODE_REASON_ETALON = {'is_stored_driver_update': False}
DEFAULT_DRIVER_DETAILS = {'in_terminal_area': False}
IN_TERMINAL_DRIVER_DETAILS = {'in_terminal_area': True}


class Context:
    def __init__(
            self,
            taxi_dispatch_airport,
            redis_store,
            cursor,
            mocked_time,
            process_positions_finished,
            merge_finished,
            queue_update_finished,
    ):
        self.service = taxi_dispatch_airport
        self.redis_store = redis_store
        self.cursor = cursor
        self.mocked_time = mocked_time
        self.process_positions_finished = process_positions_finished
        self.merge_finished = merge_finished
        self.update_finished = queue_update_finished


async def iteration(
        context,
        position,
        now_dt,
        expected_processed,
        expected_airport,
        expected_areas,
        expected_etalon=None,
        process_svo=True,
):
    if expected_etalon is None:
        expected_etalon = DEFAULT_DRIVER_DETAILS
    geobus_now = context.mocked_time.now() + datetime.timedelta(seconds=now_dt)
    geobus_drivers = {
        'dbid_uuid1': {'position': position, 'timestamp': geobus_now},
    }
    utils.publish_positions(
        context.redis_store, geobus_drivers, geobus_now, edge=False,
    )

    if expected_processed:
        etalon = {
            'driver_id': 'dbid_uuid1',
            'is_stored_driver_update': True,
            'airport_id': expected_airport,
            'areas': expected_areas,
        }
        if expected_etalon is not None:
            etalon.update(expected_etalon)

        processed_drivers = (
            await context.process_positions_finished.wait_call()
        )['data']
        assert len(processed_drivers) == 1
        utils.check_drivers_pos(processed_drivers[0], etalon)

        merged_response = (await context.merge_finished.wait_call())['data']
        assert len(merged_response[expected_airport]) == 1
        utils.check_drivers_pos(merged_response[expected_airport][0], etalon)

        await context.service.run_task('distlock/queue-update-scheduler-ekb')
        await utils.wait_certain_testpoint('ekb', context.update_finished)
        if process_svo:
            await context.service.run_task(
                'distlock/queue-update-scheduler-svo',
            )
            await utils.wait_certain_testpoint('svo', context.update_finished)

        assert utils.is_driver_exists(
            context.cursor, 'dbid_uuid1', expected_airport,
        )
    else:
        processed_drivers = (
            await context.process_positions_finished.wait_call()
        )['data']
        assert not processed_drivers

    await context.service.invalidate_caches()


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2020-02-02T00:00:00+03:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_POS_SETTINGS={
        'source': 'raw',
        'track_points_ttl': 60,
        'max_track_size': 4,
        'outside_limit': 3,
        'inside_limit': 3,
    },
)
@pytest.mark.parametrize(
    'ekb_out_position', [utils.OUT_POSITION, utils.SVO_WAITING_POSITION],
)
@pytest.mark.parametrize(
    'group_ids',
    [
        {'ekb': None, 'svo': None},
        {'ekb': 'test_group_id', 'svo': None},
        {'ekb': 'test_group_id_1', 'svo': 'test_group_id_2'},
    ],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'ekb': {'marked_area_type': 'terminal'},
    },
)
async def test_driver_pos_settings(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
        ekb_out_position,
        group_ids,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    for airport_id in ('ekb', 'svo'):
        config[airport_id].update(
            {
                'group_id': group_ids[airport_id],
                'terminal_area': 'ekb_airport_waiting',
            },
        )
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: not airport areas
    context = Context(
        taxi_dispatch_airport,
        redis_store,
        pgsql['dispatch_airport'],
        mocked_time,
        process_positions_finished,
        merge_finished,
        queue_update_finished,
    )

    # driver is outside of all airports, no changes
    await iteration(
        context,
        utils.OUT_POSITION,
        1,
        False,
        None,
        None,
        expected_etalon=DEFAULT_DRIVER_DETAILS,
    )
    # driver enters zone
    await iteration(
        context,
        utils.NOTIFICATION_POSITION,
        2,
        True,
        'ekb',
        [2],
        {**OLD_MODE_REASON_ETALON, **DEFAULT_DRIVER_DETAILS},
    )
    # outdates timestamp, ignoring
    await iteration(
        context,
        ekb_out_position,
        1,
        False,
        'ekb',
        [2],
        expected_etalon=DEFAULT_DRIVER_DETAILS,
    )

    # moving to waiting position, but not enough inside points in track
    await iteration(
        context,
        utils.WAITING_POSITION,
        3,
        True,
        'ekb',
        [2],
        expected_etalon=DEFAULT_DRIVER_DETAILS,
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        4,
        True,
        'ekb',
        [2],
        expected_etalon=DEFAULT_DRIVER_DETAILS,
    )
    # finally moved into waiting position
    await iteration(
        context,
        utils.WAITING_POSITION,
        5,
        True,
        'ekb',
        [1, 2],
        expected_etalon=IN_TERMINAL_DRIVER_DETAILS,
    )

    # track should be cleared, so one position clears areas
    mocked_time.sleep(70)
    await taxi_dispatch_airport.invalidate_caches()
    # start again from outside all airports position
    await iteration(
        context,
        utils.OUT_POSITION,
        1,
        True,
        'ekb',
        [],
        {**DEFAULT_DRIVER_DETAILS},
    )

    # track contains only good positions
    await iteration(
        context,
        utils.WAITING_POSITION,
        2,
        True,
        'ekb',
        [],
        {**DEFAULT_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        3,
        True,
        'ekb',
        [],
        {**DEFAULT_DRIVER_DETAILS},
    )
    # two good positions allows to enter area
    await iteration(
        context,
        utils.WAITING_POSITION,
        4,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )

    # one outside position doesn't matter
    await iteration(
        context,
        ekb_out_position,
        5,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )

    # and again only good positions in track
    await iteration(
        context,
        utils.WAITING_POSITION,
        6,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        7,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        8,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )

    # and now two ouside doesn't matter.
    # previous ekb_out_position removed by max_track_size.
    await iteration(
        context,
        ekb_out_position,
        9,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        ekb_out_position,
        10,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )

    # good track again
    await iteration(
        context,
        utils.WAITING_POSITION,
        11,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        12,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        13,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )

    # moving outside airport, but not enough points outside track
    await iteration(
        context,
        ekb_out_position,
        14,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.NOTIFICATION_POSITION,
        15,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    # finally moved from waiting zone
    await iteration(
        context,
        utils.NOTIFICATION_POSITION,
        16,
        True,
        'ekb',
        [2],
        {**DEFAULT_DRIVER_DETAILS},
    )
    await iteration(
        context,
        ekb_out_position,
        17,
        True,
        'ekb',
        [2],
        {**DEFAULT_DRIVER_DETAILS},
    )
    await iteration(
        context,
        ekb_out_position,
        18,
        True,
        'ekb',
        [2],
        {**DEFAULT_DRIVER_DETAILS},
    )
    # finally moved from notification zone
    await iteration(
        context,
        ekb_out_position,
        19,
        True,
        'ekb',
        [],
        {**DEFAULT_DRIVER_DETAILS},
    )

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_POS_SETTINGS': {
                'source': 'raw',
                'track_points_ttl': 60,
                'max_track_size': 4,
                'outside_limit': 2,
                'inside_limit': 1,
            },
        },
    )
    await taxi_dispatch_airport.invalidate_caches()

    # good track again
    await iteration(
        context,
        utils.WAITING_POSITION,
        20,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        21,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        utils.WAITING_POSITION,
        22,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        ekb_out_position,
        23,
        True,
        'ekb',
        [1, 2],
        {**IN_TERMINAL_DRIVER_DETAILS},
    )
    await iteration(
        context,
        ekb_out_position,
        24,
        True,
        'ekb',
        [],
        {**DEFAULT_DRIVER_DETAILS},
    )
    # check that inside_limit is now used when new pos it outside zone
    await iteration(
        context,
        ekb_out_position,
        25,
        True,
        'ekb',
        [],
        {**DEFAULT_DRIVER_DETAILS},
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2020-02-02T00:00:00+03:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_POS_SETTINGS={
        'source': 'raw',
        'track_points_ttl': 60,
        'max_track_size': 4,
        'outside_limit': 3,
        'inside_limit': 3,
    },
    DISPATCH_AIRPORT_FILTER_REMOVED_FROM_CACHE_UPDATES_ENABLED=True,
)
async def test_driver_pos_settings_equal_group_entered_driver(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    for airport_id in ('ekb', 'svo'):
        config[airport_id].update({'group_id': 'test_group_id'})
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: not airport areas
    context = Context(
        taxi_dispatch_airport,
        redis_store,
        pgsql['dispatch_airport'],
        mocked_time,
        process_positions_finished,
        merge_finished,
        queue_update_finished,
    )

    # driver enters 'ekb' zone
    await iteration(
        context,
        utils.NOTIFICATION_POSITION,
        1,
        True,
        'ekb',
        [2],
        OLD_MODE_REASON_ETALON,
    )

    # moving to waiting 'ekb' position, but not enough inside points in track
    await iteration(context, utils.WAITING_POSITION, 2, True, 'ekb', [2])
    await iteration(context, utils.WAITING_POSITION, 3, True, 'ekb', [2])

    # driver move to 'svo' position, discard tracks, update airport
    await iteration(
        context, utils.SVO_NOTIFICATION_POSITION, 4, True, 'svo', [2],
    )
    # not enough inside points in track
    await iteration(context, utils.SVO_WAITING_POSITION, 5, True, 'svo', [2])
    await iteration(context, utils.SVO_WAITING_POSITION, 6, True, 'svo', [2])

    # finally moved into waiting 'ekb' position, driver in queue
    await iteration(context, utils.WAITING_POSITION, 7, True, 'ekb', [1, 2])
    await iteration(context, utils.WAITING_POSITION, 8, True, 'ekb', [1, 2])


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2020-02-02T00:00:00+03:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_POS_SETTINGS={
        'source': 'raw',
        'track_points_ttl': 60,
        'max_track_size': 4,
        'outside_limit': 3,
        'inside_limit': 3,
    },
)
async def test_driver_pos_settings_equal_group_queued_driver(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    for airport_id in ('ekb', 'svo'):
        config[airport_id].update({'group_id': 'test_group_id'})
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: not airport areas
    context = Context(
        taxi_dispatch_airport,
        redis_store,
        pgsql['dispatch_airport'],
        mocked_time,
        process_positions_finished,
        merge_finished,
        queue_update_finished,
    )

    # start from 'ekb' waiting position
    await iteration(
        context,
        utils.WAITING_POSITION,
        1,
        True,
        'ekb',
        [1, 2],
        OLD_MODE_REASON_ETALON,
    )
    await iteration(context, utils.WAITING_POSITION, 2, True, 'ekb', [1, 2])

    # queued driver move to 'svo' position, don't update airport and areas
    await iteration(
        context, utils.SVO_WAITING_POSITION, 3, True, 'ekb', [1, 2],
    )

    # don't update airport, still don't update areas
    await iteration(
        context, utils.SVO_WAITING_POSITION, 4, True, 'ekb', [1, 2],
    )

    # don't update airport, finally update areas
    await iteration(context, utils.SVO_WAITING_POSITION, 5, True, 'ekb', [])

    # and again 'ekb' positions in track
    await iteration(context, utils.WAITING_POSITION, 6, True, 'ekb', [])
    await iteration(context, utils.WAITING_POSITION, 7, True, 'ekb', [])
    # finally in 'ekb' zone again
    await iteration(context, utils.WAITING_POSITION, 8, True, 'ekb', [1, 2])
    await iteration(context, utils.WAITING_POSITION, 9, True, 'ekb', [1, 2])
    await iteration(context, utils.WAITING_POSITION, 10, True, 'ekb', [1, 2])

    # and now two outside of all airports positions, doesn't matter
    await iteration(context, utils.OUT_POSITION, 11, True, 'ekb', [1, 2])
    await iteration(context, utils.OUT_POSITION, 12, True, 'ekb', [1, 2])

    # finally moved from 'ekb' waiting zone
    await iteration(context, utils.OUT_POSITION, 13, True, 'ekb', [])


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2020-02-02T00:00:00+03:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_POS_SETTINGS={
        'source': 'raw',
        'track_points_ttl': 60,
        'max_track_size': 1,
        'outside_limit': 1,
        'inside_limit': 1,
    },
)
async def test_driver_pos_settings_old_data_in_same_group(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    for airport_id in ('ekb', 'svo'):
        config[airport_id].update({'group_id': 'test_group_id'})
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: not airport areas
    context = Context(
        taxi_dispatch_airport,
        redis_store,
        pgsql['dispatch_airport'],
        mocked_time,
        process_positions_finished,
        merge_finished,
        queue_update_finished,
    )

    # at first publish driver pos in SVO, but don't run queue update
    geobus_now = context.mocked_time.now() + datetime.timedelta(seconds=0)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.SVO_WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(
        context.redis_store, geobus_drivers, geobus_now, edge=False,
    )
    processed_drivers = (await context.process_positions_finished.wait_call())[
        'data'
    ]
    assert len(processed_drivers) == 1
    merged_response = (await context.merge_finished.wait_call())['data']
    assert len(merged_response['svo']) == 1

    await taxi_dispatch_airport.run_task('driver_pos_processor/clear_state')

    # now publish driver in EKB and run queue update only for EKB
    await iteration(
        context,
        utils.WAITING_POSITION,
        1,
        True,
        'ekb',
        [1, 2],
        OLD_MODE_REASON_ETALON,
        process_svo=False,
    )

    @testpoint('candidates-filter-finished')
    def candidates_filter_finished(data):
        return data

    # now process svo, merged data from previosly published
    # svo positions should be ignored
    await context.service.run_task('distlock/queue-update-scheduler-svo')
    await utils.wait_certain_testpoint('svo', context.update_finished)
    candidates_filter_result = await candidates_filter_finished.wait_call()
    assert candidates_filter_result['data'] == []


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2021-01-01T00:00:00+00:00')
@pytest.mark.config(DISPATCH_AIRPORT_MERGE_WITH_SAME_AIRPORT_GROUP=True)
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['drivers_queue_change_airport_for_queued_driver.sql'],
)
async def test_driver_pos_change_airport_for_queued_driver_in_same_group(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        taxi_config,
):
    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    for airport_id in ('ekb', 'svo'):
        config[airport_id].update({'group_id': 'test_group_id'})
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('candidates-filter-finished')
    def candidates_filter_finished(data):
        return data

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # dbid_uuid1 - stored entered driver in ekb

    # at first publish driver pos in SVO, but don't run queue update
    geobus_now = mocked_time.now() + datetime.timedelta(seconds=5)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.SVO_WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, geobus_now, edge=True)
    processed_drivers = (await process_positions_finished.wait_call())['data']
    assert len(processed_drivers) == 1
    merged_response = (await merge_finished.wait_call())['data']
    # check that driver airport is changed to svo
    assert merged_response['svo'] == [
        {
            'airport_id': 'svo',
            'areas': [1, 2],
            'driver_id': 'dbid_uuid1',
            'heartbeated': '2021-01-01T00:00:05+00:00',
            'in_terminal_area': False,
            'is_stored_driver_update': True,
            'lat': 11.0,
            'lon': 61.0,
        },
    ]

    # emulate that on other instance driver was queued
    cursor = pgsql['dispatch_airport'].cursor()
    cursor.execute(
        f"""
      UPDATE dispatch_airport.drivers_queue
      SET state='queued';""",
    )
    await taxi_dispatch_airport.invalidate_caches()

    # now process svo, queued driver should be ignored
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')
    await utils.wait_certain_testpoint('svo', queue_update_finished)
    candidates_filter_result = await candidates_filter_finished.wait_call()
    assert candidates_filter_result['data'] == []
