# -*- encoding: utf-8 -*-
import datetime

import pytest

from protocol.ordercommit import order_commit_common

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
ORDER_ID = '8c83b49edb274ce0992f337061047375'

DECOUPLING = {
    'driver_price_info': {
        'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
        'fixed_price': 317.0,
        'paid_cancel_in_driving': {
            'price': 78.0,
            'free_cancel_timeout': 300,
            'for_paid_supply': True,
        },
        'paid_supply_price': 77.0,
        'sp': 1.0,
        'sp_alpha': 1.0,
        'sp_beta': 0.0,
        'sp_surcharge': 0.0,
        'tariff_id': '585a6f47201dd1b2017a0eab',
    },
    'success': True,
    'user_price_info': {
        'category_id': '5f40b7f324414f51a1f9549c65211ea5',
        'fixed_price': 633.0,
        'paid_cancel_in_driving': {
            'price': 78.0,
            'free_cancel_timeout': 300,
            'for_paid_supply': True,
        },
        'paid_supply_price': 77.0,
        'sp': 1.0,
        'sp_alpha': 1.0,
        'sp_beta': 0.0,
        'sp_surcharge': 0.0,
        'tariff_id': (
            '585a6f47201dd1b2017a0eab-'
            '507000939f17427e951df9791573ac7e-'
            '7fc5b2d1115d4341b7be206875c40e11'
        ),
    },
}


def prepare_tracker(tracker, now):
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )


def make_call(taxi_protocol):
    return taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'format_currency': True,
            'id': USER_ID,
            'orderid': ORDER_ID,
        },
    )


def check_decoupling(
        db,
        user_cost,
        driver_cost,
        user_cost_is_unusual,
        driver_cost_is_unusual,
):
    proc = db.order_proc.find_one(ORDER_ID)

    decoupling = proc['order']['decoupling']
    assert decoupling['driver_price_info']['cost'] == driver_cost
    if user_cost > 0.0:
        assert proc['order']['cost'] == user_cost
        assert decoupling['user_price_info']['cost'] == user_cost
    else:
        assert proc['order']['cost'] is None
        assert 'cost' not in decoupling['user_price_info']

    if user_cost_is_unusual:
        assert decoupling['user_price_info']['cost_is_unusual'] is True
    else:
        assert 'cost_is_unusual' not in decoupling['user_price_info']
    if driver_cost_is_unusual:
        assert decoupling['driver_price_info']['cost_is_unusual'] is True
    else:
        assert 'cost_is_unusual' not in decoupling['driver_price_info']

    order_commit_common.check_current_prices(proc, 'final_cost', user_cost)


def make_checks(
        db,
        response,
        user_cost,
        driver_cost,
        user_calc_fallback,
        driver_cost_is_unusual,
        user_cost_nullified,
):
    assert response.status_code == 200
    content = response.json()

    if user_calc_fallback and not user_cost_nullified:
        user_cost = driver_cost  # service fail, user pays by basic tariff
    assert content['status'] == 'cancelled'
    if not user_cost_nullified:
        assert content['cost'] == user_cost
        assert content['final_cost'] == user_cost

    check_decoupling(
        db, user_cost, driver_cost, user_calc_fallback, driver_cost_is_unusual,
    )


def nullify_user_paid_supply_cost(db):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.decoupling.user_price_info.paid_supply_price': 0.0,
                (
                    'order.decoupling.user_price_info.'
                    'paid_cancel_in_driving.price'
                ): 0.0,
                'order.fixed_price.paid_supply_price': 0.0,
                'order.paid_cancel_in_driving.price': 0.0,
                'order.paid_cancel_in_driving.free_cancel_timeout': 300,
                'order.paid_cancel_in_driving.for_paid_supply': True,
            },
        },
    )


def make_checks_final_cost_of_canceled_order(db, user_cost, driver_cost):
    proc = db.order_proc.find_one(ORDER_ID)

    current_prices = proc['order']['current_prices']
    assert current_prices['kind'] == 'final_cost'
    assert current_prices['final_cost'] == {
        'driver': {'total': driver_cost},
        'user': {'total': user_cost},
    }
    assert current_prices['final_cost_meta'] == {
        'driver': {
            'driver_meta': driver_cost,
            'paid_cancel_in_waiting_price': driver_cost,
        },
        'user': {
            'user_meta': user_cost,
            'paid_cancel_in_waiting_price': user_cost,
        },
    }


@pytest.mark.translations(
    tariff={'name.econom': {'ru': 'Эконом', 'en': 'Economy'}},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_tow_cancel_minimal_decoupling(
        taxi_protocol, mockserver, recalc_order, db, tracker, now,
):
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.decoupling': DECOUPLING}},
    )

    prepare_tracker(tracker, now)

    user_cost = 198  # minimal from corp tariff
    driver_cost = 99  # minimal from base tariff
    recalc_order.set_driver_recalc_result(
        driver_cost, driver_cost, {'driver_meta': driver_cost},
    )
    recalc_order.set_user_recalc_result(
        user_cost, user_cost, {'user_meta': user_cost},
    )

    response = make_call(taxi_protocol)
    make_checks(db, response, user_cost, driver_cost, False, False, False)
    make_checks_final_cost_of_canceled_order(db, user_cost, driver_cost)


@pytest.mark.translations(
    tariff={'name.econom': {'ru': 'Эконом', 'en': 'Economy'}},
)
@pytest.mark.parametrize(
    'driver_add_minimal, driver_paid_cancel_fix, driver_cost',
    [
        # minimal = 99, ride_price = 21.3 rounded to 22
        (False, 200, 222),  # paid_cancel_fix + ride_price
        (True, 0, 121),  # minimal + ride_price
    ],
)
@pytest.mark.parametrize(
    'user_add_minimal, user_paid_cancel_fix, user_cost',
    [
        # minimal = 99, ride_price = 42.6 rounded to 43
        (False, 400, 443),  # paid_cancel_fix + ride_price
        (True, 0, 241),  # minimal + ride_price
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=9))
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_tow_cancel_paid_decoupling(
        taxi_protocol,
        mockserver,
        recalc_order,
        tracker,
        load_json,
        now,
        db,
        driver_add_minimal,
        driver_paid_cancel_fix,
        driver_cost,
        user_add_minimal,
        user_paid_cancel_fix,
        user_cost,
):
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.decoupling': DECOUPLING}},
    )

    db.tariffs.update(
        {
            'categories': {
                '$elemMatch': {
                    'category_type': 'application',
                    'id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                },
            },
        },
        {
            '$set': {
                'categories.$.add_minimal_to_paid_cancel': driver_add_minimal,
                'categories.$.paid_cancel_fix': driver_paid_cancel_fix,
            },
        },
    )
    taxi_protocol.tests_control(now, invalidate_caches=True)

    prepare_tracker(tracker, now)

    recalc_order.set_driver_recalc_result(driver_cost, driver_cost)
    recalc_order.set_user_recalc_result(user_cost, user_cost)

    response = make_call(taxi_protocol)

    make_checks(db, response, user_cost, driver_cost, False, False, False)


@pytest.mark.translations(
    tariff={'name.econom': {'ru': 'Эконом', 'en': 'Economy'}},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='paid_supply', order_proc='paid_supply_paid_cancel')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.parametrize(
    'switch_to_waiting,user_cost_nullified,'
    'expected_key,expected_user_cost,expected_driver_cost',
    [
        (False, False, 'paid.paidsupply.driving', 78, 78),
        (True, False, 'paid.paidsupply.waiting', 77 + 198, 77 + 99),
        # user cost nullified
        (False, True, 'paid.paidsupply.driving', 0, 78),
        (True, True, 'paid.paidsupply.waiting', 0 + 198, 77 + 99),
    ],
)
def test_tow_paid_supply_paid_cancel(
        taxi_protocol,
        recalc_order,
        tracker,
        now,
        db,
        mockserver,
        load_json,
        switch_to_waiting,
        user_cost_nullified,
        expected_key,
        expected_user_cost,
        expected_driver_cost,
):
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.decoupling': DECOUPLING}},
    )
    if user_cost_nullified:
        nullify_user_paid_supply_cost(db)
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    (
                        'order.pricing_data.user.additional_prices.'
                        'paid_supply.meta.'
                        'paid_supply_paid_cancel_in_driving_price'
                    ): 0.0,
                },
            },
        )

    @mockserver.json_handler('/corp_integration_api/tariffs')
    def mock_tariffs(request):
        return load_json('tariffs_response.json')

    if switch_to_waiting:
        db.order_proc.update(
            {'_id': ORDER_ID}, {'$set': {'order.taxi_status': 'waiting'}},
        )
        db.orders.update(
            {'_id': ORDER_ID}, {'$set': {'taxi_status': 'waiting'}},
        )
        recalc_order.set_driver_recalc_result(
            expected_driver_cost, expected_driver_cost,
        )
        recalc_order.set_user_recalc_result(
            expected_user_cost, expected_user_cost,
        )

    prepare_tracker(tracker, now)

    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid',
            'format_currency': True,
            'id': USER_ID,
            'orderid': ORDER_ID,
        },
    )
    assert response.status_code == 200
    content = response.json()

    if expected_user_cost > 0.0:
        assert 'cost' in content
        assert 'final_cost' in content
        assert content['cost'] == expected_user_cost
        assert content['final_cost'] == expected_user_cost
    else:
        assert 'cost' not in content
        assert 'final_cost' not in content

    assert 'cost_message' in content
    assert (
        content['cost_message']
        == 'Paid supply with paid cancel in '
        + ('waiting' if switch_to_waiting else 'driving')
        + ' OK'
    )
    check_decoupling(
        db, expected_user_cost, expected_driver_cost, False, False,
    )


@pytest.mark.translations(
    tariff={'name.econom': {'ru': 'Эконом', 'en': 'Economy'}},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='paid_cancel_in_driving', order_proc='paid_cancel_in_driving',
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.config(ROUTER_42GROUP_ENABLED=False)
@pytest.mark.parametrize(
    'order_proc_setup, paid_cancel_expected',
    [
        ({}, False),
        (
            {
                'order.paid_cancel_in_driving': {
                    'price': 75,
                    'free_cancel_timeout': 300,
                    'for_paid_supply': True,
                },
                'order.user_tags': [],
            },
            True,
        ),
        (
            {
                'order.paid_cancel_in_driving': {
                    'price': 75,
                    'free_cancel_timeout': 300,
                    'for_paid_supply': True,
                },
                'order.user_tags': [],
            },
            True,
        ),
    ],
)
@pytest.mark.parametrize('user_cost_nullified', [False, True])
def test_tow_paid_cancel_in_driving_decoupling(
        taxi_protocol,
        recalc_order,
        tracker,
        now,
        db,
        order_proc_setup,
        paid_cancel_expected,
        user_cost_nullified,
):
    if order_proc_setup != {}:
        db.order_proc.update({'_id': ORDER_ID}, {'$set': order_proc_setup})

    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.decoupling': DECOUPLING}},
    )

    user_cost = driver_cost = 78

    if user_cost_nullified:
        user_cost = 0
        nullify_user_paid_supply_cost(db)
    if not paid_cancel_expected:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {'$unset': {'order.paid_cancel_in_driving': ''}},
        )
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                (
                    'order.pricing_data.user.meta.'
                    'paid_cancel_in_driving_price'
                ): user_cost,
                (
                    'order.pricing_data.driver.meta.'
                    'paid_cancel_in_driving_price'
                ): driver_cost,
            },
        },
    )

    prepare_tracker(tracker, now)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid' if paid_cancel_expected else 'free',
            'format_currency': True,
            'id': USER_ID,
            'orderid': ORDER_ID,
        },
    )
    assert response.status_code == 200
