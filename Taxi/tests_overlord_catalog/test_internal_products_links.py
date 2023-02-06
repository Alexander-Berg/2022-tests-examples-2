import pytest

from testsuite.utils import ordered_object

from . import sql_queries

# POST /internal/v1/catalog/v1/products-links
# Проверяет, что ручка возвращает набор связей продуктов и категорий.
@pytest.mark.pgsql(
    'overlord_catalog', files=['links.sql', 'refresh_wms_views.sql'],
)
async def test_internal_catalog_products_links_returns_links(
        pgsql, taxi_overlord_catalog, load_json,
):

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-links',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200

    products = response.json()['products']
    ordered_object.assert_eq(
        products, load_json('response_links.json')['products'], [''],
    )

    assert len(products) == sql_queries.count_products(pgsql)


def is_sorted(indexable, key=lambda item: item):
    return all(
        key(indexable[i]) <= key(indexable[i + 1])
        for i in range(len(indexable) - 1)
    )


# POST /internal/v1/catalog/v1/products-links
# Проверяет ручку в "потоковом" режиме.
@pytest.mark.pgsql(
    'overlord_catalog', files=['wms_menu_data.sql', 'refresh_wms_views.sql'],
)
async def test_internal_catalog_products_links_in_chunked_mode(
        pgsql, taxi_overlord_catalog, load_json,
):

    response_len = [100, 52, 0]
    products = []
    limit = 100
    cursor = 0
    for length in response_len:
        response = await taxi_overlord_catalog.post(
            '/internal/v1/catalog/v1/products-links',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            # Индекс не изменился для "пустого", завершающего "поточную"
            # передачу ответа.
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['products']) == length
        products.extend(response.json()['products'])

    def get_product_id(product):
        return product['product_id']

    # Возвращаются в отсортированном порядке
    assert is_sorted(products, get_product_id)

    # Ни одна запись не возвращается более одного раза
    assert len(products) == len(set(map(get_product_id, products)))

    # Возвращается в полном объеме
    assert len(products) == sum(response_len)
    assert len(products) == sql_queries.count_products(pgsql)
