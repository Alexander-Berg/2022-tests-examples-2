import pytest

from tests_grocery_market_gw import models


@pytest.mark.parametrize('limit', [1, 2])
async def test_market_search(
        taxi_grocery_market_gw, mock_api_v1_for_lavka, limit,
):
    products = [
        models.MarketProduct('product-1', 10, 10, []),
        models.MarketProduct('product-2', 10, 5, []),
        models.MarketProduct('product-3', 10, 10, ['RU_18+']),
    ]
    products_data = [product.get_data() for product in products]

    banner_url = 'some-banner-url'
    results_url = 'some-results-url'

    mock_api_v1_for_lavka.set_products(products)
    mock_api_v1_for_lavka.set_banner_url(banner_url)
    mock_api_v1_for_lavka.set_results_url(results_url)

    response_products = []
    cursor = None
    while True:
        headers = {
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=lavka_android',
        }
        request_body = {
            'text': 'some-query-text',
            'position': {'location': [0, 0]},
        }
        if cursor is not None:
            request_body['cursor'] = cursor
        if limit is not None:
            request_body['limit'] = limit

        response = await taxi_grocery_market_gw.post(
            path='/lavka/v1/market-gw/v1/market/search',
            headers=headers,
            json=request_body,
        )
        response_body = response.json()
        assert response.status_code == 200

        assert 'products' in response_body
        assert response_body['banner_url'] == banner_url
        assert response_body['results_url'] == results_url

        response_products.extend(response_body['products'])

        if 'cursor' not in response_body:
            break
        cursor = response_body['cursor']

    assert len(response_products) == len(products)
    equal_format_fields = [
        'type',
        'id',
        'title',
        'available',
        'image_url_templates',
        'market_product_url',
    ]
    for response_product, product_data, product in zip(
            response_products, products_data, products,
    ):
        for field in equal_format_fields:
            assert response_product[field] == product_data[field]
        assert 'pricing' in response_product
        assert (
            str(product.pricing.price)
            in response_product['pricing']['price_template']
        )
        if product.pricing.price != product.discount_pricing.price:
            assert 'discount_pricing' in response_product
        else:
            assert 'discount_pricing' not in response_product
        if 'RU_18+' in product.restrictions:
            assert 'ru_18+' in response_product['restrictions']
