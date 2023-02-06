import pytest

from . import utils

MENU_ITEM_ID = 232323
PLACE_SLUG = 'place123'
EATER_ID = 'eater2'
CART_ID = '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9'
HEADERS = {
    'X-YaTaxi-Session': 'eats:',
    'X-YaTaxi-Bound-UserIds': '',
    'X-YaTaxi-Bound-Sessions': '',
    'X-Eats-User': f'user_id={EATER_ID},',
}


@pytest.mark.now('2021-04-03T01:12:46+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.pgsql('eats_cart', files=['internal_insert_values.sql'])
@pytest.mark.parametrize(
    'cart_id,file_name',
    [
        ('00000000000000000000000000000001', 'expected_old_cart.json'),
        (
            '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
            'internal_expected_options_no_surge.json',
        ),
    ],
)
async def test_internal_get(
        taxi_eats_cart, local_services, load_json, cart_id, file_name,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    local_services.catalog_place_id = 123
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/get_cart',
        headers=HEADERS,
        json={'cart_id': cart_id},
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 0

    expected_json = load_json(file_name)
    if cart_id == CART_ID:
        del expected_json['surge']
        del expected_json['surge_is_actual']
        del expected_json['delivery_fee']
        del expected_json['applied_checkers']
        del expected_json['surge_info']
        expected_json['revision'] = 1

    data = response.json()

    utils.compare_and_remove_time(data, expected_json, 'created_at')
    assert data == expected_json


@pytest.mark.now('2021-04-03T01:12:46+0300')
@pytest.mark.pgsql('eats_cart', files=['internal_shop.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
async def test_internal_get_shop(taxi_eats_cart, local_services, load_json):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]

    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/get_cart',
        headers=HEADERS,
        json={'cart_id': '00000000000000000000000000000001'},
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == load_json('expected_get_shop.json')


@pytest.mark.parametrize(
    'cart_id',
    [
        '00000000000000000000000000000001',
        '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
    ],
)
async def test_get_cart_not_found(taxi_eats_cart, cart_id):
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/get_cart', json={'cart_id': cart_id},
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_get_cart_not_found_in_sql(taxi_eats_cart):
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/get_cart',
        headers=HEADERS,
        json={'cart_id': '00000000000000000000000000000000'},
    )
    assert response.status_code == 404
