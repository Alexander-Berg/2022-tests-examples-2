import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}

DEFAULT_PICTURE_URL = (
    'https://avatars.mds.yandex.net/get-eda'
    + '/3770794/4a5ca0af94788b6e40bec98ed38f58cc/{w}x{h}'
)

PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}
PRODUCTS_HEADERS_PARTNER = {
    'X-Eats-User': 'partner_user_id=4',
    'X-AppMetrica-DeviceId': 'device_id',
}


async def test_return_from_v1_nomenclature(
        taxi_eats_products, mockserver, load_json, add_place_products_mapping,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_6',
                core_id=6,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
            ),
        ],
    )
    products_request = copy.copy(PRODUCTS_BASE_REQUEST)
    products_request['maxDepth'] = 3
    products_request['category'] = 1

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_category.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200

    # Проверяет что public_id соответствует public_id товара
    # из /v1/nomenclature
    expected_public_ids = {'Молоко': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006'}
    category = response.json()['payload']['categories'][0]
    products = {p['name']: p['public_id'] for p in category['items']}
    assert products == expected_public_ids


@pytest.mark.pgsql(
    'eats_products', files=['pg_eats_products.sql', 'add_mapping.sql'],
)
@experiments.repeat_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
    ),
)
async def test_find_repeat_category_v2(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что public_id правильно передаётся
    # из категории 'Повторим', когда repeat_to_assortment_enabled = True
    products_request = copy.copy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_category.json')

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    expected_public_ids = {'item_1': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'}
    category = response.json()['payload']['categories'][0]
    products = {p['name']: p['public_id'] for p in category['items']}
    assert products == expected_public_ids
    assert mock_retail_categories_brand_orders_history.times_called == 1


@experiments.discount_category()
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_find_discount_category_v2(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
):
    # Тест проверяет, что public_id правильно передаётся
    # из категории 'Скидки', когда discount_to_assortment_enabled = True
    products_request = copy.copy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', name='item_1',
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', name='item_2',
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', name='item_3',
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
    )

    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', old_price=1990,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', old_price=1000,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', in_stock=0,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    expected_public_ids = {
        'item_2': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        'item_3': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    }
    category = response.json()['payload']['categories'][0]
    products = {p['name']: p['public_id'] for p in category['items']}
    assert products == expected_public_ids
