# pylint: disable=too-many-lines

# Общие сценарии для ручек modes/category-group и modes/category
import pytest

from . import common
from . import conftest
from . import const
from . import experiments


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'he'])
@pytest.mark.config(
    GROCERY_LOCALIZATION_CATEGORIES_KEYSET='wms_items',
    GROCERY_LOCALIZATION_PRODUCT_DESCRIPTION_SUFFIX='_description',
    GROCERY_LOCALIZATION_CATEGORY_TITLE_SUFFIX='_title',
    GROCERY_LOCALIZATION_CATEGORY_DESCRIPTION_SUFFIX='_description',
)
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize('locale', ['ru', 'en', 'he'])
async def test_modes_category_groups_translations(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        locale,
        test_handler,
        now,
):
    """ Если присутствует перевод, то он берётся из Танкера """
    overlord_catalog.add_category_tree(
        depot_id=const.DEPOT_ID,
        category_tree={
            'categories': [{'id': 'localized-product-category'}],
            'depot_ids': ['test-depot-id'],
            'products': [
                {
                    'full_price': '1.2',
                    'id': 'localized-product',
                    'category_ids': ['localized-product-category'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )
    overlord_catalog.add_categories_data(
        new_categories_data=[
            {
                'category_id': 'localized-product-category',
                'description': 'localized-product-category-description',
                'image_url_template': (
                    'localized-product-category-image-url-template'
                ),
                'title': 'localized-product-category-title',
            },
        ],
    )
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'localized-product-description',
                'image_url_template': 'localized-product-image-url-template',
                'long_title': 'localized-product-long-title',
                'product_id': 'localized-product',
                'title': 'localized-product-title',
            },
        ],
    )
    overlord_catalog.add_products_stocks(
        depot_id=const.DEPOT_ID,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': 'localized-product',
                'quantity_limit': '5',
            },
        ],
    )
    layout = grocery_products.add_layout(test_id='1')

    category_group_1 = layout.add_category_group(test_id='localized')

    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='localized', add_short_title=True,
    )
    virtual_category_1.add_subcategory(
        subcategory_id='localized-product-category',
    )

    headers = {}
    if locale:
        headers['Accept-Language'] = locale

    json = common.build_grocery_mode_request(
        test_handler,
        layout.layout_id,
        layout.group_ids_ordered[0],
        virtual_category_1.virtual_category_id,
    )

    offers.add_offer_elementwise(
        json['offer_id'], now, const.DEPOT_ID, const.LOCATION,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=json, headers=headers,
    )
    assert response.status_code == 200

    if not locale:
        locale = 'en'
    expected_response = load_json(
        'localized_modes_category_group_expected_response.json',
    )[locale]
    assert response.json() == expected_response


# локализация единиц измерения
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'he'])
@pytest.mark.config(
    GROCERY_LOCALIZATION_CATEGORIES_KEYSET='wms_items',
    GROCERY_LOCALIZATION_AMOUNT_UNITS_KEYSET='wms_amount_units',
    GROCERY_LOCALIZATION_PRODUCT_DESCRIPTION_SUFFIX='_description',
    GROCERY_LOCALIZATION_CATEGORY_TITLE_SUFFIX='_title',
    GROCERY_LOCALIZATION_CATEGORY_DESCRIPTION_SUFFIX='_description',
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_WMS_AMOUNT_UNITS_TABLE={
        'amount_units': [
            {'alias': 'gram', 'values': ['г']},
            {'alias': 'kilogram', 'values': ['КГ.']},
        ],
    },
)
@pytest.mark.translations(
    wms_amount_units={
        'gram': {
            'ru': ['грамм', 'грамма', 'граммов'],
            'en': ['gram', 'grams'],
            'he': 'ג',
        },
    },
)
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize(
    'amount,amount_units,amount_units_alias,locale,expected_amount_units',
    [
        pytest.param(
            '1', 'л', None, 'en', 'л', id='alias not found in fallback table',
        ),
        pytest.param('1', 'г', None, 'ru', 'грамм', id='plural form 1'),
        pytest.param('2', 'г', None, 'ru', 'грамма', id='plural form 2'),
        pytest.param('6', 'г', None, 'ru', 'граммов', id='plural form 3'),
        pytest.param(
            '1',
            'г',
            None,
            'he',
            'ג',
            id='translation is not set for plural form',
        ),
        pytest.param(
            '8.7', 'г', None, 'ru', 'грамм', id='amount with fractional part',
        ),
        pytest.param(
            '2', 'г', 'gram', 'ru', 'грамма', id='alias from db field',
        ),
        pytest.param('1', 'г', 'gram', 'en', 'gram', id='en - plural form 1'),
        pytest.param('2', 'г', 'gram', 'en', 'grams', id='en - plural form 2'),
        pytest.param(
            '1',
            'г',
            'gram',
            'he',
            'ג',
            id='he - plural form 1 (no translation)',
        ),
        pytest.param(
            '2',
            'г',
            'gram',
            'he',
            'ג',
            id='he - plural form 2 (no translation)',
        ),
    ],
)
async def test_modes_category_groups_translations_amount_units(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        locale,
        test_handler,
        amount,
        amount_units,
        amount_units_alias,
        expected_amount_units,
):
    depot_id = const.DEPOT_ID
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree={
            'categories': [{'id': 'test-product-category'}],
            'products': [
                {
                    'full_price': '1.2',
                    'id': 'test-product',
                    'category_ids': ['test-product-category'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )
    overlord_catalog.add_categories_data(
        new_categories_data=[
            {
                'category_id': 'test-product-category',
                'description': 'test-product-category-description',
                'image_url_template': (
                    'test-product-category-image-url-template'
                ),
                'title': 'test-product-category-title',
            },
        ],
    )
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'test-product-description',
                'image_url_template': 'test-product-image-url-template',
                'long_title': 'test-product-long-title',
                'product_id': 'test-product',
                'title': 'test-product-title',
                'options': {
                    'shelf_life_measure_unit': '',
                    'amount': amount,
                    'amount_units': amount_units,
                    'amount_units_alias': amount_units_alias,
                    'pfc': [],
                    'storage': [],
                    'ingredients': [],
                    'country_codes': [],
                },
            },
        ],
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': 'test-product',
                'quantity_limit': '5',
            },
        ],
    )
    layout = grocery_products.add_layout(test_id='1')

    test_category_group = layout.add_category_group(
        test_id='test-virtual-category',
    )

    test_virtual_category = test_category_group.add_virtual_category(
        test_id='test-virtual-category', add_short_title=True,
    )
    test_virtual_category.add_subcategory(
        subcategory_id='test-product-category',
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            test_virtual_category.virtual_category_id,
        ),
        headers={'Accept-Language': locale},
    )
    assert response.status_code == 200

    products = response.json()['products']
    good = next((p for p in products if p['type'] == 'good'), 'good_is_absent')
    assert good != 'good_is_absent'
    assert 'options' in good
    assert good['options']['amount_units'] == expected_amount_units


# тест GROCERY_LOCALIZATION_WHICH_AMOUNT_FORMS_VALUE_USED
@pytest.mark.config(LOCALES_SUPPORTED=['ru'])
@pytest.mark.translations(
    wms_amount_units={'gram': {'ru': ['грамм', 'грамма', 'граммов']}},
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_WMS_AMOUNT_UNITS_TABLE={
        'amount_units': [{'alias': 'gram', 'values': ['г']}],
    },
)
@common.HANDLERS
@pytest.mark.parametrize(
    'amount,amount_units,amount_units_alias,locale,'
    'is_config_on,expected_amount_units',
    [
        pytest.param(
            '1', 'г', None, 'ru', True, 'грамм', id='use plural form 1',
        ),
        pytest.param(
            '2', 'г', None, 'ru', True, 'грамма', id='use plural form 2',
        ),
        pytest.param(
            '1', 'г', None, 'ru', False, 'грамм', id='use default plural 1',
        ),
        pytest.param(
            '2', 'г', None, 'ru', False, 'грамм', id='use default plural 2',
        ),
    ],
)
async def test_amount_units_translation_use_usual_plural_config(
        taxi_grocery_api,
        overlord_catalog,
        taxi_config,
        grocery_products,
        load_json,
        locale,
        test_handler,
        amount,
        amount_units,
        amount_units_alias,
        is_config_on,
        expected_amount_units,
):
    taxi_config.set_values(
        {
            'GROCERY_LOCALIZATION_WHICH_AMOUNT_UNITS_COUNT_USED': {
                'is_actual_value_used': is_config_on,
                'fallback_count': 1,
            },
        },
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        products_data=[
            {
                'description': 'product-1-description',
                'image_url_template': 'product-1-image-url-template',
                'long_title': 'product-1-long-title',
                'product_id': 'product-1',
                'title': 'product-1-title',
                'options': {
                    'shelf_life_measure_unit': '',
                    'amount': amount,
                    'amount_units': amount_units,
                    'amount_units_alias': amount_units_alias,
                    'pfc': [],
                    'storage': [],
                    'ingredients': [],
                    'country_codes': [],
                },
            },
        ],
    )
    layout = common.build_basic_layout(grocery_products)

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            'virtual-category-1',
        ),
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200

    products = response.json()['products']
    good = next((p for p in products if p['type'] == 'good'), 'good_is_absent')
    assert good != 'good_is_absent'
    assert 'options' in good
    assert good['options']['amount_units'] == expected_amount_units


@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize('empty', [True, False])
@pytest.mark.parametrize('hide_if_empty_value', [True, False, None])
async def test_modes_category_groups_hide_if_empty(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        empty,
        hide_if_empty_value,
        taxi_config,
        test_handler,
):
    """ test POST /lavka/v1/api/v1/modes/category-group hide virtual category
    based on hide_if_empty param in its meta """

    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    item_meta = (
        '{"hide_if_empty":'
        + (
            str(hide_if_empty_value).lower()
            if hide_if_empty_value is not None
            else 'null'
        )
        + '}'
    )
    virtual_category = category_group.add_virtual_category(
        test_id='1', add_short_title=True, item_meta=item_meta,
    )
    if not empty:
        virtual_category.add_subcategory(
            subcategory_id='category-1-subcategory-1',
        )

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
    virtual_category_in_response = False
    available = None
    for item in response.json()['products']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
            available = item['available']

    assert (
        virtual_category_in_response == (not empty)
        or (hide_if_empty_value is False)
        or (hide_if_empty_value is None)
    )
    if virtual_category_in_response:
        assert available == (not empty) or (hide_if_empty_value is None)


@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize('stocks', [None, '5', '0'])
@pytest.mark.parametrize(
    'hide_if_product_is_missing_value',
    ['null', '"product-1"', '"product-not-in-category-tree"'],
)
async def test_modes_category_groups_hide_if_product_is_missing(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        stocks,
        hide_if_product_is_missing_value,
        taxi_config,
        test_handler,
):
    """ test POST /lavka/v1/api/v1/modes/category-group hide virtual category
    based on hide_if_product_is_missing param in its meta """

    location = const.LOCATION
    product_stocks = []
    if stocks is not None:
        product_stocks = [
            {
                'in_stock': stocks,
                'product_id': 'product-1',
                'quantity_limit': stocks,
            },
            {
                'in_stock': '10',
                'product_id': 'product-2',
                'quantity_limit': '10',
            },
        ]
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=product_stocks,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    item_meta = (
        '{"hide_if_product_is_missing":'
        + hide_if_product_is_missing_value
        + '}'
    )
    virtual_category = category_group.add_virtual_category(
        test_id='1', add_short_title=True, item_meta=item_meta,
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
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
    if hide_if_product_is_missing_value == 'null':
        # product_id not set
        assert virtual_category_in_response is True
    elif hide_if_product_is_missing_value == '"product-1"':
        # product_id in category-tree
        assert virtual_category_in_response == (stocks == '5')
    elif hide_if_product_is_missing_value == '"product-not-in-category-tree"':
        # product_id not found in category-tree
        assert virtual_category_in_response is False
    else:
        assert False


@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize('stocks', [None, '5', '0'])
@pytest.mark.parametrize(
    'if_subcategory_is_empty_value',
    ['null', '"category-1-subcategory-1"', '"category-not-in-category-tree"'],
)
async def test_modes_category_groups_hide_if_subcategory_is_empty(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        stocks,
        if_subcategory_is_empty_value,
        taxi_config,
        test_handler,
):
    """ test POST /lavka/v1/api/v1/modes/category-group hide virtual category
    based on hide_if_subcategory_is_empty param in its meta """

    location = const.LOCATION
    product_stocks = []
    if stocks is not None:
        product_stocks = [
            {
                'in_stock': stocks,
                'product_id': 'product-1',
                'quantity_limit': stocks,
            },
        ]
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=product_stocks,
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1',
        available=(stocks is not None and int(stocks) > 0),
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    item_meta = (
        '{"hide_if_subcategory_is_empty":'
        + if_subcategory_is_empty_value
        + '}'
    )
    virtual_category = category_group.add_virtual_category(
        test_id='1', add_short_title=True, item_meta=item_meta,
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
    virtual_category_in_response = False
    for item in response.json()['modes'][0]['items']:
        if item['id'] == virtual_category.virtual_category_id:
            virtual_category_in_response = True
    if if_subcategory_is_empty_value == 'null':
        # subcategory_id not set
        assert virtual_category_in_response is True
    elif if_subcategory_is_empty_value == '"category-1-subcategory-1"':
        # subcategory_id in category-tree
        assert virtual_category_in_response == (stocks == '5')
    elif if_subcategory_is_empty_value == '"category-not-in-category-tree"':
        # subcategory_id not found in category-tree
        assert virtual_category_in_response is False
    else:
        assert False


@experiments.GROCERY_PRODUCTS_BIG_CARDS
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize(
    'category_id,width,height,index_in_subcategory',
    [('1', 6, 3, 1), ('2', 2, 4, 2)],
)
async def test_modes_products_big_cards(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        category_id,
        width,
        height,
        test_handler,
        index_in_subcategory,
):
    """ Test that product tile width and height taken from big cards config
    when product id and virtual category id matched, also checks that
    product with big card is moved on first position in subcategory """

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
    subcategory_index = 0
    for i, item in enumerate(response.json()['modes'][0]['items']):
        if item['type'] == 'subcategory':
            subcategory_index = i
        if item['type'] == 'good':
            if item['id'] == 'product-2':
                assert item['width'] == width
                assert item['height'] == height
                assert index_in_subcategory == i - subcategory_index
            else:
                assert item['width'] == 2
                assert item['height'] == 4


# когда товар разобран, карточка заменяется на обычную, и товар перемещается
# вниз
@experiments.GROCERY_PRODUCTS_BIG_CARDS
@experiments.GROCERY_PRODUCTS_SMALL_CARDS
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize(
    'category_id,in_stock,width,height,index_in_subcategory',
    [
        pytest.param(
            '1', '0', 3, 4, 3, marks=[experiments.SHOW_SOLD_OUT_ENABLED],
        ),
        pytest.param('1', '1', 6, 3, 1),
    ],
)
async def test_modes_products_big_cards_sold_out(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        category_id,
        width,
        height,
        test_handler,
        index_in_subcategory,
        in_stock,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
            {
                'in_stock': in_stock,
                'product_id': 'product-2',
                'quantity_limit': in_stock,
            },
            {
                'in_stock': '1',
                'product_id': 'product-3',
                'quantity_limit': '1',
            },
        ],
    )

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
    subcategory_index = 0
    actual_index = None
    actual_width = None
    actual_height = None
    for i, item in enumerate(response.json()['modes'][0]['items']):
        if item['type'] == 'subcategory':
            subcategory_index = i
        if item['type'] == 'good':
            if item['id'] == 'product-2':
                actual_width = item['width']
                actual_height = item['height']
                actual_index = i - subcategory_index
            else:
                assert item['width'] == 3
                assert item['height'] == 4
    assert actual_index == index_in_subcategory
    assert actual_width == width
    assert actual_height == height


# При ответе 500 от ручки остатков, ручки каталога отвечают 500
# При ответе 404 от ручки остатков, ручки каталога отвечают 404
@pytest.mark.parametrize(
    'error_code,error_response',
    [(500, None), (404, {'code': 'Error', 'message': 'Error'})],
)
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_grocery_with_stocks_error(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
        test_handler,
        error_code,
        error_response,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    @mockserver.json_handler('overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return mockserver.make_response(status=error_code, json=error_response)

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
    )
    assert response.status_code == error_code
    if response.status_code == 404:
        assert response.json()['code'] == 'DEPOT_NOT_FOUND'


@pytest.mark.translations(
    wms_attributes={
        'sticker_id_1': {'en': 'some text'},
        'sticker_id_2': {'en': 'another text'},
    },
)
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.config(GROCERY_LOCALIZATION_ATTRIBUTES_KEYSET='wms_attributes')
@common.STICKERS_INFO_CONFIG
async def test_modes_category_groups_stickers(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
):
    depot_id = const.DEPOT_ID
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree={
            'categories': [{'id': 'test-product-category'}],
            'products': [
                {
                    'full_price': '1.2',
                    'id': 'test-product',
                    'category_ids': ['test-product-category'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )
    overlord_catalog.add_categories_data(
        new_categories_data=[
            {
                'category_id': 'test-product-category',
                'description': 'test-product-category-description',
                'image_url_template': (
                    'test-product-category-image-url-template'
                ),
                'title': 'test-product-category-title',
            },
        ],
    )
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'test-product-description',
                'image_url_template': 'test-product-image-url-template',
                'long_title': 'test-product-long-title',
                'product_id': 'test-product',
                'title': 'test-product-title',
                'options': {
                    'shelf_life_measure_unit': '',
                    'amount': '',
                    'amount_units': '',
                    'pfc': [],
                    'storage': [],
                    'ingredients': [],
                    'country_codes': [],
                    'photo_stickers': ['sticker_id_1', 'sticker_id_2'],
                },
            },
        ],
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': 'test-product',
                'quantity_limit': '5',
            },
        ],
    )

    layout = grocery_products.add_layout(test_id='1')
    test_category_group = layout.add_category_group(
        test_id='test-virtual-category',
    )
    test_virtual_category = test_category_group.add_virtual_category(
        test_id='test-virtual-category', add_short_title=True,
    )
    test_virtual_category.add_subcategory(
        subcategory_id='test-product-category',
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            test_virtual_category.virtual_category_id,
        ),
        headers={},
    )
    assert response.status_code == 200

    products = response.json()['products']
    good = next((p for p in products if p['type'] == 'good'), 'good_is_absent')
    assert good != 'good_is_absent'
    assert 'options' in good
    expected_stickers = [
        {
            'sticker_color': 'yellow',
            'text': 'some text',
            'text_color': 'white',
        },
        {
            'sticker_color': 'black',
            'text': 'another text',
            'text_color': 'white',
        },
    ]
    assert good['stickers'] == expected_stickers


# проверяем что для подкатегорий и виртуальных категорий
# передается поле deep_link
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_deep_link_for_response_products(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
):
    location = const.LOCATION
    category_deep_link = 'virtual-category-deeplink'
    subcategory_deep_link = 'subcategory-deeplink'

    categories_data = [
        {
            'category_id': 'category-1-subcategory-1',
            'description': 'category-1-subcategory-1-description',
            'image_url_template': (
                'category-1-subcategory-1-image-url-template'
            ),
            'title': 'category-1-subcategory-1-title',
            'deep_link': subcategory_deep_link,
        },
    ]
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, categories_data=categories_data,
    )
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(
        test_id='1', add_short_title=True, deep_link=category_deep_link,
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
    assert [
        item['deep_link']
        for item in response.json()['products']
        if 'deep_link' in item
    ] == [category_deep_link, subcategory_deep_link]


# проверяет, корректно ли переводится описание и ингредиенты
@experiments.DESCRIPTION_INGREDIENTS_CONTENT
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.config(
    GROCERY_LOCALIZATION_PRODUCT_DESCRIPTION={
        'keyset': 'wms_items',
        'suffix': '_description',
    },
)
@pytest.mark.parametrize('locale', ['en', 'ru'])
@pytest.mark.parametrize(
    'product_id',
    [
        pytest.param('product-1', id='translation exists'),
        pytest.param('product-2', id='translation is absent'),
        pytest.param('product-3', id='translation is empty'),
    ],
)
async def test_modes_translate_product_card_content(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        locale,
        test_handler,
        grocery_products,
        product_id,
):
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': product_id,
                'quantity_limit': '5',
            },
        ],
    )
    layout = common.build_basic_layout(grocery_products)

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            'virtual-category-1',
        ),
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'content' in response_json['products'][2]

    content = response_json['products'][2]['content']

    expected_result = load_json(
        'modes_translate_product_content_expected.json',
    )[product_id][locale]

    assert content == expected_result


# Проверяем, что лайки прорастают в ответ ручек
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_favorites(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        test_handler,
        grocery_products,
        mockserver,
        grocery_fav_goods,
):
    common.prepare_overlord_catalog_json(load_json, overlord_catalog)
    layout = common.build_basic_layout(grocery_products)

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/favorites/list')
    def _mock_favorite(request):
        return {'products': [{'product_id': 'product-1', 'is_favorite': True}]}

    grocery_fav_goods.add_favorite(
        yandex_uid=common.DEFAULT_UID, product_id='product-1',
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            'virtual-category-1',
        ),
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    product_1_in_response = False
    product_2_in_response = False
    for product in response.json()['products']:
        if product['id'] == 'product-1':
            assert product['is_favorite']
            product_1_in_response = True
        if product['id'] == 'product-2':
            assert 'is_favorite' not in product
            product_2_in_response = True
    assert product_1_in_response and product_2_in_response


# Проверяем, что приходят легальные ограничения в ручках
# modes/category, modes/category-group
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_common_category_legal_restrictions(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        test_handler,
        grocery_products,
):
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        common.DEFAULT_LOCATION,
        products_data=load_json(
            'overlord_catalog_products_data_with_options.json',
        ),
    )
    layout = common.build_basic_layout(grocery_products)

    virtual_category = 'virtual-category-1'
    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            virtual_category,
        ),
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    category_in_response = False
    for product in response.json()['products']:
        if product['id'] == virtual_category:
            assert product['legal_restrictions'] == ['RU_18+']
            category_in_response = True
    assert category_in_response


# Проверяем, что приходят легальные ограничения в ручках
# modes/category, modes/category-group
@common.HANDLERS
@conftest.DIFFERENT_LAYOUT_SOURCE
@pytest.mark.parametrize(
    'item_meta,expected_items',
    [
        pytest.param(
            '{"show_empty_subcategories": true}',
            ['virtual-category-1', 'category-1-subcategory-1'],
            id='show empty',
        ),
        pytest.param('{ }', ['virtual-category-1'], id='dont show empty'),
    ],
)
async def test_modes_common_empty_subcategories(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        test_handler,
        grocery_products,
        item_meta,
        expected_items,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, product_stocks=[],
    )
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')
    virtual_category.item_meta = item_meta
    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            layout.group_ids_ordered[0],
            virtual_category.virtual_category_id,
        ),
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    actual_items = []
    for product in response.json()['products']:
        actual_items.append(product['id'])
    assert actual_items == expected_items


# Проверяем, что возвращаются маркетинговые описания
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.translations(
    marketing_description_text={
        'external_id_1_text': {'en': 'description_text'},
    },
    marketing_description_list_items={
        'external_id_1.0': {'en': 'descriptions_item_0'},
        'external_id_1.1': {'en': 'descriptions_item_1'},
        'external_id_1.2': {'en': 'descriptions_item_2'},
        'external_id_1.4': {'en': 'descriptions_item_4'},
    },
)
async def test_product_marketing_description(grocery_modes):
    product_id = 'product-1'
    [layout, virtual_category] = grocery_modes.add_product(
        product_id=product_id,
    )

    response = await grocery_modes.post(product_id, layout, virtual_category)

    assert response.status_code == 200
    product = grocery_modes.get_products(response.json())[0]
    assert product['marketing_description'] == {
        'text': 'description_text',
        'list_items': [
            'descriptions_item_0',
            'descriptions_item_1',
            'descriptions_item_2',
        ],
    }


# Проверяем, что достаем новые title из вмсного или
# голубиного кейсетов в зависимости от конфига
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.translations(
    pigeon_product_title={'external_id_1': {'en': 'pigeon_title'}},
    wms_items={'product-1_title': {'en': 'wms_title'}},
)
@pytest.mark.parametrize(
    'pigeon_enabled,title',
    [
        pytest.param(True, 'pigeon_title', id='pigeon'),
        pytest.param(False, 'wms_title', id='wms'),
    ],
)
async def test_product_pigeon_titles(
        taxi_config, pigeon_enabled, title, grocery_modes,
):
    taxi_config.set(
        GROCERY_LOCALIZATION_PIGEON_PRODUCT_TITLE={
            'keyset': 'pigeon_product_title',
            'enabled': pigeon_enabled,
        },
    )
    product_id = 'product-1'
    [layout, virtual_category] = grocery_modes.add_product(
        product_id=product_id,
    )

    response = await grocery_modes.post(product_id, layout, virtual_category)
    assert response.status_code == 200
    product = grocery_modes.get_products(response.json())[0]
    assert product['title'] == title


# Проверяем, что возвращаются детальные описания
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.DESCRIPTION_INGREDIENTS_CONTENT
@pytest.mark.translations(
    detailed_ingredients_list_items_titles={
        'external_id_2.0': {'en': 'ingredients_text_0'},
        'external_id_2.1': {'en': 'ingredients_text_1'},
        'external_id_2.2': {'en': 'ingredients_text_2'},
        'external_id_2.3': {'en': 'ingredients_text_3'},
    },
    detailed_ingredients_list_items_texts={
        'external_id_2.0': {'en': 'ingredients_item_0'},
        'external_id_2.1': {'en': 'ingredients_item_1'},
        'external_id_2.2': {'en': 'ingredients_item_2'},
        'external_id_2.4': {'en': 'ingredients_item_4'},
    },
)
async def test_product_detailed_ingredients(grocery_modes):
    product_id = 'product-2'
    [layout, virtual_category] = grocery_modes.add_product(
        product_id=product_id,
    )

    response = await grocery_modes.post(product_id, layout, virtual_category)

    assert response.status_code == 200
    product = next(
        product
        for product in grocery_modes.get_products(response.json())
        if product['id'] == product_id
    )
    assert product['content']['items'] == [
        {
            'attributes': ['ingredients'],
            'title': f'ingredients_text_{i}',
            'type': 'text',
            'value': f'ingredients_item_{i}',
        }
        for i in range(3)
    ]
