import pytest

from . import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T11:00:00+03:00',
}

PROMO_TYPE = {'id': 1001, 'name': 'Promo', 'picture_uri': 'http://picture'}

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323
PUT_BODY = utils.ITEM_PROPERTIES

OPTION_PRICES = {1679268432: 1, 1679268437: 2, 1679268442: 3, 1679268447: 4}


async def test_delete_no_eater_cart(taxi_eats_cart, local_services):
    item_id = 1234

    response = await taxi_eats_cart.delete(
        f'/api/v1/cart/{item_id}',
        params=PARAMS,
        headers=utils.get_auth_headers(EATER_ID),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 24,
        'domain': 'UserData',
        'err': 'Корзина не найдена',
    }


@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_delete_last_item(
        taxi_eats_cart, local_services, load_json, eats_cart_cursor,
):
    item_id = 6
    eater_id = 'eater3'
    place_slug = 'place123'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = ['123', '1234']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.delete(
        f'/api/v1/cart/{item_id}',
        params=PARAMS,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(
        f'SELECT * FROM eats_cart.carts WHERE eater_id = \'{eater_id}\' '
        'AND deleted_at IS NOT NULL',
    )
    items = eats_cart_cursor.fetchall()
    assert len(items) == 1


@pytest.mark.now('2021-06-22T15:58:18.4505+0000')
async def test_delete_last_item_without_promo(
        taxi_eats_cart, db_insert, local_services, load_json, eats_cart_cursor,
):
    menu_item_id, promo_menu_item_id = '123', '1234'
    eater_id = 'eater3'
    place_slug = 'place123'

    cart_id = db_insert.cart(
        eater_id,
        place_slug=place_slug,
        promo_subtotal=100,
        total=100,
        delivery_fee=10,
        service_fee=1.05,
    )
    db_insert.eater_cart(eater_id, cart_id)
    item_id = db_insert.cart_item(cart_id, menu_item_id, price=10)
    promo_item_id = db_insert.cart_item(cart_id, promo_menu_item_id, price=0)
    db_insert.item_discount(
        promo_item_id, promo_id='promo1', promo_type_id='promo_type1',
    )

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [menu_item_id, promo_menu_item_id]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.delete(
        f'/api/v1/cart/{item_id}',
        params=PARAMS,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(
        'SELECT deleted_at FROM eats_cart.carts'
        f' WHERE eater_id = \'{eater_id}\' ',
    )
    carts = eats_cart_cursor.fetchall()
    assert len(carts) == 1
    assert carts[0][0] is not None

    empy_cart = load_json('empty_cart.json')
    assert response.json()['cart'] == empy_cart


@pytest.mark.parametrize('should_insert_item', [True, False])
async def test_delete_non_existing_id(
        taxi_eats_cart, local_services, db_insert, should_insert_item,
):
    non_exisiting_id = 1

    cart_id = db_insert.cart(EATER_ID)
    db_insert.eater_cart(EATER_ID, cart_id)
    if should_insert_item:
        non_exisiting_id = 1 + db_insert.cart_item(cart_id, MENU_ITEM_ID)

    response = await taxi_eats_cart.delete(
        f'/api/v1/cart/{non_exisiting_id}',
        params=PARAMS,
        headers=utils.get_auth_headers(EATER_ID),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 4,
        'domain': 'Network',
        'err': 'Не найдено',
    }


@pytest.mark.now('2021-04-03T01:12:31.4505+0300')
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
@pytest.mark.parametrize('available_discounts', [False, True])
@utils.additional_payment_text()
async def test_delete_item_without_promo(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        available_discounts,
):
    local_services.available_discounts = available_discounts
    cart_item_id = '1'
    place_slug = 'place123'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = ['123', '1234']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.core_discounts_response = {
        'total': '148.95',
        'promos': [],
        'items': [
            {
                'id': 123,
                'price': '50',
                'quantity': 1,
                'options': [],
                'promo_type': None,
                'promo_price': '48.95',
            },
            {
                'id': 1234,
                'price': '100',
                'quantity': 1,
                'options': [],
                'promo_type': None,
                'promo_price': None,
            },
        ],
    }
    plus_response = load_json('eats_plus_cashback.json')
    del plus_response['cashback_outcome_details']
    local_services.set_plus_response(status=200, json=plus_response)
    local_services.set_params(utils.get_params())

    response = await taxi_eats_cart.delete(
        f'/api/v1/cart/{cart_item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID, yandex_uid='uid0'),
    )

    assert response.status_code == 200

    expected_json = load_json('expected_resp.json')
    response_json = response.json()
    del response_json['cart']['updated_at']
    expected_json['cart']['cashbacked_total'] = (
        expected_json['cart']['total'] - plus_response['cashback_outcome']
    )
    expected_json['cart']['decimal_cashbacked_total'] = str(
        float(expected_json['cart']['decimal_total'])
        - float(plus_response['decimal_cashback_outcome']),
    )

    plus_response = utils.make_cashback_data(plus_response)

    expected_json['cart']['yandex_plus'] = {'cashback': plus_response}
    del response_json['cart']['id']
    del response_json['cart']['revision']
    assert response_json == expected_json

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 2
    cart = next(cart for cart in result if cart['eater_id'] == EATER_ID)
    assert str(cart['promo_subtotal']) == '148.95'
    assert str(cart['total']) == '158.95'

    eats_cart_cursor.execute(
        'SELECT id FROM eats_cart.cart_items WHERE deleted_at IS NOT NULL',
    )
    items = eats_cart_cursor.fetchall()
    assert len(items) == 1
    assert items[0]['id'] == 1

    rows = utils.get_pg_records_as_dicts(
        'SELECT total from eats_cart.carts '
        'WHERE eater_id = \'%s\'' % EATER_ID,
        eats_cart_cursor,
    )
    total = float(rows[0]['total'])

    response_cart = response.json()['cart']
    assert response_cart['total'] == int(round(total))
    assert response_cart['decimal_total'] == '{:.2f}'.format(total)
