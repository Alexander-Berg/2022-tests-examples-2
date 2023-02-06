import datetime

import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize('drivers_pos_source', ['edge', 'raw'])
async def test_driver_pos_processor(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        now,
        pgsql,
        mockserver,
        taxi_config,
        drivers_pos_source,
):
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
        append = request.json['append'][0]
        remove = request.json['remove'][0]
        utils.check_airport_tags(append, ('dbid_uuid6',), ('dbid_uuid2',))
        utils.check_airport_tags(
            remove, (), ('dbid_uuid3', 'dbid_uuid4', 'dbid_uuid6'),
        )
        return {}

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_POS_SETTINGS': {
                'source': drivers_pos_source,
            },
        },
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: not airport areas
    # dbid_uuid2 - new driver: notification zone
    # dbid_uuid3 - stored driver (wrong heartbeated)
    # dbid_uuid4 - stored driver (not airport areas)
    # dbid_uuid5 - stored driver (another airport, notification zone)
    # dbid_uuid6 - stored driver (waiting zone)

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.OUT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now - datetime.timedelta(minutes=3),
        },
        'dbid_uuid4': {
            'position': utils.OUT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(
        redis_store, geobus_drivers, now, drivers_pos_source == 'edge',
    )

    # driver-pos-processor geobus process check
    processed_drivers = (await process_positions_finished.wait_call())['data']
    etalons_ekb = {
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'is_stored_driver_update': False,
            'airport_id': 'ekb',
            'areas': [2],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'is_stored_driver_update': True,
            'airport_id': 'ekb',
            'areas': [],
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'is_stored_driver_update': True,
            'airport_id': 'ekb',
            'areas': [1, 2],
        },
    }
    etalons_another_airport = {
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'is_stored_driver_update': True,
            'airport_id': 'another_airport',
            'areas': [],
        },
    }
    etalons = {**etalons_ekb, **etalons_another_airport}
    assert len(processed_drivers) == len(etalons)
    for driver in processed_drivers:
        etalon = etalons[driver['driver_id']]
        utils.check_drivers_pos(driver, etalon)

    # driver-pos-processor merge check
    merged_response = (await merge_finished.wait_call())['data']
    assert len(merged_response['ekb']) == len(etalons_ekb)
    for driver in merged_response['ekb']:
        etalon = etalons_ekb[driver['driver_id']]
        utils.check_drivers_pos(driver, etalon)

    assert len(merged_response['another_airport']) == len(
        etalons_another_airport,
    )
    for driver in merged_response['another_airport']:
        etalon = etalons_another_airport[driver['driver_id']]
        utils.check_drivers_pos(driver, etalon)

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    drivers = utils.get_drivers_queue(pgsql['dispatch_airport'])
    assert drivers == [
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
    ]


@pytest.mark.geoareas(filename='geoareas_intersecting.json')
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['driver_events.sql', 'drivers_queue_for_intersecting_test.sql'],
)
@pytest.mark.parametrize('check_in_airport', ['ekb', 'svo'])
@pytest.mark.parametrize(
    'use_partner_parking_for_airport_selection', [True, False],
)
async def test_driver_pos_processor_with_intersecting_geoareas(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        now,
        taxi_config,
        mockserver,
        check_in_airport,
        use_partner_parking_for_airport_selection,
):
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

    @mockserver.json_handler(
        '/dispatch-airport-partner-protocol/service/v2/parked_drivers',
    )
    def _dapp_parked_drivers(request):
        assert request.json.get('parking_id') == check_in_airport
        if check_in_airport == 'ekb':
            return {
                'drivers': [
                    {
                        'driver_id': 'dbid_uuid3',
                        'arrived_at': '2020-10-02T10:36:36+0000',
                    },
                ],
            }

        return {
            'drivers': [
                {
                    'driver_id': 'dbid_uuid4',
                    'arrived_at': '2020-10-02T10:36:36+0000',
                },
                {
                    'driver_id': 'dbid_uuid5',
                    'arrived_at': '2020-10-02T10:36:36+0000',
                },
                {
                    'driver_id': 'dbid_uuid6',
                    'arrived_at': '2020-10-02T10:36:36+0000',
                },
            ],
        }

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config[check_in_airport]['distributive_zone_type'] = 'check_in'
    zones_config[check_in_airport]['partner_parking_id'] = check_in_airport
    zones_config[check_in_airport]['partner_parking_check_enabled'] = True
    zones_config[check_in_airport][
        'use_partner_parking_for_airport_selection'
    ] = use_partner_parking_for_airport_selection
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - outside ekb and svo
    # dbid_uuid2 - only in ekb
    # dbid_uuid3 - both ekb and svo, repo offer to ekb
    # dbid_uuid4 - both ekb and svo, repo offer to svo, svo areas [1, 2]
    # dbid_uuid5 - both ekb and svo, repo offer to svo, svo areas [0, 1, 2]
    # dbid_uuid6 - only in ekb, repo offer to svo (repo shouldn't matter)
    # dbid_uuid7 - both ekb and svo, no repo -> expected non check_in airport
    # dbid_uuid8 - stored driver, was in ekb, new pos in both ekb and svo
    # dbid_uuid9 - stored driver, was in svo, new pos in both ekb and svo

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.OUT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': [29, 19],  # lies inside both airports, except svo main
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': [29, 19],  # lies inside both airports, except svo main
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': [31.5, 18.5],  # inside both airports and all svo areas
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.AIRPORT_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': [31.5, 18.5],  # inside both airports and all svo areas
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': [31.5, 18.5],  # inside both airports and all svo areas
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': [31.5, 18.5],  # inside both airports and all svo areas
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)

    # driver-pos-processor geobus process check
    processed_drivers = (await process_positions_finished.wait_call())['data']
    etalons = {
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'is_stored_driver_update': False,
            'airport_id': 'ekb',
            'areas': [0, 1, 2],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'is_stored_driver_update': False,
            'airport_id': 'ekb',
            'areas': [0, 1, 2],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'is_stored_driver_update': False,
            'airport_id': 'svo',
            'areas': (
                [0, 1, 2]
                if use_partner_parking_for_airport_selection
                and check_in_airport == 'svo'
                else [1, 2]
            ),
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'is_stored_driver_update': False,
            'airport_id': 'svo',
            'areas': [0, 1, 2],
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'is_stored_driver_update': False,
            'airport_id': (
                'svo'
                if use_partner_parking_for_airport_selection
                and check_in_airport == 'svo'
                else 'ekb'
            ),
            'areas': [0, 1, 2],
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'is_stored_driver_update': False,
            'airport_id': 'ekb' if check_in_airport == 'svo' else 'svo',
            'areas': [0, 1, 2],
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'is_stored_driver_update': True,
            'airport_id': 'ekb',
            # Stored driver was in ekb.
            # If use_partner_parking_for_airport_selection then other airport
            # should be selected because driver is not on parking,
            # so areas are cleared
            'areas': (
                []
                if use_partner_parking_for_airport_selection
                and check_in_airport == 'ekb'
                else [0, 1, 2]
            ),
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'is_stored_driver_update': True,
            'airport_id': 'svo',
            # Stored driver was in svo.
            # If use_partner_parking_for_airport_selection then other airport
            # should be selected because driver is not on parking,
            # so areas are cleared
            'areas': (
                []
                if use_partner_parking_for_airport_selection
                and check_in_airport == 'svo'
                else [0, 1, 2]
            ),
        },
    }

    assert len(processed_drivers) == len(etalons)
    for driver in processed_drivers:
        etalon = etalons[driver['driver_id']]
        utils.check_drivers_pos(driver, etalon)

    # run queue update to remove unprocessed points from cache
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')
    await utils.wait_certain_testpoint('svo', queue_update_finished)


@pytest.mark.now('2021-01-01T10:00:00+00:00')
@pytest.mark.geoareas(filename='geoareas_terminal.json')
@pytest.mark.parametrize(
    'zone, terminal',
    [
        ('ekb', 'ekb_airport'),  # terminal area = airport
        ('ekb', None),  # terminal area is not set in DISPATCH_AIRPORT_ZONES
        ('svo', 'svo_airport_toll_area'),  # special terminal area
    ],
)
@pytest.mark.parametrize('max_track_size', [1, 2])
@pytest.mark.parametrize('drivers_pos_source', ['edge'])
@pytest.mark.config(
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'ekb': {'marked_area_type': 'terminal'},
        'svo': {'marked_area_type': 'terminal'},
    },
)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue_terminal.sql'])
async def test_process_terminal_area(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        now,
        pgsql,
        mockserver,
        taxi_config,
        drivers_pos_source,
        zone,
        terminal,
        max_track_size,
):
    settings = {
        'ekb': {
            'terminal_position': utils.AIRPORT_POSITION,
            'not_terminal_position': utils.NOTIFICATION_POSITION,
            'terminal_areas': [0, 1, 2],
            'not_terminal_areas': [2],
        },
        'svo': {
            'terminal_position': [84, 6],
            'not_terminal_position': utils.SVO_NOTIFICATION_POSITION,
            'terminal_areas': [2],
            'not_terminal_areas': [2],
        },
    }

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

    async def process_point(driver_movement, zone, geobus_now):
        geobus_drivers = {
            driver_id: {
                'position': (
                    settings[zone]['terminal_position']
                    if driver_movement[driver_id]['point_is_inside']
                    else settings[zone]['not_terminal_position']
                ),
                'timestamp': geobus_now,
            }
            for driver_id in driver_movement
        }
        etalons = {
            driver_id: {
                'driver_id': driver_id,
                'is_stored_driver_update': driver_id in (
                    'dbid_uuid2',
                    'dbid_uuid3',
                    'dbid_uuid4',
                ),
                'airport_id': zone,
                'areas': (
                    settings[zone]['terminal_areas']
                    if driver_movement[driver_id]['driver_is_inside']
                    else settings[zone]['not_terminal_areas']
                ),
                'lon': geobus_drivers[driver_id]['position'][0],
                'lat': geobus_drivers[driver_id]['position'][1],
                'in_terminal_area': driver_movement[driver_id][
                    'driver_is_inside'
                ],
            }
            for driver_id in driver_movement
        }

        utils.publish_positions(
            redis_store, geobus_drivers, now, drivers_pos_source == 'edge',
        )
        processed_drivers = (await process_positions_finished.wait_call())[
            'data'
        ]
        assert {
            driver['driver_id'] for driver in processed_drivers
        } == driver_movement.keys()
        for driver in processed_drivers:
            if terminal:
                utils.check_drivers_pos(driver, etalons[driver['driver_id']])
            else:
                assert driver['in_terminal_area'] is False
        await merge_finished.wait_call()

    # ekb - terminal is ekb_airport, inside waiting and notification
    # svo - terminal crosses notification, outside of all other
    # dbid_uuid1 - new driver: entered terminal zone
    # dbid_uuid2 - stored driver entered terminal area
    # dbid_uuid3 - stored driver left terminal area
    # dbid_uuid4 - stored driver out of terminal area gps flickered

    cursor = pgsql['dispatch_airport'].cursor()
    cursor.execute(
        f"""
      UPDATE dispatch_airport.drivers_queue
      SET airport='{zone}';""",
    )

    if terminal:
        zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
        zones_config[zone]['terminal_area'] = terminal
        taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_POS_SETTINGS': {
                'source': drivers_pos_source,
                'max_track_size': max_track_size,
            },
        },
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()
    initial_track = {
        'dbid_uuid2': {
            'position': settings[zone]['not_terminal_position'],
            'timestamp': now + datetime.timedelta(seconds=5),
        },
        'dbid_uuid3': {
            'position': settings[zone]['terminal_position'],
            'timestamp': now + datetime.timedelta(seconds=5),
        },
        'dbid_uuid4': {
            'position': settings[zone]['not_terminal_position'],
            'timestamp': now + datetime.timedelta(seconds=5),
        },
    }
    utils.publish_positions(
        redis_store,
        initial_track,
        now + datetime.timedelta(seconds=5),
        drivers_pos_source == 'edge',
    )
    await process_positions_finished.wait_call()
    await merge_finished.wait_call()

    ids = ['dbid_uuid1', 'dbid_uuid2', 'dbid_uuid3', 'dbid_uuid4']
    await process_point(
        {
            driver_id: {
                'point_is_inside': driver_id != 'dbid_uuid3',
                'driver_is_inside': terminal and (
                    ((max_track_size > 1) is (driver_id == 'dbid_uuid3'))
                    or driver_id == 'dbid_uuid1'
                ),
            }
            for driver_id in ids
        },
        zone,
        now + datetime.timedelta(seconds=10),
    )
    if max_track_size > 1:
        await process_point(
            {
                driver_id: {
                    'point_is_inside': driver_id in [
                        'dbid_uuid1',
                        'dbid_uuid2',
                    ],
                    'driver_is_inside': driver_id in [
                        'dbid_uuid1',
                        'dbid_uuid2',
                    ],
                }
                for driver_id in ids
            },
            zone,
            now + datetime.timedelta(seconds=20),
        )

    await taxi_dispatch_airport.run_task(
        'distlock/queue-update-scheduler-' + zone,
    )
    await utils.wait_certain_testpoint(zone, queue_update_finished)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue_skip_old_merged_pos.sql'],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_FILTER_REMOVED_FROM_CACHE_UPDATES_ENABLED=True,
)
async def test_driver_pos_processor_skip_old_merged_pos(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # at first publish driver pos in SVO, but don't run queue update
    geobus_now = mocked_time.now() + datetime.timedelta(seconds=5)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.SVO_WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, geobus_now)
    processed_drivers = (await process_positions_finished.wait_call())['data']
    assert len(processed_drivers) == 1
    merged_response = (await merge_finished.wait_call())['data']
    assert len(merged_response['svo']) == 1

    # emulate driver is filtered and removed from db by other instance
    cursor = pgsql['dispatch_airport'].cursor()
    cursor.execute('DELETE FROM dispatch_airport.drivers_queue;')
    await taxi_dispatch_airport.invalidate_caches()

    # run queue update -> saved merged pos should not be used
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')
    await queue_update_finished.wait_call()

    db_drivers = utils.get_drivers_queue(pgsql['dispatch_airport'])
    assert not db_drivers


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['drivers_queue_airport_changed_in_same_group.sql'],
)
async def test_airport_changed_in_same_group(
        taxi_dispatch_airport, redis_store, testpoint, now, taxi_config,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['group_id'] = 'test_group_id'
    zones_config['svo']['group_id'] = 'test_group_id'
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # airport should be changed only for driver dbid_uuid1
    # dbid_uuid1 - entered ekb driver
    # dbid_uuid2 - queued ekb driver
    # dbid_uuid3 - filtered ekb driver

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.SVO_NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.SVO_NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.SVO_NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    merged_response = (await merge_finished.wait_call())['data']

    assert len(merged_response['svo']) == 1
    assert merged_response['svo'][0]['driver_id'] == 'dbid_uuid1'
    assert len(merged_response['ekb']) == 2
