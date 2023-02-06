import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}


def init_categories(mock_v1_nomenclature_context):
    apple = conftest.NomenclatureProduct(
        public_id='apple', price=100, nom_id='item_id_1',
    )
    orange = conftest.NomenclatureProduct(
        public_id='orange', price=100, promo_price=90, nom_id='item_id_2',
    )
    not_available = conftest.NomenclatureProduct(
        public_id='not_available',
        price=100,
        promo_price=90,
        nom_id='item_id_3',
        is_available=False,
    )
    # для тестирования с request_first_leaf_early=true и has_discounts=true
    fruits = conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1)
    fruits.add_product(apple)
    fruits.add_product(orange)
    fruits.add_product(not_available)
    mock_v1_nomenclature_context.add_category(fruits)

    # для тестирования с request_first_leaf_early=false и has_discounts=null
    potato = conftest.NomenclatureProduct(
        public_id='potato', price=100, promo_price=80,
    )
    vegetables = conftest.NomenclatureCategory('category_id_2', 'Овощи', 2)
    vegetables.add_product(potato)
    mock_v1_nomenclature_context.add_category(vegetables)

    # для тестирования с request_first_leaf_early=true и has_discounts=null
    milk = conftest.NomenclatureCategory('category_id_3', 'Молочное', 3)
    mock_v1_nomenclature_context.add_category(milk)

    # для тестирования с request_first_leaf_early=true и has_discounts=false
    meat = conftest.NomenclatureCategory('category_id_4', 'Мясное', 4)
    mock_v1_nomenclature_context.add_category(meat)


@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'products_count_expiry_seconds': 2000},
)
async def test_products_count_in_category_save_to_redis(
        redis_store, stq_runner, mock_v1_nomenclature_context,
):
    init_categories(mock_v1_nomenclature_context)
    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    items_in_category = {b'1': b'2', b'2': b'1', b'3': b'0', b'4': b'0'}
    redis_key = 'products:count:1'
    assert redis_store.exists(redis_key)
    assert redis_store.ttl(redis_key) > 0
    assert redis_store.hgetall(redis_key) == items_in_category


@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'products_count_expiry_seconds': 2000},
)
async def test_discounts_products_count_in_category_save_to_redis(
        redis_store, stq_runner, mock_v1_nomenclature_context,
):
    init_categories(mock_v1_nomenclature_context)
    await stq_runner.eats_products_update_discount_products.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    items_in_category = {b'1': b'1', b'2': b'1', b'3': b'0', b'4': b'0'}
    redis_key = 'products:discounts:count:1'
    assert redis_store.exists(redis_key)
    assert redis_store.ttl(redis_key) > 0
    assert redis_store.hgetall(redis_key) == items_in_category


@experiments.REQUEST_FIRST_LEAF_EXP
@pytest.mark.redis_store(file='count_cache')
async def test_menu_goods_extra_flags(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    init_categories(mock_v1_nomenclature_context)
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert categories

    # достаточно продуктов, есть данные о скидочных
    assert categories[0]['id'] == 1
    assert categories[0]['request_first_leaf_early'] is True
    assert categories[0]['has_discounts'] is True

    # недостаточно продуктов
    assert categories[1]['id'] == 2
    assert categories[1]['request_first_leaf_early'] is False
    assert 'has_discounts' not in categories[1]

    # достаточно продуктов, нет данных о скидочных
    assert categories[2]['id'] == 3
    assert categories[2]['request_first_leaf_early'] is True
    assert 'has_discounts' not in categories[2]

    # достаточно продуктов, скидочных 0
    assert categories[3]['id'] == 4
    assert categories[3]['request_first_leaf_early'] is True
    assert categories[3]['has_discounts'] is False


@pytest.mark.parametrize(
    (),
    [
        pytest.param(
            id='experiment disabled',
            marks=[experiments.REQUEST_FIRST_LEAF_EXP_OFF],
        ),
        pytest.param(id='experiment not found'),
    ],
)
@pytest.mark.redis_store(file='count_cache')
async def test_menu_goods_extra_flags_experiment_off(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    init_categories(mock_v1_nomenclature_context)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert categories
    count = len(categories)
    assert count == 4
    for i in range(count):
        assert categories[i]['id'] == i + 1
        assert 'request_first_leaf_early' not in categories[i]
        assert 'has_discounts' not in categories[i]


@experiments.REQUEST_FIRST_LEAF_EXP
@pytest.mark.redis_store(file='count_cache')
async def test_menu_goods_extra_flags_category_id(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    init_categories(mock_v1_nomenclature_context)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert categories[0]['id'] == 1
    assert 'request_first_leaf_early' not in categories[0]
    assert 'has_discounts' not in categories[0]


@experiments.REQUEST_FIRST_LEAF_EXP
@pytest.mark.redis_store(file='count_cache_wrong_data')
async def test_menu_goods_extra_flags_wrong_cache(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    init_categories(mock_v1_nomenclature_context)
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert categories

    # есть данные о количестве продуктов, ошибка при чтении скидочных
    assert categories[0]['id'] == 1
    assert categories[0]['request_first_leaf_early'] is True
    assert 'has_discounts' not in categories[1]

    # ошибка при чтении количества продуктов
    assert categories[1]['id'] == 2
    assert categories[1]['request_first_leaf_early'] is False
    assert 'has_discounts' not in categories[1]

    # нет данных о количестве продуктов
    assert categories[2]['id'] == 3
    assert categories[2]['request_first_leaf_early'] is False
    assert 'has_discounts' not in categories[2]


@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.REQUEST_FIRST_LEAF_EXP
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.redis_store(file='count_cache')
@pytest.mark.parametrize(
    'has_discounts',
    [
        pytest.param(
            True,
            id='discounts category enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
                        utils.dynamic_categories_config(
                            discount_enabled=True, cashback_enabled=True,
                        )
                    ),
                ),
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.discount_category(),
                experiments.CASHBACK_CATEGORY_ENABLED,
            ],
        ),
        pytest.param(
            True,
            id='discounts category disabled',
            marks=[experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED],
        ),
        pytest.param(
            False,
            id='cashback category enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
                        utils.dynamic_categories_config(cashback_enabled=True)
                    ),
                ),
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_CATEGORY_ENABLED,
            ],
        ),
        pytest.param(
            False,
            id='cashback enabled, both categories enabled',
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
                        utils.dynamic_categories_config(
                            discount_enabled=True, cashback_enabled=True,
                        )
                    ),
                ),
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.discount_category(),
                experiments.CASHBACK_CATEGORY_ENABLED,
            ],
        ),
    ],
)
async def test_menu_goods_extra_flags_discounts_applicator(
        taxi_eats_products,
        mockserver,
        mock_v1_nomenclature_context,
        mock_v2_fetch_discounts_context,
        has_discounts,
):
    init_categories(mock_v1_nomenclature_context)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_v2_details(request):
        return {
            'categories': [{'name': 'category 4', 'public_id': '4'}],
            'products': [],
        }

    mock_v2_fetch_discounts_context.add_discount_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', 'absolute', 3.0,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )

    assert mock_v1_nomenclature_context.handler.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1

    assert response.status_code == 200
    categories = {
        category['id']: category
        for category in response.json()['payload']['categories']
    }

    # достаточно продуктов, нет данных о скидочных в кэше, нет скидочных
    # в applicator
    assert 3 in categories
    assert categories[3]['request_first_leaf_early'] is True
    assert 'has_discounts' not in categories[3]
    # достаточно продуктов для request_first_leaf_early, скидочных в кэше 0
    # есть скидочные в applicator
    assert 4 in categories
    assert categories[4]['request_first_leaf_early'] is True
    assert categories[4]['has_discounts'] == has_discounts


@pytest.mark.parametrize(
    (),
    [
        pytest.param(id='no mapping'),
        pytest.param(
            id='has mapping',
            marks=[
                pytest.mark.pgsql(
                    'eats_products',
                    files=['pg_eats_products.sql', 'add_mapping.sql'],
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'nomenclature_error',
    [pytest.param(None), pytest.param('404'), pytest.param('500')],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.REQUEST_FIRST_LEAF_EXP
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@pytest.mark.redis_store(file='count_cache')
async def test_menu_goods_extra_flags_wrong_data(
        taxi_eats_products,
        mockserver,
        mock_v1_nomenclature_context,
        mock_v2_fetch_discounts_context,
        nomenclature_error,
):
    init_categories(mock_v1_nomenclature_context)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_v2_details(request):
        if nomenclature_error == '404':
            return mockserver.make_response('bad request', status=404)
        if nomenclature_error == '500':
            raise mockserver.NetworkError()
        return {'categories': [], 'products': []}

    mock_v2_fetch_discounts_context.add_discount_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', 'absolute', 3.0,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )

    assert mock_v1_nomenclature_context.handler.times_called == 1
    assert mock_v2_fetch_discounts_context.handler.times_called == 1

    assert response.status_code == 200
    categories = {
        category['id']: category
        for category in response.json()['payload']['categories']
    }

    # достаточно продуктов для request_first_leaf_early, скидочных в кэше 0
    # есть скидочные в applicator
    assert 4 in categories
    assert categories[4]['request_first_leaf_early'] is True
    assert categories[4]['has_discounts'] is False
