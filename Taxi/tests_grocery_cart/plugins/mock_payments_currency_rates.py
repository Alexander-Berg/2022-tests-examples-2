# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest

STOCK_PRICE_1 = '1.1111'

CURRENCY_RATES_RESPONSE = {
    'rates': [{'from': 'RUB', 'to': 'ILS', 'rate': STOCK_PRICE_1}],
}


@pytest.fixture(name='grocery_payments', autouse=True)
def mock_grocery_payments(mockserver):
    class Context:
        def __init__(self):
            self.currency_rates = HandleContext()
            self.currency_rates.mock_response(**CURRENCY_RATES_RESPONSE)

    @mockserver.json_handler(
        '/grocery-payments/internal/v1/payments/currency-rates',
    )
    def _mock_currency_rates(request):
        context.currency_rates(request)

        return context.currency_rates.response

    context = Context()
    return context
