import copy

import pytest

from tests_eats_cart import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T11:00:00+03:00',
}
EATER_ID = 'eater2'
MENU_ITEM_ID = 123
POST_BODY_WITH_OPTIONS = {
    'items': [
        {
            'item_id': 232323,
            'quantity': 2,
            'item_options': [
                {
                    'group_id': 10372250,
                    'group_options': [1679268432, 1679268437],
                    'modifiers': [
                        {'option_id': 1679268432, 'quantity': 1},
                        {'option_id': 1679268437, 'quantity': 1},
                    ],
                },
                {
                    'group_id': 10372255,
                    'group_options': [1679268442],
                    'modifiers': [{'option_id': 1679268442, 'quantity': 1}],
                },
            ],
        },
        {
            'item_id': 2,
            'quantity': 1,
            'item_options': [
                {
                    'group_id': 10376250,
                    'group_options': [1679228437],
                    'modifiers': [{'option_id': 1679228437, 'quantity': 1}],
                },
            ],
        },
    ],
    'shipping_type': 'delivery',
}

POST_BODY_WITHOUT_OPTIONS = {
    'items': [
        {'item_id': 232323, 'quantity': 2, 'item_options': []},
        {'item_id': 2, 'quantity': 2, 'item_options': []},
    ],
    'shipping_type': 'delivery',
}


@pytest.mark.now('2021-04-04T00:00:00+03:00')
@pytest.mark.parametrize(
    'items,promo_subtotal,total',
    [
        pytest.param(
            [('232323', 150, 100, 1), ('2', 200, 120, 1)],
            350,
            220,
            id='two_items',
        ),
    ],
)
async def test_update_old_items_with_count(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        db_insert,
        local_services,
        items,
        promo_subtotal,
        total,
):
    place_slug, place_id = 'place123', '22'
    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [
        str(MENU_ITEM_ID),
        '232323',
        '1',
        '2',
        '3',
    ]
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
    request_body = copy.deepcopy(POST_BODY_WITHOUT_OPTIONS)
    db_insert.eater_cart(EATER_ID, cart_id)
    counter = 0
    for item in items:
        id_for_insert = db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )
        request_body['items'][counter]['item_id'] = id_for_insert
        counter += 1

    params = copy.deepcopy(PARAMS)
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/update_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(cart_items_res) == 2
    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert items[0]['place_menu_item_id'] == '232323'
    assert items[0]['quantity'] == 2
    assert items[1]['place_menu_item_id'] == '2'
    assert items[1]['quantity'] == 2
    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert not options


@pytest.mark.now('2021-04-04T00:00:00+03:00')
@pytest.mark.parametrize(
    'items,promo_subtotal,total',
    [
        pytest.param(
            [('232323', 150, 100, 1), ('2', 200, 120, 1)],
            350,
            220,
            id='two_items',
        ),
    ],
)
async def test_update_old_items_with_options(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        db_insert,
        local_services,
        items,
        promo_subtotal,
        total,
):
    place_slug, place_id = 'place123', '22'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [
        str(MENU_ITEM_ID),
        '232323',
        '1',
        '2',
        '3',
    ]
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
    request_body = copy.deepcopy(POST_BODY_WITH_OPTIONS)
    db_insert.eater_cart(EATER_ID, cart_id)
    counter = 0
    for item in items:
        id_for_insert = db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )
        request_body['items'][counter]['item_id'] = id_for_insert
        counter += 1

    params = copy.deepcopy(PARAMS)
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/update_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(cart_items_res) == 2
    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert items[0]['place_menu_item_id'] == '232323'
    assert items[0]['quantity'] == 2
    assert items[1]['place_menu_item_id'] == '2'
    assert items[1]['quantity'] == 1
    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert len(options) == 4
    assert options[0][1] == '1679268432'
    assert options[1][1] == '1679268437'
    assert options[2][1] == '1679268442'
    assert options[3][1] == '1679228437'


@pytest.mark.now('2021-04-04T00:00:00+03:00')
@pytest.mark.parametrize(
    'items,promo_subtotal,total',
    [
        pytest.param(
            [('232323', 150, 100, 9), ('2', 200, 120, 5)],
            350,
            220,
            id='two_items',
        ),
    ],
)
async def test_decrease_count(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        db_insert,
        local_services,
        items,
        promo_subtotal,
        total,
):
    place_slug, place_id = 'place123', '22'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [
        str(MENU_ITEM_ID),
        '232323',
        '1',
        '2',
        '3',
    ]
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
    request_body = copy.deepcopy(POST_BODY_WITHOUT_OPTIONS)
    counter = 0
    db_insert.eater_cart(EATER_ID, cart_id)
    for item in items:
        id_for_insert = db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )
        request_body['items'][counter]['item_id'] = id_for_insert
        counter += 1

    params = copy.deepcopy(PARAMS)
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/update_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(cart_items_res) == 2
    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert items[0]['place_menu_item_id'] == '232323'
    assert items[0]['quantity'] == 2
    assert items[1]['place_menu_item_id'] == '2'
    assert items[1]['quantity'] == 2


@pytest.mark.now('2021-04-04T00:00:00+03:00')
@pytest.mark.parametrize(
    'items,promo_subtotal,total',
    [
        pytest.param(
            [('232323', 150, 100, 1), ('2', 40, 40, 1)],
            190,
            140,
            id='two_items',
        ),
    ],
)
async def test_zero_count(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        db_insert,
        local_services,
        items,
        promo_subtotal,
        total,
):
    place_slug, place_id = 'place123', '22'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [
        str(MENU_ITEM_ID),
        '232323',
        '1',
        '2',
        '3',
    ]
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
    request_body = copy.deepcopy(POST_BODY_WITHOUT_OPTIONS)
    counter = 0
    db_insert.eater_cart(EATER_ID, cart_id)
    for item in items:
        id_for_insert = db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )
        request_body['items'][counter]['item_id'] = id_for_insert
        counter += 1

    params = copy.deepcopy(PARAMS)
    request_body['items'][1]['quantity'] = 0
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/update_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(cart_items_res) == 2
    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert items[0]['place_menu_item_id'] == '232323'
    assert items[0]['quantity'] == 2
    assert items[1]['deleted_at']
