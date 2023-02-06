# coding: utf-8
from __future__ import unicode_literals
import collections
import copy
import datetime
import json

import pytest

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.core import arequests
from taxi.core import db
from taxi.internal import dbh
from taxi.internal.order_kit import antifraud
from taxi.internal.order_kit import const
from taxi.internal.order_kit import exceptions
from taxi.internal.order_kit import payment_helpers


Exp3Result = collections.namedtuple('Exp3Result', ['name', 'value'])


def make_active_devault_antifraud_config():
    default_antifraud_config = copy.deepcopy(config.DEFAULT_ANTIFRAUD_CONFIG.get())
    default_antifraud_config['enabled'] = True
    return default_antifraud_config


ACTIVE_DEFAULT_ANTIFRAUD_CONFIG = make_active_devault_antifraud_config()


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('antifraud_finished,performer,expected_result', [
    # antifraud_finished (no matter what performer is) - doesn't need start
    (True, {'clid': 'some_clid'}, False),
    (True, {}, False),
    # antifraud not finished, has performer - need start
    (False, {'clid': 'some_clid'}, True),
    # antifraud not finished, no performer - doesn't need start
    (False, {}, False),
])
def test_need_start(antifraud_finished, performer, expected_result):
    order_doc = {
        'payment_tech': {'antifraud_finished': antifraud_finished},
    }
    proc = dbh.order_proc.Doc({
        'order': {
            'performer': performer
        }
    })
    assert antifraud.need_start(order_doc, proc) == expected_result


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    AFS_PAUSE_BEFORE_START_TO_PARTIAL_DEBIT=True,
    ANTIFRAUD_ENABLE_EXTERNAL_USER_CHECK=True,
    ANTIFRAUD_EXTERNAL_USER_CHECK_CONFIG={
        'user_antifraud': [
            {
                'config': {
                    'hold_fix_price': True,
                    'last_payment_delta': 500,
                    'pause_before_hold': 7200,
                    'pause_before_hold_airport': 7200,
                    'pause_before_hold_fix_price': 7200,
                    'pause_before_hold_no_dest': 0,
                    'payment_deltas': [
                        300,
                    ],
                },
                'status': 'hacked',
            },
        ]
    },
)
@pytest.inline_callbacks
def test_pause_before_start_uafs(patch):
    payment_tech = {
        'type': 'card',
        'prev_type': 'card',
        'last_known_ip': '2a02:6b8:b010:7047::3',
        'last_known_region_id': 225,
        'debt': False,
        'hold_initiated': False,
        'need_cvn': False,
        'main_card_payment_id': 'card-xf70193b212d5ede690dcf8c1',
        'main_card_persistent_id': '',
        'main_card_billing_id': '',
        'main_card_possible_moneyless': False,
        'driver_without_vat_to_pay': {
            'ride': 0,
            'tips': 0,
        },
        'sum_to_pay': {
            'ride': 12700000,
            'tips': 0,
            'toll_road': 0,
        },
        'without_vat_to_pay': {
            'ride': 12700000,
            'tips': 0,
            'toll_road': None,
        },
        'user_to_pay': {
            'ride': 12700000,
            'tips': 0,
            'toll_road': 0,
        },
        'ctt': True,
        'antifraud_group_recalculated': True,
        'antifraud_group': 3,
        'check_card_is_finished': True,
        'antifraud_finished': True,
        'finish_handled': True,
        'history': [],
        'inn_for_receipt': '381805387129',
        'inn_for_receipt_id': 'e7fc0c1b184a4a6bb56f8e0b3c344e8c',
        'nds_for_receipt': 18,
        'antifraud_start_sum': 12700000,
        'just_closed': None,
    }
    proc_order_doc = {
        '_id': 'order_id1',
        'user_phone_id': 'user_phone_id1',
        'user_uid': 'user_uid1',
        'user_id': 'user_id1',
        'uber_id': 'uber_id1',
        'city': 'Moscow',
        'nz': 'mytishchi',
        'created': datetime.datetime.strptime(
            '2022-02-22 22:22:22',
            '%Y-%m-%d %H:%M:%S',
        ),
        'class': 'vip',
        'device_id': 'device_id1',
        'antifraud_group': 1,
        'current_prices': {
            'kind': 'fixed',
            'user_ride_display_price': 510,
            'user_total_display_price': 511,
            'user_total_price': 512,
        },
        'fixed_price': {
            'destination': [
                37.565305946734,
                55.7455375419869
            ],
            'driver_price': 513,
            'max_distance_from_b': 501,
            'price': 514,
            'price_original': 515,
            'show_price_in_taximeter': False,
        },
    }
    order_doc = copy.deepcopy(proc_order_doc)
    order_doc['payment_tech'] = payment_tech

    status_updates = dbh.order_proc.Doc.order_info.statistics.status_updates
    transporting_delay = datetime.timedelta(seconds=100)
    transporting_start_ts = datetime.datetime.utcnow() - transporting_delay

    proc_doc = dbh.order_proc.Doc({
        'order_info': {
            'statistics': {
                'status_updates': [
                    {
                        status_updates.created.key: transporting_start_ts,
                        status_updates.taxi_status.key:
                            dbh.orders.TAXI_STATUS_TRANSPORTING
                    }
                ]
            }
        },
        'payment_tech': payment_tech,
        'order': order_doc,
    })

    zone_config = {'enabled': True, 'personal': []}

    @patch('taxi.internal.order_kit.antifraud._get_zone_config')
    @async.inline_callbacks
    def _get_zone_config(zone_id, *args, **kwargs):
        yield
        assert zone_id == order_doc['nz']
        async.return_value(zone_config)

    @patch('taxi.internal.order_kit.antifraud._is_fixed_price')
    def _is_fixed_price(order_doc):
        return True

    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, personal_config):
        return True

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def mock_post_request(url, timeout=None, *args, **kwargs):
        assert kwargs['json'] == {
            'antifraud_group': 3,
            'city': u'Moscow',
            'class': {},
            'created': '2022-02-22T22:22:22+00:00',
            'currency': 'RUB',
            'current_price': 512,
            'device_id': u'device_id1',
            'fixed_price_original': 515,
            'is_fixed_price': True,
            'nz': u'mytishchi',
            'order_id': u'order_id1',
            'payment_method_id': u'card-xf70193b212d5ede690dcf8c1',
            'payment_type': u'card',
            'uber_id': u'uber_id1',
            'user_id': u'user_id1',
            'user_phone_id': 'user_phone_id1',
            'user_uid': u'user_uid1',
        }
        response = {
            'use_custom_config': True,
            'status': 'hacked',
        }
        yield async.return_value(
            arequests.Response(
                status_code=200,
                content=json.dumps(response),
            )
        )

    pause = yield antifraud.pause_before_start(order_doc, proc_doc, 'hacked')
    assert pause == 7100


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'holded_once,fix_price,fix_pause,airport_pause,personal_pause,expected_pause',
    [
        (True, True, 100, 150, 200, 100),
        (True, False, 100, 150, 200, 150),
        (False, False, 100, 150, 200, 200),
    ]
)
@pytest.inline_callbacks
def test_pause_before_start(patch, holded_once, fix_price, fix_pause,
                            airport_pause, personal_pause, expected_pause):
    ORDER_DOC = {
        'nz': 'some_city_id',
        'user_phone_id': 'some_phone_id',
        'performer': {'tariff': {'class': 'econom'}},
        'payment_tech': {
            'type': 'card',
        },
        'status': 'assigned',
        'taxi_status': 'driving'
    }
    status_updates = dbh.order_proc.Doc.order_info.statistics.status_updates
    transporting_delay = datetime.timedelta(seconds=100)
    transporting_start_ts = datetime.datetime.utcnow() - transporting_delay
    PROC_DOC = dbh.order_proc.Doc({
        'order_info': {
            'statistics': {
                'status_updates': [
                    {
                        status_updates.created.key: transporting_start_ts,
                        status_updates.taxi_status.key:
                            dbh.orders.TAXI_STATUS_TRANSPORTING
                    }
                ]
            }
        },
        'order': {
            'nz': 'some_city_id',
            'user_phone_id': 'some_phone_id',
            'performer': {'tariff': {'class': 'econom'}},
            'payment_tech': {
                'type': 'card',
            },
            'status': 'assigned',
            'taxi_status': 'driving'
        }
    })
    ZONE_CONFIG = {'enabled': True, 'personal': []}
    PERSONAL_CONFIG = {'pause_before_hold': personal_pause,
                       'pause_before_hold_fix_price': fix_pause,
                       'pause_before_hold_airport': airport_pause}
    AF_HOLD_CONFIG = {'hold_fix_price': False}
    GROUP = 1

    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, personal_config):
        assert order_doc == ORDER_DOC
        assert personal_config == PERSONAL_CONFIG
        return holded_once

    @patch('taxi.internal.order_kit.antifraud._is_fixed_price')
    def _is_fixed_price(order_doc):
        assert order_doc == ORDER_DOC
        return fix_price

    @patch('taxi.internal.order_kit.antifraud._get_zone_config')
    @async.inline_callbacks
    def _get_zone_config(zone_id, *args, **kwargs):
        yield
        assert zone_id == ORDER_DOC['nz']
        async.return_value(ZONE_CONFIG)

    @patch('taxi.internal.order_kit.antifraud._get_user_group')
    @async.inline_callbacks
    def _get_user_group(order_doc):
        yield
        assert order_doc == ORDER_DOC
        async.return_value(GROUP)

    @patch('taxi.internal.order_kit.antifraud._get_personal_config')
    @async.inline_callbacks
    def _get_personal_config(
            zone_config, user_group, tariff_class, user_antifraud_status=None, log_extra=None):
        yield
        async.return_value(PERSONAL_CONFIG)

    @patch('taxi.internal.order_kit.antifraud._get_experiment3_af_hold_config')
    @async.inline_callbacks
    def _get_experiment3_af_hold_config(zone_id, phone_id, log_extra=None):
        yield
        async.return_value(AF_HOLD_CONFIG)

    @patch('taxi.internal.order_kit.antifraud._order_without_destination')
    def _order_without_destination(order_doc):
        return False

    pause = yield antifraud.pause_before_start(ORDER_DOC, PROC_DOC, None)
    assert pause == expected_pause - 100

    with pytest.raises(antifraud.InvalidOrderState):
        yield antifraud.pause_before_start(
            ORDER_DOC, dbh.order_proc.Doc({
                'order': ORDER_DOC
            }), None)


@pytest.mark.parametrize(
    'is_fixed_price,order_cost,overdraft_limit,expected', [
        # not fixed price, limit 0 — False
        (False, 300, 0, False),
        # not fixed price, limit is less than cost — False
        (False, 300, 100, False),
        # not fixed price, limit is equals to cost — False
        (False, 300, 300, False),
        # not fixed price, limit is more than cost — False
        (False, 300, 500, False),
        # fixed price, limit 0 — False
        (True, 300, 0, False),
        # fixed price, limit is less than cost — False
        (True, 300, 100, False),
        # fixed price, limit is equals to cost — True
        (True, 300, 300, True),
        # fixed price, limit is more than cost — True
        (True, 300, 500, True),
    ],
)
@pytest.inline_callbacks
def test_check_if_debt_allowed_by_overdraft(
        patch,
        is_fixed_price,
        order_cost,
        overdraft_limit,
        expected,
):
    PROC_DOC = dbh.order_proc.Doc({
        'performer': {'park_id': 'some_park_id', 'candidate_index': 0},
        'candidates': [{'tariff_currency': 'RUB'}],
        'order': {
            'nz': 'moscow',
            'fixed_price': {'price': order_cost} if is_fixed_price else {},
            'user_phone_id': 'some_phone_id',
            'current_prices': {
                'user_total_price': order_cost,
            },
        }
    })

    @patch('taxi.internal.order_kit.antifraud._get_experiment3_af_hold_config')
    @async.inline_callbacks
    def _get_experiment3_af_hold_config(zone_id, phone_id, log_extra=None):
        yield
        async.return_value({'allowed_overdraft_debt': True})

    @patch('taxi.internal.order_kit.antifraud.get_personal_phone_id_by_phone_id')
    @pytest.inline_callbacks
    def _get_personal_phone_id_by_phone_id(phone_id):
        assert phone_id == PROC_DOC.order.phone_id
        yield
        async.return_value('some_personal_phone_id')

    @patch('taxi.external.debts.get_overdraft_limit')
    @pytest.inline_callbacks
    def _get_overdraft_limit(
            phone_id,
            personal_phone_id,
            currency,
            src_service,
            force_request=False,
            log_extra=None,
    ):
        assert phone_id == PROC_DOC.order.phone_id
        assert personal_phone_id == 'some_personal_phone_id'
        assert currency == PROC_DOC.chosen_candidate.tariff_currency
        yield
        async.return_value({'remaining_limit': overdraft_limit})

    result = yield antifraud.check_if_debt_allowed_by_overdraft(PROC_DOC)
    assert result == expected


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_update_ride_sum_disabled(patch):
    ORDER_DOC = {'_id': 'some_id', 'nz': 'some_city_id'}
    ZONE_CONFIG = {'enabled': False}

    proc = dbh.order_proc.Doc({})

    @patch('taxi.internal.order_kit.antifraud._get_zone_config')
    @async.inline_callbacks
    def test_get_zone_id(city_id, *args, **kwargs):
        yield
        assert city_id == ORDER_DOC['nz']
        async.return_value(ZONE_CONFIG)

    updated = yield antifraud.update_ride_sum(ORDER_DOC, proc, 1005001000)
    assert not updated


@pytest.mark.filldb(tariff_settings='enabled', orders='bigger_last_sum')
@pytest.inline_callbacks
def test_update_ride_sum_lte_new_sum(patch):

    @patch('taxi.internal.order_kit.order_helpers.get_cost_with_coupon')
    def _cost_with_coupon(order_doc, new_cost):
        return (new_cost, 0)

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    proc = dbh.order_proc.Doc({})
    last_sum = order_doc['payment_tech']['sum_to_pay']['ride']
    last_cost = payment_helpers.inner2cost(last_sum)
    assert last_cost == 500
    assert not (yield antifraud.update_ride_sum(order_doc, proc, 500))
    assert not (yield antifraud.update_ride_sum(order_doc, proc, 300))


@pytest.mark.filldb(tariff_settings='config', orders='without_transactions')
@pytest.inline_callbacks
def test_update_ride_sum_first_full_payment(patch):
    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, zone_config):
        return True

    @patch('taxi.internal.order_kit.order_helpers.get_cost_with_coupon')
    def _cost_with_coupon(order_doc, new_cost):
        return (new_cost, 0)

    new_cost = 150
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    proc = dbh.order_proc.Doc({})
    updated = yield antifraud.update_ride_sum(order_doc, proc, new_cost)
    assert updated

    new_sum = payment_helpers.cost2inner(new_cost)
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == new_sum


@pytest.mark.parametrize('hold_init', (True, False))
@pytest.mark.filldb(tariff_settings='config', orders='without_transactions')
@pytest.inline_callbacks
def test_set_hold_init(patch, hold_init, mock_fix_change_payment_in_py2_config):
    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, zone_config):
        return True

    @patch('taxi.internal.order_kit.order_helpers.get_cost_with_coupon')
    def _cost_with_coupon(order_doc, new_cost):
        return (new_cost, 0)

    mock_fix_change_payment_in_py2_config(hold_init)

    new_cost = 150
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    proc = dbh.order_proc.Doc({})
    updated = yield antifraud.update_ride_sum(order_doc, proc, new_cost)
    assert updated

    new_sum = payment_helpers.cost2inner(new_cost)
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == new_sum
    if hold_init:
        assert order_doc['payment_tech']['hold_initiated']
    else:
        assert 'hold_initiated' not in order_doc['payment_tech']


@pytest.mark.filldb(tariff_settings='config', orders='without_transactions')
@pytest.inline_callbacks
def test_update_ride_sum_first_full_payment_with_no_finish_holds(patch):
    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, zone_config):
        return True

    @patch('taxi.internal.order_kit.order_helpers.get_cost_with_coupon')
    def _cost_with_coupon(order_doc, new_cost):
        return (new_cost, 0)

    new_cost = 150
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    order_doc['billing_tech']['transactions'] = [
        {'status': const.HOLD_FAIL},
        {'status': const.HOLD_INIT},
        {'status': const.HOLD_PENDING}
    ]
    proc = dbh.order_proc.Doc({})
    updated = yield antifraud.update_ride_sum(order_doc, proc, new_cost)
    assert updated

    new_sum = payment_helpers.cost2inner(new_cost)
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == new_sum


@pytest.mark.filldb(tariff_settings='config', orders='possible_moneyless')
@pytest.inline_callbacks
def test_update_ride_sum_possible_moneyless(patch):
    @patch('taxi.internal.order_kit.antifraud._get_mrt_min')
    def _get_mrt_min(*args, **kwargs):
        return 99

    @patch('taxi.internal.order_kit.antifraud._order_without_destination')
    def _order_without_destination(order_doc):
        return False

    yield config.ANTIFRAUD_POSSIBLE_MONEYLESS_PAYMENT_DELTA.save({
        'rus': 50,
    })
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    proc = dbh.order_proc.Doc({})
    updated = yield antifraud.update_ride_sum(order_doc, proc, 257)
    assert updated

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == 2490000


@pytest.mark.filldb(tariff_settings='enabled', orders='without_transactions')
@pytest.inline_callbacks
def test_update_ride_sum_groups(patch):
    NEXT_COST = 3500
    NEXT_SUM = payment_helpers.cost2inner(NEXT_COST)

    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, zone_config):
        return False

    @patch('taxi.internal.order_kit.antifraud._get_user_group')
    @async.inline_callbacks
    def _get_user_group(order_doc):
        yield
        async.return_value(1)

    @patch('taxi.internal.order_kit.antifraud._get_personal_config')
    @async.inline_callbacks
    def _get_personal_config(
            zone_config, user_group, tariff_class, user_antifraud_status=None, log_extra=None):
        yield
        async.return_value({'last_payment_delta': 1000})

    @patch('taxi.internal.order_kit.antifraud._get_payment_deltas')
    def _get_payment_deltas(order_doc, personal_config,
                            user_group, log_extra=None):
        return [500, 1500]

    @patch('taxi.internal.order_kit.antifraud._calc_delta_to_pay')
    def _calc_delta_to_pay(thresholds, delta, new_sum):
        return NEXT_SUM

    @patch('taxi.internal.order_kit.order_helpers.get_cost_with_coupon')
    def _cost_with_coupon(order_doc, new_cost):
        return (new_cost, 0)

    @patch('taxi.internal.order_kit.antifraud._order_without_destination')
    def _order_without_destination(order_doc_update_user_group):
        return False

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    proc = dbh.order_proc.Doc({})
    updated = yield antifraud.update_ride_sum(order_doc, proc, NEXT_COST + 100)
    assert updated

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == NEXT_SUM


@pytest.mark.filldb(tariff_settings='config', orders='without_destinations')
@pytest.mark.parametrize('min_price,current', [
    (199, 100),
    (99, 200),
])
@pytest.inline_callbacks
def test_update_ride_sum_order_without_dest(patch, min_price, current):
    @patch('taxi.internal.order_kit.antifraud._get_mrt_min')
    def _get_mrt_min(*args, **kwargs):
        return min_price

    @patch('taxi.internal.order_kit.antifraud._is_holded_once')
    def _is_holded_once(order_doc, zone_config):
        return False

    @patch('taxi.internal.order_kit.antifraud._get_personal_config')
    @async.inline_callbacks
    def _get_personal_config(
            zone_config, user_group, tariff_class, user_antifraud_status=None, log_extra=None):
        fallback_config = yield config.FALLBACK_ANTIFRAUD_CONFIG.get()
        async.return_value(fallback_config)

    ANTIFRAUD_DELTA = 500

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    proc = dbh.order_proc.Doc({})
    updated = yield antifraud.update_ride_sum(order_doc, proc, current)
    assert updated

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    cost = payment_helpers.cost2inner(max(min_price, current))
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == cost

    order_doc['billing_tech']['transactions'] = [
        {'status': const.HOLD_SUCCESS}
    ]

    updated = yield antifraud.update_ride_sum(
        order_doc,
        proc,
        payment_helpers.inner2cost(cost) + (ANTIFRAUD_DELTA - 100)
    )
    assert not updated

    updated = yield antifraud.update_ride_sum(
        order_doc,
        proc,
        payment_helpers.inner2cost(cost) + ANTIFRAUD_DELTA
    )
    assert updated
    assert order_doc['payment_tech']['sum_to_pay']['ride'] == (
        payment_helpers.cost2inner(
            payment_helpers.inner2cost(cost) + ANTIFRAUD_DELTA)
    )


@pytest.mark.filldb(tariff_settings='config', orders='without_destinations')
@pytest.mark.parametrize('cashback_price, wallet_payment, expected_ride, expected_cashback', [
    (None, None, 1000000, None),
    (10, None, 900000, 100000),
    (0, None, 1000000, 0),
    (9, 10, 910000, 90000),
    (None, 100, 1000000, None)
])
@pytest.inline_callbacks
def test_antifraud_with_cashback(patch, cashback_price, wallet_payment,
                                 expected_ride, expected_cashback):
    @patch('taxi.internal.order_kit.antifraud._get_mrt_min')
    def _get_mrt_min(*args, **kwargs):
        return 80

    order_doc = yield db.orders.find_one({'_id': 'order_id'})

    user_total_price = 100
    paid_from_card = user_total_price - (wallet_payment or 0)
    order_doc['current_prices'] = {
        'user_total_price': user_total_price
    }
    if cashback_price is not None:
        order_doc['current_prices']['cashback_price'] = cashback_price
    if wallet_payment is not None:
        order_doc['current_prices']['cost_breakdown'] = [
            {'type': 'personal_wallet', 'amount': wallet_payment},
            {'type': 'card', 'amount': paid_from_card}
        ]
    proc = dbh.order_proc.Doc({'order': order_doc})
    updated = yield antifraud.update_ride_sum(
        order_doc,
        proc,
        user_total_price
    )
    assert updated

    sum_to_pay = order_doc['payment_tech']['sum_to_pay']
    assert sum_to_pay['ride'] == expected_ride
    if expected_cashback is not None:
        assert sum_to_pay['cashback'] == expected_cashback
    else:
        assert 'cashback' not in sum_to_pay


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_schedule_user_group_update_recalculated():
    order_doc = {'payment_tech': {
        'antifraud_group_recalculated': True,
        'finish_handled': True,
    }}
    eta = yield antifraud.schedule_user_group_update(order_doc)
    assert eta is None


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_schedule_user_group_update_eta(patch):
    CONFIG = {'some': 'config'}
    ETA = 'ETA'

    @patch('taxi.internal.order_kit.antifraud._get_common_config')
    @async.inline_callbacks
    def _get_common_config():
        yield
        async.return_value(CONFIG)

    @patch('taxi.internal.order_kit.antifraud._get_group_recalc_eta')
    def _get_group_recalc_eta(order_doc, common_config):
        assert common_config == CONFIG
        return ETA

    order_doc = {'payment_tech': {
        'antifraud_group_recalculated': False,
        'finish_handled': True,
    }}
    eta = yield antifraud.schedule_user_group_update(order_doc)
    assert eta == ETA


@pytest.mark.filldb(_fill=False)
def test_calc_next_update_eta():
    eta = antifraud.calc_next_update_eta()
    assert eta == settings.PROGRESSIVE_PAYMENT_INTERVAL


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_update_user_group_recalculated():
    order_doc = {'payment_tech': {
        'antifraud_group_recalculated': True,
        'finish_handled': True,
    }}
    yield antifraud.update_user_group(order_doc)


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_update_user_group_skipped_cash(patch):
    @patch(
        'taxi.internal.order_kit.antifraud._mark_antifraud_group_recalculated'
    )
    @async.inline_callbacks
    def _mark_antifraud_group_recalculated(order_doc):
        yield

    @patch('taxi.internal.order_kit.payment_handler.is_prev_error_technical')
    @async.inline_callbacks
    def is_prev_error_technical(order_doc, log_extra):
        yield
        async.return_value(False)

    order_doc = {'_id': 'some_id', 'payment_tech': {
        'type': const.CASH,
        'prev_type': const.CASH,
        'antifraud_group_recalculated': False,
        'finish_handled': True,
    }}
    yield antifraud.update_user_group(order_doc)
    assert _mark_antifraud_group_recalculated.calls == [{
        'args': (order_doc,), 'kwargs': {},
    }]


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_update_user_group_skipped_technical_error(patch):
    # Group is not updated if previous error was technical

    @patch(
        'taxi.internal.order_kit.antifraud._mark_antifraud_group_recalculated'
    )
    @async.inline_callbacks
    def _mark_antifraud_group_recalculated(order_doc):
        yield

    @patch('taxi.internal.order_kit.payment_handler.is_prev_error_technical')
    @async.inline_callbacks
    def is_prev_error_technical(order_doc, log_extra):
        yield
        async.return_value(True)

    @patch('taxi.internal.order_kit.antifraud._is_ready_to_recalculate_group')
    def _is_ready_to_recalculate_group(order_doc, log_extra=None):
        # Decision that group is not updated is made only when debt was
        # not paid within some time
        return antifraud.RecalcParams(
            ready=True, is_good=False, mark_recalculated=False,
        )

    order_doc = {'_id': 'some_id', 'payment_tech': {
        'sum_to_pay': {'ride': 100500},
        'debt': True,
        'type': const.CARD,
        'prev_type': const.CARD,
        'antifraud_group_recalculated': False,
        'finish_handled': True,
    },
    'status': 'finished', 'taxi_status': 'complete'}
    yield antifraud.update_user_group(order_doc)
    assert _mark_antifraud_group_recalculated.calls == [{
        'args': (order_doc,), 'kwargs': {},
    }]


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('ready,called', [
    (True, True),
    (False, False),
])
@pytest.inline_callbacks
def test_update_user_group(patch, ready, called):
    COMMON_CONFIG = {'some': 'config'}

    @patch('taxi.internal.order_kit.payment_handler.is_prev_error_technical')
    @async.inline_callbacks
    def is_prev_error_technical(order_doc, log_extra):
        yield
        async.return_value(False)

    @patch('taxi.internal.order_kit.antifraud._get_common_config')
    @async.inline_callbacks
    def _get_common_config():
        yield
        async.return_value(COMMON_CONFIG)

    @patch('taxi.internal.order_kit.antifraud._is_ready_to_recalculate_group')
    def _is_ready_to_recalculate_group(order_doc, log_extra=None):
        return antifraud.RecalcParams(
            ready=ready, is_good=False, mark_recalculated=False,
        )

    @patch('taxi.internal.order_kit.antifraud._update_user_group')
    @async.inline_callbacks
    def _update_user_group(order_doc, is_good, log_extra=None):
        yield

    order_doc = {'_id': 'some_id', 'payment_tech': {
        'sum_to_pay': {'ride': 100500},
        'type': const.CARD,
        'prev_type': const.CARD,
        'antifraud_group_recalculated': False,
        'finish_handled': True,
    },
    'status': 'finished', 'taxi_status': 'complete'}
    yield antifraud.update_user_group(order_doc)
    assert bool(_update_user_group.calls) is called


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'is_good,paid_orders,expected_orders,expected_group',
    [
        (True, [], ['4'], antifraud.GROUP_OLDSCHOOL),
        (True, ['1', '2'], ['1', '2', '4'], 1),
        (True, ['1', '2', '3'], ['1', '2', '3', '4'], 1),
        (True, range(1, 20), range(1, 20) + ['4'], 4),
        (True, range(1, 21), range(2, 21) + ['4'], 4),
        (True, ['1', '4'], ['1', '4'], antifraud.GROUP_OLDSCHOOL),
        (False, ['1', '2', '3'], [], antifraud.GROUP_NEWBIE),
    ]
)
@pytest.inline_callbacks
def test_update_user_group_conditions(
        patch, is_good, paid_orders, expected_orders, expected_group):
    @patch('taxi.internal.order_kit.antifraud._get_phone_antifraud')
    @async.inline_callbacks
    def _get_phone_antifraud(phone_id):
        yield
        obj = {
            'version': 1,
            'group': antifraud.GROUP_OLDSCHOOL,
            'paid_orders': paid_orders[:],
        }
        async.return_value(obj)

    @patch('taxi.internal.order_kit.antifraud._save_phone_antifraud')
    @async.inline_callbacks
    def _save_phone_antifraud(order_doc, antifraud_object):
        yield

    @patch('taxi.internal.city_kit.country_manager.get_doc_by_city_id')
    @async.inline_callbacks
    def get_doc_by_city_id(city_id, log_extra=None):
        yield
        async.return_value({})

    @patch(
        'taxi.internal.order_kit.antifraud._mark_antifraud_group_recalculated'
    )
    @async.inline_callbacks
    def _mark_antifraud_group_recalculated(order_doc):
        yield

    order_doc = {'_id': '4', 'user_phone_id': 'phone_id', 'city': 'msk'}
    yield antifraud._update_user_group(order_doc, is_good)

    calls = list(_save_phone_antifraud.calls)
    assert len(calls) == 1
    calls = calls[0]
    assert calls['args'][0] == order_doc
    expected_obj = calls['args'][1]
    assert expected_obj['version'] == 1
    assert expected_obj['paid_orders'] == expected_orders
    assert expected_obj['group'] == expected_group


@pytest.mark.filldb(user_phones='save_group')
@pytest.mark.parametrize('phone_id', [
    'with_antifraud',
    'without_antifraud',
])
@pytest.inline_callbacks
def test_save_phone_antifraud(phone_id):
    order_doc = {'user_phone_id': phone_id}
    antifraud_object = {'version': 1, 'group': 2, 'paid_orders': ['1', '2']}
    yield antifraud._save_phone_antifraud(order_doc, antifraud_object)
    assert antifraud_object['version'] == 2

    phone_doc = yield db.user_phones.find_one({'_id': phone_id})
    assert phone_doc['antifraud'] == antifraud_object
    assert phone_doc['updated'] == datetime.datetime.utcnow()


@pytest.mark.filldb(user_phones='save_group')
@pytest.inline_callbacks
def test_save_phone_antifraud_race():
    order_doc = {'user_phone_id': 'with_antifraud'}
    antifraud_object = {'version': 2, 'group': 2, 'paid_orders': ['1', '2']}
    with pytest.raises(exceptions.RaceConditionError):
        yield antifraud._save_phone_antifraud(order_doc, antifraud_object)


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('deltas,last_delta,sum_delta_from_park,sum_to_pay', [
    ([199, 500, 1000, 1500], 1000, 50, 0),
    ([199, 500, 1000, 1500], 1000, 199, 199),
    ([199, 500, 1000, 1500], 1000, 450, 199),
    ([199, 500, 1000, 1500], 1000, 920, 699),
    ([199, 500, 1000, 1500], 1000, 1800, 1699),
    ([199, 500, 1000, 1500], 1000, 3300, 3199),
    ([199, 500, 1000, 1500], 1000, 4500, 4199),
    ([199, 500, 1000, 1500], 1000, 5000, 4199),
    ([199, 250, 420], 70, 100, 0),
])
def test_sum_to_pay(deltas, last_delta, sum_delta_from_park, sum_to_pay):
    real_delta_to_pay = antifraud._calc_delta_to_pay(
        deltas, last_delta, sum_delta_from_park
    )
    assert real_delta_to_pay == sum_to_pay


@pytest.mark.filldb(orders='group_not_calculated')
@pytest.inline_callbacks
def test_mark_antifraud_group_recalculated():
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    yield antifraud._mark_antifraud_group_recalculated(order_doc)
    assert order_doc['payment_tech']['antifraud_group_recalculated']
    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    assert order_doc['payment_tech']['antifraud_group_recalculated']


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(ANTIFRAUD_ENABLE_GROUP_RECALC_EXP=True)
@pytest.mark.parametrize(['exp_enabled', 'exp_value', 'expected_result'], [
    # exp is disabled, skip is disabled — standard recalc flow
    (False, False, (True, False, False)),
    # skip is enabled, but exp is disabled — standard recalc flow
    (False, True, (True, False, False)),
    # exp is enabled, but skip is disabled — standard recalc flow
    (True, False, (True, False, False)),
    # exp is enabled, skip is enabled — do not recal the group
    (True, True, (True, True, True)),
])
@pytest.inline_callbacks
def test_is_ready_to_recalculate_group_by_exp(
        exp_enabled, exp_value, expected_result, patch,
):
    @patch(
        'taxi.internal.order_kit.antifraud._get_antifraud_experiments3'
    )
    @async.inline_callbacks
    def _get_antifraud_experiments3(*args, **kwargs):
        yield
        value = {
            'enabled': exp_enabled,
            'skip_group_recalc': exp_value,
        }
        exp = Exp3Result(
            name=antifraud.ANTIFRAUD_RECALC_EXP3_CONFIG,
            value=value,
        )
        async.return_value([exp])

    @patch('taxi.internal.order_kit.antifraud._get_group_recalc_eta')
    def _get_group_recalc_eta(order_doc, common_config):
        now = datetime.datetime.utcnow()
        eta = now + datetime.timedelta(hours=-1)
        return eta

    order_doc = {
        'nz': 'moscow',
        'payment_tech': {'debt': True},
        'status': 'finished',
        'taxi_status': 'complete',
        'status_updated': datetime.datetime.utcnow(),
    }
    params = yield antifraud._is_ready_to_recalculate_group(order_doc)
    assert params == antifraud.RecalcParams(*expected_result)


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_is_ready_to_recalculate_group_no_debt():

    order_doc = {
        'nz': 'moscow',
        'payment_tech': {'debt': False},
        'status': 'finished',
        'taxi_status': 'complete',
    }
    params = yield antifraud._is_ready_to_recalculate_group(order_doc)
    assert params.ready
    assert params.is_good


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('now_plus,too_early', [
    (-1, False),
    (1, True),
])
@pytest.inline_callbacks
def test_is_ready_to_recalculate_group_debt(patch, now_plus, too_early):
    @patch('taxi.internal.order_kit.antifraud._get_group_recalc_eta')
    def _get_group_recalc_eta(order_doc, common_config):
        now = datetime.datetime.utcnow()
        eta = now + datetime.timedelta(seconds=now_plus)
        return eta

    order_doc = {'payment_tech': {'debt': True}, 'status': 'finished',
                 'taxi_status': 'complete', 'nz': 'moscow'}
    params = yield antifraud._is_ready_to_recalculate_group(order_doc)
    assert params.ready is not too_early
    assert not params.is_good


@pytest.mark.filldb(_fill=False)
def test_get_group_recalc_eta():
    TIMEOUT = 30

    now = datetime.datetime.utcnow()
    order_doc = {'status_updated': now}
    common_config = {'debt_timeout': TIMEOUT}

    eta = antifraud._get_group_recalc_eta(order_doc, common_config)
    assert (eta - now).seconds == TIMEOUT


@pytest.mark.filldb(static='common_config')
@pytest.inline_callbacks
def test_get_common_config_from_db():
    doc = yield db.static.find_one({'_id': 'antifraud_config'})
    config = yield antifraud._get_common_config()
    assert config == doc['config']


@pytest.inline_callbacks
def test_get_common_config_from_settings():
    config = yield antifraud._get_common_config()
    assert config == settings.ANTIFRAUD_COMMON


@pytest.mark.filldb(tariff_settings='config')
@pytest.inline_callbacks
def test_get_zone_config():
    # Zone where antifraud_config is set
    moscow_doc = yield db.tariff_settings.find_one({'hz': 'moscow'})
    moscow_config = yield antifraud._get_zone_config('moscow', 'phone_id')
    assert moscow_config == moscow_doc['antifraud_config']

    # Zone without antifraud_config
    any_zone_config = yield antifraud._get_zone_config('spb', 'phone_id')
    assert any_zone_config == (yield config.DEFAULT_ANTIFRAUD_CONFIG.get())


def check_personal_config(personal_config):
    assert 'payment_deltas' in personal_config
    assert 'last_payment_delta' in personal_config
    assert 'pause_before_hold' in personal_config
    assert 'pause_before_hold_fix_price' in personal_config
    assert 'pause_before_hold_airport' in personal_config
    assert 'hold_fix_price' in personal_config


@pytest.mark.filldb(tariff_settings='config')
@pytest.inline_callbacks
def test_get_tariff_config():
    zone_config = yield antifraud._get_zone_config('moscow', 'phone_id')
    default_config = ACTIVE_DEFAULT_ANTIFRAUD_CONFIG
    check_personal_config(antifraud._get_tariff_config(zone_config, 1, 'econom'))
    assert antifraud._get_tariff_config(zone_config, 1, 'vip') is None
    check_personal_config(antifraud._get_tariff_config(default_config, 1, 'vip'))


@pytest.mark.config(ANTIFRAUD_ENABLE_DEFAULT_CONFIG_AS_OVERRIDE=True)
@pytest.mark.config(DEFAULT_ANTIFRAUD_CONFIG=ACTIVE_DEFAULT_ANTIFRAUD_CONFIG)
@pytest.mark.filldb(tariff_settings='config')
@pytest.inline_callbacks
def test_get_personal_config():
    # Personal config depends on user group and tariff class. It can be
    # returned only for city where antifraud is enabled (for those ones
    # where antifraud_config is present in document).
    zone_config = yield antifraud._get_zone_config('moscow', 'phone_id')
    personal_config = yield antifraud._get_personal_config(
        zone_config, 1, 'econom')
    check_personal_config(personal_config)

    # For cities without antifraud_config or with wrongly filled data
    # return default zone config first.
    default_antifraud_config = yield config.DEFAULT_ANTIFRAUD_CONFIG.get()
    immediate_default_config = antifraud._get_tariff_config(default_antifraud_config, 3, 'express')
    default_config = yield antifraud._get_personal_config(
        zone_config, 3, 'express')
    check_personal_config(default_config)
    assert default_config == immediate_default_config

    # For cities without antifraud_config or with wrongly filled data
    # return fallback config.
    fallback_config = yield antifraud._get_personal_config(
        zone_config, 5, 'any')
    check_personal_config(fallback_config)


@pytest.mark.config(ANTIFRAUD_ENABLE_DEFAULT_CONFIG_AS_OVERRIDE=False)
@pytest.mark.filldb(tariff_settings='config')
@pytest.inline_callbacks
def test_get_personal_config_wo_default_config():
    # Personal config depends on user group and tariff class. It can be
    # returned only for city where antifraud is enabled (for those ones
    # where antifraud_config is present in document).
    zone_config = yield antifraud._get_zone_config('moscow', 'phone_id')
    default_antifraud_config = yield config.DEFAULT_ANTIFRAUD_CONFIG.get()
    fallback_config = yield antifraud._get_personal_config(
        zone_config, 5, 'any')

    immediate_default_config = antifraud._get_tariff_config(default_antifraud_config, 3, 'express')
    personal_config = yield antifraud._get_personal_config(
        zone_config, 3, 'express')
    check_personal_config(personal_config)
    assert personal_config == fallback_config
    assert personal_config != immediate_default_config


@pytest.mark.config(ANTIFRAUD_ENABLE_DEFAULT_CONFIG_AS_OVERRIDE=False)
@pytest.mark.filldb(tariff_settings='config')
@pytest.inline_callbacks
def test_get_personal_config_with_external_user_antifraud():
    zone_config = yield antifraud._get_zone_config('moscow', 'phone_id')
    personal_config = yield antifraud._get_personal_config(
        zone_config, 3, 'express')
    hacked_config = yield antifraud._get_personal_config(
        zone_config, 3, 'express', 'hacked')
    check_personal_config(personal_config)
    check_personal_config(hacked_config)
    assert hacked_config != personal_config


@pytest.mark.filldb(orders='fixed_price')
@pytest.mark.parametrize('airport_order,is_fixed_price,expected', [
    (False, False, False),
    (False, True, True),
    (True, False, True),
    (True, True, True),
])
@pytest.inline_callbacks
def test_is_holded_once(patch, airport_order, is_fixed_price, expected):
    @patch('taxi.internal.order_kit.order_helpers.is_airport_order')
    def is_airport_order(order_doc):
        return airport_order

    order_doc = yield db.orders.find_one({'_id': 'order_id'})
    personal_config = {'hold_fix_price': is_fixed_price}

    assert antifraud._is_holded_once(order_doc, personal_config) == expected


@pytest.mark.filldb(user_phones='group')
@pytest.mark.parametrize('phone_id,expected_group', [
    ('known_loyal', 1),
    ('known_newbee', antifraud.GROUP_NEWBIE),
    ('known_oldschool', antifraud.GROUP_OLDSCHOOL),
    ('without_antifraud_field', antifraud.GROUP_NEWBIE),
])
@pytest.inline_callbacks
def test_get_current_group(phone_id, expected_group):
    group = yield antifraud._get_current_group(phone_id)
    assert group == expected_group


@pytest.mark.filldb(orders='with_payment_tech')
@pytest.mark.parametrize(
    'order_id,expected_status,expected_decision_id',
    [
        ('antifraud_finished', antifraud.ANTIFRAUD_STATUS_FINISHED, None),
        ('antifraud_disabled', antifraud.ANTIFRAUD_STATUS_DISABLED, None),
        (
            'antifraud_overdraft_debt',
            antifraud.ANTIFRAUD_STATUS_OVERDRAFT_DEBT_ALLOWED,
            None,
        ),
        (
            'fail_transaction_allowed_debt',
            antifraud.ANTIFRAUD_STATUS_PAYMENT_FAIL_DEBT_ALLOWED,
            'fail_transaction_allowed_debt_fail_id',
        ),
        (
            'fail_transaction_tech_error',
            antifraud.ANTIFRAUD_STATUS_BILLING_ERROR,
            'fail_transaction_tech_error_fail_id',
        ),
        (
            'fail_transaction',
            antifraud.ANTIFRAUD_STATUS_PAYMENT_FAIL,
            'fail_transaction_fail_id',
        ),
        (
            'fail_transaction_new_search',
            antifraud.ANTIFRAUD_STATUS_PAYMENT_FAIL,
            'fail_transaction_new_search_fail_id',
        ),
        ('need_accept', antifraud.ANTIFRAUD_STATUS_MOVED_TO_ACCEPT, None),
        ('antifraud_working', antifraud.ANTIFRAUD_STATUS_WORKING, None),
        (
            'antifraud_working_new_search',
            antifraud.ANTIFRAUD_STATUS_WORKING,
            None,
        ),
    ]
)
@pytest.inline_callbacks
def test_get_status_and_decision(
        mock_fix_change_payment_in_py2_config,
        order_id,
        expected_status,
        expected_decision_id,
):
    new_search_cases_order = [
        'fail_transaction_new_search',
        'antifraud_working_new_search',
    ]
    mock_fix_change_payment_in_py2_config(
        is_enabled=(order_id in new_search_cases_order),
    )

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    payment_fail = yield antifraud.PaymentFail.from_last_transaction(
        order_doc, None,
    )
    status, decision_id = yield antifraud.get_status_and_decision(
        order_doc, payment_fail, None,
    )

    assert status == expected_status
    assert decision_id == expected_decision_id


@pytest.mark.filldb(orders='with_payment_tech')
@pytest.mark.config(ANTIFRAUD_ALLOWED_PAYMENT_TYPES_MOVED_TO_CASH=['yandex_card'])
@pytest.inline_callbacks
def test_payment_fail_yandex_card():
    order_doc = yield dbh.orders.Doc.find_one_by_id('yandex_card_fail_transaction')
    payment_fail = yield antifraud.PaymentFail.from_last_transaction(
        order_doc, None,
    )
    status, decision_id = yield antifraud.get_status_and_decision(
        order_doc, payment_fail, None,
    )

    assert status == antifraud.ANTIFRAUD_STATUS_PAYMENT_FAIL
    assert decision_id == 'yandex_card_fail_transaction_fail_id'
