import copy
import decimal
import typing

import pytest


from tests_grocery_invoices import models

DEFAULT_URL = 'https://ofd.ru/url'
DEFAULT_RECEIPT_INFO_RESPONSE = {
    'orderNr': '1234',
    'documentId': 'some-doc-id',
    'ofdReceiptInfo': {'ofdReceiptUrl': DEFAULT_URL},
}


@pytest.fixture(name='eats_core_receipts', autouse=True)
def mock_eats_core_receipts(mockserver):
    class Context:
        def __init__(self):
            self.check_receipt_send_data = None
            self.check_receipt_info_data = None
            self.mock_receipt_info_error404 = False
            self.mock_receipt_info_data = {}

        def check_receipt_send(self, **argv):
            self.check_receipt_send_data = copy.deepcopy(argv)

        def check_receipt_info(self, **argv):
            self.check_receipt_info_data = copy.deepcopy(argv)

        def mock_receipt_info(self, error404=False, **argv):
            self.mock_receipt_info_error404 = error404
            self.mock_receipt_info_data = copy.deepcopy(argv)

        def times_receipts_send_called(self):
            return _mock_receipts_send.times_called

        def times_receipts_info_called(self):
            return _mock_receipts_info.times_called

    context = Context()

    @mockserver.json_handler(
        '/eats-core-receipts/internal-api/v1/receipts/send',
    )
    def _mock_receipts_send(request):
        if context.check_receipt_send_data is not None:
            for key, value in context.check_receipt_send_data.items():
                assert request.json[key] == value, key

        return {'success': 'success'}

    @mockserver.json_handler(
        '/eats-core-receipts/internal-api/v1/receipts/info',
    )
    def _mock_receipts_info(request):
        if context.check_receipt_info_data is not None:
            for key, value in context.check_receipt_info_data.items():
                assert request.json[key] == value, key

        if context.mock_receipt_info_error404:
            return mockserver.make_response(json={}, status=404)

        return {
            **DEFAULT_RECEIPT_INFO_RESPONSE,
            **context.mock_receipt_info_data,
        }

    return context


def convert_items(
        cart_items: typing.List[models.GroceryCartItemV2], supplier_tin: str,
):
    items = []

    for cart_item in cart_items:
        for sub_item in cart_item.sub_items:
            quantity = int(decimal.Decimal(sub_item.quantity))
            for _ in range(0, quantity):
                items.append(
                    {
                        'id': sub_item.item_id,
                        'parent': None,
                        'price': sub_item.price,
                        'supplierINN': supplier_tin,
                        'tax': cart_item.vat,
                        'title': cart_item.title,
                    },
                )

    return items
