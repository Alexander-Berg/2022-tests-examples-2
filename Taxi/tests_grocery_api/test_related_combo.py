# pylint: disable=import-error
from grocery_mocks import grocery_menu as mock_grocery_menu
from grocery_mocks import grocery_p13n as p13n
import pytest

from . import common


def _enable_combo_v2(value):
    return pytest.mark.experiments3(
        name='grocery_enable_combo_products',
        consumers=['grocery-api/modes'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {'type': 'true'},
                'value': {'enabled': False, 'enabled_combo_v2': value},
            },
        ],
        default_value={'enabled': False, 'enabled_combo_v2': False},
    )


ENABLE_COMBO_V2 = _enable_combo_v2(True)

DISABLE_COMBO_V2 = _enable_combo_v2(False)

COMBO_ID = 'meta-product-1'

DEFAULT_REQUEST = {
    'modes': ['grocery'],
    'position': {'location': common.DEFAULT_LOCATION},
    'category_path': {'layout_id': 'layout-1', 'group_id': 'category-group-1'},
    'category_id': 'virtual-category-1',
}

DEFAULT_PRODUCT_REQUEST = {
    'position': {'location': common.DEFAULT_LOCATION},
    'product_id': 'product-1',
}


def _add_discounts(grocery_p13n, products):
    for product in products:
        grocery_p13n.add_modifier(
            product_id=product,
            value='10',
            value_type=p13n.DiscountValueType.RELATIVE,
        )


def _prepare_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
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

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {'id': 'category-1', 'products': [COMBO_ID]},
            {
                'id': 'category-2',
                'products': [
                    'product-1',
                    'product-2',
                    'product-3',
                    'product-4',
                ],
            },
        ],
        product_prices=prices,
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


@ENABLE_COMBO_V2
async def test_combo_single_selection_related(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    product_group_1 = mock_grocery_menu.ProductGroup(True, 1, ['product-1'])
    product_group_2 = mock_grocery_menu.ProductGroup(True, 1, ['product-2'])
    product_group_3 = mock_grocery_menu.ProductGroup(True, 1, ['product-3'])
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [product_group_1, product_group_2, product_group_3],
            'combo_revision',
        ),
    )
    _prepare_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )
    _add_discounts(grocery_p13n, ['product-1', 'product-2', 'product-3'])

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200

    combo_response = response.json()['related_combo']
    assert {item['id'] for item in combo_response['content']} == {
        'product-2',
        'product-3',
    }
    assert len(combo_response['combo']) == 1
    combo = combo_response['combo'][0]
    assert combo['product_ids'] == ['product-1', 'product-2', 'product-3']
    assert combo['type'] == 'single_selection_combo'


# если нельзя собрать комбо то он не появится на карточке товара
@ENABLE_COMBO_V2
async def test_combo_single_selection_related_missing(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    product_group_1 = mock_grocery_menu.ProductGroup(True, 1, ['product-1'])
    product_group_2 = mock_grocery_menu.ProductGroup(True, 1, ['product-2'])
    product_group_3 = mock_grocery_menu.ProductGroup(True, 1, ['product-3'])
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [product_group_1, product_group_2, product_group_3],
            'combo_revision',
        ),
    )
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-2', '0')],
    )
    _add_discounts(grocery_p13n, ['product-1', 'product-2', 'product-3'])

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    assert 'related_combo' not in response.json()


@ENABLE_COMBO_V2
async def test_non_unique_selection_combo_product_related(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2', 'product-3'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'non_unique_selection_combo',
            [COMBO_ID],
            [product_group],
            'combo_revision',
        ),
    )

    price_1 = '10'
    price_2 = '50'
    price_3 = '100'

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', price_1),
            ('product-2', price_2),
            ('product-3', price_3),
        ],
        stocks=None,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    combo_response = response.json()['related_combo']
    assert {item['id'] for item in combo_response['content']} == {
        'product-2',
        'product-3',
    }
    assert len(combo_response['combo']) == 1
    combo = combo_response['combo'][0]
    assert combo['product_ids'] == ['product-1', 'product-2', 'product-3']
    assert combo['type'] == 'non_unique_selection_combo'


@pytest.mark.translations(
    pigeon_combo_groups={'title_tanker_key': {'en': 'group title'}},
)
@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_product_related(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    _prepare_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'product_id': 'product-4',
        },
    )
    assert response.status_code == 200
    combo_response = response.json()['related_combo']
    assert {item['id'] for item in combo_response['content']} == {
        'product-1',
        'product-2',
        'product-3',
    }
    assert len(combo_response['combo']) == 1
    combo = combo_response['combo'][0]
    assert combo['groups'] == [
        {'products': ['product-4', 'product-3'], 'title': 'group title'},
        {'products': ['product-1', 'product-2'], 'title': 'group title'},
    ]
    assert combo['type'] == 'single_selection_in_group_combo'


# если некоторые товары отсутсвуют, но при этом можно составить комбо
# товары для комбо уходят с available=false
@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_missing_products(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-2', '0'), ('product-4', '0')],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    combo_response = response.json()['related_combo']
    assert {
        (item['id'], item['available']) for item in combo_response['content']
    } == {('product-2', False), ('product-3', True), ('product-4', False)}


@ENABLE_COMBO_V2
async def test_multiple_combos(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    product_group_1 = mock_grocery_menu.ProductGroup(True, 1, ['product-1'])
    product_group_2 = mock_grocery_menu.ProductGroup(True, 1, ['product-2'])
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    product_group_3 = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-3'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'non_unique_selection_combo',
            [COMBO_ID],
            [product_group_3],
            'combo_revision',
        ),
    )

    product_group_4 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'],
    )
    product_group_5 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_4, product_group_5],
            'combo_revision',
        ),
    )

    _prepare_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )
    _add_discounts(grocery_p13n, ['product-1', 'product-2', 'product-3'])

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200

    combo_response = response.json()['related_combo']
    assert {item['id'] for item in combo_response['content']} == {
        'product-2',
        'product-3',
        'product-4',
    }
    assert len(combo_response['combo']) == 3
    assert {combo_item['type'] for combo_item in combo_response['combo']} == {
        'single_selection_combo',
        'non_unique_selection_combo',
        'single_selection_in_group_combo',
    }
