import pytest

ENDPOINT = '/internal/fleet-orders/v1/orders/customer/summary'

HEADERS = {
    'X-Ya-Service-Ticket': 'ticket_valid1',
    'X-Yandex-UID': '1',
    'X-Park-ID': 'park_id',
}


@pytest.mark.parametrize(
    'customer_phone_pd_id, customer_created_at, count_orders_total',
    [
        ('customer_phone_pd_id', '2021-05-05T00:00:00+03:00', 2),
        ('non_existing_customer_phone_pd_id', '2021-05-05T00:00:00+03:00', 0),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_fleet_orders_info_ok(
        taxi_fleet_orders,
        customer_phone_pd_id,
        customer_created_at,
        count_orders_total,
):
    body_request = {
        'customer_phone_pd_id': customer_phone_pd_id,
        'customer_created_at': customer_created_at,
    }
    response = await taxi_fleet_orders.post(
        ENDPOINT, json=body_request, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['total'] == count_orders_total
