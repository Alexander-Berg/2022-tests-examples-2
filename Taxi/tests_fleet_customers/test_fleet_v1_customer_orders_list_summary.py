import pytest

ENDPOINT = 'fleet/fleet-customers/v1/customer/orders/summary'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


async def test_success(
        taxi_fleet_customers, personal_phones_retrieve, mockserver,
):
    total = 5

    @mockserver.json_handler(
        '/fleet-orders/internal/fleet-orders/v1/orders/customer/summary',
    )
    def _mock_fleet_orders(request):
        assert request.json == {
            'customer_phone_pd_id': 'existing_personal_phone_id',
            'customer_created_at': '2022-01-01T00:00:00+00:00',
        }
        return {'total': total}

    response = await taxi_fleet_customers.get(
        ENDPOINT, params={'id': 'existing_customer_id'}, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'total': total}


@pytest.mark.parametrize(
    'customer_id, park_id',
    [
        ('non_existing_customer_id', PARK_ID),
        ('deleted_customer_id', PARK_ID),
        ('existing_customer_id', 'incorrcet_park_id'),
    ],
)
async def test_customer_not_found(
        taxi_fleet_customers,
        personal_phones_retrieve,
        mockserver,
        customer_id,
        park_id,
):
    headers = HEADERS.copy()
    headers['X-Park-ID'] = park_id
    params = {'id': customer_id, 'cursor': 'cursor', 'limit': 2}
    response = await taxi_fleet_customers.get(
        ENDPOINT, params=params, headers=headers,
    )
    assert response.status_code == 404
