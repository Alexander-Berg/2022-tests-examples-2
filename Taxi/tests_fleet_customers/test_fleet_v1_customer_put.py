import dateutil.parser
import pytest

from tests_fleet_customers import base_mocks
from tests_fleet_customers import utils


ENDPOINT = 'fleet/fleet-customers/v1/customer'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


@pytest.mark.now('2022-01-01T00:00:00+00:00')
async def test_success_customer_creating(
        taxi_fleet_customers, pgsql, personal_phones_store,
):
    customer_id = 'new_customer_id'
    assert not utils.get_customer_by_id(pgsql, customer_id)

    body = {
        'comment': 'comment',
        'invoice_enabled': False,
        'name': 'new_name',
        'phone': 'new_phone',
        'sms_enabled': True,
    }
    response = await taxi_fleet_customers.put(
        ENDPOINT, headers=HEADERS, json=body, params={'id': customer_id},
    )
    assert response.status_code == 200

    customer = utils.get_customer_by_id(pgsql, customer_id)
    assert customer == {
        'comment': 'comment',
        'created_at': dateutil.parser.parse('2022-01-01T00:00:00Z'),
        'id': customer_id,
        'invoice_enabled': False,
        'park_id': PARK_ID,
        'personal_phone_id': 'new_personal_phone_id',
        'name': 'new_name',
        'sms_enabled': True,
    }


async def test_success_customer_updating(
        taxi_fleet_customers, pgsql, personal_phones_store,
):
    customer_id = 'existing_customer_id'
    assert utils.get_customer_by_id(pgsql, customer_id)

    body = {
        'comment': 'comment',
        'invoice_enabled': False,
        'name': 'existing_name',
        'phone': 'existing_phone',
        'sms_enabled': False,
    }
    response = await taxi_fleet_customers.put(
        ENDPOINT, headers=HEADERS, json=body, params={'id': customer_id},
    )
    assert response.status_code == 200

    customer = utils.get_customer_by_id(pgsql, customer_id)
    assert customer == {
        'comment': 'comment',
        'created_at': dateutil.parser.parse('2022-01-01T00:00:00Z'),
        'id': customer_id,
        'invoice_enabled': False,
        'park_id': PARK_ID,
        'personal_phone_id': 'existing_personal_phone_id',
        'name': 'existing_name',
        'sms_enabled': False,
    }


@pytest.mark.parametrize('phone', ['existing_phone', 'new_phone'])
async def test_success_phone_updating(
        taxi_fleet_customers, pgsql, personal_phones_store, phone,
):
    body = {'invoice_enabled': False, 'phone': phone, 'sms_enabled': True}
    response = await taxi_fleet_customers.put(
        ENDPOINT,
        headers=HEADERS,
        json=body,
        params={'id': 'existing_customer_id'},
    )
    assert response.status_code == 200

    customer = utils.get_customer_by_id(pgsql, 'existing_customer_id')
    assert customer['personal_phone_id'] == base_mocks.PERSONAL_STORE[phone]


@pytest.mark.parametrize('name', ['existing_name', 'existing_name1', None])
async def test_success_name_updating(
        taxi_fleet_customers, pgsql, personal_phones_store, name,
):
    body = {
        'invoice_enabled': False,
        'phone': 'existing_phone',
        'name': name,
        'sms_enabled': True,
    }
    response = await taxi_fleet_customers.put(
        ENDPOINT,
        headers=HEADERS,
        json=body,
        params={'id': 'existing_customer_id'},
    )
    assert response.status_code == 200

    customer = utils.get_customer_by_id(pgsql, 'existing_customer_id')
    assert customer['name'] == name


async def test_failed_deleted_customer(
        taxi_fleet_customers, personal_phones_store,
):
    customer_id = 'deleted_customer_id'
    body = {
        'comment': 'comment',
        'invoice_enabled': False,
        'name': 'deleted_name',
        'phone': 'deleted_phone',
        'sms_enabled': False,
    }
    response = await taxi_fleet_customers.put(
        ENDPOINT, params={'id': customer_id}, headers=HEADERS, json=body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'deleted_customer',
        'message': 'deleted customer',
    }


@pytest.mark.parametrize(
    'customer_id', ['existing_customer_id', 'not_existing_customer_id'],
)
async def test_failed_duplicate_phone(
        taxi_fleet_customers, personal_phones_store, customer_id,
):
    body = {
        'comment': 'comment',
        'invoice_enabled': False,
        'name': 'name',
        'phone': 'existing_phone1',
        'sms_enabled': True,
    }
    response = await taxi_fleet_customers.put(
        ENDPOINT, params={'id': customer_id}, headers=HEADERS, json=body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'duplicate_phone',
        'message': 'duplicate_phone',
    }


async def test_failed_invalid_phone_personal(
        taxi_fleet_customers, personal_phones_store,
):
    body = {
        'comment': 'comment',
        'invoice_enabled': False,
        'name': 'name',
        'phone': 'invalid_phone',
        'sms_enabled': True,
    }
    response = await taxi_fleet_customers.put(
        ENDPOINT,
        params={'id': 'existing_customer_id'},
        headers=HEADERS,
        json=body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_phone',
        'message': 'invalid phone number',
    }
