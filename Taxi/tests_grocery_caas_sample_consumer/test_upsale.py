import pytest

CATEGORY_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_caas_upsale',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)

# Проверяем что выдает grocery_caas_upsale
@CATEGORY_EXPERIMENT
async def test_caas_upsale(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_upsale,
        default_auth_headers,
):
    response = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'store11xx', 'category': 'upsale'},
        headers=default_auth_headers,
    )

    expected_products = ['product-3', 'product-5', 'product-7', 'product-8']

    assert grocery_caas_upsale.times_called == 1
    assert response.status_code == 200

    products = [
        product['product_id'] for product in response.json()['products']
    ]
    assert products == expected_products
