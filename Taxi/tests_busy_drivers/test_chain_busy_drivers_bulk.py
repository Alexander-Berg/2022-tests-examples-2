# pylint: disable=import-error
import asyncio
import datetime


import busy_drivers.fbs.ChainBusyDriverList as ChainBusyDriverList
import pytest


def _ms_to_datetime(milliseconds):
    return datetime.datetime.utcfromtimestamp(milliseconds / 1000.0)


def _fbs_response_extractor(content):
    driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            content, 0,
        )
    )
    drivers = [driver_list.List(i) for i in range(driver_list.ListLength())]
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
        'timestamp': _ms_to_datetime(driver_list.Timestamp()),
    }


async def _perform_requests(taxi_busy_drivers):
    await taxi_busy_drivers.invalidate_caches()
    coros = [
        taxi_busy_drivers.get(
            '/chain_busy_drivers_bulk', params={'chunk_id': i},
        )
        for i in range(8)
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


@pytest.mark.now('2004-10-19T07:25:00Z')
@pytest.mark.config(BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC=300)
@pytest.mark.pgsql('busy_drivers', files=['chain_busy_drivers.sql'])
async def test_chain_busy_drivers_bulk(taxi_busy_drivers):
    drivers = await _perform_requests(taxi_busy_drivers)

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


@pytest.mark.parametrize(
    'cache_max_age, expected_driver_count', [(300, 4), (120, 1)],
)
@pytest.mark.now('2004-10-19T07:25:00Z')
@pytest.mark.pgsql('busy_drivers', files=['chain_busy_drivers.sql'])
async def test_chain_busy_drivers_cache_slice_by_timestamp(
        cache_max_age, expected_driver_count, taxi_busy_drivers, taxi_config,
):
    taxi_config.set_values(
        {'BUSY_DRIVERS_CHAIN_BUSY_DRIVERS_MAX_AGE_SEC': cache_max_age},
    )
    drivers = await _perform_requests(taxi_busy_drivers)
    assert len(drivers['drivers']) == expected_driver_count
