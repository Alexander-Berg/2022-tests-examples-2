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
    response = await taxi_fleet_customers.put(
        ENDPOINT,
        params={'id': location_id},
        headers=HEADERS,
        json={
            'customer_id': 'existing_customer_id',
            'location': {
                'point': {'latitude': 52.518613, 'longitude': 13.376159},
                'address': 'Berlin, Deutschland',
            },
        },
    )
    assert response.status_code == 204


@pytest.mark.parametrize(
    ('location_id', 'customer_id', 'error'),
    (
        pytest.param(
            'location_id1',
            'customer_id1',
            {
                'code': 'customer_does_not_exist',
                'message': 'Customer does not exist',
            },
            id='Customer does not exist',
        ),
        pytest.param(
            'location_id1',
            'customer_id_other_park',
            {
                'code': 'customer_from_another_park',
                'message': 'Customer is from another park',
            },
            id='Customer is from another park',
        ),
        pytest.param(
            'location_id1',
            'existing_customer_id1',
            {
                'code': 'location_exists_for_another_customer',
                'message': 'Location exists for another customer',
            },
            id='Location exists for another customer',
        ),
        pytest.param(
            'location_id2',
            'existing_customer_id1',
            {
                'code': 'location_exists_in_another_park',
                'message': 'Location exists in another park',
            },
            id='Location exists in another park',
        ),
    ),
)
@pytest.mark.pgsql(
    'fleet_customers',
    files=['pg_fleet_customers.sql', 'pg_fleet_customers_locations.sql'],
)
async def test_failure(taxi_fleet_customers, location_id, customer_id, error):
    response = await taxi_fleet_customers.put(
        ENDPOINT,
        params={'id': location_id},
        headers=HEADERS,
        json={
            'customer_id': customer_id,
            'location': {
                'point': {'latitude': 52.518613, 'longitude': 13.376159},
                'address': 'Berlin, Deutschland',
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == error
