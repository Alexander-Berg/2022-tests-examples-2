import pytest

from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
]


def add_default_brand_products(mock_retail_categories_brand_orders_history):
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 3,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 5,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 3,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', 1,
    )


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.repeat_category()
@experiments.products_scoring()
async def test_top_repeat_products(
        load_json,
        taxi_eats_products,
        mock_nomenclature_v2_details_context,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_categories,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    price = 100
    for public_id in PUBLIC_IDS:
        mock_nomenclature_v2_details_context.add_product(
            public_id, shipping_type='all', price=price,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id,
            measure={'unit': 'KGRM', 'value': 1},
            description_general='ghi',
            name='item_4',
            images=[],
        )
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=price,
        )
        price += 1
    add_default_brand_products(mock_retail_categories_brand_orders_history)
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
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


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.repeat_category()
@experiments.products_scoring()
async def test_top_repeat_products_empty_nomenclature(
        taxi_eats_products,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_categories,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    add_default_brand_products(mock_retail_categories_brand_orders_history)
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'categories': []}
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
        assert mock_nomenclature_get_parent_context.handler.times_called == 0


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.repeat_category('disabled')
@experiments.products_scoring()
async def test_top_repeat_products_repeat_disabled(
        taxi_eats_products, handlers_version,
):
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'categories': []}


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.repeat_category()
@experiments.products_scoring()
async def test_top_repeat_products_min_empty(
        taxi_eats_products,
        mock_nomenclature_v2_details_context,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_categories,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    for public_id in PUBLIC_IDS:
        mock_nomenclature_v2_details_context.add_product(public_id)
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    add_default_brand_products(mock_retail_categories_brand_orders_history)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 5,
                    'max_items_count': 100,
                },
            ],
        },
        headers=PRODUCTS_HEADERS,
    )

    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'categories': []}
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@experiments.repeat_category()
@experiments.products_scoring()
async def test_top_repeat_products_max(
        load_json,
        taxi_eats_products,
        mock_nomenclature_v2_details_context,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_categories,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    price = 100
    for public_id in PUBLIC_IDS:
        mock_nomenclature_v2_details_context.add_product(
            public_id, shipping_type='all', price=price,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id,
            measure={'unit': 'KGRM', 'value': 1},
            description_general='ghi',
            name='item_4',
            images=[],
        )
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=price,
        )
        price += 1

    add_default_brand_products(mock_retail_categories_brand_orders_history)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 2,
                },
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    expected_response_items = expected_response['categories'][0]['items']
    expected_response_items = expected_response_items[:-1]
    items = response.json()['categories'][0]['items']
    assert len(items) == 2
    assert items == expected_response_items
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


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
@experiments.repeat_category()
@experiments.products_scoring()
async def test_top_repeat_products_with_default(
        load_json,
        taxi_eats_products,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_categories,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    price = 100
    for public_id in PUBLIC_IDS:
        mock_nomenclature_v2_details_context.add_product(
            public_id, shipping_type='all', price=price,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id,
            measure={'unit': 'KGRM', 'value': 1},
            description_general='ghi',
            name='item_4',
            images=[],
        )
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=price,
        )
        price += 1
    mock_nomenclature_get_parent_context.add_category('123')

    add_default_brand_products(mock_retail_categories_brand_orders_history)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.REPEAT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
                {'id': 123, 'min_items_count': 1, 'max_items_count': 4},
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert response.status_code == 200
    assert response.json() == load_json('expected_with_default_response.json')
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


@pytest.fixture(name='mock_nomenclature_products')
def _mock_nomenclature_products(mockserver, load_json):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock(request):
        assert set(request.json['products']) == set(
            [
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            ],
        )
        return load_json('v2_place_assortment_details_response.json')

    return _mock


@pytest.fixture(name='mock_nomenclature_categories')
def _mock_nomenclature_categories(mockserver, load_json):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock(request):
        return load_json('v1_product_categories_response.json')

    return _mock
