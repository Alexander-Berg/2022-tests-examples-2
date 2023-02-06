import pytest

ENDPOINT = 'fleet/fleet-customers/v1/customer/orders/list'

PARK_ID = 'park_id'

HEADERS = {
    'X-Park-ID': PARK_ID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Remote-IP': '1.2.3.4',
}


@pytest.mark.parametrize(
    'query, cursor',
    [
        ({'sort': {'field': 'order_created_at', 'dir': 'desc'}}, 'cursor1'),
        (
            {
                'sort': {'field': 'order_created_at', 'dir': 'asc'},
                'booked_at': {'from': '2022-01-02T00:00:00+00:00'},
            },
            'cursor2',
        ),
        (
            {
                'sort': {'field': 'order_booked_at', 'dir': 'desc'},
                'statuses': ['created', 'driving'],
            },
            'cursor3',
        ),
        (
            {
                'sort': {'field': 'order_ended_at', 'dir': 'asc'},
                'booked_at': {'from': '2022-01-02T00:00:00+00:00'},
                'statuses': ['created', 'expired'],
            },
            'cursor4',
        ),
    ],
)
async def test_success(
        taxi_fleet_customers,
        personal_phones_retrieve,
        mockserver,
        query,
        cursor,
):
    @mockserver.json_handler('/fleet-orders/fleet/fleet-orders/v1/orders/list')
    def _mock_fleet_orders(request):
        assert request.json['query'] == {
            **query,
            'customer_phone_number': 'existing_phone',
            'created_at': {'from': '2022-01-01T00:00:00+00:00'},
        }
        return {'cursor': cursor}

    response = await taxi_fleet_customers.post(
        ENDPOINT,
        params={'id': 'existing_customer_id'},
        headers=HEADERS,
        json={'query': query},
    )
    assert response.status_code == 200
    assert response.json() == {'cursor': cursor}


@pytest.mark.parametrize(
    'customer_id, park_id',
    [
        ('non_existing_customer_id', PARK_ID),
        ('deleted_customer_id', PARK_ID),
        ('existing_customer_id', 'incorrcet_park_id'),
    ],
)
async def test_failed(
        taxi_fleet_customers, personal_phones_retrieve, customer_id, park_id,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id
    response = await taxi_fleet_customers.post(
        ENDPOINT,
        params={'id': customer_id},
        headers=headers,
        json={'query': {'sort': {'field': 'order_created_at', 'dir': 'desc'}}},
    )
    assert response.status_code == 404
