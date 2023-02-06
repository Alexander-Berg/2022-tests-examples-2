from grocery_mocks import (  # pylint: disable=E0401
    grocery_menu as mock_grocery_menu,
)

from . import common

COMBO_ID = 'meta-product-1'

PRODUCT_GROUP1 = mock_grocery_menu.ProductGroup(True, 1, ['product-1'])
PRODUCT_GROUP2 = mock_grocery_menu.ProductGroup(True, 1, ['product-2'])
PRODUCT_GROUP3 = mock_grocery_menu.ProductGroup(True, 1, ['product-3'])


def prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=None,
        parent_products=None,
        combos_ids=None,
):
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1')

    prices = None
    if product_prices:
        prices = [
            {'id': product_id, 'price': price}
            for product_id, price in product_prices
        ]

    if combos_ids is None:
        combos_ids = [COMBO_ID]

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {'id': 'category-1', 'products': combos_ids},
            {
                'id': 'category-2',
                'products': [
                    'product-1',
                    'product-2',
                    'product-3',
                    'product-4',
                    'product-5',
                ],
            },
        ],
        product_prices=prices,
        parent_products=parent_products,
    )
    if stocks:
        overlord_catalog.add_products_stocks(
            depot_id=common.DEFAULT_DEPOT_ID,
            new_products_stocks=[
                {
                    'in_stock': quantity,
                    'product_id': product_id,
                    'quantity_limit': quantity,
                }
                for product_id, quantity in stocks
            ],
        )


def find_combo_product(response):
    return next(
        item for item in response.json()['products'] if item['id'] == COMBO_ID
    )


def find_combo_layout_item(response):
    return next(
        item
        for item in response.json()['modes'][0]['items']
        if item['id'] == COMBO_ID
    )
