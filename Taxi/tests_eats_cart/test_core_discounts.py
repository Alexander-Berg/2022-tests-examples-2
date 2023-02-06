import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323

ITEM_PROPERTIES = {
    'quantity': 1,
    'item_options': [],
    'shipping_type': 'delivery',
}
POST_BODY = dict(item_id=MENU_ITEM_ID, **ITEM_PROPERTIES)


@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_update_discount_item(
        taxi_eats_cart, load_json, local_services, eats_cart_cursor,
):
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_discounts_response = load_json(
        'get_core_discount.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    # check cart items
    eats_cart_cursor.execute(
        'SELECT id, quantity from eats_cart.cart_items '
        'WHERE cart_id = \'00000000000000000000000000000000\'',
    )
    items = set((i[0], i[1]) for i in eats_cart_cursor.fetchall())
    assert len(items) == 2
    assert (10, 2) in items  # check item
    assert (20, 2) in items  # check discount item


@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_additional_item_with_promo_price(
        taxi_eats_cart, load_json, local_services, eats_cart_cursor,
):
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_discounts_response = load_json(
        'core_discount_additional_item_with_promo_price.json',
    )
    local_services.core_items_request = ['1', '2']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    post_body = dict(item_id='2', **ITEM_PROPERTIES)
    eater_id = 'eater3'
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
        json=post_body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 2
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    # check cart items
    eats_cart_cursor.execute(
        'SELECT id, price, promo_price, deleted_at from eats_cart.cart_items '
        'WHERE cart_id = \'00000000000000000000000000000001\'',
    )
    items = set((i[0], i[1], i[2], i[3]) for i in eats_cart_cursor.fetchall())
    assert len(items) == 5
    for item in items:
        promo_item_with_promo_price = (
            item[3] == 'None' and item[1] == '0' and item[2] != 'None'
        )
        assert not promo_item_with_promo_price


@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
@pytest.mark.parametrize(
    'not_show_discounts',
    [
        pytest.param(
            True,
            marks=utils.not_show_row_discount(),
            id='not_show_row_discount',
        ),
        pytest.param(False, id='show_row_discount'),
    ],
)
async def test_exclude_discounts_from_promo_items(
        taxi_eats_cart, load_json, local_services, not_show_discounts,
):
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_discounts_response = load_json(
        'get_core_discount.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 200
    if not_show_discounts:
        assert not response.json()['cart']['promo_items']
    else:
        assert response.json()['cart']['promo_items']
