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
async def test_success(taxi_fleet_orders, mockserver):
    response = await taxi_fleet_orders.post(
        '/fleet/fleet-orders/v1/orders/metrics/interval',
        headers=build_headers(park_id='park_id1'),
        json={
            'interval': {
                'from': '2021-02-08T00:00:00Z',
                'to': '2021-02-09T00:00:00Z',
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {'completed_orders': 1, 'cancelled_orders': 1}
