import dataclasses
import decimal

import pytest

from tests_grocery_caas_markdown.common import constants


@dataclasses.dataclass
class Stock:
    product_id: str
    quantity: decimal.Decimal = constants.DEFAULT_PRODUCT_QUANTITY


@pytest.fixture(name='grocery_wms', autouse=True)
def mock_grocery_wms(mockserver):
    class Context:
        def __init__(self):
            self.expected_request = None

            self.cursor = 'test_cursor_{}'
            self.cursor_num = 1

            self.stocks = []

        def setup_request_checking(self, stocks_filter):
            self.expected_request = {'filter': stocks_filter}

        @property
        def times_called(self):
            return mock_stocks.times_called

        def add_stocks(self, depot_id, stocks, shelf_type='markdown'):
            if isinstance(stocks, Stock):
                stocks = [stocks]
            elif isinstance(stocks, str):
                stocks = [Stock(product_id=stocks)]
            elif isinstance(stocks, list) and isinstance(stocks[0], str):
                stocks = [Stock(product_id=stock) for stock in stocks]

            self.stocks.extend(
                [
                    {
                        'store_id': depot_id,
                        'product_id': stock.product_id,
                        'shelf_type': shelf_type,
                        'count': int(stock.quantity),
                    }
                    for stock in stocks
                ],
            )

    context = Context()

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_stocks(request):
        if context.expected_request is not None:
            assert request.json['filter'] == context.expected_request['filter']

        cursor_num = context.cursor_num
        stocks = context.stocks.copy()

        context.cursor_num += 1
        context.stocks.clear()

        return {'cursor': context.cursor.format(cursor_num), 'stocks': stocks}

    return context
