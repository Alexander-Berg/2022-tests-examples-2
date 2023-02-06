import pytest

from tests_driver_weariness import const


@pytest.mark.now('2018-01-01T00:00:00')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql('drivers_status_ranges', files=['pg_whitelist_items.sql'])
async def test_whitelist_items(taxi_driver_weariness):

    response = await taxi_driver_weariness.get('v1/whitelist/items')
    assert response.status_code == 200
    data = response.json()

    expected_data = {
        'items': [
            {
                'unique_driver_id': 'udid1',
                'author': 'ivanov',
                'ttl': '2021-01-21T18:45:00+0000',
            },
            {
                'unique_driver_id': 'udid3',
                'author': 'sidorov',
                'ttl': '2022-01-21T18:45:00+0000',
            },
            {
                'unique_driver_id': 'udid2',
                'author': 'petrov',
                'ttl': '2023-01-21T18:45:00+0000',
            },
        ],
    }
    assert data == expected_data
