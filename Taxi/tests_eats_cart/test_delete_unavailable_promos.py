import pytest

from tests_eats_cart import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'deliveryTime': '2021-04-04T11:00:00+03:00',
}

EATER_ID = 'eater2'


@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
async def test_post_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.core_discounts_response = load_json('get_discount.json')
    local_services.available_discounts = True
    local_services.core_items_request = ['1', '2', '3', '20']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.delete(
        '/api/v1/cart/unavailable-promos',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 2
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART_DISCOUNTS)
    cart_discount = eats_cart_cursor.fetchall()

    assert len(cart_discount) == 3
    res = {}
    for i in utils.pg_result_to_repr(cart_discount):
        res[i[0]] = i[1]
    assert res['edit_promo'] == 'None'
    assert res['new_promo'] == 'None'
    assert res['old_promo'] != 'None'

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    cart_items = eats_cart_cursor.fetchall()
    assert len(cart_items) == 4
    res = {}
    for i in utils.pg_result_to_repr(cart_items):
        res[(i[2], i[3])] = (
            i[4],
            i[6],
        )  # (place_menu_item_id, price) -> (promo_price, deleted_at)
    assert res[('1', '100.00')][1] != 'None'
    assert res[('2', '100.00')] == ('None', 'None')
    assert res[('3', '0.00')] == ('None', 'None')

    assert response.json()['cart']['promos']
    assert len(response.json()['cart']['promo_items']) is not None
    assert len(response.json()['cart']['items']) == 3
    for i in response.json()['cart']['items']:
        assert i['name'] != ''
