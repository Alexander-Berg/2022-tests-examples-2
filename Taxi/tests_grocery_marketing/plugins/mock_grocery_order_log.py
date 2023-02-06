import pytest


@pytest.fixture(name='grocery_order_log')
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.yandex_uid = None
            self.order_id = None
            self.order_by_id_error = None
            self.personal_phone_id = None
            self.cart_id = None
            self.order_state = None
            self.order_type = None
            self.retrieve_raw_error = None

            self.created_at = None
            self.status = None
            self.depot_id = None
            self.cashback_gain = None

            self.check_request_flag = False

        def check_request(self, order_id=None):
            self.order_id = order_id

            self.check_request_flag = True

        def set_order_id(self, order_id):
            self.order_id = order_id

        def set_yandex_uid(self, yandex_uid):
            self.yandex_uid = yandex_uid

        def set_order_meta(
                self, personal_phone_id, cart_id, order_state, order_type,
        ):
            self.personal_phone_id = personal_phone_id
            self.cart_id = cart_id
            self.order_state = order_state
            self.order_type = order_type

        def set_order_raw(self, created_at, status, depot_id, cashback_gain):
            self.created_at = created_at
            self.status = status
            self.depot_id = depot_id
            self.cashback_gain = cashback_gain

        def set_order_by_id_error(self, code=500):
            self.order_by_id_error = code

        def set_retrieve_raw_error(self, code=500):
            self.retrieve_raw_error = code

        def times_order_by_id_called(self):
            return mock_order_by_id.times_called

        def times_order_meta_called(self):
            return mock_order_meta.times_called

        def times_order_raw_called(self):
            return mock_order_raw.times_called

        def flush(self):
            mock_order_by_id.flush()

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/v1/order-log/v1/order-by-id',
    )
    def mock_order_by_id(request):
        if context.check_request_flag:
            if context.order_id:
                assert request.json['order_id'] == context.order_id

        if context.order_by_id_error is not None:
            return mockserver.make_response('', context.order_by_id_error)

        return {
            'yandex_uid': context.yandex_uid,
            'order_id': context.yandex_uid or '123456',
        }

    @mockserver.json_handler(
        '/grocery-order-log/internal/v1/order-log/v1/get-orders-meta-by-ids',
    )
    def mock_order_meta(request):
        if context.personal_phone_id is not None:
            personal_phone_id = {
                'personal_phone_id': context.personal_phone_id,
            }
        else:
            personal_phone_id = {}

        if context.cart_id is not None:
            cart_id = {'cart_id': context.cart_id}
        else:
            cart_id = {}

        return {
            'orders_meta': [
                {
                    'order_id': context.order_id,
                    **personal_phone_id,
                    'yandex_uid': context.yandex_uid,
                    **cart_id,
                    'order_state': context.order_state,
                    'order_type': context.order_type,
                },
            ],
            'failed_order_ids': [],
        }

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_order_raw(request):
        if context.retrieve_raw_error:
            return mockserver.make_response('', context.retrieve_raw_error)

        if context.depot_id is not None:
            depot_id = {'depot_id': context.depot_id}
        else:
            depot_id = {}

        if context.cashback_gain is not None:
            cashback_gain = {'cashback_gain': context.cashback_gain}
        else:
            cashback_gain = {}

        return {
            'orders': [
                {
                    'order_id': context.order_id,
                    'created_at': context.created_at,
                    'status': context.status,
                    'calculation': {
                        'items': [],
                        'final_cost': '0',
                        'currency_code': 'RUB',
                    },
                    'contact': {},
                    'destinations': [],
                    **depot_id,
                    **cashback_gain,
                },
            ],
        }

    return context
