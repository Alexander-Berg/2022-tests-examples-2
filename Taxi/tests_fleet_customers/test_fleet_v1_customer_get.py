import pytest


ENDPOINT = 'fleet/fleet-customers/v1/customer'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


async def test_success(taxi_fleet_customers, personal_phones_retrieve):
    response = await taxi_fleet_customers.get(
        ENDPOINT, params={'id': 'existing_customer_id'}, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'created_at': '2022-01-01T00:00:00+00:00',
        'id': 'existing_customer_id',
        'invoice_enabled': True,
        'name': 'existing_name',
        'phone': 'existing_phone',
        'sms_enabled': True,
    }


@pytest.mark.parametrize(
    'customer_id',
    [
        'not_existing_customer_id',
        'deleted_customer_id',
        'customer_id_other_park',
    ],
)
async def test_failed(
        taxi_fleet_customers, personal_phones_retrieve, customer_id,
):
    response = await taxi_fleet_customers.get(
        ENDPOINT, params={'id': customer_id}, headers=HEADERS,
    )
    assert response.status_code == 404
