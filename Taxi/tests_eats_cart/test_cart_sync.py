import datetime

import pytest

from tests_eats_cart import utils


@pytest.mark.now('2021-06-22T15:58:18.4505+0000')
@pytest.mark.parametrize('shipping_type', ['pickup', 'delivery'])
@pytest.mark.parametrize('delivery_time', ['2021-04-04T11:00:00+03:00', None])
@pytest.mark.parametrize(
    'point, tz_offset',
    [
        (utils.Point(43.10, 131.87), datetime.timedelta(hours=10)),
        (None, datetime.timedelta(hours=3)),  # Moscow
    ],
)
async def test_do_not_create_new_cart(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        shipping_type,
        delivery_time,
        point,
        tz_offset,
):
    now = '2021-06-22T15:58:18+00:00'
    eater_id = 'eater1'

    local_services.request_params = utils.get_params(
        shipping_type=shipping_type, delivery_time=delivery_time, point=point,
    )
    response = await taxi_eats_cart.post(
        '/api/v1/cart/sync',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
        json={},
    )

    assert response.status_code == 200

    empy_cart = utils.get_empty_cart(
        load_json, delivery_time, now, shipping_type, tz_offset,
    )

    assert response.json()['cart'] == empy_cart
    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert not result

    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert not result


@pytest.mark.now('2021-04-04T00:00:00+03:00')
@utils.additional_payment_text()
async def test_replace_existing_cart(
        taxi_eats_cart, load_json, eats_cart_cursor, db_insert, local_services,
):
    eater_id = 'eater2'
    local_services.set_place_slug('place123')
    place_id = '123'
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
        '/api/v1/cart/sync',
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
        place_id,  # place_id
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


@pytest.mark.now('2021-06-22T15:58:18.4505+0000')
@pytest.mark.parametrize(
    'should_go_to_products',
    [
        pytest.param(
            True, marks=utils.erase_place_business_enabled(), id='replace_on',
        ),
        pytest.param(False, id='replace_off'),
    ],
)
async def test_replace_place_business(
        taxi_eats_cart, load_json, local_services, should_go_to_products,
):
    eater_id = 'eater2'
    local_services.set_place_slug('place123')
    menu_item_id = 232323

    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.set_params(utils.get_params())
    post_body = {
        'items': [
            {'item_id': menu_item_id, 'quantity': 2, 'item_options': []},
        ],
        'shipping_type': 'delivery',
        'place_business': 'restaurant',
    }

    response = await taxi_eats_cart.post(
        '/api/v1/cart/sync',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
        json=post_body,
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert (
        local_services.mock_eats_products_menu.times_called
        == should_go_to_products
    )
