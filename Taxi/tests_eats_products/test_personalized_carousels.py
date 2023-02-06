# pylint: disable=too-many-lines
# Проверка отключена по причине того, что линтер не находит библиотеку
# pylint: disable=import-error
from eats_bigb import eats_bigb
import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PASSPORT_UID = '1'
CATEGORY_ID = '1001'
CHILD_ID = '1002'
THIRD_CATEGORY_ID = '1003'
FOURTH_CATEGORY_ID = '1004'
FIFTH_CATEGORY_ID = '1005'

GET_CATEGORIES_REQUEST = {
    'slug': 'slug',
    'categories': [
        {'uid': CATEGORY_ID, 'min_items_count': 1, 'max_items_count': 4},
    ],
}
SCORING_CONFIG = {
    'batch_size': 2,
    'categories_tables': [],
    'period_minutes': 30,
    'tables': [
        {
            'name': 'yt_table_v3',
            'yt_path': '//home/eda-analytics/retail/product_SKU_score',
        },
    ],
    'personalized_table_template': 'yt_personalized_',
    'personalized_categories_table_template': 'categories_',
}

REDIS_READ_COMMAND_CONTROL = {
    'best_dc_count': 1,
    'max_retries': 2,
    'strategy': 'nearest_server_ping',
    'timeout_all_ms': 200,
    'timeout_single_ms': 100,
}


PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION = pytest.mark.parametrize(
    'handlers_version',
    [
        pytest.param(
            'v1',
            id='v1',
            marks=pytest.mark.config(
                EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                    {'get_items_categories_version': 'v2'}
                ),
            ),
        ),
        pytest.param(
            'v2',
            id='v2',
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                        {
                            'get_categories_products_info_version': 'v2',
                            'get_items_categories_version': 'v2',
                        }
                    ),
                ),
            ),
        ),
    ],
)


def make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_retail_categories_brand_orders_history=None,
):
    ids_mapping = []
    for i in range(1, 7):
        origin_id = 'origin_id_' + str(i)
        core_id = i
        public_id = 'public_id_' + str(i)

        ids_mapping.append(
            conftest.ProductMapping(origin_id, core_id, public_id),
        )
        mock_nomenclature_v2_details_context.add_product(id_=public_id)

    add_place_products_mapping(ids_mapping)

    mock_nomenclature_v1_categories_context.add_category(
        public_id=CHILD_ID, name='Плотва', parent_public_id=CATEGORY_ID,
    )
    mock_nomenclature_v1_categories_context.add_category(
        public_id=CATEGORY_ID, name='Рыба',
    )
    mock_nomenclature_v1_categories_context.add_category(
        public_id=THIRD_CATEGORY_ID, name='Овощи',
    )
    mock_nomenclature_v1_categories_context.add_category(
        public_id=FOURTH_CATEGORY_ID, name='Кулинария',
    )
    mock_nomenclature_v1_categories_context.add_category(
        public_id=FIFTH_CATEGORY_ID, name='Носки',
    )

    if mock_retail_categories_brand_orders_history is not None:
        mock_retail_categories_brand_orders_history.add_brand_product(
            1, 'public_id_1', 2,
        )
        mock_retail_categories_brand_orders_history.add_brand_product(
            1, 'public_id_2', 5,
        )
        mock_retail_categories_brand_orders_history.add_brand_product(
            1, 'public_id_3', 3,
        )
        mock_retail_categories_brand_orders_history.add_brand_product(
            1, 'public_id_4', 1,
        )

    def add_product_full_info(number, categories):
        public_id = 'public_id_' + str(number)
        mock_nomenclature_dynamic_info_context.add_product(
            public_id,
            origin_id='origin_id_' + str(number),
            parent_category_ids=categories,
        )
        mock_nomenclature_static_info_context.add_product(public_id)

    add_product_full_info(1, [CATEGORY_ID])
    add_product_full_info(2, [CATEGORY_ID])
    add_product_full_info(3, [CHILD_ID, THIRD_CATEGORY_ID])
    add_product_full_info(4, [THIRD_CATEGORY_ID])
    add_product_full_info(5, [FOURTH_CATEGORY_ID])
    add_product_full_info(6, [FIFTH_CATEGORY_ID])

    mock_nomenclature_get_parent_context.add_category(
        id_=CHILD_ID, parent_id=CATEGORY_ID,
    )
    mock_nomenclature_get_parent_context.add_category(id_=CATEGORY_ID)
    mock_nomenclature_get_parent_context.add_category(id_=THIRD_CATEGORY_ID)
    mock_nomenclature_get_parent_context.add_category(id_=FOURTH_CATEGORY_ID)
    mock_nomenclature_get_parent_context.add_category(id_=FIFTH_CATEGORY_ID)


def make_default_carousels(table, category, place=1, products_count=3):
    result = ['zadd']
    result.append('scores:top:' + table + ':' + str(place) + ':' + category)
    accumulator = 0.0
    for i in range(1, products_count + 1):
        accumulator += 0.1
        result.append(accumulator)
        result.append('origin_id_' + str(i))

    return result


def make_ordershistory_response(core_ids, place=1):
    return {
        'orders': [
            {
                'cart': [
                    {'name': '', 'place_menu_item_id': core_id, 'quantity': 1}
                    for core_id in core_ids
                ],
                'place_id': 1,
                'order_id': '',
                'is_asap': True,
                'source': 'eda',
                'status': 'delivered',
                'total_amount': '2222',
                'delivery_location': {'lat': 0.0, 'lon': 0.0},
                'created_at': '2020-01-28T12:00:00+03:00',
                'delivered_at': '2020-01-28T12:00:00+03:00',
            },
        ],
    }


def set_retail_categories_orders(
        core_ids, mock_retail_categories_brand_orders_history, brand_id=1,
):
    id_to_count = dict()
    for core_id in core_ids:
        if core_id in id_to_count:
            id_to_count[core_id] += 1
            continue
        id_to_count[core_id] = 1

    for core_id in id_to_count:
        mock_retail_categories_brand_orders_history.add_brand_product(
            brand_id, f'public_id_{core_id}', id_to_count[core_id],
        )


def make_categories_request(categories):
    return {
        'slug': 'slug',
        'categories': [
            {'uid': category, 'min_items_count': 1, 'max_items_count': 5}
            for category in categories
        ],
    }


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    ('bigb_profile', 'expected_order'),
    [
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb ничего не ответил, в конфиге брендов нет
        # нужного бренда, то будет использована дефолтная таблица скорингов
        pytest.param(
            None,
            [101, 102, 103],
            marks=[
                experiments.personalized_carousels(['products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
                        '0.1',
                        'id_3',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_1',
                    ],
                ),
            ],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb ничего не ответил, в конфиге брендов есть
        # нужный бренд, то будет использована таблица скорингов с учетом данных
        # из конфига
        pytest.param(
            None,
            [103, 102, 101],
            marks=[
                experiments.personalized_carousels(['products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_personalized_B1:1:' + CATEGORY_ID,
                        '0.1',
                        'id_1',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_3',
                    ],
                ),
            ],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb вернул категорию пользователя, в конфиге
        # брендов нет нужного бренда, то будет использована таблица скорингов
        # с учетом данных bigb
        pytest.param(
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [101, 103, 102],
            marks=[
                experiments.personalized_carousels(['products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_personalized_C2:1:' + CATEGORY_ID,
                        '0.1',
                        'id_2',
                        '0.2',
                        'id_3',
                        '0.3',
                        'id_1',
                    ],
                ),
            ],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb вернул категорию пользователя, в конфиге
        # брендов есть нужный бренд, то будет использована таблица скорингов
        # с учетом данных bigb (bigb приоритетнее)
        pytest.param(
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [101, 103, 102],
            marks=[
                experiments.personalized_carousels(['products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_personalized_C2:1:' + CATEGORY_ID,
                        '0.1',
                        'id_2',
                        '0.2',
                        'id_3',
                        '0.3',
                        'id_1',
                    ],
                ),
            ],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb вернул ответ, но категория пользователя
        # отсутствует, в конфиге брендов есть нужный бренд, то будет
        # использована таблица скорингов с учетом данных из конфига
        pytest.param(
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    income_level=None,
                ),
            ),
            [103, 102, 101],
            marks=[
                experiments.personalized_carousels(['products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_personalized_B1:1:' + CATEGORY_ID,
                        '0.1',
                        'id_1',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_3',
                    ],
                ),
            ],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb вернул ответ, но категория пользователя
        # отсутствует, в конфиге брендов нет нужного бренда, то будет
        # использована дефолтная таблица скорингов
        pytest.param(
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    income_level=None,
                ),
            ),
            [101, 102, 103],
            marks=[
                experiments.personalized_carousels(['products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'10': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
                        '0.1',
                        'id_3',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_1',
                    ],
                ),
            ],
        ),
        # Тест проверяет что включение в эксперименте персонализации
        # сортировок категорий не ломает сортировку товаров
        pytest.param(
            None,
            [101, 102, 103],
            marks=[
                experiments.personalized_carousels(['carousels_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
                        '0.1',
                        'id_3',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_1',
                    ],
                ),
            ],
        ),
        # Тест проверяет что включение в эксперименте персонализации
        # сортировок товаров в меню не влияет на сортировку товаров в каруселях
        pytest.param(
            None,
            [101, 102, 103],
            marks=[
                experiments.personalized_carousels(['menu_products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
                        '0.1',
                        'id_3',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_1',
                    ],
                    [
                        'zadd',
                        'scores:top:yt_personalized_B1:1:' + CATEGORY_ID,
                        '0.1',
                        'id_1',
                        '0.2',
                        'id_2',
                        '0.3',
                        'id_3',
                    ],
                ),
            ],
        ),
        # Тест проверяет что включение в эксперименте персонализации
        # сортировок категорий не включет сортировку товаров
        pytest.param(
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [101, 103, 102],
            marks=[
                experiments.personalized_carousels(['carousels_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
                        '0.1',
                        'id_2',
                        '0.2',
                        'id_3',
                        '0.3',
                        'id_1',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG)
@experiments.products_scoring()
async def test_personalized_carousels_bigb(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        bigb,
        bigb_profile,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        expected_order,
        mock_retail_categories_brand_orders_history,
):
    # Для сохранения текущей логики теста. Сервис не может сходить в ручку
    # orders-history из-за пустого eater-id.
    mock_retail_categories_brand_orders_history.set_status(500)
    public_ids = ['public_id_1', 'public_id_2', 'public_id_3']
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='id_1', core_id=101, public_id=public_ids[0],
            ),
            conftest.ProductMapping(
                origin_id='id_2', core_id=102, public_id=public_ids[1],
            ),
            conftest.ProductMapping(
                origin_id='id_3', core_id=103, public_id=public_ids[2],
            ),
        ],
    )
    for public_id in public_ids:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)

    mock_nomenclature_v1_categories_context.add_category(
        public_id=CHILD_ID, name='Плотва', parent_public_id=CATEGORY_ID,
    )
    mock_nomenclature_v1_categories_context.add_category(
        public_id=CATEGORY_ID, name='Рыба',
    )
    mock_nomenclature_get_parent_context.add_category(
        CHILD_ID, name='Плотва', parent_id=CATEGORY_ID,
    )
    mock_nomenclature_get_parent_context.add_category(CATEGORY_ID, name='Рыба')

    if bigb_profile:
        bigb.add_profile(passport_uid=PASSPORT_UID, profile=bigb_profile)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=GET_CATEGORIES_REQUEST,
        headers={'X-Yandex-Uid': PASSPORT_UID},
    )
    assert response.status_code == 200
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 1
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    assert 'categories' in response.json()

    categories = response.json()['categories']
    assert len(categories) == 1
    assert CATEGORY_ID == categories[0]['uid']

    items = categories[0]['items']
    assert len(items) == 3
    assert expected_order == [item['id'] for item in items]

    assert bigb.times_called == 1


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='v1_repeat_category', marks=experiments.repeat_category('v1'),
        ),
        pytest.param(
            id='v2_repeat_category', marks=experiments.repeat_category('v2'),
        ),
        pytest.param(
            id='disabled_repeat_category',
            marks=experiments.repeat_category('disabled'),
        ),
    ],
)
@experiments.products_scoring()
@experiments.personalized_carousels(['products_sort'])
@pytest.mark.config(EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG)
@pytest.mark.redis_store(
    [
        'zadd',
        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
        '0.1',
        'origin_id_3',
        '0.2',
        'origin_id_2',
        '0.3',
        'origin_id_1',
    ],
)
async def test_personalized_carousels_orders_history(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_static_info_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что товары в карусели категории вернутся в порядке,
    # соответствующем количеству заказанных товаров в истории пользователя
    # И персонализация не зависит от версии категории "Вы заказывали"

    make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_retail_categories_brand_orders_history,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=GET_CATEGORIES_REQUEST,
        headers={'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 200
    assert 'categories' in response.json()

    categories = response.json()['categories']
    assert len(categories) == 1
    assert CATEGORY_ID == categories[0]['uid']

    items = categories[0]['items']
    assert len(items) == 3
    assert [2, 3, 1] == [item['id'] for item in items]
    assert mock_retail_categories_brand_orders_history.times_called == 1

    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 1
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
        assert mock_nomenclature_get_parent_context.handler.times_called == 2


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.personalized_carousels(['products_sort'])
@pytest.mark.config(EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG)
@pytest.mark.redis_store(
    [
        'zadd',
        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
        '0.1',
        'origin_id_1',
        '0.2',
        'origin_id_2',
        '0.3',
        'origin_id_3',
    ],
)
async def test_personalized_carousels_no_orders_history(
        mockserver,
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_static_info_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что в случае, когда историю пользователя получить
    # не удалось, то товары в карусели категории вернутся в порядке,
    # соответствующем таблице скорингов карусели

    make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
    )

    mock_retail_categories_brand_orders_history.set_status(500)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=GET_CATEGORIES_REQUEST,
        headers={'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
    )
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 1
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    assert 'categories' in response.json()

    categories = response.json()['categories']
    assert len(categories) == 1
    assert CATEGORY_ID == categories[0]['uid']

    items = categories[0]['items']
    assert len(items) == 3
    assert [3, 2, 1] == [item['id'] for item in items]


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.personalized_carousels(['products_sort'])
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS={
        'get_items_categories_version': 'v2',
    },
)
@pytest.mark.redis_store(
    [
        'zadd',
        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
        '0.1',
        'origin_id_3',
        '0.2',
        'origin_id_2',
        '0.3',
        'origin_id_1',
    ],
)
async def test_personalized_carousels_no_categories_for_orders_history(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_static_info_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что в случае, когда категории для истории пользователя
    # получить не удалось, то товары в карусели категории вернутся в порядке,
    # соответствующем таблице скорингов карусели
    make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_retail_categories_brand_orders_history,
    )

    mock_nomenclature_dynamic_info_context.set_statuses([500, 200])

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=GET_CATEGORIES_REQUEST,
        headers={'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 200
    assert 'categories' in response.json()

    categories = response.json()['categories']
    assert len(categories) == 1
    assert CATEGORY_ID == categories[0]['uid']

    items = categories[0]['items']
    assert len(items) == 3
    assert [1, 2, 3] == [item['id'] for item in items]
    assert mock_retail_categories_brand_orders_history.times_called == 1
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 1
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.personalized_carousels(['products_sort'])
@pytest.mark.config(EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG)
@pytest.mark.redis_store(
    [
        'zadd',
        'scores:top:yt_table_v3:1:' + CATEGORY_ID,
        '0.1',
        'origin_id_3',
        '0.2',
        'origin_id_2',
        '0.3',
        'origin_id_1',
    ],
)
async def test_personalized_carousels_partial_categories_for_orders_history(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_static_info_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что в случае, когда категории верхнего уровня для
    # истории пользователя получить не удалось, но удалось получить
    # непосредственные категории товаров, то в карусели категории в начале
    # будут расположены товары из истории пользователя, а затем из таблицы
    # скорингов карусели

    make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_retail_categories_brand_orders_history,
    )
    mock_nomenclature_get_parent_context.set_statuses([500, 200])

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=GET_CATEGORIES_REQUEST,
        headers={'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 200
    assert 'categories' in response.json()

    categories = response.json()['categories']
    assert len(categories) == 1
    assert CATEGORY_ID == categories[0]['uid']

    items = categories[0]['items']
    assert len(items) == 3
    assert [2, 1, 3] == [item['id'] for item in items]
    assert mock_retail_categories_brand_orders_history.times_called == 1
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 1
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
        assert mock_nomenclature_get_parent_context.handler.times_called == 2


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    (
        'get_categories_request',
        'ordershistory_core_ids',
        'bigb_profile',
        'expected_order',
    ),
    [
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, то пересортировки категорий не происходит
        # и они возвращаются в том же порядке что и были запрошены
        pytest.param(
            make_categories_request(
                [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 4 - товар из THIRD_CATEGORY_ID
            # 1 - товар из CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [5, 5, 5, 5, 4, 4, 1],
            None,
            [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            marks=[experiments.personalized_carousels(['products_sort'])],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок категорий, то категории из истории покупок располагаются
        # в порядке количества купленных в них товаров.
        pytest.param(
            make_categories_request(
                [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 4 - товар из THIRD_CATEGORY_ID
            # 1 - товар из CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [5, 5, 5, 5, 4, 4, 1],
            None,
            [FOURTH_CATEGORY_ID, THIRD_CATEGORY_ID, CATEGORY_ID],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок категорий, то категории из истории покупок располагаются
        # перед категориями, покупок в которых не было. А категории, покупок
        # в которых не было, располагаются в том же порядке что и были
        # запрошены.
        pytest.param(
            make_categories_request(
                [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            ),
            # 4 - товар из THIRD_CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [4],
            None,
            [THIRD_CATEGORY_ID, CATEGORY_ID, FOURTH_CATEGORY_ID],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест по сути проверяет объединение условий двух предыдущих.
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок категорий, то категории из истории покупок располагаются
        # в порядке купленных в них товаров и перед категориями, покупок в
        # которых не было. А категории, покупок в которых не было,
        # располагаются в том же порядке что и были запрошены.
        pytest.param(
            make_categories_request(
                [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 1, 2 - товары из CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [5, 5, 1],
            None,
            [FOURTH_CATEGORY_ID, CATEGORY_ID, THIRD_CATEGORY_ID],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест проверяет что расположение динамической категории не меняется
        # даже если включен эксперимент по персонализации сортировок
        # категорий. Но не динамические размещаются так: категории из истории
        # покупок располагаютс в порядке купленных в них товаров и перед
        # категориями, покупок в которых не было. А категории, покупок в
        # которых не было, располагаются в том же порядке что и были
        # запрошены.
        pytest.param(
            make_categories_request(
                [
                    str(utils.REPEAT_CATEGORY_ID),
                    CATEGORY_ID,
                    THIRD_CATEGORY_ID,
                    FOURTH_CATEGORY_ID,
                ],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 1, 2 - товары из CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [5, 5, 1],
            None,
            [
                str(utils.REPEAT_CATEGORY_ID),
                FOURTH_CATEGORY_ID,
                CATEGORY_ID,
                THIRD_CATEGORY_ID,
            ],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест проверяет тоже самое что и предыдущий тест, но при запросе
        # динамическая категория располагается в середине.
        # Для подробностей см. коммент к предыдущему тесту
        pytest.param(
            make_categories_request(
                [
                    CATEGORY_ID,
                    str(utils.REPEAT_CATEGORY_ID),
                    THIRD_CATEGORY_ID,
                    FOURTH_CATEGORY_ID,
                ],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 1, 2 - товары из CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [5, 5, 1],
            None,
            [
                FOURTH_CATEGORY_ID,
                str(utils.REPEAT_CATEGORY_ID),
                CATEGORY_ID,
                THIRD_CATEGORY_ID,
            ],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест проверяет тоже самое что и два предыдущих теста, но при запросе
        # динамическая категория располагается в конце.
        # Для подробностей см. коммент к пред-предыдущему тесту.
        pytest.param(
            make_categories_request(
                [
                    CATEGORY_ID,
                    THIRD_CATEGORY_ID,
                    FOURTH_CATEGORY_ID,
                    str(utils.REPEAT_CATEGORY_ID),
                ],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 1, 2 - товары из CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [5, 5, 1],
            None,
            [
                FOURTH_CATEGORY_ID,
                CATEGORY_ID,
                THIRD_CATEGORY_ID,
                str(utils.REPEAT_CATEGORY_ID),
            ],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест проверяет что при включенном эксперименте сортировки каруселей,
        # успешном вычислении уровня дохода пользователя, наличии таблицы
        # скорингов для этого уровня дохода и отсутствии истории заказов,
        # карусели будут отсортированы в соответствии с весами в таблице
        # скорингов.
        pytest.param(
            make_categories_request(
                [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            ),
            [],
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [FOURTH_CATEGORY_ID, CATEGORY_ID, THIRD_CATEGORY_ID],
            marks=[
                experiments.personalized_carousels(['carousels_sort']),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:categories_C2:1',
                        {
                            FOURTH_CATEGORY_ID: '0.9',
                            CATEGORY_ID: '0.8',
                            THIRD_CATEGORY_ID: '0.7',
                        },
                    ],
                ),
            ],
        ),
        # Тест проверяет что при включенном эксперименте сортировки каруселей,
        # успешном вычислении уровня дохода пользователя, отсутствии таблицы
        # скорингов для этого уровня дохода и отсутствии истории заказов,
        # карусели будут отсортированы в соответствии с порядком в запросе.
        pytest.param(
            make_categories_request(
                [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            ),
            [],
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
            marks=[experiments.personalized_carousels(['carousels_sort'])],
        ),
        # Тест проверяет что при включенном эксперименте сортировки каруселей,
        # успешном вычислении уровня дохода пользователя, наличии таблицы
        # скорингов для этого уровня дохода и при наличии истории заказов,
        # карусели категорий из истории заказов будут первыми, а затем
        # остальные карусели будут отсортированы в соответствии с весами в
        # таблице скорингов.
        pytest.param(
            make_categories_request(
                [
                    CATEGORY_ID,
                    THIRD_CATEGORY_ID,
                    FOURTH_CATEGORY_ID,
                    FIFTH_CATEGORY_ID,
                ],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 4 - товар из THIRD_CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [4, 5, 5],
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [
                FOURTH_CATEGORY_ID,
                THIRD_CATEGORY_ID,
                FIFTH_CATEGORY_ID,
                CATEGORY_ID,
            ],
            marks=[
                experiments.personalized_carousels(['carousels_sort']),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:categories_C2:1',
                        {
                            FOURTH_CATEGORY_ID: '0.9',
                            FIFTH_CATEGORY_ID: '0.8',
                            CATEGORY_ID: '0.7',
                            THIRD_CATEGORY_ID: '0.6',
                        },
                    ],
                ),
            ],
        ),
        # Тест проверяет что при включенном эксперименте сортировки каруселей,
        # успешном вычислении уровня дохода пользователя, наличии истории
        # заказов, наличии таблицы скорингов для этого уровня дохода, но при
        # отсутствии некоторых категорий в этой таблице, карусели категорий из
        # истории заказов будут первыми, затем остальные карусели будут
        # отсортированы в соответствии с весами в таблице скорингов,
        # категории, отсутствующие в таблице скорингов окажутся в конце списка.
        pytest.param(
            make_categories_request(
                [
                    CATEGORY_ID,
                    THIRD_CATEGORY_ID,
                    FOURTH_CATEGORY_ID,
                    FIFTH_CATEGORY_ID,
                ],
            ),
            # 5 - товар из FOURTH_CATEGORY_ID
            # 4 - товар из THIRD_CATEGORY_ID
            # количество повторений товара в списке соответствует
            # количеству заказов этого товара пользователем.
            [4, 5, 5],
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [
                FOURTH_CATEGORY_ID,
                THIRD_CATEGORY_ID,
                CATEGORY_ID,
                FIFTH_CATEGORY_ID,
            ],
            marks=[
                experiments.personalized_carousels(['carousels_sort']),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:categories_C2:1',
                        {CATEGORY_ID: '0.9', FOURTH_CATEGORY_ID: '0.7'},
                    ],
                ),
            ],
        ),
    ],
)
@experiments.repeat_category()
@experiments.products_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={},
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
    ),
    EATS_PRODUCTS_REDIS_READ_COMMAND_CONTROL=REDIS_READ_COMMAND_CONTROL,
)
@pytest.mark.redis_store(
    make_default_carousels(table='yt_table_v3', category=CATEGORY_ID),
    make_default_carousels(table='yt_table_v3', category=THIRD_CATEGORY_ID),
    make_default_carousels(table='yt_table_v3', category=FOURTH_CATEGORY_ID),
    make_default_carousels(table='yt_table_v3', category=FIFTH_CATEGORY_ID),
)
async def test_personalized_carousels_sort(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        bigb,
        mock_nomenclature_static_info_context,
        handlers_version,
        get_categories_request,
        ordershistory_core_ids,
        bigb_profile,
        expected_order,
        mock_retail_categories_brand_orders_history,
):

    make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
    )

    if bigb_profile:
        bigb.add_profile(passport_uid=PASSPORT_UID, profile=bigb_profile)

    set_retail_categories_orders(
        ordershistory_core_ids, mock_retail_categories_brand_orders_history,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=get_categories_request,
        headers={'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
    )

    assert response.status_code == 200
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 1
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == (
            1 if ordershistory_core_ids else 0
        )
        assert mock_nomenclature_get_parent_context.handler.times_called == (
            1 if ordershistory_core_ids else 0
        )
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == (
            2 if ordershistory_core_ids else 1
        )
        assert mock_nomenclature_get_parent_context.handler.times_called == (
            2 if ordershistory_core_ids else 1
        )
    assert 'categories' in response.json()

    categories = response.json()['categories']
    assert expected_order == [category['uid'] for category in categories]


@PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.personalized_carousels(['products_sort'])
@experiments.repeat_category()
@experiments.products_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG,
    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={},
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
    ),
    EATS_PRODUCTS_REDIS_READ_COMMAND_CONTROL=REDIS_READ_COMMAND_CONTROL,
)
@pytest.mark.parametrize(
    ['headers', 'has_eater_id'],
    [
        pytest.param({'X-Yandex-Uid': PASSPORT_UID}, False, id='no eater_id'),
        pytest.param(
            {'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id='},
            False,
            id='empty eater_id',
        ),
        pytest.param(
            {'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
            True,
            id='has eater_id',
        ),
    ],
)
async def test_personalized_carousels_no_eater_id(
        mockserver,
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_static_info_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
        headers,
        has_eater_id,
):
    # Проверяется, что при пустом eater_id не будет сделан запрос
    # в eats-retail-categories через ручку
    # /v1/orders-history/products/brand

    make_default_environment(
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
    )

    orders_history_core_ids = [5, 5, 5, 5, 4, 4, 1]

    set_retail_categories_orders(
        orders_history_core_ids, mock_retail_categories_brand_orders_history,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json=make_categories_request(
            [CATEGORY_ID, THIRD_CATEGORY_ID, FOURTH_CATEGORY_ID],
        ),
        headers=headers,
    )

    assert response.status_code == 200
    assert mock_retail_categories_brand_orders_history.times_called == (
        1 if has_eater_id else 0
    )
