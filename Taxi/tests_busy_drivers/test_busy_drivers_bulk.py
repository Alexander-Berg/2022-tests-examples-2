# pylint: disable=import-error
import asyncio
import datetime

import busy_drivers.fbs.BusyDriverList as fbBusyDrivers
import pytest


def _ms_to_datetime(milliseconds):
    return datetime.datetime.utcfromtimestamp(milliseconds / 1000.0)


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
        'timestamp': _ms_to_datetime(parsed.Timestamp()),
    }


async def _perform_requests(taxi_busy_drivers):
    await taxi_busy_drivers.invalidate_caches()
    coros = [
        taxi_busy_drivers.get('/busy_drivers_bulk', params={'chunk_id': i})
        for i in range(8)
    ]
    responses = await asyncio.gather(*coros)

    result = {'drivers': [], 'timestamp': datetime.datetime(1970, 1, 1)}
    for response in responses:
        assert response.status_code == 200
        data = _fbs_response_extractor(response.content)
        result['timestamp'] = max(result['timestamp'], data['timestamp'])
        result['drivers'].extend(data['drivers'])

    return result


@pytest.mark.pgsql('busy_drivers', files=['orders.sql'])
async def test_busy_drivers_bulk(taxi_busy_drivers):
    drivers = await _perform_requests(taxi_busy_drivers)
    assert sorted(drivers['drivers'], key=lambda x: x['driver_id']) == [
        {
            'driver_id': 'dbid_uuid0',
            'order_id': 'order_id0',
            'status': 3,  # transporting
            'destination': {'lon': 55.45, 'lat': 37.36},
            'final_destination': {'lon': 55.4723, 'lat': 37.3598},
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
        {
            'order_id': 'order_id6',
            'driver_id': 'dbid_uuid6',
            'status': 3,  # transporting'2004-10-19 10:20:00+03',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'final_destination': {'lon': 55.4723, 'lat': 37.3598},
        },
        {
            'order_id': 'order_id7',
            'driver_id': 'dbid_uuid7',
            'status': 3,  # transporting '2004-10-19 10:20:00+03',
            'destination': {'lon': 55.45, 'lat': 37.36},
            'final_destination': {'lon': 55.4723, 'lat': 37.3598},
        },
    ]
