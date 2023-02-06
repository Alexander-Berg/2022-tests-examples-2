import pytest

INVOICE_LINK = 'https://site.com/123/receipt'
INVOICE_ID = 'invoice-id-xxx-2004'
INVOICE_UUID = '7aa39782-c40c-49ea-9083-03edbb5e89a4'
CHECK_CREATE_INVOICE_KEY = 'check-create-invoice-key'
CHECK_CREATE_PARENT_KEY = 'check-create-parent-key'
IDEMPOTENCY_TOKEN_KEY = 'idempotency-token'


@pytest.fixture(name='grocery_invoices')
def mock_grocery_invoices(mockserver, personal):
    data = {}

    @mockserver.json_handler(
        '/grocery-invoices/internal/v1/invoices/v1/create',
    )
    def _mock_invoice_create(request):
        invoice_items = data.get(CHECK_CREATE_INVOICE_KEY, None)
        parent_uuid = data.get(CHECK_CREATE_PARENT_KEY, None)
        if invoice_items is not None:
            assert request.json['items'] == invoice_items
        if parent_uuid is not None:
            assert request.json['parent_uuid'] == parent_uuid
        if IDEMPOTENCY_TOKEN_KEY in data:
            assert (
                request.headers['X-Idempotency-Token']
                == data[IDEMPOTENCY_TOKEN_KEY]
            )

        return {
            'receipt': {
                'link': INVOICE_LINK,
                'id': INVOICE_ID,
                'uuid': INVOICE_UUID,
            },
        }

    class Context:
        def invoice_create_times_called(self):
            return _mock_invoice_create.times_called

        def check_create_invoice(self, invoice_items, parent_uuid=None):
            data[CHECK_CREATE_INVOICE_KEY] = invoice_items
            data[CHECK_CREATE_PARENT_KEY] = parent_uuid

        def check_idempotency_token(self, expected_token):
            data[IDEMPOTENCY_TOKEN_KEY] = expected_token

        def flush(self):
            _mock_invoice_create.flush()
            data.clear()

    context = Context()
    return context
