import typing

import pytest

from tests_grocery_orders import headers
from tests_grocery_orders import models

DEFAULT_INVOICE_VERSION = 28
DEFAULT_OPERATION_ID = 'refund-123'
DEFAULT_RESPONSE: dict = {}

USER_INFO = {
    'login_id': headers.LOGIN_ID,
    'personal_phone_id': headers.PERSONAL_PHONE_ID,
    'user_ip': headers.USER_IP,
    'yandex_uid': headers.YANDEX_UID,
    'request_application': headers.APP_INFO,
    'is_portal': False,
    'locale': 'ru',
}


CREATE = 'create-handler'
CANCEL = 'cancel-handler'
REMOVE = 'remove-handler'
CLEAR = 'clear-handler'
UPDATE = 'update-handler'
APPEND = 'append-handler'
VALIDATE = 'validate-handler'


@pytest.fixture(name='grocery_payments', autouse=True)
def mock_grocery_payments(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.check_create_data = None
            self.check_cancel_data = None
            self.check_remove_data = None
            self.check_clear_data = None
            self.check_update_data = None
            self.check_append_data = None
            self.check_validate_data = None
            self.mock_validate_data = None
            self.cancel_operation_type = 'cancel'

        def check_create(self, **argv):
            self.check_create_data = {}
            for key in argv:
                self.check_create_data[key] = argv[key]

        def check_clear(self, **argv):
            self.check_clear_data = {}
            for key in argv:
                self.check_clear_data[key] = argv[key]

        def check_remove(self, **argv):
            self.check_remove_data = {}
            for key in argv:
                self.check_remove_data[key] = argv[key]

        def check_cancel(self, **argv):
            self.check_cancel_data = {}
            for key in argv:
                self.check_cancel_data[key] = argv[key]

        def check_update(self, **argv):
            self.check_update_data = {}
            for key in argv:
                self.check_update_data[key] = argv[key]

        def check_append(self, **argv):
            self.check_append_data = {}
            for key in argv:
                self.check_append_data[key] = argv[key]

        def check_validate(self, **argv):
            self.check_validate_data = {}
            for key in argv:
                self.check_validate_data[key] = argv[key]

        def mock_validate(self, **argv):
            self.mock_validate_data = {}
            for key in argv:
                self.mock_validate_data[key] = argv[key]

        def set_error_code(self, handler, code):
            self.error_code[handler] = code

        def set_cancel_operation_type(self, operation_type):
            self.cancel_operation_type = operation_type

        def times_create_called(self):
            return mock_create_order.times_called

        def times_clear_called(self):
            return mock_clear_order.times_called

        def times_cancel_called(self):
            return mock_cancel_order.times_called

        def times_remove_called(self):
            return mock_remove_order.times_called

        def times_update_called(self):
            return mock_update_order.times_called

        def times_append_called(self):
            return mock_append_order.times_called

        def times_validate_called(self):
            return mock_validate_order.times_called

        def flush_all(self):
            mock_create_order.flush()
            mock_cancel_order.flush()
            mock_remove_order.flush()
            mock_clear_order.flush()
            mock_update_order.flush()
            mock_validate_order.flush()

    context = Context()

    @mockserver.json_handler('/grocery-payments/payments/v1/create')
    def mock_create_order(request):
        if CREATE in context.error_code:
            code = context.error_code[CREATE]
            return mockserver.make_response('{}', code)

        if context.check_create_data is not None:
            for key, value in context.check_create_data.items():
                assert request.json[key] == value, key

        return {
            'invoice_id': '123',
            'invoice_version': DEFAULT_INVOICE_VERSION,
            'operation_id': request.json['operation_id'],
        }

    @mockserver.json_handler('/grocery-payments/payments/v1/cancel')
    def mock_cancel_order(request):
        if CANCEL in context.error_code:
            code = context.error_code[CANCEL]
            return mockserver.make_response('{}', code)

        if context.check_cancel_data is not None:
            for key, value in context.check_cancel_data.items():
                assert request.json[key] == value, key

        return {
            'invoice_id': '123',
            'invoice_version': DEFAULT_INVOICE_VERSION,
            'operation_type': context.cancel_operation_type,
            'operation_id': DEFAULT_OPERATION_ID,
        }

    @mockserver.json_handler('/grocery-payments/payments/v1/remove')
    def mock_remove_order(request):
        if REMOVE in context.error_code:
            code = context.error_code[REMOVE]
            if code == 400:
                return mockserver.make_response(
                    '{"message": "bad request", "code": "bad_request"}',
                    status=code,
                )
            return mockserver.make_response('{}', code)

        if context.check_remove_data is not None:
            for key, value in context.check_remove_data.items():
                assert request.json[key] == value, key

        return {
            'invoice_id': '123',
            'invoice_version': DEFAULT_INVOICE_VERSION,
            'operation_id': DEFAULT_OPERATION_ID,
        }

    @mockserver.json_handler('/grocery-payments/payments/v1/clear')
    def mock_clear_order(request):
        if CLEAR in context.error_code:
            code = context.error_code[CLEAR]
            return mockserver.make_response('{}', code)

        if context.check_clear_data is not None:
            for key, value in context.check_clear_data.items():
                assert request.json[key] == value, key

        return {}

    @mockserver.json_handler('/grocery-payments/payments/v1/update')
    def mock_update_order(request):
        if UPDATE in context.error_code:
            code = context.error_code[UPDATE]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_update_data is not None:
            for key, value in context.check_update_data.items():
                assert request.json[key] == value, key

        return {
            'invoice_id': '123',
            'invoice_version': DEFAULT_INVOICE_VERSION,
            'operation_id': request.json['operation_id'],
        }

    @mockserver.json_handler('/grocery-payments/payments/v1/append')
    def mock_append_order(request):
        if APPEND in context.error_code:
            code = context.error_code[APPEND]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_append_data is not None:
            for key, value in context.check_append_data.items():
                assert request.json[key] == value, key

        return {
            'invoice_id': '123',
            'invoice_version': DEFAULT_INVOICE_VERSION,
            'operation_id': request.json['operation_id'],
        }

    @mockserver.json_handler('/grocery-payments/payments/v1/validate')
    def mock_validate_order(request):
        if VALIDATE in context.error_code:
            code = context.error_code[VALIDATE]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_validate_data is not None:
            for key, value in context.check_validate_data.items():
                assert request.json[key] == value, key

        if context.mock_validate_data is not None:
            return context.mock_validate_data

        return DEFAULT_RESPONSE

    return context


def convert_cart_items(items: typing.List[models.GroceryCartItem]):
    result = []
    for item in items:
        item_id = item.item_id
        if item.item_id not in ('delivery', 'tips', 'service_fee'):
            item_id += '_0'
            item_type = 'product'
        else:
            item_type = item_id

        to_add: typing.Dict[typing.Any, typing.Any] = {
            'item_id': item_id,
            'price': item.price,
            'quantity': item.quantity,
            'item_type': item_type,
        }

        result.append(to_add)

    return result


def convert_cart_items_v2(
        items: typing.List[models.GroceryCartItemV2], exchange_flow: bool,
):
    result = []
    for item in items:
        for sub_item in item.sub_items:
            price = sub_item.price

            if item.item_id not in ('delivery', 'tips', 'service_fee'):
                item_type = 'product'
            else:
                item_type = item.item_id

            if exchange_flow is True:
                price = sub_item.price_exchanged

            to_add: typing.Dict[typing.Any, typing.Any] = {
                'item_id': sub_item.item_id,
                'price': price,
                'quantity': sub_item.quantity,
                'item_type': item_type,
            }

            result.append(to_add)

    return result


def get_items_by_payment_type(
        items: typing.List[models.GroceryCartItem], payment_method,
):
    items_payments = convert_cart_items(items)
    return {'items': items_payments, 'payment_method': payment_method}


def get_items_v2_by_payment_type(
        items: typing.List[models.GroceryCartItemV2],
        payment_method,
        exchange_flow=False,
):
    items_payments = convert_cart_items_v2(items, exchange_flow)
    return {'items': items_payments, 'payment_method': payment_method}
