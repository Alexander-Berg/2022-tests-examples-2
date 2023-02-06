import copy
import decimal

import pytest

from . import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T08:00:00+00:00',
}

EATER_ID = 'eater4'
PLACE_SLUG = 'place123'
CORE_ITEMS = ['232323']
CART_ID = '00000000000000000000000000000002'


def make_subtitle(weight_fee):
    result = ''
    fee = weight_fee if weight_fee is not None else 0
    if fee != 0:
        result += f'В том числе {fee} ₽ за доставку 2 кг\n'
    result += f'Закажите ещё на 100 ₽ для доставки за {500 + fee} ₽'
    return result


def make_description(weight_fee):
    fee = 0 if weight_fee is None else weight_fee
    return (
        f'Стоимость доставки: 100 ₽\nДоплата за вес: {fee} ₽\n\n'
        'Доставка осуществляется средствами Яндекса'
    )


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text(
    delivery_fee_main_text='message.delivery_fee_with_fees_text',
)
@pytest.mark.parametrize(
    'weight_fee',
    [
        pytest.param(None, id='without_weight_fee'),
        pytest.param(0, id='weight_fee=0'),
        pytest.param(10, id='with_weight_fee'),
    ],
)
async def test_cart_weight_fee(
        taxi_eats_cart, local_services, eats_cart_cursor, weight_fee,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = CORE_ITEMS

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

    if weight_fee is not None:
        local_services.delivery_price_response['cart_delivery_price'][
            'weight_fee'
        ] = str(weight_fee)

    local_services.set_params(copy.deepcopy(PARAMS))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=PARAMS, headers=utils.get_auth_headers(EATER_ID),
    )

    assert local_services.mock_eda_delivery_price.times_called == 1

    assert response.status_code == 200
    additional_payment = response.json()['additional_payments'][0]
    assert additional_payment['subtitle']['text'] == make_subtitle(weight_fee)
    assert additional_payment['action']['description'][
        'text'
    ] == make_description(weight_fee)
    assert response.json()['total'] == 197 + (
        weight_fee if weight_fee is not None else 0
    )

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount, payload FROM eats_cart.extra_fees '
        'WHERE cart_id = %s AND type = \'weight_fee\'',
        (CART_ID,),
    )
    result = eats_cart_cursor.fetchall()

    assert len(result) == (1 if weight_fee is not None else 0)
    if weight_fee is not None:
        assert result == [
            [
                '00000000-0000-0000-0000-000000000002',
                'weight_fee',
                decimal.Decimal(weight_fee),
                None,
            ],
        ]


@pytest.mark.parametrize(
    'exp_enabled',
    [
        pytest.param(False, id='weight_fee_exp_disabled'),
        pytest.param(
            True,
            marks=utils.weight_fee_experiment(),
            id='weight_fee_exp_enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'weight_fee',
    [
        pytest.param(None, id='without_weight_fee'),
        pytest.param(10, id='with_weight_fee'),
    ],
)
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql(
    'eats_cart', files=['insert_values.sql', 'add_extra_fees.sql'],
)
async def test_cart_weight_fee_stored_fee(
        taxi_eats_cart,
        local_services,
        eats_cart_cursor,
        exp_enabled,
        weight_fee,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = CORE_ITEMS

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

    if exp_enabled and weight_fee is not None:
        local_services.delivery_price_response['cart_delivery_price'][
            'weight_fee'
        ] = str(weight_fee)

    local_services.set_params(copy.deepcopy(PARAMS))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=PARAMS, headers=utils.get_auth_headers(EATER_ID),
    )

    assert local_services.mock_eda_delivery_price.times_called == 1
    assert response.status_code == 200

    eats_cart_cursor.execute(
        'SELECT cart_id, type, amount, payload FROM eats_cart.extra_fees '
        'WHERE cart_id = %s AND type = \'weight_fee\'',
        (CART_ID,),
    )
    result = eats_cart_cursor.fetchall()

    assert len(result) == 1

    assert result == [
        [
            '00000000-0000-0000-0000-000000000002',
            'weight_fee',
            decimal.Decimal(
                weight_fee if exp_enabled and weight_fee is not None else 0,
            ),
            None,
        ],
    ]


@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'has_experiment',
    [
        pytest.param(None, id='weight_fee_exp_not_found'),
        pytest.param(
            False,
            marks=utils.weight_fee_experiment(False),
            id='weight_fee_exp_disabled',
        ),
        pytest.param(
            True,
            marks=utils.weight_fee_experiment(),
            id='weight_fee_exp_enabled',
        ),
    ],
)
async def test_cart_weight_sending(
        taxi_eats_cart, local_services, has_experiment,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = CORE_ITEMS

    local_services.direct_pricing = True
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {'min_cart': '50', 'delivery_fee': '500'},
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }

    def delivery_price_assertion(request):
        if has_experiment:
            assert request.json['cart_info']['weight'] == 2000
        else:
            assert 'weight' not in request.json['cart_info']

    local_services.delivery_price_assertion = delivery_price_assertion
    local_services.set_params(copy.deepcopy(PARAMS))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=PARAMS, headers=utils.get_auth_headers(EATER_ID),
    )

    assert local_services.mock_eda_delivery_price.times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize('weight_fee', ['10', '0', None])
@pytest.mark.pgsql(
    'eats_cart', files=['insert_values.sql', 'add_extra_fees.sql'],
)
async def test_cart_weight_lock_cart(
        taxi_eats_cart, local_services, weight_fee,
):
    place_id = 123
    delivery_time = 10
    local_services.set_place_slug(PLACE_SLUG)
    offer_time = '2021-04-04T08:00:00+00:00'

    local_services.core_items_request = CORE_ITEMS
    local_services.set_params(copy.deepcopy(PARAMS))
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': '100',
            'weight_fee': weight_fee,
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
        taxi_eats_cart, EATER_ID, utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200
    data = response.json()

    assert data['surge_is_actual']
    assert data['surge_info'] == {
        'level': 10,
        'delivery_fee': '110',
        'additional_fee': '100',
    }
