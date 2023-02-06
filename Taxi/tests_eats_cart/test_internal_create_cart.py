import pytest

from tests_eats_cart import utils

TEST_URI = '/internal/eats-cart/v1/create_cart'


@pytest.mark.now('2021-06-22T15:58:18+0000')
async def test_do_not_create_new_cart(
        taxi_eats_cart, load_json, eats_cart_cursor, db_insert, local_services,
):
    eater_id = 'eater1'

    cart_id = db_insert.cart(eater_id)
    db_insert.eater_cart(eater_id, cart_id)
    db_insert.cart_item(
        cart_id, 111, price=1000, promo_price=None, quantity=10,
    )

    post_body = {'eater_id': eater_id}
    post_body.update(utils.get_body_params())

    response = await taxi_eats_cart.post(
        TEST_URI, params={}, headers={}, json=post_body,
    )

    assert response.status_code == 200

    assert response.json()['cart_id'] == ''

    eats_cart_cursor.execute(utils.SELECT_ACTIVE_CART)
    result = eats_cart_cursor.fetchall()
    assert not result

    eats_cart_cursor.execute(utils.SELECT_ACTIVE_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert not result


async def test_replace_existing_cart(
        taxi_eats_cart, load_json, eats_cart_cursor, db_insert, local_services,
):
    eater_id = 'eater2'
    local_services.set_place_slug('place123')
    place_id = '123'
    menu_item_id, old_item_id = 232323, 111
    local_services.available_discounts = True
    local_services.core_discounts_response = load_json(
        'get_proper_discount.json',
    )

    old_cart_id = db_insert.cart(eater_id)
    db_insert.eater_cart(eater_id, old_cart_id)
    db_insert.cart_item(
        old_cart_id, old_item_id, price=1000, promo_price=None, quantity=10,
    )

    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    del local_services.request_params['deliveryTime']
    del local_services.request_params['longitude']
    del local_services.request_params['latitude']
    local_services.request_params['shippingType'] = 'pickup'
    post_body = utils.get_body_params()
    post_body.update(
        {
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
            'shipping_type': 'pickup',
            'eater_id': eater_id,
        },
    )

    response = await taxi_eats_cart.post(
        TEST_URI, params={}, headers={}, json=post_body,
    )

    assert response.status_code == 200

    cart_id = response.json()['cart_id']
    assert cart_id != ''
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 2

    assert result[0]['id'] == old_cart_id
    assert result[0]['deleted_at'] is not None
    assert result[1]['id'] == cart_id

    assert utils.pg_result_to_repr(result)[1][1:] == [
        '2',  # revision
        eater_id,  # eater_id
        next(iter(local_services.place_slugs)),  # place_slug
        place_id,  # place_id
        '118.56',  # promo_subtotal
        '118.56',  # total
        '0.00',  # delivery_fee
        'pickup',  # shipping_type
        'None',  # deleted_at
        'None',  # delivery_time
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
