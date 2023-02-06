import pytest

ENDPOINT = '/fleet/fleet-customers/v1/customer/locations/list'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


@pytest.mark.pgsql(
    'fleet_customers',
    files=['pg_fleet_customers.sql', 'pg_fleet_customers_locations.sql'],
)
async def test_success(taxi_fleet_customers):
    response = await taxi_fleet_customers.post(
        ENDPOINT,
        headers=HEADERS,
        json={'customer_id': 'existing_customer_id'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'locations': [
            {
                'location': {
                    'address': 'Berlin, Deutschland',
                    'point': {'latitude': 52.518613, 'longitude': 13.376159},
                },
                'location_id': 'location_id1',
            },
        ],
    }


@pytest.mark.parametrize(
    ('customer_id', 'error'),
    (
        pytest.param(
            'customer_id_other_park',
            {
                'code': 'customer_from_another_park',
                'message': 'Customer is from another park',
            },
            id='Customer is from another park',
        ),
        pytest.param(
            'customer_id1',
            {
                'code': 'customer_does_not_exist',
                'message': 'Customer does not exist',
            },
            id='Customer does not exist',
        ),
    ),
)
@pytest.mark.pgsql(
    'fleet_customers',
    files=['pg_fleet_customers.sql', 'pg_fleet_customers_locations.sql'],
)
async def test_failure(taxi_fleet_customers, customer_id, error):
    response = await taxi_fleet_customers.post(
        ENDPOINT, headers=HEADERS, json={'customer_id': customer_id},
    )
    assert response.status_code == 400
    assert response.json() == error
