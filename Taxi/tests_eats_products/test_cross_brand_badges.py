import pytest

from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {
    'shippingType': 'pickup',
    'slug': 'slug',
    'category': 1,
}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
]

SKU_IDS = ['1', '2', '3', '4', '5']

THIS_PLACE_ID = str(utils.PLACE_ID)
OTHER_PLACE_ID = '2'

EATER_ID = '123'
HEADERS = {'X-Eats-User': f'user_id={EATER_ID}'}

HAS_HISTORY_BRANDS = ['set', f'has_history:{EATER_ID}:brands', '1']
HAS_CROSS_BRANDS_HISTORY = ['set', f'has_history:{EATER_ID}:cross_brands', '1']


@experiments.cross_brand_history()
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'discount_promo': {'enabled': True}},
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
)
async def test_cross_brand_badges_discount(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        mockserver,
        mock_retail_categories_cross_brand_orders,
        mock_retail_categories_brand_orders_history,
):
    """
    Тест проверяет выставление цветов для бейджа со скидкой (cross_brand)
    """
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)

    public_ids = PUBLIC_IDS[:2]
    add_default_product_mapping()
    for public_id in public_ids:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, old_price=1000,
        )

    place_sku_to_public_ids = {
        THIS_PLACE_ID: {
            SKU_IDS[0]: [public_ids[0]],
            SKU_IDS[1]: [public_ids[1]],
        },
        OTHER_PLACE_ID: {SKU_IDS[1]: [public_ids[1]]},
    }

    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[1], 5, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(OTHER_PLACE_ID), PUBLIC_IDS[1], 5, SKU_IDS[1],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2'],
            'selected_place': {'place_slug': 'slug', 'brand_name': 'Ашан'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_item_0 = response.json()['categories'][0]['products'][0]
    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )

    utils.compare_badges(resp_item_0, expected)

    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1
