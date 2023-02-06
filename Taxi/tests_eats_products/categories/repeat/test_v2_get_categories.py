import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

EATER_ID = '12345'
PRODUCTS_HEADERS = {
    'X-Eats-User': f'user_id={EATER_ID}',
    'X-AppMetrica-DeviceId': 'device_id',
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

EATS_PRODUCTS_CONFIG = {'enable_cross_brand_order_history_storage': True}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
]

SKU_IDS = ['1', '2', '3']

SKU_TO_PUBLIC_IDS = {
    str(utils.PLACE_ID): {
        SKU_IDS[0]: [PUBLIC_IDS[0], PUBLIC_IDS[2]],
        SKU_IDS[1]: [PUBLIC_IDS[1], PUBLIC_IDS[3]],
    },
}


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@experiments.products_scoring()
async def test_repeat_category_v2_get_categories_with_products(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_nomenclature_v2_details_context,
        make_public_by_sku_id_response,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что возвращаются кроссбрендовые товары
    # в ручке каруселей товаров
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
        1, PUBLIC_IDS[0], 1,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[1], 2,
    )
    mock_retail_categories_cross_brand_orders.add_product(
        1, PUBLIC_IDS[2], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        1, PUBLIC_IDS[3], 3, SKU_IDS[1],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_nomenclature_categories(request):
        return {'categories': [], 'products': []}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

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
        assert mock_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_retail_categories_cross_brand_orders.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    ['origin_id', 'core_id', 'public_id', 'has_products'],
    [
        pytest.param('item_id_1', None, PUBLIC_IDS[0], True, id='no_core_id'),
        pytest.param('item_id_1', 1, None, True, id='no_public_id'),
        pytest.param(None, None, None, True, id='no_mapping'),
        pytest.param('item_id_1', 1, PUBLIC_IDS[0], False, id='no_products'),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@experiments.products_scoring()
async def test_repeat_category_v2_get_categories_no_products_or_mapping(
        taxi_eats_products,
        mockserver,
        mock_nomenclature_v2_details_context,
        add_place_products_mapping,
        make_public_by_sku_id_response,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        origin_id,
        core_id,
        public_id,
        has_products,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что если у товаров нет маппинга,
    # то категория не будет возвращена в ручке каруселей товаров
    if origin_id:
        add_place_products_mapping(
            [conftest.ProductMapping(origin_id, core_id, public_id)],
        )
    if public_id:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)
    if has_products:
        mock_retail_categories_brand_orders_history.add_brand_product(
            brand_id=1, public_id=PUBLIC_IDS[0], orders_count=1,
        )
        mock_retail_categories_brand_orders_history.add_brand_product(
            brand_id=1, public_id=PUBLIC_IDS[1], orders_count=2,
        )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_nomenclature_categories(request):
        return {'categories': [], 'products': []}

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
    assert response.json() == {'categories': []}
    assert mock_retail_categories_brand_orders_history.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    ['brand_products_to_count', 'has_cross_brand_products'],
    [
        pytest.param(
            {PUBLIC_IDS[0]: 1, PUBLIC_IDS[1]: 2},
            False,
            id='only_brand_products',
        ),
        pytest.param(
            {PUBLIC_IDS[0]: 1}, True, id='brand_and_cross_brand_different',
        ),
        pytest.param(
            {PUBLIC_IDS[0]: 1, PUBLIC_IDS[1]: 2},
            True,
            id='brand_and_cross_brand_intersection',
        ),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@experiments.products_scoring()
async def test_repeat_category_v2_get_categories_only_brand_products(
        taxi_eats_products,
        mockserver,
        mock_nomenclature_v2_details_context,
        make_public_by_sku_id_response,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        brand_products_to_count,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
        has_cross_brand_products,
):
    # Проверяется, что товары из брендовой и кроссбрендовой истории заказов
    # замешиваются вместе в ручке каруселей товаров
    add_default_product_mapping()
    for public_id in PUBLIC_IDS[:2]:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    for brand_id in brand_products_to_count:
        mock_retail_categories_brand_orders_history.add_brand_product(
            brand_id=1,
            public_id=brand_id,
            orders_count=brand_products_to_count[brand_id],
        )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_nomenclature_categories(request):
        return {'categories': [], 'products': []}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    if has_cross_brand_products:
        mock_retail_categories_cross_brand_orders.add_product(
            utils.PLACE_ID, PUBLIC_IDS[1], 2, SKU_IDS[1],
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
    products = response.json()['categories'][0]['items']
    assert len(products) == 2
    assert [product['id'] for product in products] == [2, 1]
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.parametrize('response_code', [404, 500])
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_bad_response(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_retail_categories_cross_brand_orders,
        mock_retail_categories_brand_orders_history,
        response_code,
):
    # Проверяется, что при ответе из eats-retail-categories
    # 404 и 500 возвращается [].
    add_default_product_mapping()

    response = mockserver.make_response('error', status=response_code)

    mock_retail_categories_cross_brand_orders.set_status(
        status_code=response_code,
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
    assert response.json()['categories'] == []
    assert mock_retail_categories_cross_brand_orders.times_called == 1
