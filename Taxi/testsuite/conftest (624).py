# root conftest for service taxi-payments
import aiohttp.web
import pytest

pytest_plugins = ['taxi_payments_plugins.pytest_plugins']


@pytest.fixture
def mock_transactions(mockserver, load_json):
    @mockserver.json_handler('/transactions/invoice/retrieve')
    def _invoice_retrieve(request):
        invoices = load_json('transaction_invoices.json')
        if request.json['id'] not in invoices:
            return aiohttp.web.json_response(
                status=404,
                data={'code': '404', 'message': 'Invoice not found'},
            )
        return invoices[request.json['id']]
