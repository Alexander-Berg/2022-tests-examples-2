# pylint: disable=C0302

import copy
import datetime
import decimal
import json
import math

import pytest

from . import utils


ROVER_COURIER_OPTION = {
    'code': 'yandex_rover',
    'title': 'Ровер',
    'description': 'Ровер приедет, если свободен',
}

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T08:00:00+00:00',
}

EMPTY_PROPERTIES = {'quantity': 1, 'item_options': []}


def setup_rover_experiment(enabled: bool):
    return pytest.mark.experiments3(
        name='eda_yandex_rover_courier',
        consumers=['eats_cart/with_place_info'],
        is_config=False,
        default_value={'enabled': enabled},
    )


def setup_catalog_experiment(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_cart_catalog_courier_options',
        consumers=['eats_cart/with_place_info'],
        is_config=False,
        default_value={'enabled': enabled},
    )


@pytest.mark.parametrize(
    'asap', [pytest.param(True, id='asap'), pytest.param(False, id='to_time')],
)
@pytest.mark.parametrize(
    'catalog_exp_enabled',
    [
        pytest.param(
            True, marks=setup_catalog_experiment(True), id='catalog_enabled',
        ),
        pytest.param(
            False,
            marks=setup_catalog_experiment(False),
            id='catalog_disabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'yandex_rover_exp_enabled',
    [
        pytest.param(
            True, marks=setup_rover_experiment(True), id='rover_enabled',
        ),
        pytest.param(
            False, marks=setup_rover_experiment(False), id='rover_disabled',
        ),
    ],
)
@pytest.mark.parametrize('shipping_type', ['delivery', 'pickup'])
@pytest.mark.parametrize(
    'eater_id, file_name',
    [
        ('eater3', 'expected_existed_cart.json'),
        ('eater2', 'expected_options_no_surge.json'),
    ],
)
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
async def test_cart_get(
        taxi_eats_cart,
        local_services,
        load_json,
        yandex_rover_exp_enabled,
        catalog_exp_enabled,
        shipping_type,
        eater_id,
        file_name,
        asap,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']
    local_services.asap = asap

    params = copy.deepcopy(PARAMS)
    if asap:
        del params['deliveryTime']

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    params['shippingType'] = shipping_type
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json(file_name)
    if yandex_rover_exp_enabled or catalog_exp_enabled:
        expected_json['place']['courier_options'].append(ROVER_COURIER_OPTION)

    resp_json = response.json()
    del resp_json['id']
    del resp_json['revision']
    assert resp_json == expected_json


@utils.additional_payment_text()
@utils.service_fee_enabled()
@utils.service_fee_from_pricing()
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'expected_service_fee, expected_total',
    (
        pytest.param(
            '1.05',
            '169.01',
            marks=utils.service_fee_from_pricing(False, False),
            id='get_service_fee_from_exp',
        ),
        pytest.param(
            '1.05',
            '169.01',
            marks=utils.service_fee_from_pricing(False, True),
            id='check_dry_run',
        ),
        pytest.param(
            '12.3',
            '180.26',
            marks=utils.service_fee_from_pricing(True, False),
            id='get_service_fee_from_handle',
        ),
        pytest.param(
            '12.3',
            '180.26',
            marks=utils.service_fee_from_pricing(True, True),
            id='get_service_fee_from_handle_with_dry_run',
        ),
    ),
)
async def test_cart_get_with_expenses_holding(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        expected_service_fee,
        expected_total,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']
    eater_id = 'eater3'

    params = copy.deepcopy(PARAMS)
    local_services.set_params(copy.deepcopy(params))
    params['shippingType'] = 'delivery'
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
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )
    assert response.status_code == 200
    expected_json = load_json('expected_options_service_fee.json')

    eats_cart_cursor.execute(
        'SELECT service_fee, total FROM eats_cart.carts '
        f'WHERE eater_id = \'{eater_id}\'',
    )
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert result[0]['service_fee'] == decimal.Decimal(expected_service_fee)

    total = decimal.Decimal(expected_total)

    assert result[0]['total'] == total

    expected_json['additional_payments'][1]['amount']['amount'] = (
        expected_service_fee + ' $SIGN$$CURRENCY$'
    )
    expected_json['decimal_total'] = total.__str__()
    expected_json['expenses_holding']['holding_amount'] = decimal.Decimal(
        expected_service_fee,
    ).__ceil__()
    expected_json['total'] = total.__ceil__()

    resp_json = response.json()
    del resp_json['id']
    del resp_json['revision']
    assert resp_json == expected_json


@utils.service_fee_enabled()
@utils.service_fee_from_pricing()
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values_with_pickup.sql'])
@pytest.mark.parametrize(
    'expected_service_fee, shipping_type',
    (
        pytest.param(
            '1.05',
            'delivery',
            marks=utils.service_fee_from_pricing(False, False),
            id='get_service_fee_from_exp',
        ),
        pytest.param(
            '1.05',
            'delivery',
            marks=utils.service_fee_from_pricing(False, True),
            id='check_dry_run',
        ),
        pytest.param(
            '12.3',
            'delivery',
            marks=utils.service_fee_from_pricing(True, False),
            id='get_service_fee_from_handle',
        ),
        pytest.param(
            '1.05',
            'pickup',
            marks=utils.service_fee_from_pricing(False, False),
            id='get_service_fee_from_exp_pickup',
        ),
        pytest.param(
            '1.05',
            'pickup',
            marks=utils.service_fee_from_pricing(False, True),
            id='check_dry_run_pickup',
        ),
        pytest.param(
            '12.3',
            'pickup',
            marks=utils.service_fee_from_pricing(True, False),
            id='get_service_fee_from_handle_pickup',
        ),
    ),
)
async def test_cart_get_extra_fees(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        expected_service_fee,
        shipping_type,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323']
    eater_id = 'eater4'
    cart_id = '00000000000000000000000000000002'
    expected_cart_id = '00000000-0000-0000-0000-000000000002'
    if shipping_type == 'pickup':
        cart_id = '00000000000000000000000000000003'
        expected_cart_id = '00000000-0000-0000-0000-000000000003'
        eater_id = 'eater5'

    params = copy.deepcopy(PARAMS)
    params['shippingType'] = shipping_type
    local_services.set_params(copy.deepcopy(params))

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

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount, payload FROM eats_cart.extra_fees '
        f'WHERE cart_id = \'{cart_id}\' ORDER BY type',
    )
    result = eats_cart_cursor.fetchall()
    assert len(result) == 3
    assert result == [
        [expected_cart_id, 'assembly_fee', decimal.Decimal('0.00'), None],
        [
            expected_cart_id,
            'delivery_fee',
            decimal.Decimal('20.00'),
            {
                'delivery_class': 'regular',
                'delivery_time': '2021-04-04T08:00:00+00:00',
                'location': {'lat': 55.75, 'lon': 37.62},
                'travel_duration': 300,
            },
        ],
        [
            expected_cart_id,
            'service_fee',
            decimal.Decimal(expected_service_fee),
            None,
        ],
    ]


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
@utils.additional_payment_text()
@pytest.mark.parametrize(
    'is_ultima',
    [pytest.param(True, id='ultima'), pytest.param(False, id='regular')],
)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_with_surge(
        taxi_eats_cart,
        local_services,
        load_json,
        config_enabled,
        eats_cart_cursor,
        is_ultima,
):
    eater_id = 'eater2'
    cart_id = '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9'
    surge_info = {
        'delivery_fee': '18.12',
        'additional_fee': '10.11',
        'level': 1,
    }

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    catalog_response = load_json('eats_catalog_internal_place.json')
    catalog_response['place']['surge_info'] = surge_info
    catalog_response['place']['is_ultima'] = is_ultima

    local_services.catalog_place_response = catalog_response
    local_services.set_params(copy.deepcopy(PARAMS))

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    expected_json = load_json('expected_options_no_surge.json')
    expected_json['is_ultima'] = is_ultima
    delivery_with_surge = float(surge_info['delivery_fee'])
    int_delivery_with_surge = int(math.ceil(delivery_with_surge))
    expected_json['surge'] = {
        'delivery_fee': int_delivery_with_surge,
        'decimal_delivery_fee': surge_info['delivery_fee'],
        'description': 'Описание повышенного спроса',
        'message': (
            'Заказов сейчас очень много — чтобы еда приехала в срок, '
            'стоимость доставки временно увеличена'
        ),
        'title': 'Повышенный спрос',
    }
    expected_json['delivery_fee'] = int_delivery_with_surge
    expected_json['decimal_delivery_fee'] = surge_info['delivery_fee']
    expected_json['charges'][0][
        'cost'
    ] = f'{int_delivery_with_surge} $SIGN$$CURRENCY$'
    expected_json['total'] = 162  # subtotal + delivery_with_surge - promocode
    expected_json['decimal_total'] = '161.08'
    expected_json['additional_payments'][0]['amount'][
        'amount'
    ] = f'{delivery_with_surge} $SIGN$$CURRENCY$'
    expected_json['additional_payments'][0]['subtitle'][
        'text'
    ] = 'Закажите еще на Х рублей для бесплатной доставки'
    del expected_json['requirements']['next_delivery_threshold']
    resp_json = response.json()
    del resp_json['id']
    del resp_json['revision']
    assert resp_json == expected_json

    eats_cart_cursor.execute(
        'SELECT * FROM eats_cart.surge_info '
        f'WHERE cart_id = \'{cart_id}\';',
    )
    result = eats_cart_cursor.fetchall()
    if config_enabled:
        assert result[0][2] == 1  # surge level
        assert result[0][3] == decimal.Decimal(
            surge_info['additional_fee'],
        )  # additional_fee
    else:
        assert result[0][2] == 2  # surge level
        assert result[0][3] == decimal.Decimal('20')  # additional_fee


@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_with_surge_by_experiment(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        experiments3,
):
    eater_id = 'eater2'
    cart_id = '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9'
    surge_info = {
        'delivery_fee': '18.12',
        'additional_fee': '10.11',
        'level': 1,
    }

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    catalog_response = load_json('eats_catalog_internal_place.json')
    catalog_response['place']['surge_info'] = surge_info

    local_services.catalog_place_response = catalog_response
    local_services.set_params(copy.deepcopy(PARAMS))

    experiments3.add_experiment(
        name='eats_cart_features',
        consumers=['eats_cart/user_only'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'surge_info': {'enabled': True}},
            },
        ],
    )
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    eats_cart_cursor.execute(
        'SELECT * FROM eats_cart.surge_info '
        f'WHERE cart_id = \'{cart_id}\';',
    )
    result = eats_cart_cursor.fetchall()
    assert result[0][2] == 1  # surge level
    assert result[0][3] == decimal.Decimal('10.11')  # additional_fee


@pytest.mark.parametrize(
    'price,quantity',
    [
        pytest.param(10, 1, id='min_order_price'),
        pytest.param(501, 2, id='max_order_price'),
        #    pytest.param(501, 100, 2, id='max_price_max_weight'),
    ],
)
@pytest.mark.config(
    EATS_CART_REDIS={'enable_menu_items_cache': False, 'menu_items_ttl': 1800},
)
async def test_cart_get_requirements(
        taxi_eats_cart,
        load_json,
        db_insert,
        price,
        #  weight,
        quantity,
        local_services,
):
    eater_id, menu_item_id = 'eater1', '123456'
    subtotal = price * quantity

    cart_id = db_insert.cart(
        eater_id, promo_subtotal=subtotal, total=subtotal, delivery_fee=20,
    )
    db_insert.eater_cart(eater_id, cart_id)
    db_insert.cart_item(
        cart_id,
        menu_item_id,
        price=price,
        promo_price=None,
        quantity=quantity,
    )

    local_services.core_items_request = [menu_item_id]
    core_response = load_json('eats_core_menu_items_requirements.json')
    menu_item = core_response['place_menu_items'][0]
    menu_item['price'] = int(price)
    # menu_item['weight_number'] = weight
    local_services.core_items_response = core_response

    min_price, max_price, max_weight = 50.1, 1000, 10.50
    constraints = {
        'maximum_order_price': str(max_price),
        'maximum_order_weight': max_weight,
        'minimum_order_price': str(min_price),
    }
    catalog_response = load_json('eats_catalog_internal_place.json')
    for key, value in constraints.items():
        catalog_response['place']['constraints'][key]['value'] = value

    local_services.catalog_place_response = catalog_response

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=PARAMS, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    expected = {'violated_constraints': []}

    if subtotal < min_price:
        expected['sum_to_min_order'] = int(math.ceil(min_price)) - subtotal
        expected['decimal_sum_to_min_order'] = str(min_price - subtotal)

    if subtotal > max_price:
        expected['violated_constraints'].append(
            {
                'title': f'Максимальный заказ {max_price} $SIGN$$CURRENCY$',
                'type': 'max_subtotal_cost',
                'violation_message': (
                    'Сумма заказа превышена на'
                    f' {subtotal - max_price} $SIGN$$CURRENCY$'
                ),
            },
        )

    # TODO EDAJAM-10: uncomment check for retail
    # if weight > constraints['maximum_order_weight']:
    #     expected['violated_constraints'].append(
    #         {
    #             'title': f'Максимальный вес {max_weight} кг',
    #             'type': 'max_weight',
    #             'violation_message': (
    #                 f'Вес заказа превышен на {weight - max_weight} кг'
    #             ),
    #         },
    #     )

    assert response.json()['requirements'] == expected


@utils.additional_payment_text()
@pytest.mark.config(
    EATS_CART_REDIS={'enable_menu_items_cache': True, 'menu_items_ttl': 1800},
)
@pytest.mark.parametrize(
    'core_weight',
    [
        pytest.param(True, id='with_weight'),
        pytest.param(False, id='without_weight'),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_place_redis(
        taxi_eats_cart, local_services, load_json, redis_store, core_weight,
):
    eater_id = 'eater2'

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    local_services.set_params(copy.deepcopy(PARAMS))
    core_resp = local_services.core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    if not core_weight:
        for item in core_resp['place_menu_items']:
            del item['measure']
    local_services.core_items_response = core_resp

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )
    assert response.status_code == 200

    parsed_json = json.loads(redis_store.get('mi:232323'))

    expected_json = load_json('expected_options_no_surge.json')
    expected_json = expected_json['items'][0]['place_menu_item']
    expected_json['weight'] = expected_json['weight'].replace('\u00a0', ' ')
    assert parsed_json['menu_item'] == expected_json

    del parsed_json['menu_item']
    expected_redis_data = {
        'place_business': 'restaurant',
        'place_id': '123',
        'place_slug': 'place123',
        'extra_info': {
            'weight': '1',
            'weight_unit': 'kg',
            'public_id': None,
            'vat': None,
            'is_catch_weight': False,
            'origin_id': '',
            'is_alcohol': False,
        },
    }
    if not core_weight:
        del expected_redis_data['extra_info']
    assert parsed_json == expected_redis_data

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    assert (
        local_services.mock_eats_core_menu.times_called == 1
    )  # must be 1, we use redis cached data on second call
    assert local_services.mock_eats_catalog.times_called == 2


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
async def test_get_cart_no_cart(
        taxi_eats_cart,
        load_json,
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
    response = await taxi_eats_cart.get(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    empy_cart = utils.get_empty_cart(
        load_json, delivery_time, now, shipping_type, tz_offset,
    )

    assert response.json() == empy_cart


@pytest.mark.config(
    EATS_CART_REDIS={'enable_menu_items_cache': False, 'menu_items_ttl': 1800},
)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_place_redis_disable(
        taxi_eats_cart, local_services, redis_store,
):
    eater_id = 'eater2'

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    local_services.set_params(copy.deepcopy(PARAMS))

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )
    assert response.status_code == 200

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )
    assert response.status_code == 200

    redis_data = redis_store.get('mi: 232323')
    assert not redis_data

    # must be 2, redis disabled
    assert local_services.mock_eats_core_menu.times_called == 2
    assert local_services.mock_eats_catalog.times_called == 2


EATS_PLUS_REQUEST_JSON = {
    'location': {'latitude': 55.75, 'longitude': 37.62},
    'currency': 'RUB',
    'place_id': {'place_id': '123', 'provider': 'eats'},
    'yandex_uid': '0',
    'services': [
        {
            'service_type': 'product',
            'quantity': '2',
            'public_id': '232323',
            'cost': '97.9',
            'is_catch_weight': False,
        },
        {
            'service_type': 'product',
            'quantity': '1',
            'public_id': '2',
            'cost': '40',
            'is_catch_weight': False,
        },
        {'service_type': 'delivery', 'quantity': '1', 'cost': '20'},
        {'service_type': 'service_fee', 'quantity': '1', 'cost': '1.05'},
    ],
    'shipping_type': 'delivery',
    'total_cost': '158.95',
}


@pytest.mark.parametrize(
    'eater_id, file_name, get_service_fee_from_pricing',
    [
        pytest.param(
            'eater3',
            'expected_options_service_fee.json',
            False,
            marks=utils.service_fee_enabled(),
            id='service_fee_on',
        ),
        pytest.param(
            'eater3',
            'expected_options_service_fee.json',
            True,
            marks=[utils.service_fee_from_pricing(True, False)],
            id='service_fee_on_from_pricing',
        ),
        pytest.param(
            'eater2',
            'expected_options_no_surge.json',
            False,
            id='service_fee_off',
        ),
    ],
)
@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_cashback(
        taxi_eats_cart,
        local_services,
        load_json,
        eater_id,
        file_name,
        get_service_fee_from_pricing,
):
    plus_response = load_json('eats_plus_cashback.json')
    plus_response['hide_cashback_income'] = True
    del plus_response['cashback_outcome_details']
    plus_request = copy.deepcopy(EATS_PLUS_REQUEST_JSON)

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    if get_service_fee_from_pricing:
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
            'service_fee': '1.05',
        }

    if eater_id == 'eater2':
        # Set total cost for eater2 from DB
        plus_request['total_cost'] = '162.96'
        plus_request['services'][0]['cost'] = '102.56'
        # eater2 has not service fee
        del plus_request['services'][-1]

    if eater_id == 'eater3':
        # Set total cost for eater3 from DB
        plus_request['total_cost'] = '169.01'

    local_services.plus_request = plus_request
    local_services.set_plus_response(status=200, json=plus_response)

    local_services.set_params(copy.deepcopy(PARAMS))

    request_headers = utils.get_auth_headers(eater_id)
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    expected_json = load_json(file_name)

    expected_json['cashbacked_total'] = (
        expected_json['total'] - plus_response['cashback_outcome']
    )
    expected_json['decimal_cashbacked_total'] = str(
        float(expected_json['decimal_total'])
        - float(plus_response['decimal_cashback_outcome']),
    )

    plus_response = utils.make_cashback_data(plus_response)

    expected_json['yandex_plus'] = {'cashback': plus_response}

    resp_json = response.json()
    del resp_json['id']
    del resp_json['revision']
    assert resp_json == expected_json


@pytest.mark.parametrize(
    'plus_after_pricing',
    [
        pytest.param(
            True,
            marks=[
                utils.service_fee_from_pricing(True, False),
                utils.setup_available_features(
                    features=['plus_after_pricing'],
                ),
            ],
            id='enabled_plus_after_pricing',
        ),
        pytest.param(
            False,
            marks=[utils.service_fee_from_pricing(True, False)],
            id='disabled_plus_after_pricing',
        ),
    ],
)
@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_cashback_plus_after_pricing(
        taxi_eats_cart, local_services, load_json, plus_after_pricing,
):
    eater_id = 'eater3'

    plus_response = load_json('eats_plus_cashback.json')
    del plus_response['cashback_outcome_details']
    plus_request = copy.deepcopy(EATS_PLUS_REQUEST_JSON)

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '10',
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {'placeId': 1},
        'service_fee': '1.05',
    }

    plus_request['services'][0]['cost'] = '146.85'
    plus_request['services'][0]['quantity'] = '3'
    plus_request['total_cost'] = '217.96'

    total = 208
    decimal_total = '207.96'

    if plus_after_pricing:
        plus_request['services'][2]['cost'] = '10'
        plus_request['total_cost'] = '207.96'

    local_services.plus_request = plus_request
    local_services.set_plus_response(status=200, json=plus_response)

    local_services.set_params(copy.deepcopy(PARAMS))

    request_headers = utils.get_auth_headers(eater_id)
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
        json=dict(item_id=str('232323'), **EMPTY_PROPERTIES),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 2
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    resp_json = response.json()

    assert resp_json['cart']['cashbacked_total'] == (
        total - plus_response['cashback_outcome']
    )
    assert resp_json['cart']['decimal_cashbacked_total'] == str(
        float(decimal_total)
        - float(plus_response['decimal_cashback_outcome']),
    )

    plus_response = utils.make_cashback_data(plus_response)

    expected_json = load_json('expected_options_service_fee.json')
    expected_json['yandex_plus'] = {'cashback': plus_response}

    assert expected_json['yandex_plus'] == resp_json['cart']['yandex_plus']


@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_cashback_204(
        taxi_eats_cart, local_services, load_json,
):
    eater_id = 'eater2'

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    plus_request = copy.deepcopy(EATS_PLUS_REQUEST_JSON)
    plus_request['total_cost'] = '162.96'
    plus_request['services'][0]['cost'] = '102.56'
    del plus_request['services'][-1]
    local_services.plus_request = plus_request

    local_services.set_params(copy.deepcopy(PARAMS))

    request_headers = utils.get_auth_headers(eater_id)
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    expected_json = load_json('expected_options_no_surge.json')

    resp_json = response.json()
    del resp_json['id']
    del resp_json['revision']
    assert resp_json == expected_json


@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_cashback_503(
        taxi_eats_cart, local_services, load_json,
):
    eater_id = 'eater2'

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    local_services.set_plus_response(status=503, json={})

    local_services.set_params(copy.deepcopy(PARAMS))

    request_headers = utils.get_auth_headers(eater_id)
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    expected_json = load_json('expected_options_no_surge.json')

    resp_json = response.json()
    del resp_json['id']
    del resp_json['revision']
    assert resp_json == expected_json


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['shop.sql'])
async def test_cart_get_shop(taxi_eats_cart, local_services, load_json):
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['1', '2', '21']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=PARAMS, headers=utils.get_auth_headers('eater2'),
    )

    assert response.status_code == 200
    result = response.json()
    del result['updated_at']
    del result['id']
    del result['revision']
    assert result == load_json('expected_shop.json')


@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_cashback_with_outcome_element(
        taxi_eats_cart, local_services, load_json,
):
    """
    Тест проверяет, что обрабатываются приходящие из eats-plus/../cart/cashback
    данные для положения тоггла Плюса "Списать" - title и subtitle - и что
    мы подставляем к ним нулевой кешбек, чтобы по щелчку тоггла надпись
    "Вы получите баллы Плюса - 100" менялась на "Баллы не будут начислены - 0"
    """

    plus_response = load_json('eats_plus_cashback_with_outcome_fields.json')

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    plus_request = copy.deepcopy(EATS_PLUS_REQUEST_JSON)
    plus_request['services'][0]['cost'] = '102.56'
    plus_request['total_cost'] = '162.96'
    del plus_request['services'][-1]
    local_services.plus_request = plus_request
    local_services.set_plus_response(status=200, json=plus_response)

    local_services.set_params(copy.deepcopy(PARAMS))

    request_headers = utils.get_auth_headers('eater2')
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    expected_fields = {
        'cashback_income': {
            'title': 'Вернётся баллами Плюса',
            'subtitle': (
                'Выберите Списать, чтобы потратить баллы на заказ.'
                ' Но тогда не будут начислены эти :c'
            ),
            'cashback': '100',
            'deeplink': 'deeplink',
        },
        'cashback_outcome': {
            'title': 'Вы списываете баллы Плюса',
            'subtitle': 'Баллы за этот заказ начислены не будут',
            'cashback': '0',
            'deeplink': 'deeplink',
        },
    }

    assert 'yandex_plus' in response.json()
    assert 'cashback' in response.json()['yandex_plus']
    assert (
        expected_fields.items()
        <= response.json()['yandex_plus']['cashback'].items()
    )


@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_get_cashback_with_partially_filled_outcome(
        taxi_eats_cart, local_services, load_json,
):
    """
    Тест проверяет, что обрабатываются приходящие из eats-plus/../cart/cashback
    данные для положения тоггла Плюса "Списать" - title и subtitle - и что
    outcome_description, если отсутствует в ответе eats-plus,
    не передаётся в нашем ответе,
    а outcome_title, если не передается, заменяется на income_title.
    """

    plus_response = load_json(
        'eats_plus_cashback_outcome_partially_filled.json',
    )

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['2', '232323']

    plus_request = copy.deepcopy(EATS_PLUS_REQUEST_JSON)
    plus_request['services'][0]['cost'] = '102.56'
    plus_request['total_cost'] = '162.96'
    del plus_request['services'][-1]
    local_services.plus_request = plus_request
    local_services.set_plus_response(status=200, json=plus_response)

    local_services.set_params(copy.deepcopy(PARAMS))

    request_headers = utils.get_auth_headers('eater2')
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    expected_fields = {
        'cashback_income': {
            'title': 'Вернётся баллами Плюса',
            'subtitle': (
                'Выберите Списать, чтобы потратить баллы на заказ.'
                ' Но тогда не будут начислены эти :c'
            ),
            'cashback': '100',
            'deeplink': 'deeplink',
        },
        'cashback_outcome': {
            'title': 'Вернётся баллами Плюса',
            'cashback': '0',
            'deeplink': 'deeplink',
        },
    }

    assert 'yandex_plus' in response.json()
    assert 'cashback' in response.json()['yandex_plus']
    assert (
        expected_fields.items()
        <= response.json()['yandex_plus']['cashback'].items()
    )


@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_cart_post_pickup_time(
        taxi_eats_cart, local_services, load_json,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323', '1', '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    local_services.set_params(utils.get_params(shipping_type='pickup'))

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater2'),
        json=dict(item_id=str('232323'), **EMPTY_PROPERTIES),
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert (
        resp_json['cart']['delivery_time']['min']
        == local_services.catalog_place_response['place']['timings'][
            'preparation'
        ]
        + local_services.catalog_place_response['place']['timings'][
            'extra_preparation'
        ]
    )
    assert (
        resp_json['cart']['delivery_time']['max']
        == local_services.catalog_place_response['place']['timings'][
            'preparation'
        ]
        + local_services.catalog_place_response['place']['timings'][
            'extra_preparation'
        ]
    )
