# Проверка отключена по причине того, что линтер не находит библиотеку
# pylint: disable=import-error
from eats_bigb import eats_bigb
import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PASSPORT_UID = '1'
CATEGORY_ID = '1111'

SCORING_CONFIG = {
    'batch_size': 1,
    'categories_tables': [],
    'period_minutes': 1,
    'tables': [],
    'personalized_table_template': 'yt_personalized_',
    'personalized_categories_table_template': 'categories_',
}


@pytest.mark.parametrize(
    ('bigb_profile', 'expected_order'),
    [
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb ничего не ответил, в конфиге брендов нет
        # нужного бренда, в таблице скорингов нет нужных товаров, то товары
        # отсортируются по полю sort_order из сервиса eats-nomenclature
        pytest.param(
            None,
            [101, 102, 103, 104, 105],
            marks=[
                experiments.personalized_carousels(['menu_products_sort']),
                pytest.mark.config(EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={}),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:yt_table_v3:' + str(utils.BRAND_ID),
                        {'origin_id_10': '0.1'},
                    ],
                ),
            ],
        ),
        # Тест проверяет что если включен эксперимент по персонализации
        # сортировок товаров, bigb ничего не ответил, в конфиге брендов нет
        # нужного бренда, в дефолтной таблице скорингов есть нужные товары,
        # то товары отсортируются по дефолтной таблице скорингов
        pytest.param(
            None,
            [105, 104, 103, 102, 101],
            marks=[
                experiments.personalized_carousels(['menu_products_sort']),
                pytest.mark.config(EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={}),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:yt_table_v3:' + str(utils.BRAND_ID),
                        {
                            'origin_id_1': '0.1',
                            'origin_id_2': '0.2',
                            'origin_id_3': '0.3',
                            'origin_id_4': '0.4',
                            'origin_id_5': '0.5',
                        },
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
            [104, 105, 103, 102, 101],
            marks=[
                experiments.personalized_carousels(['menu_products_sort']),
                pytest.mark.config(
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'B1'},
                ),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:yt_personalized_B1:'
                        + str(utils.BRAND_ID),
                        {
                            'origin_id_1': '0.1',
                            'origin_id_2': '0.2',
                            'origin_id_3': '0.3',
                            'origin_id_4': '0.5',
                            'origin_id_5': '0.4',
                        },
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
            [104, 103, 105, 102, 101],
            marks=[
                experiments.personalized_carousels(['menu_products_sort']),
                pytest.mark.config(EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={}),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:yt_personalized_C2:'
                        + str(utils.BRAND_ID),
                        {
                            'origin_id_1': '0.1',
                            'origin_id_2': '0.2',
                            'origin_id_3': '0.4',
                            'origin_id_4': '0.5',
                            'origin_id_5': '0.3',
                        },
                    ],
                ),
            ],
        ),
        # Тест проверяет что включение персонализации в каруселях
        # не влияет на сортировку товаров в ручке menu/goods.
        pytest.param(
            eats_bigb.Profile(
                demographics=eats_bigb.Demograpics(
                    gender=eats_bigb.Gender.MALE,
                    age_category=eats_bigb.AgeCategory.LESS_THEN_18,
                    # C2
                    income_level=eats_bigb.IncomeLevel.WELL_ABOVE_AVERAGE,
                ),
            ),
            [101, 102, 103, 104, 105],
            marks=[
                experiments.personalized_carousels(
                    ['products_sort', 'carousels_sort'],
                ),
                pytest.mark.config(
                    EATS_PRODUCTS_INCOME_LEVEL_BY_BRAND={'1': 'C2'},
                ),
                pytest.mark.redis_store(
                    [
                        'hmset',
                        'scores:brands:yt_personalized_C2:'
                        + str(utils.BRAND_ID),
                        {
                            'origin_id_1': '0.1',
                            'origin_id_2': '0.2',
                            'origin_id_3': '0.4',
                            'origin_id_4': '0.5',
                            'origin_id_5': '0.3',
                        },
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('nmn_integration_version', ['v1', 'v2'])
@pytest.mark.config(EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG)
@experiments.products_scoring()
async def test_personalized_menu_bigb(
        add_place_products_mapping,
        mock_nomenclature_for_v2_menu_goods,
        bigb,
        bigb_profile,
        expected_order,
        nmn_integration_version,
):
    menu_goods_context = mock_nomenclature_for_v2_menu_goods
    category = conftest.CategoryMenuGoods(
        public_id=CATEGORY_ID,
        name='Молочные продукты',
        origin_id='category_1',
    )

    ids_mapping = []
    for i in range(1, 6):
        origin_id = 'origin_id_' + str(i)
        core_id = 100 + i
        public_id = 'public_id_' + str(i)
        name = 'product_' + str(i)
        product = conftest.ProductMenuGoods(
            public_id=public_id, name=name, origin_id=origin_id,
        )

        ids_mapping.append(
            conftest.ProductMapping(origin_id, core_id, public_id),
        )

        category.add_product(product, sort_order=i)

    add_place_products_mapping(ids_mapping)

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(category)
    menu_goods_context.set_place(place)

    if bigb_profile:
        bigb.add_profile(passport_uid=PASSPORT_UID, profile=bigb_profile)

    response = await menu_goods_context.invoke_menu_goods_basic(
        {
            'shippingType': 'pickup',
            'slug': utils.PLACE_SLUG,
            'category_uid': CATEGORY_ID,
            'maxDepth': 100,
        },
        integration_version=nmn_integration_version,
        headers={'X-Yandex-Uid': PASSPORT_UID},
    )

    assert response.status_code == 200

    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    items = categories[0]['items']
    assert len(items) == 5
    assert expected_order == [item['id'] for item in items]

    assert bigb.times_called == 1


@pytest.mark.parametrize(
    'nmn_integration_version',
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
            marks=pytest.mark.config(
                EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS={
                    'menu_goods_category_products_version': 'v2',
                    'get_items_categories_version': 'v2',
                },
            ),
        ),
    ],
)
@experiments.products_scoring()
@experiments.personalized_carousels(['menu_products_sort'])
@pytest.mark.config(EATS_PRODUCTS_YT_PRODUCTS_SCORING=SCORING_CONFIG)
@pytest.mark.redis_store(
    [
        'hmset',
        'scores:brands:yt_table_v3:' + str(utils.BRAND_ID),
        {'origin_id_6': '0.6', 'origin_id_7': '0.7'},
    ],
)
async def test_personalized_menu_orders_history(
        add_place_products_mapping,
        mock_nomenclature_for_v2_menu_goods,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_retail_categories_brand_orders_history,
        nmn_integration_version,
):
    # Тест проверяет, что товары в категории вернутся в порядке,
    # соответствующем количеству заказанных товаров в истории пользователя

    menu_goods_context = mock_nomenclature_for_v2_menu_goods
    category = conftest.CategoryMenuGoods(
        public_id=CATEGORY_ID,
        name='Молочные продукты',
        origin_id='category_1',
    )

    ids_mapping = []
    for i in range(1, 8):
        origin_id = 'origin_id_' + str(i)
        core_id = i
        public_id = 'public_id_' + str(i)
        name = 'product_' + str(i)
        product = conftest.ProductMenuGoods(
            public_id=public_id, name=name, origin_id=origin_id,
        )

        ids_mapping.append(
            conftest.ProductMapping(origin_id, core_id, public_id),
        )

        category.add_product(product, sort_order=i)

        mock_nomenclature_dynamic_info_context.add_product(
            public_id, origin_id=origin_id, parent_category_ids=[CATEGORY_ID],
        )

    add_place_products_mapping(ids_mapping)

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(category)
    menu_goods_context.set_place(place)

    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'public_id_1', 1,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'public_id_2', 3,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'public_id_3', 2,
    )

    mock_nomenclature_get_parent_context.set_status(500)

    response = await menu_goods_context.invoke_menu_goods_basic(
        {
            'shippingType': 'pickup',
            'slug': utils.PLACE_SLUG,
            'category_uid': CATEGORY_ID,
            'maxDepth': 100,
        },
        integration_version=nmn_integration_version,
        headers={'X-Yandex-Uid': PASSPORT_UID, 'X-Eats-User': 'user_id=123'},
        use_version_for_all=False,
    )

    assert response.status_code == 200
    assert (
        mock_retail_categories_brand_orders_history.handler.times_called == 1
    )

    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    items = categories[0]['items']
    assert len(items) == 7

    # Товары 2, 3, 1 - из истории покупок, 7 и 6 есть в табличке скорингов,
    # 4 и 5 нет ни в истории ни в табличке скорингов, сортируются согласно
    # полю sort_order из сервиса eats-nomenclature.
    assert [2, 3, 1, 7, 6, 4, 5] == [item['id'] for item in items]
