# Общие сценарии для ручек modes/category-group и modes/category

import datetime
import enum

import pytest

# pylint: disable=too-many-lines

from . import common
from . import const
from . import experiments

DEFAULT_LOCATION = const.LOCATION

DEFAULT_GROUP_REQUEST_BODY = {
    'modes': ['grocery'],
    'position': {'location': DEFAULT_LOCATION},
    'layout_id': 'layout-1',
    'group_id': 'category-group-some-id',
    'offer_id': 'some-offer-id',
}
DEFAULT_CATEGORY_REQUEST_BODY = {
    'modes': ['grocery'],
    'position': {'location': DEFAULT_LOCATION},
    'category_path': {
        'layout_id': 'layout-1',
        'group_id': 'category-group-some-id',
    },
    'category_id': 'virtual-category-some-id',
    'offer_id': 'some-offer-id',
}

HANDLERS = pytest.mark.parametrize(
    'test_handler,request_body',
    [
        pytest.param(
            '/lavka/v1/api/v1/modes/category-group',
            DEFAULT_GROUP_REQUEST_BODY,
            id='category_group',
        ),
        pytest.param(
            '/lavka/v1/api/v1/modes/category',
            DEFAULT_CATEGORY_REQUEST_BODY,
            id='category',
        ),
    ],
)


class CategoryType(enum.IntEnum):
    PROMO_CAAS = 1
    CASHBACK_CAAS = 2
    MARKDOWN = 3
    UPSALE = 4
    RECENT_PURCHASES = 5
    HAPPY_NEW_YEAR = 6
    PERSONAL = 7
    MARKDOWN_V2 = 8


SPECIAL_CATEGORY_DATA = {
    CategoryType.PROMO_CAAS: 'promo-caas',
    CategoryType.CASHBACK_CAAS: 'cashback-caas',
    CategoryType.MARKDOWN: 'markdown',
    CategoryType.UPSALE: 'upsale',
    CategoryType.RECENT_PURCHASES: 'recent-purchases',
    CategoryType.HAPPY_NEW_YEAR: 'happy.new.year',
    CategoryType.PERSONAL: 'personal',
    CategoryType.MARKDOWN_V2: 'markdown_v2',
}

CUSTOM_CATEGORY = 'custom_category'


def _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=None,
        build_layout=True,
        use_markdown_category_tree=False,
        item_meta=None,
        layout_meta=None,
        custom_special_category=None,
):
    depot_id = const.DEPOT_ID

    if use_markdown_category_tree:
        overlord_catalog.add_category_tree(
            depot_id=depot_id,
            category_tree=load_json(
                'overlord_catalog_markdown_category_tree.json',
            ),
        )
    else:
        overlord_catalog.add_category_tree(
            depot_id=depot_id,
            category_tree=load_json(
                'overlord_catalog_category_tree_response.json',
            ),
        )
    overlord_catalog.add_categories_data(
        new_categories_data=load_json('overlord_catalog_categories_data.json'),
    )
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=load_json(
            'overlord_catalog_products_stocks.json'
            if category_type
            not in [CategoryType.MARKDOWN, CategoryType.MARKDOWN_V2]
            else 'overlord_catalog_products_stocks_markdown.json',
        ),
    )

    if build_layout:
        layout = grocery_products.add_layout(test_id='1')
        category_group = layout.add_category_group(test_id='some-id')
        special_category = SPECIAL_CATEGORY_DATA.get(
            category_type, custom_special_category,
        )
        category = category_group.add_virtual_category(
            test_id='some-id',
            special_category=special_category,
            layout_meta=layout_meta,
        )
        if item_meta is not None:
            category.item_meta = item_meta


def _validate_response(
        response, expected_items, include_default_category=True,
):
    expected_items_prepared = []
    if include_default_category:
        expected_items_prepared.append('virtual-category-some-id')
    expected_items_prepared.extend(expected_items)

    assert [
        item['id'] for item in response['modes'][0]['items']
    ] == expected_items_prepared
    assert [item['id'] for item in response['modes'][0]['items']] == [
        product['id'] for product in response['products']
    ]


def _retrieve_layout_item(response, item_type):
    return [
        item
        for item in response['modes'][0]['items']
        if item['type'] == item_type
    ]


# получаем категорию кэшбека через caas-promo
@pytest.mark.translations(
    virtual_catalog={
        'subcategory-1-title': {'en': 'subcategory 1'},
        'subcategory-2-title': {'en': 'subcategory 2'},
        'other-products-tanker-key': {'en': 'other products'},
        'virtual_category_title_some-id': {'en': 'virtual category'},
    },
    pigeon_catalog={
        'subcategory-1-title': {'en': 'subcategory 1'},
        'subcategory-2-title': {'en': 'subcategory 2'},
        'virtual_category_title_some-id': {'en': 'virtual category'},
    },
)
@pytest.mark.parametrize(
    'pigeon_data_enabled',
    [
        pytest.param(False, marks=[experiments.PIGEON_DATA_DISABLED]),
        pytest.param(True, marks=[experiments.PIGEON_DATA_ENABLED]),
    ],
)
@experiments.CASHBACK_EXPERIMENT
@HANDLERS
async def test_modes_cashback_caas(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
        load_json,
        test_handler,
        request_body,
        pigeon_data_enabled,
):
    keyset = 'pigeon_catalog' if pigeon_data_enabled else 'virtual_catalog'
    grocery_caas_promo.add_subcategory(
        subcategory_id='caas-subcategory-1',
        title_tanker_key='subcategory-1-title',
        keyset=keyset,
        is_cashback=True,
    )
    grocery_caas_promo.add_products(
        product_ids=['product-3', 'product-2'], is_cashback=True,
    )
    grocery_caas_promo.add_subcategory(
        subcategory_id='caas-subcategory-2',
        title_tanker_key='subcategory-2-title',
        keyset=keyset,
        is_cashback=True,
    )
    grocery_caas_promo.add_product(product_id='product-2', is_cashback=True)
    grocery_caas_promo.add_subcategory(
        subcategory_id='caas-other-products',
        title_tanker_key='other-products-tanker-key',
        is_cashback=True,
    )
    grocery_caas_promo.add_product(product_id='product-1', is_cashback=True)
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.CASHBACK_CAAS,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()

    expected_products = [
        ('virtual-category-some-id', 'virtual category'),
        ('caas-subcategory-1', 'subcategory 1'),
        ('product-3', 'product-3-title'),
        ('product-2', 'product-2-title'),
        ('caas-subcategory-2', 'subcategory 2'),
        ('product-2', 'product-2-title'),
        ('caas-other-products', 'other products'),
        ('product-1', 'product-1-title'),
    ]
    assert [
        (item['id'], item['title'])
        for item in response_json['modes'][0]['items']
    ] == expected_products
    assert [item['id'] for item in response_json['modes'][0]['items']] == [
        product['id'] for product in response_json['products']
    ]
    special_category = SPECIAL_CATEGORY_DATA[CategoryType.CASHBACK_CAAS]
    assert grocery_caas_promo.times_called(special_category) == 1


# проверяем категорию выгодно через caas-promo
# в категории находятся только товары со скидками
@experiments.PROMO_CAAS_EXPERIMENT
@HANDLERS
async def test_modes_promo_caas(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
        grocery_p13n,
        load_json,
        test_handler,
        request_body,
):
    # product-1 - есть скидка деньгами, попадает в выдачу ручки
    # product-2 - есть скидка продуктом, попадает в выдачу
    # product-3 - есть скидка продуктом, но на складе хранится 10
    # единиц, а для скидки необходимо 100, товар не попадет в выдачу ручки

    product_1 = 'product-1'
    product_2 = 'product-2'
    product_3 = 'product-3'
    grocery_caas_promo.add_subcategory(
        subcategory_id='caas-subcategory-1',
        title_tanker_key='subcategory-1-title',
    )
    grocery_caas_promo.add_products(
        product_ids=[product_1, product_2, product_3],
    )
    grocery_p13n.add_modifier(product_id=product_1, value='1.1')
    grocery_p13n.add_modifier_product_payment(
        product_id=product_2,
        payment_per_product='50',
        quantity='2',
        meta={'title_tanker_key': 'test_discount_label'},
    )
    grocery_p13n.add_modifier_product_payment(
        product_id=product_3,
        payment_per_product='50',
        quantity='100',
        meta={'title_tanker_key': 'test_discount_label'},
    )
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.PROMO_CAAS,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert [
        item['id']
        for item in response_json['modes'][0]['items']
        if item['type'] == 'good'
    ] == [product_1, product_2]
    special_category = SPECIAL_CATEGORY_DATA[CategoryType.PROMO_CAAS]
    assert grocery_caas_promo.times_called(special_category) == 1


# проверяем что флаг pigeon_data_enabled передается в ручку
# сервиса grocery-caas-promo
@experiments.PROMO_CAAS_EXPERIMENT
@pytest.mark.parametrize(
    'pigeon_data_enabled',
    [
        pytest.param(False, marks=[experiments.PIGEON_DATA_DISABLED]),
        pytest.param(True, marks=[experiments.PIGEON_DATA_ENABLED]),
    ],
)
async def test_modes_promo_caas_pigeon_request(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
        pigeon_data_enabled,
):
    _prepare_test_context(
        overlord_catalog, grocery_products, load_json, CategoryType.PROMO_CAAS,
    )

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/discounts',
    )
    def discounts_handler(request):
        assert request.json['pigeon_data_enabled'] == pigeon_data_enabled
        return {'items': [], 'products': [], 'subcategories': []}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=DEFAULT_CATEGORY_REQUEST_BODY,
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert discounts_handler.times_called == 1


@experiments.PROMO_CAAS_EXPERIMENT
@experiments.CASHBACK_EXPERIMENT
@pytest.mark.parametrize(
    'special_category,handler',
    [
        pytest.param(CategoryType.PROMO_CAAS, 'discounts'),
        pytest.param(CategoryType.CASHBACK_CAAS, 'cashback'),
    ],
)
async def test_modes_promo_caas_offer_time(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
        offers,
        special_category,
        handler,
):
    _prepare_test_context(
        overlord_catalog, grocery_products, load_json, special_category,
    )

    date = '2022-06-21T10:00:00+00:00'
    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=datetime.datetime.fromisoformat(date),
        depot_id=const.DEPOT_ID,
        location=const.LOCATION,
    )

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/' + handler,
    )
    def discounts_handler(request):
        assert request.json['offer_time'] == date
        return {'items': [], 'products': [], 'subcategories': []}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=DEFAULT_CATEGORY_REQUEST_BODY,
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert discounts_handler.times_called == 1


# проверяем что в категрии выгодно нет товаров для
# которых пришел флаг is_price_uncrossed
@experiments.PROMO_CAAS_EXPERIMENT
@HANDLERS
async def test_modes_promo_filter_by_price_strikethrough(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
        grocery_p13n,
        load_json,
        test_handler,
        request_body,
):
    product_1 = 'product-1'
    product_2 = 'product-2'
    grocery_caas_promo.add_subcategory(
        subcategory_id='caas-subcategory-1',
        title_tanker_key='subcategory-1-title',
    )
    grocery_caas_promo.add_products(product_ids=[product_1, product_2])
    grocery_p13n.add_modifier(
        product_id=product_1, value='1.0', meta={'is_price_uncrossed': False},
    )
    grocery_p13n.add_modifier(
        product_id=product_2, value='1.0', meta={'is_price_uncrossed': True},
    )
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.PROMO_CAAS,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert [
        item['id']
        for item in response_json['modes'][0]['items']
        if item['type'] == 'good'
    ] == [product_1]


# ручки отдают 200 даже при 500 от caas-promo
@HANDLERS
@pytest.mark.parametrize(
    'category_type',
    [
        pytest.param(
            CategoryType.CASHBACK_CAAS,
            marks=[experiments.CASHBACK_EXPERIMENT],
            id='cashback-caas',
        ),
        pytest.param(
            CategoryType.PROMO_CAAS,
            marks=[experiments.PROMO_CAAS_EXPERIMENT],
            id='promo-caas',
        ),
    ],
)
async def test_modes_cashback_caas_unavailable(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
        test_handler,
        request_body,
        category_type,
):
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=category_type,
    )

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/cashback',
    )
    def _mock_promo(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/discounts',
    )
    def _mock_cashback(request):
        return mockserver.make_response(status=500)

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200


# POST /lavka/v1/api/v1/modes/category-group.
# Получить информацию о спецальной категории "Markdown"
@HANDLERS
@pytest.mark.parametrize(
    'phone_id,yandex_uid',
    (
        pytest.param(
            None,
            'test_yandex_uid',
            marks=[
                pytest.mark.experiments3(
                    name='lavka_selloncogs',
                    consumers=['grocery-caas/client_library'],
                    clauses=[
                        {
                            'title': 'match yandex uid',
                            'predicate': {
                                'init': {
                                    'value': 'test_yandex_uid',
                                    'arg_name': 'yandex_uid',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            'value': {'enabled': True},
                        },
                    ],
                    is_config=True,
                ),
            ],
            id='match_by_yandex_uid',
        ),
        pytest.param(
            'test_phone_id',
            None,
            marks=[
                pytest.mark.experiments3(
                    name='lavka_selloncogs',
                    consumers=['grocery-caas/client_library'],
                    clauses=[
                        {
                            'title': 'match phone id',
                            'predicate': {
                                'init': {
                                    'value': 'test_phone_id',
                                    'arg_name': 'phone_id',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            'value': {'enabled': True},
                        },
                    ],
                    is_config=True,
                ),
            ],
            id='match_by_phone_id',
        ),
    ),
)
async def test_modes_category_groups_200_markdown(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_markdown,
        load_json,
        phone_id,
        yandex_uid,
        test_handler,
        request_body,
):
    grocery_caas_markdown.add_product(product_id='product-1')
    grocery_caas_markdown.add_product(product_id='product-2')
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.MARKDOWN,
        use_markdown_category_tree=True,
    )
    response = await taxi_grocery_api.post(
        test_handler,
        json=request_body,
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-PhoneId': phone_id},
    )
    assert response.status_code == 200
    _validate_response(response.json(), ['product-1:st-md', 'product-2:st-md'])


# Проверяем что название продуктов локализуется в спец категории
@experiments.MARKDOWN_ENABLED
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'he'])
@pytest.mark.translations(
    wms_items={
        'product-1_title': {
            'he': 'product-1-title-he',
            'ru': 'product-1-title-ru',
        },
        'product-2_title': {
            'he': 'product-2-title-he',
            'ru': 'product-2-title-ru',
        },
    },
)
@HANDLERS
@pytest.mark.parametrize('accept_language', ['ru', 'he'])
async def test_modes_category_markdown_translation(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_markdown,
        load_json,
        test_handler,
        request_body,
        accept_language,
):
    grocery_caas_markdown.add_product(product_id='product-1')
    grocery_caas_markdown.add_product(product_id='product-2')
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.MARKDOWN,
        use_markdown_category_tree=True,
    )
    response = await taxi_grocery_api.post(
        test_handler,
        json=request_body,
        headers={'Accept-Language': accept_language},
    )
    assert response.status_code == 200
    _validate_response(response.json(), ['product-1:st-md', 'product-2:st-md'])

    for item in response.json()['modes'][0]['items']:
        if item['type'] == 'good':
            assert item['title'].endswith(accept_language)

    for item in response.json()['products']:
        if item['type'] == 'good':
            assert item['title'].endswith(accept_language)


# Проверяем, что специальные категории(на примере markdown)
# корректно работают с флагом hide_if_empty.
# При hide_if_empty: false и активной и пустой специальной категории
# на фронт отдаем available: false
@experiments.MARKDOWN_ENABLED
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('available', [True, False])
async def test_modes_root_category_markdown_available(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_markdown,
        load_json,
        available,
):
    depot_id = const.DEPOT_ID
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json(
            'overlord_catalog_markdown_category_tree.json',
        ),
    )
    grocery_caas_markdown.add_product(product_id='product-1')
    grocery_caas_markdown.add_product(product_id='product-2')
    overlord_catalog.add_categories_data(
        new_categories_data=load_json('overlord_catalog_categories_data.json'),
    )
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=load_json(
            'overlord_catalog_products_stocks_markdown.json',
        )
        if available
        else {},
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='some-id')
    meta = (
        """{
        "hide_if_empty": false
    }""".replace(
            '\n', '',
        )
    )
    category_group.add_virtual_category(
        test_id='some-id', special_category='markdown', item_meta=meta,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={
            'modes': ['grocery'],
            'position': {'location': DEFAULT_LOCATION},
        },
    )

    assert response.status_code == 200
    category = next(
        item
        for item in response.json()['products']
        if item['type'] == 'category'
    )
    assert category['id'].endswith('some-id')
    assert category['available'] == available


# Проверяем правильность шаблона: разделитель и количество знаков
@common.HANDLERS
@pytest.mark.parametrize('locale', ['en', 'fr', 'ru'])
@pytest.mark.parametrize(
    'price,expected_result',
    [('5.30', '5.30'), ('5.25', '5.25'), ('1.001', '1.00')],
)
@pytest.mark.parametrize('currency', ['EUR', 'GBP', 'RUB'])
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'grocery': 0.01},
        'GBP': {'grocery': 0.01},
        '__default__': {'__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={
        'EUR': {'__default__': 2, 'iso4217': 2},
        'GBP': {'__default__': 2, 'iso4217': 2},
        'RUB': {'grocery': 2},
    },
    LOCALES_SUPPORTED=['en', 'fr', 'ru'],
)
async def test_price_format_and_trailing_zeros(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
        test_handler,
        locale,
        price,
        expected_result,
        currency,
        grocery_depots,
):
    if currency == 'RUB':
        expected_result = expected_result.split('.')[0]

    location = const.LOCATION
    depot_id = const.DEPOT_ID

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=const.DEPOT_ID,
        currency=currency,
    )

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location=location, currency=currency,
    )
    layout = common.build_basic_layout(grocery_products)
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree={
            'categories': [{'id': 'category-2-subcategory-2'}],
            'products': [
                {
                    'full_price': price,
                    'id': 'product-2',
                    'category_ids': ['category-2-subcategory-2'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )

    await taxi_grocery_api.invalidate_caches()

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-2',
        ),
        headers={'Accept-Language': locale},
    )
    assert response.status == 200
    item = next(
        item
        for item in response.json()['products']
        if item['id'] == 'product-2'
    )
    if locale == 'en':
        assert item['pricing'][
            'price_template'
        ] == '$SIGN${}$CURRENCY$'.format(expected_result)
    if locale in ('fr', 'ru'):
        expected_result = expected_result.replace('.', ',')
        assert item['pricing'][
            'price_template'
        ] == '{} $SIGN$$CURRENCY$'.format(expected_result)


# Проверяем что одна специальная категория может быть
# привязана к двум виртуальным. Виртуальные категории будут
# содержать одинаковые продукты
@experiments.CASHBACK_EXPERIMENT
async def test_modes_shared_special_category(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
        load_json,
):
    subcategory_id = 'caas-subcategory-1'
    grocery_caas_promo.add_subcategory(
        subcategory_id=subcategory_id,
        title_tanker_key='subcategory-1-title',
        is_cashback=True,
    )
    grocery_caas_promo.add_products(
        product_ids=['product-1', 'product-2'], is_cashback=True,
    )
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.CASHBACK_CAAS,
        build_layout=False,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='some-id')
    special_category = SPECIAL_CATEGORY_DATA[CategoryType.CASHBACK_CAAS]
    category_1 = category_group.add_virtual_category(
        test_id='1', special_category=special_category,
    )
    category_2 = category_group.add_virtual_category(
        test_id='2', special_category=special_category,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group',
        json=DEFAULT_GROUP_REQUEST_BODY,
        headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['modes'][0]['items']] == [
        category_1.virtual_category_id,
        subcategory_id,
        'product-1',
        'product-2',
        category_2.virtual_category_id,
        subcategory_id,
        'product-1',
        'product-2',
    ]

    special_category = SPECIAL_CATEGORY_DATA[CategoryType.CASHBACK_CAAS]
    assert grocery_caas_promo.times_called(special_category) == 1


# проверяем что возвращается скидка на уцененные товары
# товары без скидки при включенном эксперименте
# grocery_enable_markdown_discounts не возвращаются
@experiments.MARKDOWN_ENABLED
@experiments.MARKDOWN_DISCOUNTS_ENABLED
@HANDLERS
@pytest.mark.parametrize('add_discount', [True, False])
async def test_modes_category_markdown_discount(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_markdown,
        grocery_p13n,
        load_json,
        test_handler,
        request_body,
        add_discount,
):
    product_1 = 'product-1'
    product_2 = 'product-2'

    grocery_caas_markdown.add_product(product_id=product_1)
    grocery_caas_markdown.add_product(product_id=product_2)
    if add_discount:
        grocery_p13n.add_modifier(product_id=product_1 + ':st-md', value='1')
        grocery_p13n.add_modifier(product_id=product_2 + ':st-md', value='2')

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.MARKDOWN,
    )
    response = await taxi_grocery_api.post(test_handler, json=request_body)
    assert response.status_code == 200
    if add_discount:
        _validate_response(
            response.json(), [product_1 + ':st-md', product_2 + ':st-md'],
        )
        assert [
            (item['pricing']['price'], item['discount_pricing']['price'])
            for item in response.json()['products']
            if item['type'] == 'good'
        ] == [('1', '0'), ('5', '3')]
    else:
        _validate_response(response.json(), [])


# Проверяем что распроданные товары отображаются только в recent-purchases
@experiments.UPSALE_EXPERIMENT
@experiments.SHOW_SOLD_OUT_ENABLED
@experiments.RECENT_GOODS_EXP
@HANDLERS
@pytest.mark.parametrize(
    'special_category', [CategoryType.UPSALE, CategoryType.RECENT_PURCHASES],
)
async def test_modes_special_category_sold_out(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_upsale,
        load_json,
        test_handler,
        request_body,
        special_category,
        grocery_fav_goods,
):
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=special_category,
    )
    product_ids = ['product-1', 'product-2', 'product-4']
    expected_ids = ['product-1', 'product-2']
    if special_category == CategoryType.RECENT_PURCHASES:
        expected_ids.append('product-4')

    grocery_fav_goods.setup_request_checking(
        yandex_uid=common.DEFAULT_HEADERS['X-Yandex-UID'],
    )
    grocery_fav_goods.set_response_product_ids(product_ids=product_ids)
    grocery_upsale.add_products(product_ids)

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    _validate_response(response.json(), expected_ids)


# Проверяем что новогодняя категория собирается правильно
@experiments.HAPPY_NEW_YEAR
@HANDLERS
@pytest.mark.translations(
    virtual_catalog={
        'category-1-subcategory-1_name': {'en': 'subcategory name'},
    },
)
async def test_modes_happy_new_year(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
        mockserver,
):
    @mockserver.json_handler(
        '/grocery-holidays/internal/v1/holidays/v1/get-new-year-answers',
    )
    def _mock_holidays(request):
        return {'answers': [1, 3, 3, 3, 3]}

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.HAPPY_NEW_YEAR,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    expected_items = ['category-1-subcategory-1', 'product-1', 'product-2']
    _validate_response(response.json(), expected_items)
    assert [
        item['title']
        for item in _retrieve_layout_item(response.json(), 'subcategory')
    ] == ['subcategory name']


# Проверяем что новогодняя категория не возвращается,
# если из g-holidays не приходят ответы
@experiments.HAPPY_NEW_YEAR
@HANDLERS
async def test_modes_happy_new_year_holidays_404(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
        mockserver,
):
    @mockserver.json_handler(
        '/grocery-holidays/internal/v1/holidays/v1/get-new-year-answers',
    )
    def _mock_holidays(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'ANSWERS_NOT_FOUND', 'message': 'not found'},
        )

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.HAPPY_NEW_YEAR,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    expected_items = []
    _validate_response(response.json(), expected_items)


# Проверяем, что категория "Мои товары" собирается правильно
@experiments.ENABLE_PERSONAL
@pytest.mark.translations(
    virtual_catalog={
        'recent-purchases-subcategory_name': {'en': 'recent purchases'},
        'favorites-subcategory_name': {'en': 'favorites'},
    },
)
@HANDLERS
@pytest.mark.parametrize('favorites_error', [True, False])
@pytest.mark.parametrize('recent_error', [True, False])
async def test_modes_personal(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
        mockserver,
        favorites_error,
        recent_error,
):
    @mockserver.json_handler('/grocery-fav-goods/internal/v1/favorites/list')
    def _mock_favorite(request):
        if favorites_error:
            return mockserver.make_response(
                status=400, json={'code': 'NO_YANDEX_UID'},
            )
        return {
            'products': [
                {'product_id': 'product-1', 'is_favorite': True},
                {'product_id': 'product-2', 'is_favorite': False},
            ],
        }

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/recent-goods/get')
    def _mock_recent(request):
        if recent_error:
            return mockserver.make_response(
                status=400, json={'code': 'NO_YANDEX_UID'},
            )
        return {'product_ids': ['product-2', 'product-3']}

    item_meta = '{"show_empty_subcategories": true}'
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.PERSONAL,
        item_meta=item_meta,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    expected_items = ['recent-purchases-subcategory']
    if not recent_error:
        expected_items.append('product-2')
        expected_items.append('product-3')
    expected_items.append('favorites-subcategory')
    if not favorites_error:
        expected_items.append('product-1')
    _validate_response(response.json(), expected_items)
    assert [
        item['title']
        for item in _retrieve_layout_item(response.json(), 'subcategory')
    ] == ['recent purchases', 'favorites']


@experiments.ENABLE_PERSONAL
@experiments.carousel_subcategories_enabled(enabled=True, min_items_count=2)
@HANDLERS
async def test_modes_personal_carousel_subcategories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
        mockserver,
):
    @mockserver.json_handler('/grocery-fav-goods/internal/v1/favorites/list')
    def _mock_favorite(request):
        return {
            'products': [
                {'product_id': 'product-1', 'is_favorite': True},
                {'product_id': 'product-2', 'is_favorite': False},
            ],
        }

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/recent-goods/get')
    def _mock_recent(request):
        return {'product_ids': ['product-2', 'product-3']}

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.PERSONAL,
        layout_meta='{"subcategories_as_carousel":'
        + '["recent-purchases-subcategory",'
        + '"favorites-subcategory"]}',
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers=common.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    expected_items = [
        'recent-purchases-subcategory',
        'product-2',
        'product-3',
        'favorites-subcategory',
        'product-1',
    ]
    _validate_response(response.json(), expected_items)
    recents_in_response = False
    favorites_in_response = False
    for item in response.json()['modes'][0]['items']:
        # Проверяем, что заданная в экспе подкатегория приходит как карусель
        if item['id'] == 'recent-purchases-subcategory':
            assert item['type'] == 'carousel'
            recents_in_response = True
        # Проверяем, что не подходящая по количеству продуктов
        # подкатегория не является каруселью
        if item['id'] == 'favorites-subcategory':
            assert item['type'] == 'subcategory'
            favorites_in_response = True
    assert recents_in_response and favorites_in_response


# Проверяем, что категория "Мои товары" приходит в modes/root
@experiments.ENABLE_PERSONAL
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'headers,recent_response,favorite_response',
    [
        pytest.param(
            {},
            {
                'status': 400,
                'json': {
                    'code': 'NO_YANDEX_UID',
                    'message': 'No YandexUid in request or it is empty',
                },
            },
            {'status': 400, 'json': {'code': 'NO_YANDEX_UID'}},
            id='empty personal category',
        ),
        pytest.param(
            common.DEFAULT_HEADERS,
            {'status': 200, 'json': {'product_ids': ['product-2']}},
            {
                'status': 200,
                'json': {
                    'products': {
                        'product_id': 'product-2',
                        'is_favorite': True,
                    },
                },
            },
            id='personal category with products',
        ),
    ],
)
async def test_modes_root_personal(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        mockserver,
        headers,
        recent_response,
        favorite_response,
):
    @mockserver.json_handler('/grocery-fav-goods/internal/v1/favorites/list')
    def _mock_favorite(request):
        return mockserver.make_response(
            status=favorite_response['status'], json=favorite_response['json'],
        )

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/recent-goods/get')
    def _mock_recent(request):
        return mockserver.make_response(
            status=recent_response['status'], json=recent_response['json'],
        )

    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.PERSONAL,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={
            'modes': ['grocery'],
            'position': {'location': DEFAULT_LOCATION},
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['products'][1]['id'] == 'virtual-category-some-id'


@experiments.MARKDOWN_ENABLED
@HANDLERS
async def test_markdown_v2(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_markdown,
        load_json,
        test_handler,
        request_body,
):
    grocery_caas_markdown.add_product(product_id='product-1')
    grocery_caas_markdown.add_product(product_id='product-2')
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.MARKDOWN_V2,
        use_markdown_category_tree=True,
    )
    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers={},
    )
    assert response.status_code == 200
    _validate_response(response.json(), ['product-1:st-md', 'product-2:st-md'])


CUSTOM_CATEGORY = 'custom_category'


@HANDLERS
@pytest.mark.parametrize(
    'expected_items',
    [
        pytest.param(
            ['virtual-category-some-id', 'product-1', 'product-2'],
            marks=[
                experiments.custom_special_category(
                    True, CUSTOM_CATEGORY, ['product-1', 'product-2'],
                ),
                pytest.mark.config(
                    GROCERY_API_CUSTOM_SPECIAL_CATEGORIES=[CUSTOM_CATEGORY],
                ),
            ],
            id='smoke',
        ),
        pytest.param(
            ['virtual-category-some-id', 'product-1', 'product-2'],
            marks=[
                experiments.custom_special_category(
                    True, CUSTOM_CATEGORY, ['product-1', 'product-2'], True,
                ),
                pytest.mark.config(
                    GROCERY_API_CUSTOM_SPECIAL_CATEGORIES=[CUSTOM_CATEGORY],
                ),
            ],
            id='by exp-config',
        ),
        pytest.param(
            ['virtual-category-some-id'],
            marks=[
                experiments.custom_special_category(
                    True, CUSTOM_CATEGORY, ['product-1', 'product-2'],
                ),
                pytest.mark.config(GROCERY_API_CUSTOM_SPECIAL_CATEGORIES=[]),
            ],
            id='not in config',
        ),
        pytest.param(
            [],
            marks=[
                pytest.mark.config(
                    GROCERY_API_CUSTOM_SPECIAL_CATEGORIES=[CUSTOM_CATEGORY],
                ),
            ],
            id='experiment not created',
        ),
    ],
)
async def test_custom_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        request_body,
        expected_items,
):
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        custom_special_category=CUSTOM_CATEGORY,
    )

    response = await taxi_grocery_api.post(
        test_handler, json=request_body, headers={},
    )
    assert response.status_code == 200
    _validate_response(
        response.json(), expected_items, include_default_category=False,
    )


# Проверяем отключение кешбека по IP
@pytest.mark.experiments3(
    name='grocery_cashback',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'predicate': {
                        'init': {
                            'value': 'ru',
                            'arg_name': 'country_iso2_by_ip',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                },
                'type': 'not',
            },
            'value': {'enabled': False},
        },
    ],
    default_value={'enabled': True},
)
@HANDLERS
@pytest.mark.parametrize(
    'ip_address, country_iso2_by_ip',
    [('95.220.20.20', 'ru'), ('2.55.77.77', 'il')],
)
async def test_disabling_cashback_by_ip(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
        load_json,
        test_handler,
        request_body,
        ip_address,
        country_iso2_by_ip,
):
    grocery_caas_promo.add_products(
        product_ids=['product-1'], is_cashback=True,
    )
    _prepare_test_context(
        overlord_catalog,
        grocery_products,
        load_json,
        category_type=CategoryType.CASHBACK_CAAS,
    )

    headers = {'X-Remote-IP': ip_address, **common.DEFAULT_HEADERS}
    response = await taxi_grocery_api.post(
        path=test_handler, json=request_body, headers=headers,
    )
    assert response.status_code == 200
    response_data = response.json()

    assert country_iso2_by_ip in ['ru', 'il']
    expected_times_called = 0
    expected_items = ['virtual-category-some-id']
    if country_iso2_by_ip == 'ru':
        expected_times_called += 1
        expected_items.append('product-1')

    special_category = SPECIAL_CATEGORY_DATA[CategoryType.CASHBACK_CAAS]
    assert (
        grocery_caas_promo.times_called(special_category)
        == expected_times_called
    )

    assert [
        (item['id']) for item in response_data['modes'][0]['items']
    ] == expected_items
