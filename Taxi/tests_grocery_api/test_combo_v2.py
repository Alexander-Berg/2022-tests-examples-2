# pylint: disable=import-error
# pylint: disable=too-many-lines

from grocery_mocks import grocery_menu as mock_grocery_menu
from grocery_mocks import grocery_p13n as p13n
import pytest

from . import combo_products_common as common_combo
from . import common
from . import experiments


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

COMBO_ID = common_combo.COMBO_ID

DEFAULT_REQUEST = {
    'modes': ['grocery'],
    'position': {'location': common.DEFAULT_LOCATION},
    'category_path': {'layout_id': 'layout-1', 'group_id': 'category-group-1'},
    'category_id': 'virtual-category-1',
}

DEFAULT_PRODUCT_REQUEST = {
    'position': {'location': common.DEFAULT_LOCATION},
    'product_id': COMBO_ID,
}

COMBO_STICKER = {
    'sticker_color': 'yellow',
    'text': 'combo-sticker',
    'text_color': 'white',
}

PRODUCT_GROUP1 = common_combo.PRODUCT_GROUP1
PRODUCT_GROUP2 = common_combo.PRODUCT_GROUP2
PRODUCT_GROUP3 = common_combo.PRODUCT_GROUP3


def _add_discounts(grocery_p13n, products):
    for product in products:
        grocery_p13n.add_modifier(
            product_id=product,
            value='10',
            value_type=p13n.DiscountValueType.RELATIVE,
        )


def _find_combo_product(response):
    try:
        return next(
            item
            for item in response.json()['products']
            if item['id'] == COMBO_ID
        )
    except StopIteration:
        return None


def _find_combo_layout_item(response):
    try:
        return next(
            item
            for item in response.json()['modes'][0]['items']
            if item['id'] == COMBO_ID
        )
    except StopIteration:
        return None


@ENABLE_COMBO_V2
async def test_combo_single_selection(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision',
        ),
    )
    price_1 = '10'
    price_2 = '50'
    price_3 = '100'
    quantity_limit_1 = '2'
    quantity_limit_2 = '3'
    quantity_limit_3 = '4'
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', price_1),
            ('product-2', price_2),
            ('product-3', price_3),
        ],
        stocks=[
            ('product-1', quantity_limit_1),
            ('product-2', quantity_limit_2),
            ('product-3', quantity_limit_3),
        ],
    )
    _add_discounts(grocery_p13n, ['product-1', 'product-2', 'product-3'])

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200

    combo_layout_item = _find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'

    combo_product = _find_combo_product(response)

    assert combo_product['quantity_limit'] == str(
        min(
            int(quantity_limit_1),
            int(quantity_limit_2),
            int(quantity_limit_3),
        ),
    )
    combo_sum = int(price_1) + int(price_2) + int(price_3)
    discount_price = int(combo_sum * 0.9)

    assert combo_product['pricing']['price'] == str(combo_sum)
    assert combo_product['discount_pricing']['price'] == str(discount_price)

    assert combo_product['combo'] == {
        'product_ids': ['product-1', 'product-2', 'product-3'],
        'selected_combo': {
            'discount_pricing': {
                'price': f'{discount_price}',
                'price_template': f'{discount_price} $SIGN$$CURRENCY$',
            },
            'pricing': {
                'price': f'{combo_sum}',
                'price_template': f'{combo_sum} $SIGN$$CURRENCY$',
            },
            'products': [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-2', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 1},
            ],
        },
        'type': 'single_selection_combo',
    }
    assert [
        item['id']
        for item in response.json()['products']
        if item['type'] == 'good'
    ] == ['meta-product-1', 'product-1', 'product-2', 'product-3']


# если нет какого либо составлющего комбо, комбо не возвращается в ответе ручки
@ENABLE_COMBO_V2
async def test_combo_single_selection_nested_absent(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-1', '0')],
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200
    assert not any(
        item['type'] == 'good' for item in response.json()['products']
    )


@ENABLE_COMBO_V2
@pytest.mark.translations(
    pigeon_combo_groups={'group-title': {'en': 'products group'}},
)
async def test_non_unique_selection_combo(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        load_json,
):
    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2', 'product-3'], 'group-title',
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

    common_combo.prepare_combo_test_context(
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
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200

    combo_layout_item = _find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'

    combo_product = _find_combo_product(response)
    assert combo_product['combo'] == {
        'product_ids': ['product-1', 'product-2', 'product-3'],
        'title': 'products group',
        'type': 'non_unique_selection_combo',
    }


# есть остатки только для одного составляющего комбо товар
@ENABLE_COMBO_V2
async def test_non_unique_selection_not_enough_products(
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

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-1', '1'), ('product-2', '0'), ('product-3', '0')],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200
    assert not any(
        item['type'] == 'good' for item in response.json()['products']
    )


@pytest.mark.translations(
    pigeon_combo_groups={
        'first-group-tanker-key': {'en': 'first group'},
        'second-group-tanker-key': {'en': 'second group'},
    },
)
@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        load_json,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'], 'first-group-tanker-key',
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'], 'second-group-tanker-key',
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
            ('product-4', '300'),
        ],
        stocks=None,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200

    combo_layout_item = _find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'

    combo_product = _find_combo_product(response)
    assert combo_product['combo'] == load_json(
        'single_selection_in_group_combo.json',
    )


@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_not_enough_products(
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

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[
            ('product-1', '2'),
            ('product-2', '2'),
            ('product-3', '0'),
            ('product-4', '0'),
        ],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200
    assert not any(
        item['type'] == 'good' for item in response.json()['products']
    )


@ENABLE_COMBO_V2
async def test_combo_single_selection_product(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision',
        ),
    )
    price_1 = '10'
    price_2 = '50'
    price_3 = '100'
    quantity_limit_1 = '2'
    quantity_limit_2 = '3'
    quantity_limit_3 = '4'
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', price_1),
            ('product-2', price_2),
            ('product-3', price_3),
        ],
        stocks=[
            ('product-1', quantity_limit_1),
            ('product-2', quantity_limit_2),
            ('product-3', quantity_limit_3),
        ],
    )
    _add_discounts(grocery_p13n, ['product-1', 'product-2', 'product-3'])

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200

    combo_product = response.json()['product']
    assert combo_product['quantity_limit'] == str(
        min(
            int(quantity_limit_1),
            int(quantity_limit_2),
            int(quantity_limit_3),
        ),
    )
    combo_sum = int(price_1) + int(price_2) + int(price_3)
    discount_price = int(combo_sum * 0.9)

    assert combo_product['pricing']['price'] == str(combo_sum)
    assert combo_product['discount_pricing']['price'] == str(discount_price)

    assert combo_product['combo'] == {
        'product_ids': ['product-1', 'product-2', 'product-3'],
        'selected_combo': {
            'discount_pricing': {
                'price': f'{discount_price}',
                'price_template': f'{discount_price} $SIGN$$CURRENCY$',
            },
            'pricing': {
                'price': f'{combo_sum}',
                'price_template': f'{combo_sum} $SIGN$$CURRENCY$',
            },
            'products': [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-2', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 1},
            ],
        },
        'type': 'single_selection_combo',
    }
    assert {item['id'] for item in response.json()['children']} == {
        'product-1',
        'product-2',
        'product-3',
    }


# при выключенном экспе возвращаем 404
@DISABLE_COMBO_V2
async def test_combo_product_exp_disabled(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision',
        ),
    )

    common_combo.prepare_combo_test_context(overlord_catalog, grocery_products)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 404


# если неудается собрать комбо возвращем 404
@ENABLE_COMBO_V2
async def test_combo_single_product_is_missing(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-1', '0')],
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 404


@ENABLE_COMBO_V2
@pytest.mark.translations(
    pigeon_combo_groups={'group-title': {'en': 'products group'}},
)
async def test_non_unique_selection_combo_product(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        load_json,
):
    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2', 'product-3'], 'group-title',
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

    common_combo.prepare_combo_test_context(
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
    combo_product = response.json()['product']
    assert combo_product['combo'] == {
        'product_ids': ['product-1', 'product-2', 'product-3'],
        'title': 'products group',
        'type': 'non_unique_selection_combo',
    }
    assert {item['id'] for item in response.json()['children']} == {
        'product-1',
        'product-2',
        'product-3',
    }


# для того чтобы собрать комбо нужно хотя бы 2 любых товара из
# тройки product-1 product-2 product-3
@ENABLE_COMBO_V2
@pytest.mark.parametrize(
    'product_count,status_code',
    [pytest.param('2', 200), pytest.param('1', 404)],
)
async def test_non_unique_selection_combo_availability(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        product_count,
        status_code,
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

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[
            ('product-1', product_count),
            ('product-2', '0'),
            ('product-3', '0'),
        ],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == status_code


@ENABLE_COMBO_V2
async def test_non_unique_selection_combo_not_in_stock(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        mockserver,
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

    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None,
    )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return {
            'stocks': [
                {
                    'in_stock': '10',
                    'product_id': 'product-1',
                    'quantity_limit': '5',
                },
            ],
        }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['product']['combo']['product_ids'] == ['product-1']


@pytest.mark.translations(
    pigeon_combo_groups={
        'first-group-tanker-key': {'en': 'first group'},
        'second-group-tanker-key': {'en': 'second group'},
    },
)
@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_product(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        load_json,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2'], 'first-group-tanker-key',
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-4'], 'second-group-tanker-key',
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
            ('product-4', '300'),
        ],
        stocks=None,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    combo_product = response.json()['product']
    assert combo_product['combo'] == load_json(
        'single_selection_in_group_combo.json',
    )
    assert {item['id'] for item in response.json()['children']} == {
        'product-1',
        'product-2',
        'product-3',
        'product-4',
    }


# если не удается собрать комбо возвращаем 404
@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_product_is_missing(
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

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-3', '0'), ('product-4', '0')],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 404


# продукты которых нет на складе возвращаются с флагом available=False
# невалидные комбинации не отправляются в selected_combo
@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_product_missing(
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

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-2', '0'), ('product-4', '0')],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    assert (
        {
            (item['id'], item['available'])
            for item in response.json()['children']
        }
        == {
            ('product-1', True),
            ('product-2', False),
            ('product-3', True),
            ('product-4', False),
        }
    )
    selected_combo = response.json()['product']['combo']['selected_combo']
    assert len(selected_combo) == 1
    assert selected_combo[0]['products'] == [
        {'product_id': 'product-1', 'quantity': 1},
        {'product_id': 'product-3', 'quantity': 1},
    ]


@ENABLE_COMBO_V2
async def test_single_selection_in_group_combo_product_not_in_stocks(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        mockserver,
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

    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None,
    )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return {
            'stocks': [
                {
                    'in_stock': '10',
                    'product_id': 'product-1',
                    'quantity_limit': '5',
                },
                {
                    'in_stock': '10',
                    'product_id': 'product-3',
                    'quantity_limit': '5',
                },
            ],
        }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    assert [
        group['products']
        for group in response.json()['product']['combo']['groups']
    ] == [['product-1'], ['product-3']]


# цена комботовара = цене первой валидной комбинации.
# первая валидная комбинация = первый валидный продукт из первой группы,
# первый валидный продукт из второй группы и т.д.
@ENABLE_COMBO_V2
@pytest.mark.parametrize(
    'absent_products,expected_selected_combo',
    [
        ([], ['product-3', 'product-4']),
        (['product-3', 'product-4'], ['product-1', 'product-5']),
        (['product-1', 'product-3'], ['product-2', 'product-4']),
    ],
)
async def test_combo_price_if_nested_absent(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        absent_products,
        expected_selected_combo,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-3', 'product-1', 'product-2'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-4', 'product-5'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    prices = {
        'product-1': '1',
        'product-2': '10',
        'product-3': '100',
        'product-4': '1000',
        'product-5': '10000',
    }

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=prices.items(),
        stocks=[(item, '0') for item in absent_products],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    product = response.json()['product']

    expected_combo_price = sum(
        [int(prices[product]) for product in expected_selected_combo],
    )
    assert product['pricing']['price'] == str(expected_combo_price)


# разобранные товары идут в конце группы
@ENABLE_COMBO_V2
async def test_combination_order_if_nested_absent(
        taxi_grocery_api, grocery_menu, overlord_catalog, grocery_products,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-2', 'product-3'],
    )
    product_group_2 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-4', 'product-5'],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_1, product_group_2],
            'combo_revision',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=[('product-1', '0'), ('product-2', '0'), ('product-4', '0')],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=DEFAULT_PRODUCT_REQUEST,
    )
    assert response.status_code == 200
    product = response.json()['product']
    assert product['combo']['groups'][0]['products'] == [
        'product-3',
        'product-1',
        'product-2',
    ]
    assert product['combo']['groups'][1]['products'] == [
        'product-5',
        'product-4',
    ]


@ENABLE_COMBO_V2
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'combo-sticker': {'sticker_color': 'yellow', 'text_color': 'white'},
    },
)
@pytest.mark.parametrize(
    'is_valid_combo,has_combo_discount',
    [(True, False), (False, True), (False, False), (True, True)],
)
async def test_combo_sticker_product(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        is_valid_combo,
        has_combo_discount,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=None if is_valid_combo else [('product-2', '0')],
    )

    if has_combo_discount:
        grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id='combo_id')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'product_id': 'product-1',
        },
    )
    assert response.status_code == 200
    product = response.json()['product']
    if is_valid_combo and has_combo_discount:
        assert product['stickers'] == [COMBO_STICKER]
    else:
        assert 'stickers' not in product


@ENABLE_COMBO_V2
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'non-unique-selection-combo-sticker': {
            'sticker_color': 'yellow',
            'text_color': 'white',
        },
    },
)
@pytest.mark.translations(
    virtual_catalog={
        'non-unique-selection-combo-sticker': {'ru': '%(value)s со скидкой'},
    },
)
async def test_combo_sticker_for_non_unique_selection(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    product_group_1 = mock_grocery_menu.ProductGroup(
        False, 3, ['product-1', 'product-2', 'product-3'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id', [COMBO_ID], [product_group_1], 'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )

    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id='combo_id')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'product_id': 'product-1',
        },
    )
    assert response.status_code == 200
    product = response.json()['product']
    assert product['stickers'] == [
        {
            'sticker_color': 'yellow',
            'text': '3 со скидкой',
            'text_color': 'white',
        },
    ]


@ENABLE_COMBO_V2
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'combo-sticker': {'sticker_color': 'yellow', 'text_color': 'white'},
    },
)
@pytest.mark.parametrize(
    'is_valid_combo,has_combo_discount',
    [(True, False), (False, True), (False, False), (True, True)],
)
async def test_combo_sticker_search(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        grocery_search,
        is_valid_combo,
        has_combo_discount,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=None,
        stocks=None if is_valid_combo else [('product-2', '0')],
    )

    if has_combo_discount:
        grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id='combo_id')

    grocery_search.add_product(product_id='product-1')
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': 'test-offer',
        },
    )
    assert response.status_code == 200
    product = response.json()['products'][0]
    if is_valid_combo and has_combo_discount:
        assert product['stickers'] == [COMBO_STICKER]
    else:
        assert 'stickers' not in product


@ENABLE_COMBO_V2
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'combo-sticker': {'sticker_color': 'yellow', 'text_color': 'white'},
    },
)
async def test_combo_sticker_upsale(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_upsale,
        grocery_menu,
        grocery_p13n,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )

    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id='combo_id')
    grocery_upsale.add_product('product-1')
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/upsale',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'products': ['product-2'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['items'][0]['products'][0]['id'] == 'product-1'
    assert data['items'][0]['products'][0]['stickers'] == [COMBO_STICKER]


@ENABLE_COMBO_V2
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'combo-sticker': {'sticker_color': 'yellow', 'text_color': 'white'},
    },
)
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_combo_stickers_root_carousel(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_menu,
        grocery_p13n,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id='combo_id')

    common.build_overlord_catalog_products(
        overlord_catalog,
        [{'id': 'category-1', 'products': ['product-1', 'product-2']}],
    )

    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    group.layout_meta = (
        group.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={
            'modes': ['grocery'],
            'position': {'location': common.DEFAULT_LOCATION},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    stikers = next(
        product['stickers']
        for product in response.json()['products']
        if product['id'] == 'product-1'
    )
    assert stikers == [COMBO_STICKER]


# если один из детей состоит в комбо, то на родительский товар
# добавляем стикер
@ENABLE_COMBO_V2
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'combo-sticker': {'sticker_color': 'yellow', 'text_color': 'white'},
    },
)
async def test_combo_sticker_on_parent(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[('product-3', '0')],
        stocks=[('product-3', '0')],
        parent_products={'product-3': ['product-1', 'product-4']},
    )
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id='combo_id')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'subcategory_id': 'category-2',
            'product_id': 'product-3',
        },
    )
    assert response.status_code == 200
    assert response.json()['children']
    product = response.json()['product']
    assert product['stickers'] == [COMBO_STICKER]


@ENABLE_COMBO_V2
@experiments.ENABLE_PERSONAL
@experiments.PROMO_CAAS_EXPERIMENT
@pytest.mark.parametrize('special_category', ['personal', 'promo-caas'])
async def test_combo_product_in_special_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_fav_goods,
        grocery_menu,
        grocery_caas_promo,
        special_category,
):
    grocery_caas_promo.add_products(product_ids=[COMBO_ID])
    grocery_fav_goods.add_favorite(
        yandex_uid=common.DEFAULT_UID, product_id=COMBO_ID,
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {'id': 'category-2', 'products': [COMBO_ID]},
            {'id': 'category-1', 'products': ['product-1', 'product-2']},
        ],
    )

    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    group.add_virtual_category(test_id='1', special_category=special_category)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=DEFAULT_REQUEST,
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    combo_layout_item = _find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'
    assert combo_layout_item['id'] == COMBO_ID


@ENABLE_COMBO_V2
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_combo_as_favorite_product(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_menu,
        grocery_fav_goods,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )

    grocery_fav_goods.add_favorite(common.DEFAULT_UID, COMBO_ID)
    grocery_fav_goods.add_favorite(common.DEFAULT_UID, 'product-1')
    grocery_fav_goods.add_favorite(common.DEFAULT_UID, 'product-2')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': common.DEFAULT_LOCATION},
            'product_id': COMBO_ID,
        },
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    product = response.json()['product']
    assert product['is_favorite']
    for child in response.json()['children']:
        assert child['is_favorite']


@ENABLE_COMBO_V2
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'selection-combo-sticker': {
            'sticker_color': 'yellow',
            'text_color': 'white',
        },
    },
)
@pytest.mark.translations(
    virtual_catalog={'selection-combo-sticker': {'ru': 'на выбор'}},
)
@pytest.mark.parametrize(
    'product_groups,has_sticker',
    [
        pytest.param(
            [
                mock_grocery_menu.ProductGroup(
                    True,
                    1,
                    ['product-1', 'product-2'],
                    'first-group-tanker-key',
                ),
                mock_grocery_menu.ProductGroup(
                    True,
                    1,
                    ['product-3', 'product-4'],
                    'second-group-tanker-key',
                ),
            ],
            True,
            id='single_selection_in_group_combo',
        ),
        pytest.param(
            [
                mock_grocery_menu.ProductGroup(
                    False,
                    2,
                    ['product-1', 'product-2', 'product-3'],
                    'first-group-tanker-key',
                ),
            ],
            True,
            id='non_unique_selection_combo',
        ),
        pytest.param(
            [
                mock_grocery_menu.ProductGroup(
                    True, 1, ['product-1'], 'first-group-tanker-key',
                ),
                mock_grocery_menu.ProductGroup(
                    True, 1, ['product-2'], 'second-group-tanker-key',
                ),
            ],
            False,
            id='single_selection_combo',
        ),
    ],
)
async def test_combo_sticker_on_meta_product(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        product_groups,
        has_sticker,
):

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo', [COMBO_ID], product_groups, 'combo_revision',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200

    combo_layout_item = _find_combo_layout_item(response)
    assert combo_layout_item['type'] == 'combo'

    combo_product = _find_combo_product(response)
    if has_sticker:
        assert combo_product['stickers'] == [
            {
                'sticker_color': 'yellow',
                'text': 'на выбор',
                'text_color': 'white',
            },
        ]
    else:
        assert 'stickers' not in combo_product


@ENABLE_COMBO_V2
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_combo_product_in_root_carousel(
        taxi_grocery_api, overlord_catalog, grocery_products, grocery_menu,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'combo_id',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2],
            'combo_revision',
        ),
    )

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {'id': 'category-1', 'products': [COMBO_ID]},
            {'id': 'category-2', 'products': ['product-1', 'product-2']},
        ],
    )
    overlord_catalog.add_products_stocks(
        depot_id=common.DEFAULT_DEPOT_ID,
        new_products_stocks=[
            {'in_stock': '0', 'product_id': COMBO_ID, 'quantity_limit': '0'},
        ],
    )

    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    group.layout_meta = (
        group.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={
            'modes': ['grocery'],
            'position': {'location': common.DEFAULT_LOCATION},
        },
    )
    assert response.status_code == 200
    assert _find_combo_layout_item(response) is not None
    assert _find_combo_product(response) is not None


# если тип комбо DISCOUNT и на него не заведена скидка, то такой
# комбо товар не попадает в ответ ручки
@ENABLE_COMBO_V2
@pytest.mark.parametrize(
    'combo_type,add_discount,presented_in_response',
    [
        pytest.param(mock_grocery_menu.ComboType.DISCOUNT, False, False),
        pytest.param(mock_grocery_menu.ComboType.DISCOUNT, True, True),
        pytest.param(mock_grocery_menu.ComboType.RECIPE, False, True),
        pytest.param(mock_grocery_menu.ComboType.RECIPE, True, True),
    ],
)
async def test_combo_type_and_discount(
        taxi_grocery_api,
        grocery_menu,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        combo_type,
        add_discount,
        presented_in_response,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision',
            combo_type,
        ),
    )
    if add_discount:
        grocery_p13n.add_bundle_v2_modifier(
            value=10, bundle_id='single_selection_combo',
        )
    common_combo.prepare_combo_test_context(
        overlord_catalog, grocery_products, product_prices=None, stocks=None,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200
    layout_item = _find_combo_layout_item(response)
    response_product = _find_combo_product(response)
    if presented_in_response:
        assert layout_item is not None
        assert response_product is not None
    else:
        assert layout_item is None
        assert response_product is None
