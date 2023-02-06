import json
import operator

import pytest

from protocol.requestconfirm.test_requestconfirm import PricingCompleteData

ORDER_ID = '1c83b49edb274ce0992f337061047375'
ALIAS_ID = 'db60d02916ae4a1a91eafa3a1a8ed04d'


def make_current_prices(current_prices):
    current_prices['cost_breakdown'] = sorted(
        current_prices['cost_breakdown'], key=operator.itemgetter('type'),
    )
    return current_prices


def make_request(taxi_protocol, extra='1000', pricing_complete_data=None):
    request_params = {
        'orderid': ALIAS_ID,
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': extra,
        'calc_method': 2,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
    }
    if pricing_complete_data:
        request_params.update(pricing_complete_data.to_json())
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'db_complement, request_complement',
    (
        (
            {'type': 'personal_wallet', 'payment_method_id': 'w/1234'},
            {'type': 'personal_wallet', 'payment_method_id': 'w/1234'},
        ),
        (
            {
                'type': 'personal_wallet',
                'payment_method_id': 'w/1234',
                'withdraw_amount': 99,
            },
            {
                'type': 'personal_wallet',
                'payment_method_id': 'w/1234',
                'withdraw_amount': '99.0000',
            },
        ),
    ),
)
@pytest.mark.parametrize(
    'with_pricing_complete_data',
    [False, True],
    ids=['with_pricing_complete_data', 'without_pricing_complete_data'],
)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_ENABLED_REQUESTCONFIRM=True)
@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_current_prices_calculator(
        taxi_protocol,
        db,
        mockserver,
        db_complement,
        request_complement,
        with_pricing_complete_data,
):
    @mockserver.json_handler(
        '/persey_payments/internal/v1/charity/ride_donation/estimate',
    )
    def _(request):
        return {}

    @mockserver.json_handler(
        '/current_prices_calculator/v1/internal/current_prices',
    )
    def mock_current_prices_calculator(request):
        assert request.headers['Content-Type'] == 'application/json'
        req = json.loads(request.get_data())
        assert req == {
            'cost': '1000.000000',
            'current_cost': '300.000000',
            'fixed_price': True,
            'nearest_zone': 'moscow',
            'order_id': '1c83b49edb274ce0992f337061047375',
            'payment': {
                'complements': [request_complement],
                'payment_method_id': 'card-1234',
                'type': 'card',
            },
            'pricing_data': {
                'currency': 'RUB',
                'price_total': '2510.000000',
                'discount_cashback_rate': '0.100000',
                'max_discount_cashback': '30.000000',
                'marketing_cashback': {
                    'rates': [
                        {
                            'fix': '22.0000',
                            'max_value': '100.0000',
                            'rate': '0.1000',
                            'sponsor': 'fintech',
                        },
                    ],
                    'fix': '22.0000',
                },
            },
            'status': 'finished',
            'taxi_status': 'complete',
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'using_new_pricing': True,
            'yandex_uid': '4003514353',
            'user_phone_id': '5714f45e98956f06baaae3d4',
        }
        return {
            'user_total_price': '123',
            'user_total_display_price': '100',
            'user_ride_display_price': '90',
            'cashback_price': '23',
            'discount_cashback': '10.0',
            'cost_breakdown': [
                {'type': 'card', 'amount': '100'},
                {'type': 'personal_wallet', 'amount': '20'},
            ],
            'kind': 'taximeter',
            'cashback_by_sponsor': [
                {'sponsor': 'portal', 'value': '1.0'},
                {'sponsor': 'fintech', 'value': '13.0'},
            ],
        }

    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.request.payment.complements': [db_complement],
                'payment_tech.complements': [db_complement],
            },
        },
    )

    pricing_complete_data = None
    if with_pricing_complete_data:
        pricing_complete_data = PricingCompleteData()
        pricing_complete_data.set_final_cost(driver_cost=100.0, user_cost=90.0)
        pricing_complete_data.set_final_cost_meta(
            {'driver': {'meta_1': 1}, 'user': {'meta_2': 2}},
        )
    make_request(taxi_protocol, pricing_complete_data=pricing_complete_data)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert proc['order']['user_uid'] == '4003514353'

    given_current_prices = proc['order']['current_prices']
    given_current_prices = make_current_prices(given_current_prices)
    expected_current_prices = make_current_prices(
        {
            'user_total_price': 123.0,
            'user_total_display_price': 100.0,
            'user_ride_display_price': 90.0,
            'cashback_price': 23.0,
            'discount_cashback': 10.0,
            'cost_breakdown': [
                {'type': 'card', 'amount': 100.0},
                {'type': 'personal_wallet', 'amount': 20.0},
            ],
            'kind': 'final_cost',
            'cashback_by_sponsor': {'fintech': 13.0, 'portal': 1.0},
        },
    )
    if with_pricing_complete_data:
        expected_current_prices.update(
            {
                'final_cost': {
                    'driver': {'total': 100.0},
                    'user': {'total': 90.0},
                },
                'final_cost_meta': {
                    'driver': {'meta_1': 1},
                    'user': {'meta_2': 2},
                },
            },
        )

    assert given_current_prices == expected_current_prices
    assert mock_current_prices_calculator.times_called == 1


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_ENABLED_REQUESTCONFIRM=True)
@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_cpc_with_coupon(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/persey_payments/internal/v1/charity/ride_donation/estimate',
    )
    def _(request):
        return {}

    @mockserver.json_handler(
        '/current_prices_calculator/v1/internal/current_prices',
    )
    def mock_current_prices_calculator(request):
        req = json.loads(request.get_data())
        assert req['cost'] == '900.000000'
        return {
            'user_total_price': '123',
            'user_total_display_price': '100',
            'user_ride_display_price': '90',
            'cashback_price': '23',
            'discount_cashback': '10.0',
            'cost_breakdown': [
                {'type': 'card', 'amount': '100'},
                {'type': 'personal_wallet', 'amount': '20'},
            ],
            'kind': 'taximeter',
        }

    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.coupon': {
                    'id': 'coupon',
                    'valid': True,
                    'valid_any': False,
                    'was_used': True,
                    'value': 100,
                },
            },
        },
    )

    make_request(taxi_protocol)
    assert mock_current_prices_calculator.times_called == 1


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_ENABLED_REQUESTCONFIRM=True)
@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_fallback_on_cost_utils(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/persey_payments/internal/v1/charity/ride_donation/estimate',
    )
    def _(request):
        return {}

    @mockserver.json_handler(
        '/current_prices_calculator/v1/internal/current_prices',
    )
    def mock_current_prices_calculator(request):
        return mockserver.make_response('', 500)

    make_request(taxi_protocol)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'

    current_prices = proc['order'].get('current_prices')
    assert current_prices is not None
    assert mock_current_prices_calculator.times_called == 1


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_ENABLED_REQUESTCONFIRM=True)
@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_charity_updates(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/current_prices_calculator/v1/internal/current_prices',
    )
    def mock_current_prices_calculator(request):
        return {
            'user_total_price': '123',
            'user_total_display_price': '100',
            'user_ride_display_price': '90',
            'cashback_price': '23',
            'discount_cashback': '10.0',
            'cost_breakdown': [
                {'type': 'card', 'amount': '100'},
                {'type': 'personal_wallet', 'amount': '20'},
            ],
            'kind': 'final_cost',
        }

    @mockserver.json_handler(
        '/persey_payments/internal/v1/charity/ride_donation/estimate',
        prefix=True,
    )
    def mock_persey(request):
        assert request.query_string.decode() == (
            f'order_id={ORDER_ID}&'
            'payment_tech_type=card&'
            'ride_cost=90.000000'
        )
        return {'amount_info': {'amount': '6', 'currency_code': 'RUB'}}

    make_request(taxi_protocol)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'

    current_prices = proc['order'].get('current_prices')
    assert current_prices is not None

    # ride user_total_display_price + charity
    assert str(current_prices['user_total_display_price']) == '106.0'

    assert mock_current_prices_calculator.times_called == 1
    assert mock_persey.times_called == 1


def update_meta(db, cashback_rate, cashback_max_value):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$unset': {
                'order.pricing_data.additional_prices.paid_supply'
                '.meta.cashback_rate': '',
                'order.pricing_data.additional_prices.paid_supply'
                '.meta.cashback_max_value': '',
                'order.pricing_data.user.meta.cashback_rate': '',
                'order.pricing_data.user.meta.cashback_max_value': '',
            },
        },
    )

    if cashback_rate is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.pricing_data.additional_prices.paid_supply.meta'
                    '.cashback_rate': cashback_rate,
                    'order.pricing_data.user'
                    '.meta.cashback_rate': cashback_rate,
                },
            },
        )
    if cashback_max_value is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.pricing_data.additional_prices.paid_supply'
                    '.meta.cashback_max_value': cashback_max_value,
                    'order.pricing_data.user'
                    '.meta.cashback_max_value': cashback_max_value,
                },
            },
        )


@pytest.mark.parametrize(
    'cashback_rate,max_value,expected_cashback',
    (
        (None, None, None),
        (0.0, None, None),
        (0.05, None, 50.0),
        (None, 3, None),
        (0.05, 3.0, 3.0),
    ),
)
@pytest.mark.config(CASHBACK_FOR_CASH_ENABLED=True)
def test_discount_cashback_calculation(
        taxi_protocol,
        db,
        mockserver,
        cashback_rate,
        max_value,
        expected_cashback,
):
    update_meta(db, cashback_rate, max_value)
    make_request(taxi_protocol)

    proc = db.order_proc.find_one(ORDER_ID)
    current_prices = proc['order'].get('current_prices')
    assert current_prices is not None

    assert current_prices.get('discount_cashback') == expected_cashback


@pytest.mark.parametrize(
    'expected_cashback',
    [
        pytest.param(99.0),
        pytest.param(
            100.0,
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=True)),
        ),
    ],
)
@pytest.mark.config(CASHBACK_FOR_CASH_ENABLED=True)
def test_discount_cashback_rounding(
        taxi_protocol, db, mockserver, expected_cashback,
):
    update_meta(db, 0.1, None)
    make_request(taxi_protocol, 999)

    proc = db.order_proc.find_one(ORDER_ID)
    current_prices = proc['order'].get('current_prices')
    assert current_prices is not None

    assert current_prices.get('discount_cashback') == expected_cashback
