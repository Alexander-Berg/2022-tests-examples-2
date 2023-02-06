import pytest

from . import common
from . import const
from . import experiments


def _generate_category_tree_products(ranks, category_id):
    products = []
    for idx, rank in enumerate(ranks):
        products.append(
            {
                'full_price': '5.0',
                'id': 'product-' + str(idx),
                'category_ids': [category_id],
                'rank': rank,
            },
        )
    return products


def _generate_products(overlord_catalog, category_id):
    ranks = [10, 20, 30]
    overlord_catalog.add_category_tree(
        depot_id=common.DEFAULT_DEPOT_ID,
        category_tree={
            'categories': [{'id': category_id}],
            'products': _generate_category_tree_products(ranks, category_id),
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


@experiments.GROCERY_PRODUCTS_SMALL_CARDS
@common.HANDLERS
@pytest.mark.parametrize(
    'category_id,width,height', [('1', 3, 4), ('2', 2, 4)],
)
async def test_modes_products_small_cards(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        category_id,
        width,
        height,
        test_handler,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(
        test_id=category_id, add_short_title=True,
    )
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            category_group.category_group_id,
            virtual_category.virtual_category_id,
        ),
    )
    assert response.status_code == 200
    for item in response.json()['modes'][0]['items']:
        if item['type'] == 'good':
            assert item['width'] == width
            assert item['height'] == height


@common.HANDLERS
@experiments.GROCERY_PRODUCTS_BIG_CARDS
@experiments.GROCERY_PRODUCTS_SMALL_CARDS
@pytest.mark.parametrize(
    'category_id, small_width, small_height,'
    'big_width, big_height, expected_order',
    [
        ('1', 3, 4, 6, 3, ['product-2', 'product-0', 'product-1']),
        ('2', 2, 4, 2, 4, ['product-0', 'product-1', 'product-2']),
        ('3', 2, 4, 6, 3, ['product-2', 'product-0', 'product-1']),
    ],
)
async def test_modes_products_big_and_small(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        category_id,
        small_width,
        small_height,
        big_width,
        big_height,
        expected_order,
        test_handler,
):
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
    _generate_products(overlord_catalog, category_id)
    layout = grocery_products.add_layout(test_id='test_layout')
    category_group = layout.add_category_group(test_id='test-group')
    virtual_category = category_group.add_virtual_category(test_id=category_id)
    virtual_category.add_subcategory(subcategory_id=category_id)

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            virtual_category.virtual_category_id,
        ),
    )
    assert response.status_code == 200

    items = response.json()['modes'][0]['items']
    items = [item['id'] for item in items if item['type'] == 'good']
    assert items == expected_order

    for item in response.json()['modes'][0]['items']:
        if item['type'] == 'good':
            if item['id'] == 'product-2':
                assert item['width'] == big_width
                assert item['height'] == big_height
            else:
                assert item['width'] == small_width
                assert item['height'] == small_height
