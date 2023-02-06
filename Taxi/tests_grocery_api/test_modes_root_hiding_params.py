import pytest

from . import common
from . import const
from . import experiments


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('in_stock', ['5', '0', None])
@pytest.mark.parametrize('hide_if_empty_value', [True, False, None])
async def test_modes_root_hide_if_empty(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        in_stock,
        hide_if_empty_value,
        taxi_config,
):
    """ test POST /lavka/v1/api/v1/modes/root hide virtual category
    based on hide_if_empty param in its meta """

    item_meta = (
        '{"hide_if_empty":'
        + (
            str(hide_if_empty_value).lower()
            if hide_if_empty_value is not None
            else 'null'
        )
        + '}'
    )
    category_tree = [{'id': 'category-1', 'products': ['product-1']}]
    stocks = {}
    if in_stock is not None:
        stocks['product-1'] = in_stock
    location = const.LOCATION
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    virtual_category_in_response = False
    available = None
    for item in response.json()['products']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
            available = item['available']

    if hide_if_empty_value is None:
        assert available is True
        assert virtual_category_in_response is True
        assert overlord_catalog.internal_stocks_times_called == 0
    else:
        if hide_if_empty_value is False:
            assert virtual_category_in_response is True
        else:
            assert virtual_category_in_response == (in_stock == '5')

        if virtual_category_in_response:
            assert available is (in_stock is not None and int(in_stock) > 0)


EXPECTED_PRODUCTS = [
    'category-group-1',
    'virtual-category-1',
    'product-1',
    'product-2',
    'product-3',
    'category-group-2',
    'virtual-category-2',
    'category-group-3',
    'virtual-category-3',
    'virtual-category-4',
]
EXPECTED_NON_HIDDEN_PRODUCTS = [
    'category-group-1',
    'virtual-category-1',
    'category-group-2',
    'virtual-category-2',
    'category-group-3',
    'virtual-category-3',
    'virtual-category-4',
]
EXPECTED_HIDDEN_PRODUCTS = [
    'category-group-2',
    'virtual-category-2',
    'category-group-3',
    'virtual-category-3',
    'virtual-category-4',
]


def build_grocery_products_data(grocery_products, add_products_to_category):
    layout = grocery_products.add_layout(test_id='1')

    group_1 = layout.add_category_group(test_id='1')

    category_1 = group_1.add_virtual_category(test_id='1')
    if add_products_to_category:
        category_1.add_subcategory(subcategory_id='category-1')

    group_2 = layout.add_category_group(test_id='2')

    group_2.add_virtual_category(test_id='2')

    group_3 = layout.add_category_group(test_id='3')

    group_3.add_virtual_category(test_id='3')
    group_3.add_virtual_category(test_id='4')


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('add_products_to_category', [True, False])
@pytest.mark.parametrize('hide_if_empty_value', [True, False, None])
async def test_modes_root_hide_carousels_if_empty(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        add_products_to_category,
        hide_if_empty_value,
        taxi_config,
):
    """
    test POST /lavka/v1/api/v1/modes/root hide carousel
    based on hide_if_empty param in category_meta

    There is categoury_group which is shown as carousel
    and it has its nested virtual_categories

    Carousel must be hidden if there is no
    products in nested virtual_categories
    """

    location = const.LOCATION

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': ['product-1', 'product-2', 'product-3'],
            },
        ],
    )

    build_grocery_products_data(grocery_products, add_products_to_category)
    layout_1 = grocery_products.get_layout('layout-1')
    group_1 = layout_1.groups['category-group-1']
    virtual_category = group_1.categories['virtual-category-1']
    group_1.layout_meta = '{"show_as_carousels": true}'
    virtual_category.item_meta = (
        '{'
        + '"hide_if_empty": '
        + (
            str(hide_if_empty_value).lower()
            if hide_if_empty_value is not None
            else 'null'
        )
        + '}'
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    headers = {'Accept-Language': 'ru'}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )
    assert response.status_code == 200

    products = [product['id'] for product in response.json()['products']]
    if add_products_to_category:
        assert products == EXPECTED_PRODUCTS
    else:
        assert products == EXPECTED_HIDDEN_PRODUCTS


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('in_stock', ['5', '0', None])
@pytest.mark.parametrize(
    'hide_if_product_is_missing_value',
    ['null', '"product-1"', '"product-not-in-category-tree"'],
)
async def test_modes_root_hide_if_product_is_missing(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        in_stock,
        hide_if_product_is_missing_value,
        taxi_config,
):
    """ test POST /lavka/v1/api/v1/modes/root hide virtual category
    based on hide_if_product_is_missing param in its meta """

    item_meta = (
        '{"hide_if_product_is_missing":'
        + hide_if_product_is_missing_value
        + '}'
    )
    category_tree = [
        {'id': 'category-1', 'products': ['product-1', 'product-2']},
    ]
    stocks = {}
    if in_stock is not None:
        stocks['product-1'] = in_stock
    stocks['product-2'] = '10'
    location = const.LOCATION
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
    if hide_if_product_is_missing_value == 'null':
        # product_id not set
        assert virtual_category_in_response is True
    elif hide_if_product_is_missing_value == '"product-1"':
        # product_id in category-tree
        assert virtual_category_in_response == (in_stock == '5')
    elif hide_if_product_is_missing_value == '"product-not-in-category-tree"':
        # product_id not found in category-tree
        assert virtual_category_in_response is False
    else:
        assert False


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('in_stock', ['5', '0', None])
@pytest.mark.parametrize(
    'hide_if_products_are_missing_value',
    [
        'null',
        '["product-1", "product-2"]',
        '["product-1", "product-3"]',
        '["product-not-in-category-tree"]',
    ],
)
async def test_modes_root_hide_if_all_products_are_missing(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        in_stock,
        hide_if_products_are_missing_value,
        taxi_config,
):
    """ test POST /lavka/v1/api/v1/modes/root hide virtual category
    based on hide_if_products_are_missing param in its meta """
    item_meta = (
        '{"hide_if_all_products_are_missing":'
        + hide_if_products_are_missing_value
        + '}'
    )
    category_tree = [
        {
            'id': 'category-1',
            'products': ['product-1', 'product-2', 'product-3'],
        },
    ]
    stocks = {}
    if in_stock is not None:
        stocks['product-1'] = in_stock
        stocks['product-2'] = in_stock
    stocks['product-3'] = '10'
    location = const.LOCATION
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
    if hide_if_products_are_missing_value == 'null':
        # product_ids not set
        assert virtual_category_in_response is True
    elif hide_if_products_are_missing_value == '["product-1", "product-2"]':
        # product_ids in category-tree
        assert virtual_category_in_response == (in_stock == '5')
    elif hide_if_products_are_missing_value == '["product-1", "product-3"]':
        # on of products is always present
        assert virtual_category_in_response is True
    elif (
        hide_if_products_are_missing_value
        == '["product-not-in-category-tree"]'
    ):
        # product_id not found in category-tree
        assert virtual_category_in_response is False
    else:
        assert False


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('in_stock', [None, '5', '0'])
@pytest.mark.parametrize(
    'if_subcategory_is_empty_value',
    ['null', '"category-1"', '"category-not-in-category-tree"'],
)
async def test_modes_root_hide_if_subcategory_is_empty(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        in_stock,
        if_subcategory_is_empty_value,
        taxi_config,
):
    """ test POST /lavka/v1/api/v1/modes/root hide virtual category
    based on hide_if_subcategory_is_empty param in its meta """

    item_meta = (
        '{"hide_if_subcategory_is_empty":'
        + if_subcategory_is_empty_value
        + '}'
    )
    category_tree = [
        {'id': 'category-1', 'products': ['product-1']},
        {'id': 'category-2', 'products': ['product-2']},
    ]
    stocks = {}
    if in_stock is not None:
        stocks['product-1'] = in_stock
    stocks['product-2'] = '10'
    location = const.LOCATION
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
    if if_subcategory_is_empty_value == 'null':
        # subcategory_id not set
        assert virtual_category_in_response is True
    elif if_subcategory_is_empty_value == '"category-1"':
        # subcategory_id in category-tree
        assert virtual_category_in_response == (in_stock == '5')
    elif if_subcategory_is_empty_value == '"category-not-in-category-tree"':
        # subcategory_id not found in category-tree
        assert virtual_category_in_response is False
    else:
        assert False


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('in_stock', [None, '5', '0'])
@pytest.mark.parametrize(
    'if_subcategories_are_empty_value,',
    [
        'null',
        '["category-1", "category-2"]',
        '["category-1", "category-3"]',
        '["category-not-in-category-tree"]',
    ],
)
async def test_modes_root_hide_if_all_subcategories_are_empty(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        in_stock,
        if_subcategories_are_empty_value,
        taxi_config,
):
    """ test POST /lavka/v1/api/v1/modes/root hide virtual category
    based on hide_if_subcategories_are_empty param in its meta """

    item_meta = (
        '{"hide_if_all_subcategories_are_empty":'
        + if_subcategories_are_empty_value
        + '}'
    )
    category_tree = [
        {'id': 'category-1', 'products': ['product-1']},
        {'id': 'category-2', 'products': ['product-1']},
        {'id': 'category-3', 'products': ['product-2']},
    ]
    stocks = {}
    if in_stock is not None:
        stocks['product-1'] = in_stock
    stocks['product-2'] = '10'
    location = const.LOCATION
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
    if if_subcategories_are_empty_value == 'null':
        # subcategory_ids are not set
        assert virtual_category_in_response is True
    elif if_subcategories_are_empty_value == '["category-1", "category-2"]':
        # subcategory_ids in category-tree
        assert virtual_category_in_response == (in_stock == '5')
    elif if_subcategories_are_empty_value == '["category-1", "category-3"]':
        # one of subcategories is always present
        assert virtual_category_in_response is True
    elif (
        if_subcategories_are_empty_value == '["category-not-in-category-tree"]'
    ):
        # subcategory_id not found in category-tree
        assert virtual_category_in_response is False
    else:
        assert False


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('subcategory_available', [True, False])
@pytest.mark.parametrize(
    'if_subcategory_is_empty_value',
    ['null', '"category-1"', '"category-not-in-category-tree"'],
)
async def test_hide_if_subcategory_is_empty_new_availability(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        if_subcategory_is_empty_value,
        taxi_config,
        subcategory_available,
):
    """ test POST /lavka/v1/api/v1/modes/root hide virtual category
    based on hide_if_subcategory_is_empty param in its meta
    using new subcategories availability check"""

    item_meta = (
        '{"hide_if_subcategory_is_empty":'
        + if_subcategory_is_empty_value
        + '}'
    )
    category_tree = [
        {'id': 'category-1', 'products': ['product-1']},
        {'id': 'category-2', 'products': ['product-2']},
    ]
    stocks = {'product-1': '10', 'product-2': '10'}
    location = const.LOCATION
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )
    overlord_catalog.set_category_availability(
        category_id='category-1', available=subcategory_available,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True

    if if_subcategory_is_empty_value == 'null':
        # subcategory_id not set
        assert virtual_category_in_response is True
        assert (
            overlord_catalog.internal_categories_availability_times_called == 0
        )
    elif if_subcategory_is_empty_value == '"category-not-in-category-tree"':
        # subcategory_id not found in category-tree
        assert (
            overlord_catalog.internal_categories_availability_times_called == 1
        )
        assert virtual_category_in_response is False
    elif if_subcategory_is_empty_value == '"category-1"':
        # subcategory_id in category-tree and available
        assert (
            overlord_catalog.internal_categories_availability_times_called == 1
        )
        assert virtual_category_in_response == subcategory_available
    else:
        assert False


@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_hide_if_empty_two_categories(
        taxi_grocery_api,
        overlord_catalog,
        taxi_config,
        grocery_products,
        grocery_depots,
):
    category_tree = [
        {'id': 'category-1', 'products': ['product-1']},
        {'id': 'category-2', 'products': ['product-2']},
    ]
    stocks = [
        {'in_stock': '0', 'product_id': 'product-1', 'quantity_limit': '0'},
        {'in_stock': '10', 'product_id': 'product-2', 'quantity_limit': '10'},
    ]
    location = const.LOCATION
    overlord_category_tree = common.build_tree(category_tree)
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        location=location,
        depot_id=const.DEPOT_ID,
        depot_test_id=int(const.LEGACY_DEPOT_ID),
    )
    common.prepare_overlord_catalog(
        overlord_catalog,
        location,
        category_tree=overlord_category_tree,
        product_stocks=stocks,
    )
    overlord_catalog.set_category_availability(
        category_id='category-2', available=True,
    )

    item_meta = '{"hide_if_empty":' + 'true' + '}'
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(
        test_id='1', add_short_title=True, item_meta=item_meta,
    )
    virtual_category_2 = category_group.add_virtual_category(
        test_id='2', add_short_title=True, item_meta=item_meta,
    )
    virtual_category_1.add_subcategory(subcategory_id='category-1')
    virtual_category_2.add_subcategory(subcategory_id='category-2')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status == 200
    virtual_category_1_in_response = False
    virtual_category_2_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category_1.virtual_category_id:
            virtual_category_1_in_response = True
        if item['id'] == virtual_category_2.virtual_category_id:
            virtual_category_2_in_response = True
    assert not virtual_category_1_in_response
    assert virtual_category_2_in_response


COMMON_CATEGORY_META = (
    """{
    "hide_if_empty": true
}""".replace(
        '\n', '',
    )
)

SPECIAL_CATEGORY_META = (
    """{
    "hide_if_empty": true
}""".replace(
        '\n', '',
    )
)


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.UPSALE_EXPERIMENT
@pytest.mark.parametrize(
    'upsale_products',
    [
        # у обычной и спец. категорий НЕТ общих продуктов
        pytest.param(['product-6', 'product-9'], id='without intersection'),
        # у обычной и спец. категорий ЕСТЬ общий продукт
        pytest.param(
            ['product-3', 'product-6', 'product-9'], id='with intersection',
        ),
    ],
)
async def test_hide_even_if_special_category_is_hiding(
        taxi_grocery_api,
        grocery_products,
        overlord_catalog,
        grocery_upsale,
        upsale_products,
        taxi_config,
):

    # prepare overlord_catalog and grocery_products
    category_tree = [
        {
            'id': 'category-common-subcategory-1',
            'products': ['product-1', 'product-2', 'product-3'],
        },
        {
            'id': 'category-special-subcategory-1',
            'products': ['product-6', 'product-9'],
        },
    ]
    common.build_overlord_catalog_products(overlord_catalog, category_tree)

    # setup availability
    for category_data in category_tree:
        overlord_catalog.set_category_availability(
            category_id=category_data['id'], available=True,
        )
    # common category is disable
    overlord_catalog.set_category_availability(
        category_id='category-common-subcategory-1', available=False,
    )

    # add layout
    layout = grocery_products.add_layout(test_id='1')

    # add group Group1
    category_group_1 = layout.add_category_group(test_id='1')
    # add common category
    common_category = category_group_1.add_virtual_category(
        test_id='1', item_meta=COMMON_CATEGORY_META,
    )
    # add subcategory
    common_category.add_subcategory(
        subcategory_id='category-common-subcategory-1',
    )

    # add group Group2
    category_group_2 = layout.add_category_group(test_id='2')
    # add special category "Upsale"
    category_group_2.add_virtual_category(
        test_id='special',
        special_category='upsale',
        item_meta=SPECIAL_CATEGORY_META,
    )
    # set special products
    grocery_upsale.add_products(upsale_products)

    # run /modes/root grocery
    json = {
        'modes': ['grocery'],
        'position': {'location': common.DEFAULT_LOCATION},
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers=common.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert overlord_catalog.internal_categories_availability_times_called == 1
    assert grocery_upsale.times_called == 1

    # category `virtual-category-1` should not be in response
    response_products = set(
        product['id'] for product in response.json()['products']
    )
    assert 'virtual-category-1' not in response_products
