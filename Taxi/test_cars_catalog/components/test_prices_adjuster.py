import decimal

import pytest

from cars_catalog.generated.web import web_context as context


@pytest.mark.config(
    CARS_CATALOG_PRICE_ADJUSTMENT={
        'yearly_adjustment_coefficient': '0.1',
        'max_coefficient_divergence': '0.3',
        'result_precision': '0',
    },
)
async def test_adjust_prices(web_context: context.Context):
    stats = {2017: decimal.Decimal(100000), 2020: decimal.Decimal(200000)}
    prices = {}
    for year in range(2013, 2024):
        prices[year] = web_context.prices_adjuster.get_price_for_year(
            stats, year,
        )

    assert prices == {
        2013: decimal.Decimal(-1),
        2014: decimal.Decimal(75131),
        2015: decimal.Decimal(82645),
        2016: decimal.Decimal(90909),
        2017: decimal.Decimal(100000),
        2018: decimal.Decimal(110000),
        2019: decimal.Decimal(181818),
        2020: decimal.Decimal(200000),
        2021: decimal.Decimal(220000),
        2022: decimal.Decimal(242000),
        2023: decimal.Decimal(-1),
    }
