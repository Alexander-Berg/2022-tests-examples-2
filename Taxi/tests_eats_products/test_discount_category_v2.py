import copy
from typing import Tuple

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

# Сходу не получилось вписаться в 1000 строк, да и после отказа от
# в RETAILDEV-1357 v1 файл похудеет
# pylint: disable=too-many-lines


PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}

DEFAULT_PICTURE_URL = (
    'https://avatars.mds.yandex.net/get-eda'
    + '/3770794/4a5ca0af94788b6e40bec98ed38f58cc/{w}x{h}'
)

PRODUCTS_SCORING_PERIODIC_NAME = 'products-scoring-update-periodic'
PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED = (
    'eats_products::products-scoring-update-periodic-finished'
)


def load_json_details_response(load_json):
    response = load_json('v2_place_assortment_details_response.json')
    response['products'][0]['old_price'] = 1999.0
    response['products'][1]['old_price'] = 1990.0
    response['products'][1]['price'] = 990.0
    response['products'][2]['price'] = 999.0
    return response


PARAMETRIZE_INTEGRATION_VERSION = pytest.mark.parametrize(
    'nmn_integration_version', ['v1', 'v2'],
)


@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
async def test_request_discount_category(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет, что если запрашивается категория "Скидки",
    # то возвращается только она.
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json_details_response(load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']


@experiments.discount_category()
@PARAMETRIZE_INTEGRATION_VERSION
async def test_discount_category_enabled(
        taxi_config,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет, что параметр 'discount_category_enabled' в конфиге
    # отключает возвращение категории "Скидки".

    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(),
    )

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']


@experiments.discount_category(enabled=False)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_discount_category_experiment(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']


@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
async def test_products_from_nomenclature(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет, что если ручка /v1/products сервиса номенклатур
    # не вернула некоторые из запрошенных товаров,
    # то этих товаров не будет в ответе.
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json_details_response(load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    products = {p['id'] for p in categories[0]['items']}
    assert 4 not in products
    assert 5 not in products


@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_sort_products(
        taxi_eats_products, setup_nomenclature_handlers_v2,
):
    # Тест проверяет, что товары возвращаются в отсортированном
    # порядке согласно значениям скидки и их цене.
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    setup_nomenclature_handlers_v2()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    products = [p['id'] for p in categories[0]['items']]
    assert products == [2, 1, 3]


@pytest.mark.yt(
    schemas=[
        {
            'path': '//yt/products_scoring_discount',
            'attributes': {
                'schema': [
                    {'name': 'brand_id', 'type': 'int64'},
                    {'name': 'item_id', 'type': 'string'},
                    {'name': 'score', 'type': 'double'},
                ],
            },
        },
    ],
    static_table_data=[
        {
            'path': '//yt/products_scoring_discount',
            'values': [
                {'brand_id': 1, 'item_id': 'item_id_1', 'score': 4.1},
                {'brand_id': 1, 'item_id': 'item_id_3', 'score': 5.1},
            ],
        },
    ],
)
@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
    EATS_PRODUCTS_YT_PRODUCTS_SCORING={
        'period_minutes': 20,
        'batch_size': 1000,
        'rows_limit': 1000000,
        'tables': [
            {
                'name': 'yt_table_discount',
                'yt_path': '//yt/products_scoring_discount',
            },
        ],
        'categories_tables': [],
    },
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.products_scoring(yt_table_name='yt_table_discount')
async def test_sort_products_by_scoring(
        taxi_eats_products, testpoint, setup_nomenclature_handlers_v2,
):
    # Тест проверяет, что товары возвращаются в отсортированном
    # порядке согласно заданному скорингу.

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PRODUCTS_SCORING_PERIODIC_NAME)
    periodic_finished.next_call()

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    setup_nomenclature_handlers_v2()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    products = [p['id'] for p in categories[0]['items']]
    assert products == [3, 1, 2]


@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_content(
        taxi_eats_products, load_json, setup_nomenclature_handlers_v2,
):
    # Тест проверяет полное содержимое ответа ручки.
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    expected_response = load_json('expected_response.json')
    setup_nomenclature_handlers_v2()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    response_json = response.json()
    assert len(response_json['payload']['categories']) == 1
    response_json['payload']['categories'][0]['items'].sort(
        key=lambda item: item['id'],
    )
    assert response_json['payload'] == expected_response


@pytest.mark.parametrize(
    'repeat_category_enabled, discount_category_enabled',
    [(True, True), (True, False), (False, True)],
)
@experiments.discount_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_discount_category_nomenclature_404(
        taxi_config,
        mock_retail_categories_brand_orders_history,
        repeat_category_enabled,
        discount_category_enabled,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет, когда /v1/nomenclature возвращает 404
    # то сервис тоже возвращает 404 даже если есть
    # динамические категории

    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            repeat_enabled=repeat_category_enabled,
            discount_enabled=discount_category_enabled,
        ),
    )

    mock_retail_categories_brand_orders_history.add_default_products()

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_context.set_place(place)
    mock_nomenclature_context.set_status(404)
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST,
        integration_version=nmn_integration_version,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'repeat_category_enabled, discount_category_enabled',
    [(True, True), (True, False), (False, True)],
)
@experiments.repeat_category()
@experiments.discount_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_discount_category_merge_responses(
        taxi_config,
        repeat_category_enabled,
        discount_category_enabled,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет, что категории объединяются корректно,
    # когда /v1/nomenclature возвращает 200.
    # если категории присутствуют в ответе
    # проверяется их признак активности (должен быть true)

    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            repeat_enabled=repeat_category_enabled,
            discount_enabled=discount_category_enabled,
        ),
    )

    mock_retail_categories_brand_orders_history.add_default_products()

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    place.add_root_category(root_cat_1)
    mock_nomenclature_context.set_place(place)
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST,
        integration_version=nmn_integration_version,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = {c['id']: c for c in response.json()['payload']['categories']}
    assert (utils.REPEAT_CATEGORY_ID in categories) == repeat_category_enabled
    if repeat_category_enabled:
        assert categories[utils.REPEAT_CATEGORY_ID]['available']
        assert mock_retail_categories_brand_orders_history.times_called == 1
    assert (
        utils.DISCOUNT_CATEGORY_ID in categories
    ) == discount_category_enabled
    if discount_category_enabled:
        assert categories[utils.DISCOUNT_CATEGORY_ID]['available']


@pytest.mark.parametrize(
    'minimal_stock',
    [
        pytest.param(
            21, marks=experiments.discount_category(minimal_stock=21),
        ),
        pytest.param(
            100, marks=experiments.discount_category(minimal_stock=100),
        ),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
async def test_minimal_stock(
        taxi_eats_products, mockserver, load_json, minimal_stock,
):
    # Тест проверяет, что товары у которых количество
    # стоков меньше параметра конфига minimal_stock
    # не попадают в категорию «Скидки»
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json_details_response(load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    for item in categories[0]['items']:
        if item['inStock']:
            assert item['inStock'] > minimal_stock


@pytest.mark.parametrize(
    'minimal_products, has_discount_category',
    [
        pytest.param(
            0,
            True,
            marks=experiments.discount_category(min_products=0),
            id='min 0',
        ),
        pytest.param(
            1,
            True,
            marks=experiments.discount_category(min_products=1),
            id='min 1',
        ),
        pytest.param(
            2,
            True,
            marks=experiments.discount_category(min_products=2),
            id='min 2',
        ),
        pytest.param(
            3,
            False,
            marks=experiments.discount_category(min_products=3),
            id='min 3',
        ),
        pytest.param(
            3,
            True,
            id='min 3, discounts from lib',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=3),
            ],
        ),
        pytest.param(
            4,
            False,
            marks=experiments.discount_category(min_products=4),
            id='min 4',
        ),
        pytest.param(
            4,
            True,
            id='min 4, discounts from lib',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=4),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_minimal_products_in_category(
        taxi_eats_products,
        load_json,
        experiments3,
        taxi_config,
        minimal_products,
        has_discount_category,
        mock_eats_catalog_storage,
        mock_v2_fetch_discounts_context,
        cache_add_discount_product,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
):
    # Тест проверяет, что категория «Скидки»
    # не возвращается, если количество скидочных товаров
    # меньше чем задано в параметре конфига minimal_products
    # и наоборот, если количество товаров в категории больше
    # или равно minimal_products то категория возвращается
    # А так же проверяется, что скидки из eats-discounts-applicator
    # тоже учитываются

    cache_add_discount_product('item_id_1')
    cache_add_discount_product('item_id_2')
    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            discount_enabled=True,
        ),
    )

    await taxi_eats_products.invalidate_caches()

    products_with_promo = [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    ]
    products_without_promo = [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
    ]
    for product_id in products_with_promo:
        mock_nomenclature_static_info_context.add_product(product_id)
        mock_nomenclature_dynamic_info_context.add_product(
            product_id, price=45, old_price=50,
        )
    for product_id in products_without_promo:
        mock_nomenclature_static_info_context.add_product(product_id)
        mock_nomenclature_dynamic_info_context.add_product(
            product_id, price=50,
        )
        mock_v2_fetch_discounts_context.add_discount_product(
            product_id, 'absolute', 20,
        )

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = {c['id']: c for c in response.json()['payload']['categories']}
    assert utils.DISCOUNT_CATEGORY_ID in categories
    assert (not categories[utils.DISCOUNT_CATEGORY_ID]['items']) == (
        not has_discount_category
    )


@pytest.mark.parametrize(
    'minimal_products, has_discount_category',
    [
        pytest.param(
            0,
            True,
            marks=experiments.discount_category(min_products=0),
            id='min 0',
        ),
        pytest.param(
            1,
            True,
            marks=experiments.discount_category(min_products=1),
            id='min 1',
        ),
        pytest.param(
            2,
            True,
            marks=experiments.discount_category(min_products=2),
            id='min 2',
        ),
        pytest.param(
            3,
            False,
            marks=experiments.discount_category(min_products=3),
            id='min 3',
        ),
        pytest.param(
            3,
            True,
            id='min 3, discounts from lib',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=3),
            ],
        ),
        pytest.param(
            4,
            False,
            id='min 4, discounts from lib',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=4),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@experiments.CASHBACK_DISCOUNTS_ENABLED
@PARAMETRIZE_INTEGRATION_VERSION
async def test_discount_category_minimal_products(
        load_json,
        taxi_config,
        experiments3,
        minimal_products,
        has_discount_category,
        mock_v2_fetch_discounts_context,
        cache_add_discount_product,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет, что категория «Скидки»
    # не возвращается, если количество скидочных товаров
    # меньше чем задано в параметре конфига minimal_products
    # и наоборот, если количество товаров в категории больше
    # или равно minimal_products то категория возвращается
    # А так же проверяется, что скидки из eats-discounts-applicator
    # тоже учитываются

    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            discount_enabled=True,
        ),
    )

    cache_add_discount_product('item_id_1')
    cache_add_discount_product('item_id_2')
    mock_v2_fetch_discounts_context.add_discount_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 'absolute', 20,
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
    categories = set(c['id'] for c in response.json()['payload']['categories'])
    assert (utils.DISCOUNT_CATEGORY_ID in categories) == has_discount_category


@experiments.discount_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_no_products_on_top_discount_category(
        taxi_config,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет, что категория «Скидки» не содержит
    # товары, если запрашивается корень магазина

    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            discount_enabled=True,
        ),
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
    categories = {c['id']: c for c in response.json()['payload']['categories']}
    category_id = utils.DISCOUNT_CATEGORY_ID
    assert category_id in categories
    assert not categories[category_id]['items']


def redis_categories_scoring_cache(
        *scores: Tuple[int, float],
        yt_table='yt_categories_table_v3',
        brand_id=1,
):
    """Задать кеш скоринга категорий по парам (id:score)"""
    commands = []
    for cat_id, score in scores:
        commands.append(
            [
                'hset',
                f'scores:brands:{yt_table}:{brand_id}',
                str(cat_id),
                str(score),
            ],
        )
    return pytest.mark.redis_store(*commands)


@pytest.mark.parametrize(
    'expected_response_file',
    [
        pytest.param(
            'expected_response_categorized.json',
            marks=[experiments.discounts_categorization(True)],
        ),
        pytest.param(
            'expected_response_categorized_with_top.json',
            marks=[experiments.discounts_categorization(True, 2)],
        ),
    ],
)
@experiments.categories_scoring()
@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=[
        'pg_eats_products.sql',
        'pg_add_discount_products.sql',
        'pg_add_discount_product_4.sql',
    ],
)
@redis_categories_scoring_cache((999106, 0.07), (333, 0.08))
async def test_discounts_categorization(
        taxi_eats_products,
        mockserver,
        load_json,
        expected_response_file,
        setup_nomenclature_handlers_v2,
):
    # Если включен эксперимент eats_products_discounts_categorization, то
    # надо разбить категорию Скидки на категории верхнего уровня

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    setup_nomenclature_handlers_v2(extra_product=True, extra_discount=False)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        json = load_json('v2_place_assortment_details_response.json')
        product_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'
        json['products'].append(
            utils.build_nomenclature_product(product_id, 'ghi', 990, 1000),
        )
        return json

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    response_json_payload = response.json()['payload']
    expected_response = load_json(expected_response_file)

    # Fake ids are not consistent, don't check them
    for response in (expected_response, response_json_payload):
        for category in response['categories']:
            category.pop('id')
            category.pop('uid')
    assert response_json_payload == expected_response


@pytest.mark.parametrize(
    'expected_cats_order',
    (
        pytest.param(
            ['Топ-левел категория 1', 'Топ-левел категория 3'],
            marks=[
                redis_categories_scoring_cache((999106, 0.09), (333, 0.08)),
            ],
        ),
        pytest.param(
            ['Топ-левел категория 3', 'Топ-левел категория 1'],
            marks=[
                redis_categories_scoring_cache((333, 0.09), (999106, 0.08)),
            ],
        ),
    ),
)
@experiments.discounts_categorization(True)
@experiments.categories_scoring()
@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=[
        'pg_eats_products.sql',
        'pg_add_discount_products.sql',
        'pg_add_discount_product_4.sql',
    ],
)
async def test_discounts_categorization_sort_order(
        taxi_eats_products,
        setup_nomenclature_handlers_v2,
        expected_cats_order,
):
    # Тест проверяет то что категории, на которые разбивается скидочная
    # категория, сортируются по данным из Redis
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    setup_nomenclature_handlers_v2(extra_product=True, extra_discount=False)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    response_json_payload = response.json()['payload']

    # Check categories sort order
    cats_ids = [
        str(cat['name'])
        for cat in response_json_payload['categories']
        if cat['parentId']
    ]
    assert cats_ids == expected_cats_order


@pytest.mark.parametrize(
    [
        'master_tree_sort_orders',
        'customs_sort_orders',
        'partner_categories_count',
        'sort_orders_out',
    ],
    [
        pytest.param(
            [-4, -3, -2],
            [-3, -2],
            0,
            [
                'Скидки',
                # 'Кастом 0',
                # 'Кастом 1',
                'МД 0',
                'МД 1',
                'МД 2',
            ],
            id='Мастер-дерево',
        ),
        pytest.param(
            [-2, -3, -4],
            [-2, -3],
            0,
            [
                'Скидки',
                # 'Кастом 1',
                # 'Кастом 0',
                'МД 2',
                'МД 1',
                'МД 0',
            ],
            id='Мастер-дерево, обратная сортировка',
        ),
        pytest.param(
            [],
            [-3, -2],
            3,
            [
                'Скидки',
                # 'Кастом 0',
                # 'Кастом 1',
                'Партнерская 0',
                'Партнерская 1',
                'Партнерская 2',
            ],
            marks=[
                redis_categories_scoring_cache(
                    (2, 0.09), (3, 0.08), (4, 0.07),
                ),
            ],
            id='Партнерское дерево',
        ),
        pytest.param(
            [],
            [-2, -3],
            3,
            [
                'Скидки',
                # 'Кастом 1',
                # 'Кастом 0',
                'Партнерская 2',
                'Партнерская 1',
                'Партнерская 0',
            ],
            marks=[
                redis_categories_scoring_cache(
                    (2, 0.07), (3, 0.08), (4, 0.09),
                ),
            ],
            id='Партнерское дерево, обратная сортировка',
        ),
    ],
)
@experiments.discounts_categorization(enabled=True)
@experiments.discount_category(min_products=1)
@experiments.categories_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=[
        'pg_eats_products.sql',
        'pg_add_discount_products.sql',
        'pg_add_discount_product_4.sql',
    ],
)
async def test_discounts_categorization_sort_order_master_tree(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        master_tree_sort_orders,
        customs_sort_orders,
        partner_categories_count,
        sort_orders_out,
):
    """Категории, на которые разбивается скидочная категория, сортируются по
    sort_order из номенклатуры, если в Redis нет данных (случай категорий
    мастер-дерева), а часть, для которой скоринг есть - по нему.
    Также проверяем, что кастомные категории не возвращаются."""
    products_request = PRODUCTS_BASE_REQUEST.copy()
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    parent_context = mock_nomenclature_get_parent_context

    all_categories = []
    global_categories_id = 0

    # Кастомки
    for i, sort_order in enumerate(customs_sort_orders):
        category_id = str(global_categories_id)
        parent_context.add_category(
            category_id,
            f'Кастом {category_id}',
            sort_order=sort_order,
            type_='custom_promo',
        )
        all_categories.append(category_id)
        global_categories_id += 1

    # Мастер-дерево
    for i, sort_order in enumerate(master_tree_sort_orders):
        category_id = str(global_categories_id)
        parent_context.add_category(
            category_id, f'МД {i}', sort_order=sort_order, type_='custom_base',
        )
        all_categories.append(category_id)
        global_categories_id += 1

    # Партнерские
    for i in range(partner_categories_count):
        category_id = str(global_categories_id)
        parent_context.add_category(
            category_id, f'Партнерская {i}', type_='partner',
        )
        all_categories.append(category_id)
        global_categories_id += 1

    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', name='item_1',
    )

    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        old_price=2.0,
        price=1.0,
        in_stock=20,
        parent_category_ids=all_categories,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    response_json_payload = response.json()['payload']

    # Проверить порядок сортировки категорий
    cats_ids = [
        str(cat['name']) for cat in response_json_payload['categories']
    ]
    assert cats_ids == sort_orders_out


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
async def test_discount_categories_show_in_empty(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет, что для категории "Скидки" поле show_in пустое
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json_details_response(load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    assert 'show_in' in response.json()['payload']['categories'][0]
    assert not response.json()['payload']['categories'][0]['show_in']


@pytest.mark.parametrize(
    'expected_products_ids',
    [
        # тест проверяет сортировку по популярности
        # и обрезание products до похода в номенклатуру.
        # значение количества товаров с которыми идти в
        # номенклатуру регулируется экспериментом
        pytest.param(
            {
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            },
            marks=[experiments.discounts_max_products(enabled=True)],
            id='exp on, check trim',
        ),
        pytest.param(
            {
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            },
            marks=[experiments.discounts_max_products(enabled=False)],
            id='exp off',
        ),
        pytest.param(
            {
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            },
            id='without exp',
        ),
    ],
)
@experiments.products_scoring(yt_table_name='yt_table_discount')
@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        False, True, False,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_discount_category_max_amount(
        taxi_eats_products,
        expected_products_ids,
        setup_nomenclature_handlers_v2,
):

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    setup_nomenclature_handlers_v2(expected_products_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.parametrize('handler', ['static_info', 'dynamic_info'])
@pytest.mark.parametrize(
    ['status_code', 'is_timeout'],
    [(400, False), (404, False), (429, False), (500, False), (500, True)],
)
@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_discount_category_nomenclature_bad_responses(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        status_code,
        is_timeout,
        handler,
):
    """
    Проверяется, что если /eats-nomenclature/v1/place/products/info
    или /eats-nomenclature/v1/place/products/info возвращает 404, то ручка
    тоже возвращает 404, в остальных случаях возвращается 500
    """
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    if handler == 'static_info':
        if is_timeout:
            mock_nomenclature_static_info_context.set_timeout_error(True)
        else:
            mock_nomenclature_static_info_context.set_status(
                status_code=status_code,
            )
    else:
        if is_timeout:
            mock_nomenclature_dynamic_info_context.set_timeout_error(True)
        else:
            mock_nomenclature_dynamic_info_context.set_status(
                status_code=status_code,
            )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    if status_code != 404:
        assert response.status_code == 500
    else:
        assert response.status_code == 404
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1
