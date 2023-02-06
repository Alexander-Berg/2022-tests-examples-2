# pylint: disable=invalid-name, import-error

import enum

from grocery_mocks.models.country import Country
from grocery_mocks.utils.handle_context import HandleContext
import pytest

from testsuite.utils import cached_property

EXTERNAL_PAYMENT_ID = 'transaction-external-payment-id'
REFUND_EXTERNAL_PAYMENT_ID = 'refund-external-payment-id'

DEFAULT_TRANSACTION = {
    'created': '2021-02-10T11:51:12.607000+03:00',
    'external_payment_id': EXTERNAL_PAYMENT_ID,
    'held': '2021-02-10T11:51:25.739000+03:00',
    'initial_sum': [{'amount': '100', 'item_id': '111'}],
    'operation_id': 'create:a5d66e1d57be46308d71ade837c199e',
    'payment_method_id': 'card-x0c0cab13124063123e35406e',
    'payment_type': 'card',
    'refunds': [],
    'status': 'hold_success',
    'sum': [
        {'amount': '200', 'item_id': '444::sub0'},
        {'amount': '500', 'item_id': '333::sub0'},
    ],
    'technical_error': False,
    'terminal_id': '95426005',
    'updated': '2021-02-10T11:52:33.262000+03:00',
}

DEFAULT_OPERATION = {
    'created': '2021-02-10T11:52:32.306000+03:00',
    'id': 'create:a5d66e1d57be46308d71ade837c1991',
    'status': 'done',
    'sum_to_pay': [
        {
            'items': [
                {'amount': '200', 'item_id': '444::sub0'},
                {'amount': '500', 'item_id': '333::sub0'},
            ],
            'payment_type': 'card',
        },
    ],
}

DEFAULT_REFUND = {
    'created': '2021-02-19T16:00:46.684000+03:00',
    'external_payment_id': REFUND_EXTERNAL_PAYMENT_ID,
    'fiscal_receipt_refund_url': 'refund-url',
    'operation_id': 'refund:a5d66e1d57be46308d71ade837c1992',
    'refunded': '2021-02-19T16:02:18.695000+03:00',
    'status': 'refund_success',
    'sum': [{'amount': '54', 'item_id': '15074909::sub0'}],
    'updated': '2021-02-19T16:02:18.695000+03:00',
}


class TransactionsInstance(enum.Enum):
    eda = 'eda'
    lavka_isr = 'lavka-isr'
    ng = 'ng'


COUNTRY_TO_INSTANCE = {
    Country.Russia: TransactionsInstance.eda.value,
    Country.Israel: TransactionsInstance.lavka_isr.value,
    Country.France: TransactionsInstance.ng.value,
    Country.GreatBritain: TransactionsInstance.ng.value,
}

DEFAULT_ERROR_BODY = {'code': '', 'message': ''}


@pytest.fixture(name='transactions')
def mock_transactions(mockserver, load_json):
    class UpdateHandleContext(HandleContext):
        def __init__(self):
            super().__init__()
            self.check_operation_type = None

        def check_body(self, data):
            operation_type = data.pop('operation_type', None)
            operation_id = data.pop('operation_id', None)

            if operation_type is not None:
                self.check_operation_type = operation_type
                if operation_id is not None:
                    data['operation_id'] = f'{operation_type}:{operation_id}'

            super().check_body(data)

        def process(self, request_body, request_headers=None):
            if self.check_operation_type is not None:
                [operation_type, _] = request_body['operation_id'].split(':')
                assert operation_type == self.check_operation_type

            super().process(request_body, request_headers)

    class Context:
        def __init__(self):
            self.create = HandleContext()
            self.update = UpdateHandleContext()
            self.clear = HandleContext()
            self.retrieve = HandleContext()
            self.payment_callback = HandleContext()

        @cached_property
        def default_invoice(self):
            return load_json('invoice.json')

    def _make_error_response(error_code):
        return mockserver.make_response(
            json=DEFAULT_ERROR_BODY, status=error_code,
        )

    context = Context()

    for instance in TransactionsInstance:

        @mockserver.json_handler(
            f'/transactions-{instance.value}/v2/invoice/create',
        )
        def _mock_create(request):
            handler = context.create
            handler(request)

            if not handler.is_ok:
                return _make_error_response(handler.status_code)

            return {}

        @mockserver.json_handler(
            f'/transactions-{instance.value}/v2/invoice/update',
        )
        def _mock_update(request):
            handler = context.update
            handler(request)

            if not handler.is_ok:
                return _make_error_response(handler.status_code)

            return {}

        @mockserver.json_handler(
            f'/transactions-{instance.value}/invoice/clear',
        )
        def _mock_clear(request):
            handler = context.clear
            handler(request)

            if not handler.is_ok:
                return _make_error_response(handler.status_code)

            return {}

        @mockserver.json_handler(
            f'/transactions-{instance.value}/v2/invoice/retrieve',
        )
        def _mock_retrieve(request):
            handler = context.retrieve
            handler(request)

            if not handler.is_ok:
                return _make_error_response(handler.status_code)

            return handler.response_with(context.default_invoice)

        @mockserver.json_handler(
            f'/transactions-{instance.value}/v1/callback/payment',
        )
        def _mock_callback(request):
            handler = context.payment_callback
            handler(request)

            if not handler.is_ok:
                return _make_error_response(handler.status_code)

            return {}

    return context


def make_transaction(**kwargs) -> dict:
    return {**DEFAULT_TRANSACTION, **kwargs}


def make_operation(**kwargs) -> dict:
    return {**DEFAULT_OPERATION, **kwargs}


def make_refund(**kwargs) -> dict:
    return {**DEFAULT_REFUND, **kwargs}
