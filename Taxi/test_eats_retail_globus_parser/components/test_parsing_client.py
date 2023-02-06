from generated.models import globus_parsing as globus_models


async def test_get_prices(stq3_context, parser_mocks, proxy_mocks):
    prices = await stq3_context.parsing_client.get_prices(place_id=1)
    assert len(prices) == 4
    assert isinstance(prices[0], globus_models.Price)


async def test_get_stocks(stq3_context, parser_mocks, proxy_mocks):
    stocks = await stq3_context.parsing_client.get_stocks(place_id=1)
    assert len(stocks) == 4
    assert isinstance(stocks[0], globus_models.Stock)


async def test_get_availabilities(stq3_context, parser_mocks, proxy_mocks):
    avs = await stq3_context.parsing_client.get_availabilities(place_id=1)
    assert len(avs) == 4
    assert isinstance(avs[0], globus_models.Availability)


async def test_get_products(stq3_context, parser_mocks, proxy_mocks):
    products = await stq3_context.parsing_client.get_products()
    assert len(products) == 4
    assert isinstance(products[0], globus_models.Product)
