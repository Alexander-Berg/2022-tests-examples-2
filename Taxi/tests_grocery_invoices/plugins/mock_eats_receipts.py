import copy
import decimal
import typing

import pytest

from tests_grocery_invoices import models

DEFAULT_URL = 'https://ofd.ru/url'
DEFAULT_RECEIPT_INFO_RESPONSE = {
    'order_id': '1234',
    'document_id': 'some_doc_id',
    'is_refund': False,
    'created_at': '2021-11-22T15:33:00+03:00',
    'country_code': 'RU',
    'payment_method': 'card',
    'ofd_info': {'ofd_receipt_url': DEFAULT_URL},
}


@pytest.fixture(name='eats_receipts', autouse=True)
def mock_eats_receipts(mockserver):
    class Context:
        def __init__(self):
            self.check_receipt_request_data = []
            self.check_receipt_data = None
            self.mock_receipt_error404 = False
            self.mock_receipt_data = {}

        def check_receipt_request(self, **argv):
            self.check_receipt_request_data = [copy.deepcopy(argv)]

        def check_receipt_requests(self, requests):
            self.check_receipt_request_data = requests

        def check_receipt(self, **argv):
            self.check_receipt_data = copy.deepcopy(argv)

        def mock_receipt_info(self, error404=False, **argv):
            self.mock_receipt_error404 = error404
            self.mock_receipt_data = copy.deepcopy(argv)

        def times_receipts_request_called(self):
            return _mock_receipt_request.times_called

        def times_receipt_called(self):
            return _mock_receipt.times_called

    context = Context()

    @mockserver.json_handler('/eats-receipts/api/v1/receipt_request')
    def _mock_receipt_request(request):
        if (
                len(context.check_receipt_request_data) > 0
                and context.check_receipt_request_data[-1] is not None
        ):
            for key, value in context.check_receipt_request_data[-1].items():
                assert request.json[key] == value, key
            context.check_receipt_request_data.pop(-1)

        return mockserver.make_response(None, status=204)

    @mockserver.json_handler('/eats-receipts/api/v1/receipt')
    def _mock_receipt(request):
        if context.check_receipt_data is not None:
            for key, value in context.check_receipt_data.items():
                assert request.json[key] == value, key

        if context.mock_receipt_error404:
            return mockserver.make_response(json={}, status=404)

        return {**DEFAULT_RECEIPT_INFO_RESPONSE, **context.mock_receipt_data}

    return context


def convert_items(
        cart_items: typing.List[models.GroceryCartItemV2],
        supplier_tin: typing.Optional[str] = None,
):
    items = []

    for cart_item in cart_items:
        for sub_item in cart_item.sub_items:
            quantity = int(decimal.Decimal(sub_item.quantity))
            for _ in range(0, quantity):
                supplier_inn = (
                    cart_item.supplier_tin
                    if supplier_tin is None
                    else supplier_tin
                )
                items.append(
                    {
                        'id': sub_item.item_id,
                        'parent': None,
                        'price': sub_item.price,
                        'tax': cart_item.vat,
                        'title': cart_item.title,
                        'supplier_inn': supplier_inn,
                    },
                )

    return items
