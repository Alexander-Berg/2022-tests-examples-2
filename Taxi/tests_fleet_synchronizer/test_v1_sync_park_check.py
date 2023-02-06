import pytest

from tests_fleet_synchronizer import common

ENDPOINT_URL = '/fleet-synchronizer/v1/sync/park/check'


async def test_ok_id(taxi_fleet_synchronizer, mock_fleet_parks_list):
    response = await taxi_fleet_synchronizer.get(
        ENDPOINT_URL,
        params={'park_id': 'ParkSeven', 'app_family': 'uberdriver'},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json()['show_button']


async def test_ok_city(taxi_fleet_synchronizer, mock_fleet_parks_list):
    response = await taxi_fleet_synchronizer.get(
        ENDPOINT_URL,
        params={'park_id': 'ParkOne', 'app_family': 'uberdriver'},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json()['show_button']


@pytest.mark.parametrize(
    'park_id',
    [
        pytest.param('ParkFour', id='bad_city'),
        pytest.param('ParkSix', id='is_partner'),
    ],
)
async def test_not_ok(taxi_fleet_synchronizer, mock_fleet_parks_list, park_id):
    response = await taxi_fleet_synchronizer.get(
        ENDPOINT_URL,
        params={'park_id': park_id, 'app_family': 'uberdriver'},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert not response.json()['show_button']


async def test_already_mapped(
        taxi_fleet_synchronizer, mock_fleet_parks_list, pgsql,
):
    common.clear_parks_mappings(pgsql, 'uberdriver')
    common.add_parks_mappings(pgsql, ['Four'], 'uberdriver')
    await taxi_fleet_synchronizer.invalidate_caches()

    response = await taxi_fleet_synchronizer.get(
        ENDPOINT_URL,
        params={'park_id': 'ParkFour', 'app_family': 'uberdriver'},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert not response.json()['show_button']
