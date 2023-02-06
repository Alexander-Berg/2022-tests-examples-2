# pylint: disable=import-error
from grocery_mocks import grocery_menu as mock_grocery_menu
from grocery_mocks import grocery_p13n as p13n
import pytest

from . import combo_products_common
from . import common
from . import experiments

DEFAULT_REQUEST = {
    'modes': ['grocery'],
    'position': {'location': common.DEFAULT_LOCATION},
    'category_path': {'layout_id': 'layout-1', 'group_id': 'category-group-1'},
    'category_id': 'virtual-category-1',
}

DEFAULT_PRODUCT_REQUEST = {
    'position': {'location': common.DEFAULT_LOCATION},
    'product_id': combo_products_common.COMBO_ID,
}


# Проверяем, что на бандлы применяются скидки в modes/category
@experiments.ENABLE_COMBO_V2
@pytest.mark.translations(
    pigeon_combo_groups={'title_tanker_key': {'en': 'group title'}},
)
async def test_category_bundle_discounts_v2(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
):
    grocery_p13n.add_bundle_v2_modifier(
        value=10, bundle_id='single_selection_in_group_combo',
    )
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [combo_products_common.COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    combo_products_common.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '100'),
            ('product-2', '100'),
            ('product-3', '100'),
            ('product-4', '100'),
        ],
        stocks=None,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200

    combo_layout_item = combo_products_common.find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'

    combo_product = combo_products_common.find_combo_product(response)
    assert combo_product['combo'] == load_json(
        'single_selection_in_group_combo.json',
    )


# Проверяем, что на бандлы применяются скидки в modes/product
@experiments.ENABLE_COMBO_V2
@pytest.mark.translations(
    pigeon_combo_groups={'title_tanker_key': {'en': 'group title'}},
)
async def test_product_bundle_discounts_v2(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
):
    grocery_p13n.add_bundle_v2_modifier(
        value=10, bundle_id='single_selection_in_group_combo',
    )
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [combo_products_common.COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    combo_products_common.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '100'),
            ('product-2', '100'),
            ('product-3', '100'),
            ('product-4', '100'),
        ],
        stocks=None,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['product']['combo'] == load_json(
        'single_selection_in_group_combo.json',
    )


# Проверяем, что относительные и абсолютные скидки применяются корректно
# Для абсолютной 20, для относительной 10% * 200 = 20
@pytest.mark.parametrize(
    'discount_value,value_type',
    [
        pytest.param(10, p13n.DiscountValueType.RELATIVE, id='relative'),
        pytest.param(20, p13n.DiscountValueType.ABSOLUTE, id='absolute'),
    ],
)
@experiments.ENABLE_COMBO_V2
async def test_bundle_discounts_v2_by_type(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        discount_value,
        value_type,
):
    grocery_p13n.add_bundle_v2_modifier(
        value=discount_value,
        bundle_id='single_selection_in_group_combo',
        value_type=value_type,
    )
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [combo_products_common.COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    combo_products_common.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '100'),
            ('product-2', '100'),
            ('product-3', '100'),
            ('product-4', '100'),
        ],
        stocks=None,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200

    combo_layout_item = combo_products_common.find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'

    selected_combo = combo_products_common.find_combo_product(response)[
        'combo'
    ]['selected_combo']
    assert len(selected_combo) == 4
    for combo in selected_combo:
        assert int(combo['discount_pricing']['price']) + 20 == int(
            combo['pricing']['price'],
        )


@pytest.mark.parametrize(
    'discount_value,value_type,is_custom_label',
    [
        pytest.param(
            10, p13n.DiscountValueType.RELATIVE, False, id='relative',
        ),
        pytest.param(
            100, p13n.DiscountValueType.ABSOLUTE, False, id='absolute',
        ),
        pytest.param(10, p13n.DiscountValueType.RELATIVE, True, id='custom'),
    ],
)
@pytest.mark.translations(
    discount_descriptions={'custom_discount_label': {'ru': 'скидка на набор'}},
)
@experiments.ENABLE_COMBO_V2
@experiments.USE_AUTOMATIC_DISCOUNT_LABEL
async def test_combo_discounts_stickers(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        discount_value,
        value_type,
        is_custom_label,
):
    grocery_p13n.add_bundle_v2_modifier(
        value=discount_value,
        bundle_id='single_selection_in_group_combo',
        value_type=value_type,
        meta={'title_tanker_key': 'custom_discount_label'}
        if is_custom_label
        else None,
    )
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [combo_products_common.COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    combo_products_common.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '100'),
            ('product-2', '200'),
            ('product-3', '300'),
            ('product-4', '400'),
        ],
        stocks=None,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=DEFAULT_REQUEST,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    product = combo_products_common.find_combo_product(response)
    selected_combo = product['combo']['selected_combo']
    assert len(selected_combo) == 4
    for combo in selected_combo:
        assert 'label_color' in combo['discount_pricing']
        discount_label = combo['discount_pricing']['discount_label']
        if is_custom_label:
            assert discount_label == 'скидка на набор'
        elif value_type == p13n.DiscountValueType.RELATIVE:
            assert discount_label == f'-{discount_value}%'
        elif value_type == p13n.DiscountValueType.ABSOLUTE:
            percent = int(
                100 * discount_value / int(combo['pricing']['price']),
            )
            assert discount_label == f'-{percent}%'
    assert 'discount_label' in product['discount_pricing']
    assert 'label_color' in product['discount_pricing']


# Если тип комбо non_unique_selection_combo, и на него есть скидка
# c кастомным лейблом, то этот лейбл так же показывается на товарах
# составляющих комбо и перетерает автоматический лейбл
@pytest.mark.parametrize(
    'add_product_discount', [pytest.param(False), pytest.param(True)],
)
@pytest.mark.translations(
    discount_descriptions={'custom_discount_label': {'ru': 'скидка на набор'}},
)
@experiments.ENABLE_COMBO_V2
@experiments.USE_AUTOMATIC_DISCOUNT_LABEL
async def test_combo_discounts_stickers_on_nested(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        add_product_discount,
):
    grocery_p13n.add_bundle_v2_modifier(
        value=10,
        bundle_id='non_unique_selection',
        value_type=p13n.DiscountValueType.RELATIVE,
        meta={'title_tanker_key': 'custom_discount_label'},
    )

    if add_product_discount:
        grocery_p13n.add_modifier(
            product_id='product-1',
            value='10',
            value_type=p13n.DiscountValueType.RELATIVE,
        )

    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'non_unique_selection',
            [combo_products_common.COMBO_ID],
            [product_group],
            'combo_revision',
        ),
    )

    combo_products_common.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'product_id': 'product-1',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    nested_products = response.json()['related_combo']['content']
    pricing = [
        nested_product['discount_pricing']
        for nested_product in nested_products
    ]
    pricing.append(response.json()['product']['discount_pricing'])
    assert len(pricing) == 2
    for product_pricing in pricing:
        assert product_pricing['discount_label'] == 'скидка на набор'
        assert 'label_color' in product_pricing
