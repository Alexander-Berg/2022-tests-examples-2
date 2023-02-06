import datetime

import pytest

import tests_dispatch_airport_partner_protocol.utils as utils

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

VEHICLE_BINDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid_uuid1',
            'data': {'car_id': 'car_id1'},
        },
    ],
}

VEHICLE_BINDING_FULL_BRANDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle2'},
        },
    ],
}


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'ttl, time_passed, should_be_empty',
    [(5, 1, False), (5, 10, True), (5, 5, False), (5, 6, True)],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_clean_old_drivers(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        mocked_time,
        taxi_config,
        load_json,
        ttl,
        time_passed,
        should_be_empty,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': ttl,
        },
    )

    init_val = await utils.get_sorted_db_drivers(pgsql)
    mocked_time.sleep(time_passed)
    await taxi_dispatch_airport_partner_protocol.run_task(
        'driver_pos_processor/clear_merged_drivers',
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot2',
    )
    if should_be_empty:
        assert await utils.get_sorted_db_drivers(pgsql) == []
    else:
        await utils.compare_db_with_expected(
            pgsql,
            init_val,
            ['driver_id', 'heartbeated', 'parking_id', 'on_parking_lot'],
        )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_not_replace_with_old_data(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        redis_store,
        testpoint,
        now,
        taxi_config,
        load_json,
):
    def set_parking_driver_heartbeated(
            pgsql, driver_id, parking_id, new_heartbeated,
    ):
        cursor = pgsql['dispatch_airport_partner_protocol'].cursor()
        cursor.execute(
            f"""
                UPDATE dispatch_airport_partner_protocol.parking_drivers
                SET heartbeated = '{new_heartbeated}'
                WHERE driver_id = '{driver_id}' and parking_id='{parking_id}';
            """,
        )

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 600,
        },
    )

    positions = load_json('positions.json')

    # dbid_uuid1 - driver heartbeated is newer than heartbeated from
    # geoubus updates and should not be stored in db
    # dbid_uuid3 - driver heartbeated is older than heartbeated from
    # geoubus updates and should be stored in db

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    new_heartbeated = (now + datetime.timedelta(minutes=3)).strftime(
        format=DATETIME_FORMAT,
    )
    set_parking_driver_heartbeated(
        pgsql, 'dbid_uuid1', 'parking_lot1', new_heartbeated,
    )

    geobus_drivers = {
        'dbid_uuid1': {
            'position': positions['inside_parking_lot1'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
        'dbid_uuid2': {
            'position': positions['outside_all_parking_areas'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
        'dbid_uuid3': {
            'position': positions['inside_parking_lot1'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now, True)
    await merge_finished.wait_call()

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot2',
    )

    expected_result = load_json(
        'expected_db_data/not_replace_with_old_data.json',
    )
    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        ['driver_id', 'heartbeated', 'parking_id', 'on_parking_lot'],
    )


@pytest.mark.parametrize('add_into_empty_db', [True, False])
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_add_new_drivers(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        redis_store,
        testpoint,
        mocked_time,
        now,
        taxi_config,
        load_json,
        add_into_empty_db,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 4,
        },
    )

    positions = load_json('positions.json')
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    if add_into_empty_db:
        # clean db
        mocked_time.sleep(5)
        await taxi_dispatch_airport_partner_protocol.run_task(
            'distlock/parking_drivers-update-scheduler-parking_lot1',
        )
        await taxi_dispatch_airport_partner_protocol.run_task(
            'distlock/parking_drivers-update-scheduler-parking_lot2',
        )
        result = await utils.get_sorted_db_drivers(pgsql)
        assert result == []

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    # dbid_uuid4 - new, driver-profiles has car_id for this driver
    # dbid_uuid5 - new, outside parking areas, will not be added
    # dbid_uuid6 - new, no info in driver-profiles, will be added
    # dbid_uuid7 - new, driver-profiles has car_id for this driver
    # dbid_uuid1 - old, has car_id in db
    # dbid_uuid(2-3) - old, has no car_id in db
    geobus_drivers = {
        'dbid_uuid4': {
            'position': positions['inside_parking_lot1'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
        'dbid_uuid5': {
            'position': positions['outside_all_parking_areas'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
        'dbid_uuid6': {
            'position': positions['inside_parking_lot2'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
        'dbid_uuid7': {
            'position': positions['inside_parking_lot1_and_parking_lot2'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now, True)
    await merge_finished.wait_call()

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot2',
    )
    expected_result = load_json('expected_db_data/add_new_drivers.json')[
        'empty_db' if add_into_empty_db else 'not_empty_db'
    ]
    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        ['driver_id', 'heartbeated', 'parking_id', 'on_parking_lot', 'car_id'],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_drivers_are_updated(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        redis_store,
        testpoint,
        mocked_time,
        now,
        taxi_config,
        load_json,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 4,
        },
    )

    positions = load_json('positions.json')
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    geobus_drivers = {
        'dbid_uuid1': {
            'position': positions['inside_parking_lot1'],
            'timestamp': now + datetime.timedelta(minutes=2),
        },
        'dbid_uuid2': {
            'position': positions['inside_parking_lot2'],
            'timestamp': now + datetime.timedelta(minutes=3),
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now, True)
    await merge_finished.wait_call()
    mocked_time.sleep(2)
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot2',
    )
    expected_result = load_json('expected_db_data/drivers_are_updated.json')
    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        ['driver_id', 'heartbeated', 'parking_id', 'on_parking_lot'],
    )


@pytest.mark.parametrize('add_into_empty_db', [True, False])
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_delete_left_driver(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        redis_store,
        testpoint,
        mocked_time,
        now,
        taxi_config,
        load_json,
        add_into_empty_db,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 4,
        },
    )

    # dbid_uuid1 - left zone, should be erased from db
    # dbid_uuid2 - stays on parking lot 2, should not be erased
    # dbid_uuid3 - stays on parking lot 1, should be deleted from
    # parking lot 2
    positions = load_json('positions.json')
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    geobus_drivers = {
        'dbid_uuid1': {
            'position': positions['outside_all_parking_areas'],
            'timestamp': now + datetime.timedelta(minutes=2),
        },
        'dbid_uuid2': {
            'position': positions['inside_parking_lot2'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
        'dbid_uuid3': {
            'position': positions['inside_parking_lot1'],
            'timestamp': now + datetime.timedelta(minutes=3),
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now, True)
    await merge_finished.wait_call()
    mocked_time.sleep(3)
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot2',
    )

    expected_result = load_json('expected_db_data/delete_left_driver.json')
    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        ['driver_id', 'heartbeated', 'parking_id', 'on_parking_lot'],
    )


@pytest.mark.parametrize(
    'parking_lot, expected_ids',
    [
        ('parking_lot1', ['dbid_uuid3']),
        ('parking_lot2', ['dbid_uuid2', 'dbid_uuid3', 'dbid_uuid4']),
        ('parking_lot3', []),
    ],
)
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_request_car_id_check.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_request_ids_for_driver_profiles(
        taxi_dispatch_airport_partner_protocol,
        mockserver,
        taxi_config,
        load_json,
        parking_lot,
        expected_ids,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        if not expected_ids:
            assert False
        assert sorted(request.json['id_in_set']) == expected_ids
        return utils.form_driver_profile_response(
            request, load_json('driver_profiles.json'),
        )

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 4,
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-' + parking_lot,
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_profiles.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_allowed_providers_update(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        pgsql,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        return utils.form_driver_profile_response(
            request, load_json('expected_allowed_providers_result.json'),
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(request):
        assert len(request.json['profile_id_in_set']) == 3

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_CHECK_ALLOWED_PROVIDERS': True,
        },
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )

    expected_results = [
        {'driver_id': 'dbid_uuid1', 'has_allowed_provider': True},
        {'driver_id': 'dbid_uuid2', 'has_allowed_provider': True},
        {'driver_id': 'dbid_uuid3', 'has_allowed_provider': False},
        {'driver_id': 'dbid_uuid4', 'has_allowed_provider': None},
    ]

    await utils.compare_db_with_expected(
        pgsql, expected_results, ['driver_id', 'has_allowed_provider'],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_unique_drivers.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_unique_drivers_update(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        mockserver,
        taxi_config,
        load_json,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(request):
        assert sorted(request.json['profile_id_in_set']) == [
            'dbid_uuid2',
            'dbid_uuid3',
        ]
        return utils.form_unique_drivers_response(
            request, load_json('unique_drivers.json'),
        )

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )

    expected_results = [
        {
            'driver_id': 'dbid_uuid1',
            'unique_driver_id': '60c9ccf18fe28d5ce431ce88',
        },
        {
            'driver_id': 'dbid_uuid2',
            'unique_driver_id': '60c9ccf18fe28d5ce431ce88',
        },
        {'driver_id': 'dbid_uuid3', 'unique_driver_id': None},
    ]

    await utils.compare_db_with_expected(
        pgsql, expected_results, ['driver_id', 'unique_driver_id'],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_dispatch_airport.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_dispatch_airport_update(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        mockserver,
        taxi_config,
        load_json,
):
    @mockserver.json_handler('/dispatch-airport/v1/partner_drivers_info')
    def _partners_drivers_info(request):
        driver_ids = [x['dbid_uuid'] for x in request.json['driver_ids']]
        assert sorted(driver_ids) == [
            'dbid_uuid1',
            'dbid_uuid2',
            'dbid_uuid3',
            'dbid_uuid4',
            'dbid_uuid5',
        ]
        return utils.form_partner_drivers_response(
            request, load_json('partner_drivers_info.json'),
        )

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )

    expected_results = load_json('expected_dispatch_airport_result.json')

    await utils.compare_db_with_expected(
        pgsql,
        expected_results,
        [
            'driver_id',
            'dispatch_airport_filter_reason',
            'dispatch_airport_times_queued',
            'dispatch_airport_partner_parking_id',
        ],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_fleet_vehicles.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_fleet_vehicles_update(
        taxi_dispatch_airport_partner_protocol,
        mockserver,
        pgsql,
        taxi_config,
        load_json,
):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _fleet_vehicles(request):
        assert request.json['id_in_set'] == ['dbid2_car_id2', 'dbid3_car_id3']
        assert request.json['projection'] == [
            'data.number',
            'data.number_normalized',
            'data.year',
            'data.model',
            'data.brand',
            'data.color',
        ]
        return utils.form_fleet_vehicles_response(
            request, load_json('fleet_vehicles.json'),
        )

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    expected_result = load_json('expected_fleet_vehicles_result.json')
    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        [
            'driver_id',
            'car_number',
            'car_number_normalized',
            'year',
            'model',
            'mark',
            'color',
        ],
    )


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_store_positions.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_store_positions_to_db(
        taxi_dispatch_airport_partner_protocol,
        pgsql,
        redis_store,
        testpoint,
        now,
        taxi_config,
        load_json,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_PSQL_PARKING_DRIVER_TTL': 600,
        },
    )
    positions = load_json('positions.json')
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    geobus_drivers = {
        'dbid_uuid1': {
            'position': positions['inside_parking_lot1'],
            'timestamp': now + datetime.timedelta(minutes=1),
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now, True)
    await merge_finished.wait_call()

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )

    expected_result = load_json('expected_db_data/positions_update.json')
    await utils.compare_db_with_expected(
        pgsql, expected_result, ['driver_id', 'latitude', 'longitude'],
    )


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_FORBIDDEN_TAGS=[
        {'reason': 'blacklist', 'tags': ['airport_queue_blacklist_driver']},
        {
            'reason': 'anti_fraud_tag',
            'tags': [
                'airport_queue_fraud_detected',
                'airport_queue_fraud_detected_short',
                'airport_queue_fraud_detected_long',
            ],
        },
    ],
)
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_dispatch_airport.sql'],
)
async def test_driver_tags_update(
        taxi_dispatch_airport_partner_protocol,
        mockserver,
        pgsql,
        taxi_config,
        load_json,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _driver_tags(http_request):
        assert http_request.json == {
            'drivers': [
                {'dbid': 'dbid', 'uuid': 'uuid3'},
                {'dbid': 'dbid', 'uuid': 'uuid1'},
                {'dbid': 'dbid', 'uuid': 'uuid2'},
                {'dbid': 'dbid', 'uuid': 'uuid4'},
                {'dbid': 'dbid', 'uuid': 'uuid5'},
            ],
        }
        return mockserver.make_response(
            json={
                'drivers': [
                    {
                        'dbid': 'dbid',
                        'uuid': 'uuid1',
                        'tags': ['airport_queue_ok'],
                    },
                    {
                        'dbid': 'dbid',
                        'uuid': 'uuid2',
                        'tags': ['airport_queue_fraud_detected'],
                    },
                    {
                        'dbid': 'dbid',
                        'uuid': 'uuid3',
                        'tags': ['airport_queue_fraud_detected_long'],
                    },
                    {
                        'dbid': 'dbid',
                        'uuid': 'uuid4',
                        'tags': ['airport_queue_blacklist_driver'],
                    },
                ],
            },
        )

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    expected_result = load_json('expected_driver_tags_result.json')
    await utils.compare_db_with_expected(
        pgsql, expected_result, ['driver_id', 'tags_block_reason'],
    )


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_dispatch_airport.sql'],
)
@pytest.mark.parametrize('use_stq_scheduler', [True, False])
async def test_key_lock_scheduler(
        taxi_dispatch_airport_partner_protocol,
        testpoint,
        taxi_config,
        load_json,
        use_stq_scheduler,
        mocked_time,
):
    @testpoint('parking-drivers-update-finished')
    def parking_drivers_update(data):
        return data

    @testpoint('started_key_lock_tasks')
    def started_key_lock_tasks(data):
        return data

    @testpoint('key_lock_tasks_disabled')
    def key_lock_tasks_disabled(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_STQ_SCHEDULER': (
                use_stq_scheduler
            ),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_'
            'PARKING_DRIVERS_UPDATE_ENABLED': True,
        },
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.enable_testpoints()

    await taxi_dispatch_airport_partner_protocol.run_task(
        'start-key-lock-scheduler',
    )

    if use_stq_scheduler:
        await key_lock_tasks_disabled.wait_call()
    else:
        await started_key_lock_tasks.wait_call()

    await taxi_dispatch_airport_partner_protocol.run_task(
        'stop-key-lock-scheduler',
    )

    if use_stq_scheduler:
        assert parking_drivers_update.times_called == 0
    else:
        assert parking_drivers_update.times_called == 3
        assert sorted(
            [parking_drivers_update.next_call()['data'] for _ in range(3)],
        ) == ['parking_lot1', 'parking_lot2', 'parking_lot3']


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_dispatch_airport.sql'],
)
@pytest.mark.parametrize('use_stq_scheduler', [True, False])
async def test_stq_scheduler(
        taxi_dispatch_airport_partner_protocol,
        testpoint,
        taxi_config,
        load_json,
        use_stq_scheduler,
        stq,
        stq_runner,
):
    @testpoint('parking-drivers-update-finished')
    def parking_drivers_update(data):
        return data

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_STQ_SCHEDULER': (
                use_stq_scheduler
            ),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_'
            'PARKING_DRIVERS_UPDATE_ENABLED': True,
        },
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.enable_testpoints()

    queue = (
        stq_runner.dispatch_airport_partner_protocol_airport_drivers_processing
    )
    await taxi_dispatch_airport_partner_protocol.run_task('watchdog')
    queue_point = (
        stq.dispatch_airport_partner_protocol_airport_drivers_processing
    )
    assert queue_point.times_called == 3
    tasks = [queue_point.next_call() for _ in range(3)]

    for task in tasks:
        # workaround for testsuite reschedule
        if task['kwargs'] is not None:
            task['kwargs'].pop('log_extra')

    tasks = sorted(tasks, key=lambda x: x['id'])
    assert tasks == [
        {
            'queue': (
                'dispatch_airport_partner_protocol_airport_drivers_processing'
            ),
            'id': 'parking_lot1',
            'args': [],
            'kwargs': {},
            'eta': datetime.datetime(2020, 2, 2, 0, 0, 3),
        },
        {
            'queue': (
                'dispatch_airport_partner_protocol_airport_drivers_processing'
            ),
            'id': 'parking_lot2',
            'args': [],
            'kwargs': {},
            'eta': datetime.datetime(2020, 2, 2, 0, 0, 3),
        },
        {
            'queue': (
                'dispatch_airport_partner_protocol_airport_drivers_processing'
            ),
            'id': 'parking_lot3',
            'args': [],
            'kwargs': {},
            'eta': datetime.datetime(2020, 2, 2, 0, 0, 3),
        },
    ]

    for task in tasks:
        await queue.call(task_id=task['id'], kwargs=task['kwargs'])

    if not use_stq_scheduler:
        assert parking_drivers_update.times_called == 0
    else:
        assert parking_drivers_update.times_called == 3
        assert sorted(
            [parking_drivers_update.next_call()['data'] for _ in range(3)],
        ) == ['parking_lot1', 'parking_lot2', 'parking_lot3']


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_profiles.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_parking_drivers_metrics(
        taxi_dispatch_airport_partner_protocol,
        taxi_dispatch_airport_partner_protocol_monitor,
        taxi_config,
        load_json,
        mocked_time,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )

    mocked_time.sleep(15)
    await taxi_dispatch_airport_partner_protocol.tests_control(
        invalidate_caches=False,
    )
    metrics = await taxi_dispatch_airport_partner_protocol_monitor.get_metric(
        'dispatch_airport_partner_protocol_metrics',
    )

    assert metrics['driver_count']['parking_lot1'] == 4
