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

PRODUCTS_HEADERS_PARTNER = {
    'X-Eats-User': 'partner_user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

PRODUCTS_BASE_REQUEST = {'slug': 'slug'}

CONFIG_NO_CATEGORIES = pytest.mark.config(
    EATS_PRODUCT_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(),
)

CONFIG_NO_CASHBACK = {
    'popular': {
        'enabled': True,
        'id': utils.POPULAR_CATEGORY_ID,
        'name': 'Популярное',
    },
    'discount': {
        'enabled': True,
        'id': utils.DISCOUNT_CATEGORY_ID,
        'name': 'Скидки',
    },
    'repeat': {
        'enabled': True,
        'id': utils.REPEAT_CATEGORY_ID,
        'name': 'Вы уже заказывали',
    },
}


@pytest.mark.parametrize(
    [],
    [
        pytest.param(id='has config'),
        pytest.param(
            id='no categories in config',
            marks=[
                experiments.discount_category(),
                pytest.mark.disable_config_check,
                CONFIG_NO_CATEGORIES,
            ],
        ),
    ],
)
async def test_discount_category_no_exp_config(taxi_eats_products):
    # Тест проверяет, что если запрашивается категория "Скидки",
    # но нет эксперимента
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert not categories[0]['items']


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.discount_category()
async def test_discount_category_nomenclature_500(
        taxi_eats_products, mockserver,
):
    # Тест проверяет, что если номенклатура вернула 500,
    # то ручка тоже 500 отдает
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        raise mockserver.NetworkError()

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'nomenclature_response',
    [
        pytest.param({}, id='empty_response'),
        pytest.param({'categories': []}, id='empty_categories'),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.discount_category()
async def test_discount_category_nomenclature_bad(
        taxi_eats_products, mockserver, nomenclature_response,
):
    # Тест проверяет, что в случае неверного ответа номенклатуры
    # возвращается 0 товаров в категории
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return nomenclature_response

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert not categories[0]['items']


@experiments.discount_category()
async def test_discount_category(taxi_eats_products, mockserver, load_json):
    # Тест проверяет, что если запрашивается категория "Скидки",
    # то возвращается только она.

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return load_json('nomenclature_v1_products.json')

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']


@experiments.discount_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_discount_category_content(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет полное содержимое ответа ручки.

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return load_json('nomenclature_v1_products.json')

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    response_json = response.json()
    categories = response_json['categories']
    assert len(categories) == 1
    categories[0]['items'].sort(key=lambda item: item['core_id'])
    assert response_json == load_json(
        'discount_category_expected_response.json',
    )


@pytest.mark.parametrize(
    ['has_category', 'has_lib_discounts', 'min_products'],
    [
        pytest.param(
            True,
            False,
            1,
            marks=experiments.discount_category(min_products=1),
            id='has category, 2/1',
        ),
        pytest.param(
            True,
            False,
            2,
            marks=experiments.discount_category(min_products=2),
            id='has category, 2/2',
        ),
        pytest.param(
            False,
            False,
            3,
            marks=experiments.discount_category(min_products=3),
            id='no category, 2/3',
        ),
        pytest.param(
            False,
            False,
            3,
            id='no category with discounts from lib, 2/3',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=3),
            ],
        ),
        pytest.param(
            True,
            True,
            3,
            id='has category with discounts from lib, 3/3',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=3),
            ],
        ),
        pytest.param(
            False,
            True,
            4,
            id='no category with discounts from lib, 3/4',
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
async def test_discount_category_minimal_products(
        taxi_eats_products,
        mockserver,
        load_json,
        experiments3,
        min_products,
        has_category,
        has_lib_discounts,
        mock_v2_fetch_discounts_context,
        cache_add_discount_product,
):
    # Тест проверяет, что категория "Скидки"
    # возвращается пустой, если количество скидочных товаров
    # меньше чем задано в параметре конфига minimal_products
    # и наоборот, если количество товаров в категории больше
    # или равно minimal_products то категория возвращается полностью

    cache_add_discount_product('item_id_1')
    cache_add_discount_product('item_id_2')

    if has_lib_discounts:
        mock_v2_fetch_discounts_context.add_discount_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 'absolute', 10,
        )

    await taxi_eats_products.invalidate_caches()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        resp = load_json('nomenclature_v1_products.json')
        items = resp['categories'][0]['items']
        result_items = []
        for item in items:
            if item['id'] in request.json['products']:
                result_items.append(item)
        return {
            'categories': [
                {
                    'available': True,
                    'id': '',
                    'images': [],
                    'items': result_items,
                    'name': '',
                    'public_id': 0,
                    'sort_order': 0,
                },
            ],
        }

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert (not categories[0]['items']) == (not has_category)


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
async def test_discount_category_removed_items(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_v2_fetch_discounts_context,
):
    # Тест проверяет, что если некоторые товары из номенклатуры
    # пришли без скидки, то возвращены не будут, за исключением
    # товаров, для которых есть скидка из либы

    mock_v2_fetch_discounts_context.add_discount_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 'absolute', 10,
    )

    await taxi_eats_products.invalidate_caches()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        resp = load_json('nomenclature_v1_products.json')
        items = resp['categories'][0]['items']
        items[0]['old_price'] = None
        items[2]['old_price'] = None
        return resp

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert len(categories[0]['items']) == 2


@experiments.discount_category(enabled=False)
async def test_discount_category_experiments_off(taxi_eats_products):
    # Тест проверяет, что категория "Скидки" возвращается пустой,
    # если выключен эксперимент.

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    assert not categories[0]['items']


@experiments.repeat_category()
async def test_repeat_category(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если запрашивается категория "Повторим",
    # то возвращается только она.

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return load_json('nomenclature_v1_products.json')

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    assert mock_retail_categories_brand_orders_history.times_called == 1


@pytest.mark.parametrize(
    'products_headers', [PRODUCTS_HEADERS, PRODUCTS_HEADERS_PARTNER],
)
@experiments.repeat_category()
async def test_repeat_category_content(
        taxi_eats_products,
        mockserver,
        load_json,
        products_headers,
        add_place_products_mapping,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет полное содержимое ответа ручки.
    mapping = []
    for i in range(4):
        origin_id = 'item_id_' + str(i)
        mapping.append(
            conftest.ProductMapping(
                origin_id,
                core_id=i,
                public_id=f'bb231b95-1ff2-4bc4-b78d-dcaa1f69b00{i}',
            ),
        )
    add_place_products_mapping(mapping)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return load_json('nomenclature_v1_products.json')

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=products_headers,
    )
    response_json = response.json()
    categories = response_json['categories']
    assert len(categories) == 1
    categories[0]['items'].sort(key=lambda item: item['core_id'])
    assert response_json == load_json('repeat_category_expected_response.json')
    assert mock_retail_categories_brand_orders_history.times_called == 1


@experiments.repeat_category('disabled')
async def test_repeat_category_experiments_off(taxi_eats_products):
    # Тест проверяет, что категория "Повторим" возвращается пустой,
    # если выключен эксперимент.

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    assert not categories[0]['items']


@experiments.repeat_category()
@pytest.mark.parametrize('products_response', [{}, {'categories': []}])
async def test_repeat_category_no_nomenclature_products(
        taxi_eats_products,
        mockserver,
        products_response,
        add_place_products_mapping,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если ручка номеклатуры /v1/products
    # вернула пустой ответ, то сервис возвращает пустой ответ
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1',
                core_id=1,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            ),
        ],
    )

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return products_response

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    categories = response.json()['categories']
    assert not categories
    assert mock_retail_categories_brand_orders_history.times_called == 1


# Пришлось вынести наружу из-за ограничения длины строки
TEST_DYNAMIC_CATEGORIES_MARKS = [
    experiments.CASHBACK_CATEGORY_ENABLED,
    pytest.mark.disable_config_check,
    pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=CONFIG_NO_CASHBACK),
]


@pytest.mark.parametrize(
    'has_cashback',
    [
        pytest.param(
            True,
            id='with cashback',
            marks=[experiments.CASHBACK_CATEGORY_ENABLED],
        ),
        pytest.param(
            False,
            id='without cashback',
            marks=[experiments.cashback_category_enabled(10)],
        ),
        pytest.param(
            False,
            id='without cashback config',
            marks=TEST_DYNAMIC_CATEGORIES_MARKS,
        ),
    ],
)
@experiments.repeat_category()
@experiments.discount_category()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_dynamic_categories(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_v2_fetch_discounts_context,
        has_cashback,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что при запросе без идентификатора категории
    # возвращаются все возможные: "Скидки" и "Повторим".

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return load_json('nomenclature_v1_products.json')

    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 'absolute', 10,
    )

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    response_json = response.json()
    categories = response_json['categories']

    categories.sort(key=lambda item: item['id'])
    categories_len = 2
    if has_cashback:
        categories_len = 3
        # casbhack category (id=1000000)
        assert categories[2]['id'] == utils.CASHBACK_CATEGORY_ID
    assert len(categories) == categories_len
    # repeat category (id=44004)
    assert categories[0]['id'] == utils.REPEAT_CATEGORY_ID
    # discounts category (id=44008)
    assert categories[1]['id'] == utils.DISCOUNT_CATEGORY_ID
    for category in categories:
        assert not category['items']
    assert mock_retail_categories_brand_orders_history.times_called == 1


@pytest.mark.parametrize('has_discount', [True, False])
@pytest.mark.parametrize('has_cashback', [True, False])
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.discount_category()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
async def test_cashback_and_discount_categories(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        has_cashback,
        has_discount,
):
    # Проверяем категории Скидки и Кешбек, если включены только они
    product_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        return load_json('nomenclature_v1_products.json')

    mock_nomenclature_v2_details_context.add_product(
        product_id, price=50, promo_price=45,
    )

    if has_discount:
        mock_v2_fetch_discounts_context.add_discount_product(
            product_id, 'absolute', 10,
        )
    if has_cashback:
        mock_v2_fetch_discounts_context.add_cashback_product(
            product_id, 'absolute', 10,
        )

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    response_json = response.json()
    categories = response_json['categories']

    assert len(categories) == int(has_discount) + int(has_cashback)
    assert (
        category['id'] == utils.DISCOUNT_CATEGORY_ID
        for category in categories
        if has_discount
    )
    assert (
        category['id'] == utils.CASHBACK_CATEGORY_ID
        for category in categories
        if has_cashback
    )
    for category in categories:
        assert not category['items']


@pytest.mark.parametrize(
    ['has_category', 'has_lib_discounts', 'min_products'],
    [
        pytest.param(
            True,
            False,
            1,
            marks=experiments.discount_category(min_products=1),
            id='has category, 2/1',
        ),
        pytest.param(
            True,
            False,
            2,
            marks=experiments.discount_category(min_products=2),
            id='has category, 2/2',
        ),
        pytest.param(
            False,
            False,
            3,
            marks=experiments.discount_category(min_products=3),
            id='no category, 2/3',
        ),
        pytest.param(
            False,
            False,
            3,
            id='no category with discounts from lib, 2/3',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=3),
            ],
        ),
        pytest.param(
            True,
            True,
            3,
            id='has category with discounts from lib, 3/3',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=3),
            ],
        ),
        pytest.param(
            False,
            True,
            4,
            id='no category with discounts from lib, 3/4',
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(min_products=4),
            ],
        ),
    ],
)
@experiments.repeat_category('disabled')
@experiments.CASHBACK_CATEGORY_DISABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
async def test_has_discounts_category(
        taxi_eats_products,
        load_json,
        mock_v2_fetch_discounts_context,
        cache_add_discount_product,
        experiments3,
        has_category,
        has_lib_discounts,
        min_products,
):
    # Тест проверяет, что при запросе без идентификатора категории
    # возвращается категория Скидки с учетом скидок
    # из либы eats-discounts-applicator

    cache_add_discount_product('item_id_1')
    cache_add_discount_product('item_id_2')

    if has_lib_discounts:
        mock_v2_fetch_discounts_context.add_discount_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 'absolute', 10,
        )

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    response_json = response.json()
    categories = response_json['categories']
    if has_category:
        assert len(categories) == 1
        assert categories[0]['id'] == utils.DISCOUNT_CATEGORY_ID
    else:
        assert not categories


@experiments.discount_category(enabled=False)
@experiments.repeat_category('disabled')
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_DISABLED
async def test_dynamic_categories_experiments_off(taxi_eats_products):
    # Тест проверяет, что возвращается пустой ответ,
    # если все категории выключены.

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert not categories


async def test_place_not_found(taxi_eats_products):
    # Тест проверяет ответ на неизвестный slug.

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params={'slug': 'unknown_slug'},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'max_batch_size, expected_call_times',
    [(1, 6), (2, 3), (4, 2), (3, 2), (6, 1), (10, 1), (100, 1)],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.discount_category()
async def test_for_search_place_discount_category_with_batch_request(
        taxi_eats_products,
        taxi_config,
        mockserver,
        max_batch_size,
        expected_call_times,
        load_json,
):
    settings = {'max_batch_size': max_batch_size}
    taxi_config.set(EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=settings)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        nom_response = load_json('nomenclature_v1_products.json')
        ids = request.json['products']
        nom_response['categories'][0]['items'] = [
            i for i in nom_response['categories'][0]['items'] if i['id'] in ids
        ]

        return nom_response

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )

    data = response.json()
    data['categories'][0]['items'].sort(key=lambda i: i['core_id'])
    load_data = load_json('discount_category_expected_response.json')

    assert _mock_eats_nomenclature_products.times_called == expected_call_times
    assert response.status_code == 200
    assert data == load_data


@experiments.discount_category()
async def test_unknown_category(taxi_eats_products, mockserver, load_json):
    # Если запрашивается не динамическая категория, то возвращается 404
    unknown_category = 100500
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = unknown_category
    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'has_category',
    [
        pytest.param(
            True,
            id='has category, enough products',
            marks=[experiments.cashback_category_enabled(2)],
        ),
        pytest.param(
            False,
            id='has category, not enough products',
            marks=[experiments.cashback_category_enabled(3)],
        ),
        pytest.param(
            False,
            id='category disabled',
            marks=[experiments.CASHBACK_CATEGORY_DISABLED],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.discount_category()
async def test_cashback_category(
        taxi_eats_products,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        has_category,
):
    product_ids = [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    ]
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.CASHBACK_CATEGORY_ID

    for product_id in product_ids:
        mock_nomenclature_v2_details_context.add_product(
            id_=product_id, price=100, promo_price=90,
        )

        mock_v2_fetch_discounts_context.add_cashback_product(
            product_id, 'absolute', 10,
        )

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    items = categories[0]['items']
    if has_category:
        assert len(items) == len(product_ids)
        for item in items:
            assert item['nomenclature_id'] in product_ids
    else:
        assert not items


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
async def test_cashback_category_no_cashbacks(
        taxi_eats_products,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
):
    product_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.CASHBACK_CATEGORY_ID

    mock_nomenclature_v2_details_context.add_product(
        id_=product_id, price=100, promo_price=90,
    )

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    assert not categories[0]['items']


@pytest.mark.parametrize(
    'category_id', [utils.DISCOUNT_CATEGORY_ID, utils.REPEAT_CATEGORY_ID],
)
@experiments.discount_category()
@experiments.repeat_category()
async def test_place_products_invalid_mapping(
        taxi_eats_products,
        mockserver,
        load_json,
        add_place_products_mapping,
        category_id,
        cache_add_discount_product,
        mock_retail_categories_brand_orders_history,
):
    origin_1 = 'item_id_1'
    origin_2 = 'item_id_2'
    cache_add_discount_product(origin_1)
    cache_add_discount_product(origin_2)
    core_id = 2
    mapping = [
        conftest.ProductMapping(
            origin_id=origin_1,
            core_id=None,
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        ),
        conftest.ProductMapping(
            origin_id=origin_2,
            core_id=core_id,
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        ),
    ]
    add_place_products_mapping(mapping)

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS)
    def _mock_eats_nomenclature_products(request):
        nom_response = load_json('nomenclature_v1_products.json')
        ids = request.json['products']
        nom_response['categories'][0]['items'] = [
            i for i in nom_response['categories'][0]['items'] if i['id'] in ids
        ]

        return nom_response

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = category_id
    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200

    assert _mock_eats_nomenclature_products.times_called == 1

    if category_id == utils.REPEAT_CATEGORY_ID:
        assert mock_retail_categories_brand_orders_history.times_called == 1

    items = response.json()['categories'][0]['items']
    assert len(items) == 1
    assert items[0]['core_id'] == core_id


async def test_for_search_without_slug(taxi_eats_products):
    """
    Тест проверяет ответ на запрос без slug.
    """
    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES,
        params={},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 400
