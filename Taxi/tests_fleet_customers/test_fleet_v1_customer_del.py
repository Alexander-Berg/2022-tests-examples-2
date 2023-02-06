import pytest

from tests_fleet_customers import utils

ENDPOINT = 'fleet/fleet-customers/v1/customer'

HEADERS = {
    'X-Park-ID': 'park_id',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


def check_customer_existence(pgsql, is_expected, customer_id):
    customer = utils.get_customer_by_id(pgsql, customer_id)
    if is_expected:
        assert customer['personal_phone_id']
    else:
        assert (
            not customer
            or not customer['personal_phone_id']
            and not customer['name']
        )


@pytest.mark.parametrize(
    'customer_id', ['existing_customer_id', 'existing_customer_id1'],
)
async def test_success_delete_active_customer(
        taxi_fleet_customers, pgsql, customer_id,
):
    check_customer_existence(pgsql, True, customer_id)

    response = await taxi_fleet_customers.delete(
        ENDPOINT, params={'id': customer_id}, headers=HEADERS,
    )
    assert response.status_code == 204

    check_customer_existence(pgsql, False, customer_id)


async def test_success_delete_deleted_customer(taxi_fleet_customers, pgsql):
    customer_id = 'deleted_customer_id'
    check_customer_existence(pgsql, False, customer_id)

    response = await taxi_fleet_customers.delete(
        ENDPOINT, params={'id': customer_id}, headers=HEADERS,
    )
    assert response.status_code == 204

    check_customer_existence(pgsql, False, customer_id)


async def test_success_delete_non_existent_customer(
        taxi_fleet_customers, pgsql,
):
    customer_id = 'not_existing_customer_id'
    check_customer_existence(pgsql, False, customer_id)

    response = await taxi_fleet_customers.delete(
        ENDPOINT, params={'id': customer_id}, headers=HEADERS,
    )
    assert response.status_code == 204

    check_customer_existence(pgsql, False, customer_id)
