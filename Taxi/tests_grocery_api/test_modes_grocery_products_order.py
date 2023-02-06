import pytest

from . import common


def _generate_category_tree_products(ranks):
    products = []
    for idx, rank in enumerate(ranks):
        products.append(
            {
                'full_price': '5.0',
                'id': 'product-' + str(idx),
                'category_ids': ['product-category'],
                'rank': rank[0],
                'ranks': rank,
            },
        )
    return products


def _generate_products(overlord_catalog, ranks, category_id):
    overlord_catalog.add_category_tree(
        depot_id=common.DEFAULT_DEPOT_ID,
        category_tree={
            'categories': [{'id': category_id}],
            'products': _generate_category_tree_products(ranks),
            'markdown_products': [],
        },
    )
    for idx, _ in enumerate(ranks):
        overlord_catalog.add_products_data(
            new_products_data=[
                {
                    'description': 'product-description',
                    'image_url_template': 'product-image-url-template',
                    'long_title': 'product-long-title',
                    'product_id': 'product-' + str(idx),
                    'title': 'product-title',
                },
            ],
        )
        overlord_catalog.add_products_stocks(
            depot_id=common.DEFAULT_DEPOT_ID,
            new_products_stocks=[
                {
                    'in_stock': '10',
                    'product_id': 'product-' + str(idx),
                    'quantity_limit': '5',
                },
            ],
        )


# проверяем, что продукты сортируются в соовествии с экспериментом
@pytest.mark.parametrize(
    'test_handler',
    [
        pytest.param(
            '/lavka/v1/api/v1/modes/category-group', id='category_group',
        ),
        pytest.param('/lavka/v1/api/v1/modes/category', id='category'),
    ],
)
@pytest.mark.parametrize(
    'ranks,expected_order,exp_value',
    [
        pytest.param(
            [[10, 1], [9, 2], [8, 3], [7, 4]],
            ['product-3', 'product-2', 'product-1', 'product-0'],
            None,
            id='sort_by_rank_0',
        ),
        pytest.param(
            [[10, 1], [9, 2], [8, 3], [7, 4]],
            ['product-3', 'product-2', 'product-1', 'product-0'],
            0,
            id='sort_by_rank_1',
        ),
        pytest.param(
            [[10, 1], [9, 2], [8, 3], [7, 4]],
            ['product-0', 'product-1', 'product-2', 'product-3'],
            1,
            id='sort_by_rank_2',
        ),
        # тест на fallback:
        pytest.param(
            [[10], [9, 2], [8, 3], [7, 4]],
            ['product-1', 'product-2', 'product-3', 'product-0'],
            1,
            id='sort_by_rank_3',
        ),
        pytest.param(
            [[10], [5], [5]],
            ['product-1', 'product-2', 'product-0'],
            None,
            id='sort_by_rank_4',
        ),
    ],
)
async def test_modes_grocery_products_order(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        experiments3,
        test_handler,
        ranks,
        expected_order,
        exp_value,
):
    if exp_value is not None:
        experiments3.add_experiment(
            name='grocery_api_products_order',
            consumers=['grocery-api/modes'],
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': True, 'order_index': exp_value},
                },
            ],
        )

    category_id = 'product-category'
    overlord_catalog.add_categories_data(
        new_categories_data=[
            {
                'category_id': category_id,
                'description': 'product-category-description',
                'image_url_template': 'product-category-image-url-template',
                'title': 'product-category-title',
            },
        ],
    )
    _generate_products(overlord_catalog, ranks, category_id)
    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='test-group')
    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='test-category',
    )
    virtual_category_1.add_subcategory(subcategory_id=category_id)

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            virtual_category_1.virtual_category_id,
        ),
    )
    assert response.status_code == 200
    items = response.json()['modes'][0]['items']
    items = [item['id'] for item in items if item['type'] == 'good']
    assert items == expected_order
