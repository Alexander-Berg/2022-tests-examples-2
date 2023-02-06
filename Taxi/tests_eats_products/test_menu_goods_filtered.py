import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

PLACE_SLUG = 'slug'
BASE_REQUEST = {'shippingType': 'delivery', 'slug': PLACE_SLUG}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
]

BRAND_FILTER_VALUES = [
    {
        'goods_count': '1',
        'is_applied': False,
        'name': 'brand_1',
        'query': '07d239cf59dfea64229a14cfd54b5e8a',
        'top_index': 0,
        'is_available': True,
    },
    {
        'goods_count': '1',
        'is_applied': False,
        'name': 'brand_2',
        'query': '755afade6859187cadfd7495087ef512',
        'top_index': 1,
        'is_available': True,
    },
]

BRAND_FILTER = utils.make_filter_for_response(
    'brand', 'Бренд', BRAND_FILTER_VALUES,
)

TRANSLATIONS = {
    'eats-products': {
        'discounts_filter_name_key': {'ru': 'Товары со скидкой'},
    },
}

DEFAULT_DISCOUNTS_FILTER_ICON = {'dark': 'icon_dark', 'light': 'icon_light'}


def make_expected_discounts_filter(is_applied=False, icon=None):
    result = {
        'is_applied': is_applied,
        'query': 'discounts_filter_id',
        'type': 'select',
        'ui_strings': {
            'all': 'Все',
            'done': 'Готово',
            'name': 'Товары со скидкой',
            'popular': 'Популярное',
            'reset': 'Сбросить',
            'show': 'Показать',
            'show_all': 'Еще 0',
        },
    }

    if icon is not None:
        result['icon'] = icon

    return result


def make_expected_filter_values(
        use_filters_from_nomenclature=False,
        use_brands_filter_from_products=True,
        applied_filter=None,
        applied_values=None,
):
    expected_filters = []
    if use_brands_filter_from_products:
        expected_filters.append(BRAND_FILTER)
    if not use_filters_from_nomenclature:
        return expected_filters

    # bool filter
    expected_filters.append(
        utils.make_filter_for_response(
            query='bool_filter',
            name='filter_name1',
            filter_type='select',
            image='image_1',
            is_applied=(
                applied_values if applied_filter == 'bool_filter' else False
            ),
        ),
    )

    # multiselect filter
    filter_values = []
    top_index = 0
    for i in range(10):
        value = {
            'goods_count': '10',
            'is_applied': False,
            'name': f'value_1_{i}',
            'query': f'value_1_{i}',
            'is_available': True,
        }

        is_applied = (
            applied_filter == 'multiselect_filter_2'
            and f'value_1_{i}' in applied_values
        )
        if is_applied or i < 2:
            value['is_applied'] = is_applied
            value['top_index'] = top_index
            top_index += 1
        filter_values.append(value)

    expected_filters.append(
        utils.make_filter_for_response(
            query='multiselect_filter_2',
            name='filter_name_2',
            values=filter_values,
            image='image_2',
            is_applied=applied_filter == 'multiselect_filter_2',
        ),
    )

    if use_brands_filter_from_products:
        return expected_filters

    # brands filter
    expected_filters.append(
        utils.make_filter_for_response(
            query='brand',
            name='Бренд',
            values=[
                {
                    'goods_count': '0',
                    'is_applied': (
                        applied_filter == 'brand'
                        and f'2_1_value' in applied_values
                    ),
                    'name': '2_1_value',
                    'query': '2_1_value',
                    'top_index': 1,
                    'is_available': False,
                },
                {
                    'goods_count': '10',
                    'is_applied': (
                        applied_filter == 'brand'
                        and f'2_2_value' in applied_values
                    ),
                    'name': '2_2_value',
                    'query': '2_2_value',
                    'top_index': 0,
                    'is_available': True,
                },
            ],
            is_applied=applied_filter == 'brand',
        ),
    )

    return expected_filters


def make_expected_response(
        mock_nomenclature_categories_filtered_context,
        use_filters_from_nomenclature=False,
        use_brands_filter_from_products=True,
        applied_filter=None,
        applied_values=None,
):
    response = (
        mock_nomenclature_categories_filtered_context.make_expected_response()
    )
    if use_brands_filter_from_products:
        response['payload']['categories'][0]['filters'] = [BRAND_FILTER]

    response['payload']['categories'][1]['filters'] = (
        make_expected_filter_values(
            use_filters_from_nomenclature,
            use_brands_filter_from_products,
            applied_filter,
            applied_values,
        )
    )
    return response


def handler_version_v2():
    return pytest.mark.config(
        EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
            {'menu_goods_category_products_version': 'v2'}
        ),
    )


def prepare_categories(
        mock_nomenclature_categories_filtered_context,
        with_discount=True,
        tags=None,
):
    root_category = conftest.NomenclatureFilteredCategory(
        public_id='1', name='Фрукты и овощи', origin_id='101', sort_order=1,
    )
    child_category_1 = conftest.NomenclatureFilteredCategory(
        public_id='2',
        name='Фрукты',
        origin_id='102',
        parent_public_id='1',
        images=[
            {'hash': 'image_hash_1', 'sort_order': 2, 'url': 'image_url_1'},
            {'hash': 'image_hash_2', 'sort_order': 1, 'url': 'image_url_2'},
        ],
        sort_order=2,
        tags=tags,
        filters=[
            conftest.NomenclatureCategoryFilter(
                id_='bool_filter',
                name='filter_name1',
                type='bool',
                sort_order=0,
                image='image_1',
            ),
            conftest.NomenclatureCategoryFilter(
                id_='multiselect_filter_2',
                name='filter_name_2',
                type='multiselect',
                sort_order=1,
                image='image_2',
                values=[
                    conftest.NomenclatureCategoryFilterValue(
                        value=f'value_1_{i}', items_count=10, sort_order=0,
                    )
                    for i in range(10)
                ],
            ),
            conftest.NomenclatureCategoryFilter(
                id_='brand',
                name='Бренд',
                type='multiselect',
                sort_order=2,
                values=[
                    conftest.NomenclatureCategoryFilterValue(
                        value='2_2_value', items_count=10, sort_order=0,
                    ),
                    conftest.NomenclatureCategoryFilterValue(
                        value='2_1_value', items_count=0, sort_order=0,
                    ),
                ],
            ),
        ],
    )
    child_category_2 = conftest.NomenclatureFilteredCategory(
        public_id='3',
        name='Овощи',
        origin_id='103',
        parent_public_id='1',
        images=[
            {'hash': 'image_hash_1', 'sort_order': 1, 'url': 'image_url_1'},
            {'hash': 'image_hash_2', 'sort_order': 2, 'url': 'image_url_2'},
        ],
        sort_order=3,
    )
    child_category_1.add_product(
        public_id=PUBLIC_IDS[0],
        name='Яблоки',
        description={'general': 'Яблоки'},
        sort_order=2,
        in_stock=5,
        images=[
            {'url': 'url_1', 'sort_order': 1},
            {'url': 'url_2', 'sort_order': 2},
        ],
        measure={'unit': 'KGRM', 'value': 1},
        is_catch_weight=True,
        shipping_type='all',
    )
    child_category_1.add_product(
        public_id=PUBLIC_IDS[1],
        name='Апельсины',
        sort_order=1,
        images=[
            {'url': 'url_1', 'sort_order': 2},
            {'url': 'url_2', 'sort_order': 1},
        ],
        old_price='120.00' if with_discount else None,
        measure={'unit': 'KGRM', 'value': 1},
        is_catch_weight=True,
    )
    child_category_2.add_product(
        public_id=PUBLIC_IDS[2],
        name='Огурцы',
        sort_order=3,
        in_stock=5,
        images=[
            {'url': 'url_1', 'sort_order': 1},
            {'url': 'url_2', 'sort_order': 2},
        ],
        measure={'unit': 'KGRM', 'value': 1},
    )

    child_category_2.add_product(
        public_id=PUBLIC_IDS[3],
        name='Огурцы',
        sort_order=4,
        in_stock=5,
        images=[
            {'url': 'url_1', 'sort_order': 1},
            {'url': 'url_2', 'sort_order': 2},
        ],
        measure={'unit': 'KGRM', 'value': 1},
        shipping_type='pickup',
    )

    mock_nomenclature_categories_filtered_context.add_category(root_category)
    mock_nomenclature_categories_filtered_context.add_category(
        child_category_2,
    )
    mock_nomenclature_categories_filtered_context.add_category(
        child_category_1,
    )


@handler_version_v2()
@experiments.filters_settings()
async def test_menu_goods_filtered_happy_path(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        mock_nomenclature_static_info_context,
):
    """
    Тест проверяет работу ручки menu/goods при использовании
    v1/place/category_products/filtered
    """
    add_default_product_mapping()

    prepare_categories(mock_nomenclature_categories_filtered_context)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0], brand='brand_1',
    )

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1], brand='brand_2',
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200
    assert response.json() == make_expected_response(
        mock_nomenclature_categories_filtered_context,
    )
    assert mock_nomenclature_categories_filtered_context.times_called == 1
    assert mock_nomenclature_static_info_context.times_called == 1


@handler_version_v2()
async def test_menu_goods_filtered_without_category(
        add_default_product_mapping, mock_nomenclature_for_v2_menu_goods,
):
    """
    Тест проверяет, что при включенном v2 и выполнении запроса без категории
    используются ручки /v1/place/categories/get_children и
    /v1/places/categories
    """
    add_default_product_mapping()
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID, slug=PLACE_SLUG, brand_id=utils.BRAND_ID,
    )
    mock_nomenclature_for_v2_menu_goods.set_place(place)
    root_cat = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='origin_id',
    )
    place.add_root_category(root_cat)
    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            BASE_REQUEST, 'v2',
        )
    )
    assert response.json()['payload']['categories']


@handler_version_v2()
@pytest.mark.parametrize(
    'status_code,expected_code,error',
    [
        (404, 404, None),
        (400, 500, None),
        (500, 500, None),
        (None, 500, 'network_error'),
        (None, 500, 'timeout_error'),
    ],
)
async def test_menu_goods_filtered_bad_response(
        taxi_eats_products,
        mock_nomenclature_categories_filtered_context,
        status_code,
        expected_code,
        error,
        add_default_product_mapping,
):
    """
    Тест проверяет работу ручки menu/goods при плохом ответе от
    v1/place/category_products/filtered
    """
    add_default_product_mapping()

    if error is None:
        mock_nomenclature_categories_filtered_context.set_status(status_code)
    elif error == 'network_error':
        mock_nomenclature_categories_filtered_context.set_network_error(True)
    elif error == 'timeout_error':
        mock_nomenclature_categories_filtered_context.set_timeout_error(True)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == expected_code
    assert (
        mock_nomenclature_categories_filtered_context.handler.times_called == 1
    )


@handler_version_v2()
@pytest.mark.parametrize(
    'status_code,error',
    [
        (404, None),
        (400, None),
        (500, None),
        (None, 'network_error'),
        (None, 'timeout_error'),
    ],
)
@experiments.filters_settings(use_nomenclature=True)
async def test_menu_goods_filtered_static_info_bad_response(
        taxi_eats_products,
        mock_nomenclature_categories_filtered_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        status_code,
        error,
):
    """
    Тест проверяет работу ручки menu/goods при плохом ответе от ручки
    статической информации
    """
    add_default_product_mapping()

    prepare_categories(mock_nomenclature_categories_filtered_context)

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0], brand='brand_1',
    )

    if error is None:
        mock_nomenclature_static_info_context.set_status(status_code)
    elif error == 'network_error':
        mock_nomenclature_static_info_context.set_network_error(True)
    elif error == 'timeout_error':
        mock_nomenclature_static_info_context.set_timeout_error(True)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert (
        mock_nomenclature_categories_filtered_context.handler.times_called == 1
    )
    expected = make_expected_response(
        mock_nomenclature_categories_filtered_context,
        use_brands_filter_from_products=False,
        use_filters_from_nomenclature=True,
    )

    assert response.json() == expected


@handler_version_v2()
@experiments.filters_settings(use_nomenclature=True, use_brand=False)
@pytest.mark.parametrize(
    'filter_query,applied_values,',
    [
        ('bool_filter', True),
        ('multiselect_filter_2', [f'value_1_{i}' for i in range(6)]),
        ('brand', {'2_2_value'}),
    ],
)
async def test_menu_goods_filtered_nmn_filters(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        filter_query,
        applied_values,
):
    """
    Тест проверяет работу фильтров, полученных из
    v1/place/category_products/filtered
    """
    add_default_product_mapping()

    prepare_categories(mock_nomenclature_categories_filtered_context)

    if filter_query != 'bool_filter':
        applied_values = list(applied_values)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1
    request['filters'] = {filter_query: applied_values}

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )

    expected_response = make_expected_response(
        mock_nomenclature_categories_filtered_context,
        use_brands_filter_from_products=False,
        use_filters_from_nomenclature=True,
        applied_filter=filter_query,
        applied_values=applied_values,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@handler_version_v2()
@pytest.mark.parametrize(
    'expected_values, category_position',
    [
        pytest.param(
            [
                {
                    'goods_count': '0',
                    'is_applied': False,
                    'name': '2_1_value',
                    'query': '2_1_value',
                    'top_index': 1,
                    'is_available': False,
                },
                {
                    'goods_count': '10',
                    'is_applied': False,
                    'name': '2_2_value',
                    'query': '2_2_value',
                    'top_index': 0,
                    'is_available': True,
                },
            ],
            2,
            marks=experiments.filters_settings(
                use_nomenclature=True, use_brand=False,
            ),
        ),
        pytest.param(
            BRAND_FILTER_VALUES,
            0,
            marks=experiments.filters_settings(use_nomenclature=True),
        ),
    ],
)
async def test_menu_goods_filtered_brands_filter(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        mock_nomenclature_static_info_context,
        expected_values,
        category_position,
):
    """
    Тест проверяет работу подмены фильтров брендов
    """
    add_default_product_mapping()

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0], brand='brand_1',
    )

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1], brand='brand_2',
    )

    prepare_categories(mock_nomenclature_categories_filtered_context)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200

    response_json = response.json()
    category_filters = response_json['payload']['categories'][1]['filters']
    assert len(category_filters) == 3
    assert (
        category_filters[category_position]
        == utils.make_filter_for_response(
            query='brand',
            name='Бренд',
            values=expected_values,
            is_applied=False,
        )
    )


@handler_version_v2()
@pytest.mark.parametrize(
    'applied_values,top_values',
    [
        (
            # В топ попадают только выбранные пользователем значения
            [f'value_1_{i}' for i in range(2, 6)],
            [f'value_1_{i}' for i in range(2, 6)],
        ),
        (
            # В топ попадает 3 значения выбранных пользователем и 1 топовое
            [f'value_1_{i}' for i in range(1, 4)],
            [f'value_1_{i}' for i in range(1, 4)] + ['value_1_0'],
        ),
        (
            # В топ попадает 2 значения выбранных пользователем и 2 топовых
            [f'value_1_{i}' for i in range(1, 3)],
            [f'value_1_{i}' for i in range(1, 3)] + ['value_1_0', 'value_1_3'],
        ),
        (
            # В топ попадает 2 значения выбранных пользователем и 2 топовых
            # Проверяется, что значения возвращается в выбранном порядке
            [f'value_1_{i}' for i in reversed(range(1, 3))],
            [f'value_1_{i}' for i in reversed(range(1, 3))]
            + ['value_1_0', 'value_1_3'],
        ),
    ],
)
@experiments.filters_settings(
    use_nomenclature=True, use_brand=False, popular_options_limit=4,
)
async def test_menu_goods_filtered_top_values(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        applied_values,
        top_values,
):
    """
    Тест проверяет работу фильтров то, что выбранные значения вытесняют из
    top_values остальные
    """
    add_default_product_mapping()

    prepare_categories(mock_nomenclature_categories_filtered_context)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1
    request['filters'] = {'multiselect_filter_2': applied_values}
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200

    response_json = response.json()
    category_filters = response_json['payload']['categories'][1]['filters']
    assert len(category_filters) == 3
    assert [
        value['query'] for value in category_filters[1]['top_values']
    ] == top_values


@pytest.mark.translations(**TRANSLATIONS)
@handler_version_v2()
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@pytest.mark.parametrize(
    'discount_applicator_discount', [None, 'fraction', 'product'],
)
@experiments.filters_settings(
    use_nomenclature=True,
    use_brand=False,
    discounts_filter=utils.make_discounts_filter_settings(position=1),
)
async def test_menu_goods_filtered_discounts_filter(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        mock_v2_match_discounts_context,
        discount_applicator_discount,
):
    """
    Тест проверяет добавление фильтра "Товары со скидкой" и то, что если в
    категории есть хотя бы один товар со скидкой, то is_available == true
    """
    add_default_product_mapping()

    prepare_categories(mock_nomenclature_categories_filtered_context)

    if discount_applicator_discount == 'fraction':
        mock_v2_match_discounts_context.add_discount_product(
            PUBLIC_IDS[2], 'fraction', 10.0,
        )
    elif discount_applicator_discount == 'product':
        mock_v2_match_discounts_context.add_discount_product(
            PUBLIC_IDS[2], promo_product=True,
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200

    response_json = response.json()
    categories = response_json['payload']['categories']

    if discount_applicator_discount is None:
        assert not categories[2]['filters'][0]['is_available']
        del categories[2]['filters'][0]['is_available']

    expected_filter = make_expected_discounts_filter()
    assert categories[0]['filters'][0] == expected_filter
    assert categories[1]['filters'][1] == expected_filter
    assert categories[2]['filters'][0] == expected_filter

    assert mock_v2_match_discounts_context.handler.times_called == 1


@pytest.mark.translations(**TRANSLATIONS)
@handler_version_v2()
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.REMOVE_EMPTY_CATEGORIES_ENABLED
@pytest.mark.parametrize('has_discount_applicator_discount', [False, True])
@experiments.filters_settings(
    use_brand=False,
    discounts_filter=utils.make_discounts_filter_settings(
        icon=DEFAULT_DISCOUNTS_FILTER_ICON,
    ),
)
async def test_menu_goods_filtered_discounts_filter_applied(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        mock_v2_match_discounts_context,
        has_discount_applicator_discount,
):
    """
    Тест проверяет применение фильтра "Товары со скидкой". Если фильтр применён
    (value==True), то из категорий удаляется весь товар без скидок, а
    is_applied устанавливается в значение True
    """
    add_default_product_mapping()

    prepare_categories(mock_nomenclature_categories_filtered_context)
    mock_nomenclature_categories_filtered_context.expected_request = {
        'filters': [],
    }

    if has_discount_applicator_discount:
        mock_v2_match_discounts_context.add_discount_product(
            PUBLIC_IDS[2], 'fraction', 10.0,
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1
    request['filters'] = {'discounts_filter_id': True}
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200

    response_json = response.json()
    categories = response_json['payload']['categories']

    expected_filter = make_expected_discounts_filter(
        True, icon=DEFAULT_DISCOUNTS_FILTER_ICON,
    )
    assert categories[0]['filters'][0] == expected_filter
    assert categories[1]['filters'][0] == expected_filter
    if has_discount_applicator_discount:
        assert categories[2]['filters'][0] == expected_filter
        assert len(categories[2]['items']) == 1
        assert categories[2]['items'][0]['public_id'] == PUBLIC_IDS[2]
    else:
        assert len(categories) == 2

    assert mock_v2_match_discounts_context.handler.times_called == 1


@handler_version_v2()
@experiments.REMOVE_EMPTY_CATEGORIES_ENABLED
@experiments.filters_settings(
    use_brand=False, discounts_filter=utils.make_discounts_filter_settings(),
)
@pytest.mark.parametrize('is_root', [True, False])
async def test_menu_goods_filtered_discounts_filter_empty_products(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        is_root,
):
    """
    Тест проверяет что при применение фильтра "Товары со скидкой" если нет
    скидочных товаров, то возвращается только запрошенная категория.
    """
    add_default_product_mapping()

    child_category_1 = conftest.NomenclatureFilteredCategory(
        public_id='105',
        name='child_category_1',
        origin_id='5',
        parent_public_id=None if is_root else '101',
        sort_order=1,
    )
    child_category_2 = conftest.NomenclatureFilteredCategory(
        public_id='106',
        name='child_category_2',
        origin_id='6',
        parent_public_id='105',
        sort_order=2,
    )
    child_category_2.add_product(public_id=PUBLIC_IDS[0], name='product_1')
    mock_nomenclature_categories_filtered_context.add_category(
        child_category_1,
    )
    mock_nomenclature_categories_filtered_context.add_category(
        child_category_2,
    )

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 105
    request['filters'] = {'discounts_filter_id': True}
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200

    response_json = response.json()
    categories = response_json['payload']['categories']

    assert len(categories) == 1
    assert not categories[0]['items']
    assert categories[0]['id'] == 105


@pytest.mark.parametrize(
    'tag_name',
    (
        pytest.param(None, marks=experiments.weight_data()),
        pytest.param('tag', marks=experiments.weight_data(tag_name='tag')),
    ),
)
@pytest.mark.parametrize('tags', (['tag'], ['tag_1'], [], None))
@handler_version_v2()
@experiments.filters_settings()
async def test_menu_goods_filtered_weight_data(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
        mock_nomenclature_static_info_context,
        tag_name,
        tags,
):
    """
    Тест проверяет добавление weight_data в зависимости от тегов категории
    """
    add_default_product_mapping()

    prepare_categories(
        mock_nomenclature_categories_filtered_context, tags=tags,
    )

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0], brand='brand_1',
    )

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1], brand='brand_2',
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200
    items = response.json()['payload']['categories'][1]['items']

    if tag_name is None or (tags and tag_name in tags):
        assert 'weight_data' in items[0]
    else:
        assert 'weight_data' not in items[0]

    assert mock_nomenclature_categories_filtered_context.times_called == 1


@handler_version_v2()
async def test_menu_goods_filtered_removing_parent_id(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_categories_filtered_context,
):
    """
    Тест проверяет что для запрашиваеммой категории parent_id==null.
    """
    add_default_product_mapping()

    category_1 = conftest.NomenclatureFilteredCategory(
        public_id='105',
        name='child_category_1',
        origin_id='5',
        parent_public_id='101',
        sort_order=1,
    )
    category_1.add_product(public_id=PUBLIC_IDS[0], name='product_1')
    mock_nomenclature_categories_filtered_context.add_category(category_1)

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 105
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 200

    response_json = response.json()
    categories = response_json['payload']['categories']

    assert len(categories) == 1
    assert not categories[0]['parentId']
    assert 'parent_uid' not in categories[0]


@handler_version_v2()
async def test_menu_goods_wrong_nmn_response(
        mockserver, taxi_eats_products, add_default_product_mapping,
):
    """
    Тест проверяет работу ручки menu/goods в случае если номенклатура вернула
    неверную категорию.
    """
    add_default_product_mapping()

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_CATEGORY_PRODUCTS_FILTERED,
    )
    def _mock_filtered(request):
        return {
            'categories': [
                {
                    'id': '2',
                    'origin_id': '2',
                    'name': 'category_name',
                    'child_ids': [],
                    'sort_order': 0,
                    'type': 'partner',
                    'images': [],
                    'filters': [],
                    'products': [],
                    'parent_id': None,
                    'tags': [],
                },
            ],
        }

    request = copy.deepcopy(BASE_REQUEST)
    request['category'] = 1

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers={},
    )
    assert response.status_code == 404
