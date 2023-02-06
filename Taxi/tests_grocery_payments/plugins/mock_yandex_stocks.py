# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest

STOCK_PRICE_1 = 15.7150
STOCK_PRICE_2 = 21.8132

STOCKS_RESPONSE = {
    'tzname': 'Europe/Moscow',
    'tzoffset_minutes': '0',
    'tzoffset_hours': '3',
    'legend': ['buy'],
    'prices': [[1650834000000, STOCK_PRICE_1], [1650920400000, STOCK_PRICE_2]],
}


@pytest.fixture(name='yandex_stocks', autouse=True)
def mock_yandex_stocks(mockserver):
    class Context:
        def __init__(self):
            self.ils_rub_stock = HandleContext()

    @mockserver.json_handler('/yandex-stocks/xmlhist/graphmin_70004.json')
    def _mock_ils_rub_stock():
        context.ils_rub_stock.times_called += 1

        return STOCKS_RESPONSE

    context = Context()
    return context
