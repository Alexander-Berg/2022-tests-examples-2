import pytest

ENDPOINT = '/fleet/fleet-customers/v1/customer/last-ride'

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
        'id': 'order_id1',
        'booked_at': '2022-01-01T00:00:00+01:00',
        'created_at': '2022-01-01T00:00:00+01:00',
        'status': 'created',
        'tariff_class_id': 'econom',
        'route': ['address_A', 'address_B1', 'address_B2'],
        'is_park_creator': True,
        'number': 1,
    },
]


@pytest.mark.pgsql('fleet_customers', files=['pg_fleet_customers.sql'])
async def test_success(
        taxi_fleet_customers, mockserver, personal_phones_retrieve,
):
    @mockserver.json_handler('/fleet-orders/fleet/fleet-orders/v1/orders/list')
    def _mock_v1_orders_list(request):
        if request.method == 'GET':
            assert request.query['limit'] == '1'
            assert request.query['cursor'] == 'cursor'
            return {'orders': ORDERS, 'next_cursor': 'next_cursor'}

        assert request.json == {
            'query': {
                'sort': {'field': 'order_created_at', 'dir': 'desc'},
                'customer_phone_number': 'existing_phone',
            },
        }
        return {'cursor': 'cursor'}

    response = await taxi_fleet_customers.get(
        ENDPOINT, headers=HEADERS, params={'id': 'existing_customer_id'},
    )
    assert response.status_code == 200
    assert response.json() == {'tariff_class_id': 'econom'}


@pytest.mark.parametrize(
    ('customer_id', 'error'),
    (
        pytest.param(
            'customer_id_other_park',
            {
                'code': 'customer_from_another_park',
                'message': 'Customer is from another park',
            },
            id='Customer is from another park',
        ),
        pytest.param(
            'customer_id1',
            {
                'code': 'customer_does_not_exist',
                'message': 'Customer does not exist',
            },
            id='Customer does not exist',
        ),
        pytest.param(
            'existing_customer_id',
            {
                'code': 'customer_has_no_rides',
                'message': 'Customer has no rides',
            },
            id='Customer has no rides',
        ),
    ),
)
@pytest.mark.pgsql('fleet_customers', files=['pg_fleet_customers.sql'])
async def test_failure(
        taxi_fleet_customers,
        mockserver,
        customer_id,
        error,
        personal_phones_retrieve,
):
    @mockserver.json_handler('/fleet-orders/fleet/fleet-orders/v1/orders/list')
    def _mock_v1_orders_list(request):
        if request.method == 'GET':
            assert request.query['limit'] == '1'
            assert request.query['cursor'] == 'cursor'
            return {'orders': [], 'next_cursor': 'next_cursor'}

        assert request.json == {
            'query': {
                'sort': {'field': 'order_created_at', 'dir': 'desc'},
                'customer_phone_number': 'existing_phone',
            },
        }
        return {'cursor': 'cursor'}

    response = await taxi_fleet_customers.get(
        ENDPOINT, headers=HEADERS, params={'id': customer_id},
    )
    assert response.status_code == 400
    assert response.json() == error
