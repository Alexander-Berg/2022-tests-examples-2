import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

REQUEST_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

DEFAULT_CATEGORY = '123'

PUBLIC_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
ORIGIN_ID_1 = 'item_id_1'
PUBLIC_ID_2 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'
ORIGIN_ID_2 = 'item_id_2'

BASE_REQUEST = {'slug': 'slug'}

ALL_CATEGORIES_ENABLED = utils.dynamic_categories_config(
    repeat_enabled=True,
    discount_enabled=True,
    popular_enabled=True,
    cashback_enabled=True,
)

ALL_CATEGORIES_DISABLED = utils.dynamic_categories_config(
    repeat_enabled=False,
    discount_enabled=False,
    popular_enabled=False,
    cashback_enabled=False,
)


@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
async def test_default_category(taxi_eats_products):
    # Проверяется, что если запрашивается дефолтная категория,
    # то поле category отсутствует
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = DEFAULT_CATEGORY

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_place_not_found(taxi_eats_products):
    # Проверяется, что если запрашивается неизвестный магазин,
    # то вернется 404
    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params={'category': DEFAULT_CATEGORY, 'slug': 'unknown_slug'},
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='config disabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
            ],
        ),
        pytest.param(
            id='config disabled, exp enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
                experiments.repeat_category(),
            ],
        ),
        pytest.param(
            id='config enabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED,
                ),
            ],
        ),
    ],
)
async def test_repeat_category_disabled(taxi_eats_products):
    # Тест проверяет, что если запрашивается категория "Вы заказывали",
    # но она выключена, то товаров в ней не вернется
    category_id = str(utils.REPEAT_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    category = response.json()['category']
    assert category['id'] == category_id
    assert category['product_ids'] == []


@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
@experiments.repeat_category()
async def test_repeat_category(
        taxi_eats_products,
        add_place_products_mapping,
        mock_retail_categories_brand_orders_history,
):
    # Проверяется, что если запрашивается категория "Вы заказывали",
    # то она возвращается с товарами
    mapping = [
        conftest.ProductMapping(
            origin_id=ORIGIN_ID_1, core_id=1, public_id=PUBLIC_ID_1,
        ),
        conftest.ProductMapping(
            origin_id=ORIGIN_ID_2, core_id=2, public_id=PUBLIC_ID_2,
        ),
    ]
    add_place_products_mapping(mapping)
    category_id = str(utils.REPEAT_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_ID_1, 2,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_ID_2, 5,
    )

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200

    assert mock_retail_categories_brand_orders_history.times_called == 1

    category = response.json()['category']
    assert category['id'] == category_id
    category['product_ids'].sort()
    assert category['product_ids'] == [PUBLIC_ID_1, PUBLIC_ID_2]


@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
@experiments.repeat_category()
async def test_repeat_category_bad_response(
        taxi_eats_products, mock_retail_categories_brand_orders_history,
):
    # Проверяется, что если запрашивается категория "Вы заказывали",
    # но сервис истории не ответил, то мы возвращаем 0 товаров

    mock_retail_categories_brand_orders_history.set_timeout_error(True)

    category_id = str(utils.REPEAT_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    assert mock_retail_categories_brand_orders_history.times_called == 1

    category = response.json()['category']
    assert category['id'] == category_id
    assert category['product_ids'] == []


@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='config disabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
            ],
        ),
        pytest.param(
            id='config disabled, exp enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
                experiments.discount_category(),
            ],
        ),
        pytest.param(
            id='config enabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED,
                ),
            ],
        ),
    ],
)
async def test_discount_category_disabled(
        taxi_eats_products,
        add_place_products_mapping,
        cache_add_discount_product,
):
    # Тест проверяет, что если запрашивается категория "Вы заказывали",
    # но она выключена, то товаров в ней не вернется
    cache_add_discount_product(ORIGIN_ID_1)
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id=ORIGIN_ID_1, public_id=PUBLIC_ID_1,
            ),
        ],
    )
    category_id = str(utils.DISCOUNT_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    category = response.json()['category']
    assert category['id'] == category_id
    assert category['product_ids'] == []


@pytest.mark.parametrize(
    'has_products',
    [
        pytest.param(
            True, marks=[experiments.discount_category(min_products=0)],
        ),
        pytest.param(
            True, marks=[experiments.discount_category(min_products=1)],
        ),
        pytest.param(
            True, marks=[experiments.discount_category(min_products=2)],
        ),
        pytest.param(
            False, marks=[experiments.discount_category(min_products=3)],
        ),
        pytest.param(
            False, marks=[experiments.discount_category(min_products=100)],
        ),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
async def test_discount_category(
        taxi_eats_products,
        add_place_products_mapping,
        cache_add_discount_product,
        has_products,
):
    # Проверяется, что если запрашивается категория "Скидки",
    # то возвращаются скидочные товары из кэша только если их больше,
    # чем minimal_products в эксперименте
    mapping = [
        conftest.ProductMapping(origin_id=ORIGIN_ID_1, public_id=PUBLIC_ID_1),
        conftest.ProductMapping(origin_id=ORIGIN_ID_2, public_id=PUBLIC_ID_2),
    ]
    add_place_products_mapping(mapping)
    cache_add_discount_product(ORIGIN_ID_1)
    cache_add_discount_product(ORIGIN_ID_2)
    cache_add_discount_product('item_id_3')
    category_id = str(utils.DISCOUNT_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200

    category = response.json()['category']
    assert category['id'] == category_id
    category['product_ids'].sort()
    expected_products = []
    if has_products:
        expected_products = [PUBLIC_ID_1, PUBLIC_ID_2]
    assert category['product_ids'] == expected_products


@pytest.mark.parametrize(
    'with_applicator',
    [
        pytest.param(False, id='applicator disabled'),
        pytest.param(
            True,
            id='applicator enabled',
            marks=experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
        ),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
@experiments.discount_category()
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_discount_category_with_applicator(
        taxi_eats_products,
        add_place_products_mapping,
        cache_add_discount_product,
        mock_v2_fetch_discounts_context,
        with_applicator,
):
    # Проверяется, что если запрашивается категория "Скидки",
    # то возвращается ответ с учетом скидок из eats-discounts
    mapping = [
        conftest.ProductMapping(ORIGIN_ID_1, public_id=PUBLIC_ID_1),
        conftest.ProductMapping(ORIGIN_ID_2, public_id=PUBLIC_ID_2),
    ]
    add_place_products_mapping(mapping)

    cache_add_discount_product(ORIGIN_ID_1)

    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_ID_1, 'absolute', 10,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_ID_2, 'absolute', 15,
    )

    category_id = str(utils.DISCOUNT_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200

    assert (
        mock_v2_fetch_discounts_context.handler.times_called == with_applicator
    )

    category = response.json()['category']
    assert category['id'] == category_id
    expected_ids = [PUBLIC_ID_1]
    if with_applicator:
        expected_ids.append(PUBLIC_ID_2)
    category['product_ids'].sort()
    assert category['product_ids'] == expected_ids


async def test_cashback_category_no_config(taxi_eats_products):
    # Тест проверяет, что если запрашивается категория "Кешбек",
    # но ее нет в конфиге, то поле category не возвращается
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = str(utils.CASHBACK_CATEGORY_ID)

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='config disabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
            ],
        ),
        pytest.param(
            id='config disabled, exp enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
            ],
        ),
        pytest.param(
            id='config enabled, not all exps enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED,
                ),
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
            ],
        ),
        pytest.param(
            id='config enabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED,
                ),
            ],
        ),
    ],
)
async def test_cashback_category_disabled(taxi_eats_products):
    # Тест проверяет, что если запрашивается категория "Кешбек",
    # но она выключена, то товаров в ней не вернется
    category_id = str(utils.CASHBACK_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    category = response.json()['category']
    assert category['id'] == category_id
    assert category['product_ids'] == []


@pytest.mark.parametrize(
    'has_products',
    [
        pytest.param(True, marks=[experiments.cashback_category_enabled(1)]),
        pytest.param(True, marks=[experiments.cashback_category_enabled(2)]),
        pytest.param(False, marks=[experiments.cashback_category_enabled(3)]),
        pytest.param(
            False, marks=[experiments.cashback_category_enabled(100)],
        ),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
async def test_cashback_category(
        taxi_eats_products, mock_v2_fetch_discounts_context, has_products,
):
    # Проверяется, что если запрашивается категория "Кешбек",
    # то возвращаются товары с кешбеком из eats-discounts
    # с учетом min_products из эксперимента
    product_ids = [PUBLIC_ID_1, PUBLIC_ID_2]

    for product_id in product_ids:
        mock_v2_fetch_discounts_context.add_cashback_product(
            product_id, 'absolute', 10,
        )

    category_id = str(utils.CASHBACK_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200

    assert mock_v2_fetch_discounts_context.handler.times_called == 1

    category = response.json()['category']
    assert category['id'] == category_id
    expected_ids = []
    if has_products:
        expected_ids = product_ids

    category['product_ids'].sort()
    assert category['product_ids'] == expected_ids


@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='config disabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
            ],
        ),
        pytest.param(
            id='config disabled, exp enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_DISABLED,
                ),
                experiments.popular_category(),
            ],
        ),
        pytest.param(
            id='config enabled, exp disabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED,
                ),
            ],
        ),
    ],
)
@experiments.products_scoring()
@pytest.mark.redis_store(file='redis_popular_products_cache')
async def test_popular_category_disabled(
        taxi_eats_products, add_place_products_mapping,
):
    # Тест проверяет, что если запрашивается категория "Популярное",
    # но она выключена, то товаров в ней не вернется
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id=ORIGIN_ID_1, public_id=PUBLIC_ID_1,
            ),
        ],
    )
    category_id = str(utils.POPULAR_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    category = response.json()['category']
    assert category['id'] == category_id
    assert category['product_ids'] == []


@pytest.mark.parametrize(
    'has_products',
    [
        pytest.param(
            True,
            marks=pytest.mark.redis_store(file='redis_popular_products_cache'),
        ),
        pytest.param(False),
    ],
)
@experiments.products_scoring()
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
@experiments.popular_category()
async def test_popular_category(
        taxi_eats_products, add_place_products_mapping, has_products,
):
    # Проверяется, что если запрашивается категория "Популярное",
    # то возвращаются популярные товары
    mapping = [
        conftest.ProductMapping(ORIGIN_ID_1, public_id=PUBLIC_ID_1),
        conftest.ProductMapping(ORIGIN_ID_2, public_id=PUBLIC_ID_2),
    ]
    add_place_products_mapping(mapping)
    category_id = str(utils.POPULAR_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200

    category = response.json()['category']
    assert category['id'] == category_id
    expected_ids = []
    if has_products:
        expected_ids = [PUBLIC_ID_1, PUBLIC_ID_2]

    category['product_ids'].sort()
    assert category['product_ids'] == expected_ids


@pytest.mark.parametrize(
    'has_products',
    [
        pytest.param(
            True, marks=[experiments.popular_category(min_products=1)],
        ),
        pytest.param(
            True, marks=[experiments.popular_category(min_products=2)],
        ),
        pytest.param(
            False, marks=[experiments.popular_category(min_products=3)],
        ),
        pytest.param(
            False, marks=[experiments.popular_category(min_products=100)],
        ),
    ],
)
@experiments.products_scoring()
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=ALL_CATEGORIES_ENABLED)
@pytest.mark.redis_store(file='redis_popular_products_cache')
async def test_popular_category_min_products(
        taxi_eats_products, add_place_products_mapping, has_products,
):
    # Проверяется, что если запрашивается категория "Популярное",
    # то возвращаются популярные товары только если их больше,
    # чем minimal_products в эксперименте
    mapping = [
        conftest.ProductMapping(ORIGIN_ID_1, public_id=PUBLIC_ID_1),
        conftest.ProductMapping(ORIGIN_ID_2, public_id=PUBLIC_ID_2),
    ]
    add_place_products_mapping(mapping)
    category_id = str(utils.POPULAR_CATEGORY_ID)
    products_request = copy.deepcopy(BASE_REQUEST)
    products_request['category'] = category_id

    response = await taxi_eats_products.get(
        utils.Handlers.FOR_SEARCH_CATEGORIES_V2,
        params=products_request,
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200

    category = response.json()['category']
    assert category['id'] == category_id
    expected_ids = []
    if has_products:
        expected_ids = [PUBLIC_ID_1, PUBLIC_ID_2]

    category['product_ids'].sort()
    assert category['product_ids'] == expected_ids
