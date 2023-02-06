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
            [('232323', 150, 100, 1), ('2', 200, 120, 2)],
            350,
            220,
            id='two_items',
        ),
        pytest.param([('232323', 150, 100, 1)], 150, 100, id='one_item'),
    ],
)
async def test_add_new_items(
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
    local_services.core_items_request = ['232323', '1', '2', '3']
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
        db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )

    params = copy.deepcopy(PARAMS)
    request_body = copy.deepcopy(POST_BODY_WITH_OPTIONS)
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/add_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    if len(items) == 2:
        assert len(cart_items_res) == 4
        eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
        items = eats_cart_cursor.fetchall()
        assert items[0]['place_menu_item_id'] == '232323'
        assert items[0]['quantity'] == 1
        assert items[1]['place_menu_item_id'] == '2'
        assert items[1]['quantity'] == 2
        assert items[2]['place_menu_item_id'] == '232323'
        assert items[2]['quantity'] == 2
        assert items[3]['place_menu_item_id'] == '2'
        assert items[3]['quantity'] == 1
        eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
        options = eats_cart_cursor.fetchall()
        assert len(options) == 4
    else:
        eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
        items = eats_cart_cursor.fetchall()
        assert len(cart_items_res) == 3
        assert items[0]['place_menu_item_id'] == '232323'
        assert items[0]['quantity'] == 1
        assert items[1]['place_menu_item_id'] == '232323'
        assert items[1]['quantity'] == 2
        assert items[2]['place_menu_item_id'] == '2'
        assert items[2]['quantity'] == 1
        eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
        options = eats_cart_cursor.fetchall()
        assert len(options) == 4


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
async def test_update_count_of_old_items(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        db_insert,
        local_services,
        items,
        promo_subtotal,
        total,
):
    place_slug, place_id = 'place123', '123'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = ['232323', '1', '2', '3']
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
        db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )

    params = copy.deepcopy(PARAMS)
    request_body = copy.deepcopy(POST_BODY_WITHOUT_OPTIONS)
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/add_bulk',
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
    assert items[0]['quantity'] == 3
    assert items[1]['place_menu_item_id'] == '2'
    assert items[1]['quantity'] == 3
    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert not options


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
    place_slug, place_id = 'place123', '123'

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = ['232323', '1', '2', '3']
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
        db_insert.cart_item(
            cart_id,
            item[0],  # item_id
            price=item[1],
            promo_price=item[2],
            quantity=item[3],
        )

    params = copy.deepcopy(PARAMS)
    request_body = copy.deepcopy(POST_BODY_WITH_OPTIONS)
    request_body['items'][0]['quantity'] = 0
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/add_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_body,
    )

    assert response.status_code == 200
    cart_items_res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(cart_items_res) == 3
    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert items[0]['place_menu_item_id'] == '232323'
    assert items[0]['quantity'] == 9
    assert items[1]['place_menu_item_id'] == '2'
    assert items[1]['quantity'] == 5
    assert items[2]['place_menu_item_id'] == '2'
    assert items[2]['quantity'] == 1


@pytest.mark.now('2021-04-04T00:00:00+03:00')
@utils.additional_payment_text()
async def test_replace_place(
        taxi_eats_cart, load_json, eats_cart_cursor, db_insert, local_services,
):
    eater_id = 'eater2'
    local_services.set_place_slug('place123')
    menu_item_id, old_item_id = 232323, 111

    old_cart_id = db_insert.cart(eater_id)
    db_insert.eater_cart(eater_id, old_cart_id)
    db_insert.cart_item(
        old_cart_id, old_item_id, price=1000, promo_price=None, quantity=10,
    )

    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    plus_response = load_json('eats_plus_cashback.json')
    del plus_response['cashback_outcome_details']
    local_services.set_plus_response(status=200, json=plus_response)
    local_services.set_params(utils.get_params())

    post_body = {
        'items': [
            {
                'item_id': menu_item_id,
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
                        'modifiers': [
                            {'option_id': 1679268442, 'quantity': 2},
                        ],
                    },
                ],
            },
        ],
        'shipping_type': 'delivery',
    }

    response = await taxi_eats_cart.post(
        '/api/v1/cart/add_bulk',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id, yandex_uid='uid0'),
        json=post_body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 2

    assert result[0]['id'] == old_cart_id
    assert result[0]['deleted_at'] is not None
    cart_id = result[1]['id']

    assert utils.pg_result_to_repr(result)[1][1:] == [
        '2',  # revision
        eater_id,  # eater_id
        next(iter(local_services.place_slugs)),  # place_slug
        '123',  # place_id
        '118.56',  # promo_subtotal
        '138.56',  # total
        '20.00',  # delivery_fee
        'delivery',  # shipping_type
        'None',  # deleted_at
        '(25,35)',  # delivery_time
    ]

    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert result[0]['eater_id'] == eater_id
    assert result[0]['cart_id'] == cart_id

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert len(items) == 2

    assert utils.pg_result_to_repr(items)[0][1:] == [
        old_cart_id,
        str(old_item_id),
        '1000.00',
        'None',
        '10',
        'None',
        'False',
    ]
    cart_item_id = str(items[1]['id'])
    assert utils.pg_result_to_repr(items)[1][1:] == [
        cart_id,
        str(menu_item_id),
        '50.00',
        '48.95',
        '2',
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

    expected_json = load_json('expected_replaced_cart.json')
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
async def test_shipping_type(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_insert,
        shipping_type,
):
    place_slug, place_id = 'place123', '123'
    cart_item_price = 50
    cart_item_promo_price = 48.95

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = ['232323', '1', '2', '3']
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
    db_insert.cart_item(
        cart_id,
        '232323',
        price=cart_item_price,
        promo_price=cart_item_promo_price,
        quantity=1,
    )

    params = copy.deepcopy(PARAMS)
    params['shippingType'] = shipping_type
    local_services.set_params(params)
    response = await taxi_eats_cart.post(
        '/api/v1/cart/add_bulk',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY_WITH_OPTIONS,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    assert response.json()['cart']['shipping_type'] == shipping_type

    res = utils.get_pg_records_as_dicts(utils.SELECT_CART, eats_cart_cursor)
    assert len(res) == 1
    assert res[0]['shipping_type'] == shipping_type


async def test_no_cart(
        taxi_eats_cart, local_services, load_json, eats_cart_cursor,
):
    place_slug = 'place123'
    local_services.set_place_slug(place_slug)
    local_services.core_items_request = ['232323', '1', '2', '3']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    response = await taxi_eats_cart.post(
        '/api/v1/cart/add_bulk',
        params=PARAMS,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY_WITH_OPTIONS,
    )
    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert len(items) == 2
    assert response.status_code == 200
