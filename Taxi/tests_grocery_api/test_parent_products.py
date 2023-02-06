# pylint: disable=too-many-lines

import copy

from grocery_mocks import grocery_p13n as p13n  # pylint: disable=E0401
import pytest

from . import common
from . import const
from . import experiments


def add_experiment_parent_products(experiments3):
    experiments3.add_experiment(
        name='grocery_api_parent_products',
        consumers=['grocery-api/modes'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


PRODUCTS_STOCKS = [
    {'in_stock': '10', 'product_id': 'product-1', 'quantity_limit': '5'},
    {'in_stock': '10', 'product_id': 'product-2', 'quantity_limit': '10'},
    {'in_stock': '10', 'product_id': 'product-3', 'quantity_limit': '5'},
    {'in_stock': '10', 'product_id': 'product-4', 'quantity_limit': '10'},
    {'in_stock': '5', 'product_id': 'product-5', 'quantity_limit': '0'},
    {'in_stock': '10', 'product_id': 'product-6', 'quantity_limit': '0'},
    {'in_stock': '5', 'product_id': 'product-7', 'quantity_limit': '123'},
    {'in_stock': '10', 'product_id': 'product-8', 'quantity_limit': '456'},
]

# POST /lavka/v1/api/v1/modes/category
# проверяем что при выключенном эксперименте
# ручка игнорирует родительские товары
# а при включенном схлопывает родителей и детей в один LayoutItem
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'experiment_parent_product, expected_layout_items, expected_products',
    [
        pytest.param(
            False,
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-1',
                'product-2',
            ],
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-1',
                'product-2',
            ],
            id='WITHOUT_EXP',
        ),
        pytest.param(
            True,
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-parent-1',
            ],
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-parent-1',
                'product-1',
                'product-2',
            ],
            id='WITH_EXP',
        ),
    ],
)
async def test_modes_category_experiment(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        experiments3,
        experiment_parent_product,
        expected_layout_items,
        expected_products,
):
    if experiment_parent_product:
        add_experiment_parent_products(experiments3)

    products_data = load_json(
        'overlord_catalog_products_data_with_parents.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'modes': ['grocery'],
        'position': {'location': const.LOCATION},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    # check layout
    response_layout_items = [
        layout_item_json['id']
        for layout_item_json in response.json()['modes'][0]['items']
    ]
    assert response_layout_items == expected_layout_items

    # check products
    response_products = [
        product_json['id'] for product_json in response.json()['products']
    ]
    assert response_products == expected_products


# POST /lavka/v1/api/v1/modes/category
# проверяем цену родительского товара
# в родительский товар записываем найменьшую цену из доступных чилдов
# если у чилда есть скидка, то берем цену со скидкой
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
async def test_modes_category_parent_price(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_parents_prices.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents_prices.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    # add discount
    grocery_p13n.add_modifier(product_id='product-4', value='4')

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'modes': ['grocery'],
        'position': {'location': const.LOCATION},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    # check parent's price
    parent_1_price = None
    parent_2_price = None
    for product_json in response.json()['products']:
        if product_json['id'] == 'product-parent-1':
            parent_1_price = product_json['pricing']['price']
        if product_json['id'] == 'product-parent-2':
            parent_2_price = product_json['pricing']['price']
    assert parent_1_price == '2'
    assert parent_2_price == '1'


# POST /lavka/v1/api/v1/modes/category
# проверяем сортировку пэрента и чилдов в моде
# чилды, пэренты и обычные продукты раскиданы,
# но rank проставлен и проставлен order чилдов
# пэрент и его чилды, должны быть на позиции пэрента
# чилды должны прийти в порядке ордера
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'experiment_parent_product, expected_layout_items, expected_products',
    [
        pytest.param(
            False,
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-1',
                'product-2',
                'product-3',
                'product-4',
            ],
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-1',
                'product-2',
                'product-3',
                'product-4',
            ],
            id='WITHOUT_EXP',
        ),
        pytest.param(
            True,
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-3',
                'product-parent-1',
                'product-4',
            ],
            [
                'virtual-category-1',
                'category-1-subcategory-1',
                'product-3',
                'product-parent-1',
                'product-2',
                'product-1',
                'product-4',
            ],
            id='WITH_EXP',
        ),
    ],
)
async def test_modes_category_order(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        experiments3,
        experiment_parent_product,
        expected_layout_items,
        expected_products,
):
    if experiment_parent_product:
        add_experiment_parent_products(experiments3)

    products_data = load_json(
        'overlord_catalog_products_data_with_parents_rnd_order.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents_rnd_order.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'modes': ['grocery'],
        'position': {'location': const.LOCATION},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    # check layout
    response_layout_items = [
        layout_item_json['id']
        for layout_item_json in response.json()['modes'][0]['items']
    ]
    assert response_layout_items == expected_layout_items

    # check products
    response_products = [
        product_json['id'] for product_json in response.json()['products']
    ]
    assert response_products == expected_products


# POST /lavka/v1/api/v1/modes/category
# проверяем выставление локализации в grades
# Для пэрента запрашиваем ключ 'product_grade_{grade_name}_title'.
# Для чилда ничего не делаем, фронт сам подклеит amount_units к первому грейду.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.parametrize(
    'locale, expected_grades_values, expected_grades_titles',
    [
        pytest.param(
            'ru',
            [
                [],
                [],
                ['weight', 'color'],
                ['800', '#FFAABB'],
                ['1600', '#ABCDEF'],
            ],
            [[], [], ['Вес', 'Цвет'], [], []],
            id='LOCALE_RU',
        ),
        pytest.param(
            'en',
            [
                [],
                [],
                ['weight', 'color'],
                ['800', '#FFAABB'],
                ['1600', '#ABCDEF'],
            ],
            [[], [], ['Weight', 'Color'], [], []],
            id='LOCALE_EN',
        ),
    ],
)
@pytest.mark.translations(
    wms_amount_units={
        'gram': {
            'ru': ['грамм', 'грамма', 'граммов'],
            'en': ['gram', 'grams'],
        },
    },
)
async def test_modes_category_localization(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        locale,
        expected_grades_values,
        expected_grades_titles,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_parents.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    headers = common.DEFAULT_HEADERS
    headers['Accept-Language'] = locale
    json = {
        'modes': ['grocery'],
        'position': {'location': const.LOCATION},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json, headers=headers,
    )

    assert response.status_code == 200

    # check grades values
    response_grades_values = [
        product_json['options']['grades']['values']
        if ('options' in product_json and 'grades' in product_json['options'])
        else []
        for product_json in response.json()['products']
    ]
    assert response_grades_values == expected_grades_values

    # check grades titles
    response_grades_titles = [
        product_json['options']['grades']['titles']
        if (
            'options' in product_json
            and 'grades' in product_json['options']
            and 'titles' in product_json['options']['grades']
        )
        else []
        for product_json in response.json()['products']
    ]
    assert response_grades_titles == expected_grades_titles


# POST /lavka/v1/api/v1/modes/category
# проверяем скрытие не нужных сущностей
# есть пэрент и есть чилды, но не все чилды доступные (нулевые стоки)
#     - отправляем всех чилдов
# есть пэрент и есть чилды, но нет доступных (нулевые стоки)
#     - не отправляем ни пэрента ни чилдов
# есть пэрент но нет чилдов
#     - скрываем пэрента
# есть чилды, но указанного пэрента нет
#     - отправляем доступных чилдов как обычные товары
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
async def test_modes_category_hiding(
        taxi_grocery_api, overlord_catalog, grocery_products, load_json,
):
    # preparing
    products_data = load_json(
        'overlord_catalog_products_data_with_parents_hiding.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents_hiding.json',
    )
    categories_data = load_json('overlord_catalog_categories_data_hiding.json')

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
        categories_data=categories_data,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_2 = category_group_1.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-2',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-3',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-4',
    )
    virtual_category_2.item_meta = '{"show_empty_subcategories": true}'

    await taxi_grocery_api.invalidate_caches()

    # action
    json = {
        'modes': ['grocery'],
        'position': {'location': const.LOCATION},
        'category_id': 'virtual-category-2',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    # check
    assert response.status_code == 200

    # check products
    expected_products = [
        'virtual-category-2',
        'category-2-subcategory-1',
        'product-parent-2',
        'product-1',
        'product-5',
        'category-2-subcategory-2',
        'category-2-subcategory-3',
        'category-2-subcategory-4',
        'product-1',
    ]
    response_products = [
        product_json['id'] for product_json in response.json()['products']
    ]
    assert response_products == expected_products


# POST /lavka/v1/api/v1/modes/product
# проверяем поведение ручки при включенном эксперименте
# если эксп не включен и запрашиваем чилда - присылаем чилда
# если эксп не включен и запрашиваем пэрента - ничего не отправляем, 404
# если эксп включен и запрашиваем чилда - присылаем чилда
# если эксп включен и запрашиваем пэрента - присылаем пэрента и чилдов
# ручка игнорирует родительский товар,
# а при включенном присылает чилдов в поле children
@pytest.mark.parametrize(
    'experiment_parent_product, product_id, expected_code, expected_children',
    [
        pytest.param(False, 'product-1', 200, [], id='WITHOUT_EXP_CHILD'),
        pytest.param(
            False, 'product-parent-1', 404, [], id='WITHOUT_EXP_PARENT',
        ),
        pytest.param(True, 'product-1', 200, [], id='WITH_EXP_CHILD'),
        pytest.param(
            True,
            'product-parent-1',
            200,
            ['product-1', 'product-2'],
            id='WITH_EXP_PARENT',
        ),
    ],
)
async def test_modes_product_experiment(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        experiments3,
        experiment_parent_product,
        product_id,
        expected_code,
        expected_children,
):
    if experiment_parent_product:
        add_experiment_parent_products(experiments3)

    products_data = load_json(
        'overlord_catalog_products_data_with_parents.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'position': {'location': const.LOCATION},
        'product_id': product_id,
        'subcategory_id': 'category-1-subcategory-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    assert response.status_code == expected_code

    # check children
    response_children = []
    if 'children' in response.json():
        response_children = [
            child_json['id'] for child_json in response.json()['children']
        ]
    assert response_children == expected_children


# POST /lavka/v1/api/v1/modes/product
# проверяем скрытие не нужных сущностей
# запрашиваем пэрента из определенной подкатегории
# есть пэрент и есть чилды, но не все чилды доступные (нулевые стоки)
#     - отправляем всех чилдов
# есть пэрент и есть чилды, но нет доступных (нулевые стоки)
#     - не отправляем ни пэрента ни чилдов, 404
# есть пэрент но нет чилдов
#     - не отправляем пэрента, 404
# есть чилды, но указанного пэрента нет
#     - отправить нечего, 404
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.parametrize(
    'subcategory_id, expected_code, expected_children',
    [
        pytest.param(
            'category-2-subcategory-1', 200, ['product-1', 'product-5'],
        ),
        pytest.param('category-2-subcategory-2', 404, []),
        pytest.param('category-2-subcategory-3', 404, []),
        pytest.param('category-2-subcategory-4', 404, []),
    ],
)
async def test_modes_product_hiding(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        subcategory_id,
        expected_code,
        expected_children,
):
    # preparing
    products_data = load_json(
        'overlord_catalog_products_data_with_parents_hiding.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents_hiding.json',
    )
    categories_data = load_json('overlord_catalog_categories_data_hiding.json')

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
        categories_data=categories_data,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_2 = category_group_1.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-2',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-3',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-4',
    )

    await taxi_grocery_api.invalidate_caches()

    # action
    json = {
        'position': {'location': const.LOCATION},
        'product_id': 'product-parent-2',
        'subcategory_id': subcategory_id,
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    # check
    assert response.status_code == expected_code

    response_children = []
    if 'children' in response.json():
        response_children = [
            child_json['id'] for child_json in response.json()['children']
        ]
    assert response_children == expected_children


# POST /lavka/v1/api/v1/modes/product
# проверяем цену родительского товара
# в родительский товар записываем найменьшую цену из доступных чилдов
# если у чилда есть скидка, то берем цену со скидкой
# если цены чилдов разные, в price_template пишем "от X р"
# если одинаковые, то "X р"
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.parametrize(
    'product_id, expected_price, expected_price_template',
    [
        pytest.param('product-parent-1', '2', 'от 2 $SIGN$$CURRENCY$'),
        pytest.param('product-parent-2', '1', 'от 1 $SIGN$$CURRENCY$'),
        pytest.param('product-parent-4', '3', '3 $SIGN$$CURRENCY$'),
    ],
)
@pytest.mark.translations(
    overlord_catalog={'grade_price': {'ru': 'от %(value)s'}},
)
async def test_modes_product_parent_price(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
        product_id,
        expected_price,
        expected_price_template,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_parents_prices.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents_prices.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    # add discount
    grocery_p13n.add_modifier(product_id='product-4', value='4.6')
    grocery_p13n.add_modifier(product_id='product-8', value='2.6')

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    # action
    json = {
        'position': {'location': const.LOCATION},
        'product_id': product_id,
        'subcategory_id': 'category-1-subcategory-1',
    }
    headers = common.DEFAULT_HEADERS
    headers['Accept-Language'] = 'ru'
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=json, headers=headers,
    )

    assert response.status_code == 200

    # check parent's price
    assert response.json()['product']['pricing']['price'] == expected_price
    assert (
        response.json()['product']['pricing']['price_template']
        == expected_price_template
    )


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.parametrize(
    'product_id, expected_cashback',
    [
        pytest.param('product-parent-2', '10'),
        pytest.param('product-parent-4', '20'),
    ],
)
@pytest.mark.translations(
    discount_descriptions={'parent_cashback': {'ru': 'от %(value)s'}},
)
async def test_modes_product_parent_cashback(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
        product_id,
        expected_cashback,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_parents_prices.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_parents_prices.json',
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=PRODUCTS_STOCKS,
        category_tree=category_tree,
    )

    # add cashback discount
    grocery_p13n.add_modifier(
        product_id='product-3',
        value='5',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )
    grocery_p13n.add_modifier(
        product_id='product-4',
        value='10',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )
    grocery_p13n.add_modifier(
        product_id='product-8',
        value='20',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    # action
    json = {
        'position': {'location': const.LOCATION},
        'product_id': product_id,
        'subcategory_id': 'category-1-subcategory-1',
    }
    headers = common.DEFAULT_HEADERS
    headers['Accept-Language'] = 'ru'
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=json, headers=headers,
    )

    assert response.status_code == 200

    # check parent's cashback
    assert (
        response.json()['product']['discount_pricing']['cashback']
        == expected_cashback
    )

    assert (
        response.json()['product']['discount_pricing']['cashback_template']
        == f'от {expected_cashback}'
    )


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.parametrize('product_id', ['product-parent-1'])
async def test_404_for_invalid_parent(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
        product_id,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_invalid_parents.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_invalid_parents.json',
    )

    stocks = copy.deepcopy(PRODUCTS_STOCKS)
    stocks.append(
        {
            'in_stock': '10',
            'product_id': 'product-parent-4',
            'quantity_limit': '5',
        },
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=stocks,
        category_tree=category_tree,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'position': {'location': const.LOCATION},
        'product_id': product_id,
        'subcategory_id': 'category-1-subcategory-1',
    }
    headers = common.DEFAULT_HEADERS
    headers['Accept-Language'] = 'ru'
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=json, headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'PRODUCT_NOT_FOUND',
        'message': 'Invalid parent product with id={}'.format(product_id),
    }


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
async def test_modes_category_no_invalid_parents(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_invalid_parents.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_invalid_parents.json',
    )

    stocks = copy.deepcopy(PRODUCTS_STOCKS)
    stocks.append(
        {
            'in_stock': '10',
            'product_id': 'product-parent-4',
            'quantity_limit': '5',
        },
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=stocks,
        category_tree=category_tree,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'modes': ['grocery'],
        'position': {'location': const.LOCATION},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    json = response.json()
    invalid_parents = [
        'product-parent-1',
        'product-parent-2',
        'product-parent-4',
    ]
    for mode in json['modes']:
        for item in mode['items']:
            assert item['id'] not in invalid_parents
    for product in json['products']:
        assert product['id'] not in invalid_parents
        if 'options' in product:
            assert 'parent_id' not in product['options']


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PARENT_PRODUCTS_ENABLED
@pytest.mark.parametrize('product_id', ['product-parent-1'])
async def test_modes_root_no_invalid_parents(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
        product_id,
):
    products_data = load_json(
        'overlord_catalog_products_data_with_invalid_parents.json',
    )
    category_tree = load_json(
        'overlord_catalog_category_tree_with_invalid_parents.json',
    )

    stocks = copy.deepcopy(PRODUCTS_STOCKS)
    stocks.append(
        {
            'in_stock': '10',
            'product_id': 'product-parent-4',
            'quantity_limit': '5',
        },
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=products_data,
        product_stocks=stocks,
        category_tree=category_tree,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    category_group_1.layout_meta = (
        category_group_1.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'position': {'location': const.LOCATION},
        'modes': ['grocery'],
        'product_id': product_id,
        'subcategory_id': 'category-1-subcategory-1',
    }
    headers = common.DEFAULT_HEADERS
    headers['Accept-Language'] = 'ru'
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )

    assert response.status_code == 200
    json = response.json()
    invalid_parents = [
        'product-parent-1',
        'product-parent-2',
        'product-parent-4',
    ]
    for mode in json['modes']:
        for item in mode['items']:
            assert item['id'] not in invalid_parents
    for product in json['products']:
        assert product['id'] not in invalid_parents
        if 'options' in product:
            assert 'parent_id' not in product['options']
