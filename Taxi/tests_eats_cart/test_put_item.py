import copy

import pytest

from . import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T11:00:00+03:00',
}

PROMO_TYPE = {
    'id': 1001,
    'type_id': 1,
    'name': 'Promo',
    'picture_uri': 'http://picture',
}

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323
PUT_BODY = utils.ITEM_PROPERTIES

OPTION_PRICES = {
    1679268432: {'price': 3.98, 'promo_price': 2.33},
    1679268437: {'price': 2, 'promo_price': None},
    1679268442: {'price': 3, 'promo_price': None},
    1679268447: {'price': 4, 'promo_price': None},
}


def convert_to_promo_item(ordinary_item, promo_item_id, promo_type):
    result = copy.deepcopy(ordinary_item)
    price = 0
    quantity = 1
    result['id'] = int(promo_item_id)
    result['price'] = price
    result['decimal_price'] = str(price)
    result['promo_type'] = promo_type
    result['quantity'] = quantity
    result['subtotal'] = str(price * quantity)
    result.pop('promo_subtotal')
    del result['decimal_promo_price']
    del result['promo_price']
    return result


async def test_put_no_eater_cart(taxi_eats_cart, local_services):
    item_id = 1234

    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{item_id}',
        params=PARAMS,
        headers=utils.get_auth_headers(EATER_ID),
        json=PUT_BODY,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 24,
        'domain': 'UserData',
        'err': 'Корзина не найдена',
    }


@pytest.mark.parametrize('should_insert_item', [True, False])
async def test_put_non_existing_id(
        taxi_eats_cart, local_services, db_insert, should_insert_item,
):
    non_exisiting_id = 1

    cart_id = db_insert.cart(EATER_ID)
    db_insert.eater_cart(EATER_ID, cart_id)
    if should_insert_item:
        non_exisiting_id = 1 + db_insert.cart_item(cart_id, MENU_ITEM_ID)

    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{non_exisiting_id}',
        params=PARAMS,
        headers=utils.get_auth_headers(EATER_ID),
        json=PUT_BODY,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 4,
        'domain': 'Network',
        'err': 'Не найдено',
    }


@pytest.mark.parametrize(
    'similar_exists,expected_json_filename,total,delivery_fee',
    [
        pytest.param(
            False,
            'expected_with_menu_promos.json',
            109.28,
            50,
            id='no_similar',
        ),
        pytest.param(
            True,
            'expected_with_options.json',
            138.56,
            20,
            id='similar_exists',
        ),
    ],
)
@utils.additional_payment_text()
@pytest.mark.parametrize(
    'erms_enabled',
    [
        pytest.param(
            True, marks=utils.get_items_from_erms(True), id='erms_enabled',
        ),
        pytest.param(
            False, marks=utils.get_items_from_erms(False), id='erms_disabled',
        ),
    ],
)
async def test_put_promo_item(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_insert,
        similar_exists,
        expected_json_filename,
        total,
        delivery_fee,
        erms_enabled,
):
    place_slug, place_id = 'place123', '22'
    cart_item_price = 50
    cart_item_promo_price = 48.95

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    if erms_enabled:
        local_services.eats_restaurant_menu_items_response = load_json(
            'eats_restaurant_menu_items.json',
        )
    else:
        local_services.core_items_response = load_json(
            'eats_core_menu_items.json',
        )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    core_promo_type = copy.deepcopy(PROMO_TYPE)
    core_promo_type['pictureUri'] = core_promo_type['picture_uri']
    del core_promo_type['picture_uri']
    del core_promo_type['type_id']
    local_services.set_core_promo_types(MENU_ITEM_ID, [core_promo_type])

    options_total_price = 0.0
    options_total_promo_price = 0.0
    for group in PUT_BODY['item_options']:
        for option in group['modifiers']:
            quantity = option['quantity']
            price = OPTION_PRICES[option['option_id']]['price']
            options_total_price += price * quantity
            promo_price = OPTION_PRICES[option['option_id']]['promo_price']
            actual_price = promo_price if promo_price else price
            options_total_promo_price += actual_price * quantity

    discounts = load_json('get_discounts_response.json')
    discounts['items'][0]['quantity'] = 1 + similar_exists
    discounts['items'][1]['promo'] = PROMO_TYPE
    discounts['total'] = str(
        (1 + similar_exists)
        * (cart_item_promo_price + options_total_promo_price),
    )
    local_services.core_discounts_response = discounts
    local_services.available_discounts = True

    cart_id = db_insert.cart(
        EATER_ID,
        place_slug=place_slug,
        place_id=place_id,
        promo_subtotal=(cart_item_promo_price + options_total_promo_price)
        * similar_exists,
        total=(cart_item_promo_price + options_total_promo_price)
        * similar_exists,
    )
    db_insert.eater_cart(EATER_ID, cart_id)
    promo_item_id = db_insert.cart_item(
        cart_id, MENU_ITEM_ID, price=0, promo_price=None, quantity=1,
    )
    for group in PUT_BODY['item_options']:
        for option in group['modifiers']:
            db_insert.item_option(
                promo_item_id,
                option['option_id'],
                price=0,
                promo_price=None,
                quantity=option['quantity'],
            )
    db_insert.item_discount(
        promo_item_id,
        PROMO_TYPE['id'],
        PROMO_TYPE['type_id'],
        name=PROMO_TYPE['name'],
        picture_uri=PROMO_TYPE['picture_uri'],
    )
    if similar_exists:
        similar_item_id = db_insert.cart_item(
            cart_id,
            MENU_ITEM_ID,
            price=cart_item_price,
            promo_price=cart_item_promo_price,
            quantity=1,
        )
        similar_item_id = str(similar_item_id)
        for group in PUT_BODY['item_options']:
            for option in group['modifiers']:
                db_insert.item_option(
                    similar_item_id,
                    option['option_id'],
                    price=OPTION_PRICES[option['option_id']]['price'],
                    promo_price=OPTION_PRICES[option['option_id']][
                        'promo_price'
                    ],
                    quantity=option['quantity'],
                )

    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{promo_item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=PUT_BODY,
    )

    assert response.status_code == 200
    if erms_enabled:
        assert (
            local_services.mocke_eats_restaurant_menu_items.times_called == 1
        )
    else:
        assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert utils.pg_result_to_repr(result)[0] == [
        cart_id,
        '2',
        EATER_ID,
        place_slug,
        place_id,
        '%.2f'
        % (
            (1 + similar_exists)
            * (cart_item_promo_price + options_total_promo_price)
        ),
        '%.2f' % total,
        '%.2f' % delivery_fee,
        'delivery',
        'None',
        '(25,35)',
    ]

    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert result[0]['eater_id'] == EATER_ID
    assert result[0]['cart_id'] == cart_id

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert len(items) == 2

    assert utils.pg_result_to_repr(items)[0] == [
        str(promo_item_id),
        cart_id,
        str(MENU_ITEM_ID),
        '0.00',
        'None',
        '1',
        'None',
        'False',
    ]
    similar_item_id = str(items[1]['id'])
    assert utils.pg_result_to_repr(items)[1] == [
        similar_item_id,
        cart_id,
        str(MENU_ITEM_ID),
        '50.00',
        '48.95',
        str(1 + similar_exists),
        'None',
        'False',
    ]

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    n_options = sum(
        1
        for group in PUT_BODY['item_options']
        for option in group['modifiers']
    )
    assert len(options) == 2 * n_options
    assert utils.pg_result_to_repr(options)[n_options:] == [
        [similar_item_id, '1679268432', '3.98', '2.33', '1'],
        [similar_item_id, '1679268437', '2.00', 'None', '1'],
        [similar_item_id, '1679268442', '3.00', 'None', '2'],
    ]

    expected_json = load_json(expected_json_filename)
    expected_items = expected_json['cart']['items']
    expected_menu_promo_type = copy.deepcopy(PROMO_TYPE)
    del expected_menu_promo_type['type_id']
    expected_items[0]['place_menu_item']['promo_types'] = [
        expected_menu_promo_type,
    ]

    expected_item_promo_type = copy.deepcopy(PROMO_TYPE)
    expected_item_promo_type['id'] = expected_item_promo_type['type_id']
    del expected_item_promo_type['type_id']
    expected_items.append(
        convert_to_promo_item(
            expected_items[0], promo_item_id, expected_item_promo_type,
        ),
    )
    expected_items[0]['id'] = int(similar_item_id)

    response_json = response.json()
    del response_json['cart']['updated_at']
    del response_json['cart']['id']
    del response_json['cart']['revision']
    assert response_json == expected_json


@utils.additional_payment_text()
@pytest.mark.parametrize('available_discounts', [True, False])
async def test_put_item_without_promo(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_insert,
        available_discounts,
):
    local_services.available_discounts = available_discounts
    local_services.core_discounts_response = load_json(
        'get_proper_discount.json',
    )
    place_slug, place_id = 'place123', '22'
    cart_item_price = 50
    cart_item_promo_price = 48.95

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    plus_response = load_json('eats_plus_cashback.json')
    del plus_response['cashback_outcome_details']
    local_services.set_plus_response(status=200, json=plus_response)
    local_services.set_params(utils.get_params())

    cart_id = db_insert.cart(
        EATER_ID,
        place_slug=place_slug,
        place_id=place_id,
        promo_subtotal=cart_item_promo_price,
        total=cart_item_promo_price,
    )
    db_insert.eater_cart(EATER_ID, cart_id)
    cart_item_id = db_insert.cart_item(
        cart_id,
        MENU_ITEM_ID,
        price=cart_item_price,
        promo_price=cart_item_promo_price,
        quantity=1,
    )

    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{cart_item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID, yandex_uid='uid0'),
        json=PUT_BODY,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert utils.pg_result_to_repr(result)[0] == [
        cart_id,
        '2',
        EATER_ID,
        place_slug,
        place_id,
        '118.56',
        '138.56',
        '20.00',
        'delivery',
        'None',
        '(25,35)',
    ]

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert len(items) == 1
    cart_item_id = str(items[0]['id'])
    assert utils.pg_result_to_repr(items)[0][1:] == [
        cart_id,
        str(MENU_ITEM_ID),
        '50.00',
        '48.95',
        str(PUT_BODY['quantity']),
        'None',
        'False',
    ]

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert len(options) == 3
    assert utils.pg_result_to_repr(options) == [
        [cart_item_id, '1679268432', '3.98', '2.33', '1'],
        [cart_item_id, '1679268437', '2.00', 'None', '1'],
        [cart_item_id, '1679268442', '3.00', 'None', '2'],
    ]

    expected_json = load_json('expected_with_options.json')
    expected_json['cart']['items'][0]['id'] = int(cart_item_id)

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


@pytest.mark.parametrize('shipping_type', ['delivery', 'pickup'])
async def test_put_item_shipping_type(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_insert,
        shipping_type,
):
    place_slug, place_id = 'place123', '22'
    cart_item_price = 50
    cart_item_promo_price = 48.95

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    cart_id = db_insert.cart(
        EATER_ID,
        place_slug=place_slug,
        place_id=place_id,
        promo_subtotal=cart_item_promo_price,
        total=cart_item_promo_price,
    )
    db_insert.eater_cart(EATER_ID, cart_id)
    cart_item_id = db_insert.cart_item(
        cart_id,
        MENU_ITEM_ID,
        price=cart_item_price,
        promo_price=cart_item_promo_price,
        quantity=1,
    )

    params = copy.deepcopy(PARAMS)
    params['shippingType'] = shipping_type
    local_services.set_params(params)
    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{cart_item_id}',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=PUT_BODY,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    assert response.json()['cart']['shipping_type'] == shipping_type

    res = utils.get_pg_records_as_dicts(utils.SELECT_CART, eats_cart_cursor)
    assert len(res) == 1
    assert res[0]['shipping_type'] == shipping_type


@pytest.mark.parametrize(
    'items,promo_subtotal,total',
    [
        pytest.param(
            [(MENU_ITEM_ID, 150, 100, 1), (MENU_ITEM_ID, 200, 120, 2)],
            350,
            220,
            id='two_items',
        ),
        pytest.param([(MENU_ITEM_ID, 150, 100, 1)], 150, 100, id='one_item'),
    ],
)
async def test_put_item_quantity_zero(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_insert,
        items,
        promo_subtotal,
        total,
):
    place_slug, place_id = 'place123', '22'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    cart_id = db_insert.cart(
        EATER_ID,
        place_slug=place_slug,
        place_id=place_id,
        promo_subtotal=promo_subtotal,
        total=total,
    )
    db_insert.eater_cart(EATER_ID, cart_id)
    for item in items:
        cart_item_id = db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )

    params = copy.deepcopy(PARAMS)
    request_body = copy.deepcopy(PUT_BODY)
    request_body['quantity'] = 0

    local_services.set_params(params)
    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{cart_item_id}',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    if len(items) == 2:
        assert local_services.mock_eats_core_menu.times_called == 1
        assert local_services.mock_eats_catalog.times_called == 1
        assert local_services.mock_eats_core_discount.times_called == 1

    cart_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART, eats_cart_cursor,
    )
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(cart_res) == 1
    if len(items) == 1:
        assert cart_res[0]['deleted_at']
    else:
        assert not cart_res[0]['deleted_at']
        assert not cart_items_res[0]['deleted_at']
        assert cart_items_res[-1]['deleted_at']
