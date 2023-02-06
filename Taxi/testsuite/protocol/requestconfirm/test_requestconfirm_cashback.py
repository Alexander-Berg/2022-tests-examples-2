import pytest

from protocol.ordercommit import order_commit_common
from protocol.requestconfirm.test_requestconfirm import PricingCompleteData


ORDER_ID = '1c83b49edb274ce0992f337061047375'
ALIAS_ID = 'db60d02916ae4a1a91eafa3a1a8ed04d'

CALC_METHOD_FREE_ROUTE = 1
CALC_METHOD_FIXED_PRICE = 2
CALC_METHOD_OTHER = 3
CALC_METHOD_ORDER_COST = 4

FINAL_COST_META = {
    'driver': {
        'unite_total_price_enabled': 1,
        'plus_cashback_rate': 0.1,
        'cashback_calc_coeff': 0,
        'cashback_fixed_price': 100,
        'user_total_price': 1000,
        'waiting_price': 47,
    },
    'user': {
        'unite_total_price_enabled': 1,
        'plus_cashback_rate': 0.1,
        'cashback_calc_coeff': 0,
        'cashback_fixed_price': 100,
        'user_total_price': 1000,
        'waiting_price': 52,
    },
}


def setup_order_proc(
        db,
        is_cashback,
        is_plus_cashback,
        payment_type,
        using_new_pricing,
        paid_supply,
):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'extra_data.cashback.is_cashback': is_cashback,
                'extra_data.cashback.is_plus_cashback': is_plus_cashback,
                'order.request.payment.type': payment_type,
                'payment_tech.type': payment_type,
                'order.using_new_pricing': using_new_pricing,
                'order.performer.paid_supply': paid_supply,
            },
        },
    )


def setup_order_proc_metas(
        db,
        cashback_fixed_price,
        cashback_fixed_price_paid_supply,
        cashback_calc_coeff,
):
    if cashback_fixed_price is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.pricing_data.user.'
                    'meta.'
                    'cashback_fixed_price': cashback_fixed_price,
                },
            },
        )
    if cashback_fixed_price_paid_supply is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.pricing_data.user.'
                    'additional_prices.paid_supply.meta.'
                    'cashback_fixed_price': cashback_fixed_price_paid_supply,
                },
            },
        )
    if cashback_calc_coeff is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.pricing_data.user.'
                    'meta.'
                    'cashback_calc_coeff': cashback_calc_coeff,
                    'order.pricing_data.user.'
                    'additional_prices.paid_supply.meta.'
                    'cashback_calc_coeff': cashback_calc_coeff,
                },
            },
        )


def setup_order_proc_meta(db, name, value, paid_supply_value=None):
    if paid_supply_value is None:
        paid_supply_value = value
    if value is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.pricing_data.user.' 'meta.' + name: value,
                    'order.pricing_data.user.'
                    'additional_prices.paid_supply.meta.' + name: value,
                },
            },
        )


def setup_complements(db, withdraw_amount):
    complements = [
        {
            'type': 'personal_wallet',
            'payment_method_id': 'wallet_id/some_number_value',
        },
    ]
    if withdraw_amount is not None:
        complements[0]['withdraw_amount'] = withdraw_amount
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.request.payment.complements': complements,
                'payment_tech.complements': complements,
            },
        },
    )


def check_cashback_cost(proc, expected_cashback_cost):
    expected_total_price = proc['order']['cost']
    if expected_cashback_cost:
        assert proc['order']['cashback_cost'] == expected_cashback_cost
        expected_total_price += expected_cashback_cost
    else:
        assert 'cashback_cost' not in proc['order']
    order_commit_common.check_current_prices(
        proc,
        'final_cost',
        expected_total_price,
        cashback_price=expected_cashback_cost,
    )


def make_request(
        taxi_protocol,
        calc_method,
        pricing_complete_data=None,
        origin='driver',
        additional_params={},
):
    request_params = {
        'orderid': ALIAS_ID,
        'origin': origin,
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
        'extra': '1000',
        'calc_method': calc_method,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
    }
    if pricing_complete_data:
        request_params.update(pricing_complete_data.to_json())
    request_params.update(additional_params)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    return response.json()


@pytest.mark.parametrize(
    [
        'is_cashback',
        'payment_type',
        'using_new_pricing',
        'cashback_fixed_price',
        'expected_cashback_cost',
    ],
    [
        (False, 'card', True, None, None),
        (True, 'card', False, None, None),
        (True, 'cash', True, 278.8, None),
        (True, 'card', True, 278.8, 278.8),
    ],
    ids=['no_cashback', 'no_new_pricing', 'cash', 'ok'],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_no_cashback_cost_cases(
        taxi_protocol,
        db,
        is_cashback,
        payment_type,
        using_new_pricing,
        cashback_fixed_price,
        expected_cashback_cost,
):
    setup_order_proc(
        db, is_cashback, is_cashback, payment_type, using_new_pricing, False,
    )
    setup_order_proc_metas(db, cashback_fixed_price, None, None)
    make_request(taxi_protocol, CALC_METHOD_FIXED_PRICE)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    check_cashback_cost(proc, expected_cashback_cost)


@pytest.mark.parametrize(
    'cashback_fixed_price,'
    'cashback_fixed_price_paid_supply,'
    'paid_supply,'
    'expected_cashback_cost',
    [
        (None, None, False, None),  # no_metas_no_paid_supply
        (None, None, True, None),  # no_metas_paid_supply
        (None, 376.4, False, None),  # needed_meta_none
        (278.8, None, True, None),  # needed_paid_supply_meta_none
        (278.8, None, False, 278.8),  # ok, paid supply meta not needed
        (278.8, 376.4, False, 278.8),  # ok, choose usual meta
        (278.8, 376.4, True, 376.4),  # ok, choose paid supply meta
    ],
    ids=[
        'no_metas_no_paid_supply',
        'no_metas_paid_supply',
        'needed_meta_none',
        'needed_paid_supply_meta_none',
        'ok',
        'ok2',
        'ok_paid_supply',
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_cashback_cost_initial_fixed_price_fallback(
        taxi_protocol,
        db,
        cashback_fixed_price,
        cashback_fixed_price_paid_supply,
        paid_supply,
        expected_cashback_cost,
):
    setup_order_proc(db, True, True, 'card', True, paid_supply)
    setup_order_proc_metas(
        db, cashback_fixed_price, cashback_fixed_price_paid_supply, None,
    )
    make_request(taxi_protocol, CALC_METHOD_FIXED_PRICE)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    check_cashback_cost(proc, expected_cashback_cost)


@pytest.mark.parametrize('paid_supply', [False, True])
@pytest.mark.parametrize(
    'calc_method',
    [CALC_METHOD_FREE_ROUTE, CALC_METHOD_OTHER, CALC_METHOD_ORDER_COST],
)
@pytest.mark.parametrize(
    'cashback_calc_coeff,expected_cashback_cost',
    [(None, None), (0.1111, 112)],
    ids=['no_meta', 'ok'],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_cashback_cost_calc_fallback(
        taxi_protocol,
        db,
        paid_supply,
        calc_method,
        cashback_calc_coeff,
        expected_cashback_cost,
):
    setup_order_proc(db, True, True, 'card', True, paid_supply)
    setup_order_proc_metas(db, None, None, cashback_calc_coeff)
    make_request(taxi_protocol, calc_method)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    check_cashback_cost(proc, expected_cashback_cost)


@pytest.mark.parametrize(
    'calc_method',
    # If final_cost_meta exists we should use it regardless of the calc method
    [
        CALC_METHOD_FREE_ROUTE,
        CALC_METHOD_FIXED_PRICE,
        CALC_METHOD_ORDER_COST,
        CALC_METHOD_OTHER,
    ],
)
def test_cashback_cost_final_meta(taxi_protocol, db, calc_method):
    setup_order_proc(
        db,
        is_cashback=True,
        is_plus_cashback=True,
        payment_type='card',
        using_new_pricing=True,
        paid_supply=False,
    )
    final_cost_meta = {
        'driver': {
            'cashback_calc_coeff': 0.11111111111111108,
            'cashback_fixed_price': 102,
            'cashback_tariff_multiplier': 0.9,
            'user_total_price': 1016,
            'waiting_price': 47,
        },
        'user': {
            'cashback_calc_coeff': 0.11111111111111108,
            'cashback_fixed_price': 773,
            'cashback_tariff_multiplier': 0.9,
            'user_total_price': 727,
            'waiting_price': 52,
        },
    }

    pricing_complete_data = PricingCompleteData()
    pricing_complete_data.set_final_cost(driver_cost=1000, user_cost=1000)
    pricing_complete_data.set_final_cost_meta(final_cost_meta)
    make_request(taxi_protocol, calc_method, pricing_complete_data)

    proc = db.order_proc.find_one(ORDER_ID)

    check_cashback_cost(proc, 773.0)


@pytest.mark.parametrize('paid_supply', [False, True])
@pytest.mark.parametrize(
    'calc_method',
    [
        CALC_METHOD_FREE_ROUTE,
        CALC_METHOD_FIXED_PRICE,
        CALC_METHOD_OTHER,
        CALC_METHOD_ORDER_COST,
    ],
)
@pytest.mark.parametrize('final_cost_meta_enabled', [False, True])
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_unite_total(
        taxi_protocol, db, paid_supply, calc_method, final_cost_meta_enabled,
):
    setup_order_proc(db, True, True, 'card', True, paid_supply)
    setup_order_proc_metas(db, None, None, 0)
    setup_order_proc_meta(db, 'unite_total_price_enabled', 1)
    setup_order_proc_meta(db, 'plus_cashback_rate', 0.1)
    final_cost_meta = (
        {
            'driver': {
                'unite_total_price_enabled': 1,
                'plus_cashback_rate': 0.1,
                'cashback_calc_coeff': 0,
                'cashback_fixed_price': 100,
                'user_total_price': 1000,
                'waiting_price': 47,
            },
            'user': {
                'unite_total_price_enabled': 1,
                'plus_cashback_rate': 0.1,
                'cashback_calc_coeff': 0,
                'cashback_fixed_price': 100,
                'user_total_price': 1000,
                'waiting_price': 52,
            },
        }
        if final_cost_meta_enabled
        else None
    )
    pricing_complete_data = PricingCompleteData()
    pricing_complete_data.set_final_cost(driver_cost=1000, user_cost=1000)
    pricing_complete_data.set_final_cost_meta(final_cost_meta)
    make_request(taxi_protocol, calc_method, pricing_complete_data)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert proc['order']['cost'] == 900
    assert proc['order']['cashback_cost'] == 100
    order_commit_common.check_current_prices(
        proc, 'final_cost', 1000, cashback_price=100,
    )


@pytest.mark.parametrize(
    'order_set,order_unset,paid_supply,additional_params,'
    'expected_cost,expected_cashback_cost,expected_total_price',
    [
        (
            {},
            {'order_info.cc': '', 'order.fixed_price': ''},
            False,
            {},
            179,
            20,
            199,
        ),
        (
            {'order.fixed_price.price': 2000},
            {'order_info.cc': ''},
            False,
            {},
            1800,
            200,
            2000,
        ),
        (
            {
                'order.fixed_price.price': 2000,
                'order.fixed_price.paid_supply_price': 200,
            },
            {'order_info.cc': ''},
            True,
            {},
            1980,
            220,
            2200,
        ),
        ({'order_info.cc': 3000}, {}, True, {}, 2700, 300, 3000),
        (
            {
                'order.current_prices.current_cost.driver.total': 300,
                'order.current_prices.current_cost.user.total': 300,
            },
            {},
            False,
            {},
            270,
            30,
            300,
        ),
        (
            {
                'order.pricing_data.published.taximeter.cost.driver.total': (
                    300
                ),
                'order.pricing_data.published.taximeter.cost.user.total': 300,
                'order.pricing_data.published.taximeter.meta': FINAL_COST_META,
                'order.pricing_data.published.current_method': 'taximeter',
            },
            {},
            False,
            {
                'dispatch_selected_price': 'taximeter',
                'need_manual_accept': False,
            },
            270,
            30,
            300,
        ),
    ],
    ids=[
        'minimal',
        'fixed_price',
        'fixed_price_with_paid_supply',
        'order_info_cc',
        'order.current_prices',
        'order.pricing_data.published',
    ],
)
@pytest.mark.parametrize('final_cost_meta_enabled', [False, True])  # same
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_disp_cost_unite(
        taxi_protocol,
        db,
        order_set,
        order_unset,
        paid_supply,
        additional_params,
        final_cost_meta_enabled,
        expected_cost,
        expected_cashback_cost,
        expected_total_price,
):
    if order_set:
        db.order_proc.update({'_id': ORDER_ID}, {'$set': order_set})
    if order_unset:
        db.order_proc.update({'_id': ORDER_ID}, {'$unset': order_unset})
    setup_order_proc(db, True, True, 'card', True, paid_supply)
    setup_order_proc_metas(db, None, None, 0)
    setup_order_proc_meta(db, 'unite_total_price_enabled', 1)
    setup_order_proc_meta(db, 'plus_cashback_rate', 0.1)
    final_cost_meta = FINAL_COST_META if final_cost_meta_enabled else None

    pricing_complete_data = PricingCompleteData()
    pricing_complete_data.set_final_cost(driver_cost=1000, user_cost=1000)
    pricing_complete_data.set_final_cost_meta(final_cost_meta)
    data = make_request(
        taxi_protocol,
        CALC_METHOD_OTHER,
        pricing_complete_data,
        'dispatch',
        additional_params,
    )
    assert data == {
        'taximeter_cost': expected_cost,
        'phone_options': [],
        'enable_no_change_flow': False,
        'final_cost': {'driver': expected_cost, 'user': expected_cost},
    }
    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert proc['order']['cost'] == expected_cost
    assert proc['order']['cashback_cost'] == expected_cashback_cost

    disp_cost = proc['order']['disp_cost']
    assert disp_cost is not None
    assert disp_cost['operator_login'] == 'disp_login'
    if 'dispatch_selected_price' in additional_params:
        assert disp_cost['disp_cost'] == expected_total_price
        assert disp_cost['taximeter_cost'] == expected_total_price
        assert disp_cost['use_recommended_cost'] != (
            additional_params.get('need_manual_accept', False)
        )
    else:
        assert disp_cost['disp_cost'] == 1000.0
        assert disp_cost['taximeter_cost'] == expected_cost
        assert disp_cost['use_recommended_cost'] is False

    order_commit_common.check_current_prices(
        proc,
        'final_cost',
        expected_total_price,
        cashback_price=expected_cashback_cost,
    )


@pytest.mark.parametrize(
    'calc_method',
    [
        CALC_METHOD_FREE_ROUTE,
        CALC_METHOD_FIXED_PRICE,
        CALC_METHOD_OTHER,
        CALC_METHOD_ORDER_COST,
    ],
)
@pytest.mark.parametrize(
    'fixed_withdraw,offer_wallet_balance,' 'expected_paid_by_wallet',
    [
        (100, None, 100),  # promo, usual case
        (None, 200, 200),  # composite, usual case
        (100, 200, 100),  # promo+composite, if somehow happen together
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_unite_cashback_for_composite_no_final_meta_check_paid_by_wallet(
        taxi_protocol,
        db,
        calc_method,
        fixed_withdraw,
        offer_wallet_balance,
        expected_paid_by_wallet,
):
    setup_order_proc(db, True, True, 'card', True, False)
    setup_complements(db, fixed_withdraw)
    setup_order_proc_metas(db, None, None, 0)
    setup_order_proc_meta(db, 'unite_total_price_enabled', 1)
    setup_order_proc_meta(db, 'plus_cashback_rate', 0.1)
    setup_order_proc_meta(db, 'wallet_balance', offer_wallet_balance)

    make_request(taxi_protocol, calc_method)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'

    paid_by_card = max(1000 - expected_paid_by_wallet, 0)
    expected_cashback_cost = paid_by_card * 0.1
    expected_cost = 1000 - expected_cashback_cost

    assert proc['order']['cost'] == expected_cost
    if expected_cashback_cost:
        assert proc['order']['cashback_cost'] == expected_cashback_cost
    else:
        assert 'cashback_cost' not in proc['order']
    order_commit_common.check_current_prices(
        proc, 'final_cost', 1000, cashback_price=expected_cashback_cost,
    )


@pytest.mark.parametrize(
    'order_set,order_unset,' 'expected_total_price',
    [
        ({}, {'order_info.cc': '', 'order.fixed_price': ''}, 199),
        ({'order.fixed_price.price': 2000}, {'order_info.cc': ''}, 2000),
        ({'order_info.cc': 3000}, {}, 3000),
    ],
)
@pytest.mark.parametrize(
    'fixed_withdraw,offer_wallet_balance,' 'expected_paid_by_wallet',
    [
        (100, None, 100),  # promo, usual case
        (None, 200, 200),  # composite, usual case
        (100, 200, 100),  # promo+composite, if somehow happen together
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_unite_cashback_for_composite_disp_cost_check_paid_by_wallet(
        taxi_protocol,
        db,
        order_set,
        order_unset,
        expected_total_price,
        fixed_withdraw,
        offer_wallet_balance,
        expected_paid_by_wallet,
):
    if order_set:
        db.order_proc.update({'_id': ORDER_ID}, {'$set': order_set})
    if order_unset:
        db.order_proc.update({'_id': ORDER_ID}, {'$unset': order_unset})
    setup_order_proc(db, True, True, 'card', True, False)
    setup_complements(db, fixed_withdraw)
    setup_order_proc_metas(db, None, None, 0)
    setup_order_proc_meta(db, 'unite_total_price_enabled', 1)
    setup_order_proc_meta(db, 'plus_cashback_rate', 0.1)
    setup_order_proc_meta(db, 'wallet_balance', offer_wallet_balance)

    data = make_request(taxi_protocol, CALC_METHOD_OTHER, origin='dispatch')

    paid_by_card = expected_total_price - expected_paid_by_wallet
    expected_cashback_cost = max(round(paid_by_card * 0.1), 0)
    expected_cost = expected_total_price - expected_cashback_cost
    assert data == {
        'taximeter_cost': expected_cost,
        'phone_options': [],
        'enable_no_change_flow': False,
        'final_cost': {'driver': expected_cost, 'user': expected_cost},
    }
    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert proc['order']['cost'] == expected_cost
    if expected_cashback_cost:
        assert proc['order']['cashback_cost'] == expected_cashback_cost
    else:
        assert 'cashback_cost' not in proc['order']

    disp_cost = proc['order']['disp_cost']
    assert disp_cost is not None
    assert disp_cost['disp_cost'] == 1000.0
    assert disp_cost['taximeter_cost'] == expected_cost
    assert disp_cost['operator_login'] == 'disp_login'
    order_commit_common.check_current_prices(
        proc,
        'final_cost',
        expected_total_price,
        cashback_price=expected_cashback_cost,
    )


@pytest.mark.parametrize(
    'cashback_for_composite, paid_by_wallet, expected_cashback_cost',
    [
        (False, 200, 0),  # no cashback for composite
        (True, 200, 80),  # (1000-200)*0.1 - common case
        (True, 1000, 0),  # 0*0.1 - full payment
        (True, 999, 0),  # extra case, cashback must be 0
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_unite_cashback_for_composite_no_final_meta_check_near_zero(
        taxi_protocol,
        db,
        cashback_for_composite,
        paid_by_wallet,
        expected_cashback_cost,
):
    setup_complements(db, None)
    setup_order_proc_metas(db, None, None, 0)
    setup_order_proc_meta(db, 'wallet_balance', paid_by_wallet)
    if cashback_for_composite:
        setup_order_proc(db, True, True, 'card', True, False)
        setup_order_proc_meta(db, 'unite_total_price_enabled', 1)
        setup_order_proc_meta(db, 'plus_cashback_rate', 0.1)
    else:
        setup_order_proc(db, False, False, 'card', True, False)

    make_request(taxi_protocol, CALC_METHOD_FREE_ROUTE)

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'

    expected_cost = 1000 - expected_cashback_cost

    assert proc['order']['cost'] == expected_cost
    if expected_cashback_cost:
        assert proc['order']['cashback_cost'] == expected_cashback_cost
    else:
        assert 'cashback_cost' not in proc['order']
    order_commit_common.check_current_prices(
        proc, 'final_cost', 1000, cashback_price=expected_cashback_cost,
    )
