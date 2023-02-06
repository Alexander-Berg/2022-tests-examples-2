import collections
import typing

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_market_gw_plugins import *  # noqa: F403 F401

from tests_grocery_market_gw import models

# pylint: disable=unused-variable


@pytest.fixture(name='market_checkouter', autouse=True)
def mock_market_checkouter(mockserver, load_json):
    checkouter_response = load_json('sample_market_order_response.json')

    @mockserver.json_handler(
        'market-checkouter-grocery/light/orders/yandexGo/all',
    )
    def _mock_checkouter_light_orders_all(request):
        print('mock checkouter:')
        print(checkouter_response)
        for param in ['clientRole', 'clientId', 'orderIds']:
            if param not in request.query:
                return mockserver.make_response(
                    status=400,
                    json={
                        'status': 400,
                        'code': 'MISSING_REQUEST_PARAMETER',
                        'message': (
                            'Required Set parameter \''
                            + param
                            + '\' is not present'
                        ),
                    },
                )
        market_orders = []
        order_ids = request.query['orderIds'].split(',')
        for order in checkouter_response['orders']:
            if str(order['id']) in order_ids:
                market_orders.append(order)
        return {'orders': market_orders}

    class Context:
        def get_order_ids(self):
            return [
                str(order['id']) for order in checkouter_response['orders']
            ]

        def set_checkouter_response(self, *, new_response):
            checkouter_response['orders'] = new_response['orders']

    context = Context()
    return context


class GroceryCart:
    def __init__(self, cart_id, client_price, items):
        self._cart_id = cart_id
        self._client_price = client_price
        self._items = items

    def get_json(self):
        return {
            'cart_id': self._cart_id,
            'cart_version': 0,
            'user_type': '',
            'user_id': '',
            'checked_out': False,
            'exists_order_id': False,
            'delivery_type': 'courier',
            'items': [item.get_json() for item in self._items],
            'total_discount_template': '',
            'total_item_discounts_template': '',
            'total_promocode_discount_template': '',
            'items_full_price_template': '',
            'items_price_template': '',
            'full_total_template': '',
            'client_price_template': '',
            'client_price': self._client_price,
            'total_discount': '0',
        }


@pytest.fixture(name='grocery_order_log', autouse=True)
def mock_grocery_order_log(mockserver):
    orders_by_uid = collections.defaultdict(list)
    order_by_id = {}

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_retrieve_orders(request):
        result = []
        if 'order_id' in request.json['range']:
            order_id = request.json['range']['order_id']
            if order_id in order_by_id:
                result.append(order_by_id[order_id])
        else:
            user = request.json['user_identity']
            yandex_uids = [user['yandex_uid']] + user['bound_yandex_uids']

            for uid in yandex_uids:
                result += orders_by_uid[uid]

        if result:
            return {'orders': result}
        return mockserver.make_response(status=404)

    class Context:
        def add_order(
                self,
                *,
                yandex_uid,
                order_id,
                status,
                items: typing.List[models.Product],
                price,
                short_order_id=None,
                order_source='market',
        ):
            order = {
                'order_id': order_id,
                'yandex_uid': yandex_uid,
                'created_at': '2021-01-01T00:00:00+03:00',
                'status': status,
                'closed_at': (
                    '2021-01-01T01:00:00+03:00' if status == 'closed' else None
                ),
                'calculation': {
                    'items': [item.get_json() for item in items],
                    'final_cost': price,
                    'discount': '0',
                    'refund': '0',
                    'currency_code': 'RUB',
                },
                'contact': {},
                'legal_entities': [],
                'destinations': [],
                'receipts': [],
            }
            if short_order_id is not None:
                order['short_order_id'] = short_order_id
            if order_source is not None:
                order['order_source'] = order_source
            orders_by_uid[yandex_uid].append(order)
            order_by_id[order_id] = order

    context = Context()
    return context
