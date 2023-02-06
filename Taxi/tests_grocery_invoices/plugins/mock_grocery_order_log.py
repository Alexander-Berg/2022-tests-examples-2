import copy

import pytest


from tests_grocery_invoices import consts

DEFAULT_ORDER = {
    'order_id': consts.ORDER_ID,
    'short_order_id': consts.SHORT_ORDER_ID,
    'yandex_uid': 'yandex_uid',
    'created_at': '2021-01-01T00:00:00+03:00',
    'status': 'closed',
    'closed_at': '2021-01-01T01:00:00+03:00',
    'calculation': {
        'items': [],
        'final_cost': '123',
        'discount': '0',
        'refund': '0',
        'currency_code': 'RUB',
    },
    'contact': {},
    'legal_entities': [],
    'destinations': [{'point': [0, 0], 'short_text': consts.ORDER_ADDRESS}],
    'receipts': [],
}


@pytest.fixture(name='grocery_order_log', autouse=True)
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.mocked_order = copy.deepcopy(DEFAULT_ORDER)

        def mock_retrieve(self, **kwargs):
            self.mocked_order.update(kwargs)

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_retrieve_raw(request):
        return {'orders': [context.mocked_order]}

    return context
