import pytest

from . import common
from . import experiments


# Проверяем выдачу ручку при разных лимитах, на "регулярных" категориях
@pytest.mark.parametrize(
    'category_limit,expected_results',
    [
        # берем только первый продукт из первой подкатегории
        pytest.param(
            1,
            [
                'virtual-category-1',
                'product-1',
                'virtual-category-2',
                'product-4',
            ],
            id='1 item',
        ),
        # берем по одному продукту из каждой подкатегории
        pytest.param(
            2,
            [
                'virtual-category-1',
                'product-1',
                'product-7',
                'virtual-category-2',
                'product-4',
                'product-5',
            ],
            id='2 items',
        ),
        # берем все продукты
        pytest.param(
            20,
            [
                'virtual-category-1',
                'product-1',
                'product-7',
                'product-2',
                'product-8',
                'product-3',
                'virtual-category-2',
                'product-4',
                'product-5',
                'product-6',
            ],
            id='20 items',
        ),
    ],
)
async def test_modes_category_group_shortcut_regular_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        category_limit,
        expected_results,
):
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(
        test_id='1',
        layout_meta='{'
        + f'"products_per_category_count": {category_limit}'
        + '}',
    )
    virtual_category_1 = category_group.add_virtual_category(
        test_id='1', add_short_title=True,
    )
    virtual_category_2 = category_group.add_virtual_category(
        test_id='2', add_short_title=True,
    )
    virtual_category_1.add_subcategory(subcategory_id='category-1')
    virtual_category_1.add_subcategory(subcategory_id='category-3')
    virtual_category_2.add_subcategory(subcategory_id='category-2')
    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': ['product-1', 'product-2', 'product-3'],
            },
            {
                'id': 'category-2',
                'products': ['product-4', 'product-5', 'product-6'],
            },
            {'id': 'category-3', 'products': ['product-7', 'product-8']},
        ],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group-shortcut',
        json={
            'modes': ['grocery'],
            'position': {'location': common.DEFAULT_LOCATION},
            'layout_id': layout.layout_id,
            'group_id': category_group.category_group_id,
        },
    )
    assert response.status_code == 200
    items = response.json()['modes'][0]['items']
    items = [item['id'] for item in items]
    assert items == expected_results
    assert items == [product['id'] for product in response.json()['products']]
    assert ['virtual-category-1', 'virtual-category-2'] == [
        item['id']
        for item in response.json()['modes'][0]['items']
        if item['type'] == 'carousel'
    ]
    assert ['virtual-category-1', 'virtual-category-2'] == [
        product['id']
        for product in response.json()['products']
        if product['type'] == 'category'
    ]
    assert response.json()['category_group']['id'] == 'category-group-1'


# Проверяем выдачу ручку при разных лимитах, на специальных категориях -
# кэшбек и промо
@experiments.CASHBACK_EXPERIMENT
@experiments.UPSALE_EXPERIMENT
@experiments.PROMO_CAAS_EXPERIMENT
@pytest.mark.parametrize(
    'category_limit,expected_results',
    [
        # берем только первый продукт из первой подкатегории
        pytest.param(
            1,
            [
                'virtual-category-promo',
                'product-1',
                'virtual-category-cashback',
                'product-6',
                'virtual-category-upsale',
                'product-3',
            ],
            id='1 item',
        ),
        # берем по одному продукту из каждой подкатегории
        pytest.param(
            2,
            [
                'virtual-category-promo',
                'product-1',
                'product-3',
                'virtual-category-cashback',
                'product-6',
                'product-7',
                'virtual-category-upsale',
                'product-3',
                'product-5',
            ],
            id='2 items',
        ),
        # берем все продукты
        pytest.param(
            20,
            [
                'virtual-category-promo',
                'product-1',
                'product-3',
                'product-2',
                'product-4',
                'product-5',
                'virtual-category-cashback',
                'product-6',
                'product-7',
                'product-8',
                'virtual-category-upsale',
                'product-3',
                'product-5',
            ],
            id='20 items',
        ),
    ],
)
async def test_modes_category_group_shortcut_special_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        category_limit,
        expected_results,
        grocery_upsale,
        grocery_caas_promo,
        grocery_p13n,
):
    for i in range(1, 9):
        grocery_p13n.add_modifier(product_id=f'product-{i}', value='1.0')
    grocery_caas_promo.add_subcategory(
        subcategory_id='money-discounts-1', title_tanker_key='key',
    )
    grocery_caas_promo.add_products(product_ids=['product-1', 'product-2'])
    grocery_caas_promo.add_subcategory(
        subcategory_id='money-discounts-2', title_tanker_key='key',
    )
    grocery_caas_promo.add_products(
        product_ids=['product-3', 'product-4', 'product-5'],
    )

    grocery_caas_promo.add_subcategory(
        subcategory_id='cashback-discounts',
        title_tanker_key='key',
        is_cashback=True,
    )
    grocery_caas_promo.add_products(
        product_ids=['product-6', 'product-7', 'product-8'], is_cashback=True,
    )

    grocery_upsale.add_products(['product-3', 'product-5'])

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(
        test_id='1',
        layout_meta='{'
        + f'"products_per_category_count": {category_limit}'
        + '}',
    )
    category_group.add_virtual_category(
        test_id='promo', special_category='promo-caas',
    )
    category_group.add_virtual_category(
        test_id='cashback', special_category='cashback-caas',
    )
    category_group.add_virtual_category(
        test_id='upsale', special_category='upsale',
    )

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': [f'product-{i}' for i in range(1, 9)],
            },
        ],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group-shortcut',
        json={
            'modes': ['grocery'],
            'position': {'location': common.DEFAULT_LOCATION},
            'layout_id': layout.layout_id,
            'group_id': category_group.category_group_id,
        },
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    items = response.json()['modes'][0]['items']
    items = [item['id'] for item in items]
    assert grocery_upsale.times_called == 1
    assert items == expected_results
    assert items == [product['id'] for product in response.json()['products']]
