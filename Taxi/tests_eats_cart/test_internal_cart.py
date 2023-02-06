import copy
import decimal

import pytest

from . import utils

MENU_ITEM_ID = 232323
PRODUCT_ID = 2
PLACE_SLUG = 'place123'
PLACE_ID = '22'
EATER_ID = 'eater2'
CART_ID = '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9'
PERSONAL_PHONE_ID = '+79999999999_id'
HEADERS = {
    'X-YaTaxi-Session': 'eats:',
    'X-YaTaxi-Bound-UserIds': '',
    'X-YaTaxi-Bound-Sessions': '',
    'X-Eats-User': f'user_id={EATER_ID},personal_phone_id={PERSONAL_PHONE_ID}',
}
GET_CART_BODY = {'eater_id': EATER_ID, 'shipping_type': 'delivery'}


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.now('2021-04-03T01:12:46.4505+0300')
@pytest.mark.pgsql('eats_cart', files=['internal_insert_values.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(False, id='delivery'), pytest.param(True, id='pickup')),
)
@utils.setup_available_checkers(
    ['CheckCartItemQuantity', 'CheckCartMaxPromoSubtotal'],
)
@utils.config_cart_total_limits()
@utils.config_cart_items_limits()
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
async def test_internal_lock(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        for_pickup,
        experiments3,
        erms_enabled,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    if erms_enabled:
        local_services.eats_restaurant_menu_items_response = load_json(
            'eats_restaurant_menu_items.json',
        )
        exp3_recorder = experiments3.record_match_tries(
            'eats_client_menu_use_erms',
        )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, for_pickup,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json('internal_expected_options_no_surge.json')
    expected_json['applied_checkers'].append('cart_item_quantity_checker')
    expected_json['applied_checkers'].append(
        'shop_threshold_cost_cart_checker',
    )
    if erms_enabled:
        match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
        for elem in match_tries:
            assert elem.kwargs['personal_phone_id'] == PERSONAL_PHONE_ID

        place_menu_item = load_json('place_menu_item.json')
        expected_json['items'][0]['place_menu_item'] = place_menu_item

    data = response.json()
    if for_pickup:
        del expected_json['surge']
        del expected_json['surge_is_actual']
        del expected_json['delivery_fee']
        del expected_json['surge_info']
        utils.compare_and_remove_time(data, expected_json, 'created_at')
    assert data == expected_json

    eats_cart_cursor.execute(
        'SELECT checked_out_at from eats_cart.carts '
        'INNER JOIN eats_cart.eater_cart on carts.id = eater_cart.cart_id '
        'WHERE eater_cart.eater_id = %s',
        (EATER_ID,),
    )
    result = eats_cart_cursor.fetchone()
    assert result[0].isoformat() == '2021-04-03T01:12:46.450500+03:00'


@pytest.mark.now('2021-04-03T01:12:46.4505+0300')
@pytest.mark.pgsql('eats_cart', files=['delivery_discount.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.parametrize(
    'eater_id, delivery_fee, delivery_discount, eda_part, place_part',
    [
        pytest.param(
            'eater_eda_discount',
            '0',
            '20',
            '20',
            '0',
            marks=utils.delivery_discount_enabled(),
            id='eda_discount',
        ),
        pytest.param(
            'eater_place_discount',
            '0',
            '20',
            '0',
            '20',
            marks=utils.delivery_discount_enabled(),
            id='place_discount',
        ),
        pytest.param(
            'eater_no_discount',
            '20',
            None,
            None,
            None,
            marks=utils.delivery_discount_enabled(),
            id='less_than_min_order',
        ),
        pytest.param(
            'eater_no_discount', '20', None, None, None, id='no_discount',
        ),
        # Ожмдаемый ответ корзины с такими параметрами - 400
        pytest.param(
            'eater_eda_discount',
            '10',
            '10',
            '10',
            '0',
            marks=utils.delivery_discount_enabled(),
            id='fail_checker',
        ),
    ],
)
@utils.setup_available_checkers(['CheckDeliveryDiscount'])
@pytest.mark.parametrize('with_surge', [True, False])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.delivery_discount_enabled()
async def test_internal_lock_delivery_discount(
        taxi_eats_cart,
        local_services,
        load_json,
        eater_id,
        delivery_fee,
        delivery_discount,
        eda_part,
        place_part,
        with_surge,
        eats_order_stats,
):
    eats_order_stats()
    local_services.available_discounts = True
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    catalog_response = load_json('eats_catalog_internal_place.json')
    if with_surge:
        surge_info = {
            'delivery_fee': delivery_fee,
            'additional_fee': '9.11',
            'level': 1,
        }
        catalog_response['place']['surge_info'] = surge_info
    local_services.catalog_place_response = catalog_response
    local_services.catalog_place_id = 123

    discounts_resp = load_json('eats_discounts_free_delivery.json')
    if place_part == '0':
        del discounts_resp['match_results'][-1]
    if eda_part == '0':
        del discounts_resp['match_results'][0]

    # Изменяем величину скидки бесплатной доставки со 100% на 50%
    # чтобы заказ сфейлился так как текущая скидка в корзине больше
    # чем доступная скидка на данный момент
    if delivery_discount == '10':
        discounts_resp['match_results'][0]['discounts'][0]['money_value'][
            'menu_value'
        ]['value'] = '50.000000'
    local_services.eats_discounts_response = discounts_resp

    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    del local_services.request_params['deliveryTime']
    req_body = utils.make_lock_cart_body(eater_id, False)
    del req_body['delivery_time']
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/lock_cart', headers=HEADERS, json=req_body,
    )

    if delivery_discount == '10':
        assert response.status_code == 400
    else:
        assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    expected_json = load_json('expected_delivery_discount.json')
    if delivery_discount:
        expected_json['delivery_discount'] = {
            'delivery_fee_discount': delivery_discount,
            'eda_part': eda_part,
            'place_part': place_part,
            'delivery_discount_info': [],
        }
        if eda_part != '0':
            expected_json['delivery_discount'][
                'delivery_discount_info'
            ].append(
                {
                    'amount': eda_part,
                    'discount_provider': 'own',
                    'promo_id': '1591',
                },
            )
        if place_part != '0':
            expected_json['delivery_discount'][
                'delivery_discount_info'
            ].append(
                {
                    'amount': place_part,
                    'discount_provider': 'place',
                    'promo_id': '1592',
                },
            )
    else:
        expected_json['applied_checkers'] = []
    expected_json['delivery_fee'] = delivery_fee
    if not with_surge:
        expected_json['surge_info'] = {'level': 0}
        expected_json['surge'] = '0'

    if delivery_discount != '10':
        data = response.json()
        del data['cart_id']
        assert data == expected_json


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.now('2021-04-03T01:12:46.4505+0300')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.pgsql('eats_cart', files=['internal_shop.sql'])
@utils.setup_available_checkers(
    ['CheckActualDiscount', 'CheckCartMaxPromoSubtotal'],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@utils.config_cart_total_limits()
async def test_internal_lock_shop(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        eats_order_stats,
):
    eats_order_stats()
    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.available_discounts = True
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, False,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_products_menu.times_called == 1

    expected_json = load_json('expected_shop.json')
    expected_json['applied_checkers'].append(
        'shop_threshold_cost_cart_checker',
    )

    data = response.json()

    assert data == expected_json

    eats_cart_cursor.execute(
        'SELECT checked_out_at from eats_cart.carts WHERE eater_id = %s',
        (EATER_ID,),
    )
    result = eats_cart_cursor.fetchone()
    assert result[0].isoformat() == '2021-04-03T01:12:46.450500+03:00'


@pytest.mark.now('2021-04-03T01:12:46.4505+0300')
@pytest.mark.pgsql('eats_cart', files=['internal_shop.sql'])
@utils.setup_available_checkers(['CheckActualDiscount'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
async def test_internal_lock_shop_unavailable_discount(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        eats_order_stats,
):
    eats_order_stats(place_id='123')
    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.available_discounts = True
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response_error.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, False,
    )

    assert response.status_code == 400
    expected_json = load_json('expected_shop_400.json')
    data = response.json()
    assert data == expected_json


@pytest.mark.now('2021-04-03T01:12:46.4505+0300')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.pgsql('eats_cart', files=['internal_shop.sql'])
@utils.setup_available_checkers(
    ['CheckCartMaxPromoSubtotal', 'CheckCartItemQuantity'],
)
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.parametrize(
    'error_code,error_message',
    [
        pytest.param(
            110,
            'error.total_limit_exceeded',
            marks=utils.config_cart_total_limits(
                shop='20.0', restaurant='20.0',
            ),
            id='kTotalLimitExceeded',
        ),
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
async def test_internal_lock_shop_400(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        eats_order_stats,
        error_code,
        error_message,
):
    eats_order_stats()
    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.available_discounts = True
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, False,
    )

    assert response.status_code == 400
    expected_json = {
        'code': error_code,
        'domain': 'UserData',
        'err': error_message,
        'payload': {},
    }
    assert response.json() == expected_json


@pytest.mark.parametrize(
    'actual_surge, additional_fee, surge_is_actual',
    [
        pytest.param('20', '10', True, id='equal'),
        pytest.param('5.5', '10', True, id='below'),
        pytest.param('25.5', '5.5', False, id='above'),
    ],
)
@pytest.mark.parametrize(
    'for_pickup',
    [pytest.param(True, id='pickup'), pytest.param(False, id='delivery')],
)
@pytest.mark.parametrize(
    'config_enabled',
    [
        pytest.param(
            True,
            marks=utils.setup_available_features(
                ['surge_info', 'new_refresh_policy'],
            ),
            id='enable_feature_surge_info',
        ),
        pytest.param(
            False,
            marks=utils.setup_available_features(['new_refresh_policy']),
            id='disable_feature_surge_info',
        ),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['internal_insert_values.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
async def test_internal_lock_with_surge(
        taxi_eats_cart,
        local_services,
        load_json,
        actual_surge,
        additional_fee,
        surge_is_actual,
        for_pickup,
        config_enabled,
        eats_cart_cursor,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]

    catalog_response = load_json('eats_catalog_internal_place.json')

    catalog_response['place']['surge_info'] = {
        'delivery_fee': actual_surge,
        'additional_fee': additional_fee,
        'level': 1,
    }
    local_services.catalog_place_response = catalog_response
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, for_pickup,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json('internal_expected_options_no_surge.json')
    data = response.json()
    if for_pickup:
        del expected_json['surge']
        del expected_json['surge_is_actual']
        del expected_json['delivery_fee']
        del expected_json['surge_info']
        utils.compare_and_remove_time(data, expected_json, 'created_at')
    else:
        delivery_fee = '20'
        expected_json['delivery_fee'] = delivery_fee
        expected_json['surge_is_actual'] = surge_is_actual
        expected_json['surge'] = (
            actual_surge if not surge_is_actual else delivery_fee
        )
        expected_json['surge_info'] = {
            'delivery_fee': expected_json['surge'],
            'additional_fee': additional_fee,
            'level': 1,
        }

        eats_cart_cursor.execute(
            'SELECT cart_id FROM eats_cart.eater_cart '
            f'WHERE eater_id = \'{EATER_ID}\';',
        )
        result = eats_cart_cursor.fetchall()
        cart_id = result[0][0]

        eats_cart_cursor.execute(
            'SELECT * FROM eats_cart.surge_info '
            f'WHERE cart_id = \'{cart_id}\';',
        )
        result = eats_cart_cursor.fetchall()
        if config_enabled:
            assert result[0][2] == 1  # surge level
            assert result[0][3] == decimal.Decimal('10.00')  # additional_fee
        else:
            assert len(result) == 1

    assert data == expected_json


@pytest.mark.parametrize(
    'db_delivery_fee',
    [
        pytest.param(20, id='equal'),
        pytest.param(30, id='above'),
        pytest.param(10, id='below'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.pgsql('eats_cart', files=['internal_insert_values.sql'])
async def test_internal_lock_wo_surge(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_delivery_fee,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]

    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    eats_cart_cursor.execute(
        'UPDATE eats_cart.carts '
        'SET delivery_fee = %s '
        'WHERE eater_id = %s',
        (db_delivery_fee, EATER_ID),
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, False,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json('internal_expected_options_no_surge.json')
    data = response.json()
    expected_json['delivery_fee'] = str(db_delivery_fee)
    expected_json['surge_is_actual'] = True
    expected_json['surge'] = '0'
    expected_json['surge_info'] = {'level': 0}

    assert data == expected_json


CHECKED_OUT_TTL = 5000


@pytest.mark.config(EATS_CART_TIMEOUTS={'checked_out_ms': CHECKED_OUT_TTL})
@pytest.mark.now('2021-04-03T01:12:46+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.pgsql('eats_cart', files=['internal_insert_values.sql'])
@pytest.mark.parametrize(
    'checked_out_at',
    [
        pytest.param('2021-04-03T01:12:40+03:00', id='is_over'),
        pytest.param('2021-04-03T01:12:42+03:00', id='is_actual'),
    ],
)
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_checked_out_ttl(
        taxi_eats_cart,
        local_services,
        eats_cart_cursor,
        load_json,
        checked_out_at,
        for_pickup,
):
    eats_cart_cursor.execute(
        'UPDATE eats_cart.carts '
        'SET checked_out_at = %s '
        'WHERE eater_id = %s',
        (checked_out_at, EATER_ID),
    )
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, for_pickup,
    )

    eats_cart_cursor.execute(
        'SELECT checked_out_at FROM eats_cart.carts '
        'WHERE eater_id = %s AND deleted_at IS NULL',
        (EATER_ID,),
    )
    t_lock = eats_cart_cursor.fetchone()

    assert response.status_code == 200
    assert local_services.mock_eats_catalog.times_called == 1
    assert t_lock[0].isoformat() == '2021-04-03T01:12:46+03:00'


@pytest.mark.config(EATS_CART_TIMEOUTS={'checked_out_ms': CHECKED_OUT_TTL})
@pytest.mark.pgsql('eats_cart', files=['internal_insert_values.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_cart_stays_locked(
        taxi_eats_cart,
        local_services,
        mocked_time,
        load_json,
        eats_cart_cursor,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    old_params = copy.deepcopy(local_services.request_params)
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, for_pickup,
    )
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    local_services.request_params = old_params
    checked_out_sec = CHECKED_OUT_TTL // 1000
    first_sleep = checked_out_sec / 2

    mocked_time.sleep(first_sleep)
    await taxi_eats_cart.invalidate_caches()

    post_item_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_item_body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'domain': 'UserData',
        'code': 42,
        'err': 'error.cart_modify_error',
    }
    mocked_time.sleep(checked_out_sec - first_sleep + 1)
    await taxi_eats_cart.invalidate_caches()
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_item_body,
    )
    assert response.status_code == 200
    eats_cart_cursor.execute(
        'SELECT checked_out_at FROM eats_cart.carts WHERE id = %s', (cart_id,),
    )
    result = eats_cart_cursor.fetchone()
    assert result[0] is None


@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
async def test_lock_cart_not_found(
        taxi_eats_cart, for_pickup, eats_order_stats,
):
    eats_order_stats()
    response = await utils.call_lock_cart(
        taxi_eats_cart,
        EATER_ID,
        HEADERS,
        for_pickup,
        data={'eater_id': 'non-existing', 'shipping_type': 'delivery'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'for_pickup, cart_id, eater_id',
    (
        pytest.param(
            True,
            '00000000-0000-0000-0000-000000000001',
            'eater3',
            id='pickup',
        ),
        pytest.param(
            False,
            '00000000-0000-0000-0000-000000000000',
            'eater2',
            id='delivery',
        ),
    ),
)
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
async def test_lock_cart_400(
        taxi_eats_cart,
        local_services,
        eats_cart_cursor,
        for_pickup,
        cart_id,
        eater_id,
):
    eats_cart_cursor.execute('BEGIN;')
    eats_cart_cursor.execute(
        'SELECT E.eater_id, E.cart_id::TEXT, C.created_at '
        'FROM eats_cart.eater_cart AS E '
        'LEFT JOIN eats_cart.carts AS C '
        'ON E.cart_id = C.id '
        'WHERE E.eater_id = %s '
        'FOR UPDATE OF E;',
        (eater_id,),
    )
    eats_cart_cursor.execute(
        'SELECT id::text FROM eats_cart.carts WHERE id = %s FOR UPDATE;',
        (cart_id,),
    )
    response = await utils.call_lock_cart(
        taxi_eats_cart, eater_id, HEADERS, for_pickup,
    )
    assert response.status_code == 400
    eats_cart_cursor.execute('COMMIT;')


@pytest.mark.parametrize('available_asap', [True, False])
@pytest.mark.pgsql('eats_cart', files=['internal_shop.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@utils.setup_available_checkers(['CheckDeliveryTime'])
async def test_validate_delivery_time_asap(
        taxi_eats_cart, local_services, load_json, available_asap,
):
    local_services.set_params(utils.get_params(delivery_time=None))

    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.available_discounts = True
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.eats_customer_slots_response = {
        'available_asap': available_asap,
        'available_slots': [],
    }
    request = utils.make_lock_cart_body(EATER_ID, False)
    del request['delivery_time']
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/lock_cart', headers=HEADERS, json=request,
    )
    assert local_services.mock_slots_validate_time.times_called == 1
    if available_asap:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 111,
            'domain': 'UserData',
            'err': 'error.asap_not_available',
            'payload': {},
        }


@pytest.mark.parametrize(
    'available_slots',
    [
        [],
        [
            {
                'start': '2021-04-04T08:00:00+03:00',
                'estimated_delivery_timepoint': '2021-04-04T08:30:00+03:00',
                'end': '2021-04-04T09:00:00+03:00',
            },
        ],
    ],
)
@pytest.mark.pgsql('eats_cart', files=['internal_shop.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
@utils.setup_available_checkers(['CheckDeliveryTime'])
async def test_validate_delivery_time_slots(
        taxi_eats_cart, local_services, load_json, available_slots,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.available_discounts = True
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )
    local_services.catalog_place_id = 123
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.eats_customer_slots_response = {
        'available_asap': False,
        'available_slots': available_slots,
    }
    response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS, False,
    )
    assert local_services.mock_slots_validate_time.times_called == 1

    if available_slots:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 112,
            'domain': 'UserData',
            'err': 'error.slot_not_available',
            'payload': {},
        }
