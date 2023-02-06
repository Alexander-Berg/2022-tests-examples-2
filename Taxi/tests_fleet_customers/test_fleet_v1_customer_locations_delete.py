import pytest

ENDPOINT = '/fleet/fleet-customers/v1/customer/locations'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


@pytest.mark.parametrize(
    'location_id',
    (
        pytest.param('location_id1', id='Existing location'),
        pytest.param('location_id3', id='Non-existent location'),
    ),
)
@pytest.mark.pgsql(
    'fleet_customers',
    files=['pg_fleet_customers.sql', 'pg_fleet_customers_locations.sql'],
)
async def test_success(taxi_fleet_customers, location_id):
    response = await taxi_fleet_customers.delete(
        ENDPOINT, params={'id': location_id}, headers=HEADERS,
    )
    assert response.status_code == 204


@pytest.mark.pgsql(
    'fleet_customers',
    files=['pg_fleet_customers.sql', 'pg_fleet_customers_locations.sql'],
)
async def test_failure(taxi_fleet_customers):
    response = await taxi_fleet_customers.delete(
        ENDPOINT, params={'id': 'location_id2'}, headers=HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'location_exists_in_another_park',
        'message': 'Location exists in another park',
    }
