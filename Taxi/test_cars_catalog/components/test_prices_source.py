import decimal

import aiohttp.web
import pytest

from testsuite.utils import http

from cars_catalog.generated.web import web_context as context


@pytest.mark.now('2020-06-01')
@pytest.mark.config(
    CARS_CATALOG_AUTORU_CACHE={'use_autoru_source': True, 'cache_ttl': '356d'},
)
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)
@pytest.mark.pgsql('cars_catalog', files=['autoru_prices_cache.sql'])
async def test_cache_hit(web_context: context.Context):
    prices = await web_context.prices_source.load_prices('VAZ', '2106')
    assert prices == {2000: decimal.Decimal(999)}


@pytest.mark.now('2020-06-01')
@pytest.mark.config(
    CARS_CATALOG_AUTORU_CACHE={'use_autoru_source': True, 'cache_ttl': '1d'},
)
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)
@pytest.mark.config(
    CARS_CATALOG_PRICE_ADJUSTMENT={
        'yearly_adjustment_coefficient': '0.1',
        'max_coefficient_divergence': '0.2',
    },
)
@pytest.mark.pgsql('cars_catalog', files=['autoru_prices_cache.sql'])
async def test_cache_expired(
        web_context: context.Context, mock_autoru, load_json,
):
    autoru_response = load_json('autoru_response.json')

    @mock_autoru('/1.0/stats/summary')
    async def _x10_stats_summary_get(request: http.Request):
        assert request.headers['X-Authorization']
        return autoru_response

    prices = await web_context.prices_source.load_prices('VAZ', '2106')
    assert prices == {
        1999: decimal.Decimal(90450),
        2000: decimal.Decimal(100500),
    }

    # Check updates stored
    stored_prices_records = await web_context.pg.master_pool.fetch(
        'SELECT age, price FROM cars_catalog.autoru_prices_cache',
    )
    stored_prices = {
        record['age']: record['price'] for record in stored_prices_records
    }
    assert stored_prices == {
        21: decimal.Decimal(90450),
        20: decimal.Decimal(100500),
    }


@pytest.mark.now('2020-06-01')
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)
@pytest.mark.config(
    CARS_CATALOG_AUTORU_CACHE={'use_autoru_source': True, 'cache_ttl': '356d'},
)
@pytest.mark.config(
    CARS_CATALOG_PRICE_ADJUSTMENT={
        'yearly_adjustment_coefficient': '0.1',
        'max_coefficient_divergence': '0.2',
    },
)
async def test_cache_miss(
        web_context: context.Context, mock_autoru, load_json,
):
    autoru_response = load_json('autoru_response.json')

    @mock_autoru('/1.0/stats/summary')
    async def _x10_stats_summary_get(request: http.Request):
        assert request.headers['X-Authorization']
        return autoru_response

    prices = await web_context.prices_source.load_prices('VAZ', '2106')
    assert prices == {
        1999: decimal.Decimal(90450),
        2000: decimal.Decimal(100500),
    }


@pytest.mark.config(
    CARS_CATALOG_AUTORU_CACHE={'use_autoru_source': True, 'cache_ttl': '1s'},
)
async def test_cache_nodata(web_context: context.Context, mock_autoru):
    @mock_autoru('/1.0/stats/summary')
    async def _x10_stats_summary_get(request: http.Request):
        return {'stats': {'model': {}}, 'status': 'SUCCESS'}

    prices = await web_context.prices_source.load_prices('VAZ', '2106')
    assert prices == {}


@pytest.mark.now('2020-06-01')
@pytest.mark.config(
    CARS_CATALOG_AUTORU_CACHE={'use_autoru_source': True, 'cache_ttl': '1s'},
)
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)
@pytest.mark.config(
    CARS_CATALOG_PRICE_ADJUSTMENT={
        'yearly_adjustment_coefficient': '0.1',
        'max_coefficient_divergence': '0.2',
    },
)
@pytest.mark.pgsql('cars_catalog', files=['autoru_prices_cache.sql'])
async def test_cache_expired_api_error(
        web_context: context.Context, mock_autoru,
):
    # Cache tolerates source errors by providing expired data
    @mock_autoru('/1.0/stats/summary')
    async def _x10_stats_summary_get(request: http.Request):
        assert request.headers['X-Authorization']
        return aiohttp.web.Response(status=500)

    prices = await web_context.prices_source.load_prices('VAZ', '2106')
    assert prices == {2000: decimal.Decimal(999)}


@pytest.mark.now('2020-06-01')
@pytest.mark.config(
    CARS_CATALOG_AUTORU_CACHE={'use_autoru_source': False, 'cache_ttl': '1s'},
)
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)
@pytest.mark.config(
    CARS_CATALOG_PRICE_ADJUSTMENT={
        'yearly_adjustment_coefficient': '0.1',
        'max_coefficient_divergence': '0.2',
    },
)
@pytest.mark.pgsql('cars_catalog', files=['autoru_prices_cache.sql'])
async def test_dont_use_autoru_source(web_context: context.Context):
    prices = await web_context.prices_source.load_prices('VAZ', '2106')
    assert prices == {2000: decimal.Decimal(999)}
