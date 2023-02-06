# pylint: disable=import-error
import asyncio
import binascii
import datetime

import busy_drivers.fbs.BusyDriverList as fbBusyDrivers
import busy_drivers.fbs.ChainBusyDriverList as ChainBusyDriverList
import pytest
from geobus_tools import geobus
from tests_plugins import utils

DRIVERS_CHUNKS_COUNT = 4

DRIVERS_COUNT = 2

EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'

NOW = datetime.datetime(2004, 10, 19, 7, 30, 0)


def _make_dbid_uuid(dbid, uuid):
    return '{}_{}'.format(dbid, uuid)


def _calc_chunk_id(dbid_uuid):
    return binascii.crc32(dbid_uuid.encode('utf8')) % DRIVERS_CHUNKS_COUNT


def _fbs_dest_extractor_busy_driver(dest):
    if dest is None:
        return None
    return {'lon': dest.Lon(), 'lat': dest.Lat()}


def _fbs_response_extractor_busy_driver(content):
    parsed = fbBusyDrivers.BusyDriverList.GetRootAsBusyDriverList(
        bytearray(content), 0,
    )
    drivers = [parsed.List(i) for i in range(parsed.ListLength())]
    drivers = [
        {
            'driver_id': driver.DriverId().decode(),
            'status': driver.TaxiStatus(),
            'order_id': driver.OrderId().decode(),
            'destination': _fbs_dest_extractor_busy_driver(
                driver.Destination(),
            ),
            'final_destination': _fbs_dest_extractor_busy_driver(
                driver.FinalDestination(),
            ),
        }
        for driver in drivers
    ]
    return {
        'drivers': drivers,
        'timestamp': datetime.datetime.utcfromtimestamp(parsed.Timestamp()),
    }


async def _perform_requests_busy_driver(taxi_busy_drivers, chunk_count):
    await taxi_busy_drivers.invalidate_caches()
    coros = [
        taxi_busy_drivers.get(
            '/v2/busy_drivers_bulk',
            params={'chunk_idx': i, 'chunk_count': chunk_count},
        )
        for i in range(chunk_count)
    ]
    responses = await asyncio.gather(*coros)

    result = {'drivers': [], 'timestamp': datetime.datetime(1970, 1, 1)}
    for response in responses:
        assert response.status_code == 200
        data = _fbs_response_extractor_busy_driver(response.content)
        result['timestamp'] = max(result['timestamp'], data['timestamp'])
        result['drivers'].extend(data['drivers'])

    return result


def _fbs_response_extractor_chain_busy_driver(content):
    parsed = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            content, 0,
        )
    )
    drivers = [parsed.List(i) for i in range(parsed.ListLength())]
    drivers = [
        {
            'driver_id': driver.DriverId().decode(),
            'order_id': driver.OrderId().decode(),
            'destination': {
                'lon': driver.Destination().Lon(),
                'lat': driver.Destination().Lat(),
            },
            'time_left': driver.TimeLeft(),
            'distance_left': driver.DistanceLeft(),
            'tracking_type': driver.TrackingType(),
            'flags': driver.Flags().decode(),
        }
        for driver in drivers
    ]
    return {
        'drivers': drivers,
        'timestamp': datetime.datetime.utcfromtimestamp(parsed.Timestamp()),
    }


async def _perform_requests_chain_busy_driver(taxi_busy_drivers, chunk_count):
    await taxi_busy_drivers.invalidate_caches()
    coros = [
        taxi_busy_drivers.get(
            '/v2/chain_busy_drivers_bulk',
            params={'chunk_idx': i, 'chunk_count': chunk_count},
        )
        for i in range(chunk_count)
    ]
    responses = await asyncio.gather(*coros)

    result = {'drivers': [], 'timestamp': datetime.datetime(1970, 1, 1)}
    for response in responses:
        assert response.status_code == 200
        data = _fbs_response_extractor_chain_busy_driver(response.content)
        result['timestamp'] = max(result['timestamp'], data['timestamp'])
        result['drivers'].extend(data['drivers'])

    return result


def _sort_drivers_by_id(drivers):
    return sorted(drivers['drivers'], key=lambda driver: driver['driver_id'])


@pytest.mark.config(BUSY_DRIVERS_DRIVERS_CHUNKS_COUNT=DRIVERS_CHUNKS_COUNT)
@pytest.mark.pgsql('busy_drivers', files=['orders.sql'])
async def test_busy_drivers_logistic_stq_worker(
        redis_store, testpoint, stq_runner, pgsql, taxi_busy_drivers,
):
    sql_select_template = (
        'SELECT * FROM busy_drivers.logistics_events '
        'WHERE cargo_ref_id = {cargo_ref_id}'
    )

    sql_chain_busy_drivers = (
        'SELECT * FROM busy_drivers.chain_busy_drivers_chunk_0'
    )

    # first logistic event, affects one order destinations
    stq_task_kwargs = {
        'cargo_ref_id': 'cargo_ref_id',
        'event': 'change',
        'updated_ts': '2004-10-19T07:25:00Z',
        'destinations': [
            {'position': [12.34, 56.78], 'status': 'pending'},
            {'position': [42.42, 42.42], 'status': 'pending'},
            {'position': [52.42, 32.42], 'status': 'pending'},
        ],
    }

    await stq_runner.busy_drivers_logistics_events.call(
        task_id='busy_drivers_logistics_events', kwargs=stq_task_kwargs,
    )
    await taxi_busy_drivers.run_task('distlock/chain-busy-drivers-updater')

    timestamp = int(utils.timestamp(NOW))
    positions = [
        {
            'driver_id': 'dbid_uuid{}'.format(i),
            'position': [37.65, 55.73],
            'direction': 0,
            'timestamp': timestamp * 1000,  # seconds -> milliseconds
            'speed': 42 / 3.6,  # km/h -> m/s
            'accuracy': 0,
            'source': 'Gps',
        }
        for i in range(DRIVERS_COUNT)
    ]

    @testpoint('geobus-positions_payload_processed')
    def redis_pos_payload_processed(data):
        return data

    await taxi_busy_drivers.enable_testpoints()

    redis_store.publish(
        EDGE_TRACKS_CHANNEL,
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await redis_pos_payload_processed.wait_call()

    # basic logistic events db check
    cursor = pgsql['busy_drivers'].cursor()
    cursor.execute(sql_select_template.format(cargo_ref_id='cargo_ref_id'))
    rows = cursor.fetchall()
    pg_colnames_events = [desc[0] for desc in cursor.description]
    pg_order = dict(zip(pg_colnames_events, rows[0]))
    assert pg_order['cargo_ref_id'] == 'cargo_ref_id'
    assert pg_order['event_type'] == 'change'
    assert (
        pg_order['destinations']
        == '{"(12.34,56.78)","(42.42,42.42)","(52.42,32.42)"}'
    )
    assert pg_order['destinations_statuses'] == [False, False, False]

    # get /v2/busy_drivers_bulk and check result
    drivers = await _perform_requests_busy_driver(
        taxi_busy_drivers, DRIVERS_CHUNKS_COUNT,
    )
    expected_drivers = [
        {
            'driver_id': 'dbid_uuid0',
            'status': 3,
            'order_id': 'order_id0',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'final_destination': {'lon': 55.4723, 'lat': 37.3598},
        },
        {
            'driver_id': 'dbid_uuid1',
            'status': 3,
            'order_id': 'order_id1',
            'destination': {'lon': 12.34, 'lat': 56.78},
            'final_destination': {'lon': 52.42, 'lat': 32.42},
        },
    ]
    assert _sort_drivers_by_id(drivers) == expected_drivers

    # check chain_busy_drivers db state
    cursor.execute(sql_chain_busy_drivers)
    pg_colnames_chain = [desc[0] for desc in cursor.description]
    rows_num = len(cursor.fetchall())
    assert rows_num == 0

    # second logistic event with increazed timestamp
    # changes same order destinations
    stq_task_kwargs = {
        'cargo_ref_id': 'cargo_ref_id',
        'event': 'change',
        'updated_ts': '2004-10-19T07:30:00Z',
        'destinations': [
            {'position': [12.34, 56.78], 'status': 'passed'},
            {'position': [42.42, 42.42], 'status': 'passed'},
            {'position': [60.00, 32.42], 'status': 'pending'},
        ],
    }

    await stq_runner.busy_drivers_logistics_events.call(
        task_id='busy_drivers_logistics_events', kwargs=stq_task_kwargs,
    )
    await taxi_busy_drivers.run_task('distlock/chain-busy-drivers-updater')

    # get /v2/busy_drivers_bulk and check result
    drivers = await _perform_requests_busy_driver(
        taxi_busy_drivers, DRIVERS_CHUNKS_COUNT,
    )
    expected_drivers[1]['destination'] = {'lon': 60.0, 'lat': 32.42}
    expected_drivers[1]['final_destination'] = {'lon': 60.0, 'lat': 32.42}
    assert _sort_drivers_by_id(drivers) == expected_drivers

    # check chain_busy_drivers db state
    cursor.execute(sql_chain_busy_drivers)
    rows = cursor.fetchall()
    pg_order = dict(zip(pg_colnames_chain, rows[0]))
    assert pg_order['order_id'] == 'order_id1'
    assert pg_order['destination'] == '(60,32.42)'
    assert pg_order['driver_skip_reason'] == 'position-too-old'

    # third logistic event with decreazed timestamp, have no affect
    stq_task_kwargs['updated_ts'] = '2004-10-19T07:29:00Z'
    stq_task_kwargs['destinations'][2] = {
        'position': [80.00, 42.42],
        'status': 'pending',
    }

    await stq_runner.busy_drivers_logistics_events.call(
        task_id='busy_drivers_logistics_events', kwargs=stq_task_kwargs,
    )
    await taxi_busy_drivers.run_task('distlock/chain-busy-drivers-updater')

    # get /v2/busy_drivers_bulk and check result
    drivers = await _perform_requests_busy_driver(
        taxi_busy_drivers, DRIVERS_CHUNKS_COUNT,
    )
    assert _sort_drivers_by_id(drivers) == expected_drivers

    # check chain_busy_drivers db state
    cursor.execute(sql_chain_busy_drivers)
    rows = cursor.fetchall()
    pg_order = dict(zip(pg_colnames_chain, rows[0]))
    assert pg_order['order_id'] == 'order_id1'
    assert pg_order['destination'] == '(60,32.42)'
    assert pg_order['driver_skip_reason'] == 'position-too-old'
