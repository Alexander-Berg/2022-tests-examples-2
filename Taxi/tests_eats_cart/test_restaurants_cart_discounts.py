# pylint: disable=too-many-lines
import decimal

import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323

POST_BODY = dict(
    item_id=MENU_ITEM_ID, place_business='restaurant', **utils.ITEM_PROPERTIES,
)


async def add_item_and_check_cart_promo(
        iteration_number, taxi_eats_cart, eats_cart_cursor, local_services,
):

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=2, shipping_type='delivery'),
    )

    assert response.status_code == 200

    assert (
        local_services.mock_match_discounts.times_called
        == 2 * iteration_number
    )
    assert (
        local_services.mock_eats_core_menu.times_called == 1 * iteration_number
    )
    assert (
        local_services.mock_eats_catalog.times_called == 1 * iteration_number
    )
    assert local_services.mock_eats_core_discount.times_called == 0

    delivery_fee = 0 if iteration_number > 1 else 10
    subtotal = 50.0 + iteration_number * 100
    promo = subtotal / 10

    eats_cart_cursor.execute(
        utils.select_new_cart_discount(
            cart_id='00000000000000000000000000000001',
        ),
    )
    new_cart_discount = eats_cart_cursor.fetchall()
    assert len(new_cart_discount) == 2
    new_discount = utils.pg_result_to_repr(new_cart_discount)
    assert new_discount[0][0] == '2'  # promo_id
    assert new_discount[0][1] == '10.00'  # amount
    assert new_discount[0][2] != 'None'  # deleted_at

    assert new_discount[1][0] == '1111'  # promo_id
    assert decimal.Decimal(new_discount[1][1]) == decimal.Decimal(
        promo,
    )  # amount
    assert new_discount[1][2] == 'None'  # deleted_at

    response_json = response.json()['cart']

    assert response_json['promo_items'] == [
        {
            'amount': int(promo),
            'decimal_amount': str(int(promo)),
            'name': 'zagolovok',
            'picture_uri': (
                '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png'
            ),
            'type': '104',
        },
    ]

    assert response_json['promos'] == [
        {
            'description': 'podzagolok',
            'name': 'zagolovok',
            'picture_uri': (
                '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png'
            ),
        },
    ]

    assert response_json['decimal_total'] == str(
        int(subtotal + delivery_fee - promo),
    )
    assert response_json['decimal_subtotal'] == str(int(subtotal))


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_cart_discount.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    await add_item_and_check_cart_promo(
        1, taxi_eats_cart, eats_cart_cursor, local_services,
    )
    await add_item_and_check_cart_promo(
        2, taxi_eats_cart, eats_cart_cursor, local_services,
    )


@utils.use_new_disc_for_rest_exp()
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.parametrize(
    'dynamic_price_percent, dynamic_price_value',
    [
        pytest.param(
            10,
            None,
            marks=[
                utils.dynamic_prices(10),
                pytest.mark.smart_prices_cache({'123': 100}),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            10,
            None,
            marks=[
                utils.dynamic_prices(100),
                pytest.mark.smart_prices_cache({'123': 10}),
            ],
            id='dynamic_prices_100_10',
        ),
        pytest.param(
            None,
            27,
            marks=[
                utils.dynamic_prices(),
                pytest.mark.smart_prices_cache({'123': 100}),
                pytest.mark.smart_prices_items(
                    {
                        '123': {
                            'updated_at': '2022-04-01T00:00:00Z',
                            'items': {
                                '232323': {'default_tag': '27'},
                                '1': {'default_tag': '27'},
                            },
                        },
                    },
                ),
            ],
            id='dynamic_prices_by_items_less_than_max',
        ),
        pytest.param(
            10,
            None,
            marks=[
                utils.dynamic_prices(),
                pytest.mark.smart_prices_cache({'123': 10}),
                pytest.mark.smart_prices_items(
                    {
                        '123': {
                            'updated_at': '2022-04-01T00:00:00Z',
                            'items': {
                                '232323': {'default_tag': '27'},
                                '1': {'default_tag': '27'},
                            },
                        },
                    },
                ),
            ],
            id='dynamic_prices_by_items_more_than_max',
        ),
        pytest.param(
            None,
            None,
            marks=pytest.mark.smart_prices_cache({'123': 10}),
            id='dynamic_prices_off_by_exp',
        ),
        pytest.param(
            None,
            None,
            marks=utils.dynamic_prices(10),
            id='dynamic_prices_off_by_service',
        ),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_gift_items(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        dynamic_price_percent,
        dynamic_price_value,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_gift_item.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=2, shipping_type='delivery'),
    )

    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(
        utils.select_new_cart_discount(
            cart_id='00000000000000000000000000000001',
        ),
    )

    new_cart_discount = eats_cart_cursor.fetchall()
    assert len(new_cart_discount) == 1
    new_discount = utils.pg_result_to_repr(new_cart_discount)
    assert new_discount[0][0] == '2'  # promo_id
    assert new_discount[0][1] == '10.00'  # amount
    assert new_discount[0][2] != 'None'  # deleted_at

    response_json = response.json()['cart']

    assert len(response_json['items']) == 2
    assert response_json['items'][1]['item_id'] == 232323
    assert response_json['items'][1]['promo_type'] == {
        'id': 105,
        'name': 'zagolovok',
        'picture_uri': '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png',
    }

    assert not response_json['promo_items']

    assert response_json['promos'] == [
        {
            'description': 'podzagolok',
            'name': 'zagolovok',
            'picture_uri': (
                '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png'
            ),
        },
    ]

    assert response_json['decimal_total'] == '160'
    assert response_json['decimal_subtotal'] == '150'

    eats_cart_cursor.execute(utils.SELECT_NEW_ITEM_DISCOUNTS)
    new_item_discounts = eats_cart_cursor.fetchall()
    assert len(new_item_discounts) == 5
    new_item_discount = utils.pg_result_to_repr(new_item_discounts)
    assert new_item_discount[4][0] == '1111'  # promo_id

    dynamic_price = 50.0  # item_price
    if dynamic_price_percent:
        dynamic_price *= (100 + dynamic_price_percent) / 100.0
    elif dynamic_price_value:
        dynamic_price += dynamic_price_value

    dynamic_price_part = (
        '{0:.2f}'.format(dynamic_price - 50.0)
        if (dynamic_price_percent or dynamic_price_value)
        else 'None'
    )
    dynamic_price_str = '{0:.2f}'.format(dynamic_price)

    assert new_item_discount[4][1] == dynamic_price_str  # amount
    assert new_item_discount[4][2] == 'None'  # deleted_at

    eats_cart_cursor.execute(
        'SELECT place_menu_item_id, price, '
        'promo_price, quantity, dynamic_price_part FROM eats_cart.cart_items '
        'WHERE deleted_at is NULL '
        'AND cart_id = \'00000000000000000000000000000001\' '
        'ORDER BY created_at;',
    )
    cart_items = eats_cart_cursor.fetchall()
    cart_item = utils.pg_result_to_repr(cart_items)
    assert cart_item == [
        # because not new item
        ['232323', '50.00', 'None', '3', 'None'],
        ['232323', dynamic_price_str, 'None', '1', dynamic_price_part],
    ]

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=2, shipping_type='delivery'),
    )

    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 2 + 3
    assert local_services.mock_eats_core_menu.times_called == 1 + 2
    assert local_services.mock_eats_catalog.times_called == 1 + 1
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(
        utils.select_new_cart_discount(
            cart_id='00000000000000000000000000000001',
        ),
    )

    new_cart_discount = eats_cart_cursor.fetchall()
    assert len(new_cart_discount) == 1
    new_discount = utils.pg_result_to_repr(new_cart_discount)
    assert new_discount[0][0] == '2'  # promo_id
    assert new_discount[0][1] == '10.00'  # amount
    assert new_discount[0][2] != 'None'  # deleted_at

    response_json = response.json()['cart']

    assert len(response_json['items']) == 2
    gift_item = response_json['items'][1]
    assert gift_item['item_id'] == 1
    assert gift_item['promo_type'] == {
        'id': 105,
        'name': 'zagolovok',
        'picture_uri': '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png',
    }
    assert gift_item['price'] == 0
    assert gift_item['decimal_price'] == '0'
    assert gift_item['subtotal'] == '0'
    assert 'promo_price' not in gift_item
    assert 'decimal_promo_price' not in gift_item
    assert 'promo_subtotal' not in gift_item

    assert not response_json['promo_items']

    assert response_json['promos'] == [
        {
            'description': 'podzagolok',
            'name': 'zagolovok',
            'picture_uri': (
                '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png'
            ),
        },
    ]

    assert response_json['decimal_total'] == '250'
    assert response_json['decimal_subtotal'] == '250'

    eats_cart_cursor.execute(utils.SELECT_NEW_ITEM_DISCOUNTS)
    new_item_discounts = eats_cart_cursor.fetchall()
    assert len(new_item_discounts) == 6
    new_item_discount = utils.pg_result_to_repr(new_item_discounts)
    assert new_item_discount[5][0] == '1111'  # promo_id

    dynamic_price = 70.0  # item_price
    if dynamic_price_percent:
        dynamic_price *= (100 + dynamic_price_percent) / 100.0
    elif dynamic_price_value:
        dynamic_price += dynamic_price_value

    dynamic_price_part = (
        '{0:.2f}'.format(dynamic_price - 70.0)
        if (dynamic_price_percent or dynamic_price_value)
        else 'None'
    )
    dynamic_price_str = '{0:.2f}'.format(dynamic_price)

    assert new_item_discount[5][1] == dynamic_price_str  # amount
    assert new_item_discount[5][2] == 'None'  # deleted_at

    eats_cart_cursor.execute(
        'SELECT place_menu_item_id, price, '
        'promo_price, quantity, dynamic_price_part FROM eats_cart.cart_items '
        'WHERE deleted_at is NULL '
        'AND cart_id = \'00000000000000000000000000000001\' '
        'ORDER BY created_at;',
    )
    cart_items = eats_cart_cursor.fetchall()
    cart_item = utils.pg_result_to_repr(cart_items)
    assert cart_item == [
        ['232323', '50.00', 'None', '5', 'None'],
        ['1', dynamic_price_str, 'None', '3', dynamic_price_part],
    ]


@utils.use_new_disc_for_rest_exp()
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@utils.exclude_discounts(['place_cart_discounts'], [])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_disabled(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_cart_discount.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=2, shipping_type='delivery'),
    )

    assert response.status_code == 200

    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(
        utils.select_new_cart_discount(
            cart_id='00000000000000000000000000000001',
        ),
    )
    new_cart_discount = eats_cart_cursor.fetchall()
    assert len(new_cart_discount) == 1

    response_json = response.json()['cart']

    assert not response_json['promo_items']
    assert not response_json['promos']

    assert response_json['decimal_subtotal'] == '150'
    assert response_json['decimal_total'] == '160'  # delivery_fee=10


HEADERS = {
    'X-YaTaxi-Session': 'eats:',
    'X-YaTaxi-Bound-UserIds': '',
    'X-YaTaxi-Bound-Sessions': '',
    'X-Eats-User': f'user_id={EATER_ID},',
}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@utils.setup_available_checkers(['CheckActualDiscount'])
@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['lock_cart.sql'])
@pytest.mark.parametrize(
    'discount_id,fail_checker',
    [
        pytest.param(
            '1111',
            False,
            marks=utils.delivery_discount_enabled(),
            id='right_promo_id',
        ),
        pytest.param('22222', True, id='new_promo_id'),
    ],
)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_lock_cart(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        discount_id,
        fail_checker,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    mock_discount = load_json('eats_discounts_cart_discount_lock_cart.json')
    mock_discount['match_results'][0]['discount_id'] = discount_id
    local_services.eats_discounts_response = mock_discount
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await utils.call_lock_cart(taxi_eats_cart, EATER_ID, HEADERS)

    assert local_services.mock_match_discounts.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_core_discount.times_called == 0

    if fail_checker:
        assert response.status_code == 400
        return

    assert response.status_code == 200
    response_json = response.json()

    assert response_json['applied_checkers'] == ['CheckActualDiscount']
    assert response_json['items'] == [
        {
            'id': '232323',
            'new_promos': [],
            'options': [],
            'price': '50',
            'quantity': 5,
            'dynamic_part_amount': '10',
            'is_gift': False,
        },
        {
            'id': '1',
            'new_promos': [
                {
                    'amount': '70',
                    'discount_provider': 'place',
                    'promo_id': '1111',
                },
            ],
            'options': [],
            'price': '70',
            'promo_price': '0',
            'quantity': 3,
            'is_gift': True,
        },
    ]

    assert response_json['new_promos'] == [
        {'amount': '25', 'discount_provider': 'place', 'promo_id': '1111'},
    ]

    assert response_json['subtotal'] == '250'
    assert response_json['total'] == '225'


@pytest.mark.parametrize(
    'eater_id',
    [
        pytest.param('eater3', id='old cart promo'),
        pytest.param('eater4', id='old gift item'),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@utils.setup_available_checkers(['CheckActualDiscount'])
@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['lock_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_fail_checkers(
        taxi_eats_cart, load_json, local_services, eats_order_stats, eater_id,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    local_services.eats_discounts_response = load_json(
        'eats_discounts_cart_discount_lock_cart.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await utils.call_lock_cart(taxi_eats_cart, eater_id, HEADERS)

    assert response.status_code == 400

    assert local_services.mock_match_discounts.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_core_discount.times_called == 0


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
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
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_free_and_gift_item(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        not_show_discounts,
):
    expected_promo_items = []
    if not not_show_discounts:
        expected_promo_items = [
            {
                'amount': 100,
                'decimal_amount': '100',
                'name': 'product_promo',
                'picture_uri': 'some_uri',
                'type': 'discount',
            },
        ]

    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_gift_and_free_item.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater3'),
        json=dict(item_id=MENU_ITEM_ID, quantity=2, shipping_type='delivery'),
    )

    assert response.status_code == 200

    assert local_services.mock_match_discounts.times_called == 2

    assert local_services.mock_eats_core_menu.times_called == 1

    assert local_services.mock_eats_catalog.times_called == 1

    assert local_services.mock_eats_core_discount.times_called == 0

    response_json = response.json()['cart']

    assert response_json['promo_items'] == expected_promo_items  # 2by1 for 5

    assert response_json['promos'] == [
        {
            'description': 'podzagolok',
            'name': 'zagolovok',
            'picture_uri': (
                '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png'
            ),
        },
        {
            'description': 'Описание',
            'name': 'product_promo',
            'picture_uri': 'some_uri',
        },
    ]

    assert response_json['decimal_subtotal'] == '250'
    assert response_json['decimal_total'] == '160'  # delivery_fee=10

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater3'),
        json=dict(item_id=MENU_ITEM_ID, quantity=6, shipping_type='delivery'),
    )

    assert response.status_code == 200

    assert local_services.mock_match_discounts.times_called == 5

    assert local_services.mock_eats_core_menu.times_called == 3

    assert local_services.mock_eats_catalog.times_called == 2

    assert local_services.mock_eats_core_discount.times_called == 0

    response_json = response.json()['cart']

    if not not_show_discounts:
        expected_promo_items = [
            {
                'amount': 250,
                'decimal_amount': '250',
                'name': 'product_promo',
                'picture_uri': 'some_uri',
                'type': 'discount',
            },
        ]

    assert response_json['promo_items'] == expected_promo_items  # 2by1 for 5

    assert response_json['promos'] == [
        {
            'description': 'podzagolok',
            'name': 'zagolovok',
            'picture_uri': (
                '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png'
            ),
        },
        {
            'description': 'Описание',
            'name': 'product_promo',
            'picture_uri': 'some_uri',
        },
    ]

    assert response_json['decimal_subtotal'] == '550'
    assert response_json['decimal_total'] == '300'  # delivery_fee=0


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_disable_items(
        taxi_eats_cart, load_json, local_services, eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123

    mock_core_menu = load_json('eats_core_menu_items.json')
    mock_core_menu['place_menu_items'][1]['available'] = False
    local_services.core_items_response = mock_core_menu
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_gift_item.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.delete(
        '/api/v1/cart/disabled-items',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater4'),
    )

    assert response.status == 200

    response_json = response.json()['cart']

    assert not response_json['promo_items']
    assert not response_json['promos']
    assert len(response_json['items']) == 1

    assert local_services.mock_match_discounts.times_called == 2

    assert local_services.mock_eats_core_menu.times_called == 1

    assert local_services.mock_eats_catalog.times_called == 1

    assert local_services.mock_eats_core_discount.times_called == 0


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
async def test_new_cart_discounts_reset_cart(
        taxi_eats_cart, load_json, local_services, eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_gift_item.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater5'),
        json=dict(item_id=MENU_ITEM_ID, quantity=1, shipping_type='delivery'),
    )

    assert response.status_code == 200

    response_json = response.json()['cart']

    assert not response_json['promos']
    assert not response_json['promo_items']


@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
async def test_new_cart_discount_get_cart(
        taxi_eats_cart, load_json, local_services, eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_gift_item.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.get(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater6'),
    )

    assert response.status_code == 200

    response_json = response.json()

    assert len(response_json['promos']) == 2


@utils.use_new_disc_for_rest_exp()
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_put_gift_item(
        taxi_eats_cart, load_json, local_services, eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_gift_item.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.put(
        '/api/v1/cart/96',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater7'),
        json=dict(quantity=4, shipping_type='delivery'),
    )
    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    response_json = response.json()['cart']
    assert len(response_json['items']) == 3
    assert response_json['items'][1]['item_id'] == 1
    assert response_json['items'][1]['quantity'] == 1
    assert 'promo_type' not in response_json['items'][1]
    assert response_json['items'][2]['item_id'] == 1
    assert response_json['items'][2]['quantity'] == 3
    assert response_json['items'][2]['promo_type']

    response = await taxi_eats_cart.put(
        '/api/v1/cart/96',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater7'),
        json=dict(quantity=4, shipping_type='delivery'),
    )

    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 4
    assert local_services.mock_eats_core_menu.times_called == 2
    assert local_services.mock_eats_catalog.times_called == 2
    assert local_services.mock_eats_core_discount.times_called == 0

    response_json = response.json()['cart']
    # item_id=1 will be first because of its cart_item_id
    assert len(response_json['items']) == 3
    assert response_json['items'][0]['item_id'] == 1
    assert response_json['items'][0]['quantity'] == 2
    assert 'promo_type' not in response_json['items'][0]
    assert response_json['items'][2]['item_id'] == 1
    assert response_json['items'][2]['quantity'] == 3
    assert response_json['items'][2]['promo_type']


@utils.use_new_disc_for_rest_exp()
@pytest.mark.parametrize(
    'should_merge',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_CART_PROMO_TYPE_IDS_TO_MERGE_PROMO_ITEMS=['104'],
            ),
            id='merge_discounts',
        ),
        pytest.param(False, id='not_merge'),
    ],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@utils.not_show_row_discount()
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_merge(
        taxi_eats_cart,
        load_json,
        should_merge,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_cofinance.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=2, shipping_type='delivery'),
    )

    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    cart_response = response.json()['cart']

    if should_merge:
        assert cart_response['promo_items'] == [
            {
                'name': 'place_name',
                'picture_uri': 'place_picture',
                'amount': 24,
                'decimal_amount': '24.8',
                'type': '104',
            },
        ]
        assert cart_response['promos'] == [
            {
                'name': 'place_name',
                'picture_uri': 'place_picture',
                'description': 'place_descr',
            },
        ]
    else:
        assert cart_response['promo_items'] == [
            {
                'name': 'place_name',
                'picture_uri': 'place_picture',
                'amount': 12,
                'decimal_amount': '12.6',
                'type': '104',
            },
            {
                'name': 'yandex_name',
                'picture_uri': 'yandex_picture',
                'amount': 12,
                'decimal_amount': '12.2',
                'type': '104',
            },
        ]
        assert cart_response['promos'] == [
            {
                'name': 'place_name',
                'picture_uri': 'place_picture',
                'description': 'place_descr',
            },
            {
                'name': 'yandex_name',
                'picture_uri': 'yandex_picture',
                'description': 'yandex_descr',
            },
        ]


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.setup_available_features(['surge_info', 'new_cart_discounts'])
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_cart_discounts_similar_items(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID), '1']
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.eats_discounts_response = load_json(
        'eats_discounts_item_discount.json',
    )
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=1, shipping_type='delivery'),
    )

    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    response_json = response.json()['cart']
    cart_id = response_json['id']

    eats_cart_cursor.execute(utils.select_new_cart_discount(cart_id=cart_id))

    new_cart_discount = eats_cart_cursor.fetchall()
    assert not new_cart_discount

    assert len(response_json['items']) == 1
    assert response_json['items'][0]['item_id'] == 232323
    assert response_json['promo_items'] == [
        {
            'amount': 10,
            'decimal_amount': '10',
            'name': 'money_promo',
            'picture_uri': 'some_uri',
            'type': 'discount',
        },
    ]

    assert response_json['promos'] == [
        {
            'description': 'Описание',
            'name': 'money_promo',
            'picture_uri': 'some_uri',
        },
    ]

    assert response_json['decimal_total'] == '90'
    assert response_json['decimal_subtotal'] == '50'

    eats_cart_cursor.execute(utils.SELECT_NEW_ITEM_DISCOUNTS)
    new_item_discounts = eats_cart_cursor.fetchall()
    assert len(new_item_discounts) == 1
    new_item_discount = utils.pg_result_to_repr(new_item_discounts)
    assert new_item_discount[0][0] == '5'  # promo_id
    assert new_item_discount[0][1] == '10.00'  # amount
    assert new_item_discount[0][2] == 'None'  # deleted_at

    eats_cart_cursor.execute(
        'SELECT place_menu_item_id, price, '
        'promo_price, quantity, dynamic_price_part FROM eats_cart.cart_items '
        'WHERE deleted_at is NULL '
        f'AND cart_id = \'{cart_id}\' '
        'ORDER BY created_at;',
    )
    cart_items = eats_cart_cursor.fetchall()
    cart_item = utils.pg_result_to_repr(cart_items)
    assert cart_item == [
        # because not new item
        ['232323', '50.00', 'None', '1', 'None'],
    ]

    response = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=MENU_ITEM_ID, quantity=1, shipping_type='delivery'),
    )

    assert response.status_code == 200
    assert local_services.mock_match_discounts.times_called == 2 + 2
    assert local_services.mock_eats_core_menu.times_called == 1 + 1
    assert local_services.mock_eats_catalog.times_called == 1 + 1
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(utils.select_new_cart_discount(cart_id=cart_id))

    new_cart_discount = eats_cart_cursor.fetchall()
    assert not new_cart_discount

    response_json = response.json()['cart']

    assert len(response_json['items']) == 1

    assert response_json['promo_items'] == [
        {
            'amount': 20,
            'decimal_amount': '20',
            'name': 'money_promo',
            'picture_uri': 'some_uri',
            'type': 'discount',
        },
    ]

    assert response_json['promos'] == [
        {
            'description': 'Описание',
            'name': 'money_promo',
            'picture_uri': 'some_uri',
        },
    ]

    assert response_json['decimal_total'] == '130'
    assert response_json['decimal_subtotal'] == '100'

    eats_cart_cursor.execute(utils.SELECT_NEW_ITEM_DISCOUNTS)
    new_item_discounts = eats_cart_cursor.fetchall()
    assert len(new_item_discounts) == 2
    new_item_discount = utils.pg_result_to_repr(new_item_discounts)
    assert new_item_discount[0][2] != 'None'  # deleted_at
    assert new_item_discount[1][0] == '5'  # promo_id
    assert new_item_discount[1][1] == '10.00'  # amount
    assert new_item_discount[1][2] == 'None'  # deleted_at

    eats_cart_cursor.execute(
        'SELECT place_menu_item_id, price, '
        'promo_price, quantity, dynamic_price_part FROM eats_cart.cart_items '
        'WHERE deleted_at is NULL '
        f'AND cart_id = \'{cart_id}\' '
        'ORDER BY created_at;',
    )
    cart_items = eats_cart_cursor.fetchall()
    cart_item = utils.pg_result_to_repr(cart_items)
    assert cart_item == [['232323', '50.00', 'None', '2', 'None']]
