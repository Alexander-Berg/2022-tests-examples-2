# pylint: disable=C0302

import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 21

ITEM_PROPERTIES = {
    'quantity': 2,
    'item_options': [],
    'shipping_type': 'delivery',
}
POST_BODY = dict(item_id=MENU_ITEM_ID, **ITEM_PROPERTIES)

SUBTITLE_WITHOUT_DISCOUNT = {
    'color': [
        {'theme': 'light', 'value': '#000000'},
        {'theme': 'dark', 'value': '#ffffff'},
    ],
    'text': 'Закажите ещё на 100 ₽ для доставки за 450 ₽',
}


def check_additional_items(response, exp_pay_quant, exp_free_quant):
    assert response.status_code == 200

    response_json = response.json()

    if exp_pay_quant + exp_free_quant == 0:
        assert not response_json['cart']['items']
        return

    exp_item_subtotal = (exp_pay_quant + exp_free_quant) * 70
    exp_item_promo_subtotal = exp_pay_quant * 70 if exp_free_quant else None
    assert len(response_json['cart']['items']) == 1
    assert (
        response_json['cart']['items'][0]['quantity']
        == exp_pay_quant + exp_free_quant
    )
    assert response_json['cart']['items'][0]['subtotal'] == str(
        exp_item_subtotal,
    )
    assert response_json['cart']['items'][0].get('promo_subtotal') == (
        str(exp_item_promo_subtotal) if exp_item_promo_subtotal else None
    )
    assert response_json['cart']['subtotal'] == exp_item_subtotal
    assert response_json['cart']['decimal_subtotal'] == str(exp_item_subtotal)


@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
@utils.eats_discounts_promo_types_info(
    {
        'special_promo_type': {
            'name': 'default_name',
            'description': 'default_descr',
            'picture_uri': 'default_picture',
        },
    },
)
async def test_post_discounts_nakap(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_discounts_response = load_json('get_discount.json')
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    mock_discount = load_json('eats_discounts_response.json')

    mock_discount['match_results'][0]['discounts'][0]['discount_meta'] = {
        'promo': {
            'promo_type': 'special_promo_type',
            'description': 'custom_descr',
        },
    }

    local_services.eats_discounts_response = mock_discount
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 1
    assert local_services.mock_match_discounts.times_called == 1
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0
    assert local_services.mock_eats_tags.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART_DISCOUNTS)
    cart_discount = eats_cart_cursor.fetchall()

    assert not cart_discount

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    cart_items = eats_cart_cursor.fetchall()

    assert len(cart_items) == 1

    item = utils.pg_result_to_repr(cart_items)[0]
    assert item[2] == '21'  # public_id
    assert item[3] == '50.00'  # price
    assert item[4] == 'None'  # promo_price

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()

    assert not options  # check if options is empty

    eats_cart_cursor.execute(
        'SELECT promo_id, amount, name, description, picture_uri, deleted_at '
        'FROM eats_cart.new_cart_item_discounts '
        'ORDER BY created_at;',
    )
    new_item_discounts = eats_cart_cursor.fetchall()

    assert len(new_item_discounts) == 1

    new_item_discount = utils.pg_result_to_repr(new_item_discounts)[0]
    assert new_item_discount[0] == '1'  # promo_id
    assert new_item_discount[1] == '10.00'  # amount
    assert new_item_discount[2] == 'default_name'  # name
    assert new_item_discount[3] == 'custom_descr'  # description
    assert new_item_discount[4] == 'default_picture'  # picture_uri
    assert new_item_discount[5] == 'None'  # deleted_at

    assert not response.json()['cart']['promo_items']
    assert response.json()['cart']['items'][0]['decimal_promo_price'] == '40'
    assert response.json()['cart']['items'][0]['decimal_price'] == '50'
    assert response.json()['cart']['decimal_subtotal'] == '100'
    assert response.json()['cart']['decimal_delivery_fee'] == '50'
    assert (
        response.json()['cart']['decimal_total'] == '130'
    )  # delivery_fee is 50 so decimal_total is 80 + 50


@pytest.mark.parametrize(
    '',
    (
        pytest.param(
            marks=pytest.mark.pgsql('eats_cart', files=['shop.sql']),
            id='fill_db',
        ),
        pytest.param(id='empty_db'),
    ),
)
@utils.discounts_applicator_enabled(False)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_post_discounts_experiment_disabled(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_cart_cursor,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID), '2', '1']
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 0
    assert local_services.mock_match_discounts.times_called == 0
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0
    assert local_services.mock_eats_tags.times_called == 0

    eats_cart_cursor.execute(utils.SELECT_ACTIVE_NEW_ITEM_DISCOUNTS)
    new_items_discount = eats_cart_cursor.fetchall()
    assert not new_items_discount


@pytest.mark.parametrize('send_business_type', (True, False))
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
async def test_post_discounts_retail(
        taxi_eats_cart,
        load_json,
        local_services,
        send_business_type,
        eats_order_stats,
):
    """Test that promo prices for shops are in `place_menu_item` object,
    as well as in cart item"""

    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    request_json = POST_BODY.copy()
    if send_business_type:
        request_json['place_business'] = 'shop'

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request_json,
    )
    assert response.status_code == 200

    place_menu_item = response.json()['cart']['items'][0]['place_menu_item']

    assert place_menu_item['promo_price'] == 40
    assert place_menu_item['decimal_promo_price'] == '40'

    assert place_menu_item['price'] == 50
    assert place_menu_item['decimal_price'] == '50'


@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['shop.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
async def test_put_existing_cart_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID), '1', '2']
    local_services.catalog_place_id = 123
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.put(
        'api/v1/cart/10',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=ITEM_PROPERTIES,
    )

    assert response.status_code == 200

    assert local_services.mock_eats_catalog_storage.times_called == 1
    assert local_services.mock_match_discounts.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0
    assert local_services.mock_eats_tags.times_called == 1

    response_json = response.json()
    del response_json['cart']['updated_at']
    del response_json['cart']['id']
    del response_json['cart']['revision']
    assert response_json == load_json('expected_shop.json')

    eats_cart_cursor.execute(utils.SELECT_NEW_ITEM_DISCOUNTS)
    new_items_discount = eats_cart_cursor.fetchall()
    assert len(new_items_discount) == 3
    new_discount = utils.pg_result_to_repr(new_items_discount)
    assert new_discount[0][0] == '23'  # promo_id
    assert new_discount[0][1] == '70.00'  # amount
    assert new_discount[0][2] == 'None'  # deleted_at
    assert new_discount[1][0] == '1'  # promo_id
    assert new_discount[1][1] == '10.00'  # amount
    assert new_discount[1][2] == 'None'  # deleted_at
    assert new_discount[2] == new_discount[1]


@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
async def test_post_discounts_promo_prices(
        taxi_eats_cart, load_json, local_services, eats_order_stats,
):
    """Test correct calculation of promo prices when item has both:
    partner discount and discount from eats-discounts"""
    menu_item_id = 2
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(menu_item_id)]
    local_services.core_items_request = [str(menu_item_id)]
    local_services.catalog_place_id = 123
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    request = dict(item_id=menu_item_id, **ITEM_PROPERTIES)
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request,
    )
    assert response.status_code == 200
    cart = response.json()['cart']
    assert cart['total'] == 76
    assert cart['subtotal'] == 80
    item = cart['items'][0]
    assert item['price'] == 40
    assert item['promo_price'] == 13
    assert item['promo_subtotal'] == '26'


@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.parametrize(
    'by_eater_id,by_phone_id',
    [
        pytest.param(False, False, id='turn off stats'),
        pytest.param(True, False, id='eater_id on'),
        pytest.param(False, True, id='phone_id on'),
        pytest.param(True, True, id='eater_id and phone_id on'),
    ],
)
@pytest.mark.now('2021-05-30T11:33:00+0000')
async def test_post_discounts_stats(
        mockserver,
        taxi_eats_cart,
        load_json,
        local_services,
        by_eater_id,
        by_phone_id,
):
    menu_item_id = 2
    place_id = 123
    brand_id = 1
    orders_count = 0
    time_from_last_order = None
    if by_eater_id:
        orders_count = 3
        time_from_last_order = 1440
    if by_phone_id:
        orders_count = 5
        time_from_last_order = 1440

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_eats_order_stats(json_request):
        groups = set(json_request.json['group_by'])
        identity_eater_id = json_request.json['identities'][0]
        counters_eater_id = []
        identity_phone_id = json_request.json['identities'][1]
        counters_phone_id = []
        if by_eater_id:
            counters_eater_id = [
                {
                    'first_order_at': '2021-05-28T10:12:00+0000',
                    'last_order_at': '2021-05-29T11:33:00+0000',
                    'properties': [
                        {'name': 'brand_id', 'value': str(brand_id)},
                        {'name': 'place_id', 'value': str(place_id)},
                        {'name': 'business_type', 'value': 'restaurant'},
                    ],
                    'value': 3,
                },
            ]
            if 'delivery_type' in groups:
                counters_eater_id[0]['properties'].append(
                    {'name': 'delivery_type', 'value': 'native'},
                )

        if by_phone_id:
            counters_phone_id = [
                {
                    'first_order_at': '2021-05-28T10:12:00+0000',
                    'last_order_at': '2021-05-29T11:33:00+0000',
                    'properties': [
                        {'name': 'brand_id', 'value': str(brand_id)},
                        {'name': 'place_id', 'value': str(place_id)},
                        {'name': 'business_type', 'value': 'restaurant'},
                    ],
                    'value': 5,
                },
            ]
            if 'delivery_type' in groups:
                counters_phone_id[0]['properties'].append(
                    {'name': 'delivery_type', 'value': 'native'},
                )

        return {
            'data': [
                {'counters': counters_eater_id, 'identity': identity_eater_id},
                {'counters': counters_phone_id, 'identity': identity_phone_id},
            ],
        }

    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(menu_item_id)]
    local_services.core_items_request = [str(menu_item_id)]
    local_services.catalog_place_id = place_id
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    discounts_resp = load_json('eats_discounts_response.json')
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    request = dict(item_id=menu_item_id, **ITEM_PROPERTIES)

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        assert (
            'orders_count' in request.json['common_conditions']['conditions']
        )
        assert request.json['common_conditions']['conditions'][
            'orders_count'
        ] == [orders_count]
        assert request.json['common_conditions']['conditions'][
            'restaurant_orders_count'
        ] == [orders_count]
        assert request.json['common_conditions']['conditions'][
            'retail_orders_count'
        ] == [0]
        if time_from_last_order:
            assert (
                'time_from_last_order'
                in request.json['common_conditions']['conditions']
            )
            assert request.json['common_conditions']['conditions'][
                'time_from_last_order'
            ] == [time_from_last_order]
        else:
            assert (
                'time_from_last_order'
                not in request.json['common_conditions']['conditions']
            )
        print(request.json['common_conditions']['conditions'])
        assert (
            'place_orders_count'
            in request.json['common_conditions']['conditions']
        )
        assert (
            'brand_orders_count'
            in request.json['common_conditions']['conditions']
        )
        assert request.json['common_conditions']['conditions'][
            'place_orders_count'
        ] == [orders_count]
        if time_from_last_order:
            assert request.json['common_conditions']['conditions'][
                'place_time_from_last_order'
            ] == [time_from_last_order]
        else:
            assert (
                'place_time_from_last_order'
                not in request.json['common_conditions']['conditions']
            )
        assert request.json['common_conditions']['conditions'][
            'brand_orders_count'
        ] == [orders_count]
        if time_from_last_order:
            assert request.json['common_conditions']['conditions'][
                'brand_time_from_last_order'
            ] == [time_from_last_order]
        else:
            assert (
                'brand_time_from_last_order'
                not in request.json['common_conditions']['conditions']
            )
        assert request.json['common_conditions']['conditions'][
            'shipping_types'
        ] == ['delivery']
        return discounts_resp

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request,
    )
    assert response.status_code == 200
    assert _mock_match_discounts.times_called == 1
    assert _mock_eats_order_stats.times_called == 2
    assert local_services.mock_eats_tags.times_called == 1


@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.matching_discounts_experiments(True, 'one_for_match')
@utils.matching_discounts_experiments(True, 'two_for_match')
@utils.matching_discounts_experiments(False, 'three_for_match')
@pytest.mark.now('2022-07-01T00:00:00+0000')
@utils.discounts_applicator_enabled(True)
async def test_discounts_request_experiments(
        mockserver,
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
):
    menu_item_id = 2
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(menu_item_id)]
    local_services.core_items_request = [str(menu_item_id)]
    local_services.catalog_place_id = 123
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    discounts_resp = load_json('eats_discounts_response.json')
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    request = dict(item_id=menu_item_id, **ITEM_PROPERTIES)

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        assert set(
            request.json['common_conditions']['conditions']['experiment'],
        ) == set(['one_for_match', 'two_for_match'])
        return discounts_resp

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=request,
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['additional_items.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
@pytest.mark.parametrize(
    'exp_pay_quant,exp_free_quant',
    [
        pytest.param(1, 0, id='1 item'),
        pytest.param(1, 1, id='2 items'),
        pytest.param(2, 1, id='3 items'),
        pytest.param(2, 2, id='4 items'),
        pytest.param(3, 2, id='5 items'),
        pytest.param(3, 3, id='6 items'),
    ],
)
async def test_additional_items_discount(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        exp_pay_quant,
        exp_free_quant,
):
    eats_order_stats()
    menu_item_id = '1'
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [menu_item_id]
    local_services.core_items_request = [menu_item_id]
    local_services.catalog_place_id = 123
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    ITEM_PROPERTIES['quantity'] = exp_pay_quant + exp_free_quant

    response = await taxi_eats_cart.put(
        'api/v1/cart/30',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=ITEM_PROPERTIES,
    )

    check_additional_items(response, exp_pay_quant, exp_free_quant)

    assert local_services.mock_eats_catalog_storage.times_called == 1
    assert local_services.mock_match_discounts.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0
    assert local_services.mock_eats_tags.times_called == 1

    response = await taxi_eats_cart.delete(
        'api/v1/cart/30',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=ITEM_PROPERTIES,
    )

    assert response.status_code == 200

    assert not response.json()['cart']['items']

    post_body = {
        'item_id': menu_item_id,
        'quantity': exp_pay_quant + exp_free_quant,
        'item_options': [],
        'shipping_type': 'delivery',
    }

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_body,
    )

    check_additional_items(response, exp_pay_quant, exp_free_quant)


@pytest.mark.parametrize(
    'exp_pay_quant,exp_free_quant',
    [
        pytest.param(1, 0, id='1 item'),
        pytest.param(1, 1, id='2 items'),
        pytest.param(2, 1, id='3 items'),
        pytest.param(2, 2, id='4 items'),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2021-06-22T15:58:18.4505+0000')
async def test_sync_with_additional_items(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        exp_pay_quant,
        exp_free_quant,
):
    eats_order_stats()
    menu_item_id = '1'
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [menu_item_id]
    local_services.core_items_request = [menu_item_id]
    local_services.catalog_place_id = 123
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    post_body = {
        'items': [
            {
                'item_id': menu_item_id,
                'quantity': exp_pay_quant + exp_free_quant,
                'item_options': [],
            },
        ],
        'shipping_type': 'delivery',
    }

    response = await taxi_eats_cart.post(
        '/api/v1/cart/sync',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_body,
    )

    check_additional_items(response, exp_pay_quant, exp_free_quant)


@pytest.mark.parametrize(
    'in_stock,exp_pay_quant,exp_free_quant',
    [
        pytest.param(4, 2, 2, id='4 in stock'),
        pytest.param(3, 2, 1, id='3 in stock'),
        pytest.param(2, 1, 1, id='2 in stock'),
        pytest.param(1, 1, 0, id='1 in stock'),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2021-06-22T15:58:18.4505+0000')
@pytest.mark.pgsql('eats_cart', files=['additional_items.sql'])
async def test_delete_disabled_items_with_additional(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        in_stock,
        exp_pay_quant,
        exp_free_quant,
):
    eats_order_stats()
    menu_item_id = '1'
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [menu_item_id]
    local_services.core_items_request = [menu_item_id]
    local_services.catalog_place_id = 123

    eats_products_json = load_json('eats_products_menu_items.json')
    # set 'in_stock'
    eats_products_json['place_menu_items'][1]['in_stock'] = in_stock
    local_services.eats_products_items_response = eats_products_json
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.delete(
        '/api/v1/cart/disabled-items',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status == 200

    check_additional_items(response, exp_pay_quant, exp_free_quant)


@utils.setup_available_features(['surge_info', 'new_refresh_policy'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    'show_threshold_discounts',
    [
        pytest.param(
            True,
            marks=utils.show_discounts(),
            id='show_threshold_delivery_discount',
        ),
        pytest.param(False, id='not_show_threshold_delivery_discount'),
    ],
)
@utils.delivery_discount_enabled()
@utils.additional_payment_text()
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_next_cost_discounts_fraction(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        show_threshold_discounts,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response_with_delivery.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response_post = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    response_get = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_post.json()['cart'] == response_get.json()
    assert (
        response_get.json()['additional_payments'][0]['original_amount']
        == '100 $SIGN$$CURRENCY$'
    )
    if show_threshold_discounts:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == {
                'color': [
                    {'theme': 'light', 'value': '#F5523A'},
                    {'theme': 'dark', 'value': '#F5523A'},
                ],
                'text': 'ещё 900₽ до -15% на доставку',
            }
        )
    else:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == SUBTITLE_WITHOUT_DISCOUNT
        )


@utils.setup_available_features(['surge_info', 'new_refresh_policy'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.delivery_discount_enabled()
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_next_cost_discounts_not_discount_now(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'delivery_discount.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response_post = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    response_get = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_post.json()['cart'] == response_get.json()
    assert (
        'original_amount' not in response_get.json()['additional_payments'][0]
    )


@utils.setup_available_features(['surge_info', 'new_refresh_policy'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.delivery_discount_enabled()
@pytest.mark.parametrize(
    'show_threshold_discounts',
    [
        pytest.param(
            True,
            marks=utils.show_discounts(),
            id='show_threshold_delivery_discount',
        ),
        pytest.param(False, id='not_show_threshold_delivery_discount'),
    ],
)
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_next_cost_discounts_absolute(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        show_threshold_discounts,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response_delivery.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response_post = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    response_get = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_post.json()['cart'] == response_get.json()
    if show_threshold_discounts:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == {
                'color': [
                    {'theme': 'light', 'value': '#F5523A'},
                    {'theme': 'dark', 'value': '#F5523A'},
                ],
                'text': 'ещё 900₽ до -50₽ на доставку',
            }
        )
    else:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == SUBTITLE_WITHOUT_DISCOUNT
        )


@utils.setup_available_features(['surge_info', 'new_refresh_policy'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.delivery_discount_enabled()
@pytest.mark.parametrize(
    'show_threshold_discounts',
    [
        pytest.param(
            True,
            marks=utils.show_discounts(),
            id='show_threshold_delivery_discount',
        ),
        pytest.param(False, id='not_show_threshold_delivery_discount'),
    ],
)
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
@pytest.mark.parametrize('same_threshold', [True, False])
async def test_next_cost_discounts_absolute_two_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        same_threshold,
        show_threshold_discounts,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response_two_delivery.json',
    )
    if same_threshold:
        local_services.eats_discounts_response = load_json(
            'eats_discounts_response_two_delivery_same_threshold.json',
        )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response_post = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    response_get = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_post.json()['cart'] == response_get.json()
    if not same_threshold and show_threshold_discounts:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == {
                'color': [
                    {'theme': 'light', 'value': '#F5523A'},
                    {'theme': 'dark', 'value': '#F5523A'},
                ],
                'text': 'ещё 800₽ до -90% на доставку',
            }
        )
    if show_threshold_discounts and same_threshold:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == {
                'color': [
                    {'theme': 'light', 'value': '#F5523A'},
                    {'theme': 'dark', 'value': '#F5523A'},
                ],
                'text': 'ещё 800₽ до -95₽ на доставку',
            }
        )
    if not show_threshold_discounts:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == SUBTITLE_WITHOUT_DISCOUNT
        )


@utils.setup_available_features(['surge_info', 'new_refresh_policy'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.delivery_discount_enabled()
@pytest.mark.parametrize(
    'show_threshold_discounts',
    [
        pytest.param(
            True,
            marks=utils.show_discounts(),
            id='show_threshold_delivery_discount',
        ),
        pytest.param(False, id='not_show_threshold_delivery_discount'),
    ],
)
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_next_cost_discounts_free(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        show_threshold_discounts,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response_delivery_free.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response_post = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    response_get = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_post.json()['cart'] == response_get.json()
    if show_threshold_discounts:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == {
                'color': [
                    {'theme': 'light', 'value': '#F5523A'},
                    {'theme': 'dark', 'value': '#F5523A'},
                ],
                'text': 'ещё 900₽ до бесплатной доставки',
            }
        )
    else:
        assert (
            response_post.json()['cart']['additional_payments'][0]['subtitle']
            == SUBTITLE_WITHOUT_DISCOUNT
        )


@utils.setup_available_features(['surge_info', 'new_refresh_policy'])
@pytest.mark.config(EATS_REWARD_COMPOSER_MAX_THRESHOLD={'RUB': 799})
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.delivery_discount_enabled()
@utils.show_discounts()
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_not_show_discounts_max_threshold(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response_delivery_free.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response_post = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    response_get = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_post.json()['cart'] == response_get.json()
    assert (
        response_post.json()['cart']['additional_payments'][0]['subtitle']
        == SUBTITLE_WITHOUT_DISCOUNT
    )
