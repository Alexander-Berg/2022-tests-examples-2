import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

PLACE_ID = str(utils.PLACE_ID)
EMPTY_CACHE_COUNTER = 'empty_cache'
EMPTY_NOMENCLATURE_RESPONSE_COUNTER = 'empty_nomenclature_responses'
UNKNOWN_COUNTER = 'unknown'
PUBLIC_ID = 'public_id_1'
POPULAR_CATEGORY_REDIS_KEY = (
    f'scores:top:yt_table_v3:1:{utils.POPULAR_CATEGORY_ID}'
)


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    'has_mapping,has_custom_category',
    [
        # Проверяется, что при не пустом ответе номенклатуры и отсутствии
        # маппинга инкрементится счётчик empty_cache
        pytest.param(
            False,
            False,
            marks=[
                pytest.mark.redis_store(
                    [
                        'zadd',
                        'scores:top:yt_table_v3:1:1001',
                        '0.00001',
                        'id_1',
                    ],
                ),
            ],
            id='empty_mapping',
        ),
        # Проверяется, что при не пустом ответе номенклатуры и отсутствии
        # скорринга инкрементится счётчик empty_cache
        pytest.param(
            True,
            True,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
                        utils.dynamic_categories_config(popular_enabled=True)
                    ),
                ),
                experiments.popular_category(),
                pytest.mark.redis_store(
                    ['zadd', POPULAR_CATEGORY_REDIS_KEY, '0.00001', 'id_1'],
                ),
            ],
            id='only_dynamic_categories',
        ),
        # Проверяется, что при отсутствии в redis данных для запрашиваемых
        # категорий инкрементится счётчик empty_cache
        pytest.param(True, False, id='empty_redis_data'),
    ],
)
@experiments.products_scoring()
async def test_get_categories_empty_cache_metric(
        taxi_eats_products,
        taxi_eats_products_monitor,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        has_mapping,
        has_custom_category,
):
    if has_mapping:
        add_place_products_mapping(
            [
                conftest.ProductMapping(
                    origin_id='id_1', core_id=101, public_id=PUBLIC_ID,
                ),
            ],
        )

    mock_nomenclature_v2_details_context.add_product(PUBLIC_ID)
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID)
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_ID)
    mock_nomenclature_get_parent_context.add_category('1001')

    mock_nomenclature_v1_categories_context.add_category(
        public_id='1001', name='Category',
    )

    request = {
        'shippingType': 'pickup',
        'slug': 'slug',
        'categories': [
            {'id': 1001, 'min_items_count': 1, 'max_items_count': 10},
            {
                'id': utils.POPULAR_CATEGORY_ID,
                'min_items_count': 1,
                'max_items_count': 10,
            },
        ],
    }

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    old_empty_responses_metric = (
        metrics_json[PLACE_ID][EMPTY_CACHE_COUNTER]
        if PLACE_ID in metrics_json
        else 0
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request,
    )
    assert response.status_code == 200
    if not has_custom_category:
        assert response.json() == {'categories': []}

    assert mock_nomenclature_v2_details_context.handler.times_called == (
        1 if handlers_version == 'v1' and has_custom_category else 0
    )
    assert mock_nomenclature_static_info_context.handler.times_called == (
        1 if handlers_version == 'v2' and has_custom_category else 0
    )
    assert mock_nomenclature_dynamic_info_context.handler.times_called == (
        1 if handlers_version == 'v2' and has_custom_category else 0
    )
    assert mock_nomenclature_get_parent_context.handler.times_called == (
        1 if handlers_version == 'v2' and has_custom_category else 0
    )

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    assert (
        metrics_json[PLACE_ID][EMPTY_CACHE_COUNTER]
        - old_empty_responses_metric
        == 1
    )


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    ('categories_returned', 'products_returned', 'discount_category_enabled'),
    [
        pytest.param(True, False, False, id='categories_returned'),
        pytest.param(False, True, False, id='products_returned'),
        pytest.param(False, False, False, id='nothing_returned'),
        pytest.param(
            False,
            True,
            True,
            marks=[
                experiments.discount_category(),
                pytest.mark.config(
                    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
                        utils.dynamic_categories_config(discount_enabled=True)
                    ),
                ),
            ],
            id='discount_category',
        ),
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'scores:top:yt_table_v3:1:1001', '0.00001', 'id_1'],
    [
        'zadd',
        f'scores:top:yt_table_v3:1:{utils.DISCOUNT_CATEGORY_ID}',
        '0.00001',
        'id_1',
    ],
)
@experiments.products_scoring()
async def test_get_categories_empty_nmn_response_metric(
        taxi_eats_products,
        taxi_eats_products_monitor,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        add_place_products_mapping,
        cache_add_discount_product,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        categories_returned,
        products_returned,
        discount_category_enabled,
):
    # Проверяется, что если номенклатура вернула пустой список товаров и/или
    # категорий инкрементится счётчик empty_nomenclature_responses

    if products_returned:
        mock_nomenclature_v2_details_context.add_product(
            PUBLIC_ID, promo_price=50 if discount_category_enabled else None,
        )
        mock_nomenclature_static_info_context.add_product(PUBLIC_ID)
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_ID, old_price=50 if discount_category_enabled else None,
        )
    if categories_returned:
        mock_nomenclature_v1_categories_context.add_category(
            public_id='1001', name='Category',
        )
        mock_nomenclature_get_parent_context.add_category('1001')
    if discount_category_enabled:
        cache_add_discount_product('id_1')

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='id_1', core_id=101, public_id=PUBLIC_ID,
            ),
        ],
    )

    request = {
        'shippingType': 'pickup',
        'slug': 'slug',
        'categories': [
            {'id': 1001, 'min_items_count': 1, 'max_items_count': 10},
            {
                'id': utils.DISCOUNT_CATEGORY_ID,
                'min_items_count': 1,
                'max_items_count': 10,
            },
        ],
    }

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    old_empty_responses_metric = (
        metrics_json[PLACE_ID][EMPTY_NOMENCLATURE_RESPONSE_COUNTER]
        if PLACE_ID in metrics_json
        else 0
    )

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
        assert (
            mock_nomenclature_get_parent_context.handler.times_called
            == products_returned
        )
    if discount_category_enabled:
        assert len(response.json()['categories']) == 1
        assert (
            response.json()['categories'][0]['id']
            == utils.DISCOUNT_CATEGORY_ID
        )
    else:
        assert response.json() == {'categories': []}

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    assert (
        metrics_json[PLACE_ID][EMPTY_NOMENCLATURE_RESPONSE_COUNTER]
        - old_empty_responses_metric
        == 1
    )


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.redis_store(
    ['zadd', 'scores:top:yt_table_v3:1:1001', '0.00001', 'id_1'],
)
@experiments.products_scoring()
async def test_get_categories_min_products_metric(
        taxi_eats_products,
        taxi_eats_products_monitor,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_v1_categories_context,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    # Проверяется, что если категории не вернулись из-за min-products
    # инкрементится счётчик unknown

    mock_nomenclature_v2_details_context.add_product(PUBLIC_ID)
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID)
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_ID)
    mock_nomenclature_v1_categories_context.add_category(
        public_id='1001', name='Category',
    )
    mock_nomenclature_get_parent_context.add_category('1001')

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='id_1', core_id=101, public_id=PUBLIC_ID,
            ),
        ],
    )

    request = {
        'shippingType': 'pickup',
        'slug': 'slug',
        'categories': [
            {'id': 1001, 'min_items_count': 5, 'max_items_count': 10},
        ],
    }

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    old_empty_responses_metric = (
        metrics_json[PLACE_ID][UNKNOWN_COUNTER]
        if PLACE_ID in metrics_json
        else 0
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request,
    )
    assert response.status_code == 200
    assert response.json() == {'categories': []}
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert (
            mock_nomenclature_v1_categories_context.handler.times_called == 0
        )
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    assert (
        metrics_json[PLACE_ID][UNKNOWN_COUNTER] - old_empty_responses_metric
        == 1
    )


async def test_menu_goods_empty_response_metric(
        taxi_eats_products,
        mock_v1_nomenclature_context,
        taxi_eats_products_monitor,
):
    # Проверяется, что если номенклатура вернула пустой список товаров
    # инкрементится счётчик empty_nomenclature_responses
    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    old_empty_responses_metric = (
        metrics_json[PLACE_ID][EMPTY_NOMENCLATURE_RESPONSE_COUNTER]
        if PLACE_ID in metrics_json
        else 0
    )

    request = {'shippingType': 'pickup', 'slug': 'slug'}
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']

    metrics_json = await taxi_eats_products_monitor.get_metric(
        'empty_response_errors',
    )

    assert (
        metrics_json[PLACE_ID][EMPTY_NOMENCLATURE_RESPONSE_COUNTER]
        - old_empty_responses_metric
        == 1
    )
