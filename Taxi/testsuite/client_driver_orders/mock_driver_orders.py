"""
Mocks for driver-orders.
"""

import pytest


@pytest.fixture
def driver_orders(mockserver, load_json):
    orders = load_json('orders.json')

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def mock_orders_list(request):
        order_ids = request.json['query']['park']['order']['ids']
        assert len(order_ids) == len(set(order_ids))
        park_id = request.json['query']['park']['id']

        orders_raw = {
            order['id']: order
            for order in orders
            if order['id'] in order_ids and order['park_id'] == park_id
        }

        result = []
        for order_id in order_ids:
            if order_id in orders_raw:
                result.append({'id': order_id, 'order': orders_raw[order_id]})
            else:
                result.append({'id': order_id})

        return {'orders': result}

    return mock_orders_list
