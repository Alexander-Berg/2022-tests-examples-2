import collections
import copy

import pytest

from testsuite.utils import cached_property

ORDER_ID = '123'
CART_ID = '00000000-0000-0000-0000-d98013100500'
YANDEX_UID = 'some_yandex_uid'
DEPOT_ID = '123456'
DEPOT_TIN = 'some_tin'
USER_IP = '1.1.1.1'

DEFAULT_ORDER = {
    'order_id': ORDER_ID,
    'order_version': 4,
    'cart_id': CART_ID,
    'cart_version': 10,
    'yandex_uid': YANDEX_UID,
    'offer_id': 'some_offer_id',
    'idempotency_token': 'token123',
    'status': 'closed',
    'created': '2020-03-03T10:04:37Z',
    'due': '2020-03-03T10:04:37.646Z',
    'region_id': 213,
    'country_iso2': 'RU',
    'location': [12, 34],
    'depot': {'id': DEPOT_ID, 'tin': DEPOT_TIN},
    'country': 'Russia',
    'user_info': {
        'yandex_uid': YANDEX_UID,
        'personal_phone_id': 'personal_phone_id',
        'user_ip': USER_IP,
    },
    'billing_flow': 'payments_eda',
    'receipts': [],
}


class Order:
    def __init__(self, **kwargs):
        self._raw_dict = copy.deepcopy(DEFAULT_ORDER)
        self.update(**kwargs)

    def __setitem__(self, key, value):
        self._raw_dict[key] = value

    def __getitem__(self, key):
        return self._raw_dict[key]

    def __delitem__(self, key):
        del self._raw_dict[key]

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'depot_id':
                self['depot']['id'] = value
                self[key] = value
            elif key == 'yandex_uid':
                self['yandex_uid'] = value
                self['user_info']['yandex_uid'] = value
            elif key == 'app_vars':
                self['user_info']['app_vars'] = value
            elif key == 'personal_phone_id':
                self['personal_phone_id'] = value
                self['user_info']['personal_phone_id'] = value
            else:
                self[key] = value

    def as_dict(self):
        return self._raw_dict


@pytest.fixture(name='grocery_orders_lib')
def mock_grocery_orders_lib(mockserver):
    @mockserver.json_handler('/grocery-orders/internal/v1/get-info')
    def _mock_get_info(request):
        order_id = request.json['order_id']
        for order in context.orders:
            if order['order_id'] == order_id:
                return mockserver.make_response(json=order.as_dict())

        return mockserver.make_response(status=404)

    @mockserver.json_handler('/grocery-orders/internal/v1/get-info-bulk')
    def _mock_get_info_bulk(request):
        if context.get_info_bulk_response is not None:
            return mockserver.make_response(
                status=context.get_info_bulk_response['status_code'],
                json=context.get_info_bulk_response['body'],
            )

        orders = []
        for order_id in request.json['order_ids']:
            for order in context.orders:
                if order['order_id'] == order_id:
                    orders.append(order.as_dict())

        return mockserver.make_response(json=orders)

    @mockserver.json_handler('/grocery-orders/internal/v1/append-receipt')
    def _mock_append_receipt(request):
        if context.append_receipt_data is not None:
            for key, value in context.append_receipt_data.items():
                assert request.json[key] == value, value

        return mockserver.make_response(json={})

    @mockserver.json_handler('/grocery-orders/internal/v1/orders-state')
    def _mock_orders_state(request):
        if context.error_response:
            return mockserver.make_response(**context.error_response)

        uids = {request.json['yandex_uid']}
        for uid in request.json.get('bound_yandex_uids', []):
            uids.add(uid)

        order_ids = set()
        orders = []

        def add_orders(items):
            for order in items:
                order_id = order['order_id']
                if order_id not in order_ids:
                    order_ids.add(order_id)
                    orders.append(order)

        for uid in uids:
            add_orders(context.order_states.by_uid.get(uid, []))
        for order_id in request.json.get('order_ids', []):
            add_orders(context.order_states.by_order_id.get(order_id, []))

        return mockserver.make_response(json={'grocery_orders': orders})

    @mockserver.json_handler('/grocery-orders/internal/v1/get-info-extended')
    def _mock_get_info_extended(request):
        order_id = request.json['order_id']
        for order in context.orders:
            if order['order_id'] == order_id:
                return mockserver.make_response(json=order.as_dict())

        return mockserver.make_response(status=404)

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v2/feedback')
    def _mock_feedback(request):
        if context.feedback_request is not None:
            assert request.json == context.feedback_request

        return mockserver.make_response(
            status=context.feedback_response['status_code'],
            json=context.feedback_response['body'],
        )

    @mockserver.json_handler(
        '/grocery-orders/lavka/v1/orders/v2/feedback/comments',
    )
    def _mock_feedback_comments(request):
        return mockserver.make_response(
            status=context.feedback_comments_response['status_code'],
            json=context.feedback_comments_response['body'],
        )

    @mockserver.json_handler(
        '/grocery-orders/lavka/v1/orders/v1/actions/rover/open_hatch',
    )
    def _mock_open_rover(request):
        return mockserver.make_response(
            status=context.open_rover_response['status_code'],
        )

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/supply-info')
    def _mock_supply_info(request):
        if context.supply_info_response['body']:
            return mockserver.make_response(
                status=context.supply_info_response['status_code'],
                json=context.supply_info_response['body'],
            )
        return mockserver.make_response(
            status=context.supply_info_response['status_code'],
        )

    @mockserver.json_handler(
        '/grocery-orders/lavka/v1/orders/v1/actions/cancel',
    )
    def _mock_order_cancel(request):
        order_id = request.json['order_id']
        yandex_uid = request.headers['X-Yandex-UID']

        status_code = 500
        json = {}

        if context.order_states.by_uid.get(yandex_uid):
            if context.order_states.by_order_id.get(order_id):
                status_code = 202
            else:
                status_code = 404
        else:
            if context.order_states.by_order_id.get(order_id):
                status_code = 401
                json = {'code': 'unauthorized', 'message': 'user not found'}
            else:
                status_code = 400

        return mockserver.make_response(status=status_code, json=json)

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/tips')
    def _mock_tips(request):
        return mockserver.make_response(
            status=context.tips_response['status_code'],
            json=context.tips_response['body'],
        )

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/tips/info')
    def _mock_tips_info(request):
        return mockserver.make_response(
            status=context.tips_info_response['status_code'],
            json=context.tips_info_response['body'],
        )

    class Context:
        def __init__(self):
            self.orders = []
            self.error_response = None
            self.append_receipt_data = None
            self.feedback_response = None
            self.feedback_request = None
            self.feedback_comments_response = None
            self.open_rover_response = None
            self.supply_info_response = None
            self.tips_response = None
            self.tips_info_response = None
            self.get_info_bulk_response = None

        @property
        def order(self):
            return self.orders[0]

        @cached_property
        def order_states(self):
            class Inner:
                def __init__(self):
                    self.by_uid = collections.defaultdict(list)
                    self.by_order_id = collections.defaultdict(list)

            return Inner()

        def add_order(self, **kwargs):
            order = Order(**kwargs)
            self.orders.append(order)
            return order

        def check_append_receipt(self, **kwargs):
            self.append_receipt_data = kwargs

        def add_order_state(
                self,
                *,
                yandex_uid,
                order_id,
                delivery_eta_min=None,
                order_source='market',
                **kwargs,
        ):
            order = {**kwargs, 'order_id': order_id}
            if delivery_eta_min is not None:
                order['delivery_eta_min'] = delivery_eta_min
            if order_source is not None:
                order['order_source'] = order_source
            self.order_states.by_uid[yandex_uid].append(order)
            self.order_states.by_order_id[order_id].append(order)

        def mock_error_response(self, status, json=None):
            self.error_response = {'status': status, 'json': json}

        def set_feedback_response(self, status_code=200, body=None):
            self.feedback_response = {'status_code': status_code, 'body': body}

        def set_feedback_comments_response(self, status_code=200, body=None):
            self.feedback_comments_response = {
                'status_code': status_code,
                'body': body,
            }

        def set_open_rover_response(self, status_code=200, body=None):
            self.open_rover_response = {
                'status_code': status_code,
                'body': body,
            }

        def set_tips_response(self, status_code=200, body=None):
            self.tips_response = {'status_code': status_code, 'body': body}

        def set_tips_info_response(self, status_code=200, body=None):
            self.tips_info_response = {
                'status_code': status_code,
                'body': body,
            }

        def set_supply_info_response(self, status_code=200, body=None):
            self.supply_info_response = {
                'status_code': status_code,
                'body': body,
            }

        def set_get_info_bulk_response(self, status_code=200, body=None):
            self.get_info_bulk_response = {
                'status_code': status_code,
                'body': body,
            }

        def check_feedback_request(self, **kwargs):
            self.feedback_request = kwargs

        def info_times_called(self):
            return _mock_get_info.times_called

        def append_receipt_times_called(self):
            return _mock_append_receipt.times_called

        def orders_state_times_called(self):
            return _mock_orders_state.times_called

        def order_feedback_times_called(self):
            return _mock_feedback.times_called

        def feedback_comments_times_called(self):
            return _mock_feedback_comments.times_called

        def open_rover_times_called(self):
            return _mock_open_rover.times_called

        def supply_info_times_called(self):
            return _mock_supply_info.times_called

        def flush_all(self):
            _mock_get_info.flush()
            _mock_append_receipt.flush()
            _mock_orders_state.flush()

    context = Context()
    return context


@pytest.fixture(name='grocery_orders')
def mock_grocery_orders(grocery_orders_lib):
    return grocery_orders_lib
