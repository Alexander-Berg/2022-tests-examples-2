# pylint: disable=too-many-lines
import copy
import decimal

import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323

POST_BODY = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
EMPTY_PROPERTIES = {'quantity': 1, 'item_options': []}


@pytest.mark.parametrize(
    'correct_core_response',
    [
        pytest.param(False, id='eats_core_api_fault'),
        pytest.param(True, id='eats_core_bad_request'),
    ],
)
@pytest.mark.parametrize(
    'ids_converter',
    [pytest.param(str, id='id_as_string'), pytest.param(int, id='id_as_int')],
)
async def test_post_non_exisiting_item(
        taxi_eats_cart,
        local_services,
        load_json,
        correct_core_response,
        ids_converter,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    if correct_core_response:
        local_services.core_items_status = 400
        local_services.core_items_response = {
            'error': 'place_menu_items_not_found',
            'message': str(MENU_ITEM_ID),
        }
    else:
        resp = load_json('eats_core_menu_items.json')
        resp['place_menu_items'][0]['id'] = MENU_ITEM_ID + 1
        local_services.core_items_response = resp

    body = utils.convert_item_ids(copy.deepcopy(POST_BODY), ids_converter)

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=body,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 5,
        'domain': 'UserData',
        'err': 'Неверный формат',
        'errors': {'item_id': ['menu item 232323  не существует']},
    }
    assert local_services.mock_eats_core_menu.times_called == 1


@pytest.mark.parametrize(
    'discount_client_available',
    [
        pytest.param(False, id='unavailable_discounts'),
        pytest.param(True, id='available_discounts'),
    ],
)
@pytest.mark.parametrize(
    'ids_converter',
    [pytest.param(str, id='id_as_string'), pytest.param(int, id='id_as_int')],
)
@utils.additional_payment_text()
async def test_post_no_cart_exists(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        discount_client_available,
        ids_converter,
):
    local_services.set_available_discounts(discount_client_available)
    local_services.core_discounts_response = load_json(
        'get_proper_discount.json',
    )
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    plus_response = load_json('eats_plus_cashback.json')
    del plus_response['cashback_outcome_details']
    local_services.set_plus_response(status=200, json=plus_response)
    local_services.set_params(utils.get_params())

    body = utils.convert_item_ids(copy.deepcopy(POST_BODY), ids_converter)
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID, yandex_uid='uid0'),
        json=body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    cart_id = result[0]['id']
    assert utils.pg_result_to_repr(result)[0][1:] == [
        '2',
        'eater2',
        'place123',
        '123',
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

    expected_json = load_json('expected_with_options.json')
    expected_json['item_id'] = MENU_ITEM_ID
    expected_json['id'] = int(cart_item_id)
    expected_json['cart']['items'][0]['id'] = int(cart_item_id)

    response_json = response.json()
    del response_json['cart']['updated_at']
    response_json['cart']['promo_items'] = []
    response_json['cart']['promos'] = []

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


@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_post_discounts(
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
    local_services.core_items_request = [str(MENU_ITEM_ID), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
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
    assert len(cart_items) == 5
    res = {}
    cart_item_id = str(cart_items[-2]['id'])
    promo_item_id = str(cart_items[-1]['id'])
    for i in utils.pg_result_to_repr(cart_items):
        res[(i[2], i[3])] = (i[4], i[6])
    assert res[('232323', '0.00')] == ('None', 'None')
    assert res[('232323', '50.00')] == ('48.95', 'None')
    assert res[('1', '100.00')][1] != 'None'
    assert res[('2', '100.00')] == ('None', 'None')

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert len(options) == 6
    assert utils.pg_result_to_repr(options) == [
        [cart_item_id, '1679268432', '3.98', '2.33', '1'],
        [cart_item_id, '1679268437', '2.00', 'None', '1'],
        [cart_item_id, '1679268442', '3.00', 'None', '2'],
        [promo_item_id, '1679268432', '0.00', 'None', '1'],
        [promo_item_id, '1679268437', '0.00', 'None', '1'],
        [promo_item_id, '1679268442', '0.00', 'None', '2'],
    ]

    assert response.json()['cart']['promos']
    assert len(response.json()['cart']['promo_items']) is not None


@pytest.mark.parametrize(
    'dynamic_price_percent, dynamic_price_value',
    [
        pytest.param(
            10,
            None,
            marks=[
                utils.dynamic_prices(10),
                pytest.mark.smart_prices_cache({'123': 99}),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            10,
            None,
            marks=[
                utils.dynamic_prices(99),
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
                            'items': {'232323': {'default_tag': '27'}},
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
                pytest.mark.smart_prices_cache({'123': 9.9}),
                pytest.mark.smart_prices_items(
                    {
                        '123': {
                            'updated_at': '2022-04-01T00:00:00Z',
                            'items': {'232323': {'default_tag': '27'}},
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
@pytest.mark.parametrize(
    'round_config',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_SMART_PRICES_ROUND={'enabled': True},
            ),
            id='turn_on_round_config',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_SMART_PRICES_ROUND={'enabled': False},
            ),
            id='turn_off_round_config',
        ),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_post_discounts_with_smart_price(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        dynamic_price_percent,
        dynamic_price_value,
        round_config,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_discounts_response = load_json('get_discount.json')
    del local_services.core_discounts_response['items'][0]['promo_price']
    local_services.core_items_request = [str(MENU_ITEM_ID), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    del local_services.core_items_response['place_menu_items'][0][
        'decimalPromoPrice'
    ]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
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

    eats_cart_cursor.execute(
        'SELECT id, cart_id, place_menu_item_id, price, dynamic_price_part, '
        'promo_price, quantity, deleted_at FROM eats_cart.cart_items '
        f'WHERE cart_id = \'00000000000000000000000000000000\''
        'ORDER BY id;',
    )
    cart_items = eats_cart_cursor.fetchall()
    assert len(cart_items) == 4
    res = {}
    cart_item_id = str(cart_items[-2]['id'])
    promo_item_id = str(cart_items[-1]['id'])
    for i in cart_items:
        res[(str(i['place_menu_item_id']), str(i['price']))] = (
            str(i['promo_price']),
            str(i['deleted_at']),
            str(i['dynamic_price_part']),
            i['quantity'],
        )
    paid_price = 50

    if dynamic_price_percent:
        if not round_config and dynamic_price_percent == 10:
            dynamic_price_percent = 9.9
        paid_price = 50.0 * (100.0 + dynamic_price_percent) / 100.0
    elif dynamic_price_value:
        paid_price += dynamic_price_value
    paid_price_str = '{0:.2f}'.format(paid_price)
    dynamic_price_part = (
        '{0:.2f}'.format(paid_price - 50.0)
        if (dynamic_price_percent and dynamic_price_percent > 0)
        or (dynamic_price_value and dynamic_price_value > 0)
        else 'None'
    )
    assert res[('232323', '0.00')] == ('None', 'None', 'None', 1)
    assert res[('232323', paid_price_str)] == (
        'None',
        'None',
        dynamic_price_part,
        2,
    )
    assert res[('1', '100.00')][1] != 'None'
    assert res[('2', '100.00')] == ('None', 'None', 'None', 1)

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert len(options) == 6
    assert utils.pg_result_to_repr(options) == [
        [cart_item_id, '1679268432', '3.98', '2.33', '1'],
        [cart_item_id, '1679268437', '2.00', 'None', '1'],
        [cart_item_id, '1679268442', '3.00', 'None', '2'],
        [promo_item_id, '1679268432', '0.00', 'None', '1'],
        [promo_item_id, '1679268437', '0.00', 'None', '1'],
        [promo_item_id, '1679268442', '0.00', 'None', '2'],
    ]

    assert (
        response.json()['cart']['items'][0]['decimal_promo_price']
        == '{:g}'.format(paid_price + 10.33)
    )  # add options price


@pytest.mark.parametrize(
    'delivery_fee, eda_part, place_part',
    [
        pytest.param(
            '0',
            '20',
            None,
            marks=utils.delivery_discount_enabled(),
            id='eda_discount',
        ),
        pytest.param(
            '0',
            None,
            '20',
            marks=utils.delivery_discount_enabled(),
            id='place_discount',
        ),
        pytest.param(
            '20',
            None,
            None,
            marks=utils.delivery_discount_enabled(),
            id='no_discount_by_eats_discounts',
        ),
        pytest.param('20', None, None, id='no_discount_by_exp'),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.discounts_applicator_enabled(True),
            id='apply_item_discounts_on',
        ),
        pytest.param(id='apply_item_discounts_off'),
    ],
)
@pytest.mark.parametrize('with_surge', [True, False])
@utils.setup_available_features(['surge_info'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_post_delivery_discount(
        mockserver,
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        delivery_fee,
        eda_part,
        place_part,
        with_surge,
        eats_order_stats,
):
    eats_order_stats()
    local_services.available_discounts = True
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    catalog_response = load_json('eats_catalog_internal_place.json')
    if with_surge:
        surge_info = {
            'delivery_fee': '20',
            'additional_fee': '10.11',
            'level': 1,
        }
        catalog_response['place']['surge_info'] = surge_info
    local_services.catalog_place_response = catalog_response

    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.catalog_place_id = 123
    discounts_resp = load_json('eats_discounts_free_delivery.json')
    if not place_part:
        del discounts_resp['match_results'][-1]
    if not eda_part:
        del discounts_resp['match_results'][0]

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        assert 'check' in request.json['common_conditions']['conditions']
        assert 'surge_range' in request.json['common_conditions']['conditions']
        assert (
            'delivery_method'
            in request.json['common_conditions']['conditions']
        )
        assert (
            'shipping_types' in request.json['common_conditions']['conditions']
        )
        return discounts_resp

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 200

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount, payload FROM eats_cart.extra_fees'
        ' ORDER BY cart_id, type',
    )
    extra_fees = eats_cart_cursor.fetchall()

    assert len(extra_fees) == 1
    db_delivery_fee = extra_fees[0]
    assert db_delivery_fee['type'] == 'delivery_fee'
    assert 'payload' in db_delivery_fee
    if eda_part:
        assert 'eda_discount' in db_delivery_fee['payload']
        assert db_delivery_fee['payload']['eda_discount']['amount'] == eda_part

    if place_part:
        assert 'place_discount' in db_delivery_fee['payload']
        assert (
            db_delivery_fee['payload']['place_discount']['amount']
            == place_part
        )

    resp = response.json()['cart']
    assert resp['decimal_delivery_fee'] == delivery_fee
    assert (
        resp['additional_payments'][0]['amount']['amount']
        == delivery_fee + ' $SIGN$$CURRENCY$'
    )
    assert ('surge' in resp) == with_surge
    if delivery_fee == 0:
        for color in resp['additional_payments'][0]['amount']['color']:
            assert color['value'] == '#F5523A'
        assert 'sum_to_free_delivery' not in resp['requirements']
        assert 'decimal_sum_to_free_delivery' not in resp['requirements']
        assert 'next_delivery_threshold' not in resp['requirements']


@pytest.mark.parametrize(
    'delivery_fee,eda_part,place_part',
    [
        pytest.param(
            '20',
            '25.000000',
            '25.000000',
            marks=utils.delivery_discount_enabled(),
            id='eda_place_discount',
        ),
        pytest.param(
            '20',
            '50.000000',
            None,
            marks=utils.delivery_discount_enabled(),
            id='eda_discount_50',
        ),
        pytest.param(
            '20',
            '30.000000',
            None,
            marks=utils.delivery_discount_enabled(),
            id='eda_discount_30',
        ),
    ],
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_post_part_delivery_discount(
        mockserver,
        taxi_eats_cart,
        load_json,
        local_services,
        delivery_fee,
        eda_part,
        place_part,
        eats_order_stats,
):
    eats_order_stats()
    local_services.available_discounts = True
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    catalog_response = load_json('eats_catalog_internal_place.json')

    local_services.catalog_place_response = catalog_response

    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.catalog_place_id = 123
    discounts_resp = load_json('eats_discounts_free_delivery.json')
    discount_size = decimal.Decimal('0.0')
    if not place_part:
        del discounts_resp['match_results'][-1]
    else:
        discounts_resp['match_results'][-1]['discounts'][0]['money_value'][
            'menu_value'
        ]['value'] = place_part
        discount_size += decimal.Decimal(place_part)
    if not eda_part:
        del discounts_resp['match_results'][0]
    else:
        discounts_resp['match_results'][0]['discounts'][0]['money_value'][
            'menu_value'
        ]['value'] = eda_part
        discount_size += decimal.Decimal(eda_part)

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        return discounts_resp

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 200

    resp = response.json()['cart']
    assert (
        decimal.Decimal(resp['decimal_delivery_fee'])
        == decimal.Decimal(delivery_fee)
        - decimal.Decimal(delivery_fee) * discount_size / 100
    )

    next_threshold = int(
        decimal.Decimal('10.0')
        - decimal.Decimal('10.0') * discount_size / 100,
    )
    assert (
        resp['requirements']['next_delivery_threshold']
        == 'Закажите ещё на 27 ₽ для доставки за ' + str(next_threshold) + ' ₽'
    )


async def test_post_cart_add_item_twice(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )

    assert response.status_code == 200

    res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(res) == 1
    assert res[0]['quantity'] == 2


@utils.service_fee_enabled()
@pytest.mark.parametrize(
    'eda_delivery_price_enabled,'
    'eda_delivery_price_dry_run,'
    'expected_service_fee',
    (
        pytest.param(
            False,
            False,
            '1.05',
            marks=utils.service_fee_from_pricing(False, False),
            id='get_service_fee_from_exp',
        ),
        pytest.param(
            False,
            True,
            '1.05',
            marks=utils.service_fee_from_pricing(False, True),
            id='check_dry_run',
        ),
        pytest.param(
            True,
            False,
            '12.3',
            marks=utils.service_fee_from_pricing(True, False),
            id='get_service_fee_from_handle',
        ),
        pytest.param(
            True,
            False,
            '12.3',
            marks=utils.service_fee_from_pricing(True, True),
            id='get_service_fee_from_handle_with_dry_run',
        ),
    ),
)
async def test_reset_extra_fees(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eda_delivery_price_enabled,
        eda_delivery_price_dry_run,
        expected_service_fee,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]

    menu_items_info = load_json('eats_core_menu_items.json')
    local_services.core_items_response = menu_items_info
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 100,
                'deliveryFee': 0,
                'loadLevel': 100,
            },
        },
        'service_fee': '12.3',
    }

    await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )

    eats_cart_cursor.execute(
        'SELECT promo_subtotal, delivery_fee, service_fee, total, id '
        f'FROM eats_cart.carts WHERE eater_id = \'{EATER_ID}\'',
    )
    result1 = eats_cart_cursor.fetchall()
    assert result1[0][3] == result1[0][0] + result1[0][1] + result1[0][2]

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount FROM eats_cart.extra_fees '
        f'WHERE cart_id = \'{result1[0][4]}\' and type = \'delivery_fee\'',
    )
    delivery_result1 = eats_cart_cursor.fetchone()
    assert delivery_result1[2] == result1[0][1]  # delivery_fee

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount FROM eats_cart.extra_fees '
        f'WHERE cart_id = \'{result1[0][4]}\' and type = \'service_fee\'',
    )
    service_result1 = eats_cart_cursor.fetchone()
    assert service_result1[2] == result1[0][2]  # service_fee

    # reset cart because change place
    menu_items_info['place_id'] = '456'
    local_services.core_items_response = menu_items_info
    local_services.set_place_slug('place456')

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(
        'SELECT promo_subtotal, delivery_fee, service_fee, total, id '
        f'FROM eats_cart.carts WHERE eater_id = \'{EATER_ID}\' and '
        'deleted_at IS NULL',
    )
    result2 = eats_cart_cursor.fetchall()
    assert result2[0][3] == result2[0][0] + result2[0][1] + result2[0][2]

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount FROM eats_cart.extra_fees '
        f'WHERE cart_id = \'{result2[0][4]}\' and type = \'delivery_fee\'',
    )
    delivery_result2 = eats_cart_cursor.fetchone()
    assert delivery_result2[2] == result2[0][1]  # delivery_fee

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount FROM eats_cart.extra_fees '
        f'WHERE cart_id = \'{result2[0][4]}\' and type = \'service_fee\'',
    )
    service_result2 = eats_cart_cursor.fetchone()
    assert service_result2[2] == result2[0][2]  # service_fee

    assert result1[0][4] != result2[0][4]


async def test_post_cart_add_item_zero_quantity(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), quantity=0, item_options=[]),
    )

    assert response.status_code == 400


@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
@pytest.mark.parametrize(
    'item_quantity', [pytest.param(0, id='zero'), pytest.param(1, id='one')],
)
async def test_post_cart_add_existing_item(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        item_quantity,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    sql_query = (
        'SELECT * FROM eats_cart.cart_items '
        'WHERE cart_id = \'00000000000000000000000000000001\''
    )

    cart_items = utils.get_pg_records_as_dicts(sql_query, eats_cart_cursor)
    assert len(cart_items) == 1
    assert cart_items[0]['quantity'] == 1

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater3'),
        json=dict(
            item_id=str(MENU_ITEM_ID), quantity=item_quantity, item_options=[],
        ),
    )

    assert response.status_code == (400 if item_quantity == 0 else 200)

    if item_quantity > 0:
        cart_items = utils.get_pg_records_as_dicts(sql_query, eats_cart_cursor)
        assert len(cart_items) == 1
        assert cart_items[0]['quantity'] == 2


@utils.config_cart_total_limits(shop='20.0', restaurant='20.0')
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_post_total_limit_exceeded(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater3'),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 110,
        'domain': 'UserData',
        'err': 'error.total_limit_exceeded',
    }


@pytest.mark.parametrize(
    'error_code,error_message',
    [
        pytest.param(
            109,
            'error.total_items_limit_exceeded',
            marks=utils.config_cart_items_limits(1),
            id='kTotalItemsLimitExceeded',
        ),
        pytest.param(
            116,
            'error.one_item_quantity_exceeded',
            marks=utils.config_cart_items_limits(1000, 100, 1),
            id='kOneItemQuantityLimitExceeded',
        ),
        pytest.param(
            115,
            'error.different_items_limit_exceeded',
            marks=utils.config_cart_items_limits(100, 0),
            id='kDifferentItemsLimitExceeded',
        ),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_post_item_limit_exceeded(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        error_code,
        error_message,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    sql_query = (
        'SELECT * FROM eats_cart.cart_items '
        'WHERE cart_id = \'00000000000000000000000000000001\''
    )
    cart_items = utils.get_pg_records_as_dicts(sql_query, eats_cart_cursor)
    assert len(cart_items) == 1
    assert cart_items[0]['quantity'] == 1

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater3'),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': error_code,
        'domain': 'UserData',
        'err': error_message,
    }


def check_item(place_item: utils.PlaceItem, cart_item: dict):
    assert float(cart_item['decimal_price']) == place_item.get_price()
    expected_promo_price = place_item.get_promo_price()
    if not expected_promo_price:
        assert (
            'decimal_promo_price' not in cart_item
            or cart_item['decimal_promo_price'] is None
        )
    else:
        assert 'decimal_promo_price' in cart_item
        assert float(cart_item['decimal_promo_price']) == expected_promo_price


async def test_post_discounts_from_item_request(
        taxi_eats_cart, load_json, local_services,
):
    local_services.set_place_slug('place123')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    core_resp = utils.CoreItemsResponse('123')

    item_1 = utils.PlaceItem(1, 100, None)
    item_1.add_option_group(utils.PlaceOptionGroup(123))
    item_1.add_option_group(utils.PlaceOptionGroup(124))
    item_1.options_groups[0].add_option(utils.PlaceOption(1123, 10, 8))
    item_1.options_groups[1].add_option(utils.PlaceOption(1124, 10, None))

    item_2 = utils.PlaceItem(2, 80, 70)
    item_2.add_option_group(utils.PlaceOptionGroup(125))
    item_2.add_option_group(utils.PlaceOptionGroup(126))
    item_2.options_groups[0].add_option(utils.PlaceOption(1125, 10, 8))
    item_2.options_groups[1].add_option(utils.PlaceOption(1126, 10, None))

    item_3 = utils.PlaceItem(3, 60, 50)

    core_resp.add_item(item_1)
    core_resp.add_item(item_2)
    core_resp.add_item(item_3)
    local_services.core_items_response = core_resp.serialize()

    local_services.core_items_request = [str(item_1.item_id)]
    await utils.add_item(taxi_eats_cart, local_services, item_1, EATER_ID)
    local_services.core_items_request = [str(item_2.item_id)]
    await utils.add_item(taxi_eats_cart, local_services, item_2, EATER_ID)
    local_services.core_items_request = [str(item_3.item_id)]
    response = await utils.add_item(
        taxi_eats_cart, local_services, item_3, EATER_ID,
    )

    cart = response['cart']
    assert len(cart['items']) == 3

    check_item(item_1, cart['items'][0])
    check_item(item_2, cart['items'][1])
    check_item(item_3, cart['items'][2])


@pytest.mark.parametrize('shipping_type', ['delivery', 'pickup'])
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_post_cart_change_shipping_type(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        shipping_type,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), '1', '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    local_services.set_params(utils.get_params(shipping_type=shipping_type))

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )

    assert response.status_code == 200

    assert response.json()['cart']['shipping_type'] == shipping_type

    res = utils.get_pg_records_as_dicts(utils.SELECT_CART, eats_cart_cursor)
    assert len(res) == 2
    assert res[0]['shipping_type'] == shipping_type


async def test_reset_place_slug(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    slug_from_client, slug_from_core = 'place456', 'place123'
    local_services.place_slugs = set((slug_from_client, slug_from_core))

    core_response = load_json('eats_core_menu_items.json')
    core_response['place_slug'] = slug_from_core
    local_services.core_items_response = core_response

    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater3'),
        json=dict(
            item_id=str(MENU_ITEM_ID),
            place_slug=slug_from_client,
            place_business='restaurant',
            **EMPTY_PROPERTIES,
        ),
    )

    assert response.status_code == 200

    carts = utils.get_pg_records_as_dicts(utils.SELECT_CART, eats_cart_cursor)
    assert len(carts) == 1
    assert carts[0]['place_slug'] == slug_from_core

    assert 1 <= local_services.mock_eats_catalog.times_called <= 2


async def test_cart_post_no_location(taxi_eats_cart, local_services):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]

    params = copy.deepcopy(local_services.request_params)
    del params['latitude']
    del params['longitude']
    del params['deliveryTime']

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=params,
        headers=utils.get_auth_headers(EATER_ID),
        json=POST_BODY,
    )

    assert response.status_code == 400
