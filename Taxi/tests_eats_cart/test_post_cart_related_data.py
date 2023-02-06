import decimal
import json

import pytest

from . import utils


def get_headers(eater_id, yandex_uid, config_enabled):
    headers = {
        'X-YaTaxi-Session': 'eats:',
        'X-YaTaxi-Bound-UserIds': '',
        'X-YaTaxi-Bound-Sessions': '',
        'X-Request-Application': 'app_brand=yataxi,app_name=web,app_ver1=2',
    }
    if config_enabled:
        headers['X-Eats-User'] = f'user_id={eater_id},'
        headers['X-Yandex-UID'] = yandex_uid
    return headers


def make_request(
        eater_id,
        personal_phone_id=None,
        delivery_date='2021-04-04T08:00:00+00:00',
):
    request = {
        'location': {'lat': 55.75, 'lon': 37.62},  # Moscow
        'eater_id': eater_id,
    }
    if personal_phone_id:
        request['personal_phone_id'] = personal_phone_id
    if delivery_date:
        request['delivery_date'] = delivery_date
    return request


@pytest.mark.parametrize(
    'feature_surge_info_enable',
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
@pytest.mark.parametrize(
    'config_enabled',
    utils.RELATED_DATA_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
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
@pytest.mark.parametrize('yandex_plus', [False, True])
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_post_cart_related_data(
        taxi_eats_cart,
        load_json,
        local_services,
        yandex_plus,
        eats_cart_cursor,
        config_enabled,
        feature_surge_info_enable,
        erms_enabled,
):
    eater_id = 'eater1'
    cart_id = '1a73add7-9c84-4440-9d3a-12f3e71c6026'
    place_slug = 'place123'

    catalog_response = load_json('eats_catalog_internal_place.json')
    catalog_response['place']['surge_info'] = {
        'delivery_fee': '18.12',
        'additional_fee': '10',
        'level': 1,
    }
    min_non_zero_delivery = 10
    catalog_response['place']['delivery']['thresholds'][-2][
        'delivery_cost'
    ] = str(min_non_zero_delivery)

    local_services.set_place_slug(place_slug)
    local_services.catalog_place_response = catalog_response
    plus_response = load_json('eats_plus_cashback.json')
    plus_response['hide_cashback_income'] = True
    local_services.set_plus_checkout_response(status=200, json=plus_response)
    local_services.plus_checkout_request = {
        'application': 'web',
        'currency': 'RUB',
        'place_id': {'place_id': '123', 'provider': 'eats'},
        'yandex_uid': '0',
        'services': [
            {
                'service_type': 'product',
                'quantity': '1',
                'public_id': '232323',
                'cost': '1',
            },
            {'service_type': 'delivery', 'quantity': '1', 'cost': '55'},
            {'service_type': 'service_fee', 'quantity': '1', 'cost': '12.78'},
        ],
        'order_id': 'cart_1a73add7-9c84-4440-9d3a-12f3e71c6026',
        'total_cost': '63.78',
    }
    if erms_enabled:
        local_services.eats_restaurant_menu_items_response = load_json(
            'eats_restaurant_menu_items.json',
        )

    request = make_request(eater_id)
    yandex_uid = ''
    if yandex_plus:
        yandex_uid = '0'
        request['yandex_uid'] = yandex_uid
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, yandex_uid, config_enabled),
        json=request,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json('expected_response_new_policy.json')
    if yandex_plus:
        expected_json['cashback'] = plus_response
        expected_json['cart']['cashbacked_total'] = 5
        expected_json['cart']['decimal_cashbacked_total'] = '4.12'
        assert local_services.mock_plus_checkout_cashback.times_called == 1

    assert response.json() == expected_json

    eats_cart_cursor.execute(
        'SELECT * FROM eats_cart.surge_info '
        f'WHERE cart_id = \'{cart_id}\';',
    )
    result = eats_cart_cursor.fetchall()
    if feature_surge_info_enable:
        assert result[0][2] == 1  # surge level
        assert result[0][3] == decimal.Decimal('10')  # additional_fee
    else:
        assert result[0][2] == 2  # surge level
        assert result[0][3] == decimal.Decimal('20')  # additional_fee


@pytest.mark.parametrize(
    'eater_id, delivery_fee',
    [
        pytest.param(
            'eater_eda_discount',
            '0',
            marks=utils.delivery_discount_enabled(),
            id='eda_discount',
        ),
        pytest.param(
            'eater_place_discount',
            '0',
            marks=utils.delivery_discount_enabled(),
            id='place_discount',
        ),
        pytest.param(
            'eater_no_discount',
            '55',
            marks=utils.delivery_discount_enabled(),
            id='less_than_min_order',
        ),
        pytest.param('eater_no_discount', '55', id='no_discount'),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['delivery_discount.sql'])
@pytest.mark.now('2021-05-04T08:00:00.4505+00:00')
async def test_post_cart_related_data_delivery_discount(
        taxi_eats_cart, load_json, local_services, eater_id, delivery_fee,
):
    place_slug = 'place123'

    catalog_response = load_json('eats_catalog_internal_place.json')
    catalog_response['place']['surge_info'] = {
        'delivery_fee': '18.12',
        'additional_fee': '10',
        'level': 1,
    }
    min_non_zero_delivery = 10
    catalog_response['place']['delivery']['thresholds'][-2][
        'delivery_cost'
    ] = str(min_non_zero_delivery)

    local_services.set_place_slug(place_slug)
    local_services.catalog_place_response = catalog_response
    request = make_request(eater_id)
    yandex_uid = ''
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, yandex_uid, False),
        json=request,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json('expected_response.json')
    expected_json['delivery']['decimal_delivery_fee'] = delivery_fee
    expected_json['delivery']['delivery_fee'] = int(delivery_fee)
    if delivery_fee == '0':
        del expected_json['surge']

    del expected_json['cart']['uid']
    resp_json = response.json()
    del resp_json['cart']['uid']
    assert resp_json == expected_json


@pytest.mark.parametrize(
    'config_enabled',
    utils.RELATED_DATA_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
async def test_post_cart_related_data_not_found(
        taxi_eats_cart, config_enabled, eats_order_stats,
):
    eats_order_stats()
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers('eater1', '', config_enabled),
        json=make_request('eater1'),
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Cart not found'}


@pytest.mark.parametrize(
    'config_enabled',
    utils.RELATED_DATA_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.parametrize(
    'place_slug, eater_id',
    [
        pytest.param('place_slug_shop', 'shop_eater', id='shop_cart'),
        pytest.param('place123', 'restaurant_eater', id='restaurant_cart'),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['related_cart.sql'])
async def test_related_cart_slot_logic(
        taxi_eats_cart,
        local_services,
        load_json,
        eater_id,
        place_slug,
        config_enabled,
):
    is_shop_eater = eater_id == 'shop_eater'
    local_services.set_place_slug(place_slug)
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['21']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, '', config_enabled),
        json=make_request(eater_id),
    )

    assert response.status_code == 200

    cnt_called_products = 0
    if is_shop_eater:
        cnt_called_products += 1

    assert (
        local_services.mock_eats_products_menu.times_called
        == cnt_called_products
    )

    if is_shop_eater:
        assert 'calculate_slot_aware_info' in response.json()
        calculate_slot_aware_info = response.json()[
            'calculate_slot_aware_info'
        ]
        assert calculate_slot_aware_info == {
            'place_id': 12345,
            'brand_id': '777',
            'flow_type': 'picking_packing',
            'items': [
                {
                    'category': {'id': 'null'},
                    'quantity': 3.0,
                    'is_catch_weight': True,
                    'public_id': 'tomato_red_super',
                    'quantum': 1500,
                    'measure_value': '1.5',
                    'core_id': '21',
                },
            ],
            'time_to_customer': 1800,
        }
    else:
        assert 'calculate_slot_aware_info' not in response.json()


@utils.setup_available_features(['new_refresh_policy'])
@pytest.mark.parametrize(
    'config_enabled',
    utils.RELATED_DATA_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
async def test_spend_cashback(
        taxi_eats_cart,
        db_insert,
        local_services,
        load_json,
        eats_cart_cursor,
        config_enabled,
):
    subtotal, old_delivery_fee, service_fee, cashback_outcome = 100, 30, 19, 10
    recalculated_delivery_fee = 20
    recalculated_total = subtotal + recalculated_delivery_fee
    total_in_db = subtotal + old_delivery_fee + service_fee
    cashbacked_total = subtotal + recalculated_delivery_fee - cashback_outcome

    menu_item_id = '232323'
    eater_id, yandex_uid = 'eater1', '0'
    place_slug, place_id = 'place123', '123'

    cart_id = db_insert.cart(
        eater_id,
        place_slug=place_slug,
        place_id=place_id,
        promo_subtotal=subtotal,
        total=total_in_db,
        delivery_fee=old_delivery_fee,
        service_fee=service_fee,
    )
    db_insert.eater_cart(eater_id, cart_id)
    db_insert.cart_item(cart_id, menu_item_id, price=100, quantity=1)
    # insert promo item that will not be added to eats-plus services
    promo_item_id = db_insert.cart_item(
        cart_id, place_menu_item_id='1', price=0, quantity=1,
    )
    db_insert.item_discount(promo_item_id, 'promo1', 'promo_type1')

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [menu_item_id]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    plus_response = load_json('eats_plus_cashback.json')
    plus_response['cashback_outcome'] = cashback_outcome
    local_services.set_plus_checkout_response(status=200, json=plus_response)
    local_services.plus_checkout_request = {
        'application': 'web',
        'currency': 'RUB',
        'place_id': {'place_id': place_id, 'provider': 'eats'},
        'yandex_uid': yandex_uid,
        'services': [
            {
                'service_type': 'product',
                'quantity': '1',
                'public_id': menu_item_id,
                'cost': str(subtotal),
            },
            {
                'service_type': 'delivery',
                'quantity': '1',
                'cost': str(old_delivery_fee),
            },
            {
                'service_type': 'service_fee',
                'quantity': '1',
                'cost': str(service_fee),
            },
        ],
        'order_id': f'cart_{cart_id}',
        'total_cost': f'{total_in_db}',
    }

    request = make_request(eater_id)
    request['yandex_uid'] = '0'
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, yandex_uid, config_enabled),
        json=request,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_checkout_cashback.times_called == 1

    response_json = response.json()['cart']

    assert response_json['total'] == recalculated_total
    assert response_json['decimal_total'] == '{:.0f}'.format(
        recalculated_total,
    )
    assert response_json['cashbacked_total'] == cashbacked_total
    assert response_json['decimal_cashbacked_total'] == str(cashbacked_total)

    rows = utils.get_pg_records_as_dicts(utils.SELECT_CART, eats_cart_cursor)
    assert len(rows) == 1
    db_cart = rows[0]
    assert db_cart['total'] == recalculated_total
    assert db_cart['promo_subtotal'] == subtotal


@pytest.mark.parametrize(
    'config_enabled',
    utils.RELATED_DATA_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.pgsql('eats_cart', files=['shop.sql'])
async def test_related_cart_new_discounts(
        taxi_eats_cart, local_services, load_json, config_enabled,
):
    eater_id = 'shop_eater'
    local_services.set_place_slug('place_slug_shop')
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['1', '2', '21']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, '', config_enabled),
        json=make_request(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_products_menu.times_called == 1

    assert response.json() == load_json('expected_shop.json')


@pytest.mark.parametrize('alcohol_items_ids', [[], [2], [2, 21]])
@pytest.mark.pgsql('eats_cart', files=['shop.sql'])
async def test_cart_related_data_alcohol_items(
        taxi_eats_cart,
        local_services,
        redis_store,
        load_json,
        alcohol_items_ids,
):
    """
    В товарах из магазинов, у которых выставлен флаг is_alcohol в ручке
    api/v2/menu/get-items, этот же признак должен быть выставлен в ручке
    v1/related_data.
    """

    eater_id = 'shop_eater'

    local_services.set_place_slug('place_slug_shop')
    local_services.eats_products_items_request = ['1', '2', '21']

    menu_items_response = load_json('eats_products_menu_items.json')
    for item in menu_items_response['place_menu_items']:
        if item['id'] in alcohol_items_ids:
            item['is_alcohol'] = True
    local_services.eats_products_items_response = menu_items_response

    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, yandex_uid='', config_enabled=True),
        json=make_request(eater_id),
    )

    assert response.status_code == 200

    for item_id in alcohol_items_ids:
        parsed_json = json.loads(redis_store.get(f'mi:{item_id}'))
        assert parsed_json['extra_info']['is_alcohol']

    items = response.json()['cart']['items']

    alcohol_items_count = 0
    for item in items:
        if 'is_alcohol' in item and item['is_alcohol']:
            alcohol_items_count += 1

    assert len(alcohol_items_ids) == alcohol_items_count


@pytest.mark.config(EATS_CART_RELATED_DATA_USER_FROM_MIDDLEWARES=False)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_post_cart_related_data_phone_id(
        taxi_eats_cart, load_json, mockserver, local_services,
):
    eater_id = 'eater1'
    place_slug = 'place123'
    personal_phone_id = '1a73add7-9c84-4440-9d3a-12f3e71c6055'

    catalog_response = load_json('eats_catalog_internal_place.json')
    catalog_response['place']['surge_info'] = {
        'delivery_fee': '18.12',
        'additional_fee': '10',
        'level': 1,
    }
    min_non_zero_delivery = 10
    catalog_response['place']['delivery']['thresholds'][-2][
        'delivery_cost'
    ] = str(min_non_zero_delivery)

    local_services.set_place_slug(place_slug)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eats_catalog(request):
        user_header = request.headers['X-Eats-User']
        user_data = user_header.split(',')
        assert f'personal_phone_id={personal_phone_id}' in user_data
        return catalog_response

    request = make_request(eater_id, personal_phone_id=personal_phone_id)
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, '', False),
        json=request,
    )

    assert response.status_code == 200
    assert _mock_eats_catalog.times_called == 1


@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize('is_cash_only', [True, False])
async def test_post_cart_related_data_cash_only(
        taxi_eats_cart, load_json, mockserver, local_services, is_cash_only,
):
    """
    Тест проверяет что магазины помеченные флагом is_cash_only в ручке
    /eats-catalog/internal/v1/place окажутся также помечены в ручке
    v1/related_data.
    """

    eater_id = 'eater1'
    place_slug = 'place123'

    catalog_response = load_json('eats_catalog_internal_place.json')
    if is_cash_only:
        catalog_response['place']['constraints']['is_cash_only'] = True

    local_services.set_place_slug(place_slug)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eats_catalog(request):
        return catalog_response

    request = make_request(eater_id)
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, '', False),
        json=request,
    )

    assert response.status_code == 200
    assert _mock_eats_catalog.times_called == 1

    if is_cash_only:
        assert 'place' in response.json()
        assert response.json()['place']['is_cash_only']
    else:
        assert 'place' not in response.json()


@pytest.mark.config(EATS_CART_RELATED_DATA_USER_FROM_MIDDLEWARES=True)
@utils.service_fee_from_pricing(True, False)
@pytest.mark.parametrize(
    'plus_after_pricing',
    [
        pytest.param(
            True,
            marks=[
                utils.setup_available_features(
                    features=['plus_after_pricing', 'new_refresh_policy'],
                ),
            ],
            id='enabled_plus_after_pricing',
        ),
        pytest.param(
            False,
            marks=[
                utils.setup_available_features(
                    features=['new_refresh_policy'],
                ),
            ],
            id='disabled_plus_after_pricing',
        ),
    ],
)
async def test_related_data_plus_after_pricing(
        taxi_eats_cart,
        db_insert,
        local_services,
        load_json,
        plus_after_pricing,
):
    menu_item_id = '232323'
    eater_id, yandex_uid = 'eater1', '0'
    place_slug, place_id = 'place123', '123'

    # Init values to DB
    subtotal = 100
    delivery_fee = 30
    service_fee = 19
    cashback_outcome = 30

    cart_id = db_insert.cart(
        eater_id,
        place_slug=place_slug,
        place_id=place_id,
        promo_subtotal=subtotal,
        total=subtotal + delivery_fee + service_fee,
        delivery_fee=delivery_fee,
        service_fee=service_fee,
    )

    db_insert.eater_cart(eater_id, cart_id)
    db_insert.cart_item(cart_id, menu_item_id, price=subtotal, quantity=1)

    new_delivery_fee = 10

    if plus_after_pricing:
        delivery_fee = new_delivery_fee
        cashback_outcome = 10

    recalculated_total = subtotal + new_delivery_fee + service_fee
    cashbacked_total = subtotal + delivery_fee + service_fee - cashback_outcome
    plus_request_total = subtotal + delivery_fee + service_fee

    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': str(new_delivery_fee),
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': str(service_fee),
    }

    local_services.set_place_slug(place_slug)
    local_services.core_items_request = [menu_item_id]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    plus_response = load_json('eats_plus_cashback.json')
    plus_response['cashback_outcome'] = cashback_outcome
    local_services.set_plus_checkout_response(status=200, json=plus_response)
    local_services.plus_checkout_request = {
        'application': 'web',
        'currency': 'RUB',
        'place_id': {'place_id': place_id, 'provider': 'eats'},
        'yandex_uid': yandex_uid,
        'services': [
            {
                'service_type': 'product',
                'quantity': '1',
                'public_id': menu_item_id,
                'cost': str(subtotal),
            },
            {
                'service_type': 'delivery',
                'quantity': '1',
                'cost': str(delivery_fee),
            },
            {
                'service_type': 'service_fee',
                'quantity': '1',
                'cost': str(service_fee),
            },
        ],
        'order_id': f'cart_{cart_id}',
        'total_cost': f'{plus_request_total}',
    }

    request = make_request(eater_id)
    request['yandex_uid'] = '0'
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=get_headers(eater_id, yandex_uid, True),
        json=request,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_checkout_cashback.times_called == 1
    assert local_services.mock_eda_delivery_price.times_called == 1

    response_json = response.json()['cart']

    assert response_json['total'] == recalculated_total
    assert response_json['decimal_total'] == '{:.0f}'.format(
        recalculated_total,
    )
    assert response_json['cashbacked_total'] == cashbacked_total
    assert response_json['decimal_cashbacked_total'] == str(cashbacked_total)
