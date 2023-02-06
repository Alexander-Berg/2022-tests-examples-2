import pytest


ENDPOINT = 'fleet/fleet-customers/v1/customer/by-phone'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


async def test_success(taxi_fleet_customers, personal_phones_store):
    response = await taxi_fleet_customers.post(
        ENDPOINT, json={'phone': 'existing_phone'}, headers=HEADERS,
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
    'phone, park_id',
    [('existing_phone', 'other_park_id'), ('deleted_phone', 'park_id')],
)
async def test_failed_customer_not_found(
        taxi_fleet_customers, personal_phones_store, phone, park_id,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id
    response = await taxi_fleet_customers.post(
        ENDPOINT, json={'phone': phone}, headers=headers,
    )
    assert response.status_code == 404


async def test_failed_invalid_phone(
        taxi_fleet_customers, personal_phones_store,
):
    response = await taxi_fleet_customers.post(
        ENDPOINT, json={'phone': 'invalid_phone'}, headers=HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_phone',
        'message': 'invalid phone number',
    }
