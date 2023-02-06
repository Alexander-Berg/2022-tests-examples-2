import pytest


@pytest.fixture(name='set_default_transactions_response')
def _set_default_transactions_response(mockserver, load_json):
    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    def handler(request):
        return mockserver.make_response(
            status=200,
            json=load_json('transactions_v2_invoice_retrieve_response.json'),
        )

    return handler


@pytest.fixture(name='get_default_fiscal_transactions')
def _get_default_fiscal_transactions(load_json):
    def handler():
        return load_json('transactions_v2_invoice_retrieve_response.json')

    return handler


@pytest.fixture(name='get_extracted_fiscal_transactions')
def _get_extracted_fiscal_transactions(load_json):
    def handler():
        return load_json('transactions_v2_invoice_extracted_transactions.json')

    return handler
