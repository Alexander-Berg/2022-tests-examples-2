from tests_grocery_caas_promo import common

EMPTY_TREE = common.build_tree([])


async def test_basic(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': ['product_1', 'product_2'],
                },
                {
                    'id': 'subcategory_2',
                    'products': ['product-3', 'product_4'],
                },
            ],
        ),
    )
    grocery_discounts.add_cashback_discount(
        product_id='subcategory_1',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    grocery_discounts.add_cashback_discount(
        product_id='product_4',
        value_type='absolute',
        value='10',
        is_subcategory=False,
    )
    grocery_discounts.add_money_discount(
        product_id='product_3',
        value_type='absolute',
        value='10',
        is_subcategory=False,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/cashback',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'group_category-group-1',
        'product_1',
        'product_2',
        'cashback-other-products',
        'product_4',
    ]
    assert sorted(
        [item['product_id'] for item in response.json()['products']],
    ) == ['product_1', 'product_2', 'product_4']
    assert sorted(
        [item['subcategory_id'] for item in response.json()['subcategories']],
    ) == ['cashback-other-products', 'group_category-group-1']
    assert sorted(
        [item['tanker_key'] for item in response.json()['subcategories']],
    ) == ['cashback.other_products', 'category_group_title_1']


# отвечаем ошибкой если не получили скидки
async def test_cashback_category_discounts_unavailable(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_products,
        mockserver,
):
    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def _mock_grocery_discounts(request):
        assert set(request.json['hierarchy_names']) == {
            'menu_cashback',
            'bundle_cashback',
        }
        return mockserver.make_response(json={}, status=500)

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=EMPTY_TREE,
    )
    grocery_products.add_layout(test_id='1')
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/cashback',
        json=common.DISCOUNT_REQUEST,
    )

    assert response.status == 500
    assert response.json()['code'] == 'GROCERY_DISCOUNTS_ERROR'
