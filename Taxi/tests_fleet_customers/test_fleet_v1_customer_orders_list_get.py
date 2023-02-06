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

ORDERS = [
    {
        'id': 'order_id',
        'booked_at': '2021-05-05T17:20:00+00:00',
        'created_at': '2021-05-05T17:20:00+00:00',
        'status': 'created',
        'tariff_class_id': 'econom',
        'route': ['address_A', 'address_B1', 'address_B2'],
        'is_park_creator': True,
        'number': 3,
    },
    {
        'id': 'order_id1',
        'contractor': {
            'affiliation': 'another_park',
            'name': 'another park name',
        },
        'created_at': '2021-05-05T17:10:00+00:00',
        'status': 'driving',
        'tariff_class_id': 'econom',
        'route': ['address_A', 'address_B1', 'address_B2'],
        'is_park_creator': True,
        'number': 2,
        'vehicle': {'brand': 'brand2', 'model': 'model2', 'number': 'number2'},
    },
    {
        'id': 'order_id2',
        'contractor': {
            'affiliation': 'your_park',
            'first_name': 'first_name',
            'id': 'driver_id1',
            'last_name': 'last_name',
            'last_photo': 'avatar_url',
            'middle_name': 'middle_name',
        },
        'created_at': '2021-05-05T17:00:00+00:00',
        'status': 'expired',
        'tariff_class_id': 'econom',
        'route': ['address_A', 'address_B1', 'address_B2'],
        'is_park_creator': True,
        'price': '28.9000',
        'park_commission': '0.1445',
        'number': 1,
        'vehicle': {
            'brand': 'brand1',
            'model': 'model1',
            'number': 'number1',
            'id': 'car_id1',
        },
    },
]


@pytest.mark.parametrize(
    'orders, next_cursor', [(ORDERS, 'next_cursor'), ([], None)],
)
async def test_success(
        taxi_fleet_customers,
        personal_phones_retrieve,
        mockserver,
        orders,
        next_cursor,
):
    params = params = {
        'id': 'existing_customer_id',
        'cursor': 'cursor',
        'limit': 2,
    }

    @mockserver.json_handler('/fleet-orders/fleet/fleet-orders/v1/orders/list')
    def _mock_fleet_orders(request):
        assert request.query['cursor'] == params['cursor']
        assert request.query['limit'] == str(params['limit'])
        return {'orders': orders, 'next_cursor': next_cursor}

    response = await taxi_fleet_customers.get(
        ENDPOINT, params=params, headers=HEADERS,
    )
    assert response.status_code == 200
    if next_cursor:
        assert response.json() == {
            'orders': orders,
            'next_cursor': next_cursor,
        }
    else:
        assert response.json() == {'orders': orders}


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


async def test_invalid_cursor(
        taxi_fleet_customers, personal_phones_retrieve, mockserver,
):
    @mockserver.json_handler('/fleet-orders/fleet/fleet-orders/v1/orders/list')
    def _mock_fleet_orders(request):
        assert request.query['cursor'] == params['cursor']
        assert request.query['limit'] == str(params['limit'])
        return mockserver.make_response(
            status=404,
            json={'code': 'invalid_cursor', 'message': 'invalid cursor'},
        )

    params = {
        'id': 'existing_customer_id',
        'cursor': 'invalid_cursor',
        'limit': 2,
    }
    response = await taxi_fleet_customers.get(
        ENDPOINT, params=params, headers=HEADERS,
    )
    assert response.status_code == 400
