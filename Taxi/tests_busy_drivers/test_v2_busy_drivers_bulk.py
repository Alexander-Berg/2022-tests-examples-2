# pylint: disable=import-error
import asyncio
import datetime

import busy_drivers.fbs.BusyDriverList as fbBusyDrivers
import pytest


def _fbs_dest_extractor(dest):
    if dest is None:
        return None
    return {'lon': dest.Lon(), 'lat': dest.Lat()}


def _fbs_response_extractor(content):
    parsed = fbBusyDrivers.BusyDriverList.GetRootAsBusyDriverList(
        bytearray(content), 0,
    )
    drivers = [parsed.List(i) for i in range(parsed.ListLength())]
    drivers = [
        {
            'driver_id': driver.DriverId().decode(),
            'status': driver.TaxiStatus(),
            'order_id': driver.OrderId().decode(),
            'destination': _fbs_dest_extractor(driver.Destination()),
            'final_destination': _fbs_dest_extractor(
                driver.FinalDestination(),
            ),
        }
        for driver in drivers
    ]
    return {
        'drivers': drivers,
        'timestamp': datetime.datetime.utcfromtimestamp(parsed.Timestamp()),
    }


async def _perform_requests(taxi_busy_drivers, chunk_count):
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
        data = _fbs_response_extractor(response.content)
        result['timestamp'] = max(result['timestamp'], data['timestamp'])
        result['drivers'].extend(data['drivers'])

    return result


@pytest.mark.parametrize('chunk_count', [1, 2, 3, 4])
@pytest.mark.pgsql('busy_drivers', files=['orders.sql'])
async def test_v2_busy_drivers_bulk(chunk_count, taxi_busy_drivers):
    drivers = await _perform_requests(taxi_busy_drivers, chunk_count)
    assert sorted(drivers['drivers'], key=lambda x: x['driver_id']) == [
        {
            'driver_id': 'dbid_uuid0',
            'order_id': 'order_id0',
            'status': 3,  # transporting
            'destination': {'lon': 55.45, 'lat': 37.36},
            'final_destination': {'lon': 55.4722, 'lat': 37.3597},
        },
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id2',
            'status': 1,  # driving
            'destination': None,
            'final_destination': None,
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id3',
            'status': 1,  # driving
            'destination': None,
            'final_destination': None,
        },
        {
            'driver_id': 'dbid_uuid3',
            'order_id': 'order_id4',
            'status': 2,  # waiting
            'destination': None,
            'final_destination': None,
        },
    ]
