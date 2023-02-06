# pylint: disable=too-many-lines
import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}

CATEGORIES_BASE_REQUEST = {
    'slug': 'slug',
    'categories': [{'id': 1, 'min_items_count': 1, 'max_items_count': 4}],
}

CASHBACK_ENABLED_SETTINGS = utils.dynamic_categories_config(
    cashback_enabled=True,
)


DEFAULT_PICTURE_URL = (
    'https://avatars.mds.yandex.net/get-eda'
    + '/3770794/4a5ca0af94788b6e40bec98ed38f58cc/{w}x{h}'
)

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
]


DEFAULT_EATS_DISCOUNTS_RESPONSE = {
    'match_results': [
        {
            'hierarchy_name': 'menu_discounts',
            'discounts': [
                {
                    'discount_id': '1',
                    'discount_meta': {
                        'promo': {
                            'name': 'Название акции',
                            'description': 'Описание',
                            'picture_uri': 'some_uri',
                        },
                    },
                    'money_value': {
                        'menu_value': {
                            'value_type': 'absolute',
                            'value': '3.0',
                        },
                    },
                },
            ],
            'subquery_results': [{'id': PUBLIC_IDS[2], 'discount_id': '1'}],
        },
    ],
}

EXPECTED_ITEMS = [
    {
        'id': 3,
        'public_id': PUBLIC_IDS[2],
        'name': 'Апельсины',
        'description': 'Описание Апельсины',
        'available': True,
        'inStock': 25,
        'price': 4,
        'decimalPrice': '4.00',
        'promoPrice': 1,
        'decimalPromoPrice': '1.00',
        'promoTypes': [
            {
                'id': 100,
                'name': 'Скидка деньгами',
                'pictureUri': 'some_uri',
                'text': '–75%',
                'type': 'price_discount',
            },
        ],
        'optionGroups': [],
        'picture': {'url': 'url_1/{w}x{h}', 'scale': 'aspect_fit'},
        'adult': False,
        'shippingType': 'pickup',
        'sortOrder': 1,
    },
    {
        'id': 2,
        'public_id': PUBLIC_IDS[1],
        'name': 'Яблоки',
        'description': 'Описание Яблоки',
        'available': True,
        'inStock': None,
        'price': 5,
        'decimalPrice': '5.00',
        'promoPrice': 3,
        'decimalPromoPrice': '3.00',
        'promoTypes': [
            {
                'id': 25,
                'name': 'Скидка для магазинов.',
                'pictureUri': (
                    'https://avatars.mds.yandex.net/get-eda/'
                    '1370147/5b73e9ea19587/80x80'
                ),
                'text': '–40%',
                'type': 'price_discount',
            },
        ],
        'optionGroups': [],
        'picture': {'url': 'url_1/{w}x{h}', 'scale': 'aspect_fit'},
        'weight': '1 кг',
        'adult': False,
        'shippingType': 'pickup',
        'sortOrder': 2,
    },
]


async def get_goods_response(taxi_eats_products, body: dict, headers=None):
    return await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=body, headers=headers or {},
    )


@pytest.mark.pgsql('eats_products', files=['pg_eats_products.sql'])
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_discounts_applicator(
        taxi_eats_products,
        mock_v1_nomenclature,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_context,
        add_default_product_mapping,
        eats_order_stats,
        mock_eats_tags,
):
    """
        Тест на проверку добавления скидки на товар (Проверка по всем полям)
    """
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[2], 'absolute', 3,
    )
    mock_v2_match_discounts_context.set_use_tags(True)
    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_v1_nomenclature.times_called == 1
    category = response.json()['payload']['categories'][0]
    assert len(category['items']) == 2
    assert category['items'] == EXPECTED_ITEMS


@pytest.mark.pgsql('eats_products', files=['pg_eats_products.sql'])
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_discounts_applicator_float_discount(
        taxi_eats_products,
        mock_v1_nomenclature,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_context,
        add_default_product_mapping,
        eats_order_stats,
        mock_eats_tags,
):
    """
        Тест на проверку отсутствия округления скидки на товар
    """
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[1], 'absolute', 0.5,
    )
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[2], 'fraction', 2,
    )
    mock_v2_match_discounts_context.set_use_tags(True)

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_v1_nomenclature.times_called == 1
    category = response.json()['payload']['categories'][0]
    assert len(category['items']) == 2
    assert category['items'][0]['decimalPromoPrice'] == '3.92'
    assert category['items'][1]['decimalPromoPrice'] == '2.50'


@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
@utils.matching_discounts_experiments(True, 'one_for_match')
@utils.matching_discounts_experiments(True, 'two_for_match')
@utils.matching_discounts_experiments(False, 'three_for_match')
async def test_menu_discount_category_discounts(
        taxi_eats_products,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        cache_add_discount_product,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_eats_tags,
):
    # Проверяется, что в ответ меню при запросе скидочной категории,
    # добавяться скидки из eats-discounts
    # А так же при наличии скидки и у партнера и в eats-discounts,
    # применится лучшая, товар не будет дублирован
    cache_add_discount_product('item_id_2')
    cache_add_discount_product('item_id_3')
    cache_add_discount_product('item_id_7')

    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[1])
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[2])
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[3])

    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=50, parent_category_ids=[],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], old_price=60, price=50, parent_category_ids=[],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], old_price=70, price=60, parent_category_ids=[],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[3], price=80, parent_category_ids=[],
    )

    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=20,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[2], value_type='absolute', value=25,
    )
    mock_v2_fetch_discounts_context.add_match_experiments('one_for_match')
    mock_v2_fetch_discounts_context.add_match_experiments('two_for_match')
    mock_v2_fetch_discounts_context.set_use_tags(True)
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    items = response.json()['payload']['categories'][0]['items']
    assert set(item['public_id'] for item in items) == {
        PUBLIC_IDS[2],
        PUBLIC_IDS[0],
        PUBLIC_IDS[1],
    }


@pytest.mark.parametrize('request_category', [True, False])
@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
async def test_menu_discount_category_no_discounts_in_lib(
        taxi_eats_products,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_v1_nomenclature_context,
        mock_nomenclature_v2_details_context,
        request_category,
):
    # Проверяется, что если в либе нет скидок, только продукт с кешбеком,
    # то категория все равно не вернется
    mock_nomenclature_v2_details_context.add_product(PUBLIC_IDS[0], price=50)
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=20,
    )

    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', 6),
    )

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    if request_category:
        request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    assert mock_nomenclature_v2_details_context.handler.times_called == 0
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert (
        categories[0]['id'] == utils.DISCOUNT_CATEGORY_ID
    ) == request_category
    assert not categories[0]['items']


@pytest.mark.parametrize('request_category', [True, False])
@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
async def test_menu_discount_category_discounts_only_lib(
        taxi_eats_products,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_v1_nomenclature_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        request_category,
):
    # Проверяется, что если скидок нет в кеше, только в либе,
    # категория Скидки возвращается
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0], price=50)
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=20,
    )

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    if request_category:
        request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    assert (
        mock_nomenclature_static_info_context.handler.times_called
        == request_category
    )
    assert (
        mock_nomenclature_dynamic_info_context.handler.times_called
        == request_category
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == utils.DISCOUNT_CATEGORY_ID
    if request_category:
        assert len(categories[0]['items']) == 1


@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True, discount_enabled=True,
    ),
)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.repeat_category()
async def test_menu_repeat_category_discounts(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_context,
        mock_nomenclature_v2_details_context,
        add_place_products_mapping,
        eats_order_stats,
        mock_eats_tags,
        mock_retail_categories_brand_orders_history,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=PUBLIC_IDS[1],
            ),
            conftest.ProductMapping(
                origin_id='item_id_3', core_id=3, public_id=PUBLIC_IDS[2],
            ),
        ],
    )
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[1], 'absolute', 20,
    )
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[2], 'fraction', 50,
    )
    mock_v2_match_discounts_context.set_use_tags(True)
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[1], price=120, promo_price=100, shipping_type='all',
    )
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[2], price=150, promo_price=120, shipping_type='all',
    )
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == make_repeat_category_response(load_json)

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_nomenclature_v2_details_context.handler.times_called == 1
    assert mock_retail_categories_brand_orders_history.times_called == 1


@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_discounts_applicator_product_discount(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_v1_nomenclature_context,
        mock_v2_match_discounts_context,
        mock_eats_catalog_storage,
        add_default_product_mapping,
        eats_order_stats,
        mock_eats_tags,
):
    """
        Тест скидки на покупку нескольких товаров(1+1)
    """
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 6

    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[2], promo_product=True,
    )
    mock_v2_match_discounts_context.set_use_tags(True)
    category = conftest.NomenclatureCategory('category_id_1', 'Фрукты', 6)
    category.add_product(
        conftest.NomenclatureProduct(
            public_id=PUBLIC_IDS[2],
            nom_id='item_id_3',
            description='Описание Апельсины',
            name='Апельсины',
            in_stock=25,
            price=4,
            shipping_type='pickup',
            is_catch_weight=False,
        ),
    )
    category.add_product(
        conftest.NomenclatureProduct(
            public_id=PUBLIC_IDS[1],
            nom_id='item_id_2',
            price=5,
            shipping_type='pickup',
            is_catch_weight=True,
        ),
    )

    mock_v1_nomenclature_context.add_category(category)

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_v1_nomenclature_context.handler.times_called == 1
    assert response.json() == load_json('expected_product_promo_response.json')


@pytest.mark.pgsql('eats_products', files=['pg_eats_products.sql'])
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
async def test_menu_cashback(
        taxi_eats_products,
        load_json,
        mock_v1_nomenclature,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_cashback,
        add_default_product_mapping,
):
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_cashback.times_called == 1
    assert mock_v1_nomenclature.times_called == 1
    assert response.json() == load_json('expected_response_cashback.json')


@pytest.mark.parametrize(
    'cashback_enabled',
    [
        pytest.param(
            True,
            id='cashback enabled',
            marks=[experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED],
        ),
        pytest.param(False, id='cashback disabled'),
    ],
)
@pytest.mark.parametrize(
    'discount_enabled',
    [
        pytest.param(
            True,
            id='discount enabled v1',
            marks=[experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED],
        ),
        pytest.param(False, id='discount disabled'),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
async def test_menu_discount_category_cashback(
        taxi_eats_products,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        cashback_enabled,
        discount_enabled,
):
    # Проверяем, что если в Скидочной категории нужны скидки или кешбек
    # из либы, то ходим в либу только 1 раз и скидки и кешбек при этом
    # правильно применяются
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = utils.DISCOUNT_CATEGORY_ID
    cashback = 33
    price = 100
    partner_promo_price = 90
    lib_discount = 20
    total_promo_price = partner_promo_price - lib_discount

    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], old_price=price, price=partner_promo_price,
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=cashback,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=lib_discount,
    )

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert (
        mock_eats_catalog_storage.times_called == discount_enabled
        or cashback_enabled
    )
    assert (
        mock_v2_fetch_discounts_context.handler.times_called
        == discount_enabled
        or cashback_enabled
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    items = categories[0]['items']
    assert len(items) == 1
    if cashback_enabled:
        assert items[0]['promoTypes'][1]['value'] == cashback
    else:
        assert len(items[0]['promoTypes']) == 1
    if discount_enabled:
        assert items[0]['promoPrice'] == total_promo_price
    else:
        assert items[0]['promoPrice'] == partner_promo_price


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True, discount_enabled=True,
    ),
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.repeat_category()
async def test_menu_repeat_category_cashback(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_cashback,
        mock_nomenclature_v2_details,
        mock_retail_categories_brand_orders_history,
):
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_repeat_category_cashback_response.json',
    )

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_cashback.times_called == 1
    assert mock_nomenclature_v2_details.times_called == 1
    assert mock_retail_categories_brand_orders_history.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.redis_store(file='redis_top_products_cache')
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.products_scoring()
@utils.matching_discounts_experiments(True, 'one_for_match')
@utils.matching_discounts_experiments(True, 'two_for_match')
@utils.matching_discounts_experiments(False, 'three_for_match')
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_get_categories_discounts(
        taxi_eats_products,
        load_json,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_eats_nomenclature_categories,
        eats_order_stats,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        mock_eats_tags,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=PUBLIC_IDS[1],
            ),
            conftest.ProductMapping(
                origin_id='item_id_3', core_id=3, public_id=PUBLIC_IDS[2],
            ),
        ],
    )
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[1], 'absolute', 20,
    )
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[2], 'fraction', 50,
    )

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[1], price=120, promo_price=100, shipping_type='all',
    )
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[2], price=150, promo_price=120, shipping_type='all',
    )

    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=100, old_price=120,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1],
        measure={'unit': 'KGRM', 'value': 1},
        name='item_4',
        images=[],
        description_general='ghi',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], price=120, old_price=150,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[2],
        measure={'unit': 'KGRM', 'value': 1},
        name='item_4',
        images=[],
        description_general='ghi',
    )
    mock_nomenclature_get_parent_context.add_category('1')
    mock_v2_match_discounts_context.add_match_experiments('one_for_match')
    mock_v2_match_discounts_context.add_match_experiments('two_for_match')
    mock_v2_match_discounts_context.set_use_tags(True)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=CATEGORIES_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert (
        response.json()['categories'][0]['items']
        == load_json('expected_category_response.json')['payload'][
            'categories'
        ][0]['items']
    )
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.products_scoring()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_get_categories_cashback(
        taxi_eats_products,
        load_json,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_cashback,
        mock_nomenclature_v2_details_context,
        mock_eats_nomenclature_categories,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[1], shipping_type='all', price=5, promo_price=3,
    )
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[2], shipping_type='all', price=6, promo_price=5,
    )

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1],
        measure={'unit': 'KGRM', 'value': 1},
        name='item_4',
        images=[],
        description_general='ghi',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=3, old_price=5,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[2],
        measure={'unit': 'KGRM', 'value': 1},
        name='item_4',
        images=[],
        description_general='ghi',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], price=5, old_price=6,
    )
    mock_nomenclature_get_parent_context.add_category('1')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=CATEGORIES_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_cashback.times_called == 1
    assert (
        response.json()['categories'][0]['items']
        == load_json('expected_discount_category_cashback_response.json')[
            'payload'
        ]['categories'][0]['items']
    )
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='discounts',
            marks=[experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED],
        ),
        pytest.param(
            id='cashback',
            marks=[experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED],
        ),
        pytest.param(
            id='cashback and discounts',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(
    ['zadd', 'scores:top:yt_table_v3:1:1', '0.00003', 'item_id_2'],
    ['zadd', 'scores:top:yt_table_v3:1:2', '0.00003', 'item_id_2'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.products_scoring()
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_get_categories_cashback_multiple(
        taxi_eats_products,
        load_json,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_cashback,
        mock_nomenclature_v2_details_context,
        mockserver,
        eats_order_stats,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    # Тест проверят, что в ручке get-categories нет лишних походов в либу
    # eats-discounts-applicator за скидками и кешбком
    for public_id in PUBLIC_IDS[:2]:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_product_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category('1')
    mock_nomenclature_get_parent_context.add_category('2')

    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request['categories'] = [
        {'id': 1, 'min_items_count': 1, 'max_items_count': 1},
        {'id': 2, 'min_items_count': 1, 'max_items_count': 1},
    ]

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_match_discounts_cashback.times_called == 1
    assert len(response.json()['categories']) == 2
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_product_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_product_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@pytest.mark.parametrize(
    'has_category',
    [
        pytest.param(
            True,
            id='has category',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
                experiments.CASHBACK_CATEGORY_ENABLED,
            ],
        ),
        pytest.param(
            False,
            id='config disabled',
            marks=[experiments.CASHBACK_CATEGORY_ENABLED],
        ),
        pytest.param(
            False,
            id='category exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
                experiments.CASHBACK_CATEGORY_DISABLED,
            ],
        ),
        pytest.param(
            False,
            id='no category exp',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('nmn_integration_version', ['v1', 'v2'])
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_has_cashback_category(
        mock_nomenclature_for_v2_menu_goods,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        has_category,
        nmn_integration_version,
):
    # Проверяет наличие категории "Кeшбек" в ответе по конфигу и экспу
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST,
        integration_version=nmn_integration_version,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == has_category
    assert mock_v2_fetch_discounts_context.handler.times_called == has_category
    categories = set(c['id'] for c in response.json()['payload']['categories'])
    assert (utils.CASHBACK_CATEGORY_ID in categories) == has_category


@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@pytest.mark.parametrize('request_category', [True, False])
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.cashback_category_enabled(10)
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS)
async def test_menu_min_cashback_category(
        taxi_eats_products,
        mockserver,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details,
        request_category,
        cashback_handles_version,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
):
    # Проверяется, что категория не вернется, если количество товаров меньше,
    # чем установлено в эксперименте (10 штук)
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def mock_eats_nomenclature(request):
        return {'categories': []}

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    if request_category:
        request['category'] = utils.CASHBACK_CATEGORY_ID

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1

    full_info_called = 1 if cashback_handles_version == 'v2' else 0
    nomenclature_called = 0 if cashback_handles_version == 'v2' else 1

    if request_category:
        assert mock_nomenclature_v2_details.times_called == nomenclature_called
        assert (
            mock_nomenclature_dynamic_info_context.handler.times_called
            == full_info_called
        )
        assert (
            mock_nomenclature_static_info_context.handler.times_called
            == full_info_called
        )
    else:
        assert mock_eats_nomenclature.times_called == 1
    categories = set(c['id'] for c in response.json()['payload']['categories'])
    assert utils.CASHBACK_CATEGORY_ID not in categories


@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS)
async def test_menu_cashback_category(
        taxi_eats_products,
        load_json,
        cashback_handles_version,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_eats_tags,
):
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = utils.CASHBACK_CATEGORY_ID

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1],
        name='item_2',
        images=[{'url': 'url_2', 'sort_order': 0}],
        description_general='def',
        shipping_type='delivery',
        is_catch_weight=False,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=3, old_price=5, in_stock=99,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[2],
        name='item_3',
        images=[],
        description_general='ghi',
        is_catch_weight=False,
        shipping_type='delivery',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], price=5, old_price=6,
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[1], value_type='absolute', value=15,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[2], value_type='absolute', value=100,
    )
    mock_v2_fetch_discounts_context.set_use_tags(True)

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    if cashback_handles_version == 'v1':
        assert mock_nomenclature_v2_details.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert response.json() == load_json(
        'expected_cashback_category_response.json',
    )


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    'has_category',
    [
        pytest.param(
            True,
            id='has category',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
                experiments.CASHBACK_CATEGORY_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
            ],
        ),
        pytest.param(
            False,
            id='config disabled',
            marks=[
                experiments.CASHBACK_CATEGORY_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
            ],
        ),
        pytest.param(
            False,
            id='category exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
                experiments.CASHBACK_CATEGORY_DISABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
            ],
        ),
        pytest.param(
            False,
            id='no category exp',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
                experiments.CASHBACK_DISCOUNTS_ENABLED,
            ],
        ),
        pytest.param(
            False,
            id='cashback exp on our side disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
                experiments.CASHBACK_CATEGORY_ENABLED,
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.products_scoring()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
async def test_get_categories_has_cashback_category(
        taxi_eats_products,
        mockserver,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        load_json,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        has_category,
):
    # Проверяет наличие категории "Кeшбек" в ответе по конфигу и экспу
    for public_id in PUBLIC_IDS[:2]:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_product_categories(request):
        return load_json('v1_product_categories_response.json')

    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request['categories'][0]['id'] = utils.CASHBACK_CATEGORY_ID
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[1], value_type='absolute', value=15,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[2], value_type='absolute', value=100,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_v2_fetch_discounts_context.handler.times_called == has_category
    categories = set(c['id'] for c in response.json()['categories'])
    assert (utils.CASHBACK_CATEGORY_ID in categories) == has_category
    if handlers_version == 'v1':
        assert (
            mock_nomenclature_v2_details_context.handler.times_called
            == has_category
        )
        assert mock_product_categories.times_called == has_category
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_product_categories.times_called == 0
        assert (
            mock_nomenclature_static_info_context.handler.times_called
            == has_category
        )
        assert (
            mock_nomenclature_dynamic_info_context.handler.times_called
            == has_category
        )
        assert (
            mock_nomenclature_get_parent_context.handler.times_called
            == has_category
        )


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    'should_reverse',
    [
        pytest.param(
            True,
            id='has scores',
            marks=[
                pytest.mark.redis_store(
                    [
                        'hset',
                        'scores:brands:yt_table_v3:1',
                        'item_id_3',
                        '0.00003',
                    ],
                    [
                        'hset',
                        'scores:brands:yt_table_v3:1',
                        'item_id_2',
                        '0.00002',
                    ],
                ),
            ],
        ),
        pytest.param(False, id='no scores'),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.products_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
async def test_get_categories_cashback_category(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        should_reverse,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_product_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[1], shipping_type='all', price=5, promo_price=3,
    )
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[2], shipping_type='all', price=6, promo_price=5,
    )

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1],
        measure={'unit': 'KGRM', 'value': 1},
        name='item_4',
        images=[],
        description_general='ghi',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=3, old_price=5,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[2],
        measure={'unit': 'KGRM', 'value': 1},
        name='item_4',
        images=[],
        description_general='ghi',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], price=5, old_price=6,
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[1], value_type='absolute', value=15,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[2], value_type='absolute', value=100,
    )
    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request['categories'][0]['id'] = utils.CASHBACK_CATEGORY_ID

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_product_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_product_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    expected_response = load_json(
        'expected_cashback_get_categories_response.json',
    )
    if should_reverse:
        items = expected_response['categories'][0]['items']
        items.reverse()
    assert response.json() == expected_response


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    ['min_products', 'max_products'], [(1, 1), (1, 2), (1, 3), (2, 2), (3, 4)],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
@experiments.products_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
async def test_get_categories_cashback_category_min_max(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        min_products,
        max_products,
):
    # Проверяет минимальное и максимальное количество товаров в ответе
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_product_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[1], value_type='absolute', value=15,
    )
    for public_id in PUBLIC_IDS[:2]:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request_category = request['categories'][0]
    request_category['id'] = utils.CASHBACK_CATEGORY_ID
    request_category['min_items_count'] = min_products
    request_category['max_items_count'] = max_products

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    empty_categories_times_called = 1 if min_products <= 2 else 0
    if handlers_version == 'v1':
        assert (
            mock_nomenclature_v2_details_context.handler.times_called
            == empty_categories_times_called
        )
        assert (
            mock_product_categories.times_called
            == empty_categories_times_called
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_product_categories.times_called == 0
        assert (
            mock_nomenclature_static_info_context.handler.times_called
            == empty_categories_times_called
        )
        assert (
            mock_nomenclature_dynamic_info_context.handler.times_called
            == empty_categories_times_called
        )
        assert (
            mock_nomenclature_get_parent_context.handler.times_called
            == empty_categories_times_called
        )
    if min_products <= 2:
        items = response.json()['categories'][0]['items']
        assert min_products <= len(items) <= max_products
    else:
        assert not response.json()['categories']


@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@pytest.mark.parametrize(
    'category_id, handlers_v2',
    [
        pytest.param(1, False),
        pytest.param(utils.DISCOUNT_CATEGORY_ID, True),
        pytest.param(utils.REPEAT_CATEGORY_ID, False),
        pytest.param(utils.POPULAR_CATEGORY_ID, False),
        pytest.param(utils.CASHBACK_CATEGORY_ID, False),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        True, True, True, True,
    ),
)
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
@experiments.repeat_category()
@experiments.popular_category()
@experiments.CASHBACK_CATEGORY_ENABLED
async def test_menu_cashback_with_discounts(
        taxi_eats_products,
        mock_eats_catalog_storage,
        mock_v2_match_discounts_context,
        category_id,
        handlers_v2,
        cashback_handles_version,
        mock_nomenclature_v2_details_context,
        mock_v1_nomenclature_context,
        mock_v2_fetch_discounts_context,
        eats_order_stats,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_retail_categories_brand_orders_history,
):
    price = 100
    discount = 20.0
    partner_promo_price = 90
    cashback_percent = 0.4
    total_promo_price = partner_promo_price - discount
    cashback_value = total_promo_price * cashback_percent

    if handlers_v2:
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[2])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[2], old_price=price, price=90,
        )
    else:
        product = conftest.NomenclatureProduct(PUBLIC_IDS[2], price, 90)
        category = conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1)
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[2])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[2], old_price=price, price=90,
        )
        category.add_product(product)
        mock_v1_nomenclature_context.add_category(category)

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[2], price, promo_price=partner_promo_price,
    )

    mock_v2_match_discounts_context.add_cashback_product(
        PUBLIC_IDS[2], 'fraction', cashback_percent * 100,
    )
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_IDS[2], 'absolute', discount,
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[2], 'fraction', cashback_percent * 100,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[2], 'absolute', discount,
    )

    mock_retail_categories_brand_orders_history.add_default_products()

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_eats_catalog_storage.has_calls
    items = response.json()['payload']['categories'][0]['items']
    assert len(items) == 1
    assert items[0]['price'] == price
    assert items[0]['promoPrice'] == total_promo_price
    assert items[0]['promoTypes'][1]['value'] == cashback_value
    assert mock_retail_categories_brand_orders_history.times_called == (
        1 if category_id == utils.REPEAT_CATEGORY_ID else 0
    )


def make_basic_category_response(load_json, category_id, category_name):
    response = load_json('expected_category_response.json')
    response['payload']['categories'][0]['id'] = category_id
    response['payload']['categories'][0]['name'] = category_name
    response['payload']['categories'][0]['uid'] = str(category_id)
    parent_id = response['payload']['categories'][0]['parentId']
    if parent_id:
        response['payload']['categories'][0]['parent_uid'] = str(parent_id)
    return response


def make_repeat_category_response(load_json):
    return make_basic_category_response(
        load_json, utils.REPEAT_CATEGORY_ID, 'Вы уже заказывали',
    )


@pytest.fixture(name='mock_v2_match_discounts')
def _mock_v2_match_discounts(mockserver):
    @mockserver.json_handler(utils.Handlers.MATCH_DISCOUNTS)
    def _mock_match_discounts(request):
        return DEFAULT_EATS_DISCOUNTS_RESPONSE

    return _mock_match_discounts


@pytest.fixture(name='mock_v2_match_discounts_cashback')
def _mock_v2_match_discounts_cashback(mockserver, load_json):
    @mockserver.json_handler(utils.Handlers.MATCH_DISCOUNTS)
    def _mock_v2_match_discounts(request):
        return load_json('v2_match-discounts_response.json')

    return _mock_v2_match_discounts


@pytest.fixture(name='mock_eats_nomenclature_categories')
def _mock_eats_nomenclature_categories(mockserver, load_json):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        assert set(
            {val['origin_id'] for val in request.json['products']},
        ) == set(['item_id_4', 'item_id_2', 'item_id_3', 'item_id_1'])
        return load_json('v1_product_categories_response.json')

    return _mock_eats_nomenclature_categories


@pytest.fixture(name='mock_v1_nomenclature')
def _mock_v1_nomenclature(mockserver, load_json):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def mock_eats_nomenclature(request):
        return load_json('nomenclature-products-mapping.json')

    return mock_eats_nomenclature


@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS)
async def test_menu_cashback_category_nomenclature_v2_place_404_code(
        taxi_eats_products,
        cashback_handles_version,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
):
    # Тест проверяет, что если
    # /eats-nomenclature/v2/place/assortment/details
    # возвращает 404, то ручка тоже возвращает 404
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = utils.CASHBACK_CATEGORY_ID

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )

    mock_nomenclature_v2_details_context.set_status(status_code=404)
    mock_nomenclature_static_info_context.set_status(status_code=404)
    mock_nomenclature_dynamic_info_context.set_status(status_code=404)

    response = await get_goods_response(
        taxi_eats_products, request, PRODUCTS_HEADERS,
    )
    assert response.status_code == 404
    assert mock_eats_catalog_storage.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    full_info_called = 1 if cashback_handles_version == 'v2' else 0
    nomenclature_called = 0 if cashback_handles_version == 'v2' else 1

    assert (
        mock_nomenclature_v2_details_context.handler.times_called
        == nomenclature_called
    )
    assert (
        mock_nomenclature_dynamic_info_context.handler.times_called
        == full_info_called
    )
    assert (
        mock_nomenclature_static_info_context.handler.times_called
        == full_info_called
    )
