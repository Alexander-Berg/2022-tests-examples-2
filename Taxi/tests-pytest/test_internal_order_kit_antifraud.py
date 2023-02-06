# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict

import datetime

import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import experiments3
from taxi.internal import card_operations
from taxi.internal import dbh
from taxi.internal.order_kit import antifraud


DEFAULT_CONFIG = object()


@pytest.mark.config(DEFAULT_ANTIFRAUD_CONFIG=DEFAULT_CONFIG)
@pytest.mark.filldb(tariff_settings='config')
@pytest.mark.parametrize('zone_id, default_expected', [
    (0, True),
    (1, True),
    (2, False),
])
@pytest.mark.parametrize('experiment_enabled', [
    True, False
])
@pytest.inline_callbacks
def test_get_zone_config(patch, zone_id, experiment_enabled, default_expected):
    # Test that `_get_zone_config()` takes:
    #   * experiments3 antifraud_config value if it exists
    #   * `antifraud_config` field of city document when it exists
    #   * `DEFAULT_ANTIFRAUD_CONFIG` when city document doesn't have
    #     `antifraud_config` field (or when city document is `None`)

    experiment_config = {
        'enabled': True,
        "personal": [
            {
                "config": {},
                "group_id": 1,
                "tariff_class": "experiment_class"
            },
        ]
    }

    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(consumer, args, **kwargs):
        yield
        assert consumer == 'backend/antifraud'
        assert len(args) == 2
        assert args[0].name == 'zone_id'
        assert args[0].value == zone_id
        assert args[1].name == 'phone_id'
        assert args[1].value == 'user_phone_id'
        if experiment_enabled:
            async.return_value([
                experiments3.ExperimentsValue(
                    name='antifraud_config',
                    value=experiment_config,
                ),
                experiments3.ExperimentsValue(
                    name='other',
                    value={}
                )
            ])
        else:
            async.return_value([
                experiments3.ExperimentsValue(
                    name='antifraud_config',
                    value={'enabled': False},
                ),
                experiments3.ExperimentsValue(
                    name='other',
                    value={}
                )
            ])

    current_config = yield antifraud._get_zone_config(zone_id, 'user_phone_id')
    assert len(mock_exp3_get_values.calls) == 1
    if experiment_enabled:
        assert current_config == experiment_config
    elif default_expected:
        assert current_config == DEFAULT_CONFIG
    else:
        doc = yield dbh.tariff_settings.Doc.find_by_home_zone(zone_id)
        assert current_config == doc.antifraud_config


@pytest.mark.parametrize(
    'order_source,application,expected_service',
    [
        (None, None, 'card'),
        (None, 'android', 'card'),
        ('yandex', 'iphone', 'card'),
        ('uber', 'uber_android', 'uber'),
        ('yauber', 'uber_iphone', 'uber'),
    ]
)
@pytest.mark.parametrize(
    'order_id,was_region_checked_result,check_card_result,'
    'expected_check_calls,expected_mark_calls,billing_status', [
        ('newbie-order', False, True, [(225, 'RUB')], [True], 'ok'),
        ('newbie-order', False, False, [(225, 'RUB')], [False], 'ok'),
        ('loyal-order', True, True, [], [], 'ok'),
        ('loyal-order', False, True, [(225, 'RUB')], [True], 'ok'),
        ('erevan-order', False, True, [(168, 'AMD')], [True], 'ok'),

        ('newbie-order', False, True, [(225, 'RUB')], [], 'fail'),
        ('newbie-order', False, True, [(225, 'RUB')], [], 'fail'),
        ('loyal-order', True, True, [], [], 'fail'),
        ('loyal-order', False, True, [(225, 'RUB')], [], 'fail'),
        ('erevan-order', False, True, [(168, 'AMD')], [], 'fail'),
])
@pytest.mark.parametrize('billing_by_brand_enabled', [False, True])
@pytest.mark.filldb(orders='check_card', user_phones='check_card')
@pytest.inline_callbacks
def test_check_card(order_id, was_region_checked_result, check_card_result,
                    expected_check_calls, expected_mark_calls, billing_status,
                    patch, order_source, application, expected_service,
                    billing_by_brand_enabled):
    yield config.BILLING_SERVICE_NAME_MAP_BY_BRAND_ENABLED.save(
        billing_by_brand_enabled,
    )
    update = defaultdict(dict)

    if order_source is not None:
        update['$set'].update({'source': order_source})
    if application is not None:
        update['$set'].update({'statistics.application': application})

    if update:
        yield db.orders.update({'_id': order_id}, update)

    class FakeCard(object):
        card_id = 'card-xxx'

        def was_region_checked(self, region_id):
            return was_region_checked_result

        @async.inline_callbacks
        def mark_as_checked(self, region_id, success=True):
            yield
            FakeCard.mark_as_checked.calls.append(success)
        mark_as_checked.calls = []

        @async.inline_callbacks
        def check(self, user_ip=None, region_id=None, currency=None,
                  service=None, uber_id=None, log_extra=None):
            assert user_ip == '1.1.1.1'
            assert service == expected_service
            assert uber_id is None

            FakeCard.check.calls.append((region_id, currency))
            yield
            if billing_status == 'ok':
                async.return_value(check_card_result)
            else:
                raise card_operations.BillingError(
                    'I\'m not working, because I can'
                )
        check.calls = []

    order_doc = yield db.orders.find_one({'_id': order_id})
    result = yield antifraud.check_card(FakeCard(), order_doc)

    assert result == check_card_result
    assert FakeCard.check.calls == expected_check_calls
    assert FakeCard.mark_as_checked.calls == expected_mark_calls


@pytest.mark.parametrize(
    ['common_config', 'order_id', 'expected_result'], [
        ({}, 'newbie-order', True),
        ({}, 'loyal-order', False),
        ({'loyal_user_region_check': True}, 'newbie-order', True),
        ({'loyal_user_region_check': True}, 'loyal-order', True),
])
@pytest.mark.filldb(orders='check_card', user_phones='check_card')
@pytest.inline_callbacks
def test_need_check_card_against_region(patch, common_config, order_id,
                                        expected_result):
    @patch('taxi.internal.order_kit.antifraud._get_common_config')
    @async.inline_callbacks
    def _get_common_config():
        yield
        async.return_value(common_config)

    order_doc = yield db.orders.find_one({'_id': order_id})
    result = yield antifraud.need_check_card_against_region(
        order_doc['user_phone_id']
    )
    assert result == expected_result


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='payment_events')
@pytest.inline_callbacks
def test_payment_events_antifraud():
    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    yield antifraud.stop_procedure_and_move_to_cash(order_doc)

    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    assert order_doc.payment_events == [
        {
            'status': 'success',
            'type': 'moved_to_cash_by_antifraud',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'reason': {'code': 'NEED_CVN'},
                'from': {'type': 'card'}
            }
        }
    ]


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='payment_events')
@pytest.inline_callbacks
def test_reset_cashback_on_stop():
    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    yield antifraud.stop_procedure_and_move_to_cash(order_doc)

    assert order_doc['payment_tech']['sum_to_pay'] == {
        'ride': 0,
        'cashback': 0
    }


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='payment_events')
@pytest.mark.parametrize('reason', ['NEED_CVN', 'UNUSABLE_CARD'])
@pytest.mark.parametrize('need_cvn', [True, False])
@pytest.inline_callbacks
def test_antifraud_move_to_cash_settings_exp(patch, reason, need_cvn):
    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')

    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(consumer, args, **kwargs):
        yield
        assert consumer == 'backend/antifraud'
        assert args[0].name == 'zone_id'
        assert args[0].value == str(order_doc.get('nz'))
        assert args[1].name == 'phone_id'
        assert args[1].value == str(order_doc.get('user_phone_id'))
        async.return_value([
            experiments3.ExperimentsValue(
                name='other_1',
                value={},
            ),
            experiments3.ExperimentsValue(
                name='antifraud_move_to_cash_settings',
                value={'reason': reason, 'need_cvn': need_cvn},
            ),
            experiments3.ExperimentsValue(
                name='other_2',
                value={},
            ),
        ])

    yield antifraud.stop_procedure_and_move_to_cash(order_doc)

    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')

    assert order_doc.payment_tech.need_cvn == need_cvn
    assert order_doc.request.updated_requirements == [
        {
            'requirement': 'creditcard',
            'value': False,
            'reason': {'code': reason},
            'from': 'card',
        }
    ]
    assert order_doc.payment_events == [
        {
            'status': 'success',
            'type': 'moved_to_cash_by_antifraud',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'reason': {'code': reason},
                'from': {'type': 'card'}
            }
        }
    ]


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='early_hold')
@pytest.mark.parametrize('order_id,policy', [
    ('no_policy', 'cancel_order',),
    ('with_policy', 'move_to_cash',),
    ('with_policy_and_typo', 'cancel_order',),
])
@pytest.inline_callbacks
def test_get_early_hold_failure_policy(order_id, policy):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    result = antifraud._get_early_hold_failure_policy(order_doc)
    assert result == policy


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='early_hold')
@pytest.mark.parametrize('order_id,result', [
    ('no_early_hold', 'payment_fail',),
    ('no_policy', 'need_to_cancel',),
    ('with_policy', 'early_hold_fail_move_to_cash',),
    ('with_policy_and_typo', 'need_to_cancel',),
])
@pytest.mark.config(
    ANTIFRAUD_ALLOWED_TAXI_STATUSES_TO_CANCEL_EARLY_HOLD=['transporting']
)
@pytest.inline_callbacks
def test_early_hold_antifraud_decision(order_id, result):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    payment_fail = yield antifraud.PaymentFail.from_last_transaction(
        order_doc, None,
    )
    status, decision = yield antifraud.get_status_and_decision(
        order_doc, payment_fail, None,
    )
    assert status == result


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='early_hold')
@pytest.mark.parametrize('order_id,expected', [
    ('no_early_hold', 'some_series',),
    ('no_policy', None,),
    ('with_policy', None,),
    ('with_policy_and_typo', None,),
])
@pytest.inline_callbacks
def test_coupon_for_experiments(order_id, expected, patch):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    coupon = antifraud._extract_used_coupon_for_exps(order_doc)
    assert coupon == expected

    exp3_data = {'args': []}

    @patch('taxi.external.experiments3.get_values')
    @pytest.inline_callbacks
    def _get_values(consumer, args, **kwargs):
        exp3_data['args'] = args
        return {}

    yield antifraud._get_antifraud_experiments3('zone', 'phone', coupon=coupon)

    args = exp3_data['args']
    coupon_args = [x for x in args if x.name == 'coupon']
    if expected:
        coupon_arg = coupon_args[0]
        assert coupon_arg.type == 'string'
        assert coupon_arg.value == expected
    else:
        assert not coupon_args


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.filldb(orders='early_hold')
@pytest.mark.parametrize('order_id,expected', [
    ('with_policy', None,),
    ('with_policy_and_typo', 'personal_wallet',),
])
@pytest.inline_callbacks
def test_complements_for_experiments(order_id, expected, patch):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    complement = antifraud._extract_complement_payment_for_exps(order_doc)
    assert complement == expected

    exp3_data = {'args': []}

    @patch('taxi.external.experiments3.get_values')
    @pytest.inline_callbacks
    def _get_values(consumer, args, **kwargs):
        exp3_data['args'] = args
        return {}

    yield antifraud._get_antifraud_experiments3('zone', 'phone', complement_payment_type=complement)

    args = exp3_data['args']
    complement_args = [x for x in args if x.name == 'complement_payment_type']
    if expected:
        complement_arg = complement_args[0]
        assert complement_arg.type == 'string'
        assert complement_arg.value == expected
    else:
        assert not complement_args


@pytest.mark.config(WITHDRAWAL_TYPE_SET_ENABLED=True)
@pytest.mark.filldb(orders='early_hold', order_proc='early_hold')
@pytest.inline_callbacks
def test_withdrawal_type_early_hold(patch):

    @patch('taxi.internal.userapi.get_user_dbh')
    @async.inline_callbacks
    def get_user_dbh(user_id, fields=None, reqire_latest=False, log_extra=None):
        yield
        async.return_value()

    @patch(
        'taxi.internal.order_kit.antifraud._get_experiment3_early_hold_params'
    )
    @async.inline_callbacks
    def _get_experiment3_early_hold_params(*args, **kwargs):
        yield
        value = {
            'enabled': True,
            'skip_group_recalc': True,
            'allowed_statuses': [
                'driving'
            ],
            'allowed_taxi_statuses': [
                'driving'
            ],
            'forced_user_antifraud_status': 'test',
            "params_by_status": {
                "test": {
                    "fixed_price_hold_all": True
                },
                "force_fix_prepay": {
                    "fixed_price_hold_all": True
                }
            },
        }
        async.return_value(value)

    @patch(
        'taxi.internal.order_kit.antifraud.commit_early_hold_sum'
    )
    @async.inline_callbacks
    def commit_early_hold_sum(order_doc, next_sum, cashback_sum, failure_policy, log_extra):
        yield

    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_doc, intent=None, log_extra=None):
        yield

    @patch('taxi.internal.order_core.get_order_proc_fields')
    @async.inline_callbacks
    def get_order_proc_fields(order_id, fields, log_extra):
        yield
        async.return_value({'revision': []})

    @patch('taxi.internal.order_core.set_order_proc_fields')
    @async.inline_callbacks
    def set_order_proc_fields(order_id, update, revision, log_extra=None):
        yield
        assert update['$set'].get('payment_tech.withdrawal_type', '') == 'early_hold'
        async.return_value()

    order_id = "withdrawal_type_early_hold"
    order_doc = dbh.orders.Doc(
        (yield db.orders.find_one({'_id': order_id}))
    )
    order_proc_doc = dbh.order_proc.Doc(
        (yield db.order_proc.find_one({'_id': order_id}))
    )
    yield antifraud.maybe_start_early_hold(order_doc, order_proc_doc, None)
    assert len(set_order_proc_fields.calls) == 1
