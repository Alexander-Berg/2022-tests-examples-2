import json

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils


def _make_discount_item(is_cashback=False):
    return {
        'id': 'e7ffe6c7-ef99-4fc9-8575-efe73615a700',
        'is_cashback': is_cashback,
        'method': 'full',
        'reason': 'for_all',
    }


def _get_service_level(content, class_name):
    for sl in content['service_levels']:
        if sl['class'] == class_name:
            return sl
    return None


def _get_brandings(content, type, classes=None):
    result = []
    for sl in content['service_levels']:
        if classes is None or sl['class'] in classes:
            brandings = sl.get('brandings', [])
            cashback = [br for br in brandings if br['type'] == type]
            if cashback:
                result.append(cashback[0])
    return result


def _get_cashbacks(content, classes=None):
    return _get_brandings(content, 'cashback', classes=classes)


def _get_wallet_suggest(content):
    return _get_brandings(content, 'wallet_payment_method_suggest')


def assert_no_cashback(content, classes=None):
    assert not _get_cashbacks(content, classes=classes)


def assert_cashback(content, classes=None):
    cashbacks = _get_cashbacks(content, classes=classes)
    assert cashbacks
    assert len(classes) == len(cashbacks)


@pytest.mark.now('2017-05-26T03:40:00+0300')
@pytest.mark.user_experiments('fixed_price')
@ORDER_OFFERS_SAVE_SWITCH
def test_cashback_ok(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        mock_order_offers,
        order_offers_save_enabled,
):
    pricing_data_preparer.set_discount(
        _make_discount_item(is_cashback=True), 'vip',
    )
    pricing_data_preparer.set_meta('cashback_rate', 0.1, 'vip')

    pricing_data_preparer.set_discount(
        _make_discount_item(is_cashback=True), 'econom',
    )
    pricing_data_preparer.set_meta('cashback_rate', 0.1, 'econom')

    pricing_data_preparer.set_discount(
        _make_discount_item(is_cashback=False), 'comfortplus',
    )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    assert_cashback(content, classes=['vip', 'econom'])
    assert_no_cashback(content, classes=['comfortplus'])

    offer = utils.get_offer(
        content['offer'], db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1

    assert len(offer['discount']['cashbacks']) == 2
    assert len(offer['discount']['by_classes']) == 1


@pytest.mark.parametrize(
    'cashback_fixed_price,'
    'user_total_price,'
    'cashback_rate,'
    'unite_total_price_enabled,'
    'user_ride_price,'
    'marketing_cashback_fix,'
    'expected_cashback',
    [
        pytest.param(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            id='no cashback, no unite',
        ),
        pytest.param(
            None, None, None, 1, 900, None, None, id='no cashback, unite',
        ),
        pytest.param(
            100,
            1000,
            None,
            None,
            None,
            None,
            '100',
            id='plus cashback, no unite',
        ),
        pytest.param(
            100, 1000, None, 1, 900, None, '100', id='plus cashback, unite',
        ),
        pytest.param(
            None,
            None,
            0.05,
            None,
            None,
            None,
            '45',
            id='marketing cashback, no unite',
        ),
        pytest.param(
            None,
            None,
            0.05,
            1,
            900,
            None,
            '45',
            id='marketing cashback, unite',
        ),
        pytest.param(
            100,
            1000,
            0.05,
            None,
            None,
            None,
            '145',
            id='both cashbacks, no unite',
        ),
        pytest.param(
            100, 1000, 0.05, 1, 900, None, '145', id='both cashbacks, unite',
        ),
        pytest.param(
            None,
            None,
            0.049,
            None,
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
            None,
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
            None,
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
            None,
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
            None,
            '144',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=False)),
            id='both cashbacks, unite, floor',
        ),
        pytest.param(
            100,
            1000,
            0.049,
            1,
            900,
            100,
            '245',
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=True)),
            id='both cashbacks, unite, ceil',
        ),
    ],
)
@pytest.mark.now('2017-05-26T03:40:00+0300')
@pytest.mark.user_experiments('fixed_price', 'personal_wallet')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 1}},
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
def test_cashback_branding(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        cashback_fixed_price,
        user_total_price,
        cashback_rate,
        unite_total_price_enabled,
        user_ride_price,
        marketing_cashback_fix,
        expected_cashback,
):
    if cashback_fixed_price and unite_total_price_enabled:
        pricing_data_preparer.set_cost(1000, 900, 'vip')
    else:
        pricing_data_preparer.set_cost(900, 900, 'vip')

    if marketing_cashback_fix:
        pricing_data_preparer.set_meta(
            'marketing_cashback:fix', marketing_cashback_fix, 'vip',
        )

    pricing_data_preparer.set_discount(
        _make_discount_item(is_cashback=True), 'vip',
    )
    pricing_data_preparer.set_meta(
        'cashback_fixed_price', cashback_fixed_price, 'vip',
    )
    pricing_data_preparer.set_meta('user_total_price', user_total_price, 'vip')
    pricing_data_preparer.set_meta('cashback_rate', cashback_rate, 'vip')
    pricing_data_preparer.set_meta(
        'unite_total_price_enabled', unite_total_price_enabled, 'vip',
    )
    pricing_data_preparer.set_meta('user_ride_price', user_ride_price, 'vip')

    pricing_data_preparer.set_discount(
        _make_discount_item(is_cashback=True), 'econom',
    )

    pricing_data_preparer.set_meta('cashback_rate', 0.0, 'econom')

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()

    service_level_vip = _get_service_level(content, 'vip')
    if cashback_fixed_price:
        assert service_level_vip['price'] == '1,000\xa0$SIGN$$CURRENCY$'
    else:
        assert service_level_vip['price'] == '900\xa0$SIGN$$CURRENCY$'

    assert_no_cashback(content, classes=['econom'])

    if expected_cashback:
        assert_cashback(content, classes=['vip'])
        branding = _get_cashbacks(content, classes=['vip'])[0]
        assert branding == {
            'title': 'Кешбэк за поездку',
            'type': 'cashback',
            'value': expected_cashback,
            'tooltip': {'text': 'Кешбэк за поездку'},
        }
    else:
        assert_no_cashback(content, classes=['vip'])


@pytest.mark.parametrize('business_unavailable', (False, True))
@pytest.mark.now('2017-05-26T03:40:00+0300')
@pytest.mark.user_experiments('fixed_price', 'personal_wallet')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 0.1}},
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
def test_no_cashback_branding_on_service_unavailable(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        mockserver,
        business_unavailable,
):
    pricing_data_preparer.set_discount(_make_discount_item(is_cashback=True))
    pricing_data_preparer.set_meta('cashback_rate', 0.1)
    pricing_data_preparer.set_meta('cashback_rate', 0.0, 'econom')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        retval = load_json('driver_eta.json')
        if business_unavailable:
            for class_name, class_info in retval['classes'].items():
                if class_name == 'business':
                    class_info['found'] = False
                    del class_info['estimated_distance']
                    del class_info['estimated_time']

        return retval

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    if business_unavailable:
        assert_no_cashback(content, classes=['business'])
    else:
        assert_cashback(content, classes=['business'])


@pytest.mark.parametrize(
    'balance, expect_branding', [('300', True), ('0', False)],
)
@pytest.mark.now('2017-05-26T03:40:00+0300')
@pytest.mark.user_experiments('fixed_price', 'personal_wallet')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 0.1}},
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
def test_wallet_suggest_branding(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        mockserver,
        balance,
        expect_branding,
):
    @mockserver.json_handler('/personal_wallet/v1/balances')
    def _mock_balances(request):
        request_json = json.loads(request.get_data())
        assert request_json['yandex_uid']
        return {
            'balances': [
                {
                    'wallet_id': 'wallet_id/some_number_value',
                    'currency': 'RUB',
                    'is_new': True,
                    'balance': balance,
                    'payment_orders': [],
                },
            ],
            'available_deposit_payment_methods': [],
        }

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()

    brandings = _get_wallet_suggest(content)
    if expect_branding:
        assert brandings[0] == {
            'type': 'wallet_payment_method_suggest',
            'tooltip': {'text': 'можно оплатить кошельком'},
        }
    else:
        assert not brandings


@pytest.mark.now('2017-05-26T03:40:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.parametrize(
    'exp_is_ok',
    [
        False,
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_create_business_account.json',
                )
            ),
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_create_business_account_wrong.json',
                )
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'has_translation',
    [
        True,
        pytest.param(
            True,
            marks=(
                pytest.mark.translations(
                    client_messages={'no': {'ru': 'translation'}},
                )
            ),
        ),
    ],
)
def test_create_business_account_branding(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        exp_is_ok,
        has_translation,
):
    EXP_ENABLED_FOR_TARIFF_CLASS = 'minivan'
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()

    experiment_tariff_classes = [
        sl
        for sl in content['service_levels']
        if sl['class'] == EXP_ENABLED_FOR_TARIFF_CLASS
    ]
    # check tariff class is in response,
    # so that the next assert actually does something
    assert experiment_tariff_classes

    for sl in content['service_levels']:
        brandings = sl.get('brandings', [])

        filtered_brandings = [
            br for br in brandings if br['type'] == 'create_business_account'
        ]

        if (
                exp_is_ok
                and has_translation
                and sl['class'] == EXP_ENABLED_FOR_TARIFF_CLASS
        ):
            assert len(filtered_brandings) == 1
            assert filtered_brandings[0] == {
                'type': 'create_business_account',
                'title': 'Подключить доставку для бизнеса',
            }
        else:
            assert len(filtered_brandings) == 0
