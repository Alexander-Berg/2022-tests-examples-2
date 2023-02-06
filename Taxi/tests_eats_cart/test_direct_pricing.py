import copy

import pytest

from . import utils


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'pricing_status,expected_fee,expected_message',
    (
        pytest.param(
            200, '100', 'Закажите ещё на 100 ₽ для доставки за 500 ₽', id='ok',
        ),
        pytest.param(
            500,
            '20',
            'Закажите ещё на 50 ₽ для доставки за 10 ₽',
            id='catalog_fallback',
        ),
    ),
)
async def test_direct_pricing(
        taxi_eats_cart,
        local_services,
        pricing_status,
        expected_fee,
        expected_message,
        eats_cart_cursor,
):
    place_id = 123
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323']
    eater_id = 'eater4'
    phone_id = 'phone4'
    x_platform = 'ios_app'
    x_app_version = '5.20.0'
    x_device_id = 'user_device-id'
    cart_id = '00000000-0000-0000-0000-000000000002'
    travel_duration = 5
    subtotal = '100'  # 50 * 2 смотри sql
    params = {
        'latitude': 55.75,  # Moscow
        'longitude': 37.62,
        'shippingType': 'delivery',
        'deliveryTime': '2021-04-04T08:00:00+00:00',
    }

    local_services.set_params(copy.deepcopy(params))
    local_services.delivery_price_status = pricing_status
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
    local_services.cart_eta = {
        place_id: utils.CartEta(
            place_id=place_id, delivery_time=travel_duration,
        ),
    }
    local_services.catalog_place_response.update(
        {
            'offer': {
                'position': [0, 0],
                'request_time': '2021-04-04T08:00:00+00:00',
            },
        },
    )

    def delivery_price_assertion(request):
        req = request.json

        assert (
            req['offer']
            == local_services.catalog_place_response['offer']['request_time']
        )

        place = local_services.catalog_place_response['place']

        assert req['place_info'] == {
            'place_id': str(place_id),
            'region_id': str(place['location']['region_id']),
            'brand_id': str(place['brand']['id']),
            'position': place['location']['position'],
            'type': 'native',
            'business_type': 'restaurant',
            'currency': {'sign': place['currency']['sign']},
        }

        assert req['user_info'] == {
            'position': [
                local_services.request_params['longitude'],
                local_services.request_params['latitude'],
            ],
            'device_id': x_device_id,
            'user_id': eater_id,
            'personal_phone_id': phone_id,
        }

        assert req['zone_info']['zone_type'] == 'pedestrian'

        assert req['cart_info']['subtotal'] == subtotal
        assert req['route_info']['time_sec'] == travel_duration * 60

        assert request.headers['x-platform'] == x_platform
        assert request.headers['x-app-version'] == x_app_version

    local_services.delivery_price_assertion = delivery_price_assertion

    headers = utils.get_auth_headers(eater_id, phone_id)
    headers.update(
        {
            'x-platform': x_platform,
            'x-app-version': x_app_version,
            'x-device-id': x_device_id,
        },
    )

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert data['decimal_delivery_fee'] == expected_fee
    assert data['requirements']['next_delivery_threshold'] == expected_message

    eats_cart_cursor.execute(
        f"""
        SELECT
            payload
        FROM eats_cart.extra_fees
        WHERE
            cart_id = '{cart_id}'
            AND
            type = 'delivery_fee'
        ORDER BY type
        """,
    )
    result = eats_cart_cursor.fetchall()

    assert len(result) == 1
    assert result[0][0]['travel_duration'] == travel_duration * 60


@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_direct_pricing_lock_cart(taxi_eats_cart, local_services):
    place_id = 123
    delivery_time = 10
    local_services.set_place_slug('place123')
    offer_time = '2021-04-04T08:00:00+00:00'
    eater_id = 'eater4'
    expected_fee = '100'

    local_services.core_items_request = ['232323']
    params = {
        'latitude': 55.75,  # Moscow
        'longitude': 37.62,
        'shippingType': 'delivery',
        'deliveryTime': '2021-04-04T08:00:00+00:00',
    }

    local_services.set_params(copy.deepcopy(params))
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': expected_fee,
            'next_delivery_threshold': {
                'amount_need': '100',
                'next_cost': '500',
            },
        },
        'surge_result': {
            'placeId': place_id,
            'nativeInfo': {
                'surgeLevel': 10,
                'deliveryFee': 100,
                'loadLevel': 100,
            },
        },
        'service_fee': '15',
    }
    local_services.cart_eta = {
        place_id: utils.CartEta(
            place_id=place_id, delivery_time=delivery_time,
        ),
    }
    local_services.catalog_place_response.update(
        {'offer': {'position': [0, 0], 'request_time': offer_time}},
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, eater_id, utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    data = response.json()

    assert not data['surge_is_actual']
    assert data['surge_info'] == {
        'level': 10,
        'delivery_fee': '100',
        'additional_fee': '100',
    }


@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.now('2021-04-03T01:22:36+03:00')
@pytest.mark.parametrize(
    'surge_is_actual',
    (
        pytest.param(
            False,
            marks=utils.disable_surge_checkout_check(5 * 60),
            id='false',
        ),
        pytest.param(
            True, marks=utils.disable_surge_checkout_check(20 * 60), id='true',
        ),
    ),
)
async def test_disable_surge_check_on_checkout(
        taxi_eats_cart, local_services, surge_is_actual,
):
    """
    Проверяем, что проверка суржа на чекауте
    контролирутеся экспериментом
    """

    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323']
    eater_id = 'eater4'

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
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 100,
                'deliveryFee': 100,
                'loadLevel': 100,
            },
        },
        'service_fee': '15',
    }

    local_services.catalog_place_response.update(
        {
            'offer': {
                'position': [0, 0],
                'request_time': '2021-04-04T08:00:00+00:00',
            },
        },
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, eater_id, utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    data = response.json()
    assert data['surge_is_actual'] == surge_is_actual


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text(delivery_fee_subtitle='message.native_delivery')
@pytest.mark.parametrize(
    'next_delivery_threshold,expected_message',
    (
        pytest.param(
            {'amount_need': '200', 'next_cost': '400'},
            'Закажите ещё на 200 ₽ для доставки за 400 ₽',
            id='has_next_delivery_threshold',
        ),
        pytest.param(
            None, 'Доставка Яндекс.Еды', id='null_next_delivery_threshold',
        ),
    ),
)
async def test_direct_pricing_surge(
        taxi_eats_cart,
        local_services,
        next_delivery_threshold,
        expected_message,
):
    """
    Проверяет, что additional payments формируется
    независимо от состояния суржа, а только от
    наличия next_delivery_threshold в ответе прайсинга
    """

    place_id = 123
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323']
    eater_id = 'eater4'
    phone_id = 'phone4'
    travel_duration = 5
    params = {
        'latitude': 55.75,  # Moscow
        'longitude': 37.62,
        'shippingType': 'delivery',
        'deliveryTime': '2021-04-04T08:00:00+00:00',
    }

    local_services.set_params(copy.deepcopy(params))
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'next_delivery_threshold': next_delivery_threshold,
        },
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 100,
                'deliveryFee': 100,
                'loadLevel': 100,
            },
        },
        'service_fee': '15',
    }
    local_services.cart_eta = {
        place_id: utils.CartEta(
            place_id=place_id, delivery_time=travel_duration,
        ),
    }

    headers = utils.get_auth_headers(eater_id, phone_id)

    response = await taxi_eats_cart.get(
        '/api/v1/cart', params=params, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()

    if next_delivery_threshold is not None:
        assert (
            data['requirements']['next_delivery_threshold'] == expected_message
        )
    else:
        assert 'next_delivery_threshold' not in data['requirements']
    assert (
        data['additional_payments'][0]['subtitle']['text'] == expected_message
    )


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
async def test_direct_pricing_zero_fee_surge(taxi_eats_cart, local_services):
    """
    Проверяет, что при нулевой цене доставки
    в ответе корзины не будет объекта суржа
    """

    place_id = 123
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323']
    eater_id = 'eater4'
    phone_id = 'phone4'
    travel_duration = 5
    params = {
        'latitude': 55.75,  # Moscow
        'longitude': 37.62,
        'shippingType': 'delivery',
        'deliveryTime': '2021-04-04T08:00:00+00:00',
    }

    local_services.set_params(copy.deepcopy(params))
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '0',
            'next_delivery_threshold': {
                'amount_need': '200',
                'next_cost': '400',
            },
        },
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 100,
                'deliveryFee': 0,
                'loadLevel': 100,
            },
        },
        'service_fee': '15',
    }
    local_services.cart_eta = {
        place_id: utils.CartEta(
            place_id=place_id, delivery_time=travel_duration,
        ),
    }

    headers = utils.get_auth_headers(eater_id, phone_id)

    response = await taxi_eats_cart.get(
        '/api/v1/cart', params=params, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert 'surge' not in data


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize('cart_delivery_price_received', [False, True])
async def test_direct_pricing_no_cart_delivery_price(
        taxi_eats_cart,
        local_services,
        eats_cart_cursor,
        cart_delivery_price_received,
):
    """
    Проверяет, что при нулевой цене доставки
    в ответе корзины не будет объекта суржа
    """

    place_id = 123
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323']
    eater_id = 'eater4'
    phone_id = 'phone4'
    cart_id = '00000000000000000000000000000002'
    travel_duration = 5
    params = {
        'latitude': 55.75,  # Moscow
        'longitude': 37.62,
        'shippingType': 'delivery',
        'deliveryTime': '2021-04-04T08:00:00+00:00',
    }
    delivery_price_response = {
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 100,
                'deliveryFee': 0,
                'loadLevel': 100,
            },
        },
        'service_fee': '15',
    }
    if cart_delivery_price_received:
        delivery_price_response['cart_delivery_price'] = {
            'min_cart': '100',
            'delivery_fee': '0',
            'next_delivery_threshold': {
                'amount_need': '200',
                'next_cost': '400',
            },
        }

    local_services.set_params(copy.deepcopy(params))
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = delivery_price_response
    local_services.cart_eta = {
        place_id: utils.CartEta(
            place_id=place_id, delivery_time=travel_duration,
        ),
    }

    headers = utils.get_auth_headers(eater_id, phone_id)

    response = await taxi_eats_cart.get(
        '/api/v1/cart', params=params, headers=headers,
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(
        f"""SELECT payload FROM eats_cart.extra_fees
            WHERE type='delivery_fee' AND cart_id='{cart_id}'""",
    )
    result = eats_cart_cursor.fetchall()[0][0]
    if cart_delivery_price_received:
        assert result['delivery_pricing']['min_cart'] == '100'
    else:
        assert 'delivery_pricing' not in result
