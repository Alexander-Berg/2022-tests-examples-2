# -*- encoding: utf-8 -*-
import datetime

import pytest

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
ORDER_ID = '8c83b49edb274ce0992f337061047375'
FIXED_PRICE = 900
TAXIMETER_PRICE = 1350
COMPLETE_PRICE = 1800
CANCELLED_PRICE = 199
PAID_SUPPLY_PRICE = 77
CURRENT_PRICES_USER_TOTAL_PRICE = 100500
CURRENT_PRICES_USER_TOTAL_DISPLAY_PRICE = 500100
CURRENT_PRICES_USER_RIDE_PRICE = 499323

CLIENT_MESSAGES = {
    'taxiontheway.cost_breakdown.paid_by_card.name': {'en': 'Paid by card'},
    'taxiontheway.cost_breakdown.paid_by_wallet.name': {
        'en': 'Paid by wallet',
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
        {'format_currency': True, 'id': USER_ID, 'orderid': ORDER_ID},
    )


def setup_collection_item(collection, key, value):
    if value is not None:
        collection.update({'_id': ORDER_ID}, {'$set': {key: value}})


def setup_order_proc_statuses(db, status, taxi_status):
    setup_collection_item(db.order_proc, 'order.status', status)
    setup_collection_item(db.order_proc, 'order.taxi_status', taxi_status)
    setup_collection_item(db.orders, 'status', status)
    setup_collection_item(db.orders, 'taxi_status', taxi_status)


def setup_order_proc_ride_prices(db, fixed_price, cc, cost):
    setup_collection_item(
        db.order_proc, 'order.fixed_price.price', fixed_price,
    )
    setup_collection_item(
        db.order_proc, 'order.fixed_price.driver_price', fixed_price,
    )
    setup_collection_item(db.order_proc, 'order_info.cc', cc)
    setup_collection_item(db.order_proc, 'order_info.driver_cc', cc)
    setup_collection_item(db.order_proc, 'order.cost', cost)


def setup_order_proc_current_prices(
        db, kind, is_cashback, is_charity, is_coupon=False,
):
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_total_price',
        CURRENT_PRICES_USER_TOTAL_PRICE,
    )
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_total_display_price',
        CURRENT_PRICES_USER_TOTAL_DISPLAY_PRICE,
    )
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_ride_display_price',
        CURRENT_PRICES_USER_RIDE_PRICE,
    )
    setup_collection_item(db.order_proc, 'order.current_prices.kind', kind)
    if is_cashback:
        setup_collection_item(
            db.order_proc, 'order.current_prices.cashback_price', 100,
        )

    if is_charity:
        setup_collection_item(
            db.order_proc, 'order.current_prices.charity_price', 777,
        )

    if is_coupon:
        setup_collection_item(
            db.order_proc,
            'order.current_prices.final_cost_meta.'
            'user.use_cost_includes_coupon',
            1,
        )
        setup_collection_item(
            db.order_proc,
            'order.current_prices.final_cost_meta.'
            'driver.use_cost_includes_coupon',
            1,
        )
        setup_collection_item(
            db.order_proc,
            'order.current_prices.final_cost_meta.user.coupon_value',
            100,
        )
        setup_collection_item(
            db.order_proc,
            'order.current_prices.final_cost_meta.driver.coupon_value',
            100,
        )
        setup_collection_item(
            db.order_proc,
            'order.current_prices.final_cost_meta.user.price_before_coupon',
            1666,
        )


def setup_order_proc_pricing_meta(db, is_coupon):
    if is_coupon:
        setup_collection_item(
            db.order_proc,
            'order.pricing_data.user.meta.use_cost_includes_coupon',
            1,
        )
        setup_collection_item(
            db.order_proc,
            'order.pricing_data.user.meta.price_before_coupon',
            1555,
        )


def setup_order_proc_coupon(db):
    setup_collection_item(
        db.order_proc,
        'order.coupon',
        {
            'id': 'sng014',
            'was_used': True,
            'valid': True,
            'valid_an': False,
            'series': 'sng014',
            'value': 100,
        },
    )
    setup_collection_item(
        db.order_proc,
        'order.pricing_data.user.meta.use_cost_includes_coupon',
        1,
    )


def check_response_cost(
        content, old_cost, cost_source, use_ride_display_price,
):
    if cost_source == 'old':
        final_cost = old_cost
        cost = old_cost
    else:
        final_cost = CURRENT_PRICES_USER_TOTAL_DISPLAY_PRICE

        if use_ride_display_price:
            cost = CURRENT_PRICES_USER_RIDE_PRICE
        else:
            cost = CURRENT_PRICES_USER_TOTAL_DISPLAY_PRICE

    assert content['final_cost'] == final_cost
    assert content['final_cost_as_str'] == '{:,}\xa0$SIGN$$CURRENCY$'.format(
        final_cost,
    )
    assert content['final_cost_decimal_value'] == '{}'.format(final_cost)

    if content['status'] == 'complete':
        assert content['cost'] == cost
        assert content['cost_as_str'] == '{:,}\xa0$SIGN$$CURRENCY$'.format(
            cost,
        )
        assert content['cost_decimal_value'] == '{}'.format(cost)


def check_paid_supply_discount(content, discount_expected, is_cashback):
    if discount_expected:
        message_cost = FIXED_PRICE
        if is_cashback:
            message_cost = CURRENT_PRICES_USER_RIDE_PRICE
        message_cost_str = '{:,}'.format(message_cost)
        message = (
            'Поездка будет стоить '
            + message_cost_str
            + '\xa0$SIGN$$CURRENCY$.'
        )
        assert 'paid_supply_discount' in content
        assert content['paid_supply_discount'] == {
            'dialog': {
                'title': 'Поездка будет дешевле',
                'message': message,
                'options': [
                    {
                        'action': 'back_to_driving_screen',
                        'button_title': 'Замечательно',
                    },
                ],
            },
        }
    else:
        assert 'paid_supply_discount' not in content


def check_response_cost_with_coupon(
        content, old_cost, cost_source, use_ride_display_price, coupon,
):
    if cost_source == 'old':
        final_cost = old_cost
        cost = old_cost
    else:
        final_cost = CURRENT_PRICES_USER_TOTAL_DISPLAY_PRICE

        if use_ride_display_price:
            cost = CURRENT_PRICES_USER_RIDE_PRICE
        else:
            cost = CURRENT_PRICES_USER_TOTAL_DISPLAY_PRICE
    cost += coupon

    assert content['final_cost'] == final_cost
    assert content['final_cost_as_str'] == '{:,}\xa0$SIGN$$CURRENCY$'.format(
        final_cost,
    )
    assert content['final_cost_decimal_value'] == '{}'.format(final_cost)

    if content['status'] == 'complete':
        assert content['cost'] == cost
        assert content['cost_as_str'] == '{:,}\xa0$SIGN$$CURRENCY$'.format(
            cost,
        )
        assert content['cost_decimal_value'] == '{}'.format(cost)


pytestmark = [
    pytest.mark.now('2016-12-15T11:30:00+0300'),
    pytest.mark.fixture_now(datetime.timedelta(minutes=9)),
    pytest.mark.parametrize(
        'use_ride_display_price',
        [
            pytest.param(
                True,
                marks=pytest.mark.config(
                    TAXIONTHEWAY_USE_RIDE_DISPLAY_PRICE=True,
                ),
            ),
            False,
        ],
    ),
    pytest.mark.parametrize(
        'cost_source, is_cashback, is_charity',
        [
            pytest.param(
                'old',
                False,
                False,
                marks=[pytest.mark.config(CURRENT_PRICES_WORK_MODE='oldway')],
                id='oldway',
            ),
            pytest.param(
                'old',
                False,
                False,
                marks=[pytest.mark.config(CURRENT_PRICES_WORK_MODE='dryrun')],
                id='dryrun',
            ),
            pytest.param(
                'new',
                False,
                False,
                marks=[pytest.mark.config(CURRENT_PRICES_WORK_MODE='tryout')],
                id='tryout',
            ),
            pytest.param(
                'new',
                False,
                False,
                marks=[pytest.mark.config(CURRENT_PRICES_WORK_MODE='newway')],
                id='newway',
            ),
            pytest.param(
                'new',
                True,
                False,
                marks=[pytest.mark.config(CURRENT_PRICES_WORK_MODE='oldway')],
                id='oldway_but_cashback',
            ),
            pytest.param(
                'new',
                False,
                True,
                marks=[pytest.mark.config(CURRENT_PRICES_WORK_MODE='oldway')],
                id='oldway_but_charity',
            ),
        ],
    ),
]


@pytest.mark.parametrize('taxi_status', ['driving', 'waiting', 'transporting'])
@pytest.mark.filldb(order_proc='fixed_price')
def test_cost_order_assigned_fixed_price(
        taxi_protocol,
        db,
        tracker,
        now,
        taxi_status,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'assigned', taxi_status)
    setup_order_proc_ride_prices(db, FIXED_PRICE, None, None)
    setup_order_proc_current_prices(db, 'fixed', is_cashback, is_charity)

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    check_response_cost(
        content, FIXED_PRICE, cost_source, use_ride_display_price,
    )
    assert content['status'] == taxi_status


@pytest.mark.parametrize(
    'taxi_status,', ['driving', 'waiting', 'transporting'],
)
@pytest.mark.parametrize(
    'unset_paid_supply_price,unset_performer_paid_supply,discount_expected',
    [(False, False, False), (False, True, True), (True, True, False)],
)
@pytest.mark.filldb(order_proc='paid_supply')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_totw_paid_supply_cost_order_assigned_fixed_price(
        taxi_protocol,
        db,
        tracker,
        now,
        taxi_status,
        unset_paid_supply_price,
        unset_performer_paid_supply,
        discount_expected,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'assigned', taxi_status)
    setup_order_proc_ride_prices(db, FIXED_PRICE, None, None)
    setup_order_proc_current_prices(db, 'fixed', is_cashback, is_charity)

    if unset_paid_supply_price:
        # This will mean that paid supply was not offered
        db.order_proc.update(
            {'_id': ORDER_ID},
            {'$unset': {'order.fixed_price.paid_supply_price': 1}},
        )

    if unset_performer_paid_supply:
        # This will mean that paid supply did not actually happen
        db.order_proc.update(
            {'_id': ORDER_ID},
            {'$set': {'order.performer.paid_supply': False}},
        )

    response = make_call(taxi_protocol)

    assert response.status_code == 200

    content = response.json()
    check_paid_supply_discount(content, discount_expected, is_cashback)

    assert content['status'] == taxi_status


@pytest.mark.parametrize('taxi_status', ['driving', 'waiting', 'transporting'])
@pytest.mark.filldb(order_proc='fixed_price')
def test_cost_order_assigned_fixed_price_with_cc(
        taxi_protocol,
        db,
        tracker,
        now,
        taxi_status,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'assigned', taxi_status)
    setup_order_proc_ride_prices(db, FIXED_PRICE, TAXIMETER_PRICE, None)
    setup_order_proc_current_prices(db, 'taximeter', is_cashback, is_charity)

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    check_response_cost(
        content, TAXIMETER_PRICE, cost_source, use_ride_display_price,
    )  # 1350 * 1.1111 by cashback
    assert content['status'] == taxi_status


@pytest.mark.filldb(order_proc='fixed_price')
@pytest.mark.parametrize(
    'exp_cost_breakdown',
    [
        None,
        pytest.param(
            [
                {
                    'display_name': 'Ride',
                    'display_amount': '499,323\u00a0$SIGN$$CURRENCY$',
                },
                {
                    'display_name': 'Helping hand',
                    'display_amount': '777\u00a0$SIGN$$CURRENCY$',
                },
            ],
            marks=pytest.mark.translations(
                client_messages={
                    'persey-payments.taxiontheway.cost_breakdown.charity': {
                        'en': 'Helping hand',
                    },
                },
            ),
        ),
    ],
)
def test_cost_order_complete_fixed_price(
        taxi_protocol,
        db,
        tracker,
        now,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
        exp_cost_breakdown,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'finished', 'complete')
    setup_order_proc_ride_prices(
        db, FIXED_PRICE, TAXIMETER_PRICE, COMPLETE_PRICE,
    )
    setup_order_proc_current_prices(db, 'final_cost', is_cashback, is_charity)

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    check_response_cost(
        content, COMPLETE_PRICE, cost_source, use_ride_display_price,
    )  # 1800 + 200 by cashback
    assert content['status'] == 'complete'

    if not is_charity or not exp_cost_breakdown or not use_ride_display_price:
        assert not content.get('cost_message_details', {}).get(
            'cost_breakdown',
        )
    else:
        assert (
            content['cost_message_details']['cost_breakdown']
            == exp_cost_breakdown
        )


@pytest.mark.filldb(order_proc='fixed_price')
@pytest.mark.parametrize(
    'complete_price, final_cost, with_new_pricing_coupon',
    [(1700, 1700, True), (1800, 1700, False)],
)
def test_cost_with_new_pricing_includes_coupon_cost(
        taxi_protocol,
        db,
        tracker,
        now,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
        with_new_pricing_coupon,
        complete_price,
        final_cost,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'finished', 'complete')
    setup_order_proc_ride_prices(
        db, FIXED_PRICE, TAXIMETER_PRICE, complete_price,
    )
    setup_order_proc_current_prices(
        db, 'final_cost', is_cashback, is_charity, with_new_pricing_coupon,
    )
    setup_order_proc_pricing_meta(db, with_new_pricing_coupon)
    setup_order_proc_coupon(db)

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    check_response_cost_with_coupon(
        content, final_cost, cost_source, use_ride_display_price, 100,
    )
    assert content['status'] == 'complete'

    content['cost_message_details']['cost_breakdown'] == [
        {
            'display_amount': '1,800\xa0$SIGN$$CURRENCY$',
            'display_name': 'Ride',
        },
        {
            'display_amount': '100\xa0$SIGN$$CURRENCY$',
            'display_name': 'Discount',
        },
    ]


@pytest.mark.parametrize(
    'status, taxi_status',
    [
        ('cancelled', 'waiting'),
        ('cancelled', 'transporting'),
        ('finished', 'cancelled'),
    ],
)
@pytest.mark.filldb(order_proc='fixed_price')
def test_cost_order_cancelled_fixed_price(
        taxi_protocol,
        db,
        tracker,
        now,
        status,
        taxi_status,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'finished', 'cancelled')
    setup_order_proc_ride_prices(
        db, FIXED_PRICE, TAXIMETER_PRICE, CANCELLED_PRICE,
    )
    # in cancelled order should be no cashback_cost
    setup_order_proc_current_prices(db, 'final_cost', is_cashback, is_charity)

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    check_response_cost(
        content, CANCELLED_PRICE, cost_source, use_ride_display_price,
    )  # just paid cancel, no cashback
    assert content['status'] == 'cancelled'


@pytest.mark.filldb(order_proc='no_point_b')
def test_cost_order_assigned_no_point_b(
        taxi_protocol,
        db,
        tracker,
        now,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
):
    prepare_tracker(tracker, now)
    # other set in db
    setup_order_proc_current_prices(db, 'prediction', is_cashback, is_charity)
    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    # ride cost is 359 from 179.5 from calc.allowed_tariffs * 2 from surge
    # and ceil from 359 to 360 in OldBuildCost
    check_response_cost(content, 360, cost_source, use_ride_display_price)
    assert content['status'] == 'transporting'


@pytest.mark.filldb(order_proc='fixed_price')
@pytest.mark.experiments3(filename='correct_experiments3.json')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'card_cost,wallet_cost,expected_breakdown',
    [
        (400, 0, []),
        (
            400,
            100,
            [
                {
                    'display_amount': '100\xa0$SIGN$$CURRENCY$',
                    'display_name': 'Paid by wallet',
                },
            ],
        ),
        (
            0,
            100,
            [
                {
                    'display_amount': '0\xa0$SIGN$$CURRENCY$',
                    'display_name': 'Paid by card',
                },
                {
                    'display_amount': '100\xa0$SIGN$$CURRENCY$',
                    'display_name': 'Paid by wallet',
                },
            ],
        ),
    ],
)
def test_payment_methods_cost_breakdown(
        taxi_protocol,
        db,
        tracker,
        now,
        cost_source,
        is_cashback,
        is_charity,
        card_cost,
        wallet_cost,
        expected_breakdown,
        use_ride_display_price,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'finished', 'complete')
    setup_order_proc_ride_prices(
        db, FIXED_PRICE, TAXIMETER_PRICE, COMPLETE_PRICE,
    )
    setup_order_proc_current_prices(db, 'final_cost', False, False)
    setup_collection_item(
        db.order_proc,
        'order.current_prices.cost_breakdown',
        [
            {'type': 'card', 'amount': card_cost},
            {'type': 'personal_wallet', 'amount': wallet_cost},
        ],
    )

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'complete'
    if (
            cost_source == 'new'
            and not is_cashback
            and not is_charity
            and expected_breakdown
    ):
        assert content.get('cost_message_details', {}).get('cost_breakdown')
        cost_breakdown = content['cost_message_details']['cost_breakdown']
        assert cost_breakdown[0]['display_name'] == 'Ride'
        assert cost_breakdown[1:] == expected_breakdown


@pytest.mark.parametrize(
    'experiment_correct',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='correct_experiments3.json',
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='incorrect_experiments3_01.json',
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='incorrect_experiments3_02.json',
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='incorrect_experiments3_03.json',
            ),
        ),
    ],
)
@pytest.mark.filldb(order_proc='fixed_price')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
def test_incorrect_totw_payment_methods_breakdown_experiment(
        taxi_protocol,
        db,
        tracker,
        now,
        cost_source,
        is_cashback,
        is_charity,
        use_ride_display_price,
        experiment_correct,
):
    prepare_tracker(tracker, now)
    setup_order_proc_statuses(db, 'finished', 'complete')
    setup_order_proc_ride_prices(
        db, FIXED_PRICE, TAXIMETER_PRICE, COMPLETE_PRICE,
    )
    setup_order_proc_current_prices(db, 'final_cost', False, False)
    setup_collection_item(
        db.order_proc,
        'order.current_prices.cost_breakdown',
        [
            {'type': 'card', 'amount': 0},
            {'type': 'personal_wallet', 'amount': 100},
        ],
    )

    response = make_call(taxi_protocol)

    assert response.status_code == 200
    content = response.json()
    if cost_source == 'new' and not is_cashback and not is_charity:
        cost_breakdown = content.get('cost_message_details', {}).get(
            'cost_breakdown',
        )
        assert experiment_correct == (cost_breakdown is not None)
