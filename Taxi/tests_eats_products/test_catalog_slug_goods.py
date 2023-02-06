# pylint: disable=too-many-lines
import copy

import pytest

from tests_eats_products import categories as cats
from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

PLACE_SLUG = 'slug'
PLACE_ID = 1
BRAND_ID = 1
PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': PLACE_SLUG}

PICTURE_URL_SUFFIX = '/{w}x{h}'

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
]

DYNAMIC_CONFIG = utils.dynamic_categories_config(
    discount_enabled=True,
    repeat_enabled=True,
    popular_enabled=True,
    cashback_enabled=True,
    repeat_this_brand_enabled=True,
    repeat_other_brands_enabled=True,
)

PARAMETRIZE_INTEGRATION_VERSION = pytest.mark.parametrize(
    'nmn_integration_version', ['v1', 'v2'],
)

PARAMETRIZE_OVERRIDING_SHOW_IN = pytest.mark.parametrize(
    'overriding_show_in',
    [
        pytest.param(None),
        pytest.param(
            ['categories_carousel'],
            marks=experiments.categories_show_in_overrides(
                ['categories_carousel'],
            ),
        ),
        pytest.param(
            ['categories_carousel', 'banner_carousel'],
            marks=experiments.categories_show_in_overrides(
                ['categories_carousel', 'banner_carousel'],
            ),
        ),
        pytest.param(
            ['horizontal_carousel'],
            marks=experiments.categories_show_in_overrides(
                ['horizontal_carousel'],
            ),
        ),
        pytest.param(
            ['banner_carousel', 'horizontal_carousel'],
            marks=experiments.categories_show_in_overrides(
                ['banner_carousel', 'horizontal_carousel'],
            ),
        ),
    ],
)

PARAMETRIZE_OVERRIDING_SORT_ORDER = pytest.mark.parametrize(
    'expected_category_order',
    [
        pytest.param(
            [
                utils.REPEAT_CATEGORY_ID,
                utils.DISCOUNT_CATEGORY_ID,
                utils.POPULAR_CATEGORY_ID,
                utils.CASHBACK_CATEGORY_ID,
            ],
            marks=experiments.categories_position_sort_order(
                categories=[
                    {'id': utils.REPEAT_CATEGORY_ID, 'sort_order': None},
                    {'id': utils.DISCOUNT_CATEGORY_ID, 'sort_order': None},
                    {'id': utils.POPULAR_CATEGORY_ID, 'sort_order': None},
                    {'id': utils.CASHBACK_CATEGORY_ID, 'sort_order': None},
                ],
            ),
        ),
        pytest.param(
            [
                utils.REPEAT_CATEGORY_ID,
                utils.DISCOUNT_CATEGORY_ID,
                utils.POPULAR_CATEGORY_ID,
                utils.CASHBACK_CATEGORY_ID,
            ],
            marks=experiments.categories_position_sort_order(
                categories=[
                    {'id': utils.REPEAT_CATEGORY_ID, 'sort_order': 0},
                    {'id': utils.DISCOUNT_CATEGORY_ID, 'sort_order': 0},
                    {'id': utils.POPULAR_CATEGORY_ID, 'sort_order': 0},
                    {'id': utils.CASHBACK_CATEGORY_ID, 'sort_order': 0},
                ],
            ),
        ),
        pytest.param(
            [
                utils.DISCOUNT_CATEGORY_ID,
                utils.REPEAT_CATEGORY_ID,
                utils.POPULAR_CATEGORY_ID,
                utils.CASHBACK_CATEGORY_ID,
            ],
            marks=experiments.categories_position_sort_order(
                categories=[
                    {'id': utils.REPEAT_CATEGORY_ID, 'sort_order': None},
                    {'id': utils.DISCOUNT_CATEGORY_ID, 'sort_order': 1},
                    {'id': utils.POPULAR_CATEGORY_ID, 'sort_order': None},
                ],
            ),
        ),
        pytest.param(
            [
                utils.CASHBACK_CATEGORY_ID,
                utils.POPULAR_CATEGORY_ID,
                utils.DISCOUNT_CATEGORY_ID,
                utils.REPEAT_CATEGORY_ID,
            ],
            marks=experiments.categories_position_sort_order(
                categories=[
                    {'id': utils.REPEAT_CATEGORY_ID, 'sort_order': 4},
                    {'id': utils.DISCOUNT_CATEGORY_ID, 'sort_order': 3},
                    {'id': utils.POPULAR_CATEGORY_ID, 'sort_order': 2},
                    {'id': utils.CASHBACK_CATEGORY_ID, 'sort_order': 1},
                ],
            ),
        ),
        pytest.param(
            [
                utils.REPEAT_CATEGORY_ID,
                utils.DISCOUNT_CATEGORY_ID,
                utils.POPULAR_CATEGORY_ID,
                utils.CASHBACK_CATEGORY_ID,
            ],
            marks=experiments.categories_position_sort_order(
                categories=[
                    {'id': utils.REPEAT_CATEGORY_ID, 'sort_order': 1},
                    {'id': utils.DISCOUNT_CATEGORY_ID, 'sort_order': 2},
                    {'id': utils.POPULAR_CATEGORY_ID, 'sort_order': 3},
                    {'id': utils.CASHBACK_CATEGORY_ID, 'sort_order': 4},
                ],
            ),
        ),
        pytest.param(
            [
                utils.REPEAT_CATEGORY_ID,
                utils.DISCOUNT_CATEGORY_ID,
                utils.POPULAR_CATEGORY_ID,
                utils.CASHBACK_CATEGORY_ID,
            ],
            marks=experiments.categories_position_sort_order(
                categories=[
                    {'id': utils.REPEAT_CATEGORY_ID, 'sort_order': 1},
                    {'id': utils.DISCOUNT_CATEGORY_ID, 'sort_order': 2},
                    {'id': utils.POPULAR_CATEGORY_ID, 'sort_order': 3},
                ],
            ),
        ),
    ],
)


async def get_goods_response(taxi_eats_products, params: dict, headers=None):
    body = {**params, 'slug': PLACE_SLUG}
    return await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=body, headers=headers or {},
    )


async def test_catalog_slug_goods_404_no_categories(
        mock_nomenclature_for_v2_menu_goods,
):
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    mock_nomenclature_context.set_status(status_code=404)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature_context.set_place(place)
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        request, integration_version='v1',
    )
    assert response.status_code == 404


@PARAMETRIZE_INTEGRATION_VERSION
async def test_x_platform_and_x_app_version(
        taxi_eats_products, mockserver, nmn_integration_version,
):
    headers = {
        'X-AppMetrica-DeviceId': 'device_id',
        'x-platform': 'android_app',
        'x-app-version': '12.11.12',
        'X-Eats-User': 'user_id=456',
    }

    def assert_headers(request):
        assert request.headers['x-platform'] == headers['x-platform']
        assert request.headers['x-app-version'] == headers['x-app-version']
        assert (
            request.headers['X-AppMetrica-DeviceId']
            == headers['X-AppMetrica-DeviceId']
        )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        assert_headers(request)

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_PLACE_CATEGORIES_GET_CHILDREN,
    )
    def _mock_nmn_categories(request):
        assert_headers(request)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PLACES_CATEGORIES)
    def _mock_nmn_places_categories(request):
        assert_headers(request)

    await get_goods_response(
        taxi_eats_products, PRODUCTS_BASE_REQUEST, headers,
    )


@experiments.repeat_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_auth_context_to_v2_assortment_details(
        taxi_eats_products,
        mockserver,
        mock_retail_categories_brand_orders_history,
):
    products_headers = {
        'X-AppMetrica-DeviceId': 'device_id',
        'x-platform': 'android_app',
        'x-app-version': '12.11.12',
        'X-Eats-User': 'user_id=456',
    }
    request = {'shippingType': 'pickup', 'category': utils.REPEAT_CATEGORY_ID}

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature(request):
        assert (
            request.headers['X-AppMetrica-DeviceId']
            == products_headers['X-AppMetrica-DeviceId']
        )
        assert request.headers['x-platform'] == products_headers['x-platform']
        assert (
            request.headers['x-app-version']
            == products_headers['x-app-version']
        )

    await get_goods_response(taxi_eats_products, request, products_headers)
    assert _mock_eats_nomenclature.has_calls
    assert mock_retail_categories_brand_orders_history.times_called == 1


@experiments.discount_category()
async def test_auth_context_discount_category_to_place_products(
        taxi_eats_products,
        mockserver,
        cache_add_discount_product,
        add_default_product_mapping,
):
    """
    Пользовательские хедеры пробрасываются в ручки номенклатуры
    в категории Скидки
    """
    cache_add_discount_product('item_id_1')
    add_default_product_mapping()
    products_headers = {
        'X-AppMetrica-DeviceId': 'device_id',
        'x-platform': 'android_app',
        'x-app-version': '12.11.12',
        'X-Eats-User': 'user_id=456',
    }
    request = {
        'shippingType': 'pickup',
        'category': utils.DISCOUNT_CATEGORY_ID,
    }

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PLACE_PRODUCTS_INFO)
    def mock_dynamic_info(request):
        assert (
            request.headers['X-AppMetrica-DeviceId']
            == products_headers['X-AppMetrica-DeviceId']
        )
        assert request.headers['x-platform'] == products_headers['x-platform']
        assert (
            request.headers['x-app-version']
            == products_headers['x-app-version']
        )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS_INFO)
    def mock_static_info(request):
        assert (
            request.headers['X-AppMetrica-DeviceId']
            == products_headers['X-AppMetrica-DeviceId']
        )
        assert request.headers['x-platform'] == products_headers['x-platform']
        assert (
            request.headers['x-app-version']
            == products_headers['x-app-version']
        )

    await get_goods_response(taxi_eats_products, request, products_headers)
    assert mock_dynamic_info.has_calls
    assert mock_static_info.has_calls


@pytest.mark.parametrize(
    'category_origin_id, max_depth, category_id, name',
    [
        ('7', None, 107, 'Маски'),
        ('4', 3, 104, 'Здоровье'),
        ('3', None, 103, 'Хлеб'),
        ('3', 4, 103, 'Хлеб'),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_no_available_products_in_category(
        mock_nomenclature_for_v2_menu_goods,
        # parametrize
        category_origin_id,
        max_depth,
        category_id,
        name,
        nmn_integration_version,
):
    # Тест проверяет, что категория возвращается,
    # даже если в ней (и в ее подкатегориях) нет товаров.
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id=str(category_id), name=name, origin_id=category_origin_id,
    )
    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_context.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        request, integration_version=nmn_integration_version,
    )

    categories = response.json()['payload']['categories']
    assert categories
    category_ids = set()
    for category in categories:
        category_ids.add(category['id'])
    assert category_id in category_ids


@pytest.mark.parametrize(
    'category_origin_id, max_depth, category_id',
    [('5', None, 105), ('5', 3, 105)],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_unavailable_requested_category(
        mock_nomenclature_for_v2_menu_goods,
        # parametrize
        category_origin_id,
        max_depth,
        category_id,
        nmn_integration_version,
):
    # Тест проверяет, что если запрашиваемая категория недоступна
    # в сервисе номенклатур, то возвращаем 404.
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id=str(category_id),
        name='Овощи',
        origin_id=category_origin_id,
        is_available=False,
    )

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_context.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        request, integration_version=nmn_integration_version,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'has_at_least_one_available, nmn_integration_version',
    [(True, 'v1'), (False, 'v1'), (False, 'v2'), (True, 'v2')],
)
async def test_unavailable_requested_by_public_id_category(
        mock_nomenclature_for_v2_menu_goods,
        add_default_product_mapping,
        # parametrize
        has_at_least_one_available,
        nmn_integration_version,
):
    # Тест проверяет, что если среди запрашиваемых категорий все недоступны
    # в сервисе номенклатур, то возвращаем 404.
    # Иначе возвращаем нормальный ответ.
    add_default_product_mapping()
    category_origin_id_unavailable = 'category_id_5'
    category_origin_id_available = 'category_id_4'
    public_id_unavailable = 105
    public_id_available = 104

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat_5 = conftest.CategoryMenuGoods(
        public_id=str(public_id_unavailable),
        name='Овощи',
        origin_id=category_origin_id_unavailable,
        is_available=False,
    )
    root_cat_4 = conftest.CategoryMenuGoods(
        public_id=str(public_id_available),
        name='Здоровье',
        origin_id=category_origin_id_available,
        is_available=True,
    )
    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat_5)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    if has_at_least_one_available:
        place.add_root_category(root_cat_4)
    else:
        request['category'] = public_id_unavailable

    mock_nomenclature_context.set_place(place)
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        request, integration_version=nmn_integration_version,
    )

    if has_at_least_one_available:
        assert response.status_code == 200
        response_categories = response.json()['payload']['categories']
        assert len(response_categories) == 1
        assert response_categories[0]['id'] == public_id_available
    else:
        assert response.status_code == 404


@pytest.mark.parametrize(
    'category_origin_id, max_depth, category_id',
    [('2', None, 102), ('2', 2, 102), ('2', 4, 102)],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_category_with_some_unavailable_products(
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        # parametrize
        category_origin_id,
        max_depth,
        category_id,
        nmn_integration_version,
):
    # Тест проверяет, что возвращаются только доступные товары.
    add_default_product_mapping()
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id=str(category_id),
        name='Молочные продукты',
        origin_id=category_origin_id,
    )

    root_cat.add_product(cats.DEFAULT_PRODUCTS['item_id_6'], sort_order=1)
    root_cat.add_product(cats.DEFAULT_PRODUCTS['item_id_7'], sort_order=2)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_context.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        request, integration_version=nmn_integration_version,
    )
    response_categories = response.json()['payload']['categories']
    assert len(response_categories) == 1
    assert response_categories[0]['id'] == category_id
    assert len(response_categories[0]['items']) == 1
    assert response_categories[0]['items'][0]['id'] == 6


@pytest.mark.parametrize(
    'category_origin_id, max_depth, category_id',
    [('6', None, 106), ('6', 3, 106), ('6', 5, 106)],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_products_order(
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        # parametrize
        category_origin_id,
        max_depth,
        category_id,
        nmn_integration_version,
):
    # Тест проверяет, что товары возвращаются в отсортированном порядке.
    add_default_product_mapping()

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id=str(category_id),
        name='Фрукты',
        origin_id=category_origin_id,
    )
    root_cat.add_product(cats.DEFAULT_PRODUCTS['item_id_3'], sort_order=3)
    root_cat.add_product(cats.DEFAULT_PRODUCTS['item_id_4'], sort_order=1)
    root_cat.add_product(cats.DEFAULT_PRODUCTS['item_id_5'], sort_order=2)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_context.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        request, integration_version=nmn_integration_version,
    )

    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    products = categories[0]['items']
    assert len(products) == 3
    expected_products = [4, 5, 3]
    for i in range(3):
        assert products[i]['id'] == expected_products[i]


@PARAMETRIZE_INTEGRATION_VERSION
async def test_get_all_categories(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    # Тест проверяет, что если не задан входной параметр 'category',
    # то возвращаются все доступные категории и без товаров.
    # Категории отсортированы сверху вниз и по 'sort_order'.

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    root_category_1 = conftest.CategoryMenuGoods(
        public_id='101', name='name', origin_id='1', sort_order=3,
    )
    root_category_2 = conftest.CategoryMenuGoods(
        public_id='102', name='name', origin_id='2', sort_order=4,
    )
    root_category_3 = conftest.CategoryMenuGoods(
        public_id='103', name='name', origin_id='3', sort_order=5,
    )
    root_category_4 = conftest.CategoryMenuGoods(
        public_id='104', name='name', origin_id='4', sort_order=6,
    )
    category_6 = conftest.CategoryMenuGoods(
        public_id='106', name='name', origin_id='6', sort_order=2,
    )
    root_category_1.add_child_category(category_6)
    category_7 = conftest.CategoryMenuGoods(
        public_id='107', name='name', origin_id='7', sort_order=7,
    )
    root_category_4.add_child_category(category_7)

    place.add_root_category(root_category_1)
    place.add_root_category(root_category_2)
    place.add_root_category(root_category_3)
    place.add_root_category(root_category_4)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, nmn_integration_version,
        )
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 6
    category_ids = []
    for category in categories:
        assert not category['items']
        category_ids.append(category['id'])
    expected_category_ids = [101, 102, 103, 104, 106, 107]
    assert category_ids == expected_category_ids


@PARAMETRIZE_INTEGRATION_VERSION
async def test_content_get_all_categories(
        load_json,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    """
    Тест проверяет содержимое всего ответа,
    когда не задан входной параметр 'category'.
    """
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    images = [('image_url_1', 1)]
    root_category_1 = conftest.CategoryMenuGoods(
        public_id='101',
        name='Овощи и фрукты',
        origin_id='1',
        sort_order=3,
        images=images,
    )
    root_category_2 = conftest.CategoryMenuGoods(
        public_id='102',
        name='Молочные продукты',
        origin_id='2',
        sort_order=4,
        images=images,
    )
    root_category_3 = conftest.CategoryMenuGoods(
        public_id='103',
        name='Хлеб',
        origin_id='3',
        sort_order=5,
        images=images,
    )
    root_category_4 = conftest.CategoryMenuGoods(
        public_id='104',
        name='Здоровье',
        origin_id='4',
        sort_order=6,
        images=images,
    )
    category_6 = conftest.CategoryMenuGoods(
        public_id='106',
        name='Фрукты',
        origin_id='6',
        sort_order=2,
        images=images,
    )
    root_category_1.add_child_category(category_6)
    category_7 = conftest.CategoryMenuGoods(
        public_id='107',
        name='Маски',
        origin_id='7',
        sort_order=7,
        images=images,
    )
    root_category_4.add_child_category(category_7)

    place.add_root_category(root_category_1)
    place.add_root_category(root_category_2)
    place.add_root_category(root_category_3)
    place.add_root_category(root_category_4)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3

    expected_response = {'payload': {'categories': []}, 'meta': None}
    category_ids = [1, 2, 3, 4, 6, 7]
    for category_id in category_ids:
        expected_category = load_json(
            'products-category-' + str(category_id) + '.json',
        )
        expected_category['items'] = []
        expected_response['payload']['categories'].append(expected_category)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, nmn_integration_version,
        )
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@PARAMETRIZE_INTEGRATION_VERSION
async def test_content_with_products(
        load_json,
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет содержимое всего ответа для v1,
    # когда задан входной параметр 'category'.
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 101
    request['maxDepth'] = 3

    expected_response = {
        'payload': {
            'categories': [
                load_json('products-category-1.json'),
                load_json('products-category-6.json'),
            ],
            'goods_count': 3,
        },
        'meta': None,
    }

    root_cat = cats.make_category(101)
    root_cat.add_child_category(cats.make_category(106))
    root_cat.add_child_category(cats.make_category(105))

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'category_id, max_depth',
    [
        (101, 1),
        (102, 1),
        (103, 1),
        (104, 1),
        (106, 1),
        (107, 1),
        (101, 10),
        (102, 10),
        (103, 10),
        (104, 10),
        (106, 10),
        (107, 10),
        (101, None),
        (102, None),
        (103, None),
        (104, None),
        (106, None),
        (107, None),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_meta_with_input_category(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        category_id,
        max_depth,
):
    # Тест проверяет, что на верхнем уровне ответа
    # есть поле meta со значением null,
    # если запрашивается конкретная категория.
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    root_cat = cats.make_category(category_id)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert 'meta' in response.json()
    assert response.json()['meta'] is None


@PARAMETRIZE_INTEGRATION_VERSION
async def test_meta_without_input_category(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    # Тест проверяет, что на верхнем уровне ответа
    # есть поле meta со значением null,
    # когда не задан входной параметр 'category'.
    root_cat = cats.make_category(101)
    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert 'meta' in response.json()
    assert response.json()['meta'] is None


@pytest.mark.parametrize(
    'category_id, max_depth',
    [
        (101, 1),
        (102, 1),
        (103, 1),
        (104, 1),
        (106, 1),
        (107, 1),
        (101, 10),
        (102, 10),
        (103, 10),
        (104, 10),
        (106, 10),
        (107, 10),
        (101, None),
        (102, None),
        (103, None),
        (104, None),
        (106, None),
        (107, None),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_features_with_input_category(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        category_id,
        max_depth,
):
    """
    Тест проверяет, что поле payload.features не выводится,
    если оно пустое и запрашивается конкретная категория.
    """
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    root_cat = cats.make_category(category_id)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert 'features' not in response.json()['payload']


@PARAMETRIZE_INTEGRATION_VERSION
async def test_features_without_input_category(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    """
    Тест проверяет, что поле payload.features не выводится,
    если оно пустое и не задан входной параметр 'category'.
    """
    root_cat = cats.make_category(101)
    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert 'features' not in response.json()['payload']


@pytest.mark.parametrize(
    'category_id, max_depth',
    [
        (101, 1),
        (102, 1),
        (103, 1),
        (104, 1),
        (106, 1),
        (107, 1),
        (101, 10),
        (102, 10),
        (103, 10),
        (104, 10),
        (106, 10),
        (107, 10),
        (101, None),
        (102, None),
        (103, None),
        (104, None),
        (106, None),
        (107, None),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_gallery_with_input_category(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        category_id,
        max_depth,
):
    # Тест проверяет, что у категорий есть непустое поле gallery,
    # если запрашивается конкретная категория и
    # сервис номенклатур возвращает непустое поле images.
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    root_cat = cats.make_category(category_id)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200
    assert 'categories' in response.json()['payload']
    for category in response.json()['payload']['categories']:
        assert 'gallery' in category
        assert category['gallery']


@PARAMETRIZE_INTEGRATION_VERSION
async def test_gallery_without_input_category(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    """
    Тест проверяет, что у категорий есть непустое поле gallery,
    если не задан входной параметр 'category' и
    сервис номенклатур возвращает непустое поле images.
    """
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    images = [('image_url_1', 1)]
    root_category_1 = conftest.CategoryMenuGoods(
        public_id='101',
        name='Овощи и фрукты',
        origin_id='1',
        sort_order=3,
        images=images,
    )
    category_6 = conftest.CategoryMenuGoods(
        public_id='106',
        name='Фрукты',
        origin_id='6',
        sort_order=2,
        images=images,
    )
    root_category_1.add_child_category(category_6)

    place.add_root_category(root_category_1)
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    for category in response.json()['payload']['categories']:
        assert 'gallery' in category
        assert category['gallery']


@pytest.mark.parametrize(
    'category_id, max_depth',
    [
        (101, 1),
        (102, 1),
        (103, 1),
        (104, 1),
        (106, 1),
        (107, 1),
        (101, 10),
        (102, 10),
        (103, 10),
        (104, 10),
        (106, 10),
        (107, 10),
        (101, None),
        (102, None),
        (103, None),
        (104, None),
        (106, None),
        (107, None),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_picture_url_with_input_category(
        category_id,
        max_depth,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет, что у категорий и товаров
    # урл изображения заканчивается на "/{w}x{h}",
    # если запрашивается конкретная категория.
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category_id
    request['maxDepth'] = max_depth

    root_cat = cats.make_category(category_id)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert 'categories' in response.json()['payload']
    for category in response.json()['payload']['categories']:
        assert 'gallery' in category
        for picture in category['gallery']:
            assert 'url' in picture
            assert picture['url'].endswith(PICTURE_URL_SUFFIX)
        assert 'items' in category
        for item in category['items']:
            assert 'picture' in item
            if item['picture']:
                assert 'url' in item['picture']
                assert item['picture']['url'].endswith(PICTURE_URL_SUFFIX)


@PARAMETRIZE_INTEGRATION_VERSION
async def test_picture_url_without_input_category(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    """
    Тест проверяет, что у категорий
    урл изображения заканчивается на "/{w}x{h}",
    если не задан входной параметр 'category'.
    """
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    images = [('image_url_1', 1)]
    root_category_1 = conftest.CategoryMenuGoods(
        public_id='101',
        name='Овощи и фрукты',
        origin_id='1',
        sort_order=3,
        images=images,
    )
    category_6 = conftest.CategoryMenuGoods(
        public_id='106',
        name='Фрукты',
        origin_id='6',
        sort_order=2,
        images=images,
    )
    root_category_1.add_child_category(category_6)

    place.add_root_category(root_category_1)
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert 'categories' in response.json()['payload']
    for category in response.json()['payload']['categories']:
        assert 'gallery' in category
        for picture in category['gallery']:
            assert 'url' in picture
            assert picture['url'].endswith(PICTURE_URL_SUFFIX)


@PARAMETRIZE_INTEGRATION_VERSION
async def test_content_with_products_and_discount_promo(
        load_json,
        taxi_config,
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # Тест проверяет содержимое всего ответа,
    # когда включен акционный шильдик "Скидка для магазинов".
    add_default_product_mapping()
    settings = {'discount_promo': {'enabled': True}}
    taxi_config.set(EATS_PRODUCTS_SETTINGS=settings)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 101
    request['maxDepth'] = 3

    expected_response = {
        'payload': {
            'categories': [
                load_json('products-category-1.json'),
                load_json('products-category-6-with-promo-types.json'),
            ],
            'goods_count': 3,
        },
        'meta': None,
    }

    root_cat = cats.make_category(101)
    root_cat.add_child_category(cats.make_category(105))
    root_cat.add_child_category(cats.make_category(106))

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@PARAMETRIZE_INTEGRATION_VERSION
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'discount_promo': {'enabled': True}},
)
async def test_percentage_promo_prices(
        load_json,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_default_product_mapping,
):
    # Тест проверяет правильное заполнение поля text в promoTypes продуктов
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 101
    request['maxDepth'] = 3

    expected_response = {
        'payload': {
            'categories': [
                load_json('products-category-1.json'),
                load_json('products-category-6-discounts.json'),
            ],
            'goods_count': 3,
        },
        'meta': None,
    }

    root_cat = cats.make_category(101)
    root_cat.add_child_category(cats.make_category(106, discount=True))

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert response.json() == expected_response


@PARAMETRIZE_INTEGRATION_VERSION
async def test_content_with_pictures_sort_order(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_default_product_mapping,
):
    # Тест проверяет то, что при получении ответа из сервиса номенклатуры
    # для продукта выбирается картинка с наибольшим числом sort_order
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 108
    request['maxDepth'] = 3

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(cats.make_category(108))
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert (
        response.json()['payload']['categories'][0]['items'][0]['picture'][
            'url'
        ]
        == 'url_2/{w}x{h}'
    )


@PARAMETRIZE_INTEGRATION_VERSION
async def test_category_pictures(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    # Тест проверяет, что у категорий возвращается картинка
    # с наибольшим sort_order
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 108
    request['maxDepth'] = 3

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(cats.make_category(108))
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    expected_images = [{'url': 'image_url_3/{w}x{h}', 'type': 'tile'}]
    assert response.status_code == 200
    assert (
        response.json()['payload']['categories'][0]['gallery']
        == expected_images
    )


@pytest.mark.parametrize('category_id', [200, 300, 400])
@pytest.mark.pgsql('eats_products', files=['pg_eats_products.sql'])
async def test_request_custom_subcategory(
        taxi_eats_products, mockserver, load_json, category_id,
):
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    request['category'] = category_id

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        response = load_json('nomenclature-custom-categories.json')
        for category in response['categories']:
            if category['public_id'] == category_id:
                return {'categories': [category]}
        return {'categories': []}

    response = await get_goods_response(taxi_eats_products, request)
    assert response.status_code == 200

    # Category shouldn't have parentId
    category = response.json()['payload']['categories'][0]
    assert not category['parentId']


@PARAMETRIZE_INTEGRATION_VERSION
async def test_custom_categories_products_mapping(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_place_products_mapping,
):
    # Insert some additional mapping for products.
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_2',
                core_id=9,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            ),
            conftest.ProductMapping(
                origin_id='item_id_4',
                core_id=11,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            ),
        ],
    )

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    request['category'] = 100

    root_category = conftest.CategoryMenuGoods(
        public_id='100',
        name='Кастомная категория 1',
        origin_id='custom_category_id_1',
        category_type='custom_base',
    )

    category_2 = conftest.CategoryMenuGoods(
        public_id='200',
        name='Кастомная категория 2',
        origin_id='custom_category_id_2',
        category_type='custom_base',
    )

    category_2.add_product(
        conftest.ProductMenuGoods(
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b009',
            name='Яблоки',
            origin_id='item_id_8',
        ),
        3,
    )
    category_2.add_product(cats.DEFAULT_PRODUCTS['item_id_4'], 1)

    category_3 = conftest.CategoryMenuGoods(
        public_id='300',
        name='Кастомная категория 3',
        origin_id='custom_category_id_3',
        category_type='custom_base',
    )

    category_4 = conftest.CategoryMenuGoods(
        public_id='400',
        name='Кастомная категория 4',
        origin_id='custom_category_id_4',
        category_type='custom_base',
    )

    category_4.add_product(cats.DEFAULT_PRODUCTS['item_id_2'], 3)

    root_category.add_child_category(category_2)
    root_category.add_child_category(category_3)
    root_category.add_child_category(category_4)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_category)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200

    # Check products mapping.
    possible_products_mapping = {
        'Яблоки': {8},
        'Апельсины': {4, 11},
        'Помидоры': {2, 9, 10},
    }

    items_in_categories = {200: 1, 100: 0, 300: 0, 400: 1}
    categories = response.json()['payload']['categories']
    assert len(categories) == 4
    for category in categories:
        items = category['items']
        assert len(items) == items_in_categories[category['id']]
        for item in items:
            assert item['id'] in possible_products_mapping[item['name']]


@PARAMETRIZE_INTEGRATION_VERSION
async def test_products_mapping(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_default_product_mapping,
):
    # Insert some additional mapping for products.
    add_default_product_mapping()

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    request['category'] = 101

    category = conftest.CategoryMenuGoods(
        public_id='101', name='Категория', origin_id='1',
    )

    category.add_product(cats.DEFAULT_PRODUCTS['item_id_3'], 3)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_4'], 1)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_5'], 2)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_1'], 1)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_2'], 2)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(category)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200

    # Check products mapping.
    possible_products_mapping = {
        'Огурцы': {1},
        'Помидоры': {2, 9, 10},
        'Яблоки': {3},
        'Апельсины': {4, 11},
        'Бананы': {5},
    }
    category = response.json()['payload']['categories'][0]
    assert len(category['items']) == 5
    for item in category['items']:
        assert item['id'] in possible_products_mapping[item['name']]


@PARAMETRIZE_INTEGRATION_VERSION
async def test_place_products_mapping(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_default_product_mapping,
):
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['maxDepth'] = 3
    request['category'] = 101

    category = conftest.CategoryMenuGoods(
        public_id='101', name='Категория', origin_id='1',
    )

    category.add_product(cats.DEFAULT_PRODUCTS['item_id_3'], 3)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_4'], 1)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_5'], 2)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_1'], 1)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_2'], 2)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(category)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200

    # Check that product mapping is from place_products table.
    expected_products = {
        'Огурцы': 1,
        'Помидоры': 2,
        'Яблоки': 3,
        'Апельсины': 4,
        'Бананы': 5,
    }
    category = response.json()['payload']['categories'][0]
    products = {p['name']: p['id'] for p in category['items']}
    assert products == expected_products


@pytest.mark.parametrize('request_with_category', [False, True])
@PARAMETRIZE_INTEGRATION_VERSION
@pytest.mark.parametrize(
    'horizontal_carousel_show_in_enabled',
    [
        pytest.param(False),
        pytest.param(
            True, marks=experiments.HORIZONTAL_CAROUSEL_SHOW_IN_ENABLED(),
        ),
    ],
)
@pytest.mark.parametrize(
    ('category_type', 'show_in'),
    [
        ('custom_base', 'categories_carousel'),
        ('custom_promo', 'banner_carousel'),
        ('partner', 'categories_carousel'),
    ],
)
@PARAMETRIZE_OVERRIDING_SHOW_IN
async def test_category_types(
        mock_nomenclature_for_v2_menu_goods,
        horizontal_carousel_show_in_enabled,
        category_type,
        show_in,
        request_with_category,
        overriding_show_in,
        nmn_integration_version,
):
    """
        Тест проверяет выставление show_in. horizontal_carousel должно
        выставляться дополнительно в show_in для всех категорий,
        кроме баннеров. Также проверяется перезапись show_in из
        eats_products_categories_position_overrides в случае
        horizontal_carousel_show_in_enabled=True
    """
    root_cat = conftest.CategoryMenuGoods(
        public_id='101',
        name='Овощи и фрукты',
        origin_id='1',
        category_type=category_type,
    )

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    if request_with_category:
        request['category'] = 101
    request['maxDepth'] = 3

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200

    expected_show_in = [show_in]
    # кастомные категории без horizontal_carousel.
    # То есть там будет приходить [banner_carousel]
    is_banner_carousel = category_type == 'custom_promo'

    if (
            not request_with_category
            and horizontal_carousel_show_in_enabled
            and overriding_show_in
    ):
        expected_show_in = overriding_show_in
    elif horizontal_carousel_show_in_enabled and not is_banner_carousel:
        expected_show_in.append('horizontal_carousel')

    category = response.json()['payload']['categories'][0]
    assert set(category['show_in']) == set(expected_show_in)


@pytest.mark.parametrize(
    'horizontal_carousel_show_in_enabled',
    [
        pytest.param(False),
        pytest.param(
            True, marks=experiments.HORIZONTAL_CAROUSEL_SHOW_IN_ENABLED(),
        ),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=DYNAMIC_CONFIG)
@experiments.discount_category()
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.repeat_category()
@experiments.popular_category()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
@PARAMETRIZE_OVERRIDING_SHOW_IN
@PARAMETRIZE_INTEGRATION_VERSION
async def test_menu_goods_show_in_dynamic_categories(
        mock_v2_fetch_discounts_context,
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        horizontal_carousel_show_in_enabled,
        mock_retail_categories_brand_orders_history,
        overriding_show_in,
        nmn_integration_version,
):
    """
       Тест проверяет выставление horizontal_carousel в show_in
       для динамических категориях. Также проверяется перезапись
       show_in из eats_products_categories_position_overrides в
       случае horizontal_carousel_show_in_enabled=True
    """

    add_default_product_mapping()
    mock_retail_categories_brand_orders_history.add_default_products()

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=2,
    )

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST,
            nmn_integration_version,
            headers=utils.PRODUCTS_HEADERS,
        )
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 4

    assert {category['id'] for category in categories} == {
        utils.REPEAT_CATEGORY_ID,
        utils.DISCOUNT_CATEGORY_ID,
        utils.POPULAR_CATEGORY_ID,
        utils.CASHBACK_CATEGORY_ID,
    }

    expected_show_in = []
    if horizontal_carousel_show_in_enabled:
        if overriding_show_in:
            expected_show_in = overriding_show_in
        else:
            expected_show_in = ['horizontal_carousel']

    for category in categories:
        assert set(category['show_in']) == set(expected_show_in)


@experiments.HORIZONTAL_CAROUSEL_SHOW_IN_ENABLED
@pytest.mark.config(EATS_PRODUCTS_DYNAMIC_CATEGORIES=DYNAMIC_CONFIG)
@experiments.discount_category()
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.repeat_category()
@experiments.popular_category()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
@PARAMETRIZE_OVERRIDING_SORT_ORDER
@PARAMETRIZE_INTEGRATION_VERSION
async def test_menu_goods_sort_order_dynamic_categories(
        mock_v2_fetch_discounts_context,
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        mock_retail_categories_brand_orders_history,
        expected_category_order,
        nmn_integration_version,
):
    """
       Тест проверяет сортировку для динамических категорий.
        с использованием sort_order.
    """

    add_default_product_mapping()
    mock_retail_categories_brand_orders_history.add_default_products()

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=2,
    )

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST,
            nmn_integration_version,
            headers=utils.PRODUCTS_HEADERS,
        )
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert [
        category['id'] for category in categories
    ] == expected_category_order


@experiments.categories_position_sort_order(
    categories=[{'id': 5, 'sort_order': 4}],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_menu_goods_sort_order_nomenclature_categories(
        mock_nomenclature_for_v2_menu_goods,
        add_default_product_mapping,
        nmn_integration_version,
):
    """
        Проверяется, что при наличии sort_order для нединамических категорий
        это не влияет на их сортировку.
    """
    add_default_product_mapping()
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    category_1 = conftest.CategoryMenuGoods(
        public_id='5', name='name', origin_id='origin_id', sort_order=1,
    )
    place.add_root_category(category_1)
    category_2 = conftest.CategoryMenuGoods(
        public_id='6', name='name', origin_id='origin_id', sort_order=2,
    )
    place.add_root_category(category_2)
    category_3 = conftest.CategoryMenuGoods(
        public_id='7', name='name', origin_id='origin_id', sort_order=3,
    )
    place.add_root_category(category_3)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST, nmn_integration_version,
        )
    )
    categories = response.json()['payload']['categories']
    category_ids = [item['id'] for item in categories]
    assert category_ids == [5, 6, 7]


@pytest.mark.parametrize(
    'horizontal_carousel_show_in_enabled',
    [
        pytest.param(False),
        pytest.param(
            True, marks=experiments.HORIZONTAL_CAROUSEL_SHOW_IN_ENABLED(),
        ),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
@experiments.repeat_category('v2', 'Мои покупки')
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'enable_cross_brand_order_history_storage': True},
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
        repeat_this_brand_enabled=True,
        repeat_other_brands_enabled=True,
    ),
)
@PARAMETRIZE_OVERRIDING_SHOW_IN
async def test_menu_goods_show_in_repeat_categories(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        horizontal_carousel_show_in_enabled,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
        overriding_show_in,
        nmn_integration_version,
):
    """
       Тест проверяет выставление horizontal_carousel в show_in
       для "мои покупки" v2.
    """

    add_default_product_mapping()
    mock_retail_categories_brand_orders_history.add_default_products()

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST,
            nmn_integration_version,
            headers=utils.PRODUCTS_HEADERS,
        )
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1

    assert (
        mock_retail_categories_brand_orders_history.handler.times_called == 1
    )
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1

    assert {category['id'] for category in categories} == {
        utils.REPEAT_CATEGORY_ID,
    }

    expected_show_in = []
    if horizontal_carousel_show_in_enabled:
        if overriding_show_in:
            expected_show_in = overriding_show_in
        else:
            expected_show_in = ['horizontal_carousel']

    for category in categories:
        assert set(category['show_in']) == set(expected_show_in)


@PARAMETRIZE_INTEGRATION_VERSION
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'discount_promo': {'enabled': True}},
)
async def test_invalid_prices(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        load_json,
        add_default_product_mapping,
):
    # Тест проверяет, что если из номенклатуры пришли неправильные поля
    # price и old_price, то товар не считается акционным
    add_default_product_mapping()
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 101
    request['maxDepth'] = 3

    expected_response = {
        'payload': {
            'categories': [load_json('products-category-wrong-prices.json')],
            'goods_count': 2,
        },
        'meta': None,
    }

    category = conftest.CategoryMenuGoods(
        public_id='101',
        name='Фрукты',
        origin_id='1',
        images=[('image_url_1', 0)],
    )

    product_1 = copy.deepcopy(cats.DEFAULT_PRODUCTS['item_id_3'])
    product_1.old_price = 100
    product_1.price = 200
    product_1.description = 'Цена со скидкой больше обычной цены'
    product_2 = copy.deepcopy(cats.DEFAULT_PRODUCTS['item_id_5'])
    product_2.old_price = 100
    product_2.old_price = 100
    product_2.price = 100
    product_2.description = 'Одинаковые цены'

    category.add_product(product_1, 3)
    category.add_product(product_2, 2)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(category)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@PARAMETRIZE_INTEGRATION_VERSION
async def test_place_products_invalid_mapping(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_place_products_mapping,
):
    core_id = 123
    origin_1 = 'item_id_1'
    origin_2 = 'item_id_2'
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

    category = conftest.CategoryMenuGoods(
        public_id='1', name='Фрукты', origin_id='category_id_1',
    )

    category.add_product(cats.DEFAULT_PRODUCTS['item_id_1'], 0)
    category.add_product(cats.DEFAULT_PRODUCTS['item_id_2'], 0)
    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(category)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200
    items = response.json()['payload']['categories'][0]['items']
    assert len(items) == 1
    assert items[0]['id'] == core_id


@PARAMETRIZE_INTEGRATION_VERSION
@utils.PARAMETRIZE_WEIGHT_DATA_ROUNDING
@experiments.weight_data()
async def test_goods_weight_data_default_category(
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
        add_default_product_mapping,
        should_round_prices,
):
    # Проверяется, что есть весовые данные товара, если включен экперимент
    # в дефолтной категории
    add_default_product_mapping()

    category = conftest.CategoryMenuGoods(
        public_id='1', name='Фрукты', origin_id='category_id_1',
    )
    category.add_product(
        conftest.ProductMenuGoods(
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            origin_id='item_id_1',
            name='item_1',
            price=100,
            measure=(250, 'GRM'),
            is_catch_weight=True,
        ),
    )
    category.add_product(
        conftest.ProductMenuGoods(
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            origin_id='item_id_2',
            name='item_2',
            price=99,
            old_price=101,
            measure=(2, 'KGRM'),
            is_catch_weight=True,
        ),
    )
    # не весовой товар
    category.add_product(
        conftest.ProductMenuGoods(
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            origin_id='item_id_3',
            name='item_3',
            price=100,
        ),
    )
    # товар с невалидными весовыми данными
    category.add_product(
        conftest.ProductMenuGoods(
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            origin_id='item_id_4',
            name='item_4',
            price=100,
            measure=(2, 'unknown_unit'),
            is_catch_weight=True,
        ),
    )

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(category)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200
    items = response.json()['payload']['categories'][0]['items']
    assert items[0]['weight_data'] == {
        'price_per_kg': '400',
        'quantim_value_g': 250,
    }
    assert items[1]['weight_data'] == {
        'price_per_kg': '51' if should_round_prices else '50.5',
        'promo_price_per_kg': '50' if should_round_prices else '49.5',
        'quantim_value_g': 2000,
    }
    assert 'weight_data' not in items[2]
    assert 'weight_data' not in items[3]


@pytest.mark.parametrize(
    ['is_catch_weight', 'measure', 'expected_weight_data'],
    [
        pytest.param(
            True,
            {'unit': 'GRM', 'value': 250},
            {
                'price_per_kg': '400',
                'promo_price_per_kg': '200',
                'quantim_value_g': 250,
            },
            id='has_weight_data_grm',
        ),
        pytest.param(
            True,
            {'unit': 'KGRM', 'value': 2},
            {
                'price_per_kg': '50',
                'promo_price_per_kg': '25',
                'quantim_value_g': 2000,
            },
            id='has_weight_data_kgrm',
        ),
        pytest.param(False, None, None, id='no_catch_weight'),
        pytest.param(
            True,
            {'unit': 'unknown_unit', 'value': 2},
            None,
            id='unknown_unit',
        ),
    ],
)
@pytest.mark.parametrize(
    'category, handlers_v2',
    [
        pytest.param(utils.REPEAT_CATEGORY_ID, False),
        pytest.param(utils.DISCOUNT_CATEGORY_ID, True),
        pytest.param(utils.POPULAR_CATEGORY_ID, False),
        pytest.param(utils.CASHBACK_CATEGORY_ID, False),
    ],
)
@utils.PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION
@experiments.discount_category()
@experiments.repeat_category()
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.popular_category()
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
@experiments.weight_data()
async def test_goods_weight_data_dynamic_categories(
        taxi_eats_products,
        mock_nomenclature_v2_details_context,
        mock_v2_fetch_discounts_context,
        mock_v2_match_discounts_context,
        add_default_product_mapping,
        cache_add_discount_product,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_retail_categories_brand_orders_history,
        cashback_handles_version,
        category,
        is_catch_weight,
        measure,
        expected_weight_data,
        handlers_v2,
):
    # Проверяется, что есть весовые данные товара, если включен эксперимент
    # в динамических категориях
    product_public_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
    add_default_product_mapping()
    cache_add_discount_product('item_id_1')

    if handlers_v2:
        mock_nomenclature_static_info_context.add_product(
            product_public_id,
            is_catch_weight=is_catch_weight,
            measure=measure,
        )
        mock_nomenclature_dynamic_info_context.add_product(
            product_public_id, price=50, old_price=100,
        )
    else:
        mock_nomenclature_v2_details_context.add_product(
            product_public_id,
            price=100,
            promo_price=50,
            is_catch_weight=is_catch_weight,
            measure=measure,
        )
        mock_nomenclature_static_info_context.add_product(
            product_public_id,
            is_catch_weight=is_catch_weight,
            measure=measure,
        )
        mock_nomenclature_dynamic_info_context.add_product(
            product_public_id, price=50, old_price=100,
        )
    mock_v2_fetch_discounts_context.add_cashback_product(
        product_public_id, 'fraction', 20,
    )
    mock_retail_categories_brand_orders_history.add_default_products()

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = category

    response = await get_goods_response(
        taxi_eats_products, request, headers={'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 200
    items = response.json()['payload']['categories'][0]['items']
    assert len(items) == 1

    if expected_weight_data:
        assert items[0]['weight_data'] == expected_weight_data
    else:
        assert 'weight_data' not in items[0]
    assert mock_retail_categories_brand_orders_history.times_called == (
        1 if category == utils.REPEAT_CATEGORY_ID else 0
    )


@pytest.mark.parametrize(
    'menu_request',
    [
        pytest.param({'slug': '&'}, id='wrong_slug_1'),
        pytest.param({'slug': 'ghjijhj_2&'}, id='wrong_slug_2'),
        pytest.param({'slug': 'ghjijhj_2 '}, id='wrong_slug_3'),
        pytest.param({'slug': 'ghjijhj_2о'}, id='wrong_slug_4'),
        pytest.param({'slug': ''}, id='wrong_slug_5'),
        pytest.param(
            {'slug': 'slug', 'category_uid': 'x' * 301},
            id='wrong_category_uid',
        ),
    ],
)
async def test_goods_wrong_request(taxi_eats_products, menu_request):
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=menu_request,
        headers={'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 400


@experiments.REMOVE_EMPTY_CATEGORIES_ENABLED
@PARAMETRIZE_INTEGRATION_VERSION
@pytest.mark.parametrize(
    'categories_with_products,expected_categories',
    [
        ({106, 107, 108, 109}, [105, 106, 107, 108, 109]),
        ({107, 108, 109}, [105, 107, 108, 109]),
        ({}, [105]),
    ],
)
async def test_goods_empty_categories(
        mock_nomenclature_for_v2_menu_goods,
        add_default_product_mapping,
        categories_with_products,
        expected_categories,
        nmn_integration_version,
):
    """
    Проверяется, работа механизма фильтрации пустых категорий из ответа
    """
    add_default_product_mapping()

    category_1 = conftest.CategoryMenuGoods('105', '5', 'root')
    category_2 = conftest.CategoryMenuGoods('106', '6', 'category_1')
    category_3 = conftest.CategoryMenuGoods('107', '7', 'category_2')
    category_4 = conftest.CategoryMenuGoods('108', '8', 'category_3')
    category_5 = conftest.CategoryMenuGoods('109', '9', 'category_4')
    category_1.add_child_category(category_2)
    category_1.add_child_category(category_3)
    category_1.add_child_category(category_4)
    category_1.add_child_category(category_5)

    if 106 in categories_with_products:
        category_2.add_product(
            conftest.ProductMenuGoods(
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 'item_id_1', 'item_1',
            ),
        )
    if 107 in categories_with_products:
        category_3.add_product(
            conftest.ProductMenuGoods(
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 'item_id_2', 'item_2',
            ),
        )
    if 108 in categories_with_products:
        category_4.add_product(
            conftest.ProductMenuGoods(
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 'item_id_3', 'item_3',
            ),
        )
    if 109 in categories_with_products:
        category_5.add_product(
            conftest.ProductMenuGoods(
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', 'item_id_4', 'item_4',
            ),
        )

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 105

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(category_1)

    mock_nomenclature_for_v2_menu_goods.set_place(place)

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    category_ids = [item['id'] for item in categories]
    assert category_ids == expected_categories


@experiments.REMOVE_EMPTY_CATEGORIES_ENABLED
@PARAMETRIZE_INTEGRATION_VERSION
async def test_goods_without_category_keep_empty(
        add_default_product_mapping,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    """
    Проверяется, что при запросе без категорий фильтрация пустых
    категорий не происходит
    """
    add_default_product_mapping()

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    root_cat = conftest.CategoryMenuGoods(
        public_id='105', name='name', origin_id='origin_id',
    )
    child_cat_1 = conftest.CategoryMenuGoods(
        public_id='106', name='name', origin_id='origin_id',
    )
    root_cat.add_child_category(child_cat_1)
    child_cat_2 = conftest.CategoryMenuGoods(
        public_id='107', name='name', origin_id='origin_id',
    )
    root_cat.add_child_category(child_cat_2)
    place.add_root_category(root_cat)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST, nmn_integration_version,
        )
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    category_ids = [item['id'] for item in categories]
    assert category_ids == [105, 106, 107]


@experiments.REMOVE_EMPTY_CATEGORIES_ENABLED
@PARAMETRIZE_INTEGRATION_VERSION
@pytest.mark.parametrize(
    'category_product_ids,goods_count',
    [
        pytest.param(
            {
                6: [
                    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010',
                ],
            },
            1,
            id='product_without_mapping',
        ),
        pytest.param(
            {
                6: ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
                7: ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
            },
            1,
            id='product_in_several_categories',
        ),
    ],
)
async def test_goods_count(
        mock_nomenclature_for_v2_menu_goods,
        add_default_product_mapping,
        category_product_ids,
        goods_count,
        nmn_integration_version,
):
    # Проверяется работа счётчика продуктов goods_count
    add_default_product_mapping()

    root_category = conftest.CategoryMenuGoods('105', '5', 'root')

    for category_id in category_product_ids:
        category = conftest.CategoryMenuGoods(
            str(category_id + 100),
            str(category_id),
            f'category_{category_id}',
        )

        for public_id in category_product_ids[category_id]:
            category.add_product(
                conftest.ProductMenuGoods(public_id, 'item_id', 'item_name'),
            )

        root_category.add_child_category(category)

    place = conftest.PlaceMenuGoods(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    place.add_root_category(root_category)
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 105
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            request, integration_version=nmn_integration_version,
        )
    )

    assert response.status_code == 200
    assert response.json()['payload']['goods_count'] == goods_count


@pytest.mark.parametrize(
    'restaurants_carousel_first',
    [
        pytest.param(
            True, marks=experiments.categories_carousels_position(1, 2, False),
        ),
        pytest.param(
            False,
            marks=experiments.categories_carousels_position(2, 1, False),
        ),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_goods_restaurant_carousels_order(
        mock_nomenclature_for_v2_menu_goods,
        taxi_eats_products,
        add_default_product_mapping,
        restaurants_carousel_first,
        nmn_integration_version,
):
    """
    Проверяется, что в ответе ручки есть новое
    поле carousel_mapping, у которого есть две
    карусели restaurants_carousel и categories_carousel.
    Так же проверяется их порядок отображения.
    """
    add_default_product_mapping()

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='105',
        name='name',
        origin_id='origin_id',
        category_type='custom_restaurant',
    )
    child_cat_1 = conftest.CategoryMenuGoods(
        public_id='106',
        name='name',
        origin_id='origin_id',
        category_type='custom_restaurant',
    )
    root_cat_1.add_child_category(child_cat_1)
    root_cat_2 = conftest.CategoryMenuGoods(
        public_id='107',
        name='name',
        origin_id='origin_id',
        category_type='custom_base',
    )
    place.add_root_category(root_cat_1)
    place.add_root_category(root_cat_2)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST, nmn_integration_version,
        )
    )
    assert response.status_code == 200
    carousels = response.json()['payload']['carousel_mapping']['carousels']
    if restaurants_carousel_first:
        assert carousels[0]['show_in'] == 'restaurants_carousel'
        assert carousels[0]['title'] == 'Рестораны'
    else:
        assert carousels[0]['show_in'] == 'categories_carousel'
        assert carousels[0]['title'] == 'Продукты'


@pytest.mark.parametrize(
    'carousels_position_exp_on, is_in_horizontal_carousels',
    [
        pytest.param(
            True,
            True,
            marks=experiments.categories_carousels_position(1, 2, True),
        ),
        pytest.param(
            True,
            False,
            marks=experiments.categories_carousels_position(1, 2, False),
        ),
        pytest.param(False, False),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_goods_restaurants_in_horizontal_carousels(
        mock_nomenclature_for_v2_menu_goods,
        taxi_eats_products,
        add_default_product_mapping,
        carousels_position_exp_on,
        is_in_horizontal_carousels,
        nmn_integration_version,
):
    """
    Проверяется, что при is_restaurants_in_horizontal_carousels = True
    у ресторанов так же будет horizontal_carousel в массиве show_in
    """
    add_default_product_mapping()

    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='105',
        name='name',
        origin_id='origin_id',
        category_type='custom_restaurant',
    )

    child_cat_1 = conftest.CategoryMenuGoods(
        public_id='106', name='name', origin_id='origin_id',
    )
    root_cat_1.add_child_category(child_cat_1)

    child_cat_2 = conftest.CategoryMenuGoods(
        public_id='107', name='name', origin_id='origin_id',
    )
    root_cat_1.add_child_category(child_cat_2)

    place.add_root_category(root_cat_1)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            PRODUCTS_BASE_REQUEST, nmn_integration_version,
        )
    )

    assert response.status_code == 200
    payload = response.json()['payload']

    if not carousels_position_exp_on:
        assert 'carousel_mapping' not in response.json()['payload']
        assert payload['categories'][0]['show_in'] == ['categories_carousel']

    elif carousels_position_exp_on and is_in_horizontal_carousels:
        assert payload['categories'][0]['show_in'] == (
            ['restaurants_carousel', 'horizontal_carousel']
        )

    elif not carousels_position_exp_on and is_in_horizontal_carousels:
        assert 'carousel_mapping' not in response.json()['payload']
        assert payload['categories'][0]['show_in'] == (
            ['restaurants_carousel', 'horizontal_carousel']
        )

    elif carousels_position_exp_on and not is_in_horizontal_carousels:
        assert 'carousel_mapping' in response.json()['payload']
        assert payload['categories'][0]['show_in'] == ['restaurants_carousel']
