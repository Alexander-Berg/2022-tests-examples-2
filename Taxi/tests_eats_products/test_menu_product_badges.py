import pytest

from tests_eats_products import utils


PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'

SLUG = 'slug'

BASE_REQUEST_PUBLIC = {
    'place_slug': SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}


@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'discount_promo': {'enabled': True}},
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
)
async def test_menu_product_badges(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
):
    """
    Тест проверяет выставление цветов для бейджа со скидкой
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=1000,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, images=[],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC,
    )

    resp_item_0 = response.json()['menu_item']
    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )

    utils.compare_badges(resp_item_0, expected)
