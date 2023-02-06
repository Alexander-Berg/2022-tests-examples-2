import pytest

from tests_grocery_invoices import models


@pytest.fixture(name='grocery_cold_storage', autouse=True)
def mock_grocery_cold_storage(mockserver):
    class Context:
        def __init__(self):
            self.receipts = []
            self.receipts_check = None

        def receipts_times_called(self):
            return _mock_receipts.times_called

        def check_receipts_request(self, **kwargs):
            self.receipts_check = kwargs

        def append_receipt(self, receipt: models.Receipt):
            self.receipts.append(receipt.to_json())

    @mockserver.json_handler(
        '/grocery-cold-storage'
        '/internal/v1/cold-storage/v1/get/invoices/receipts',
    )
    def _mock_receipts(request):
        if context.receipts_check is not None:
            for key, value in context.receipts_check.items():
                assert request.json[key] == value, key

        return dict(items=context.receipts)

    context = Context()
    return context
