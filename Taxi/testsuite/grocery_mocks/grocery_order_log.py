import copy

import pytest

ORDER_ID = 'order_id'
SHORT_ORDER_ID = 'short_order_id'
ORDER_ADDRESS = 'some street, 10'

DEFAULT_ORDER = {
    'order_id': ORDER_ID,
    'short_order_id': SHORT_ORDER_ID,
    'yandex_uid': 'yandex_uid',
    'created_at': '2020-12-31T21:00:00.778583+00:00',
    'status': 'closed',
    'closed_at': '2020-12-31T22:00:00.778583+00:00',
    'calculation': {
        'items': [],
        'final_cost': '123',
        'discount': '0',
        'refund': '0',
        'currency_code': 'RUB',
    },
    'contact': {},
    'legal_entities': [],
    'destinations': [{'point': [0, 0], 'short_text': ORDER_ADDRESS}],
    'receipts': [{'title': 'receipt_title', 'receipt_url': 'receipt_url'}],
}


@pytest.fixture(name='grocery_order_log', autouse=True)
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.mocked_order = copy.deepcopy(DEFAULT_ORDER)
            self.yandex_uid = None
            self.check_uid = False

        def mock_retrieve(self, **kwargs):
            self.mocked_order.update(kwargs)

        def set_yandex_uid(self, yandex_uid):
            self.yandex_uid = yandex_uid
            self.check_uid = True

        def times_retrieve_raw_called(self):
            return _mock_retrieve_raw.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_retrieve_raw(request):
        if context.check_uid:
            assert (
                request.json['user_identity']['yandex_uid']
                == context.yandex_uid
            )
        return {'orders': [context.mocked_order]}

    return context
