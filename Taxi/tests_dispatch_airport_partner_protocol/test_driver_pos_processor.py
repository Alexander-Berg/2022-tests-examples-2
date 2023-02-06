import datetime

import pytest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'drivers_pos_source, times_called',
    [('edge', 1), ('edge', 4), ('raw', 1), ('raw', 4)],
)
async def test_geobus_connection(
        taxi_dispatch_airport_partner_protocol,
        redis_store,
        testpoint,
        now,
        taxi_config,
        drivers_pos_source,
        times_called,
):
    process_position_name = (
        'geobus_process_' + drivers_pos_source + '_position'
    )
    process_positions_finished_name = (
        'process_' + drivers_pos_source + '_positions_finished'
    )
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_POS_SETTINGS': {
                'source': drivers_pos_source,
            },
        },
    )

    @testpoint(process_position_name)
    def geobus_process_position(data):
        return data

    @testpoint(process_positions_finished_name)
    def process_positions_finished(data):
        return data

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.enable_testpoints()

    geobus_drivers = {'dbid_uuid1': {'position': [14, 9], 'timestamp': now}}
    for _ in range(times_called):
        utils.publish_positions(
            redis_store, geobus_drivers, now, drivers_pos_source == 'edge',
        )
        await process_positions_finished.wait_call()

    assert geobus_process_position.times_called == times_called
    for _ in range(times_called):
        assert geobus_process_position.next_call()['data'] == {
            'pos_source': drivers_pos_source,
            'driver_id': 'dbid_uuid1',
            'latitude': 9.0,
            'longitude': 14.0,
            'time': '2020-02-02T00:00:00+00:00',
        }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize('use_geoareas', [False, True])
@pytest.mark.parametrize('drivers_pos_source', ['edge', 'raw'])
@pytest.mark.parametrize(
    'scenario_name',
    [
        'not_saved_driver/outside_parking_area',
        'not_saved_driver/inside_one_parking_area',
        'not_saved_driver/inside_two_parking_areas',
        'saved_driver/no_track',
        'saved_driver/moved_into_his_parking_area',
        'saved_driver/moved_into_other_parking_area',
        'saved_driver/first_time_moved_from_his_parking_area',
        'saved_driver/completely_moved_from_his_parking_area',
        'saved_driver_in_two_paring_areas/completely_moved_from_parking_area1',
        'saved_driver_in_two_paring_areas/moved_into_two_parking_areas',
        'saved_driver_in_two_paring_areas/moved_from_two_parking_areas',
    ],
)
async def test_pos_processor_process_positions(
        taxi_dispatch_airport_partner_protocol,
        redis_store,
        testpoint,
        load_json,
        now,
        taxi_config,
        drivers_pos_source,
        scenario_name,
        use_geoareas,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-process-finished')
    def process_positions_finished(data):
        return data

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_POS_SETTINGS': {
                'source': drivers_pos_source,
                'outside_limit': 2,
                'inside_limit': 2,
                'max_track_size': 3,
            },
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_GEOAREAS': use_geoareas,
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    data = load_json('process_scenarios/' + scenario_name + '.json')
    positions = load_json('positions.json')
    process_result = []
    for position_name in data['position_names']:
        now += datetime.timedelta(minutes=2)
        geobus_drivers = {
            data['driver_id']: {
                'position': positions[position_name],
                'timestamp': now,
            },
        }
        utils.publish_positions(
            redis_store, geobus_drivers, now, drivers_pos_source == 'edge',
        )
        process_result = (await process_positions_finished.wait_call())['data']
    process_result = sorted(process_result, key=lambda x: x['parking'])
    assert process_result == data['expected_process_result']


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize('drivers_pos_source', ['edge', 'raw'])
@pytest.mark.parametrize(
    'scenario_name',
    [
        'one_parking_lot_diff_drivers',
        'many_parking_areas_one_driver',
        'many_parking_areas_many_drivers',
    ],
)
async def test_pos_processor_merge(
        taxi_dispatch_airport_partner_protocol,
        redis_store,
        testpoint,
        load_json,
        now,
        taxi_config,
        drivers_pos_source,
        scenario_name,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_POS_SETTINGS': {
                'source': drivers_pos_source,
                'outside_limit': 2,
                'inside_limit': 2,
                'max_track_size': 3,
            },
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'driver_pos_processor/clear_merged_drivers',
    )
    data = load_json('merge_scenarios/' + scenario_name + '.json')
    positions = load_json('positions.json')
    process_result = {}
    for position in data['position_name']:
        geobus_drivers = {}
        now += datetime.timedelta(minutes=2)
        for driver_id in data['driver_ids']:
            geobus_drivers[driver_id] = {
                'position': positions[position],
                'timestamp': now,
            }
        utils.publish_positions(
            redis_store, geobus_drivers, now, drivers_pos_source == 'edge',
        )
        process_result = (await merge_finished.wait_call())['data']
    process_result = {
        k: sorted(v, key=lambda x: x['driver_id'])
        for k, v in process_result.items()
    }
    assert process_result == data['expected_merge_result']
