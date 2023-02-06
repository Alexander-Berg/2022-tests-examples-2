import pytest


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }
    return headers


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_success(taxi_fleet_orders):
    response = await taxi_fleet_orders.post(
        '/fleet/fleet-orders/v1/orders/metrics/now',
        headers=build_headers(park_id='park_id1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders_being_executed': 3,
        'orders_without_performers': 1,
    }
