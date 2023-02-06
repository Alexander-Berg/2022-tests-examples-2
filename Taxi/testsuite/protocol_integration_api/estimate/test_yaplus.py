import pytest

TURBOAPP_USER_WITH_CASHBACK = {
    'phone': '+79061112288',
    'personal_phone_id': 'p00000000000000000000008',
    'user_id': 'turboapp-user-with-cashback',
}

TURBOAPP_USER_WITHOUT_CASHBACK = {
    'phone': '+79061112288',
    'personal_phone_id': 'p00000000000000000000008',
    'user_id': 'turboapp-user-without-cashback',
}

COST_BREAKDOWN_YAPLUS_CASHBACK = [
    {
        'display_amount': 'Ride ' '1,000 ' 'rub, ' '~1 ' 'min',
        'display_name': 'cost',
    },
]


COST_BREAKDOWN_YAPLUS_DISCOUNT = [
    {
        'display_amount': 'Ride ' '900 ' 'rub, ' '~1 ' 'min',
        'display_name': 'cost',
    },
    {
        'display_amount': '1,000 ' 'rub',
        'display_name': 'cost_without_discount',
    },
    {'display_amount': '10%', 'display_name': 'discount'},
    {'display_amount': '10%', 'display_name': 'total_discount'},
]


OFFER_YAPLUS_MODIFIERS = {
    'items': [
        {
            'pay_subventions': True,
            'reason': 'ya_plus',
            'tariff_categories': ['business', 'comfortplus'],
            'type': 'multiplier',
            'value': '0.900000',
        },
    ],
}


pytestmark = [
    pytest.mark.now('2017-05-25T11:30:00+0300'),
    pytest.mark.config(
        ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
        ALICE_APPLY_PLUS_PRICE_MODIFIER=True,
        APPLICATION_BRAND_CATEGORIES_SETS={
            '__default__': [
                'econom',
                'comfortplus',
                'child_tariff',
                'minivan',
            ],
        },
        ROUTER_MAPS_ENABLED=True,
        INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
        INTEGRATION_API_ENABLED_YA_PLUS_FOR_SOURCE=['turboapp'],
    ),
    pytest.mark.experiments3(filename='experiments3_offer_coupon.json'),
    pytest.mark.user_experiments('fixed_price', 'no_cars_order_available'),
]


@pytest.mark.parametrize(
    'user, user_total_price, expected_price,'
    'expected_cost_breakdown, expected_price_modifiers',
    [
        pytest.param(
            TURBOAPP_USER_WITH_CASHBACK,
            1000,
            '1,000 rub',
            COST_BREAKDOWN_YAPLUS_CASHBACK,
            None,
            id='user has cashback',
        ),
        pytest.param(
            TURBOAPP_USER_WITHOUT_CASHBACK,
            None,
            '900 rub',
            COST_BREAKDOWN_YAPLUS_DISCOUNT,
            OFFER_YAPLUS_MODIFIERS,
            id='user hasn`t cashback',
        ),
        pytest.param(
            TURBOAPP_USER_WITH_CASHBACK,
            None,
            '900 rub',
            COST_BREAKDOWN_YAPLUS_DISCOUNT,
            OFFER_YAPLUS_MODIFIERS,
            marks=[
                pytest.mark.config(
                    CASHBACK_FOR_PLUS_COUNTRIES={
                        'check_enabled': True,
                        'countries': [],
                    },
                ),
            ],
            id='user has cashback, but disabled for country',
        ),
    ],
)
def test_user_price(
        taxi_integration,
        mockserver,
        db,
        discounts,
        load_json,
        pricing_data_preparer,
        user,
        user_total_price,
        expected_price,
        expected_cost_breakdown,
        expected_price_modifiers,
):
    pricing_data_preparer.set_cost(900, 900)
    pricing_data_preparer.set_strikeout(1000)
    pricing_data_preparer.set_meta('user_total_price', user_total_price)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'user': user,
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'turboapp',
        'all_classes': False,
        'chainid': 'chainid_1',
        'payment': {'payment_method_id': 'card-x7698', 'type': 'card'},
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()

    service_level = response_value['service_levels'][0]
    assert service_level['price'] == expected_price
    assert (
        service_level['cost_message_details']['cost_breakdown']
        == expected_cost_breakdown
    )

    offer_id = response_value.pop('offer')
    offer = db.order_offers.find_one({'_id': offer_id})
    for offer_price in offer['prices']:
        assert offer_price['price'] == 900.0
        assert offer_price['driver_price'] == 900.0
    if expected_price_modifiers:
        assert 'price_modifiers' in offer
        assert offer['price_modifiers'] == expected_price_modifiers
    else:
        assert 'price_modifiers' not in offer


@pytest.mark.parametrize(
    'cashback_fixed_price,'
    'user_total_price,'
    'cashback_rate,'
    'unite_total_price_enabled,'
    'user_ride_price,'
    'expected_cashback',
    [
        pytest.param(
            None, None, None, None, None, None, id='no cashback, no unite',
        ),
        pytest.param(None, None, None, 1, 900, None, id='no cashback, unite'),
        pytest.param(
            100, 1000, None, None, None, '100', id='plus cashback, no unite',
        ),
        pytest.param(
            100, 1000, None, 1, 900, '100', id='plus cashback, unite',
        ),
        pytest.param(
            None,
            None,
            0.05,
            None,
            None,
            '45',
            id='marketing cashback, no unite',
        ),
        pytest.param(
            None, None, 0.05, 1, 900, '45', id='marketing cashback, unite',
        ),
        pytest.param(
            100, 1000, 0.05, None, None, '145', id='both cashbacks, no unite',
        ),
        pytest.param(
            100, 1000, 0.05, 1, 900, '145', id='both cashbacks, unite',
        ),
        pytest.param(
            None,
            None,
            0.049,
            None,
            None,
            '45',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=True)),
            id='marketing cashbacks, no unite, ceil',
        ),
        pytest.param(
            None,
            None,
            0.049,
            None,
            None,
            '44',
            id='marketing cashbacks, no unite, floor',
        ),
        pytest.param(
            None,
            None,
            0.049,
            1,
            900,
            '45',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=True)),
            id='marketing cashback, unite, ceil',
        ),
        pytest.param(
            None,
            None,
            0.049,
            1,
            900,
            '44',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=False)),
            id='marketing cashback, unite, floor',
        ),
        pytest.param(
            100,
            1000,
            0.049,
            1,
            900,
            '145',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=True)),
            id='both cashbacks, unite, ceil',
        ),
        pytest.param(
            100,
            1000,
            0.049,
            1,
            900,
            '144',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=False)),
            id='both cashbacks, unite, floor',
        ),
    ],
)
def test_cashback(
        taxi_integration,
        mockserver,
        db,
        load_json,
        pricing_data_preparer,
        cashback_fixed_price,
        user_total_price,
        cashback_rate,
        unite_total_price_enabled,
        user_ride_price,
        expected_cashback,
):
    if cashback_fixed_price and unite_total_price_enabled:
        pricing_data_preparer.set_cost(1000, 900)
    else:
        pricing_data_preparer.set_cost(900, 900)
    pricing_data_preparer.set_strikeout(1000)
    pricing_data_preparer.set_meta(
        'cashback_fixed_price', cashback_fixed_price,
    )
    pricing_data_preparer.set_meta('user_total_price', user_total_price)
    pricing_data_preparer.set_meta('cashback_rate', cashback_rate)
    pricing_data_preparer.set_meta(
        'unite_total_price_enabled', unite_total_price_enabled,
    )
    pricing_data_preparer.set_meta('user_ride_price', user_ride_price)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'user': TURBOAPP_USER_WITH_CASHBACK,
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'turboapp',
        'all_classes': False,
        'chainid': 'chainid_1',
        'payment': {'payment_method_id': 'card-x7698', 'type': 'card'},
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()

    service_level = response_value['service_levels'][0]
    response_cost_breakdown = {
        v['display_name']: v['display_amount']
        for v in service_level['cost_message_details']['cost_breakdown']
    }

    if cashback_fixed_price:
        assert service_level['price'] == '1,000 rub'
        assert response_cost_breakdown['cost'] == 'Ride 1,000 rub, ~1 min'
    else:
        assert service_level['price'] == '900 rub'
        assert response_cost_breakdown['cost'] == 'Ride 900 rub, ~1 min'

    if expected_cashback:
        assert response_cost_breakdown['cashback'] == expected_cashback
    else:
        assert 'cashback' not in response_cost_breakdown
