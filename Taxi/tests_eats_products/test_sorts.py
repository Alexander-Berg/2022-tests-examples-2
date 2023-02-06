# pylint: disable=too-many-lines
import copy

import eats_adverts_goods  # pylint: disable=import-error
import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}

GET_CATEGORIES_CONSUMER = 'eats_products/get_categories'

EATER_ID = '123'
PRODUCTS_HEADERS = {
    'X-Eats-User': f'user_id={EATER_ID}',
    'X-AppMetrica-DeviceId': 'device_id',
}

CASHBACK_ENABLED_SETTINGS = utils.dynamic_categories_config(
    cashback_enabled=True,
)

PRICE_DESC = 'price_desc'
PRICE_ASC = 'price_asc'
BY_POPULARITY = 'by_popularity'
EXPECTED_RESPONSE_SORTS_ENABLED = {
    'available': [
        {
            'slug': BY_POPULARITY,
            'title_in_list': 'Популярные',
            'title_applied': 'Сначала популярные',
        },
        {
            'slug': PRICE_DESC,
            'title_in_list': 'Дорогие',
            'title_applied': 'Сначала дорогие',
        },
    ],
    'applied': PRICE_DESC,
    'default': BY_POPULARITY,
    'position': 'before_filters',
}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
]

PROMOTION_NAME = 'testsuite_1'

CATEGORIES_BASE_REQUEST = {
    'slug': 'slug',
    'categories': [{'id': 1, 'min_items_count': 1, 'max_items_count': 4}],
}


REPEAT_CATEGORIES_CONFIG = {
    'discount': {
        'enabled': False,
        'id': utils.DISCOUNT_CATEGORY_ID,
        'name': 'Скидки',
    },
    'popular': {
        'enabled': False,
        'id': utils.POPULAR_CATEGORY_ID,
        'name': 'Популярное',
    },
    'repeat': {
        'enabled': True,
        'id': utils.REPEAT_CATEGORY_ID,
        'name': 'Вы уже заказывали',
    },
    'repeat_this_brand': {
        'enabled': True,
        'id': utils.REPEAT_THIS_BRAND_ID,
        'name': 'В этом магазине',
    },
    'repeat_other_brands': {
        'enabled': True,
        'id': utils.REPEAT_OTHER_BRANDS_ID,
        'name': 'В других магазинах',
    },
}


def load_json_details_response(load_json):
    response = load_json('v2_place_assortment_details_response.json')
    response['products'][0]['old_price'] = 1999.0
    response['products'][1]['old_price'] = 1990.0
    response['products'][1]['price'] = 990.0
    response['products'][2]['price'] = 999.0
    return response


@experiments.FEW_SORTS_ENABLED
async def test_sort_types_sorting_enable(
        taxi_eats_products, mockserver, load_json,
):
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 106
    request['sort'] = PRICE_DESC

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature-response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request,
    )

    for item in response.json()['payload']['categories']:
        assert item['sorts'] == EXPECTED_RESPONSE_SORTS_ENABLED
    assert response.status_code == 200


@experiments.SORTS_DISABLED
async def test_sort_types_sorting_disable(
        taxi_eats_products, mockserver, load_json,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature-response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )

    for item in response.json()['payload']['categories']:
        assert 'sorts' not in item
    assert response.status_code == 200


@pytest.mark.parametrize(
    'category_id, handlers_v2',
    [
        pytest.param(utils.DISCOUNT_CATEGORY_ID, True, id='discount category'),
        pytest.param(utils.REPEAT_CATEGORY_ID, False, id='repeat category'),
        pytest.param(utils.POPULAR_CATEGORY_ID, False, id='popular category'),
        pytest.param(
            utils.CASHBACK_CATEGORY_ID,
            False,
            marks=(
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
                experiments.CASHBACK_CATEGORY_ENABLED,
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
                ),
            ),
            id='cashback category',
        ),
    ],
)
@experiments.FEW_SORTS_ENABLED
@experiments.discount_category()
@experiments.repeat_category()
@experiments.popular_category()
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
        discount_enabled=True,
        popular_enabled=True,
        cashback_enabled=True,
    ),
)
async def test_dynamic_categories_sorts_enable(
        taxi_eats_products,
        mockserver,
        load_json,
        category_id,
        handlers_v2,
        mock_v2_fetch_discounts_context,
        setup_nomenclature_handlers_v2,
        mock_retail_categories_brand_orders_history,
):
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = category_id
    products_request['sort'] = PRICE_DESC

    if handlers_v2:
        setup_nomenclature_handlers_v2()
    else:

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature(request):
            return load_json('v2_place_assortment_details_response.json')

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.EATS_CATALOG_STORAGE)
    def _mock_retrieve_by_ids(request):
        return utils.DEFAULT_EATS_CATALOG_RESPONSE

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    for item in response.json()['payload']['categories']:
        assert item['sorts'] == EXPECTED_RESPONSE_SORTS_ENABLED
    assert response.status_code == 200


@pytest.mark.parametrize(
    'sort_type, expected_id_sort_order,',
    [
        pytest.param(
            # тест показывает, что в эксперименте такой
            # сортировки нет, но фронт может ее прислать
            PRICE_ASC,
            {5: 2, 3: 3, 4: 4, 9: 1, 7: 5, 6: 6},
            id='price asc',
        ),
        pytest.param(
            PRICE_DESC, {4: 3, 3: 4, 5: 5, 6: 1, 7: 2, 9: 6}, id='price desc',
        ),
        pytest.param(
            BY_POPULARITY,
            {4: 1, 5: 2, 3: 4, 7: 3, 6: 5, 9: 6},
            id='by popularity',
        ),
        pytest.param(None, {4: 1, 5: 2, 3: 4, 7: 3, 6: 5, 9: 6}, id='default'),
    ],
)
@experiments.FEW_SORTS_ENABLED
async def test_default_categories_sort_from_front(
        taxi_eats_products,
        mockserver,
        load_json,
        sort_type,
        expected_id_sort_order,
        add_default_product_mapping,
):
    # тест проверяет сортировки: цена по возрастанию,
    # цена по убыванию, по популярности.
    # тест проверяетя проставление поля sortOrder
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 106
    products_request['sort'] = sort_type

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature-response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    for category in categories:
        for item in category['items']:
            assert item['sortOrder'] == expected_id_sort_order[item['id']]


@pytest.mark.parametrize(
    'sort_type, expected_order',
    [(PRICE_ASC, [4, 5, 3]), (PRICE_DESC, [4, 5, 3])],
)
async def test_default_categories_sort_with_equal_price(
        taxi_eats_products,
        mockserver,
        load_json,
        sort_type,
        expected_order,
        add_default_product_mapping,
):
    # тест проверяет сортировку по цене.
    # если цена одинковая, то сортирется по алфавиту
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 106
    products_request['sort'] = sort_type

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        nom_response = load_json('nomenclature-response.json')
        for item in nom_response['categories'][0]['items']:
            item['price'] = 4
        return nom_response

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    products = categories[0]['items']
    for i, order in enumerate(expected_order):
        assert products[i]['id'] == order


@pytest.mark.parametrize(
    'category_id, sort_type, expected_order, handlers_v2',
    [
        pytest.param(
            utils.DISCOUNT_CATEGORY_ID,
            PRICE_ASC,
            [2, 1, 3],
            True,
            id='discount category, price asc',
        ),
        pytest.param(
            utils.DISCOUNT_CATEGORY_ID,
            PRICE_DESC,
            [1, 3, 2],
            True,
            id='discount category, price desc',
        ),
        pytest.param(
            utils.REPEAT_CATEGORY_ID,
            PRICE_ASC,
            [2, 7, 1, 3],
            False,
            id='repeat category, price asc',
        ),
        pytest.param(
            utils.REPEAT_CATEGORY_ID,
            PRICE_DESC,
            [1, 3, 2, 7],
            False,
            id='repeat category, price desc',
        ),
        pytest.param(
            utils.POPULAR_CATEGORY_ID,
            PRICE_ASC,
            [2, 1, 3],
            False,
            id='popular category, price asc',
        ),
        pytest.param(
            utils.POPULAR_CATEGORY_ID,
            PRICE_DESC,
            [1, 3, 2],
            False,
            id='popular category, price desc',
        ),
        pytest.param(
            utils.CASHBACK_CATEGORY_ID,
            PRICE_ASC,
            [2, 1, 3],
            False,
            marks=(
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
                experiments.CASHBACK_CATEGORY_ENABLED,
            ),
            id='cashback category, price asc',
        ),
        pytest.param(
            utils.CASHBACK_CATEGORY_ID,
            PRICE_DESC,
            [1, 3, 2],
            False,
            marks=(
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
                experiments.CASHBACK_CATEGORY_ENABLED,
            ),
            id='cashback category, price desc',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@experiments.discount_category()
@experiments.repeat_category()
@experiments.popular_category()
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
        discount_enabled=True,
        popular_enabled=True,
        cashback_enabled=True,
    ),
)
@experiments.FEW_SORTS_ENABLED
async def test_dynamic_categories_sort_from_front(
        taxi_eats_products,
        mockserver,
        load_json,
        category_id,
        sort_type,
        expected_order,
        handlers_v2,
        cashback_handles_version,
        mock_v2_fetch_discounts_context,
        setup_nomenclature_handlers_v2,
        mock_retail_categories_brand_orders_history,
):
    # тест проверяет сортировку динамических категорий.
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = category_id
    products_request['sort'] = sort_type

    if handlers_v2:
        setup_nomenclature_handlers_v2()
    else:
        if cashback_handles_version == 'v2':
            setup_nomenclature_handlers_v2()

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature(request):
            return load_json_details_response(load_json)

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.EATS_CATALOG_STORAGE)
    def _mock_retrieve_by_ids(request):
        return utils.DEFAULT_EATS_CATALOG_RESPONSE

    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', value_type='absolute', value=7,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', value_type='absolute', value=9,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    products = categories[0]['items']
    for i, order in enumerate(expected_order):
        assert products[i]['id'] == order

    for category in categories:
        assert category['sorts']['applied'] == sort_type


@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(
                    product_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                ),
                eats_adverts_goods.types.Product(
                    product_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'sort_type, expected_order',
    [
        pytest.param(
            BY_POPULARITY,
            {101: [], 105: [1, 2, 3], 106: [4, 5, 6]},
            id='sort without promos',
        ),
        pytest.param(
            BY_POPULARITY,
            {101: [], 105: [3, 1, 2], 106: [6, 4, 5]},
            marks=(
                experiments.make_promo_sorts_experiment(
                    promotions=[PROMOTION_NAME],
                ),
            ),
            id='sort with promos',
        ),
        pytest.param(
            BY_POPULARITY,
            {101: [], 105: [1, 3, 2], 106: [4, 6, 5]},
            marks=(
                experiments.make_promo_sorts_experiment(
                    promotions=[PROMOTION_NAME], promo_positions=[1],
                ),
            ),
            id='sort with promos and positions',
        ),
        pytest.param(
            PRICE_ASC,
            {101: [], 105: [1, 2, 3], 106: [4, 5, 6]},
            marks=(
                experiments.make_promo_sorts_experiment(
                    promotions=[PROMOTION_NAME],
                ),
            ),
            id='sort with non-default sort ignore promos',
        ),
    ],
)
async def test_promo_sorts(
        taxi_eats_products,
        eats_adverts_goods_cache,
        yt_apply,
        add_default_product_mapping,
        mock_v1_nomenclature_context,
        sort_type,
        expected_order,
):
    # EDACAT-2138: тест проверяет рекламные сортировки.
    # Рекламируемые внутри категории товары должны подниматься
    # в начало органической выдачи, или на указанные позиции
    # (если заданы в эксперименте).
    # Рекламные сортировки применяются только если не задана
    # какая либо кастомная сортировка.
    # По-умолчанию: {101: [], 105: [1, 2, 3], 106: [4, 5, 6]}

    add_default_product_mapping()

    # category 1
    category_1 = conftest.NomenclatureCategory(
        id_='category_id_5',
        name='Фрукты',
        public_id=105,
        parent_id='category_id_1',
        parent_public_id=101,
    )
    for i in range(1, 4):
        category_1.add_product(
            conftest.NomenclatureProduct(
                public_id=f'bb231b95-1ff2-4bc4-b78d-dcaa1f69b00{i}',
                price=100 * i,
                nom_id=f'item_id_{i}',
            ),
        )
    mock_v1_nomenclature_context.add_category(category_1)

    # category 2
    category_2 = conftest.NomenclatureCategory(
        id_='category_id_6',
        name='Овощи',
        public_id=106,
        parent_id='category_id_1',
        parent_public_id=101,
    )
    for i in range(4, 7):
        category_2.add_product(
            conftest.NomenclatureProduct(
                public_id=f'bb231b95-1ff2-4bc4-b78d-dcaa1f69b00{i}',
                price=100 * i,
                nom_id=f'item_id_{i}',
            ),
        )
    mock_v1_nomenclature_context.add_category(category_2)

    # parent category
    parent_category = conftest.NomenclatureCategory(
        id_='category_id_1', name='Овощи и фрукты', public_id=101,
    )
    mock_v1_nomenclature_context.add_category(parent_category)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 101
    products_request['sort'] = sort_type

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']

    actual_order = {}
    for category in categories:
        order = [item['id'] for item in category['items']]
        actual_order[category['id']] = order
    assert actual_order == expected_order


@pytest.mark.parametrize(
    'category_id, sort_type, expected_order, handlers_v2',
    [
        pytest.param(
            utils.DISCOUNT_CATEGORY_ID,
            BY_POPULARITY,
            [3, 2, 1],
            True,
            id='discount default sort',
        ),
        pytest.param(
            utils.DISCOUNT_CATEGORY_ID,
            PRICE_DESC,
            [1, 3, 2],
            True,
            id='discount price desc sort',
        ),
        pytest.param(
            utils.CASHBACK_CATEGORY_ID,
            BY_POPULARITY,
            [3, 1, 2],
            False,
            marks=(
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
                experiments.CASHBACK_CATEGORY_ENABLED,
            ),
            id='cashback price default sort',
        ),
        pytest.param(
            utils.CASHBACK_CATEGORY_ID,
            PRICE_DESC,
            [1, 3, 2],
            False,
            marks=(
                experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
                experiments.CASHBACK_CATEGORY_ENABLED,
            ),
            id='cashback price desc sort',
        ),
        pytest.param(
            utils.REPEAT_CATEGORY_ID,
            BY_POPULARITY,
            [2, 3, 1],
            False,
            id='repeat promo sort ignored',
        ),
        pytest.param(
            utils.POPULAR_CATEGORY_ID,
            BY_POPULARITY,
            [3, 2, 1],
            False,
            id='popular promo sort ignored',
        ),
    ],
)
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(
                    product_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@experiments.discount_category()
@experiments.repeat_category()
@experiments.popular_category()
@experiments.products_scoring()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
        discount_enabled=True,
        popular_enabled=True,
        cashback_enabled=True,
    ),
)
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.FEW_SORTS_ENABLED
@experiments.make_promo_sorts_experiment(promotions=[PROMOTION_NAME])
async def test_dynamic_categories_promo_sort(
        taxi_eats_products,
        mockserver,
        load_json,
        category_id,
        sort_type,
        expected_order,
        handlers_v2,
        cashback_handles_version,
        mock_v2_fetch_discounts_context,
        setup_nomenclature_handlers_v2,
        mock_retail_categories_brand_orders_history,
):
    # EDACAT-2138:
    # Тест проверяет рекламные сортировки в категориях скидки и кэшбек.
    # В категориях 'Вы заказывали' и 'Популярное' рекламная сортировка
    # игнорируется. Рекламируемые товары должны подниматься в начало
    # органической выдачи. Рекламные сортировки применяются только если
    # не задана какая либо кастомная сортировка.

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = category_id
    products_request['sort'] = sort_type

    if handlers_v2:
        setup_nomenclature_handlers_v2()
    else:
        if cashback_handles_version == 'v2':
            setup_nomenclature_handlers_v2()

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature(request):
            return load_json_details_response(load_json)

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.EATS_CATALOG_STORAGE)
    def _mock_retrieve_by_ids(request):
        return utils.DEFAULT_EATS_CATALOG_RESPONSE

    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', value_type='absolute', value=7,
    )
    mock_v2_fetch_discounts_context.add_cashback_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', value_type='absolute', value=9,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    products = categories[0]['items']
    actual_order = []
    for item in products:
        actual_order.append(item['id'])
    assert actual_order == expected_order

    for category in categories:
        assert category['sorts']['applied'] == sort_type


@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(
                    product_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                ),
                eats_adverts_goods.types.Product(
                    product_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
                ),
            ],
        ),
    ],
)
@experiments.make_promo_sorts_experiment(promotions=[PROMOTION_NAME])
@pytest.mark.config(
    EATS_ADVERTS_GOODS_YT_LOG_SETTINGS={'is_auction_log_enabled': True},
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_promo_sorts_analytical_log(
        taxi_eats_products,
        yt_apply,
        testpoint,
        add_default_product_mapping,
        mock_v1_nomenclature_context,
):
    # EDACAT-2353: проверяем аналитическое логирование коммерческих
    # сортировок

    add_default_product_mapping()

    category = conftest.NomenclatureCategory(
        id_='category_id_1', name='Фрукты', public_id=101,
    )
    for i in range(1, 5):
        category.add_product(
            conftest.NomenclatureProduct(
                public_id=f'bb231b95-1ff2-4bc4-b78d-dcaa1f69b00{i}',
                price=100 * i,
                nom_id=f'item_id_{i}',
            ),
        )
    mock_v1_nomenclature_context.add_category(category)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 101
    products_request['sort'] = BY_POPULARITY

    @testpoint('adverts-auction-sort-items')
    def log_promo_sorts(data):
        assert data == {
            'timestamp': '2022-01-01T15:00:00+03:00',
            'tags': {'context': 'retail-auction', 'category_public_id': '101'},
            'promo_items': [
                {
                    'item_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                    'pos_before_sort': 0,
                    'pos_after_sort': 0,
                },
                {
                    'item_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
                    'pos_before_sort': 3,
                    'pos_after_sort': 1,
                },
            ],
        }

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    assert log_promo_sorts.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.now('2022-01-01T12:00:00+0000')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[0]),
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[3]),
            ],
        ),
    ],
)
@pytest.mark.config(
    EATS_ADVERTS_GOODS_YT_LOG_SETTINGS={'is_auction_log_enabled': True},
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=CASHBACK_ENABLED_SETTINGS,
)
@experiments.make_promo_sorts_experiment(
    promotions=[PROMOTION_NAME], consumer=GET_CATEGORIES_CONSUMER,
)
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.products_scoring()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
async def test_promo_sorts_cashback_get_categories(
        taxi_eats_products,
        load_json,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mockserver,
        handlers_version,
        redis_store,
        add_default_product_mapping,
        mock_nomenclature_v1_categories_context,
):
    # EDACAT-2821: Проверяет рекламные сортировки в категории с
    # кешбеком в ручке get-categories
    add_default_product_mapping()

    for i, public_id in enumerate(PUBLIC_IDS):
        mock_nomenclature_v2_details_context.add_product(
            public_id, price=(i + 1) * 100,
        )
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=(i + 1) * 100,
        )
        mock_v2_fetch_discounts_context.add_cashback_product(
            public_id, value_type='absolute', value=(i + 1) * 10,
        )

    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request['categories'][0]['id'] = utils.CASHBACK_CATEGORY_ID

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_v2_fetch_discounts_context.handler.times_called == 1
    categories = set(c['id'] for c in response.json()['categories'])
    assert (utils.CASHBACK_CATEGORY_ID in categories) == 1

    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_nomenclature_v1_categories_context.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_v1_categories_context.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1

    products = response.json()['categories'][0]['items']
    assert len(products) == 4
    assert [product['public_id'] for product in products][0:2] == [
        PUBLIC_IDS[0],
        PUBLIC_IDS[3],
    ]


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.now('2022-01-01T12:00:00+0000')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[0]),
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[3]),
            ],
        ),
    ],
)
@pytest.mark.config(
    EATS_ADVERTS_GOODS_YT_LOG_SETTINGS={'is_auction_log_enabled': True},
)
@experiments.make_promo_sorts_experiment(
    promotions=[PROMOTION_NAME], consumer=GET_CATEGORIES_CONSUMER,
)
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@pytest.mark.redis_store(
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:{utils.DISCOUNT_CATEGORY_ID}',  # noqa: E501
        '0.00004',
        'item_id_1',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:{utils.DISCOUNT_CATEGORY_ID}',  # noqa: E501
        '0.00003',
        'item_id_2',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:{utils.DISCOUNT_CATEGORY_ID}',  # noqa: E501
        '0.00002',
        'item_id_3',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:{utils.DISCOUNT_CATEGORY_ID}',  # noqa: E501
        '0.00001',
        'item_id_4',
    ],
)
@experiments.products_scoring()
async def test_promo_sorts_discount_get_categories(
        taxi_eats_products,
        load_json,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_v1_categories_context,
        mockserver,
        handlers_version,
        cache_add_discount_product,
        add_default_product_mapping,
        redis_store,
        add_place_products_mapping,
):
    # EDACAT-2821: Проверяет рекламные сортировки в категории
    # с cкидками в ручке get-categories
    add_default_product_mapping()
    for i, public_id in enumerate(PUBLIC_IDS):
        mock_nomenclature_v2_details_context.add_product(
            public_id, price=120, promo_price=100, shipping_type='all',
        )
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=999, old_price=1000, in_stock=20,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id,
            name=f'item_{i + 1}',
            images=[{'url': 'url_1/{w}x{h}', 'sort_order': 0}],
        )
        cache_add_discount_product(f'item_id_{i + 1}')

    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request['categories'][0]['id'] = utils.DISCOUNT_CATEGORY_ID

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request,
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

    products = response.json()['categories'][0]['items']
    assert len(products) == 4
    assert [product['public_id'] for product in products][0:2] == [
        PUBLIC_IDS[0],
        PUBLIC_IDS[3],
    ]


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[0]),
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[3]),
            ],
        ),
    ],
)
@pytest.mark.config(
    EATS_ADVERTS_GOODS_YT_LOG_SETTINGS={'is_auction_log_enabled': True},
)
@experiments.make_promo_sorts_experiment(
    promotions=[PROMOTION_NAME], consumer=GET_CATEGORIES_CONSUMER,
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS={'enable_cross_brand_order_history_storage': True},
)
@experiments.repeat_category('v2', 'Мои покупки')
@experiments.products_scoring()
async def test_promo_sorts_repeat_category(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_nomenclature_v2_details_context,
        make_public_by_sku_id_response,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_v1_categories_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # EDACAT-2821: проверяется что если вставить в старый тест repeat категорий
    # рекламные сортировки то ничего не поменяется
    add_default_product_mapping()

    for public_id in PUBLIC_IDS:
        mock_nomenclature_v2_details_context.add_product(
            public_id, shipping_type='all', price=10,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id,
            measure={'unit': 'KGRM', 'value': 1},
            name='item_4',
            images=[],
            description_general='ghi',
        )
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[0], 2,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[1], 4,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[2], 1,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[3], 3,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 10,
                },
            ],
        },
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == load_json('get_categories_response.json')
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_nomenclature_v1_categories_context.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_v1_categories_context.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1

    assert mock_retail_categories_brand_orders_history.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.now('2022-01-01T12:00:00+0000')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion=PROMOTION_NAME,
            products=[
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[0]),
                eats_adverts_goods.types.Product(product_id=PUBLIC_IDS[3]),
            ],
        ),
    ],
)
@pytest.mark.config(
    EATS_ADVERTS_GOODS_YT_LOG_SETTINGS={'is_auction_log_enabled': True},
)
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@pytest.mark.redis_store(
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:1',  # noqa: E501
        '0.00004',
        'item_id_1',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:1',  # noqa: E501
        '0.00003',
        'item_id_2',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:1',  # noqa: E501
        '0.00002',
        'item_id_3',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:{utils.PLACE_ID}:1',  # noqa: E501
        '0.00001',
        'item_id_4',
    ],
)
@pytest.mark.parametrize(
    'is_get_categories_consumer',
    [
        pytest.param(
            True,
            id='get-categories_consumer',
            marks=[
                experiments.make_promo_sorts_experiment(
                    promotions=[PROMOTION_NAME],
                    consumer=GET_CATEGORIES_CONSUMER,
                ),
            ],
        ),
        pytest.param(
            False,
            id='no_get-categories_consumer',
            marks=[
                experiments.make_promo_sorts_experiment(
                    promotions=[PROMOTION_NAME],
                ),
            ],
        ),
    ],
)
@experiments.products_scoring()
async def test_promo_sorts_basic_get_categories(
        taxi_eats_products,
        load_json,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_v1_categories_context,
        mockserver,
        handlers_version,
        cache_add_discount_product,
        add_default_product_mapping,
        add_place_products_mapping,
        is_get_categories_consumer,
):
    # EDACAT-2821: Проверяет рекламные сортировки в обычных категориях
    # для консьюмера eats_products/get_categories
    # при указании другого консьюмрера сортировки в get-categories
    # не должны применятся
    for i, public_id in enumerate(PUBLIC_IDS):
        add_place_products_mapping(
            [
                conftest.ProductMapping(
                    origin_id=f'item_id_{i + 1}',
                    public_id=public_id,
                    core_id=i + 1,
                ),
            ],
        )
        mock_nomenclature_v2_details_context.add_product(
            public_id, price=120, shipping_type='all',
        )
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=999, in_stock=20,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id,
            name=f'item_{i + 1}',
            images=[{'url': 'url_1/{w}x{h}', 'sort_order': 0}],
        )

    mock_nomenclature_v1_categories_context.add_category(
        public_id='1', name='name_1',
    )
    mock_nomenclature_v1_categories_context.add_category(
        public_id='2', name='name_1',
    )
    mock_nomenclature_get_parent_context.add_category(id_='1', parent_id='2')

    request = copy.deepcopy(CATEGORIES_BASE_REQUEST)
    request['categories'][0]['id'] = 1

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request,
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

    products = response.json()['categories'][0]['items']
    if is_get_categories_consumer:
        assert [product['public_id'] for product in products][0:2] == [
            PUBLIC_IDS[0],
            PUBLIC_IDS[3],
        ]
    else:
        assert [product['public_id'] for product in products] == [
            PUBLIC_IDS[0],
            PUBLIC_IDS[1],
            PUBLIC_IDS[2],
            PUBLIC_IDS[3],
        ]


@pytest.mark.parametrize(
    'position',
    [
        pytest.param(None, marks=experiments.FEW_SORTS_ENABLED),
        pytest.param(
            'before_filters',
            marks=experiments.few_sorts_enabled('before_filters'),
        ),
        pytest.param(
            'after_filters',
            marks=experiments.few_sorts_enabled('after_filters'),
        ),
    ],
)
async def test_sort_types_block_position(
        taxi_eats_products, mock_nomenclature_v1_categories_context, position,
):
    """
    Тест проверяет, что sorts.position корректно устанавливается из конфига
    """
    mock_nomenclature_v1_categories_context.add_category(
        public_id='1', name='name_1',
    )

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request,
    )

    assert response.status_code == 200
    for item in response.json()['payload']['categories']:
        assert item['sorts']['position'] == position
