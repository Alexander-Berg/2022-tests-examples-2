import pytest

DEFAULT_ORDER_ID = 'randomOrderId-grocery'
DEFAULT_GOOD_FIELDS = {'name': 'Hungry for apples?', 'cost': '99.99'}
DEFAULT_ORDER_FIELDS = {
    'status': 'closed',
    'contact': {},
    'legal_entities': [],
    'destinations': [],
    'receipts': [],
}
DEFAULT_CALCULATION_FIELDS = {
    'final_cost': '0.00',
    'discount': '0.00',
    'refund': '0.00',
    'currency_code': 'RUB',
}


@pytest.fixture(name='order_log')
def mock_order_log(mockserver):
    class Context:
        def __init__(self):
            self.expected_request = None
            self.orders = []

        def setup_request_checking(
                self,
                yandex_uid,
                count,
                accept_language=None,
                include_service_metadata=None,
        ):
            if accept_language is None:
                accept_language = 'ru'
            if include_service_metadata is None:
                include_service_metadata = False

            self.expected_request = {
                'yandex_uid': yandex_uid,
                'range': {'count': count},
                'accept_language': accept_language,
                'include_service_metadata': include_service_metadata,
            }

        @property
        def times_called(self):
            return mock_orders_retrieve.times_called

        @property
        def has_calls(self):
            return mock_orders_retrieve.has_calls

        def add_order(
                self, created_at, product_ids, order_id=DEFAULT_ORDER_ID,
        ):
            self.orders.append(
                {
                    'order_id': order_id,
                    'created_at': created_at,
                    'product_ids': product_ids,
                },
            )

    context = Context()

    @mockserver.json_handler('/grocery-order-log/internal/orders/v1/retrieve')
    def mock_orders_retrieve(request):
        if context.expected_request is not None:
            assert (
                request.headers['Accept-Language']
                == context.expected_request['accept_language']
            )

            assert (
                request.json['include_service_metadata']
                == context.expected_request['include_service_metadata']
            )
            assert (
                request.json['user_identity']['yandex_uid']
                == context.expected_request['yandex_uid']
            )
            assert request.json['user_identity']['bound_yandex_uids'] == []

            assert request.json['range'] == context.expected_request['range']

            assert 'order_id' not in request.json['range']
            assert 'older_than' not in request.json['range']

        return {'orders': _convert_orders(context.orders)}

    return context


def _convert_orders(orders):
    return [
        {
            'created_at': order['created_at'],
            'order_id': order['order_id'],
            'closed_at': order['created_at'],
            **DEFAULT_ORDER_FIELDS,
            'calculation': {
                **DEFAULT_CALCULATION_FIELDS,
                'addends': [
                    {'product_id': product_id, **DEFAULT_GOOD_FIELDS}
                    for product_id in order['product_ids']
                ],
            },
        }
        for order in orders
    ]
