# pylint: disable=import-error
import asyncio
import datetime


import busy_drivers.fbs.ChainBusyDriverList as ChainBusyDriverList
import pytest


def _fbs_response_extractor(content):
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
            'left_time': driver.LeftTime(),
            'left_distance': driver.LeftDistance(),
            'approximate': driver.Approximate(),
            'flags': driver.Flags().decode(),
        }
        for driver in drivers
    ]
    return {
        'drivers': drivers,
        'timestamp': datetime.datetime.utcfromtimestamp(parsed.Timestamp()),
    }


async def _perform_requests(taxi_busy_drivers, chunk_count):
    await taxi_busy_drivers.invalidate_caches()
    coros = [
        taxi_busy_drivers.get(
            '/v2/chain_busy_drivers_bulk',
            params={'chunk_idx': i, 'chunk_count': chunk_count},
        )
        for i in range(chunk_count)
    ]
    responses = await asyncio.gather(*coros)

    result = {
        'drivers': [],
        'timestamp': datetime.datetime(2004, 10, 19, 7, 25),
    }
    for response in responses:
        assert response.status_code == 200
        data = _fbs_response_extractor(response.content)
        if data['drivers']:
            result['timestamp'] = min(result['timestamp'], data['timestamp'])
            result['drivers'].extend(data['drivers'])

    return result


@pytest.mark.uservice_oneshot
@pytest.mark.parametrize('chunk_count', [1, 2, 3])
@pytest.mark.now('2004-10-19T07:25:00Z')
@pytest.mark.config(BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC=300)
@pytest.mark.pgsql('busy_drivers', files=['chain_busy_drivers.sql'])
async def test_v2_chain_busy_drivers_bulk(chunk_count, taxi_busy_drivers):
    drivers = await _perform_requests(taxi_busy_drivers, chunk_count)

    assert drivers['timestamp'] == datetime.datetime(2004, 10, 19, 7, 20)
    assert sorted(drivers['drivers'], key=lambda x: x['driver_id']) == [
        {
            'driver_id': 'dbid_uuid0',
            'order_id': 'order_id0',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'left_time': 100,
            'left_distance': 1000,
            'approximate': False,
            'flags': '0',
        },
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id1',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'left_time': 200,
            'left_distance': 2000,
            'approximate': True,
            'flags': '1',
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id2',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'left_time': 200,
            'left_distance': 2000,
            'approximate': True,
            'flags': '1',
        },
        {
            'driver_id': 'dbid_uuid3',
            'order_id': 'order_id3',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'left_time': 200,
            'left_distance': 2000,
            'approximate': True,
            'flags': '1',
        },
    ]


@pytest.mark.uservice_oneshot
@pytest.mark.parametrize(
    'cache_max_age, expected_driver_count', [(300, 4), (120, 1)],
)
@pytest.mark.now('2004-10-19T07:25:00Z')
@pytest.mark.pgsql('busy_drivers', files=['chain_busy_drivers.sql'])
async def test_v2_chain_busy_drivers_cache_slice_by_timestamp(
        cache_max_age, expected_driver_count, taxi_busy_drivers, taxi_config,
):
    taxi_config.set_values(
        {'BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC': cache_max_age},
    )
    drivers = await _perform_requests(taxi_busy_drivers, 42)
    assert len(drivers['drivers']) == expected_driver_count


@pytest.mark.uservice_oneshot
@pytest.mark.now('2004-10-19T07:25:00Z')
@pytest.mark.config(BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC=300)
async def test_driver_cache_dirty_update(taxi_busy_drivers, pgsql, testpoint):
    cursor = pgsql['busy_drivers'].cursor()
    cursor.execute(
        """
    create table if not exists busy_drivers.chain_busy_drivers_chunk_0
    partition of busy_drivers.chain_busy_drivers
    for values in (0);

    create table if not exists busy_drivers.chain_busy_drivers_chunk_1
    partition of busy_drivers.chain_busy_drivers
    for values in (1);

    insert into busy_drivers.chain_busy_drivers(
        chunk_id, updated, order_id, driver_id, flags
    )
    values (
        0, '2004-10-19 10:20:00+03', 'order_id0', 'dbid_uuid0', '0'
    ), (
        1, '2004-10-19 10:20:00+03', 'order_id1', 'dbid_uuid1', '0'
    );
    """,
    )

    await taxi_busy_drivers.invalidate_caches()

    @testpoint('chain-busy-drivers-cache-get-chunk')
    def get_chunk(data):
        return {'inject_failure_by_chunk_id': 0}

    @testpoint('chain-busy-drivers-cache-keep-old')
    def keep_old(data):
        return

    await taxi_busy_drivers.enable_testpoints()
    await taxi_busy_drivers.invalidate_caches()

    await get_chunk.wait_call()
    await keep_old.wait_call()


@pytest.mark.uservice_oneshot
@pytest.mark.now('2004-10-19T07:25:00Z')
async def test_driver_cache_empty_chunks(
        taxi_busy_drivers, pgsql, taxi_config, testpoint,
):
    cursor = pgsql['busy_drivers'].cursor()
    cursor.execute(
        """
    create table if not exists busy_drivers.chain_busy_drivers_chunk_0
    partition of busy_drivers.chain_busy_drivers
    for values in (0);

    create table if not exists busy_drivers.chain_busy_drivers_chunk_1
    partition of busy_drivers.chain_busy_drivers
    for values in (1);

    insert into busy_drivers.chain_busy_drivers(
        chunk_id, updated, order_id, driver_id, flags
    )
    values (
        0, '2004-10-19 10:20:00+03', 'order_id0', 'dbid_uuid0', '0'
    ), (
        1, '2004-10-19 10:20:00+03', 'order_id1', 'dbid_uuid1', '0'
    );
    """,
    )

    taxi_config.set(BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC=300)
    await taxi_busy_drivers.invalidate_caches()

    @testpoint('chain-busy-drivers-cache-no-change')
    def no_change(data):
        return

    @testpoint('chain-busy-drivers-cache-data-empty')
    def data_empty(data):
        return

    cursor.execute(
        """
    delete from busy_drivers.chain_busy_drivers;
    """,
    )
    await taxi_busy_drivers.enable_testpoints()

    await taxi_busy_drivers.invalidate_caches()
    await no_change.wait_call()

    taxi_config.set(BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC=60)
    await taxi_busy_drivers.invalidate_caches()
    await data_empty.wait_call()
