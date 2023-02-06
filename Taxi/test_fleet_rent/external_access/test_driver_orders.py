import datetime as dt

import pytest

from testsuite.utils import http

from fleet_rent.entities import order as order_entities
from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import driver_orders


@pytest.mark.parametrize('order_exists', [True, False])
async def test_last_order(
        web_context: context_module.Context, mock_driver_orders, order_exists,
):
    @mock_driver_orders('/v1/parks/orders/list')
    async def _parks_orders_list(request: http.Request):
        assert request.json == {
            'limit': 1,
            'query': {
                'park': {
                    'driver_profile': {'id': 'driver_id'},
                    'id': 'park_id',
                    'order': {
                        'ended_at': {
                            'from': '2020-02-01T18:00:00+03:00',
                            'to': '2020-02-02T17:00:00+03:00',
                        },
                        'statuses': ['complete'],
                    },
                },
            },
        }
        if order_exists:
            orders = [
                {
                    'id': 'some_alias_id',
                    'short_id': 234,
                    'status': 'complete',
                    'created_at': '2020-02-01T18:00:00+03:00',
                    'booked_at': '2020-02-01T18:00:00+03:00',
                    'ended_at': '2020-02-01T19:00:00+00:00',
                    'provider': 'official_taxi',
                    'amenities': [],
                    'address_from': {'address': 'txt', 'lat': 12, 'lon': 23},
                    'route_points': [],
                    'events': [],
                },
            ]
        else:
            orders = []
        return {'limit': 1, 'cursor': 'cursor', 'orders': orders}

    client: driver_orders.DriverOrdersService = web_context.external_access.driver_orders  # noqa: E501

    result = await client.get_last_order(
        'park_id',
        'driver_id',
        dt.datetime(2020, 2, 1, 15, 00, tzinfo=dt.timezone.utc),
        dt.datetime(2020, 2, 2, 14, 00, tzinfo=dt.timezone.utc),
    )
    if order_exists:
        assert result is not None
        assert result == order_entities.LastOrderInfo(
            order_id='some_alias_id',
            complete_at=dt.datetime(2020, 2, 1, 19, tzinfo=dt.timezone.utc),
        )
    else:
        assert result is None
