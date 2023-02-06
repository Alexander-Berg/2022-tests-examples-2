# coding: utf-8
from __future__ import unicode_literals

import bson
import contextlib
import copy
import datetime
import decimal
import json

from bson import json_util
import pytest
from twisted.internet import error

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.conf import settings
from taxi.core import twisty_helpers
from taxi.external import billing
from taxi.external import processing_antifraud
from taxi.internal import card_operations
from taxi.internal import dbh
from taxi.internal.coop_account import client as coop_client
from taxi.internal.order_kit import antifraud
from taxi.internal.order_kit import exceptions
from taxi.internal.order_kit import invoice_handler
from taxi.internal.order_kit import order_helpers
from taxi.internal.order_kit import payment_handler
from taxi.internal.order_kit import payment_helpers
from taxi.internal.order_kit import tips_handler
from taxi.internal.order_kit.payables import coop
from taxi.internal.payment_kit import invoices

from cardstorage_mock import mock_cardstorage

NOW = datetime.datetime.utcnow().replace(microsecond=0)


@pytest.fixture(params=[True, False])
def b2b_sng_flag(request):
    return request.param


@pytest.fixture(autouse=True)
def patch_cardsotrage_client(patch):
    mock_cardstorage(patch)


class _Response(object):
    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.filldb(
    parks='no_performer',
)
@pytest.inline_callbacks
def test_update_transactions_no_performer(patch, load):
    order_id = 'no_performer'

    @patch('taxi.internal.order_kit.invoice_handler._calc_next_update_eta')
    @async.inline_callbacks
    def calc_next_update_eta(
            payable, processing, feedback_context, log_extra=None
    ):
        yield

    expected_request = json.loads(load('test_update_transactions_no_performer/v2_invoice_update_request.json'))

    @patch('taxi.external.transactions._perform_request')
    @async.inline_callbacks
    def _perform_request_mock(method, location, json, **kwargs):
        assert method == 'POST'
        assert location == 'v2/invoice/update'
        assert json == expected_request
        yield
        async.return_value(_Response({}))

    invoice_dict = json.loads(load('test_update_transactions_no_performer/invoice.json'))
    _patch_try_process_invoice(patch, True, invoices.InvoiceV2(invoice_dict))

    yield invoice_handler.update_transactions_iteration(order_id)


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.filldb(
    parks='no_performer',
)
@pytest.inline_callbacks
def test_update_transactions_intent(patch, load):
    order_id = 'no_performer'
    expected_intent = 'test_intent'

    @patch('taxi.internal.order_kit.invoice_handler._calc_next_update_eta')
    @async.inline_callbacks
    def calc_next_update_eta(
            payable, processing, feedback_context, log_extra=None
    ):
        yield

    @patch('taxi.external.transactions._perform_request')
    @async.inline_callbacks
    def _perform_request_mock(method, location, json, **kwargs):
        assert method == 'POST'
        assert location == 'v2/invoice/update'
        assert json['intent'] == expected_intent
        yield
        async.return_value(_Response({}))

    @patch('taxi.internal.order_kit.payment_handler.PayableOrder.before_update_transactions_dirty')
    @async.inline_callbacks
    def _before_update_transactions_dirty_mock(processing, intent, log_extra):
        assert intent == expected_intent
        yield
        async.return_value(False)

    invoice_dict = json.loads(load('test_update_transactions_no_performer/invoice.json'))
    _patch_try_process_invoice(patch, True, invoices.InvoiceV2(invoice_dict))

    yield invoice_handler.update_transactions_iteration(order_id, intent=expected_intent)
    assert len(_perform_request_mock.calls) == 1
    assert len(_before_update_transactions_dirty_mock.calls) == 1


@pytest.mark.parametrize('order_id,card_ids', [
    ('order_with_one_card', ['one_card']),
    ('order_with_many_cards', [
        'card_one', 'card_two', 'card_three', 'zero_card',
    ]),
])
@pytest.mark.filldb(orders='unmark_paid', cards='unmark_paid')
@pytest.inline_callbacks
def test_unmark_if_paid(order_id, card_ids):
    """Test that all cards (even failed) are released when order is paid fully.
    """
    order_doc = yield db.orders.find_one({'_id': order_id})
    yield invoice_handler._unmark_if_paid(order_doc)
    for card in (yield db.cards.find({'_id': {'$in': card_ids}}).run()):
        busy_orders = [i['order_id'] for i in card['busy_with']]
        assert order_id not in busy_orders, '{} in {}'.format(order_id, card)


@pytest.mark.config(COOP_ACCOUNT_ACTIVATE_FROM_NEW_POINT=True)
@pytest.mark.parametrize('is_debt', [False, True])
@pytest.mark.parametrize('config_send_order_id', [False, True])
@pytest.mark.filldb(orders='unmark_paid', cards='unmark_paid')
@pytest.inline_callbacks
def test_coop_unlock(patch, is_debt, config_send_order_id):
    order_doc = yield db.orders.find_one({'_id': 'order_with_one_card'})
    order_doc['payment_tech']['debt'] = is_debt
    order_doc['request']['payment']['type'] = 'coop_account'
    order_doc['request']['payment']['payment_method_id'] = 'family-1'

    @patch('taxi.config.COOP_ACCOUNT_DO_SEND_ORDER_ID.get')
    @async.inline_callbacks
    def get_config_send_order_id():
        yield
        async.return_value(config_send_order_id)

    @patch('taxi.internal.coop_account.client.activate_account')
    @async.inline_callbacks
    def _activate_account(account_id, order_id):
        yield
        async.return_value({})

    yield invoice_handler._unmark_if_paid(order_doc)

    call_0 = _activate_account.calls[0]
    assert call_0['args'] == ('family-1',)
    debt_order_id = 'order_with_one_card' if config_send_order_id else None
    assert call_0['kwargs'] == {'order_id': debt_order_id}


@pytest.mark.parametrize('payment_type,not_fake_ride, check_passed', [
    ('card', None, False),
    ('card', True, True),
    ('card', False, False),

    ('applepay', None, False),
    ('applepay', True, True),
    ('applepay', False, False),

    ('googlepay', None, False),
    ('googlepay', True, True),
    ('googlepay', False, False),

    ('cash', None, False),
    ('cash', True, True),
    ('cash', False, False),

    ('corp', None, False),
    ('corp', True, True),
    ('corp', False, False),

    ('personal_wallet', None, False),
    ('personal_wallet', True, True),
    ('personal_wallet', False, False)

])
@pytest.mark.parametrize('update_proc_in_procaas', [False, True])
@pytest.mark.config(WITHDRAWAL_TYPE_SET_ENABLED=False)
@pytest.inline_callbacks
def test_antifraud_fake(not_fake_ride, check_passed, payment_type,
                        update_proc_in_procaas):
    """Test timecheck is disabled with 'not_fake_ride' == True.
    """
    yield config.PY2_PROCESSING_UPDATE_PROC_IN_PROCAAS.save(update_proc_in_procaas)

    def check_init_order(order_doc):
        assert order_doc.payment_tech.finish_handled is False
        assert order_doc.payment_tech.sum_to_pay == {u'ride': 1180000, u'tips': 0, u'rebate': 400000}
        assert order_doc.payment_tech.user_to_pay == {u'ride': 1180000, u'tips': 0}
        assert order_doc.payment_tech.without_vat_to_pay == {u'ride': 1000000, u'tips': 0}

    def check_finish_good_order(order_doc):
        assert order_doc.payment_tech.finish_handled is True
        if payment_type == 'cash':
            assert order_doc.payment_tech.sum_to_pay == {u'ride': 0, u'tips': 0, u'rebate': 400000}
            assert order_doc.payment_tech.user_to_pay == {u'ride': 0, u'tips': 0}
            assert order_doc.payment_tech.without_vat_to_pay == {u'ride': 0, u'tips': 0}
        elif payment_type == 'corp':
            assert order_doc.payment_tech.sum_to_pay == {u'ride': 21240000, u'tips': 0, u'rebate': 400000}
            assert order_doc.payment_tech.user_to_pay == {u'ride': 21240000, u'tips': 0}
            assert order_doc.payment_tech.without_vat_to_pay == {u'ride': 18000000, u'tips': 0}
        else:
            assert order_doc.payment_tech.sum_to_pay == {u'ride': 18000000, u'tips': 0, u'rebate': 400000}
            assert order_doc.payment_tech.user_to_pay == {u'ride': 18000000, u'tips': 0}
            assert order_doc.payment_tech.without_vat_to_pay == {u'ride': 18000000, u'tips': 0}

    def check_finish_fraud_order(order_doc):
        assert order_doc.payment_tech.finish_handled is True
        assert order_doc.payment_tech.sum_to_pay == {u'ride': 0, u'tips': 0, u'rebate': 400000}
        assert order_doc.payment_tech.user_to_pay == {u'ride': 0, u'tips': 0}
        assert order_doc.payment_tech.without_vat_to_pay == {u'ride': 0, u'tips': 0}

    order_id = 'check_fake_ride'
    fake_ride_time = settings.FAKE_RIDE_TIME - 10
    update = {
        'request.payment.type': payment_type,
        'payment_tech.finish_handled': False,
        'payment_tech.type': payment_type,
        'statistics.travel_time': fake_ride_time,
    }
    if payment_type == 'corp':
        update.update({
            "request.corp": {
                "client_id": "some_client_id",
                "user_id": "some_corp_user_id"
            },
        })
    if not_fake_ride is not None:
        update.update({'not_fake_ride': not_fake_ride})
    yield db.orders.update({'_id': order_id}, {'$set': update})

    order = yield dbh.orders.Doc.find_one_by_exact_id(order_id)
    order_proc = yield dbh.order_proc.Doc.find_one_by_exact_id(order_id)

    check_init_order(order)

    passed_by_ride_time = not order_helpers.is_fake_ride_time(order)
    assert check_passed == passed_by_ride_time

    yield invoice_handler.finish_ride(order, order_proc, order.billing_contract)
    finished_order = yield dbh.orders.Doc.find_one_by_exact_id(order_id)
    if not check_passed:
        check_finish_fraud_order(finished_order)
    else:
        check_finish_good_order(finished_order)
    finished_proc = yield dbh.order_proc.Doc.find_one_by_exact_id(order_id)
    if update_proc_in_procaas:
        assert order_proc.preupdated_proc_data.check_card_is_finished == {'payment_tech.check_card_is_finished': True}
        assert finished_proc.payment_tech == {}
    else:
        assert order_proc.preupdated_proc_data.check_card_is_finished is None
        assert finished_proc.payment_tech == {'check_card_is_finished': True}


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_ENABLED=True
)
@pytest.mark.parametrize('order_id,is_fake,request_error', [
    ('540_2', True, True),
    ('540_1', False, True),
    ('540_2', True, False),
    ('540_1', False, False),
])
@pytest.inline_callbacks
def test_antifraud_fallback(patch, order_id, is_fake, request_error):

    @patch('taxi.external.processing_antifraud._request')
    def _mock_antifraud(*args, **kwargs):
        if request_error:
            raise processing_antifraud.ProcessingAntifraudRequestError
        else:
            return {
                'is_fake_ride': is_fake
            }

    order_doc = yield db.orders.find_one({'_id': order_id})
    fake_ride = yield invoice_handler.is_fake_ride(order_doc)

    assert fake_ride == is_fake


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_ENABLED=True
)
@pytest.mark.parametrize(
    'order_id,request_json',
    [
        (
            '540_1',
            {
                'order_id': '540_1',
                'order_status': 'finished',
                'tariff_class': 'econom',
                'taxi_status': 'completed',
                'total_time_after_assignment': 1222,
                'travel_time': 120,
            },
        ),
        (
            '540_2',
            {
                'order_id': '540_2',
                'order_status': 'finished',
                'taxi_status': 'complete',
                'travel_time': 0,
            },
        ),
        (
            '540_2_2',
            {
                'order_id': '540_2_2',
                'order_status': 'finished',
                'taxi_status': 'complete',
                'total_time_after_assignment': 16707829,
                'travel_time': 0,
            },
        )
    ],
)
@pytest.inline_callbacks
def test_antifraud_fake_ride_params(patch, order_id, request_json):

    @patch('taxi.external.processing_antifraud._request')
    def _mock_antifraud(method, url, tvm_src_service, json, **kwargs):
        assert json == request_json
        return {
            'is_fake_ride': False
        }

    order_doc = yield db.orders.find_one({'_id': order_id})
    yield invoice_handler.is_fake_ride(order_doc)

    assert len(_mock_antifraud.calls) == 1


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_ENABLED=False
)
@pytest.mark.parametrize('order_id,is_fake', [
    ('540_2', True),
    ('540_1', False)
])
@pytest.inline_callbacks
def test_antifraud_disabled_config(patch, order_id, is_fake):

    order_doc = yield db.orders.find_one({'_id': order_id})
    fake_ride = yield invoice_handler.is_fake_ride(order_doc)

    assert fake_ride == is_fake


@pytest.mark.parametrize('order_id,current_card_id,old_card_ids', [
    ('order_with_one_card', 'one_card', []),
    ('order_with_many_cards', 'card_three', [
        'card_one', 'card_two', 'zero_card',
    ]),
])
@pytest.mark.filldb(orders='unmark_paid', cards='unmark_paid')
@pytest.inline_callbacks
def test_release_old_cards(order_id, current_card_id, old_card_ids):
    """Test that current card is not released in _release_old_cards.
    """
    order_doc = yield db.orders.find_one({'_id': order_id})
    yield invoice_handler._release_old_cards(order_doc)
    for card in (yield db.cards.find({'_id': {'$in': old_card_ids}}).run()):
        busy_orders = [i['order_id'] for i in card['busy_with']]
        assert order_id not in busy_orders, '{} in {}'.format(order_id, card)
    for card in (yield db.cards.find({'_id': current_card_id}).run()):
        busy_orders = [i['order_id'] for i in card['busy_with']]
        assert order_id in busy_orders, '{} not in {}'.format(order_id, card)


class NoException(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.parametrize(
    'config_value,order_id,expectation,expected_reason,'
    'expected_transaction_index', [
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'invoice_payment_tech_order_id',
            pytest.raises(invoice_handler.CardUnboundViaTransactionsError),
            'created_basket_with_unbound_card',
            None,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'after_pay_basket_order_id',
            pytest.raises(invoice_handler.CardUnboundViaTransactionsError),
            'transaction_failed',
            0,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'after_pay_basket_py2_order_id',
            NoException(),
            None,
            None,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'after_pay_basket_second_time_order_id',
            NoException(),
            None,
            None,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'py2_order_id',
            NoException(),
            None,
            None,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'after_pay_basket_successful_main_payment_order_id',
            NoException(),
            None,
            None,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'after_pay_basket_unusable_complement_payment_order_id',
            NoException(),
            None,
            None,
        ),
        (
            [
                {'payment_resp_code': 'invalid_processing_request'}
            ],
            'after_pay_basket_usable_main_payment_order_id',
            NoException(),
            None,
            None,
        ),
        # every payment_method_type is affected by default
        (
            [
                {
                    'payment_resp_code': 'invalid_processing_request',
                }
            ],
            'after_pay_basket_unusable_main_payment_order_id',
            pytest.raises(invoice_handler.CardUnboundViaTransactionsError),
            'transaction_failed',
            0,
        ),
        # explicit payment_method_types
        (
            [
                {
                    'payment_resp_code': 'invalid_processing_request',
                    'payment_method_types': ['card']
                }
            ],
            'after_pay_basket_unusable_main_payment_order_id',
            pytest.raises(invoice_handler.CardUnboundViaTransactionsError),
            'transaction_failed',
            0,
        ),
        (
            [
                {
                    'payment_resp_code': 'invalid_processing_request',
                    'payment_method_types': ['applepay', 'googlepay'],
                }
            ],
            'after_pay_basket_unusable_main_payment_order_id',
            NoException(),
            None,
            None,
        ),
        # every payment_method_type is affected by default
        (
            [
                {
                    'payment_resp_code': 'invalid_processing_request',
                }
            ],
            'after_pay_basket_unusable_old_main_payment_order_id',
            pytest.raises(invoice_handler.CardUnboundViaTransactionsError),
            'transaction_failed',
            0,
        ),
        # explicit payment_method_types and transaction without payment_method_type
        (
            [
                {
                    'payment_resp_code': 'invalid_processing_request',
                    'payment_method_types': ['card']
                }
            ],
            'after_pay_basket_unusable_old_main_payment_order_id',
            NoException(),
            None,
            None,
        ),
        (
            [
                {
                    'payment_resp_code': 'invalid_processing_request',
                    'payment_method_types': ['applepay', 'googlepay'],
                }
            ],
            'after_pay_basket_unusable_main_payment_order_id',
            NoException(),
            None,
            None,
        ),
])
@pytest.mark.filldb(
    orders='for_test_check_unbound_card_via_transactions'
)
@pytest.inline_callbacks
def test_check_unbound_card_via_transactions(
        config_value,
        order_id,
        expectation, expected_reason, expected_transaction_index,
):
    yield config.TRANSACTIONS_TAXI_UNUSABLE_CARD_ERRORS.save(config_value)
    payable_order = yield _fetch_payable_order(order_id)
    with expectation as excinfo:
        yield invoice_handler._check_unbound_card_via_transactions(
            payable_order
        )

    if excinfo is not None:
        assert excinfo.value.reason == expected_reason
        assert excinfo.value.transaction_index == expected_transaction_index


@pytest.mark.filldb(
    orders='for_test_apply_card_unbound_reason'
)
@pytest.inline_callbacks
def test_apply_card_unbound_reason_created_basket_with_unbound_card():
    payable_order = yield _fetch_payable_order('some_order_id')
    yield invoice_handler._apply_card_unbound_reason(
        payable_order=payable_order,
        reason='created_basket_with_unbound_card',
        transaction_index=None,
        log_extra=None,
    )
    after = yield _fetch_payable_order('some_order_id')
    invoice_payment_tech = after.order_doc['invoice_payment_tech']
    assert 'created_basket_with_unbound_card' not in invoice_payment_tech


@pytest.mark.filldb(
    orders='for_test_apply_card_unbound_reason'
)
@pytest.inline_callbacks
def test_apply_card_unbound_reason_transaction():
    payable_order = yield _fetch_payable_order('some_order_id')
    yield invoice_handler._apply_card_unbound_reason(
        payable_order=payable_order,
        reason='transaction_failed',
        transaction_index=0,
        log_extra=None,
    )
    after = yield _fetch_payable_order('some_order_id')
    assert after.transactions[0]['handled_unbound_card'] is True


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_set_tips_sum_not_complete():
    order_doc = {
        'taxi_status': 'not_complete',
        'payment_tech': {'finish_handled': False},
    }
    # No more calculations
    yield tips_handler.set_tips_sum(order_doc, None)


@pytest.mark.config(
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=False
)
@pytest.mark.parametrize(('order_id,summ,version,_get_card_exception,'
                          'expected_sum_to_pay,expected_can_take_tips,'
                          'expected_refresh_attempts_count, decision,'
                          'decision_sum,exception,need_debt_check,country_vat,'
                          'inner_vat,ignore_max_sum,use_configurable_limit,update_configurable_limit'), [
    # we keep tips and set payment_tech.can_take_tips to False during charge
    ('540_1', 610, 1, None,
     {'ride': 6100000, 'tips': 1000}, False, 0, 'charge', 70,
     None, True, 11800, None, False, False, None),
    # we reset tips during refund
    ('540_1', 500, 1, None,
     {'ride': 5000000, 'tips': 0}, True, 0, 'refund', 40,
     None, True, 11800, None, False, False, None),
    # we don't check card during refund
    ('540_1', 500, 1, card_operations.CardNotFoundError,
     {'ride': 5000000, 'tips': 0}, True, 0, 'refund', 40,
     None, True, 11800, None, False, False, None),
    # we decrement refresh_attempts_count if it's greater than
    # settings.BILLING_MAX_REFRESH_ATTEMPTS, that's why 98
    ('1540_2', 1500, 1, None,
     {'ride': 15000000, 'tips': 0}, True, 98, 'refund', 40,
     None, True, 11800, None, False, False, None),
    # we recalculate corp_user stat, also vat is 20% for this order
    ('540_2', 150, 1, None,
     {'ride': 1500000, 'tips': 1000}, False, 0, 'charge', 50,
     None, False, 12000, None, False, False, None),

    # versions mismatch
    ('1540_2', 500, 2, None,
     {'ride': 15400000, 'tips': 1000}, True, 100, None, None,
     exceptions.RaceConditionError, False, 11800, None, False, False, None),
    # summ < 0
    ('540_1', -2, 1, None,
     {'ride': 5400000, 'tips': 1000}, True, 0, None, None,
     exceptions.InvalidRefundSumError, False, 11800, None, False, False, None),
    # can't change sum to the same sum
    ('540_1', 540, 1, None,
     {'ride': 5400000, 'tips': 1000}, True, 0, None, None,
     exceptions.SameRideSumError, False, 11800, None, False, False, None),
    # refund > 1000
    ('1540_2', 500, 1, None,
     {'ride': 15400000, 'tips': 1000}, True, 100, None, None,
     exceptions.InvalidRefundSumError, False, 11800, None, False, False, None),
    # charge > 900, max_manual_charge is defined in db_cities.json
    ('540_1', 1441, 1, None,
     {'ride': 5400000, 'tips': 1000}, True, 0, None, None,
     exceptions.InvalidChargeSumError, False, 11800, None, False, False, None),
    # card not found
    ('540_1', 610, 1, card_operations.CardNotFoundError,
     {'ride': 5400000, 'tips': 1000}, True, 0, None, None,
     exceptions.CardNotFoundError, False, 11800, None, False, False, None),
    # order with need_disp_accept
    ('order_need_disp_accept', 610, 1, None,
     {'ride': 15400000, 'tips': 1000}, True, 100, None, None,
     exceptions.InvalidRideCostError, False, 11800, None, False, False, None),
    ('order_with_just_partner_payments', 100, 1, None,
     {'ride': 5400000, 'tips': 1000}, True, 0, None, None,
     exceptions.JustPartnerPaymentsRefundError, False, 11800, None, False, False, None),

    # rebate
    ('540_3', 50, 1, None,
     {'ride': 500000, 'tips': 0}, False, 0, 'refund', 50,
     None, False, 11800, None, False, False, None),
    ('540_4', 500, 1, None,
     {'ride': 4800000, 'tips': 0, 'rebate': 200000},
     False, 0, 'refund', 500, None, False, 11800, None, False, False, None),
    ('540_4', 500, 1, None,
     {'ride': 5664000, 'tips': 0, 'rebate': 236000},
     False, 0, 'refund', 500, None, False, 11800, 11800, False, False, None),
    # charge > 900. Set ingore flag to perform action
    # no inner vat
    ('540_4', 1100, 1, None,
     {'ride': 10560000, 'tips': 0, 'rebate': 440000},
     False, 0, 'charge', 100, None, False, 11800, None, True, False, None),
    # no inner vat
    ('540_4', 1500, 1, None,
     {'ride': 14520000, 'tips': 0, 'rebate': 480000},
     False, 0, 'charge', 500, None, False, 11800, None, True, False, None),
    # inner vat exists
    ('540_4', 1100, 1, None,
     {'ride': 12460800, 'tips': 0, 'rebate': 519200},
     False, 0, 'charge', 100, None, False, 11800, 11800, True, False, None),
    # inner vat exists
    ('540_4', 1500, 1, None,
     {'ride': 17133600, 'tips': 0, 'rebate': 566400},
     False, 0, 'charge', 500, None, False, 11800, 11800, True, False, None),
    # refund > 1000
    ('1540_2', 500, 1, None,
     {'ride': 5000000, 'tips': 0},
     True, 98, 'refund', 1040, None, False, 11800, None, True, False, None),
    # charge > 900
    ('540_1', 1441, 1, None,
     {'ride': 14410000, 'tips': 1000},
     False, 0, 'charge', 901, None, False, 11800, None, True, False, None),

    # ADMIN_PAYMENT_MAX_MANUAL_CHARGE,
    # charge > 900, < ADMIN_PAYMENT_MAX_MANUAL_CHARGE, use_configurable_limit = True
    ('540_1', 1441, 1, None,
     {'ride': 14410000, 'tips': 1000},
     False, 0, 'charge', 901, None, False, 11800, None, False, True, None),
    # charge > ADMIN_PAYMENT_MAX_MANUAL_CHARGE (25000), use_configurable_limit = True
    ('540_1', 25001, 1, None,
     {'ride': 5400000, 'tips': 1000},
     True, 0, 'charge', 901,
     exceptions.ChargeSumGreaterLimitError, False, 11800, None, False, True, None),
    # charge > ADMIN_PAYMENT_MAX_MANUAL_CHARGE (25000), ignore_limit = True, use_configurable_limit = True
    ('540_1', 25001, 1, None,
     {'ride': 250010000, 'tips': 1000},
     False, 0, 'charge', 24461, None, False, 11800, None, True, True, None),
    # charge < limit, but charge > ADMIN_PAYMENT_MAX_MANUAL_CHARGE, use_configurable_limit = True
    ('540_1', 899, 1, None,
     {'ride': 5400000, 'tips': 1000},
     True, 0, 'charge', 899,
     exceptions.ChargeSumGreaterLimitError, False, 11800, None, False, True, {'RUB': 800}),
    # charge < limit, but charge > ADMIN_PAYMENT_MAX_MANUAL_CHARGE, ignore_limit = True, use_configurable_limit = True
    ('540_1', 899, 1, None,
     {'ride': 8990000, 'tips': 1000},
     False, 0, 'charge', 359,
     None, False, 11800, None, True, True, {'RUB': 800}),
    # charge < limit, ADMIN_PAYMENT_MAX_MANUAL_CHARGE NOT SET, use_configurable_limit = True
    ('540_1', 899, 1, None,
     {'ride': 8990000, 'tips': 1000},
     False, 0, 'charge', 359,
     None, False, 11800, None, False, True, {'RUB': None}),
    # charge > limit, ADMIN_PAYMENT_MAX_MANUAL_CHARGE NOT SET, use_configurable_limit = True
    ('540_1', 25001, 1, None,
     {'ride': 5400000, 'tips': 1000},
     True, 0, 'charge', 901,
     exceptions.MaxManualChargeNotSetError, False, 11800, None, False, True, {'RUB': None}),
    # charge > limit, ADMIN_PAYMENT_MAX_MANUAL_CHARGE NOT SET, ignore_limit = True, use_configurable_limit = True
    ('540_1', 25001, 1, None,
     {'ride': 250010000, 'tips': 1000},
     False, 0, 'charge', 24461,
     None, False, 11800, None, True, True, {'RUB': None}),

    # refunds
    # refund > 1000, < ADMIN_PAYMENT_MAX_MANUAL_CHARGE (25000), ignore_limit = False, use_configurable_limit = True
    ('1540_2', 500, 1, None,
     {'ride': 5000000, 'tips': 0},
     True, 98, 'refund', 1040, None, False, 11800, None, False, True, None),
    # refund > 1000, > ADMIN_PAYMENT_MAX_MANUAL_CHARGE (25000), ignore_limit = False, use_configurable_limit = True
    ('1540_2', 400, 1, None,
     {'ride': 15400000, 'tips': 1000},
     True, 100, 'refund', 1040,
     exceptions.RefundSumGreaterLimitError, False, 11800, None, False, True, {'RUB': 1050}),
    # refund > 1000, > ADMIN_PAYMENT_MAX_MANUAL_CHARGE (25000), ignore_limit = True, use_configurable_limit = True
    ('1540_2', 400, 1, None,
     {'ride': 4000000, 'tips': 0},
     True, 98, 'refund', 1140, None, False, 11800, None, True, True, {'RUB': 1050}),
    # refund < 1000, > ADMIN_PAYMENT_MAX_MANUAL_CHARGE (900), ignore_limit = False, use_configurable_limit = True
    ('1540_2', 600, 1, None,
     {'ride': 15400000, 'tips': 1000},
     True, 100, 'refund', 940,
     exceptions.RefundSumGreaterLimitError, False, 11800, None, False, True, {'RUB': 900}),
    # refund < 1000, > ADMIN_PAYMENT_MAX_MANUAL_CHARGE (900), ignore_limit = True, use_configurable_limit = True
    ('1540_2', 600, 1, None,
     {'ride': 6000000, 'tips': 0},
     True, 98, 'refund', 940,
     None, False, 11800, None, True, True, {'RUB': 900}),
    # refund < 1000, ADMIN_PAYMENT_MAX_MANUAL_CHARGE NOT SET, ignore_limit = False, use_configurable_limit = True
    ('1540_2', 600, 1, None,
     {'ride': 6000000, 'tips': 0},
     True, 98, 'refund', 940,
     None, False, 11800, None, True, True, {'RUB': None}),
    # refund > 1000, ADMIN_PAYMENT_MAX_MANUAL_CHARGE NOT SET, ignore_limit = False, use_configurable_limit = True
    ('1540_2', 400, 1, None,
     {'ride': 15400000, 'tips': 1000},
     True, 100, 'refund', 1040,
     exceptions.MaxManualChargeNotSetError, False, 11800, None, False, True, {'RUB': None}),
    # refund < 1000, ADMIN_PAYMENT_MAX_MANUAL_CHARGE NOT SET, ignore_limit = True, use_configurable_limit = True
    ('1540_2', 600, 1, None,
     {'ride': 6000000, 'tips': 0},
     True, 98, 'refund', 940,
     None, False, 11800, None, True, True, {'RUB': None})
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_ride_sum_to_pay(patch, b2b_sng_flag,
                             order_id, summ, version,
                             _get_card_exception, expected_sum_to_pay,
                             expected_can_take_tips,
                             expected_refresh_attempts_count, decision,
                             decision_sum, exception, need_debt_check,
                             country_vat, inner_vat, ignore_max_sum,
                             use_configurable_limit, update_configurable_limit):
    yield _impl_test_set_ride_sum_to_pay(
        patch, b2b_sng_flag,
        order_id, summ, version,
        _get_card_exception, expected_sum_to_pay,
        expected_can_take_tips,
        expected_refresh_attempts_count, decision,
        decision_sum, exception, need_debt_check,
        country_vat, inner_vat, ignore_max_sum,
        use_configurable_limit, update_configurable_limit)


@pytest.mark.config(
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True
)
@pytest.mark.parametrize(('order_id,summ,version,_get_card_exception,'
                          'expected_sum_to_pay,expected_can_take_tips,'
                          'expected_refresh_attempts_count, decision,'
                          'decision_sum,exception,need_debt_check,country_vat,'
                          'inner_vat,ignore_max_sum,use_configurable_limit'), [
    # refund > 1300
    ('1540_2', 200, 1, None,
     {'ride': 15400000, 'tips': 1000}, True, 100, None, None,
     exceptions.InvalidRefundSumError, False, 11800, None, False, False),
    # charge > 1900, max_manual_charge is defined in db_tariff_settings.json
    ('540_1', 2441, 1, None,
     {'ride': 5400000, 'tips': 1000}, True, 0, None, None,
     exceptions.InvalidChargeSumError, False, 11800, None, False, False),
    ('1540_2', 1500, 1, None,
     {'ride': 15000000, 'tips': 0},
     True, 98, 'refund', 40, None, False, 11800, None, False, False),
    ('540_1', 1441, 1, None,
     {'ride': 14410000, 'tips': 1000},
     False, 0, 'charge', 901, None, False, 11800, None, False, False)
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_tariff_refunds(patch, b2b_sng_flag,
                        order_id, summ, version,
                        _get_card_exception, expected_sum_to_pay,
                        expected_can_take_tips,
                        expected_refresh_attempts_count, decision,
                        decision_sum, exception, need_debt_check,
                        country_vat, inner_vat, ignore_max_sum,
                        use_configurable_limit):
    yield _impl_test_set_ride_sum_to_pay(
        patch, b2b_sng_flag,
        order_id, summ, version,
        _get_card_exception, expected_sum_to_pay,
        expected_can_take_tips,
        expected_refresh_attempts_count, decision,
        decision_sum, exception, need_debt_check,
        country_vat, inner_vat, ignore_max_sum,
        use_configurable_limit, None)


@async.inline_callbacks
def _impl_test_set_ride_sum_to_pay(patch, b2b_sng_flag,
                                   order_id, summ, version,
                                   _get_card_exception, expected_sum_to_pay,
                                   expected_can_take_tips,
                                   expected_refresh_attempts_count, decision,
                                   decision_sum, exception, need_debt_check,
                                   country_vat, inner_vat, ignore_max_sum,
                                   use_configurable_limit, update_configurable_limit):
    _patch_update_transactions_call_later(patch)

    @patch('taxi.internal.order_kit.invoice_handler._get_card')
    @async.inline_callbacks
    def _get_card(order_doc):
        if _get_card_exception is not None:
            raise _get_card_exception
        yield  # to make a generator out of it

    if inner_vat is not None:
        @patch('taxi.internal.order_kit.invoice_handler._get_corp_vat_inner')
        @async.inline_callbacks
        def _get_corp_vat_inner(order_doc, log_extra=None):
            yield
            async.return_value(inner_vat)

    @patch('taxi.internal.order_kit.order_helpers.is_rebate_enabled')
    @async.inline_callbacks
    def is_rebate_enabled(order_doc, log_extra=None):
        yield
        async.return_value(b2b_sng_flag)

    if update_configurable_limit:
        yield config.ADMIN_PAYMENTS_MAX_MANUAL_CHARGE.save(update_configurable_limit)
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    args = (
        'operator',
        order_doc,
        version,
    )
    kwargs = {
        'user_data': {
            'sum': summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        'driver_data': None,
        'ignore_limit': ignore_max_sum,
        'use_configurable_limit': use_configurable_limit,
    }
    if exception is not None:
        with pytest.raises(exception):
            yield invoice_handler.update_type_sum_to_pay(*args, **kwargs)
    else:
        yield invoice_handler.update_type_sum_to_pay(*args, **kwargs)
        yield _check_last_order_history(order_id, decision, decision_sum)
    yield _check_order_ride_sum_to_pay(order_id, expected_sum_to_pay, b2b_sng_flag)

    if need_debt_check:
        yield _check_user_is_not_debtor(order_id)

    order_doc = yield db.orders.find_one({'_id': order_id})
    assert order_doc['payment_tech']['ctt'] == expected_can_take_tips
    actual_rac = order_doc['billing_tech']['refresh_attempts_count']
    assert actual_rac == expected_refresh_attempts_count


@async.inline_callbacks
def _check_last_order_history(order_id, last_decision, last_decision_sum):
    order_doc = yield db.orders.find_one({'_id': order_id})
    last = order_doc['payment_tech']['history'][-1]
    assert last['decision'] == last_decision
    assert last['%s_sum' % last_decision]['ride'] == last_decision_sum


@async.inline_callbacks
def _check_order_ride_sum_to_pay(order_id, expected_sum_to_pay, b2b_sng):
    order_doc = yield db.orders.find_one({'_id': order_id})
    assert (order_doc['payment_tech']['sum_to_pay']['tips'] ==
            expected_sum_to_pay['tips'])
    if expected_sum_to_pay.get('rebate') and b2b_sng:
        assert (order_doc['payment_tech']['sum_to_pay']['rebate'] ==
                expected_sum_to_pay['rebate'])
    if expected_sum_to_pay.get('rebate') and not b2b_sng:
        assert (order_doc['payment_tech']['sum_to_pay']['ride'] ==
                expected_sum_to_pay['ride'] + expected_sum_to_pay['rebate'])
    else:
        assert (order_doc['payment_tech']['sum_to_pay']['ride'] ==
                expected_sum_to_pay['ride'])


@async.inline_callbacks
def _check_user_is_not_debtor(order_id):
    order_doc = yield db.orders.find_one({'_id': order_id})
    assert not order_doc['payment_tech'].get('debt')


@pytest.mark.parametrize('order_id,check_card_result', [
    ('order1', False),
    ('order1', True),
])
@pytest.mark.filldb(orders='check_card', order_proc='check_card',
                    user_phones='check_card')
@pytest.inline_callbacks
def test_check_card_task(order_id, check_card_result, patch, mock_send_event):
    class FakeCard(object):
        pass

    @patch('taxi.internal.order_kit.antifraud.check_card')
    @async.inline_callbacks
    def antifraud_check_card(card, order_doc, log_extra=None):
        yield
        async.return_value(check_card_result)

    @patch('taxi.internal.card_operations.get_card_from_db')
    @async.inline_callbacks
    def get_card_from_db(owner_uid, card_id):
        assert owner_uid == 'some_user_uid'
        assert card_id == 'card-some_card_id'
        yield
        async.return_value(FakeCard())

    yield invoice_handler._check_card._task_function(order_id)

    order_doc = yield db.orders.find_one({'_id': order_id})
    assert order_doc['payment_tech']['check_card_is_finished']
    assert order_doc['payment_tech']['type'] == 'card'
    if not check_card_result:
        order_proc_doc = yield db.order_proc.find_one({'_id': order_id})
        statistics = order_proc_doc['order_info']['statistics']
        assert statistics['status_updates'][0]['q'] == 'moved_to_cash'


@pytest.mark.now('2018-05-18 00:00:00.0')
@pytest.mark.parametrize(
    'order_id,number_of_send_payment_calls,expected_to_send',
    [
        (
            'order_without_experiment',
            1,
            {'updated': datetime.datetime(2018, 5, 18)},
        ),
        (
            'order_with_experiment',
            1,
            {'updated': datetime.datetime(2018, 5, 18)},
        ),
    ]
)
@pytest.mark.filldb(orders='experiment_disables_send_payment')
@pytest.inline_callbacks
def test_experiment_disables_send_payment(
        order_id, number_of_send_payment_calls, expected_to_send, patch):
    @patch('taxi.taxi_protocol.protocol_1x.client.send_payment')
    def send_payment(order_id, log_extra=None):
        yield
        async.return_value(None)

    order_doc = yield db.orders.find_one({'_id': order_id})
    yield invoice_handler._notify_on_payments(order_doc)
    assert len(send_payment.calls) == number_of_send_payment_calls
    to_send = order_doc['payment_tech']['notifications']['payment']['to_send']
    assert to_send == expected_to_send


@pytest.mark.parametrize('order_doc,expected_calls', [
    (
        {
            '_id': 'order1',
            'status': 'assigned',
            'taxi_status': 'driving'
        },
        []
    ),
    (
        {
            '_id': 'order1',
            'status': 'finished',
            'taxi_status': 'complete'
        },
        [
            {
                'args': ('order1',),
                'kwargs': {'intent': invoice_handler.INTENT_UPGRADE_TIPS_SUM, 'log_extra': None},
            }
        ]
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_upgrade_tips_sum(patch, order_doc, expected_calls):
    order_doc = dbh.orders.Doc(order_doc)

    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_doc, intent=None, log_extra=None):
        yield

    yield invoice_handler.upgrade_tips_sum(order_doc)
    assert update_transactions_call.calls == expected_calls


def _make_py2_history_item(compensation_ride_sum, full_ride_sum):
    return {
        'compensation_sum': {
            'ride': compensation_ride_sum
        },
        'created': datetime.datetime(2020, 1, 1),
        'decision': 'compensate_ride',
        'full_sum': {
            'ride': full_ride_sum,
        },
        'operator_login': 'test-operator',
        'otrs_ticket': 'otrs-123',
        'ticket_type': 'zendesk',
    }


def _make_transactions_history_item(
        compensation_ride_sum, full_ride_sum, acquiring_rate,
        gateway_name=None, pass_params=None,
):
    transactions_params = {
        'operation_id': 'compensation/create/abc',
        'gross_amount': str(full_ride_sum),
        'acquiring_rate': acquiring_rate,
        'product_id': 'taxi_100500_ride',
        'region_id': 225,
    }
    item = {
        'compensation_sum': {
            'ride': compensation_ride_sum
        },
        'created': datetime.datetime(2020, 1, 1),
        'decision': 'compensate_ride',
        'full_sum': {
            'ride': full_ride_sum,
        },
        'operator_login': 'test-operator',
        'otrs_ticket': 'otrs-123',
        'ticket_type': 'zendesk',
        'transactions_params': transactions_params,
    }
    if gateway_name is not None:
        transactions_params['gateway_name'] = gateway_name
    if pass_params is not None:
        transactions_params['pass_params'] = pass_params
    return item


@pytest.mark.parametrize(
    'order_id,summ,via_transactions,agent_compensations_via_tlog_enabled,'
    'expected_compensations,expected_history',
    [
        (  # -5% by contract
            'order-card',
            123,
            False,
            False,
            [
                {
                    'sum': {
                        'ride': 1168500,
                    },
                    'full_sum': {
                        'ride': 1230000,
                    },
                }
            ],
            [_make_py2_history_item(116.85, 123)],
        ),
        (  # -5% by contract, via transactions
            'order-card',
            123,
            True,
            False,
            [],
            [_make_transactions_history_item(116.85, 123, '0.05')],
        ),
        (  # fallback to settings.ACQUIRING_BANK
            'order-card-default-percent',
            123,
            False,
            False,
            [
                {
                    'sum': {
                        'ride': 1205400,
                    },
                    'full_sum': {
                        'ride': 1230000,
                    },
                }
            ],
            [_make_py2_history_item(120.54, 123)],
        ),
        (
            'order-corp',
            123,
            False,
            False,
            [
                {
                    'sum': {
                        'ride': 1230000,
                    },
                    'full_sum': {
                        'ride': 1230000,
                    },
                }
            ],
            [_make_py2_history_item(123, 123)],
        ),
        # agent compensations via tlog disabled: make trust compensation
        # via transactions
        (
            'order-agent',
            123,
            True,
            False,
            [],
            [_make_transactions_history_item(116.85, 123, '0.05')],
        ),
        # agent compensations via tlog ENABLED: make tlog compensation
        # via transactions
        (
            'order-agent',
            123,
            True,
            True,
            [],
            [
                _make_transactions_history_item(
                    116.85,
                    123,
                    '0.05',
                    gateway_name='tlog',
                    pass_params={
                        'agent_id': 'agent_gepard',
                    },
                ),
            ],
        ),
    ]
)
@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.filldb(
    orders='compensation',
    parks='compensation',
    cities='compensation',
)
@pytest.mark.load_data(
    countries='compensation',
)
@pytest.inline_callbacks
def test_save_ride_compensation(
        patch, order_id, summ, via_transactions,
        agent_compensations_via_tlog_enabled,
        expected_compensations, expected_history
):
    @patch('taxi.internal.order_kit.payment_handler.create_compensation_object')
    @async.inline_callbacks
    def create_compensation_object(
            order_doc, compensation_type, compensation_sum, log_extra=None):
        yield
        async.return_value({
            'sum': compensation_sum,
        })
    _patch_try_process_invoice(patch, via_transactions)
    _patch_uuid4(patch)

    yield config.BILLING_AGENT_COMPENSATIONS_VIA_TLOG_ENABLED.save(
        agent_compensations_via_tlog_enabled,
    )

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    net_sum, acquiring_percent = invoice_handler._get_net_compensation_sum(
        order_doc, summ,
    )
    assert acquiring_percent is not None

    yield invoice_handler._save_ride_compensation(
        order_doc=order_doc,
        summ=summ,
        net_sum=net_sum,
        acquiring_percent=acquiring_percent,
        operator_login='test-operator',
        otrs_ticket='otrs-123',
        ticket_type='zendesk'
    )

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    compensations = order_doc['billing_tech']['compensations']
    history = order_doc['payment_tech']['history']

    assert compensations == expected_compensations
    assert history == expected_history


@pytest.mark.config(BILLING_DEBT_FALLBACK_ENABLED=True)
@pytest.inline_callbacks
def test_update_transactions_iteration_billing_debt():
    yield invoice_handler._update_transactions_iteration(
        'order1', log_extra={'link': 'link1'}
    )
    transactions = yield db.pending_transactions.find().run()
    assert len(transactions) == 1
    assert transactions[0]['_id'] == 'order1'
    assert transactions[0]['log_extra']['link'] == 'link1'


def _patch_try_process_invoice(patch, via_transactions, invoice=None):
    @patch('taxi.internal.payment_kit.invoices.try_process_invoice')
    @async.inline_callbacks
    def try_process_invoice(payable_order, log_extra=None):
        async.return_value(invoices.Processing(via_transactions, invoice))
        yield


def _patch_uuid4(patch):
    class Mock(object):
        def __init__(self, hex):
            self.hex = hex

    @patch('uuid.uuid4')
    def uuid4():
        return Mock('abc')


@pytest.inline_callbacks
def test_payment_uid_is_valid():
    order_id = '87c60433929043a1bd46801637bd6699'
    order_doc = yield invoice_handler._get_order_doc(order_id)
    payable = payment_handler.PayableOrder(order_doc)
    payment_uid = yield payable.get_payment_uid()

    assert payment_uid == u'323193276'


@pytest.inline_callbacks
def test_PayableInvoice_get_payment_uid():
    pi = payment_handler.PayableInvoice(None)
    uid = yield pi.get_payment_uid()

    assert uid == billing.MISSING_UID_PARAM


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.parametrize('method,args,expected', [
    (invoice_handler._save_check_card_result, (False,), [
        {
            'status': 'success',
            'type': 'moved_to_cash_by_check_card',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'reason': {'code': 'NEED_CVN'},
                'from': {'type': 'card'}
            }
        }
    ]),
])
@pytest.mark.filldb(orders='payment_events')
@pytest.inline_callbacks
def test_payment_events_card(method, args, expected):
    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    yield method(order_doc, *args)

    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    assert order_doc.payment_events == expected


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.parametrize('method,args,expected', [
    (
        invoice_handler._switch_expired_order_back_to_card,
        ('operator', 'ticket', 'card',),
        [
            {
                'status': 'success',
                'type': 'expired_switched_to_card',
                'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
                'data': {
                    'to': {'type': 'card'},
                    'from': {'type': 'cash'}
                }
            }
        ]
    ),
    (invoice_handler._remember_need_cvn, (True,), [
        {
            'status': 'success',
            'type': 'remembered_cvn',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'reason': {'code': 'NEED_CVN'},
                'from': {'type': 'cash'}
            }
        }
    ]),
    (invoice_handler._remember_need_cvn, (False,), [
        {
            'status': 'success',
            'type': 'not_remembered_cvn',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'from': {'type': 'cash'}
            }
        }
    ])
])
@pytest.mark.filldb(orders='payment_events_not_finished')
@pytest.inline_callbacks
def test_payment_events_checks(method, args, expected, mock_send_event):
    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    yield method(order_doc, *args)

    order_doc = yield dbh.orders.Doc.find_one_by_id('540_1')
    assert order_doc.payment_events == expected


def test_switch_back_to_card():
    pass


@pytest.mark.now('2017-12-31 21:22:23')
@pytest.mark.parametrize('order_id,method,expected', [
    ('540_1', invoice_handler._close_with_cash, [
        {
            'status': 'success',
            'type': 'closed_with_cash',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'reason': {'code': 'ORDER_CANCELLED'},
                'from': {'type': 'card'}
            }
        }
    ]),
    ('540_1', invoice_handler._move_back_to_cash, [
        {
            'status': 'success',
            'type': 'moved_to_cash_by_update_transactions',
            'c': datetime.datetime(2017, 12, 31, 21, 22, 23),
            'data': {
                'to': {'type': 'cash'},
                'from': {'type': 'card'},
                'reason': {'code': 'NEED_CVN'},
            }
        }
    ]),
    ('paid_for_ride_order_id', invoice_handler._move_back_to_cash, []),
    ('paid_for_cashback_order_id', invoice_handler._move_back_to_cash, []),
])
@pytest.mark.filldb(orders='payment_events_card')
@pytest.inline_callbacks
def test_payment_event_cash(order_id, method, expected):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield method(order_doc)

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert list(order_doc.payment_events) == expected


@pytest.mark.filldb(orders='card_debt')
@pytest.mark.parametrize('order_id,should_mark_as_debt,'
                         'debt,skipped_debt', [
    ('no_debt', False, False, None),
    ('closed_debt', False, False, None),
    ('open_debt', True, True, None),
    ('tech_debt', False, False, ['59a30001b5a2d42a62df7ef8'])
])
@pytest.mark.parametrize('fix_logic_exp_enabled', (True, False))
@pytest.inline_callbacks
def test_mark_ride_as_debt(
        mock_fix_change_payment_in_py2_config,
        order_id,
        should_mark_as_debt,
        debt,
        skipped_debt,
        patch,
        fix_logic_exp_enabled,
):
    called = []
    called_phone = []
    called_device = []

    mock_fix_change_payment_in_py2_config(fix_logic_exp_enabled)

    @patch('taxi.internal.dbh.cardlocks.Doc.mark_unpaid')
    def test_mark_unpaid(order_id, persistent_id):
        called.append(order_id)

    @patch('taxi.internal.dbh.phonelocks.Doc.mark_unpaid')
    def test_mark_unpaid_phone(order_id, persistent_id):
        called_phone.append(order_id)

    @patch('taxi.internal.dbh.devicelocks.Doc.mark_unpaid')
    def test_mark_unpaid_device(order_id, persistent_id):
        called_device.append(order_id)

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    payment_fail = yield antifraud.PaymentFail.from_last_transaction(
        order_doc, None,
    )
    yield invoice_handler._mark_ride_as_debt(
        order_doc, payment_fail, log_extra=None
    )
    if should_mark_as_debt:
        assert called == called_phone == called_device == [order_id]
    else:
        assert called == called_phone == called_device == []

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order_doc['payment_tech']['debt'] == debt
    assert order_doc['payment_tech'].get('debt_skipped') == skipped_debt


@pytest.mark.filldb(orders='disp_cost', order_proc='disp_cost')
@pytest.inline_callbacks
def test_accept_disp_cost_after_moved_to_cash(patch):
    called = []

    @patch('taxi.internal.dbh.cardlocks.Doc.mark_unpaid')
    def test_mark_unpaid(order_id, persistent_id):
        called.append(order_id)

    @patch('taxi_stq.client.prepare_order_event')
    @async.inline_callbacks
    def prepare_order_event(order_id, order_version, event_type,
                            eta=0, reason=None, log_extra=None):
        yield

    order_id = 'cash_need_disp_accept'
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'need_disp_accept' in order_doc['payment_tech']
    version = order_doc['billing_tech']['version']

    yield invoice_handler.accept_disp_cost(
        order_id, 'decline_dispatch', version, 'vasya', '123', log_extra=None
    )

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'need_disp_accept' not in order_doc['payment_tech']
    assert order_doc['cost'] == 719.0
    assert order_doc['payment_tech']['sum_to_pay'] == {
        "ride": 0,
        "tips": 0
    }
    assert not order_doc['payment_tech']['debt']

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    assert proc.order.cost == 719.0


@pytest.mark.filldb(orders='set_tips_sum')
@pytest.mark.config(USE_TIPS_SERVICE=False)
@pytest.inline_callbacks
def test_tips_remote_disabled(patch):
    @patch('taxi.external.tips._perform_request')
    def patched_perform_request(*args, **kwargs):
        pass

    order_doc = yield dbh.orders.Doc.find_one_by_id('order_1_card')
    yield tips_handler.set_tips_sum(order_doc)
    yield tips_handler.need_hold_tips(order_doc)
    # both funcs exited early because USE_TIPS_SERVICE=False
    assert len(patched_perform_request.calls) == 0


@pytest.mark.filldb(orders='set_tips_sum')
@pytest.mark.config(USE_TIPS_SERVICE=True)
@pytest.inline_callbacks
def test_tips_remote_set_tips_sum(patch):
    order_id = 'order_1_card'

    @patch('taxi.external.tips.get_tips_sum')
    @async.inline_callbacks
    def patched_get_tips_sum(order_id_, log_extra=None):
        assert order_id == order_id_
        async.return_value(600000)
        yield

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield tips_handler.set_tips_sum(order_doc)
    assert len(patched_get_tips_sum.calls) == 1
    tips_sum = order_doc['payment_tech']['sum_to_pay']['tips']
    assert tips_sum == 600000


@pytest.mark.filldb(orders='need_hold_tips')
@pytest.mark.config(USE_TIPS_SERVICE=True)
@pytest.inline_callbacks
def test_tips_remote_need_hold_tips(patch):
    order_id = 'order_2_applepay'

    @patch('taxi.external.tips.need_hold_tips')
    @async.inline_callbacks
    def patched_need_hold_tips(order_id_, log_extra=None):
        assert order_id == order_id_
        async.return_value((True, 1234))
        yield

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    need_hold_tips, time_before_take_tips = yield tips_handler.need_hold_tips(
        order_doc,
    )
    assert len(patched_need_hold_tips.calls) == 1
    assert need_hold_tips
    assert time_before_take_tips == 1234


@pytest.mark.filldb(orders='disp_cost', order_proc='disp_cost')
@pytest.mark.parametrize('order_id, cost, driver_cost, sum_to_pay', [
    (
            'accept_driver_cost', 1600, 1600,
            {'ride': 16000000, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_coupon', 1600, 1600,
            {'ride': 13000000, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_coupon_bigger_than_cost', 1600, 1600,
            {'ride': 0, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_discounts', 899.8, 1000,
            {'ride': 8998000, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_discounts_and_surge', 949.8, 1050,
            {'ride': 9498000, 'tips': 0}
    )
])
@pytest.mark.config(
    SUBVENTIONS_DISCOUNT_LIMIT_FOR_ORDERS_AFTER='2000-01-01 00:00:00'
)
@pytest.inline_callbacks
def test_accept_disp_cost_driver(patch, order_id, cost,
                                        driver_cost, sum_to_pay):

    @patch('taxi.internal.dbh.cardlocks.Doc.mark_unpaid')
    def test_mark_unpaid(order_id, persistent_id):
        pass

    @patch('taxi_stq.client.prepare_order_event')
    @async.inline_callbacks
    def prepare_order_event(order_id, order_version, event_type,
                            eta=0, reason=None, log_extra=None):
        yield

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'need_disp_accept' in order_doc['payment_tech']
    version = order_doc['billing_tech']['version']

    yield invoice_handler.accept_disp_cost(
        order_id, 'accept_driver', version, 'vasya', '123', log_extra=None
    )

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'need_disp_accept' not in order_doc['payment_tech']
    assert order_doc['cost'] == cost
    assert order_doc['disp_cost']['driver_cost'] == driver_cost
    assert order_doc['payment_tech']['sum_to_pay'] == sum_to_pay


@pytest.mark.filldb(orders='disp_cost', order_proc='disp_cost')
@pytest.mark.parametrize('order_id, cost, new_cost, sum_to_pay', [
    (
            'accept_driver_cost', 1600, 1600,
            {'ride': 16000000, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_coupon', 1600, 1600,
            {'ride': 13000000, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_coupon_bigger_than_cost', 1600, 1600,
            {'ride': 0, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_discounts', 899.8, 1000,
            {'ride': 8998000, 'tips': 0}
    ),
    (
            'accept_driver_cost_with_order_cost_includes_coupon', 1600, 1600,
            {'ride': 13000000, 'tips': 0}
    ),
])
@pytest.mark.config(
    SUBVENTIONS_DISCOUNT_LIMIT_FOR_ORDERS_AFTER='2000-01-01 00:00:00'
)
@pytest.inline_callbacks
def test_new_disp_cost_driver(patch, order_id, cost, new_cost, sum_to_pay):

    @patch('taxi.internal.dbh.cardlocks.Doc.mark_unpaid')
    def test_mark_unpaid(*_):
        pass

    @patch('taxi_stq.client.prepare_order_event')
    @async.inline_callbacks
    def prepare_order_event(*_, **__):
        yield

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'need_disp_accept' in order_doc['payment_tech']
    version = order_doc['billing_tech']['version']

    yield invoice_handler.new_disp_cost(
        order_doc, new_cost, 'new_sum_driver', version, 'any_reason', 'vasya',
        '123', log_extra=None
    )

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'need_disp_accept' not in order_doc['payment_tech']
    assert order_doc['cost'] == cost
    assert order_doc['disp_cost']['driver_cost'] == new_cost
    assert order_doc['payment_tech']['sum_to_pay'] == sum_to_pay
    assert 'final_cost_meta' not in order_doc.get('current_prices', {})


@pytest.inline_callbacks
@pytest.mark.config(TAXIMETER_MANUAL_COST_ACCEPT_THRESHOLD={
    '__default__': 0,
    'moscow': 100
})
@pytest.mark.parametrize('order_doc, expected', [
    (
        {
            '_id': '1',
            'disp_cost': {
                'driver_cost': 300,
                'taximeter_cost': 150
            },
            'nz': 'moscow'
        },
        True
    ),
    (
        {
            '_id': '2',
            'disp_cost': {
                'driver_cost': 300,
                'taximeter_cost': 250
            },
            'nz': 'moscow'
        },
        False
    ),
    (
        {
            '_id': '3',
            'disp_cost': {
                'driver_cost': 300,
                'taximeter_cost': 250
            },
            'nz': 'spb'
        },
        True
    )
])
def test_need_disp_accept(order_doc, expected):
    result = yield invoice_handler._check_need_disp_accept(order_doc)
    assert result == expected


@pytest.mark.now('2017-12-31 05:00:00 +05')
@pytest.inline_callbacks
def test_handle_ratelimit_and_get_random_eta():
    timeout = (yield config.UPDATE_TRANSACTIONS_TIMEOUT.get())
    eta = invoice_handler._handle_ratelimit_and_get_random_eta(
        Exception(), timeout
    )
    min_eta = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=0.5 * timeout
    )
    assert eta >= min_eta


@pytest.mark.parametrize('update_set,expected,expected_reason', [
    ({'a': None}, (100500, decimal.Decimal('0.02'), 'USD'), None),
    (
        {
            'payment_tech.sum_to_pay.ride': 11000,
            'billing_contract': {
                'is_set': True,
                'acquiring_percent': '0.999',
            }
        },
        None,
        'Too small net compensation sum 0.0011',
    ),
    ({'payment_tech.type': 'cash'}, None, None),
    ({'payment_tech.type': 'corp'}, None, None),
    ({'payment_tech.finish_handled': False}, None, None),
    ({'payment_tech.debt': False}, None, None),
    ({'payment_tech.history': [{}]}, None, None),
    ({'billing_tech.compensations': [{}]}, None, None),
    ({'payment_tech.need_accept': True}, None, None),
    ({'payment_tech.need_disp_accept': True}, None, None),
    (
        {'performer.tariff.currency': 'RUB'},
        None,
        'Too big compensation sum, limit 100000, sum 100500',
    ),
    (
        {'performer.tariff': {}},
        None,
        'Too big compensation sum, limit 100000, sum 100500',
    ),
    ({'billing_contract': {}}, None, None),
    ({'billing_contract': {'is_set': True}}, None, None),
    (
        {'status_updated': datetime.datetime(2017, 9, 8)},
        (100500, decimal.Decimal('0.02'), 'USD'),
        None,
    ),
])
@pytest.mark.now('2017-09-10T10:00:00.0')
@pytest.mark.filldb(orders='auto_compensations')
@pytest.inline_callbacks
def test_get_auto_compensation_sum(update_set, expected, expected_reason):
    yield config.AUTO_COMPENSATION_MAX_SUM.save({
        '__default__': 10,
        'USD': 20,
    })
    order_doc = yield db.orders.find_and_modify(
        {'_id': 'order_id'},
        {'$set': update_set},
        new=True,
    )
    result = yield invoice_handler._get_auto_compensation_sum(order_doc)
    actual_reason = order_doc.get('payment_tech', {}).get(
        'no_auto_compensation_reason',
    )
    assert result == expected
    assert actual_reason == expected_reason


@pytest.mark.filldb(orders='auto_compensations')
@pytest.inline_callbacks
def test_auto_compensation_eta():
    order_doc = yield db.orders.find_one('order_id')
    eta = yield invoice_handler._auto_compensation_eta(order_doc)
    assert eta == datetime.datetime(2017, 9, 10, 9)


@pytest.mark.filldb(orders='auto_compensations')
@pytest.inline_callbacks
def test_auto_compensation_eta_delayed():
    order_doc = yield db.orders.find_one('order_id_delayed')
    eta = yield invoice_handler._auto_compensation_eta(order_doc)
    assert eta == datetime.datetime(2017, 9, 10, 9)

    order_doc['status_change_positions'].pop(-1)
    eta = yield invoice_handler._auto_compensation_eta(order_doc)
    assert eta == datetime.datetime(2017, 9, 10, 9, 10)


@pytest.mark.filldb(orders='auto_compensations')
@pytest.mark.now('2017-09-10T10:00:00.0')
@pytest.inline_callbacks
def test_auto_compensations(patch):
    @patch('taxi.internal.order_kit.invoice_handler._auto_compensation_task.call')
    def call(*args, **kwargs):
        pass

    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(*args, **kwargs):
        assert not args
        assert kwargs == {
            'payable': payable,
            'processing': processing,
            'log_extra': None,
        }
        yield

    yield config.AUTO_COMPENSATION_MAX_SUM.save({
        '__default__': 10,
        'USD': 20,
    })
    order_doc = yield db.orders.find_one('order_id')
    payable = payment_handler.PayableOrder(order_doc)
    processing = invoices.processing_via_py2()
    yield invoice_handler._auto_compensation(
        order_doc, payable, processing, False)
    assert call.calls == [{'args': ('order_id',), 'kwargs': {'log_extra': None}}]
    assert try_fill_service_orders.calls == []

    yield invoice_handler._auto_compensation(
        order_doc, payable, processing, True)
    assert call.calls == [{'args': ('order_id',), 'kwargs': {'log_extra': None}}]
    assert len(try_fill_service_orders.calls) == 1

    order2 = copy.deepcopy(order_doc)
    order2['status_updated'] = datetime.datetime(2017, 9, 9)
    yield invoice_handler._auto_compensation(order2, payable, processing, False)
    order3 = copy.deepcopy(order_doc)
    order3['payment_tech']['debt'] = False
    yield invoice_handler._auto_compensation(order3, payable, processing, False)
    assert call.calls == []
    yield invoice_handler._auto_compensation(order_doc, payable, processing, False)
    assert call.calls != []
    yield config.AUTO_COMPENSATION_INSTANT_SETTINGS.save(
        {
            'enable': True,
            'unique_drivers_find': True,
            'time_limit': 100000000,
            'tariff_zones': {
                'msk': 510,
            },
            'payment_types': [
                'card'
            ]
        }
    )
    order4 = copy.deepcopy(order_doc)
    yield invoice_handler._auto_compensation(order4, payable, processing, False)
    assert call.calls != []


@pytest.mark.parametrize('dbid_uuid,expected,db_request', [
    (('dbid_1', 'uuid1'), bson.ObjectId('000000000000000000000001'), True),
    (('dbid_1', 'uuid1'), None, False),
    (('dbid_2', 'uuid2'), None, True),
])
@pytest.mark.filldb(orders='auto_compensations')
@pytest.inline_callbacks
def test_get_driver_udid(dbid_uuid, db_request, expected, patch):

    @patch('taxi.external.unique_drivers.get_unique_driver_id')
    @async.inline_callbacks
    def get_unique_driver_id(db, uuid, src_service_tvm_name, consumer=None,
                             log_extra=None):
        assert (db, uuid) == dbid_uuid
        yield async.return_value(expected)

    yield config.AUTO_COMPENSATION_INSTANT_SETTINGS.save({
        'unique_drivers_find': db_request
    })
    order = yield db.orders.find_one('order_id')
    order['performer']['db_id'], order['performer']['uuid'] = dbid_uuid
    udid = yield invoice_handler._get_driver_udid(order)
    assert udid == expected


@pytest.mark.filldb(orders='auto_compensations', auto_compensations='instant')
@pytest.mark.now('2017-09-7T10:00:00.0')
@pytest.inline_callbacks
def test_instant_auto_compensations(patch):
    @patch('taxi.internal.order_kit.invoice_handler.'
           '_auto_compensation_task.call_later')
    def call(*args, **kwargs):
        pass

    @patch('taxi.external.unique_drivers.get_unique_driver_id')
    @async.inline_callbacks
    def get_unique_driver_id(db, uuid, src_service_tvm_name, consumer=None,
                             log_extra=None):
        udid_by_uuid = {
            'test_uuid': bson.ObjectId('000000000000000000000001'),
            'test_uuid2': bson.ObjectId('000000000000000000000001'),
            'test_uuid3': bson.ObjectId('000000000000000000000002'),
        }
        yield async.return_value(udid_by_uuid.get(uuid))

    yield config.AUTO_COMPENSATION_MAX_SUM.save({
        '__default__': 100,
        'USD': 25,
    })
    yield config.AUTO_COMPENSATION_INSTANT_SETTINGS.save(
        {
            'enable': True,
            'unique_drivers_find': True,
            'time_limit': 1000000,
            'tariff_zones': {
                'msk': 515,
                'small_zone': 5,
            },
            'payment_types': [
                'card'
            ]
        }
    )
    order_doc = yield invoice_handler._get_order_doc('order_id')
    payable = payment_handler.PayableOrder(order_doc)
    processing = invoices.processing_via_py2()
    yield invoice_handler._auto_compensation(order_doc, payable, processing, False)
    assert call.calls != []

    order_wrong_payment_type = copy.deepcopy(order_doc)
    order_wrong_payment_type['payment_tech']['type'] = 'applepay'
    yield invoice_handler._auto_compensation(
        order_wrong_payment_type, payable, processing, False)
    assert (
        order_wrong_payment_type.get('payment_tech').get('no_instant_compensation_reason')
        == 'The payment method is not supported: applepay')
    assert call.calls == []

    order_wrong_nearest_zone = copy.deepcopy(order_doc)
    order_wrong_nearest_zone.nearest_zone = 'tula'
    yield invoice_handler._auto_compensation(
        order_wrong_nearest_zone, payable, processing, False)
    assert (
        order_wrong_nearest_zone.get('payment_tech').get('no_instant_compensation_reason')
        == 'Disabled in zone: tula')
    assert call.calls == []

    order_wrong_limit_exceed = copy.deepcopy(order_doc)
    order_wrong_limit_exceed['payment_tech']['sum_to_pay']['ride'] = 200500
    yield invoice_handler._auto_compensation(
        order_wrong_limit_exceed, payable, processing, False)
    assert (
        order_wrong_limit_exceed.get('payment_tech').get('no_instant_compensation_reason')
        == 'Allowable limit exceeded in zone: msk, limit 5150000, sum 200500, total 5000000')
    assert call.calls == []

    order_wrong_zone_limit_exceed = copy.deepcopy(order_doc)
    order_wrong_zone_limit_exceed.nearest_zone = 'small_zone'
    order_wrong_zone_limit_exceed['payment_tech']['sum_to_pay']['ride'] = 200500
    yield invoice_handler._auto_compensation(
        order_wrong_zone_limit_exceed, payable, processing, False)
    assert (
        order_wrong_zone_limit_exceed.get('payment_tech').get('no_instant_compensation_reason')
        == 'Allowable limit exceeded in zone: small_zone, limit 50000, sum 200500')
    assert call.calls == []

    order_wrong_driver_id = copy.deepcopy(order_doc)
    order_wrong_driver_id['performer'].pop('db_id', None)
    order_wrong_driver_id['performer'].pop('uuid', None)
    yield invoice_handler._auto_compensation(
        order_wrong_driver_id, payable, processing, False)
    assert (
        order_wrong_driver_id.get('payment_tech').get('no_instant_compensation_reason')
        == 'No unique driver id')
    assert call.calls == []

    order_wrong_compensation_limit_exceed = copy.deepcopy(order_doc)
    order_wrong_compensation_limit_exceed['payment_tech']['sum_to_pay']['ride'] = 10000000
    yield invoice_handler._auto_compensation(
        order_wrong_compensation_limit_exceed, payable, processing, False
    )
    assert (
        order_wrong_compensation_limit_exceed.get('payment_tech').get('no_auto_compensation_reason')
        == 'Too big compensation sum, limit 250000, sum 10000000')
    assert call.calls == []

    order_another_profile = copy.deepcopy(order_doc)
    order_another_profile['performer']['uuid'] = 'test_uuid2'
    order_another_profile['payment_tech']['sum_to_pay']['ride'] = 200500
    yield invoice_handler._auto_compensation(
        order_another_profile, payable, processing, False)
    assert call.calls == []

    order_another_driver = copy.deepcopy(order_doc)
    order_another_driver['performer']['uuid'] = 'test_uuid3'
    order_another_driver['payment_tech']['sum_to_pay']['ride'] = 200500
    yield invoice_handler._auto_compensation(
        order_another_driver, payable, processing, False)
    assert call.calls != []


@pytest.mark.parametrize('delay_sec', [
    0,
    20,
    123
])
@pytest.mark.filldb(orders='auto_compensations', auto_compensations='instant')
@pytest.mark.now('2017-09-7T10:00:00.0')
@pytest.inline_callbacks
def test_instant_auto_compensation_delay(patch, delay_sec):
    @patch('taxi.internal.order_kit.invoice_handler.'
           '_auto_compensation_task.call_later')
    def call(*args, **kwargs):
        assert args[0] == delay_sec
        pass

    @patch('taxi.external.unique_drivers.get_unique_driver_id')
    @async.inline_callbacks
    def get_unique_driver_id(db, uuid, src_service_tvm_name, consumer=None,
                             log_extra=None):
        yield async.return_value(bson.ObjectId('000000000000000000000001'))

    yield config.AUTO_COMPENSATION_MAX_SUM.save({
        '__default__': 100,
        'USD': 25,
    })
    yield config.AUTO_COMPENSATION_INSTANT_SETTINGS.save(
        {
            'enable': True,
            'unique_drivers_find': True,
            'time_limit': 1000000,
            'tariff_zones': {
                'msk': 515,
                'small_zone': 5,
            },
            'payment_types': [
                'card'
            ],
            'delay': delay_sec,
        }
    )
    order_doc = yield invoice_handler._get_order_doc('order_id')
    payable = payment_handler.PayableOrder(order_doc)
    processing = invoices.processing_via_py2()
    yield invoice_handler._auto_compensation(
        order_doc, payable, processing, False)
    assert call.calls != []


@pytest.mark.parametrize(
    'via_transactions,expected_compensations,expected_history', [
        (
            False,
            [
                {
                    'compensation_made_at': None,
                    'created': datetime.datetime(2017, 9, 10, 10),
                    'updated': datetime.datetime(2017, 9, 10, 10),
                    'type': 'compensation',
                    'status': 'compensation_init',
                    'sum': {'ride': 98490},
                    'terminal_id': None,
                    'refunds': [],
                    'full_sum': {'ride': 100500},
                    'trust_payment_id': 'tpi',
                    'owner_uid': 'yandex_uid',
                    'billing_response': None,
                }
            ],
            [
                {
                    'created': datetime.datetime(2017, 9, 10, 10),
                    'operator_login': '-',
                    'otrs_ticket': '-',
                    'decision': 'compensate_ride',
                    'compensation_sum': {'ride': 9.85},
                    'full_sum': {'ride': 10.05},
                }
            ]
        ),
        (
            True,
            [],
            [
                {
                    'created': datetime.datetime(2017, 9, 10, 10),
                    'operator_login': '-',
                    'otrs_ticket': '-',
                    'decision': 'compensate_ride',
                    'compensation_sum': {'ride': 9.85},
                    'full_sum': {'ride': 10.05},
                    'transactions_params': {
                        'operation_id': 'compensation/create/autocompensation',
                        'gross_amount': '10.05',
                        'acquiring_rate': '0.02',
                        'product_id': 'taxi_100500_ride',
                        'region_id': 225,
                    }
                }
            ]
        ),
    ]
)
@pytest.mark.now('2017-09-10T10:00:00.0')
@pytest.mark.filldb(
    orders='auto_compensations',
    parks='auto_compensations',
    cities='auto_compensations',
)
@pytest.mark.load_data(
    countries='auto_compensations',
)
@pytest.inline_callbacks
def test_auto_compensations_task(
        patch, via_transactions, expected_compensations, expected_history
):

    _patch_try_process_invoice(patch, via_transactions)

    @patch('taxi.external.billing._call_simple')
    def _call_simple(*args, **kwargs):
        return {
            'status': 'success',
            'trust_payment_id': 'tpi',
        }

    @patch('taxi.external.unique_drivers.get_unique_driver_id')
    @async.inline_callbacks
    def get_unique_driver_id(db, uuid, src_service_tvm_name, consumer=None,
                             log_extra=None):
        yield async.return_value(bson.ObjectId('000000000000000000000001'))

    now = datetime.datetime.utcnow()
    yield config.AUTO_COMPENSATION_MAX_SUM.save({
        '__default__': 10,
        'USD': 20,
    })
    yield config.AUTO_COMPENSATION_INSTANT_SETTINGS.save({
        'unique_drivers_find': True
    })

    yield db.orders.update({}, {'$set': {'payment_tech.debt': False}})
    yield invoice_handler._auto_compensation_task(
        'order_id', None, 'order_id', __stq_exec_tries=0,
    )
    order_doc = yield db.orders.find_one('order_id')
    assert order_doc['billing_tech'].get('compensations', []) == []
    compensations = yield db.auto_compensations.find().run()
    assert compensations == []

    yield db.orders.update({}, {'$set': {'payment_tech.debt': True}})
    yield invoice_handler._auto_compensation_task(
        'order_id', None, 'order_id', __stq_exec_tries=0,
    )
    order_doc = yield db.orders.find_one('order_id')
    assert order_doc['billing_tech']['version'] == 2
    actual_compensations = order_doc['billing_tech'].get('compensations')
    assert actual_compensations == expected_compensations
    assert order_doc['payment_tech'].get('history') == expected_history
    assert order_doc['payment_tech'].get('was_auto_compensated') is True
    compensations = yield db.auto_compensations.find().run()
    expected_compensations = [{
        '_id': 'order_id',
        'created': datetime.datetime(2017, 9, 7, 8),
        'nearest_zone': 'msk',
        'unique_driver_id': bson.ObjectId('000000000000000000000001'),
        'clid': '100500',
        'compensation': 9.85,
        'full_compensation': 10.05,
        'currency': 'USD',
        'updated': now,
    }]
    assert compensations == expected_compensations
    yield invoice_handler._auto_compensation_task(
        'order_id', None, 'order_id', __stq_exec_tries=0,
    )
    compensations = yield db.auto_compensations.find().run()
    assert len(compensations) == 1
    yield db.auto_compensations.remove()
    yield invoice_handler._auto_compensation_task(
        'order_id', None, 'order_id', __stq_exec_tries=0,
    )
    compensations = yield db.auto_compensations.find().run()
    assert compensations == expected_compensations


@pytest.mark.parametrize('sources,include_card', [
    (['card'], True),
    (['card'], False),
    (['phone'], True),
    (['device'], True),
    (['card', 'phone', 'device'], True),
    (['card', 'phone', 'device'], False),
])
@pytest.mark.filldb(order_proc='antifraud_failure')
@pytest.inline_callbacks
def test_broadcast_antifraud_failure(sources, include_card, mock_send_event):
    yield config.RELATED_ORDERS_CLASSES.save(sources)
    yield config.RELATED_ORDERS_CLASSES.get_fresh()
    order_doc = {
        '_id': 'order_id',
        'user_id': 'user_id',
        'user_phone_id': 'phone_id',
        'payment_tech': {}
    }
    if include_card:
        order_doc['payment_tech']['main_card_persistent_id'] = 'card_id'

    yield invoice_handler._broadcast_payment_failure(
        order_doc, 'some-decision-id', log_extra=None
    )
    for source in ['card', 'phone', 'device', 'id']:
        proc = yield dbh.order_proc.Doc.find_one_by_id('order_%s' % source)
        if source in sources and (source != 'card' or include_card):
            update = proc.order_info.statistics.status_updates[-1]
            assert update.reason_code == 'related_moved_to_cash'
            assert update.reason_arg == {
                'decision_id': 'some-decision-id',
                'source_order_id': 'order_id'
            }
        else:
            assert not proc.order_info.statistics.status_updates


@pytest.mark.parametrize(('order_id,compensation_sum,exception_cls,'
                          'ignore_max_sum, use_configurable_limit, update_configurable_limit'), [
    (
        'order_with_previous_compensation',
        109,
        None,
        False,
        False,
        None
    ),
    (
        'order_with_previous_compensation',
        1950,
        None,
        False,
        False,
        None
    ),
    (
        'order_with_previous_compensation',
        2000,
        exceptions.InvalidCompensationSumError,
        False,
        False,
        None
    ),
    (
        'order_with_two_compensations',
        100,
        exceptions.TooManyCompensationsError,
        False,
        False,
        None
    ),
    (
        'order_with_failed_compensations',
        100,
        None,
        False,
        False,
        None
    ),
    (
        'order_with_previous_compensation',
        2000,
        None,
        True,
        False,
        None
    ),
    # summ > max_total_sum - compensated, summ < ADMIN_PAYMENTS_MAX_MANUAL_CHARGE - compensated
    (
        'order_with_previous_compensation',
        2000,
        None,
        False,
        True,
        None
    ),
    # summ > max_total_sum - compensated, summ > ADMIN_PAYMENTS_MAX_MANUAL_CHARGE - compensated
    (
        'order_with_previous_compensation',
        24951,
        exceptions.CompensationSumGreaterLimitError,
        False,
        True,
        None
    ),
    # summ > max_total_sum - compensated, summ > ADMIN_PAYMENTS_MAX_MANUAL_CHARGE - compensated, ignore_limit
    (
        'order_with_previous_compensation',
        24951,
        None,
        True,
        True,
        None
    ),
    # summ < max_total_sum - compensated, summ > ADMIN_PAYMENTS_MAX_MANUAL_CHARGE - compensated
    (
        'order_with_previous_compensation',
        951,
        exceptions.CompensationSumGreaterLimitError,
        False,
        True,
        {'RUB': 1000}
    ),
    # summ < max_total_sum - compensated, summ > ADMIN_PAYMENTS_MAX_MANUAL_CHARGE - compensated, ignore_limit
    (
        'order_with_previous_compensation',
        951,
        None,
        True,
        True,
        {'RUB': 1000}
    ),
    # summ < max_total_sum - compensated, ADMIN_PAYMENTS_MAX_MANUAL_CHARGE not set for RUB
    (
        'order_with_previous_compensation',
        1950,
        None,
        False,
        True,
        {'RUB': None}
    ),
    # summ > max_total_sum - compensated, ADMIN_PAYMENTS_MAX_MANUAL_CHARGE not set for RUB
    (
        'order_with_previous_compensation',
        2000,
        exceptions.MaxManualChargeNotSetError,
        False,
        True,
        {'RUB': None}
    ),
    # summ > max_total_sum - compensated, ADMIN_PAYMENTS_MAX_MANUAL_CHARGE not set for RUB, ignore_limit
    (
        'order_with_previous_compensation',
        1951,
        None,
        True,
        True,
        {'RUB': None}
    )
])
@pytest.mark.filldb(
    orders='test_compensate_ride',
    cities='test_compensate_ride',
)
@pytest.mark.config(
    BILLING_MAX_NUMBER_OF_COMPENSATIONS=2,
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=False
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_compensate_ride(patch, order_id, compensation_sum, exception_cls,
                         ignore_max_sum, use_configurable_limit, update_configurable_limit):
    yield _impl_test_compensate_ride(
        patch, order_id, compensation_sum, exception_cls, ignore_max_sum, use_configurable_limit,
        update_configurable_limit
    )


@pytest.mark.parametrize(('order_id,compensation_sum,exception_cls,'
                         'ignore_max_sum'), [
    (
        'order_with_previous_compensation',
        950,
        None,
        False
    ),
    (
        'order_with_previous_compensation',
        1000,
        exceptions.InvalidCompensationSumError,
        False
    )
])
@pytest.mark.filldb(
    orders='test_compensate_ride',
    cities='test_compensate_ride',
)
@pytest.mark.config(
    BILLING_MAX_NUMBER_OF_COMPENSATIONS=2,
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_compensate_from_tariffs(patch, order_id, compensation_sum,
                                 exception_cls, ignore_max_sum):
    yield _impl_test_compensate_ride(
        patch, order_id, compensation_sum, exception_cls, ignore_max_sum, False, None
    )


@async.inline_callbacks
def _impl_test_compensate_ride(
        patch, order_id, compensation_sum, exception_cls, ignore_max_sum, use_configurable_limit,
        update_configurable_limit):
    _patch_try_process_invoice(patch, False)

    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_doc, intent=None, log_extra=None):
        yield

    @async.inline_callbacks
    def _get_billing_version(order_id):
        order = yield db.orders.find_one({'_id': order_id})
        async.return_value(order['billing_tech']['version'])

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield async.return_value('trust_payment_id')

    if update_configurable_limit:
        yield config.ADMIN_PAYMENTS_MAX_MANUAL_CHARGE.save(update_configurable_limit)
    billing_version = yield _get_billing_version(order_id)
    args = (order_id, compensation_sum, billing_version,
            'foobar', '1337', None, ignore_max_sum, use_configurable_limit)
    if exception_cls is not None:
        with pytest.raises(exception_cls):
            yield invoice_handler.compensate_ride(*args)
    else:
        yield invoice_handler.compensate_ride(*args)


@pytest.mark.parametrize('order_id,exception_cls', [
    ('540_1', None),
    ('540_2', exceptions.RaceConditionError),
    ('540_3', exceptions.OrderNotFoundError),
])
@pytest.mark.filldb(orders='test_mark_paid_by_cash')
@pytest.inline_callbacks
def test_mark_paid_by_cash(order_id, exception_cls, patch, mock_send_event):
    args = (order_id, 'operator_login', 'otrs_ticket')
    if exception_cls is not None:
        with pytest.raises(exception_cls):
            yield invoice_handler.mark_paid_by_cash(*args)
    else:
        yield invoice_handler.mark_paid_by_cash(*args)


def _patch_internal_functions(patch):
    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(*args, **kwargs):
        yield

    # billing._call_simple will return something like
    # {'status': 'error', 'status_code': 'invalid_payment_method'}
    # this catches in billing._check_card_bound and
    # raises billing.CardUnboundError exception
    # function below internally calls billing._call_simple,
    # so we can simulate throwing exception
    @patch('taxi.internal.order_kit.invoice_handler._update_transactions_dirty')
    @async.inline_callbacks
    def _update_transactions_dirty(*args, **kwargs):
        yield
        raise billing.CardUnboundError('bad response', 'some trust id')


@contextlib.contextmanager
def _check_flag_changed(order_id):
    order_doc = db.orders.find_one(order_id).result
    old_status = order_doc['payment_tech']['hold_initiated']
    assert old_status

    yield

    order_doc = db.orders.find_one(order_id).result
    new_status = order_doc['payment_tech']['hold_initiated']
    assert not new_status
    assert old_status != new_status


@pytest.mark.skipif(True, reason=
                    'fails after removing orderlocks_2. see TAXIBACKEND-18014')
@pytest.mark.parametrize('order_id', [
    '540_5'
])
@pytest.inline_callbacks
def test_hold_initiated_flag_on_card_unhold__update_transactions_iteration(
        patch, order_id
):
    _patch_internal_functions(patch)
    with _check_flag_changed(order_id):
        yield invoice_handler.update_transactions_iteration(order_id)


@pytest.mark.skipif(True, reason=
                    'fails after removing orderlocks_2. see TAXIBACKEND-18014')
@pytest.mark.parametrize('order_id', [
    '540_5'
])
@pytest.inline_callbacks
def test_hold_initiated_flag_on_card_unhold__update_donation_transactions(
        patch, order_id
):
    _patch_internal_functions(patch)
    with _check_flag_changed(order_id):
        order_doc = yield db.orders.find_one(order_id)
        payable = payment_handler.PayableOrder(order_doc)
        yield invoice_handler.update_donation_transactions(payable)


def test_random_delay(patch):
    @patch('random.random')
    def random():
        return 0.3  # fairly random
    assert 8 == invoice_handler._randomize_delay(10)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('fail_count, min_interval, max_interval, expected', [
    (0, 1, 10, 1),
    (1, 1, 10, 2),
    (2, 1, 10, 4),
    (3, 1, 10, 8),
    (5, 1, 10, 10),
    (5, 1, 10, 10),
    (100, 1, 10, 10)
])
def test_calculate_exp_delay(fail_count, min_interval, max_interval, expected):
    result = invoice_handler._calc_exp_backoff_delay(
        fail_count,
        min_interval,
        max_interval
    )
    assert result == expected


@pytest.inline_callbacks
def test_increase_fail_count():
    order_doc = yield db.orders.find_one('540_6')
    fail_count = yield invoice_handler._get_and_increase_fail_count(order_doc)
    assert fail_count == 0
    fail_count = yield invoice_handler._get_and_increase_fail_count(order_doc)
    assert fail_count == 1


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.config(
    UPDATE_TRANSACTIONS_USE_EXP_BACKOFF=True,
    UPDATE_TRANSACTIONS_MIN_RETRY_INTERVAL=1,
    UPDATE_TRANSACTIONS_MAX_RETRY_INTERVAL=6,
    )
@pytest.mark.parametrize('order_id, expected_delays', [
    ('540_6', [1, 2, 4, 6, 6, 6])
])
@pytest.inline_callbacks
def test_expbackoff_update_transactions_iteration(patch, order_id, expected_delays):
    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(*args, **kwargs):
        yield

    @patch('taxi.internal.order_kit.invoice_handler._update_transactions_dirty')
    @async.inline_callbacks
    def _update_transactions_dirty_timeout(*args, **kwargs):
        yield
        raise billing.TimeoutError()

    @patch('taxi_stq.client.update_transactions_call_later')
    def update_transactions_call_later(eta, order_id, intent=None, log_extra=None):
        pass

    @patch('random.random')
    def random():
        return 0.5  # fairly random

    #  test billing timeouts and etas
    for i, delay in enumerate(expected_delays, 1):
        yield invoice_handler.update_transactions_iteration(order_id)
        order_doc = yield db.orders.find_one(order_id)
        assert order_doc['billing_tech']['fail_count'] == i
        expected_eta = (datetime.datetime.now() +
                        datetime.timedelta(seconds=delay))

        call, = update_transactions_call_later.calls
        assert call['eta'] == expected_eta, 'fail on %d iteration' % i
        assert call['order_id'] == '540_6'

    # now test that fail_count is dropped and eta is NOW

    @patch('taxi.internal.order_kit.invoice_handler._update_transactions_dirty')
    @async.inline_callbacks
    def _update_transactions_dirty_success(
            payable, processing, lazy_create_order, **kwargs
    ):
        yield payable.commit_payments()
        async.return_value(True)

    yield invoice_handler.update_transactions_iteration(order_id)
    order_doc = yield db.orders.find_one(order_id)
    assert 'fail_count' not in order_doc['billing_tech']

    call, = update_transactions_call_later.calls
    assert call['eta'] == 0
    assert call['order_id'] == '540_6'


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.filldb()
@pytest.mark.parametrize('payment_type', [
        dbh.orders.PAYMENT_TYPE_CARD,
        dbh.orders.PAYMENT_TYPE_CORP,
        dbh.orders.PAYMENT_TYPE_APPLE,
        dbh.orders.PAYMENT_TYPE_GOOGLE
])
@pytest.mark.parametrize('status', ['pending', 'assigned'])
@pytest.inline_callbacks
def test_notify_client_on_antifraud_stop_procedure(patch, payment_type, status):
    # check client gets notification if payment was stoped by antifraud:
    # in cases when order was moved to cash or when debt was allowed.
    # In normal flow this happens in functions:
    #     invoice_handler._update_transactions_iteration
    #     invoice_handler._do_antifraud_proc

    @patch('taxi.internal.dbh.order_proc.Doc.enqueue_on_moved_to_cash')
    @async.inline_callbacks
    def enqueue_on_moved_to_cash(*args, **kwargs):
        yield

    update_set = {
        'payment_tech.type': payment_type,
        'payment_tech.antifraud_finished': False,
        'status': status,
        'taxi_status': 'transporting'
    }

    order_doc = yield db.orders.find_and_modify(
        {'_id': 'stop_procedure_test'},
        {'$set': update_set},
        new=True,
    )
    yield antifraud.stop_procedure_and_move_to_cash(order_doc)

    order_doc = yield db.orders.find_one({'_id': 'stop_procedure_test'})
    # notify conditions
    assert order_doc['payment_tech']['antifraud_finished'] is True
    assert (order_doc['payment_tech']['antifraud_stop_reason'] ==
            antifraud.ANTIFRAUD_STATUS_PAYMENT_FAIL)

    yield invoice_handler._notify_client(order_doc)

    order_doc = yield db.orders.find_one({'_id': 'stop_procedure_test'})
    assert (order_doc['client_notifications']['moved_to_cash']['sent'] ==
            datetime.datetime.utcnow())


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_billing_timeouts(patch, mock):

    @patch('taxi.external.billing._call_xmlrpc_async')
    def _call_xmlrpc_async(*args, **kwargs):
        deferred = async.Deferred()
        deferred.addErrback(twisty_helpers.substitute_errors, billing._ERRMAP)
        deferred.errback(error.ConnectError())
        return deferred

    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(*args, **kwargs):
        yield

    @patch('taxi_stq.client.update_transactions_call_later')
    def update_transactions_call_later(eta, order_id, intent=None, log_extra=None):
        pass

    yield invoice_handler._update_transactions_iteration('540_7')
    call = update_transactions_call_later.call
    assert call['order_id'] == '540_7'


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.inline_callbacks
def test_update_transactions_invalid_payment_method(patch):
    order_id = 'invalid_pm_1'

    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(*args, **kwargs):
        yield

    @patch('taxi.internal.order_kit.invoice_handler._calc_next_update_eta')
    @async.inline_callbacks
    def calc_next_update_eta(
            payable, processing, feedback_context, log_extra=None
    ):
        yield
        assert payment_handler.invalid_payment_method(payable.order_doc)

    yield invoice_handler.update_transactions_iteration(order_id)
    order_doc = yield db.orders.find_one(order_id)
    assert 'fail_count' not in order_doc['billing_tech']

    assert len(calc_next_update_eta.calls) == 1


@pytest.mark.filldb(orders='invalid_payment')
@pytest.mark.parametrize('order_id, expected_payment_invalid', [
    ('coop', 'account-card'),
    ('card', 'any-card'),
])
@pytest.inline_callbacks
def test_mark_main_card_as_unusable(patch, order_id, expected_payment_invalid):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        assert 'yandex_uid' in args[0].to_dict()
        async.return_value(coop_client.PaymentResponse(
            '123', 'account-card', 'billing_id', 'persistent_id',
        ))

    order_doc = yield db.orders.find_one(order_id)

    payable = payment_handler.PayableOrder(order_doc)
    if payable.is_paid_by_coop_account:
        payable = coop.PayableOrderCoop(order_doc)
        yield payable.init_payment()

    yield invoice_handler._mark_main_card_as_unusable(
        order_doc, payable.payment_method_id
    )

    order_doc = yield db.orders.find_one(order_id)

    invalid_payment = order_doc['billing_tech']['invalid_payment_methods'][0]
    assert invalid_payment['payment_id'] == expected_payment_invalid

    payment_id = None
    if payable.is_paid_by_coop_account:
        payment_id = expected_payment_invalid
    assert payment_handler.invalid_payment_method(
        order_doc, payment_id=payment_id
    )


@pytest.mark.config(
    TRACK_ORDER_COST_RETURN_VALUE='taximeter_track_cost',
    MAX_TRACK_COST_DIFF=0.5,
    MIN_PRICE_FOR_COST_DIFF={
        'RUB': 200
    },
)
@pytest.mark.parametrize('taximeter_track_cost, taximeter_cost, expected', [
    (100, 100, False),
    (300, 300, False),
    (199, 1, False),
    (100, 201, True),
    (10, 199, False)
])
@pytest.inline_callbacks
def test_taximeter_and_backend_cost_diff(taximeter_track_cost, taximeter_cost,
                                         expected):
    proc = {
        'order': {
            'track_costs': {
                'taximeter_cost': float(taximeter_cost),
                'taximeter_track_cost': float(taximeter_track_cost)
            },
            'performer': {
                'tariff': {
                    'currency': 'RUB'
                }
            }
        }
    }
    proc_doc = dbh.order_proc.Doc(proc)
    res = yield invoice_handler._is_big_cost_diff(proc_doc)
    assert res == expected


@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.parametrize('order_id, expected_pcv', [
    ('test_pcv_plain_corp_order', 10000),
    ('test_pcv_need_disp_accept', 10000),
    ('test_pcv_need_accept_by_sum', 10000)
])
@pytest.inline_callbacks
def test_set_park_corp_vat(order_id, expected_pcv, patch,
                           corp_clients_get_client_by_client_id_mock):
    @patch('taxi_stq.client.corp_sync_order')
    @async.inline_callbacks
    def corp_sync_order(order_id, order_doc, log_extra):
        yield

    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': order_id})
        async.return_value(dbh.orders.Doc(order))

    order_doc = yield _get_order_doc(order_id)
    proc_doc = dbh.order_proc.Doc({})
    yield invoice_handler._close_with_corp(
        order_doc, proc_doc, order_doc.billing_contract)
    new_order_doc = yield _get_order_doc('order_id')
    assert new_order_doc.payment_tech.park_corp_vat == expected_pcv


@pytest.mark.config(
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True
)
@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.parametrize('cost,need_accept', [
    (7001, True),
    (7000, None),
])
@pytest.inline_callbacks
def test_close_with_card_tariff_setting_accept(patch, cost, need_accept):
    @patch('taxi_stq.client.corp_sync_order')
    @async.inline_callbacks
    def corp_sync_order(order_id, order_doc, log_extra):
        yield

    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': order_id})
        async.return_value(dbh.orders.Doc(order))

    order_id = 'card_with_cost'
    update = {
        'cost': cost
    }
    yield db.orders.update({'_id': order_id}, {'$set': update})

    order_doc = yield _get_order_doc(order_id)
    proc_doc = dbh.order_proc.Doc({})
    yield invoice_handler._close_with_card(order_doc, proc_doc)
    new_order_doc = yield _get_order_doc(order_id)

    assert (
        new_order_doc['payment_tech'].get('need_accept', None) == need_accept)


@pytest.mark.now('2020-07-23 15:00:00')
@pytest.mark.filldb(orders='cashback')
@pytest.mark.filldb(order_proc='cashback')
@pytest.mark.parametrize(
    'order_id, cost, cashback_cost, expected_ride, expected_cashback',
    [
        ('some_plus_cashback_order', 900, 100, 9000000, 1000000),
        ('cancelled_cashback_order', None, None, 0, 0)
    ],
    ids=['regular-order', 'cancelled-order']
)
@pytest.mark.parametrize('payment_method', ['card', 'yandex_card'])
@pytest.inline_callbacks
def test_close_with_card_cashback(
        patch,
        order_id,
        cost,
        cashback_cost,
        payment_method,
        expected_ride,
        expected_cashback,
):
    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': _order_id})
        order['payment_tech']['type'] = payment_method
        async.return_value(dbh.orders.Doc(order))

    @async.inline_callbacks
    def _get_order_proc_doc(_order_id):
        order_proc = yield db.order_proc.find_one({'_id': _order_id})
        order_proc['payment_tech']['type'] = payment_method
        async.return_value(dbh.order_proc.Doc(order_proc))

    if cost is not None:
        update_order = {
            'cost': cost
        }
        update_proc = {
            'order.cost': cost,
        }
        yield db.orders.update({'_id': order_id}, {'$set': update_order})
        yield db.order_proc.update({'_id': order_id}, {'$set': update_proc})

    if cashback_cost is not None:
        update_proc = {

            'order.cashback_cost': cashback_cost
        }
        yield db.order_proc.update({'_id': order_id}, {'$set': update_proc})

    order_doc = yield _get_order_doc(order_id)
    proc_doc = yield _get_order_proc_doc(order_id)
    yield invoice_handler._close_with_card(order_doc, proc_doc)
    new_order_doc = yield _get_order_doc(order_id)
    assert new_order_doc['payment_tech']['sum_to_pay']['ride'] == expected_ride
    assert new_order_doc['payment_tech']['user_to_pay']['ride'] == expected_ride
    assert new_order_doc['payment_tech']['without_vat_to_pay']['ride'] == expected_ride
    assert new_order_doc['payment_tech']['sum_to_pay']['cashback'] == expected_cashback
    assert new_order_doc['payment_tech']['user_to_pay']['cashback'] == expected_cashback
    assert new_order_doc['payment_tech']['without_vat_to_pay']['cashback'] is None


@pytest.mark.now('2020-07-23 15:00:00')
@pytest.mark.filldb(orders='toll_road')
@pytest.mark.filldb(order_proc='toll_road')
@pytest.mark.parametrize(
    'order_id, cost, toll_road_cost, expected_ride, expected_toll_road',
    [
        ('toll_road_order', 900, 100, 9000000, 1000000),
        ('free_order', 900, None, 9000000, None),
        ('cancelled_order', None, None, 0, 0)
    ],
    ids=['regular-order', 'free-order', 'cancelled-order']
)
@pytest.inline_callbacks
def test_close_with_card_toll_road(patch, order_id, cost, toll_road_cost, expected_ride, expected_toll_road):
    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': _order_id})
        async.return_value(dbh.orders.Doc(order))

    @async.inline_callbacks
    def _get_order_proc_doc(_order_id):
        order_proc = yield db.order_proc.find_one({'_id': _order_id})
        async.return_value(dbh.order_proc.Doc(order_proc))

    if cost is not None:
        update_order = {
            'cost': cost
        }
        update_proc = {
            'order.cost': cost,
        }
        yield db.orders.update({'_id': order_id}, {'$set': update_order})
        yield db.order_proc.update({'_id': order_id}, {'$set': update_proc})

    if toll_road_cost is not None:
        update_proc = {
            'order.toll_road': {
                'toll_road_price': toll_road_cost,
                'hidden': True,
            }
        }
        yield db.order_proc.update({'_id': order_id}, {'$set': update_proc})

    order_doc = yield _get_order_doc(order_id)
    proc_doc = yield _get_order_proc_doc(order_id)
    yield invoice_handler._close_with_card(order_doc, proc_doc)
    new_order_doc = yield _get_order_doc(order_id)
    assert new_order_doc['payment_tech']['sum_to_pay']['ride'] == expected_ride
    assert new_order_doc['payment_tech']['user_to_pay']['ride'] == expected_ride
    assert new_order_doc['payment_tech']['without_vat_to_pay']['ride'] == expected_ride
    assert new_order_doc['payment_tech']['sum_to_pay'].get('toll_road') == expected_toll_road
    assert new_order_doc['payment_tech']['user_to_pay'].get('toll_road') == expected_toll_road
    assert new_order_doc['payment_tech']['without_vat_to_pay'].get('toll_road') == expected_toll_road


@pytest.mark.config(
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True
)
@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.parametrize('cost,need_accept', [
    (8001, True),
    (8000, None),
])
@pytest.inline_callbacks
def test_close_with_corp_tariff_setting_accept(patch, cost, need_accept,
                                               corp_clients_get_client_by_client_id_mock):
    @patch('taxi_stq.client.corp_sync_order')
    @async.inline_callbacks
    def corp_sync_order(order_id, order_doc, log_extra):
        yield

    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': order_id})
        async.return_value(dbh.orders.Doc(order))

    order_id = 'corp_with_cost'
    update = {
        'cost': cost
    }
    yield db.orders.update({'_id': order_id}, {'$set': update})

    order_doc = yield _get_order_doc(order_id)
    proc_doc = dbh.order_proc.Doc({})
    yield invoice_handler._close_with_corp(
        order_doc, proc_doc, order_doc.billing_contract)
    new_order_doc = yield _get_order_doc(order_id)

    assert (
        new_order_doc['payment_tech'].get('need_accept', None) == need_accept)


@pytest.mark.parametrize(
    'order_id,processing,clear_timeout_config,expected_clear_timeout', [
        (
            '540_5',
            invoices.processing_via_py2(),
            {},
            24 * 3600,
        ),
        (
            'filled_clear_timeout_order_id',
            invoices.processing_via_py2(),
            {},
            1000
        ),
        (
            '540_5',
            invoices.processing_via_transactions(invoices.InvoiceV2({})),
            {},
            None,
        ),
        (
            '540_5',
            invoices.processing_via_py2(),
            {'rus': 3600},
            3600,
        ),
        (
            '540_5',
            invoices.processing_via_py2(),
            {'rus': 7200},
            7200,
        ),
    ]
)
@pytest.inline_callbacks
def test_try_fill_service_orders(
        patch, order_id, processing, clear_timeout_config,
        expected_clear_timeout,
):
    yield config.BILLING_TIME_BEFORE_CLEAR_HOLDED.save(clear_timeout_config)
    yield config.BILLING_TIME_BEFORE_CLEAR_HOLDED.get_fresh()

    @patch('taxi.internal.park_kit.park_helpers.get_billing_product_ids')
    def get_billing_product_ids(*args, **kwargs):
        return {
            'ride': 'ride',
            'tips': 'tips',
            'rebate': 'rebate'
        }

    @patch('taxi.external.billing._call_simple')
    @async.inline_callbacks
    def call_simple(*args, **kwargs):
        yield
        async.return_value({'status': 'success'})

    order = yield db.orders.find_one({'_id': order_id})
    payable = payment_handler.PayableOrder(order)
    yield payment_handler.try_fill_service_orders(
        payable, processing,
    )

    alias_id = order['performer']['taxi_alias']['id']
    if processing.via_transactions:
        assert 'updated' not in payable.doc
        assert 'clear_timeout' not in payable.doc['billing_tech']
        assert payable.service_orders == {'ride': None, 'tips': None}
        assert payable.doc['billing_tech']['version'] == 1
        assert not call_simple.calls
    else:

        assert 'updated' in payable.doc
        assert payable.service_orders['ride'] == (
            alias_id)
        assert payable.service_orders['tips'] == (
            alias_id + '_tips')
        assert payable.doc['billing_tech']['version'] == 2
        actual_clear_timeout = payable.doc['billing_tech']['clear_timeout']
        assert actual_clear_timeout == expected_clear_timeout

        call_simple_calls = call_simple.calls
        assert len(call_simple_calls) == 2


@pytest.mark.parametrize(
    'order_id,processing,expected_num_refresh_attempts,expected_version', [
        (
            'some_order_id',
            invoices.processing_via_py2(),
            2,
            4,
        ),
        (
            'some_order_id',
            invoices.processing_via_transactions(invoices.InvoiceV2({})),
            1,
            3,
        )
])
@pytest.mark.filldb(
    orders='for_test_repeat_refresh_later',
)
@pytest.inline_callbacks
def test_repeat_refresh_later(
        patch, order_id, processing,
        expected_num_refresh_attempts, expected_version
):
    mock = _patch_update_transactions_call_later(patch)
    payable = yield _fetch_payable_order(order_id)
    yield invoice_handler._repeat_refresh_later(payable.order_doc, processing)
    assert payable.num_refresh_attempts == expected_num_refresh_attempts
    assert payable.doc['billing_tech']['version'] == expected_version
    assert len(mock.calls) == 1


class _InvoiceMock(object):
    def __init__(
            self, is_pending=False,
            try_update_from_order_result=True,
            try_compensate_result=True,
            try_refund_compensations_after_hold_result=True,
            needs_to_disable_composite=False,
    ):
        self.is_pending = is_pending
        self._try_update_from_order_result = try_update_from_order_result
        self._try_compensate_result = try_compensate_result
        self._try_refund_compensations_after_hold_result = (
            try_refund_compensations_after_hold_result
        )
        self.needs_to_disable_composite = needs_to_disable_composite

    @async.inline_callbacks
    def try_update_from_order(
            self, payable_order, hold_options, intent=None, log_extra=None,
    ):
        assert isinstance(payable_order, payment_handler.PayableOrder)
        async.return_value(self._try_update_from_order_result)
        yield

    @async.inline_callbacks
    def try_compensate(self, payable_order, log_extra=None):
        assert isinstance(payable_order, payment_handler.PayableOrder)
        async.return_value(self._try_compensate_result)
        yield

    @async.inline_callbacks
    def try_refund_compensations_after_hold(
            self, payable_order, log_extra=None
    ):
        async.return_value(self._try_refund_compensations_after_hold_result)
        yield


@pytest.mark.parametrize(
    'processing,expected_refreshed,expected_has_pending', [
        (
            invoices.processing_via_py2(),
            True,
            True,
        ),
        (
            invoices.processing_via_transactions(
                _InvoiceMock(is_pending=True),
            ),
            False,
            True,
        ),
        (
            invoices.processing_via_transactions(
                _InvoiceMock(is_pending=False),
            ),
            False,
            False,
        ),
    ]
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_has_pending_transactions(
        processing, expected_refreshed, expected_has_pending
):
    payable = _PayableMock(has_pending_transactions=True)
    actual = yield invoice_handler._has_pending_transactions(
        payable, processing
    )
    assert actual is expected_has_pending
    assert payable.refreshed is expected_refreshed


@pytest.mark.parametrize('processing,expected', [
    (invoices.processing_via_py2(), False),
    (
        invoices.processing_via_transactions(
            _InvoiceMock(try_compensate_result=True)
        ),
        True,
    ),
    (
        invoices.processing_via_transactions(
            _InvoiceMock(try_compensate_result=False)
        ),
        False,
    )
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_refresh_pending_compensations(patch, processing, expected):
    _patch_has_pending_compensations(patch)

    actual = yield invoice_handler._refresh_pending_compensations(
        payment_handler.PayableOrder({}), processing, None
    )
    assert actual == expected


def _patch_has_pending_compensations(patch):
    @patch('taxi.internal.order_kit.payment_handler.has_pending_compensations')
    def has_pending_compensations(order_doc, log_extra=None):
        return False


@pytest.mark.parametrize(
    'order_id,processing,expected_num_calls, expected_updated', [
        (
            'some_order_id',
            invoices.processing_via_py2(),
            1,
            True,
        ),
        (
            'some_order_id',
            invoices.processing_via_transactions(_InvoiceMock(
                is_pending=False,
                try_update_from_order_result=True,
            )),
            0,
            True,
        ),
        (
            'some_order_id',
            invoices.processing_via_transactions(_InvoiceMock(
                is_pending=False,
                try_update_from_order_result=False,
            )),
            0,
            False,
        ),
    ]
)
@pytest.mark.filldb(
    orders='for_test_update_transactions_dirty',
)
@pytest.inline_callbacks
def test_update_transactions_dirty(
        patch, order_id, processing, expected_num_calls, expected_updated):
    mock = _patch_update_dirty_transactions(patch)

    payable = yield _fetch_payable_order(order_id)
    actual = yield invoice_handler._update_transactions_dirty(
        payable, processing, lazy_create_order=False, log_extra={'_link': 'x'}
    )
    assert actual == expected_updated
    assert len(mock.calls) == expected_num_calls


def _patch_update_dirty_transactions(patch):
    @patch('taxi.internal.order_kit.payment_handler.update_dirty_transactions')
    @async.inline_callbacks
    def update_dirty_transactions(
            payable, processing, hold_options, lazy_create_order, can_clear,
            log_extra=None):
        async.return_value(True)
        yield
    return update_dirty_transactions


@pytest.mark.parametrize('processing,expected_updated', [
    (
        invoices.processing_via_py2(),
        False,
    ),
    (
        invoices.processing_via_transactions(
            _InvoiceMock(try_refund_compensations_after_hold_result=True)
        ),
        True,
    ),
    (
        invoices.processing_via_transactions(
            _InvoiceMock(try_refund_compensations_after_hold_result=False)
        ),
        False,
    )
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_try_refund_compensations_after_hold(processing, expected_updated):
    actual = yield invoice_handler._try_refund_compensations_after_hold(
        payment_handler.PayableOrder({}),
        processing,
        log_extra=None
    )
    assert actual is expected_updated


@pytest.mark.parametrize(
    'order_id,processing,expected_updated,expected_num_complements', [
        (
            'composite_order_id',
            invoices.processing_via_transactions(
                _InvoiceMock(needs_to_disable_composite=True)
            ),
            True,
            0,
        ),
        (
            'composite_order_id',
            invoices.processing_via_transactions(
                _InvoiceMock(needs_to_disable_composite=False)
            ),
            False,
            1,
        ),
        (
            'card_order_id',
            invoices.processing_via_transactions(
                _InvoiceMock(needs_to_disable_composite=True)
            ),
            False,
            0,
        ),
        (
            'composite_order_id',
            invoices.processing_via_py2(),
            False,
            1,
        ),
    ]
)
@pytest.mark.filldb(
    orders='for_test_try_disable_composite',
)
@pytest.inline_callbacks
def test_try_disable_composite(
        order_id, processing, expected_updated, expected_num_complements):
    payable_order = yield _fetch_payable_order(order_id)
    actual = yield invoice_handler._try_disable_composite(
        payable_order, processing, log_extra=None,
    )
    assert actual is expected_updated
    payable_order_after = yield _fetch_payable_order(order_id)
    assert len(payable_order_after.complements) == expected_num_complements


@pytest.mark.parametrize(
    [
        'order_id',
        'sum_to_pay',
        'user_to_pay',
        'without_vat_to_pay',
        'driver_without_vat_to_pay',
        'is_vat_included',
    ],
    [
        (
            'corp_isr',
            {'ride': 5500000, 'tips': 0},
            {'ride': 5500000, 'tips': 0},
            {'ride': 4700855, 'tips': 0},
            {'ride': 0, 'tips': 0},
            True,
        ),
        (
            'corp_isr_wo_vat',
            {'ride': 5500000, 'tips': 0},
            {'ride': 5500000, 'tips': 0},
            {'ride': 5500000, 'tips': 0},
            {'ride': 0, 'tips': 0},
            True,
        ),
])
@pytest.mark.config(
    COUNTRY_CORP_VAT_BY_DATE={
        'isr': [
            {
                'end': '2020-04-01 00:00:00',
                'start': '2019-12-01 00:00:00',
                'value': 10000
            },
            {
                'end': '2999-12-31 00:00:00',
                'start': '2020-04-01 00:00:00',
                'value': 11700
            }
        ]
    },
    CORP_COUNTRIES_SUPPORTED={
        'isr': {
            'are_tariffs_include_vat': True,
        }
    },
    BILLING_CORP_REBATE_COUNTRIES=[]
)
@pytest.inline_callbacks
def test_close_with_corp(
        patch,
        order_id,
        sum_to_pay,
        user_to_pay,
        without_vat_to_pay,
        driver_without_vat_to_pay,
        is_vat_included,
        corp_clients_get_client_by_client_id_mock,
):
    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': order_id})
        async.return_value(dbh.orders.Doc(order))

    order_doc = yield _get_order_doc(order_id)

    proc_doc = dbh.order_proc.Doc({})

    yield invoice_handler._close_with_corp(
        order_doc, proc_doc, order_doc.billing_contract)

    order_doc = yield db.orders.find_one({'_id': order_id})
    assert 'is_decoupling' not in order_doc['payment_tech']
    assert order_doc['payment_tech']['is_vat_included'] == is_vat_included

    assert (
        order_doc['payment_tech']['driver_without_vat_to_pay'] ==
        driver_without_vat_to_pay
    )
    assert order_doc['payment_tech']['sum_to_pay'] == sum_to_pay
    assert order_doc['payment_tech']['user_to_pay'] == user_to_pay
    assert order_doc['payment_tech']['without_vat_to_pay'] == without_vat_to_pay


@pytest.mark.parametrize(
    [
        'order_id',
        'driver_cost',
        'sum_to_pay',
        'user_to_pay',
        'without_vat_to_pay',
        'driver_without_vat_to_pay',
        'is_vat_included',
    ],
    [
        (
            'decoupling_osn',
            50,
            {'ride': 600000, 'tips': 0},
            {'ride': 1200000, 'tips': 0},
            {'ride': 1000000, 'tips': 0},
            {'ride': 500000, 'tips': 0},
            False,
        ),
        (
            'decoupling_odn',
            50,
            {'ride': 500000, 'tips': 0},
            {'ride': 1200000, 'tips': 0},
            {'ride': 1000000, 'tips': 0},
            {'ride': 500000, 'tips': 0},
            False,
        ),
        (
            'decoupling_kaz',
            50,
            {'ride': 519200, 'tips': 0, 'rebate': 70800},
            {'ride': 1180000, 'tips': 0},
            {'ride': 1000000, 'tips': 0},
            {'ride': 440000, 'tips': 0, 'rebate': 60000},
            False,
        ),
        (
            'decoupling_isr',
            50,
            {'ride': 500000, 'tips': 0},
            {'ride': 5500000, 'tips': 0},
            {'ride': 4700855, 'tips': 0},
            {'ride': 427350, 'tips': 0},
            True,
        ),
        (
            'decoupling_arm',
            60,
            {'ride': 540000, 'tips': 0, 'rebate': 60000},
            {'ride': 1200000, 'tips': 0},
            {'ride': 1000000, 'tips': 0},
            {'ride': 450000, 'tips': 0, 'rebate': 50000},
            True,
        ),
])
@pytest.mark.config(
    COUNTRY_CORP_VAT_BY_DATE={
        'rus': [
            {
                'end': '2018-12-31 21:00:00',
                'start': '1970-01-01 00:00:00',
                'value': 11800
            },
            {
                'end': '2999-12-31 00:00:00',
                'start': '2018-12-31 21:00:00',
                'value': 12000
            }
        ]
    },
    CORP_COUNTRIES_SUPPORTED={
        'arm': {
            'are_tariffs_include_vat': True,
        },
        'isr': {
            'are_tariffs_include_vat': True,
        }
    },
    BILLING_CORP_REBATE_COUNTRIES=['kaz', 'arm']
)
@pytest.inline_callbacks
def test_close_with_corp_decoupling(
        patch,
        order_id,
        driver_cost,
        sum_to_pay,
        user_to_pay,
        without_vat_to_pay,
        driver_without_vat_to_pay,
        is_vat_included,
        corp_clients_get_client_by_client_id_mock,
):
    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': order_id})
        async.return_value(dbh.orders.Doc(order))

    order_doc = yield _get_order_doc(order_id)

    proc_doc = dbh.order_proc.Doc({})
    proc_doc.order.decoupling.success = True
    proc_doc.order.decoupling.driver_price_info.cost = driver_cost

    yield invoice_handler._close_with_corp(
        order_doc, proc_doc, order_doc.billing_contract)

    order_doc = yield db.orders.find_one({'_id': order_id})
    assert order_doc['payment_tech']['is_decoupling'] is True
    assert order_doc['payment_tech']['is_vat_included'] == is_vat_included

    assert (
        order_doc['payment_tech']['driver_without_vat_to_pay'] ==
        driver_without_vat_to_pay
    )
    assert order_doc['payment_tech']['sum_to_pay'] == sum_to_pay
    assert order_doc['payment_tech']['user_to_pay'] == user_to_pay
    assert order_doc['payment_tech']['without_vat_to_pay'] == without_vat_to_pay


@pytest.inline_callbacks
def test_coop_account_limits(patch):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        async.return_value({
            'owner_uid': '123',
            'payment_method_id': 'payment_id',
            'persistent_id': 'billing_id',
            'billing_id': 'persistent_id'
        })

    @patch('taxi_stq.client.shared_payments_update_transaction_call')
    @async.inline_callbacks
    def _update_transaction(*args, **kwargs):
        yield
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id('coop_order')
    payable = payment_handler.PayableOrder(order_doc)
    processing = invoices.processing_via_py2()
    yield coop.coop_update_limits(processing, payable)
    calls = _update_transaction.calls
    assert calls[0]['args'] == (
        'new_trust_payment_id_1', 'coop_order', 'hold', 2000000, 'RUB'
    )
    assert calls[1]['args'] == (
        'new_trust_payment_id_2', 'coop_order', 'hold', 3000000, 'RUB'
    )


@pytest.inline_callbacks
def test_coop_account_limits_when_transactions_used(patch):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        async.return_value({
            'owner_uid': '123',
            'payment_method_id': 'payment_id',
            'persistent_id': 'billing_id',
            'billing_id': 'persistent_id'
        })

    @patch('taxi_stq.client.shared_payments_update_transaction_call')
    @async.inline_callbacks
    def _update_transaction(*args, **kwargs):
        yield
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id('coop_order')
    payable = coop.PayableOrderCoop(order_doc)
    processing = invoices.processing_via_transactions(order_doc)
    yield coop.coop_update_limits(processing, payable)
    calls = _update_transaction.calls
    assert calls[0]['args'] == (
        'new_trust_payment_id_1', 'coop_order', 'hold', 2000000, 'RUB'
    )
    assert calls[1]['args'] == (
        'new_trust_payment_id_2', 'coop_order', 'hold', 3000000, 'RUB'
    )
    assert calls[2]['args'] == (
        'new_trust_payment_id_3', 'coop_order', 'hold', 3000000, 'RUB'
    )
    assert calls[3]['args'] == (
        'new_trust_payment_id_3', 'coop_order', 'refund', -1000000, 'RUB'
    )
    assert calls[4]['args'] == (
        'new_trust_refund_id', 'coop_order', 'refund', -2000000, 'RUB'
    )


@pytest.mark.parametrize('order_id, expected_eta', [
    ('coop-account-order', datetime.datetime(2019, 6, 19, 22, 0, 5)),
    ('card-order', datetime.datetime(2019, 6, 20, 21, 0, 0))
])
@pytest.mark.parametrize('fix_logic_exp_enabled', (True, False))
@pytest.mark.config(
    COOP_ACCOUNT_HOLDING_RETRY_TIME=3600 + 5
)
@pytest.mark.now('2019-06-19 22:00:00')
@pytest.inline_callbacks
def test_calc_hold_eta(
        mock_fix_change_payment_in_py2_config,
        order_id,
        expected_eta,
        fix_logic_exp_enabled,
):
    mock_fix_change_payment_in_py2_config(fix_logic_exp_enabled)
    now = datetime.datetime.utcnow()
    order = yield db.orders.find_one({'_id': order_id})
    order_doc = dbh.orders.Doc(order)
    res = yield invoice_handler._calc_hold_eta(order_doc, now, None)
    assert res == expected_eta


@pytest.mark.parametrize('order_id, driver_summ, decision, extra', [
    (
        'test_set_driver_ride',
        75.0,
        'driver_charge',
        {'driver_charge_sum': {'ride': 25.0}},
    ),
    (
        'test_set_driver_ride',
        25.0,
        'driver_refund',
        {'driver_refund_sum': {'ride': 25.0}},
    ),
])
@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_driver_ride_sum_to_pay(
        order_id,
        driver_summ,
        decision,
        extra,
):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield invoice_handler.update_type_sum_to_pay(
        operator_login='operator',
        order_doc=order_doc,
        version=1,
        user_data=None,
        driver_data={
            'sum': driver_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        ignore_limit=False,
        log_extra=None,
    )

    order_doc = yield db.orders.find_one({'_id': order_id})
    assert order_doc['payment_tech']['sum_to_pay'] == {
        'ride': payment_helpers.cost2inner(driver_summ) * 1.2,
        'tips': 0,
    }
    assert order_doc['payment_tech']['without_vat_to_pay'] == {
        'ride': 1000000,
        'tips': 0,
    }
    assert order_doc['payment_tech']['user_to_pay'] == {
        'ride': 1200000,
        'tips': 0,
    }
    assert order_doc['payment_tech']['driver_without_vat_to_pay'] == {
        'ride': payment_helpers.cost2inner(driver_summ),
        'tips': 0,
    }

    history_obj = {
        'created': NOW,
        'operator_login': 'operator',
        'otrs_ticket': '1',
        'decision': decision,
        'reason_code': 'OTHER',
        'ticket_type': None,
    }
    history_obj.update(extra)

    assert order_doc['payment_tech']['history'] == [history_obj]


@pytest.mark.parametrize(
    [
        'order_id',
        'user_summ',
        'user_decision',
        'user_extra',
        'driver_summ',
        'driver_decision',
        'driver_extra',
    ], [
    (
        'test_set_driver_ride',
        150.0,
        'charge',
        {'charge_sum': {'ride': 50.0}},
        75.0,
        'driver_charge',
        {'driver_charge_sum': {'ride': 25.0}},
    ),
    (
        'test_set_driver_ride',
        50.0,
        'refund',
        {'refund_sum': {'ride': 50.0}},
        25.0,
        'driver_refund',
        {'driver_refund_sum': {'ride': 25.0}},
    ),
])
@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_decoupling_ride_sum_to_pay(
        mock_uuid,
        order_id,
        user_summ,
        user_decision,
        user_extra,
        driver_summ,
        driver_decision,
        driver_extra,
):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield invoice_handler.update_type_sum_to_pay(
        operator_login='operator',
        order_doc=order_doc,
        version=1,
        user_data={
            'sum': user_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        driver_data={
            'sum': driver_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        ignore_limit=False,
        log_extra=None,
    )

    order_doc = yield db.orders.find_one({'_id': order_id})
    assert order_doc['payment_tech']['sum_to_pay'] == {
        'ride': payment_helpers.cost2inner(driver_summ * 1.2),
        'tips': 0,
    }
    assert order_doc['payment_tech']['without_vat_to_pay'] == {
        'ride': payment_helpers.cost2inner(user_summ),
        'tips': 0,
    }
    assert order_doc['payment_tech']['user_to_pay'] == {
        'ride': payment_helpers.cost2inner(user_summ * 1.2),
        'tips': 0,
    }
    assert order_doc['payment_tech']['driver_without_vat_to_pay'] == {
        'ride': payment_helpers.cost2inner(driver_summ),
        'tips': 0,
    }

    user_history_obj = {
        'created': NOW,
        'operator_login': 'operator',
        'otrs_ticket': '1',
        'decision': user_decision,
        'reason_code': 'OTHER',
        'ticket_type': None,
        'transactions_params': {
            'operation_id': 'update_sum_to_pay/randomuuid1234',
        },
    }
    user_history_obj.update(user_extra)

    driver_history_obj = {
        'created': NOW,
        'operator_login': 'operator',
        'otrs_ticket': '1',
        'decision': driver_decision,
        'reason_code': 'OTHER',
        'ticket_type': None,
    }
    driver_history_obj.update(driver_extra)

    assert order_doc['payment_tech']['history'] == [
        user_history_obj,
        driver_history_obj,
    ]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(CARGO_CLAIMS_ENABLE_CALL_CHANGE_CLAIM_ORDER_PRICE=True)
@pytest.mark.parametrize('order_id', [
    ('test_set_driver_ride'),
    ('test_just_partner_payments_false'),
])
@pytest.inline_callbacks
def test_set_decoupling_ride_sum_to_pay_with_cargo_ref_id(patch, order_id):
    user_summ = 150.0
    driver_summ = 25.0

    @patch('taxi_stq.client.change_claim_order_price')
    @async.inline_callbacks
    def change_claim_order_price(cargo_ref_id, new_price,
                                 reason_code, log_extra=None):
        assert cargo_ref_id == 'some cargo ref id'
        assert new_price == str(user_summ)
        assert reason_code == 'OTHER'
        yield async.return_value(None)

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield invoice_handler.update_type_sum_to_pay(
        operator_login='operator',
        order_doc=order_doc,
        version=1,
        user_data={
            'sum': user_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        driver_data={
            'sum': driver_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        ignore_limit=False,
        log_extra=None,
    )
    assert len(change_claim_order_price.calls) == 1


@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    CARGO_CLAIMS_ENABLE_CALL_CHANGE_CLAIM_ORDER_PRICE=True,
    CARGO_DRAGON_ENABLE_CALL_CHANGE_ORDER_PRICE_STQ=False,
)
@pytest.inline_callbacks
def test_cargo_batch_order_do_not_allow_change_price(patch):
    user_summ = 150.0
    driver_summ = 25.0

    order_doc = yield dbh.orders.Doc.find_one_by_id('test_cargo_dragon_order')

    with pytest.raises(exceptions.CargoDragonChangePriceBadWay):
        yield invoice_handler.update_type_sum_to_pay(
            operator_login='operator',
            order_doc=order_doc,
            version=1,
            user_data={
                'sum': user_summ,
                'otrs_ticket': '1',
                'reason_code': 'OTHER',
                'ticket_type': None,
            },
            driver_data={
                'sum': driver_summ,
                'otrs_ticket': '1',
                'reason_code': 'OTHER',
                'ticket_type': None,
            },
            ignore_limit=False,
            log_extra=None,
        )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(CARGO_CLAIMS_ENABLE_CALL_CHANGE_CLAIM_ORDER_PRICE=True)
@pytest.inline_callbacks
def test_cargo_batch_order_allow_change_price(patch):
    user_summ = 150.0
    driver_summ = 25.0

    order_doc = yield dbh.orders.Doc.find_one_by_id('test_cargo_dragon_order')

    @patch('taxi_stq.client.change_claim_order_price')
    @async.inline_callbacks
    def change_claim_order_price(cargo_ref_id, new_price,
                                 reason_code, log_extra=None):
        assert cargo_ref_id == 'order/cargo-order-id'
        assert new_price == str(user_summ)
        assert reason_code == 'OTHER'
        yield async.return_value(None)

    yield invoice_handler.update_type_sum_to_pay(
        operator_login='operator',
        order_doc=order_doc,
        version=1,
        user_data={
            'sum': user_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        driver_data={
            'sum': driver_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        ignore_limit=False,
        log_extra=None,
    )
    assert len(change_claim_order_price.calls) == 1


@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    CARGO_CLAIMS_ENABLE_CALL_CHANGE_CLAIM_ORDER_PRICE=True,
    CARGO_DRAGON_ENABLE_CALL_CHANGE_ORDER_PRICE_STQ=False,
)
@pytest.inline_callbacks
def test_cargo_batch_order_allow_change_price_for_card_order(patch):
    user_summ = 150.0
    driver_summ = 25.0

    order_id = 'test_cargo_dragon_order_with_card'
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    @patch('taxi_stq.client.change_claim_order_price')
    @async.inline_callbacks
    def change_claim_order_price(cargo_ref_id, new_price,
                                 reason_code, log_extra=None):
        assert cargo_ref_id == 'order/cargo-order-id'
        assert new_price == str(user_summ)
        assert reason_code == 'OTHER'
        yield async.return_value(None)

    yield invoice_handler.update_type_sum_to_pay(
        operator_login='operator',
        order_doc=order_doc,
        version=1,
        user_data={
            'sum': user_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        driver_data={
            'sum': driver_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        ignore_limit=False,
        log_extra=None,
    )
    assert len(change_claim_order_price.calls) == 1


@pytest.mark.parametrize('user_summ, expected_cashback', [
    (
        100.0,
        11.0,
    ),
    (
        80.0,
        8,
    ),
])
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(orders='cashback')
@pytest.mark.filldb(order_proc='cashback')
@pytest.inline_callbacks
def test_update_cashback_on_change_ride_sum_to_pay(
        user_summ,
        expected_cashback,
        patch
):
    class FakeCard(object):
        pass

    @patch('taxi.internal.card_operations.get_card_from_db')
    @async.inline_callbacks
    def get_card_from_db(owner_uid, card_id):
        yield
        async.return_value(FakeCard())

    order_id = 'some_plus_cashback_order'

    update_set = {
        'payment_tech.finish_handled': True,
    }

    yield db.orders.find_and_modify(
        {'_id': order_id},
        {'$set': update_set},
    )
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield invoice_handler.update_type_sum_to_pay(
        operator_login='operator',
        order_doc=order_doc,
        version=1,
        user_data={
            'sum': user_summ,
            'otrs_ticket': '1',
            'reason_code': 'OTHER',
            'ticket_type': None,
        },
        driver_data=None,
        ignore_limit=False,
        log_extra=None,
    )

    order_doc = yield db.orders.find_one({'_id': order_id})
    inner_user_summ = payment_helpers.cost2inner(user_summ)
    inner_expected_cashback = payment_helpers.cost2inner(expected_cashback)
    assert order_doc['payment_tech']['sum_to_pay'] == {
        'ride': inner_user_summ,
        'cashback': inner_expected_cashback,
        'tips': 0,
    }
    assert order_doc['payment_tech']['user_to_pay'] == {
        'ride': inner_user_summ,
        'cashback': inner_expected_cashback,
        'tips': 0,
    }


@pytest.mark.parametrize('expected_update', [
    (
        {
            '$set': {'payment_tech.just_closed': True}
        }
    ),
])
@pytest.mark.filldb(_fill=False)
def test_modify_update_with_just_closed(expected_update):
    update = {'$set': {}}
    invoice_handler._modify_update_with_just_closed(update)
    assert update == expected_update


@pytest.mark.parametrize(
    'clid,pending_transaction,expected_payments',
    [
        (
            'clid',
            {
                'card_billing_id': 'check_for_compensations_card_billing_id',
                'card_owner_uid': 'owner_uid',
                'card_payment_id': 'card-x1111',
                'holded': None,
                'payment_method_type': 'card',
                'status': 'hold_pending',
                'initial_sum': {'ride': 2990000, 'cashback': 500000},
                'sum': {'ride': 2990000, 'cashback': 500000},
                'trust_payment_id': 'transaction_1'
            },
            [
                # Hold from cleared_transactions_with_old_resize_logic and
                # cleared_transactions_with_new_resize_logic
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 15, 23, 0),
                    'transactions': [
                        'cleared_transactions_with_old_resize_logic',
                        'cleared_transactions_with_new_resize_logic'
                    ],
                    'values': {'USD': 1615000}
                },
                # Hold from transaction_1
                # Resize from cleared_transactions_with_new_resize_logic
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 16, 0, 0),
                    'transactions': [
                        'transaction_1',
                        'cleared_transactions_with_new_resize_logic'
                    ],
                    'values': {'RUB': -230000, 'USD': 1495000}
                }
            ]
        ),
        (
            'clid',
            {
                'card_billing_id': 'check_for_compensations_card_billing_id',
                'card_owner_uid': 'owner_uid',
                'card_payment_id': 'card-x1111',
                'holded': None,
                'payment_method_type': 'card',
                'status': 'refund_pending',
                'initial_sum': {'ride': 5980000},
                'sum': {'ride': 5980000},
                'refunds': [
                  {
                    'status': 'refund_pending',
                    'sum': {
                      'ride': 2990000
                    },
                    'trust_refund_id': 'transaction_1_refund_id_1',
                  }
                ],
                'trust_payment_id': 'transaction_1'
            },
            [
                # Hold from cleared_transactions_with_old_resize_logic and
                # cleared_transactions_with_new_resize_logic
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 15, 23, 0),
                    'transactions': [
                        'cleared_transactions_with_old_resize_logic',
                        'cleared_transactions_with_new_resize_logic'
                    ],
                    'values': {'USD': 1615000}
                },
                # Refund from transaction_1
                # Resize from cleared_transactions_with_new_resize_logic
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 16, 0, 0),
                    'transactions': [
                        'transaction_1',
                        'cleared_transactions_with_new_resize_logic'
                    ],
                    'values': {'RUB': -3220000}
                }
            ]
        ),
        # Resize happens right now and holded is older than
        # PAYMENTS_STATS_NEW_RESIZE_LOGIC_SINCE. Expect this resize to be added
        # to stats immediately
        (
            'clid',
            {
                'card_billing_id': 'check_for_compensations_card_billing_id',
                'card_owner_uid': 'owner_uid',
                'card_payment_id': 'card-x1111',
                'holded': datetime.datetime(2020, 4, 15, 23),
                'payment_method_type': 'card',
                'status': 'hold_success',
                'initial_sum': {'ride': 3990000},
                'sum': {'ride': 3990000},
                'trust_payment_id': 'resized_transaction_1'
            },
            [
                # Hold from resized_transaction_1,
                # cleared_transactions_with_old_resize_logic,
                # cleared_transactions_with_new_resize_logic
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 15, 23, 0),
                    'transactions': [
                        'resized_transaction_1',
                        'cleared_transactions_with_old_resize_logic',
                        'cleared_transactions_with_new_resize_logic'
                    ],
                    'values': {'USD': 3610000}
                },
                # Resize from cleared_transactions_with_new_resize_logic,
                # resize from resized_transaction_1
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 16, 0, 0),
                    'transactions': [
                        'cleared_transactions_with_new_resize_logic',
                        'resized_transaction_1'
                    ],
                    'values': {'RUB': -1230000}
                },
            ]
        ),
        # Resize happens right now and holded is newer than
        # PAYMENTS_STATS_NEW_RESIZE_LOGIC_SINCE. Expect this
        # resize NOT to be added to stats immediately
        (
            'clid',
            {
                'card_billing_id': 'check_for_compensations_card_billing_id',
                'card_owner_uid': 'owner_uid',
                'card_payment_id': 'card-x1111',
                'holded': datetime.datetime(2020, 4, 16),
                'payment_method_type': 'card',
                'status': 'hold_success',
                'initial_sum': {'ride': 3990000},
                'sum': {'ride': 3990000},
                'trust_payment_id': 'transaction_1'
            },
            [
                # Hold from transaction_1,
                # cleared_transactions_with_old_resize_logic,
                # cleared_transactions_with_new_resize_logic
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 15, 23, 0),
                    'transactions': [
                        'cleared_transactions_with_old_resize_logic',
                        'cleared_transactions_with_new_resize_logic'
                    ],
                    'values': {'USD': 1615000}
                },
                # Hold from transaction_1, resize from
                # cleared_transactions_with_new_resize_logic,
                {
                    'clid': 'clid',
                    'timestamp': datetime.datetime(2020, 4, 16, 0, 0),
                    'transactions': [
                        'transaction_1',
                        'cleared_transactions_with_new_resize_logic',
                    ],
                    'values': {'RUB': -230000, 'USD': 1995000}
                },
            ]
        ),
        # Resize happens right now and holded is newer than
        # PAYMENTS_STATS_NEW_RESIZE_LOGIC_SINCE. Expect this
        # resize NOT to be added to stats immediately
        # using clid from transaction_payload
        (
            'payload_clid',
            {
                'card_billing_id': 'check_for_compensations_card_billing_id',
                'card_owner_uid': 'owner_uid',
                'card_payment_id': 'card-x1111',
                'holded': datetime.datetime(2020, 4, 16),
                'payment_method_type': 'card',
                'status': 'hold_success',
                'initial_sum': {'ride': 3990000},
                'sum': {'ride': 3990000},
                'trust_payment_id': 'transaction_1'
            },
            [
                # cleared_transactions_with_new_resize_logic_and_payload
                {
                    'clid': 'payload_clid',
                    'timestamp': datetime.datetime(2020, 4, 15, 23, 0),
                    'transactions': [
                        'cleared_transactions_with_new_resize_logic_and_payload',
                    ],
                    'values': {'USD': 615000}
                },
                # cleared_transactions_with_new_resize_logic_and_payload
                {
                    'clid': 'payload_clid',
                    'timestamp': datetime.datetime(2020, 4, 16, 0, 0),
                    'transactions': [
                        'cleared_transactions_with_new_resize_logic_and_payload',
                    ],
                    'values': {'RUB': -230000}
                },
            ]
        )
    ]
)
@pytest.mark.now(datetime.datetime(2020, 4, 16).isoformat())
@pytest.mark.filldb(
    orders='test_payments_stats_updated',
)
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.config(PAYMENTS_STATS_MAX_TRANSACTION_AGE_MINUTES=60)
@pytest.mark.config(
    PAYMENTS_STATS_NEW_RESIZE_LOGIC_SINCE='2020-04-15T23:50:00+00:00',
)
@pytest.inline_callbacks
def test_payments_stats_updated(
    patch, clid, pending_transaction, expected_payments):
    yield _check_payment_stats(
        patch,
        order_id='test_payments_stats_updated',
        clid=clid,
        pending_transactions=[pending_transaction],
        expected_payments=expected_payments
    )


@pytest.mark.parametrize(
    'test_case_path',
    [
        'test_tlog_notification/migration_disabled.json',
        'test_tlog_notification/transactions_scheduled_to_be_sent_to_tlog.json',
        'test_tlog_notification/unsent_transaction.json',
        'test_tlog_notification/unsent_refund.json',
        'test_tlog_notification/unsent_compensation.json',
        'test_tlog_notification/unsent_compensation_refund.json',
        'test_tlog_notification/no_cleared_transactions.json',
    ]
)
@pytest.mark.now(datetime.datetime(2020, 4, 16).isoformat())
@pytest.mark.filldb(
    orders='for_test_tlog_notification',
)
@pytest.mark.config(RELY_ON_TRANSACTIONS_NOTIFY_OF_COMPLETE_OPERATIONS=True)
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_tlog_notification(patch, load, test_case_path):
    class MockInvoice(object):
        def is_synced_with(self, *args, **kwargs):
            return True

        @property
        def is_pending(self):
            return True

        @async.inline_callbacks
        def try_update_from_order(self, *args, **kwargs):
            yield async.return_value(False)

        @async.inline_callbacks
        def try_refund_compensations_after_hold(self, *args, **kwargs):
            yield async.return_value(False)

        @async.inline_callbacks
        def try_compensate(self, *args, **kwargs):
            yield async.return_value(False)

        @async.inline_callbacks
        def try_update_from_just_closed(self, *args, **kwargs):
            yield

    @patch('taxi.internal.payment_kit.invoices.try_process_invoice')
    @async.inline_callbacks
    def try_process_invoice(*args, **kwargs):
        yield async.return_value(
            invoices.Processing(
                via_transactions=True,
                invoice=MockInvoice(),
            ),
        )

    @patch('taxi_stq.client.billing_process_payments')
    @async.inline_callbacks
    def billing_process_payments(*args, **kwargs):
        yield

    order_id = 'for-test-tlog-notification'
    test_case = json.loads(
        load(test_case_path), object_hook=json_util.object_hook,
    )
    yield config.TRANSACTIONS_TAXI_TLOG_NOTIFICATION_MIGRATION_ENABLED.save(
        test_case['migration_enabled']
    )
    upd_push = {}
    if 'transactions' in test_case:
        upd_push['billing_tech.transactions'] = {
            '$each': test_case['transactions'],
            '$position': 0,
        }
    if 'compensations' in test_case:
        upd_push['billing_tech.compensations'] = {
            '$each': test_case['compensations'],
            '$position': 0,
        }
    if upd_push:
        yield db.orders.update({'_id': order_id}, {'$push': upd_push})
    yield invoice_handler._update_transactions_iteration(
        order_id, log_extra={'link': 'link1'},
    )
    assert (
        len(billing_process_payments.calls)
        == test_case['expected_times_called']
    )


@pytest.mark.filldb(orders='for_test_lazy_create_order')
@pytest.mark.config(BILLING_LAZY_CREATE_ORDER=False)
@pytest.inline_callbacks
def test_lazy_create_order_disabled(patch):
    yield _check_lazy_create_order(
        patch=patch,
        expected_num_fill_calls=1,
        expected_lazy_create_order=False,
    )


@pytest.mark.filldb(orders='for_test_lazy_create_order')
@pytest.mark.config(BILLING_LAZY_CREATE_ORDER=True)
@pytest.inline_callbacks
def test_lazy_create_order_enabled(patch):
    yield _check_lazy_create_order(
        patch,
        expected_num_fill_calls=0,
        expected_lazy_create_order=True,
    )


@async.inline_callbacks
def _check_lazy_create_order(
        patch,
        expected_num_fill_calls,
        expected_lazy_create_order):
    @patch('taxi.internal.order_kit.invoice_handler._auto_compensation')
    @async.inline_callbacks
    def _auto_compensation(
            order_doc, payable, processing, lazy_create_order, log_extra=None):
        assert lazy_create_order is expected_lazy_create_order
        yield

    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(payable, processing, log_extra=None):
        yield

    @patch('taxi.internal.order_kit.payment_handler.update_dirty_transactions')
    @async.inline_callbacks
    def update_dirty_transactions(
            payable, processing, hold_options, lazy_create_order, can_clear,
            log_extra=None):
        assert lazy_create_order is expected_lazy_create_order
        async.return_value(False)
        yield

    yield invoice_handler._update_transactions_iteration(
        'some_order_id', log_extra={'link': 'link1'}
    )
    assert len(try_fill_service_orders.calls) == expected_num_fill_calls
    assert len(_auto_compensation.calls) == 1
    assert len(update_dirty_transactions.calls) == 1


@pytest.mark.now(datetime.datetime(2020, 4, 16).isoformat())
@pytest.mark.filldb(
    orders='test_payments_stats_updated',
)
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.config(PAYMENTS_STATS_MAX_TRANSACTION_AGE_MINUTES=60)
@pytest.mark.config(
    PAYMENTS_STATS_NEW_RESIZE_LOGIC_SINCE='2020-04-15T23:50:00+00:00',
)
@pytest.inline_callbacks
def test_payments_stats_wallet_ignored(patch):
    yield _check_payment_stats(
        patch,
        order_id='test_wallet_ignored',
        clid='clid',
        pending_transactions=[],
        expected_payments=[]
    )


@pytest.mark.now(datetime.datetime(2020, 4, 16).isoformat())
@pytest.mark.filldb(
    orders='test_payments_stats_updated',
)
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.config(PAYMENTS_STATS_MAX_TRANSACTION_AGE_MINUTES=60)
@pytest.mark.config(
    PAYMENTS_STATS_NEW_RESIZE_LOGIC_SINCE='2020-04-15T23:50:00+00:00',
)
@pytest.inline_callbacks
def test_payments_stats_updated_for_agent(patch):
    yield _check_payment_stats(
        patch,
        order_id='test_payments_stats_updated_for_agent',
        clid='clid',
        pending_transactions=[],
        expected_payments=[
            {
                'clid': 'clid',
                'timestamp': datetime.datetime(2020, 4, 16, 0, 0),
                'transactions': ['test_payments_stats_updated_for_agent/0'],
                'values': {'USD': 600000},
            },
            {
                'clid': 'clid',
                'timestamp': datetime.datetime(2020, 4, 16, 1, 0),
                'transactions': ['test_payments_stats_updated_for_agent/0'],
                'values': {'RUB': -1200000},
            },
        ]
    )


@pytest.mark.parametrize('order_id,summ,expectation', [
    ('byn_order_id', 1, NoException()),
    ('byn_order_id', 0.01, pytest.raises(exceptions.InvalidRefundSumError)),
    ('corp_byn_order_id', 0.01, NoException()),
    ('rub_order_id', 0.01, NoException()),
    ('rub_order_id', 0, pytest.raises(exceptions.InvalidRefundSumError)),
])
@pytest.mark.filldb(
    cities='for_test_check_refund_summ',
    orders='for_test_check_refund_summ',
)
@pytest.mark.config(
    BILLING_MIN_REFUND={'BYN': '0.02'}
)
@pytest.inline_callbacks
def test_check_refund_summ(patch, order_id, summ, expectation):
    _patch_get_max_refund_sum(patch)
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order_doc
    with expectation:
        yield invoice_handler._check_refund_summ(order_doc, 100, summ, False)


@pytest.inline_callbacks
def test_close_with_agent():
    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': _order_id})
        async.return_value(dbh.orders.Doc(order))

    order_doc = yield _get_order_doc('agent')
    proc_doc = dbh.order_proc.Doc({})

    yield invoice_handler._close_with_agent(
        order_doc, proc_doc, order_doc.billing_contract)

    new_order_doc = yield _get_order_doc('agent')
    assert 'is_decoupling' not in new_order_doc['payment_tech']
    assert not new_order_doc['payment_tech'].get('is_vat_included', False)
    assert 'driver_without_vat_to_pay' not in new_order_doc['payment_tech']

    expected_sum = {'ride': 5500000, 'tips': 0}
    assert new_order_doc['payment_tech']['sum_to_pay'] == expected_sum
    assert new_order_doc['payment_tech']['user_to_pay'] == expected_sum
    assert new_order_doc['payment_tech']['without_vat_to_pay'] == expected_sum


@pytest.mark.config(
    USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True
)
@pytest.mark.now('2018-01-01 00:00:00')
@pytest.mark.parametrize(
    'cost, need_accept',
    [
        (8001, True),
        (8000, None),
    ],
)
@pytest.inline_callbacks
def test_close_with_agent_accept_by_corp_settings(patch, cost, need_accept):
    @async.inline_callbacks
    def _get_order_doc(_order_id):
        order = yield db.orders.find_one({'_id': _order_id})
        async.return_value(dbh.orders.Doc(order))

    yield db.orders.update({'_id': 'agent'}, {'$set': {'cost': cost}})

    order_doc = yield _get_order_doc('agent')
    proc_doc = dbh.order_proc.Doc({})
    yield invoice_handler._close_with_agent(
        order_doc, proc_doc, order_doc.billing_contract)
    new_order_doc = yield _get_order_doc('agent')

    assert new_order_doc['payment_tech'].get('need_accept') == need_accept


@pytest.mark.filldb(orders='check_need_change_cvn')
@pytest.mark.parametrize(
    'order_id, expected_need_change, expected_need_cvn, fix_experiment',
    (
        ('yandex_card', False, False, False),
        ('agent', False, False, False),
        ('not_main_card_payment_id', True, False, False),
        ('applepay', False, False, False),
        ('googlepay', True, False, False),
        ('corp', False, False, False),
        ('personal_wallet', True, False, False),
        ('coop_account', False, False, False),
        ('no_debt_paid_by_card', True, False, False),
        ('success_transaction', False, False, False),
        ('failed_transaction', True, True, False),
        ('success_transaction', False, False, True),
        ('failed_transaction', True, True, True),
    ),
)
@pytest.inline_callbacks
def test_check_need_change_cvn(
        mock_fix_change_payment_in_py2_config,
        order_id,
        expected_need_change,
        expected_need_cvn,
        fix_experiment,
):
    mock_fix_change_payment_in_py2_config(is_enabled=fix_experiment)
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    (need_change, need_cvn) = yield invoice_handler._check_need_change_cvn(
        order_doc, None,
    )
    assert need_change == expected_need_change
    assert need_cvn == expected_need_cvn


@pytest.mark.filldb(orders='check_need_change_cvn')
@pytest.mark.parametrize(
    'order_id, cancel_need_cvn, expected_need_change, expected_need_cvn',
    (
        ('failed_transaction', True, False, False),
        ('failed_transaction', False, True, True),
    ),
)
@pytest.inline_callbacks
def test_check_need_change_cvn_with_cancel_need_cvn_for_debts_exp(
        patch,
        mock_fix_change_payment_in_py2_config,
        order_id,
        cancel_need_cvn,
        expected_need_change,
        expected_need_cvn,
):

    def _patch_experiments(experiments_enabled):
        @patch('taxi.internal.order_kit.payment_handler.is_paying_debts_without_cvv_enabled')
        @async.inline_callbacks
        def is_paying_debts_without_cvv_enabled(order_id, phone_id, log_extra=None):
            async.return_value(experiments_enabled)
            yield

        return is_paying_debts_without_cvv_enabled

    mock_fix_change_payment_in_py2_config(is_enabled=True)
    _patch_experiments(cancel_need_cvn)
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    (need_change, need_cvn) = yield invoice_handler._check_need_change_cvn(
        order_doc, None,
    )
    assert need_change == expected_need_change
    assert need_cvn == expected_need_cvn


@pytest.mark.parametrize('is_withdrawal_type_exist,order_core_response', [
    (False, {}),
    (
        True,
        {
            'document': {
                'payment_tech': {
                    'withdrawal_type': 'early_hold',
                }
            }
        }
    )
])
@pytest.mark.config(WITHDRAWAL_TYPE_SET_ENABLED=True)
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_withdrawal_type_prepay(patch, is_withdrawal_type_exist,
                                order_core_response):

    @patch('taxi.internal.order_kit.invoice_handler._get_max_card_ride_cost')
    @async.inline_callbacks
    def _get_max_card_ride_cost(*args, **kwargs):
        yield
        max_card_ride_cost = 1000
        async.return_value(max_card_ride_cost)

    @patch('taxi.internal.order_kit.antifraud.update_ride_sum')
    @async.inline_callbacks
    def update_ride_sum(order_doc, proc, cost, log_extra=None):
        yield
        async.return_value(True)

    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_doc, intent=None, log_extra=None):
        yield
        async.return_value()

    @patch('taxi.internal.order_core.get_order_proc_fields')
    @async.inline_callbacks
    def get_order_proc_fields(order_id, fields, log_extra):
        yield
        response = dict({'revision': []}, **order_core_response)
        async.return_value(response)

    @patch('taxi.internal.order_core.set_order_proc_fields')
    @async.inline_callbacks
    def set_order_proc_fields(order_id, update, revision, log_extra=None):
        yield
        assert update['$set'].get('payment_tech.withdrawal_type', '') == invoice_handler.WITHDRAWAL_TYPE_PREPAY
        async.return_value()

    order_id = 'test_withdrawal_type'
    order_doc = dbh.orders.Doc(
        (yield db.orders.find_one({'_id': order_id}))
    )
    order_proc_doc = dbh.order_proc.Doc(
        (yield db.order_proc.find_one({'_id': order_id}))
    )
    random_cost_lower_than_max = 123

    yield invoice_handler._antifraud_try_hold(order_doc, order_proc_doc, random_cost_lower_than_max)
    assert (len(set_order_proc_fields.calls) == 1) == (not is_withdrawal_type_exist)


@pytest.mark.parametrize('is_withdrawal_type_exist,order_core_response', [
    (False, {}),
    (
        True,
        {
            'document': {
                'payment_tech': {
                    'withdrawal_type': 'early_hold',
                }
            }
        }
    )
])
@pytest.mark.parametrize('is_finish_handled_response', [True, False])
@pytest.mark.config(
    WITHDRAWAL_TYPE_SET_ENABLED=True,
    ENABLE_PAID_CANCEL_PAYMENTS=True
)
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_withdrawal_type_postpay(patch, is_withdrawal_type_exist,
                                 order_core_response, is_finish_handled_response):

    @patch('taxi.internal.order_kit.invoice_handler._stop_prefinished')
    @async.inline_callbacks
    def _stop_prefinished(order_doc, order_proc_doc):
        yield
        async.return_value(False)

    @patch('taxi.internal.order_kit.payment_handler.is_finish_handled')
    @async.inline_callbacks
    def is_finish_handled(order_doc):
        yield
        async.return_value(is_finish_handled_response)

    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_doc, intent=None, log_extra=None):
        yield
        async.return_value()

    @patch('taxi.internal.order_kit.invoice_handler._notify_updated')
    @async.inline_callbacks
    def _notify_updated(order_doc, log_extra=None):
        yield

    @patch('taxi.internal.order_kit.invoice_handler._close_with_card')
    @async.inline_callbacks
    def _close_with_card(order_doc, order_proc, log_extra=None):
        yield

    @patch('taxi.internal.order_core.get_order_proc_fields')
    @async.inline_callbacks
    def get_order_proc_fields(order_id, fields, log_extra):
        yield
        response = dict({'revision': []}, **order_core_response)
        async.return_value(response)

    @patch('taxi.internal.order_core.set_order_proc_fields')
    @async.inline_callbacks
    def set_order_proc_fields(order_id, update, revision, log_extra=None):
        yield
        assert update['$set'].get('payment_tech.withdrawal_type', '') == invoice_handler.WITHDRAWAL_TYPE_POSTPAY
        async.return_value()

    order_id = 'test_withdrawal_type'
    order_doc = dbh.orders.Doc(
        (yield db.orders.find_one({'_id': order_id}))
    )
    order_proc_doc = dbh.order_proc.Doc(
        (yield db.order_proc.find_one({'_id': order_id}))
    )

    yield invoice_handler.finish_ride(order_doc, order_proc_doc)
    assert (len(set_order_proc_fields.calls) == 1) == (not is_withdrawal_type_exist)


def _patch_get_max_refund_sum(patch):
    @patch('taxi.internal.order_kit.invoice_handler._get_max_refund_sum')
    @async.inline_callbacks
    def _get_max_refund_sum(order_doc):
        async.return_value(1000)
        yield


@async.inline_callbacks
def _check_payment_stats(
        patch, order_id, clid, pending_transactions, expected_payments):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield async.return_value({'status': 'success'})

    @patch('taxi.external.billing.do_refund')
    @async.inline_callbacks
    def do_refund(*args, **kwargs):
        yield async.return_value({'status': 'success'})

    @patch('taxi.external.billing.update_basket')
    @async.inline_callbacks
    def update_basket(*args, **kwargs):
        yield async.return_value({'status': 'success'})

    yield db.orders.update(
        {'_id': order_id},
        {
            '$push': {
                'billing_tech.transactions': {
                    '$each': pending_transactions,
                    '$position': 0
                }
            }
        }
    )
    yield invoice_handler._update_transactions_iteration(
        order_id, log_extra={'link': 'link1'}
    )
    payments = yield db.cashless_payments_stats.find(
        {'clid': clid},
        {'_id': False},
    ).sort([('timestamp', 1)]).run()
    assert payments == expected_payments


@async.inline_callbacks
def _fetch_payable_order(order_id):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    async.return_value(payment_handler.PayableOrder(order))


def _patch_update_transactions_call_later(patch):
    @patch('taxi_stq.client.update_transactions_call_later')
    @async.inline_callbacks
    def update_transactions_call_later(eta, order_id, intent=None, log_extra=None):
        yield
    return update_transactions_call_later


class _PayableMock(object):
    def __init__(self, has_pending_transactions):
        self.has_pending_transactions = has_pending_transactions
        self.refreshed = False

    @async.inline_callbacks
    def refresh_pending_transactions(self, log_extra):
        self.refreshed = True
        yield


@pytest.fixture
def mock_uuid(patch):
    @patch('uuid.uuid4')
    def _uuid4():
        class Hex(object):
            hex = 'randomuuid1234'
        return Hex

    return _uuid4
