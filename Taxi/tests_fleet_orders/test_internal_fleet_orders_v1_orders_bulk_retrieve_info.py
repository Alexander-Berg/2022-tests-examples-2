import pytest


ENDPOINT = '/internal/fleet-orders/v1/orders/bulk-retrieve-info'


HEADERS = {'X-Ya-Service-Ticket': 'ticket_valid1', 'X-Yandex-UID': '1'}


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
@pytest.mark.parametrize(
    'info_request, info_response',
    [
        (
            {
                'ids': [
                    {'alias_id': 'alias_id1', 'park_id': 'park_id1'},
                    {'alias_id': 'alias_id1', 'park_id': 'park_id2'},
                    {'alias_id': 'alias_id2', 'park_id': 'park_id2'},
                ],
            },
            {
                'orders': [
                    {
                        'alias_id': 'alias_id1',
                        'order_id': 'order_id1_park_id1',
                        'park_id': 'park_id1',
                        'short_id': 1,
                        'route': [
                            {'address': 'address_A', 'geopoint': [37.6, 50.6]},
                            {
                                'address': 'address_B1',
                                'geopoint': [37.6, 51.6],
                            },
                            {
                                'address': 'address_B2',
                                'geopoint': [37.6, 52.6],
                            },
                        ],
                    },
                    {
                        'alias_id': 'alias_id1',
                        'order_id': 'order_id1_park_id2',
                        'park_id': 'park_id2',
                        'short_id': 2,
                        'route': [
                            {'address': 'address_A', 'geopoint': [37.6, 50.6]},
                            {
                                'address': 'address_B1',
                                'geopoint': [37.6, 51.6],
                            },
                            {
                                'address': 'address_B2',
                                'geopoint': [37.6, 52.6],
                            },
                        ],
                    },
                    {
                        'alias_id': 'alias_id2',
                        'order_id': 'order_id2_park_id2',
                        'park_id': 'park_id2',
                        'short_id': 3,
                        'route': [
                            {'address': 'address_A', 'geopoint': [37.6, 50.6]},
                            {
                                'address': 'address_B1',
                                'geopoint': [37.6, 51.6],
                            },
                            {
                                'address': 'address_B2',
                                'geopoint': [37.6, 52.6],
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_fleet_orders_info_ok(
        taxi_fleet_orders, info_request, info_response,
):

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=info_request, headers=HEADERS,
    )

    assert response.json() == info_response
