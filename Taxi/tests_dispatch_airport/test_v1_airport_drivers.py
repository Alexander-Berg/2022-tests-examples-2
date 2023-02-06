import pytest

from tests_dispatch_airport import common


@pytest.mark.parametrize(
    'airport_id, response_file_name',
    [('ekb', 'response_by_ekb.json'), ('unknown', 'empty_response.json')],
)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_airport_drivers(
        taxi_dispatch_airport, load_json, airport_id, response_file_name,
):
    url = '/v1/airport-drivers'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport_id': airport_id},
    )
    assert response.status_code == 200
    drivers = response.json()['drivers']
    etalon_drivers = load_json(response_file_name)['drivers']
    assert len(drivers) == len(etalon_drivers)

    drivers = sorted(drivers, key=lambda x: x['dbid_uuid'])
    for driver, etalon_driver in zip(drivers, etalon_drivers):
        if 'queue_info' in driver:
            driver['queue_info'] = sorted(
                driver['queue_info'], key=lambda x: x['tariff'],
            )
        assert driver == etalon_driver
