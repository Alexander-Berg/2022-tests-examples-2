# pylint: disable=E0401

from grocery_mocks import grocery_menu as mock_grocery_menu

from tests_grocery_cart import experiments


@experiments.ENABLE_BUNDLE_DISCOUNT_V2
async def test_combo_log(overlord_catalog, grocery_menu, testpoint, cart):
    products = {
        'product_1': {'p': '100', 'q': '2'},
        'product_2': {'p': '100', 'q': '1'},
        'product_3': {'p': '100', 'q': '3'},
    }

    for product_id, data in products.items():
        overlord_catalog.add_product(product_id=product_id, price=data['p'])
    await cart.modify(products)

    combo_1 = 'combo_1'
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_1,
            ['some_product'],
            [
                mock_grocery_menu.ProductGroup(
                    True, 1, ['product_1', 'product_2'], 'group_title',
                ),
                mock_grocery_menu.ProductGroup(
                    True, 1, ['product_3', 'product_4'], 'group_title',
                ),
            ],
            'revision_1',
        ),
    )

    @testpoint('cart_combo_log')
    def cart_combo_log(cart_log):
        assert cart_log == {
            'cart_combo': [
                {
                    'combo_id': 'combo_1',
                    'revision': 'revision_1',
                    'meta_products': ['some_product'],
                    'combo_items': [
                        {
                            'products': [
                                {'product_id': 'product_1', 'quantity': '1'},
                                {'product_id': 'product_3', 'quantity': '1'},
                            ],
                            'count': '2',
                        },
                        {
                            'products': [
                                {'product_id': 'product_2', 'quantity': '1'},
                                {'product_id': 'product_3', 'quantity': '1'},
                            ],
                            'count': '1',
                        },
                    ],
                },
            ],
        }

    await cart.checkout()
    assert cart_combo_log.times_called == 1
