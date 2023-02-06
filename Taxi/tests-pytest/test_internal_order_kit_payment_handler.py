import datetime
import decimal
import itertools
import json

import bson
import pytest

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import billing
from taxi.external import corp_clients
from taxi.external import plus_wallet as plus_wallet_service
from taxi.internal import card_operations
from taxi.internal import dbh
from taxi.internal.coop_account import client as coop_client
from taxi.internal.order_kit import antifraud
from taxi.internal.order_kit import const
from taxi.internal.order_kit import invoice_handler
from taxi.internal.order_kit import payment_handler
from taxi.internal.order_kit.payables import coop as coop_payable
from taxi.internal.payment_kit import invoices
from taxi.internal.payment_kit import payable as payable_module

from cardstorage_mock import mock_cardstorage

import helpers


NOW = datetime.datetime(2016, 8, 4, 20, 0)
PAYMENT_NOT_FOUND_AT = datetime.datetime(2018, 1, 11, 12)


@pytest.fixture(autouse=True)
def patch_userapi_phone_id(patch):
    @patch('taxi.internal.userapi.get_user_phone')
    @async.inline_callbacks
    def impl(
            phone_id,
            primary_replica=False,
            fields=None,
            log_extra=None,
    ):
        doc = yield dbh.user_phones.Doc.find_one_by_id(
            phone_id,
            secondary=not primary_replica,
            fields=fields,
        )
        async.return_value(doc)


@pytest.fixture(autouse=True)
def patch_cardsotrage_client(patch):
    mock_cardstorage(patch)


@pytest.fixture
def patch_corp_clients(patch):
    clients = {
        'client_id_1': {
            'id': 'client_id_1',
            'billing_id': 'billing_id_1234',
            'services': {
                'taxi': {
                    'is_test': False,
                }
            }
        },
        'client_id_2': {
            'id': 'client_id_2',
            'billing_id': 'billing_id_1234',
            'services': {
                'taxi': {
                    'is_test': True,
                },
                'cargo': {
                    'is_test': True,
                }
            }
        },
        'client_id_3': {
            'id': 'client_id_3',
            'billing_id': 'billing_id_kaz_1234',
            'services': {
                'taxi': {
                    'is_test': False,
                }
            }
        },
        'client_id_4': {
            'id': 'client_id_4',
            'billing_id': 'billing_id_isr_1234',
            'services': {
                'taxi': {
                    'is_test': False,
                }
            }
        },
        'client_id_without_vat_1': {
            'id': 'client_id_1',
            'billing_id': 'billing_id_1234',
            'services': {
                'taxi': {
                    'is_test': False,
                }
            }
        },
    }

    @patch('taxi.external.corp_clients.get_client_by_client_id')
    @async.inline_callbacks
    def get_client_by_client_id(client_id, fields=None, log_extra=None, **kwargs):
        client_data = clients.get(client_id)
        if not client_data:
            raise corp_clients.NotFoundError
        yield async.return_value({f: client_data[f] for f in ('id', 'billing_id')
                                  if f in client_data})

    @patch('taxi.external.corp_clients.get_service_taxi')
    @async.inline_callbacks
    def get_service_taxi(client_id, log_extra=None, **kwargs):
        client_data = clients.get(client_id)
        if not client_data or 'taxi' not in client_data['services']:
            raise corp_clients.NotFoundError
        yield async.return_value(client_data['services']['taxi'])

    @patch('taxi.external.corp_clients.get_service_cargo')
    @async.inline_callbacks
    def get_service_cargo(client_id, log_extra=None, **kwargs):
        client_data = clients.get(client_id)
        if not client_data or 'cargo' not in client_data['services']:
            raise corp_clients.NotFoundError
        yield async.return_value(client_data['services']['cargo'])


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_mark_holded_or_failed_call(patch):
    # `_mark_holded_or_failed` is called when `_clear_basket` raises
    # `billing.UpdateBasketError` exception

    module = 'taxi.internal.order_kit.payment_handler.'

    @patch(module + '_clear_basket')
    @async.inline_callbacks
    def _clear_basket(*args, **kwargs):
        yield
        raise billing.UpdateBasketError('got status:failed')

    @patch(module + '_mark_holded_or_failed')
    @async.inline_callbacks
    def _mark_holded_or_failed(tran):
        yield

    transaction = {'status': const.CLEAR_INIT}
    order_doc = {
        '_id': 'id',
        'billing_tech': {
            'transactions': [transaction],
            'version': 1,
        },
        'payment_tech': {},
        'user_uid': '12334567fdhugejw'
    }
    yield db.orders.save(order_doc)
    payable = payment_handler.PayableOrder(order_doc)
    yield payment_handler.refresh_pending_transactions(payable)

    assert len(_clear_basket.calls) == 1
    assert len(_mark_holded_or_failed.calls) == 1


@pytest.mark.filldb(_fill=False)
def test_mark_holded_or_failed(monkeypatch):
    monkeypatch.setattr(settings, 'MAX_CLEAR_ATTEMPTS', 2)

    # First time move back to hold_success and increment counter
    tran = {}
    payment_handler._mark_holded_or_failed(tran)
    assert tran == {
        'status': const.HOLD_SUCCESS,
        'updated': datetime.datetime.utcnow(),
        'clear_attempts': 1,
    }

    # The same will be done for second time
    payment_handler._mark_holded_or_failed(tran)
    assert tran['status'] == const.HOLD_SUCCESS
    assert tran['clear_attempts'] == 2

    # Third time mark as CLEAR_FAIL
    payment_handler._mark_holded_or_failed(tran)
    assert tran['status'] == const.CLEAR_FAIL
    assert tran['clear_attempts'] == 2


@pytest.mark.parametrize('ready,status,new_status', [
    (False, const.HOLD_FAIL, const.HOLD_FAIL),
    (True, const.HOLD_SUCCESS, const.CLEAR_INIT),
    (False, const.HOLD_SUCCESS, const.HOLD_SUCCESS),
])
@pytest.mark.filldb(_fill=False)
def test_mark_ready_to_clear(patch, ready, status, new_status):
    # `_mark_ready_to_clear` changes status of transactions from
    # `HOLD_SUCCESS` to `CLEAR_INIT` if it is time to clear (clear eta
    # is less than or equal now)

    @patch('taxi.internal.order_kit.payment_handler._calc_clear_eta')
    def _calc_clear_eta(tran, clear_timeout=None):
        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(seconds=1)
        if ready:
            eta = now - delta
        else:
            eta = now + delta
        return eta

    tran = {'status': status}
    order_doc = {'billing_tech': {'transactions': [tran]}}
    payable = payment_handler.PayableOrder(order_doc)
    marked = payment_handler._mark_ready_to_clear(payable)
    assert tran['status'] == new_status
    status_was_changed = new_status != status
    assert marked == status_was_changed


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('processing,expected', [
    (
        invoices.processing_via_py2(),
        datetime.datetime(2018, 1, 1, 3),
    ),
    (
        invoices.processing_via_transactions(invoices.InvoiceV2({})),
        None,
    ),
])
def test_calc_nearest_clear_eta(patch, processing, expected):

    @patch('taxi.internal.order_kit.payment_handler._calc_clear_eta')
    def _calc_clear_eta(tran, clear_timeout=None):
        return tran['holded']

    transactions = [
        {
            'status': const.HOLD_FAIL,
            'holded': datetime.datetime(2018, 1, 1, 1),
        },
        {
            'status': const.HOLD_SUCCESS,
            'holded': datetime.datetime(2018, 1, 1, 3),
        },
        {
            'status': const.HOLD_SUCCESS,
            'holded': datetime.datetime(2018, 1, 1, 5),
        },
    ]
    order_doc = {'billing_tech': {'transactions': transactions}}

    eta = payment_handler.calc_nearest_clear_eta(order_doc, processing, None)
    assert eta == expected


@pytest.mark.parametrize('clear_attempts,extra_seconds,clear_timeout', [
    (0, 0, None),
    (1, 10, None),
    (2, 20, None),
    (3, 40, None),
    (5, 80, None),
    (0, 0, 0),
    (1, 10, 0),
    (2, 20, 0),
    (3, 40, 0),
    (5, 80, 0),
    (0, 0, 1200),
    (1, 10, 1200),
    (2, 20, 1200),
    (3, 40, 1200),
    (5, 80, 1200),
    (0, 0, 3600),
    (1, 10, 3600),
    (2, 20, 3600),
    (3, 40, 3600),
    (5, 80, 3600),
])
@pytest.mark.filldb(_fill=False)
def test_calc_clear_eta(monkeypatch, clear_attempts, extra_seconds,
                        clear_timeout):
    monkeypatch.setattr(settings, 'CLEAR_INTERVALS', [10, 20])

    now = datetime.datetime.utcnow()
    transaction = {'holded': now, 'clear_attempts': clear_attempts}
    eta = payment_handler._calc_clear_eta(transaction, clear_timeout)
    real_clear_timeout = (clear_timeout if clear_timeout is not None
                          else settings.TIME_BEFORE_CLEAR)
    seconds_to_clear = real_clear_timeout + extra_seconds
    assert eta == now + datetime.timedelta(seconds=seconds_to_clear)


@pytest.mark.parametrize(
    'is_transactions,billing_response,expected_is_technical',
    (
        # Without fail transaction answer is "no" becase there are no
        # errors at all
        (False, None, False),
        # Without `billing_response` response is "no" again
        (True, None, False),
        # Without `status_desc` field response is "no" too, because
        # decision is made with this field
        (True, {}, False),
        # If `status_desc` is not about technical error, answer is "no"
        (True, {'status_code': 'any_error'}, False),
        # If `status_desc` is not about technical error, answer is "no"
        (True, {'status_code': 'technical_error'}, True),
    )
)
@pytest.mark.parametrize('fix_exp_enabled', (True, False))
@pytest.inline_callbacks
def test_is_prev_error_technical(
        mock_fix_change_payment_in_py2_config,
        is_transactions,
        billing_response,
        expected_is_technical,
        fix_exp_enabled,
):
    mock_fix_change_payment_in_py2_config(is_enabled=fix_exp_enabled)
    order_doc = yield db.orders.find_one(
        {'_id': 'is_prev_error_technical_order'},
    )
    if is_transactions:
        if billing_response is not None:
            transactions = order_doc['billing_tech']['transactions']
            transactions[0]['billing_response'] = billing_response
    else:
        order_doc['billing_tech']['transactions'] = []
    is_technical = yield payment_handler.is_prev_error_technical(
        order_doc, None,
    )
    assert is_technical == expected_is_technical


def _order_doc_with_refresh_attempts_count(count):
    return {
        'billing_tech': {
            'refresh_attempts_count': count
        }
    }


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('order_doc,expected_num_refresh_attempts', [
    (_order_doc_with_refresh_attempts_count(5), 5),
])
def test_payable_order_num_refresh_attempts(
        order_doc, expected_num_refresh_attempts):
    payable_order = payment_handler.PayableOrder(order_doc)
    assert payable_order.num_refresh_attempts == expected_num_refresh_attempts


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('order_doc', [
    (_order_doc_with_refresh_attempts_count(5)),
])
def test_payable_order_num_refresh_attempts_setter(order_doc):
    payable_order = payment_handler.PayableOrder(order_doc)
    payable_order.num_refresh_attempts = 10
    assert payable_order.num_refresh_attempts == 10
    actual_value = order_doc['billing_tech']['refresh_attempts_count']
    assert actual_value == 10


def _order_doc_with_service_orders(ride=None, tips=None):
    return {
            'billing_tech': {
                'service_orders': {
                    'ride': ride,
                    'tips': tips,
            }
        }
    }


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('order_doc,expected_is_filled', [
    (_order_doc_with_service_orders(ride='some_ride'), True),
    (_order_doc_with_service_orders(ride=None), False),
])
def test_payable_order_is_filled_service_orders(order_doc, expected_is_filled):
    payable_order = payment_handler.PayableOrder(order_doc)
    assert payable_order.is_filled_service_orders == expected_is_filled


def _order_doc_with_transaction_statuses(statuses):
    transactions = [{'status': status} for status in statuses]
    return {
        'billing_tech': {
            'transactions': transactions
        }
    }


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('order_doc,expected_result', [
    # only pending
    (_order_doc_with_transaction_statuses(
        const.PENDING_STATUSES
    ), True),
    # HOLD_INIT is a pending status
    (_order_doc_with_transaction_statuses(
        [const.HOLD_INIT, const.HOLD_SUCCESS]
    ), True),
    # no transactions - no pending transactions
    (_order_doc_with_transaction_statuses(
        []
    ), False),
    # HOLD_SUCCESS is not a pending status
    (_order_doc_with_transaction_statuses(
        [const.HOLD_SUCCESS]
    ), False),
])
def test_payable_order_has_pending_transactions(
        order_doc, expected_result):
    payable_order = payment_handler.PayableOrder(order_doc)
    assert payable_order.has_pending_transactions == expected_result


def _make_invoice_doc(transactions, tv, extra_data=None):
    result = {
        'payment_tech': {},
        'billing_tech': {
            'transactions': transactions,
            'compensations': [],
        },
        'tv': tv,
    }
    if extra_data is not None:
        result.update(extra_data)
    return result


def _make_transaction(
        status, tv, refunds, ride=None, tips=None, cashback=None, toll_road=None):
    result = {
        'status': status,
        'refunds': refunds,
        'data': {'tv': tv}
    }
    _add_to_sum(result, ride, tips, cashback, toll_road)
    return result


def _make_refund(status, tv, ride=None, tips=None, cashback=None):
    result = {
        'status': status,
        'data': {'tv': tv},
    }
    _add_to_sum(result, ride, tips, cashback)
    return result


def _add_to_sum(some_dict, ride, tips, cashback, toll_road=None):
    components = [ride, tips, cashback, toll_road]
    if any(c is not None for c in components):
        if ride is not None:
            some_dict.setdefault('sum', {})['ride'] = ride
        if tips is not None:
            some_dict.setdefault('sum', {})['tips'] = tips
        if cashback is not None:
            some_dict.setdefault('sum', {})['cashback'] = cashback
        if toll_road is not None:
            some_dict.setdefault('sum', {})['toll_road'] = toll_road


@pytest.mark.parametrize('invoice_doc,expected_num_failed', [
    # no fails
    (_make_invoice_doc(
        transactions=[
            _make_transaction('clear_success', 1, []),
        ],
        tv=1,
    ), 0),
    # different tv version: no my fails
    (_make_invoice_doc(
        transactions=[
            _make_transaction('hold_fail', 1, []),
        ],
        tv=2,
    ), 0),
    # 1 my fail
    (_make_invoice_doc(
        transactions=[
            _make_transaction('hold_fail', 1, []),
        ],
        tv=1,
    ), 1),
    # 2 my fails in refunds
    (_make_invoice_doc(
        transactions=[
            _make_transaction('hold_fail', 1, []),
            _make_transaction('clear_success', 1, [
                _make_refund('refund_fail', 1),
                _make_refund('refund_fail', 2),
            ]),
            _make_transaction('clear_success', 2, [
                _make_refund('refund_fail', 2),
            ]),
        ],
        tv=2,
    ), 2),
])
def test_get_num_failed_transactions_or_refunds(
        invoice_doc, expected_num_failed):
    payable = payment_handler.PayableInvoice(invoice_doc)
    actual_num_failed = payment_handler.get_num_failed_transactions_or_refunds(
        payable, payable.data
    )
    assert actual_num_failed == expected_num_failed


@pytest.mark.parametrize(
    'order_doc,compensation_sum,expected_obj,expected_create_basket_calls', [
        (
            {
                'nz': 'moscow',
                'user_locale': 'ru',
                'user_uid': 'uid',
                'request': {
                    'requirements': {},
                    'payment': {'type': 'cash'}
                },
                'billing_tech': {
                    'service_orders': {
                        'ride': 'ride_id',
                    }
                },
                'payment_tech': {
                    'last_known_ip': '127.0.0.1'
                }
            },
            100000,
            {
                'billing_response': None,
                'created': datetime.datetime(2016, 8, 4, 20, 0, 0),
                'owner_uid': 'uid',
                'status': 'compensation_init',
                'sum': {'ride': 100000},
                'refunds': [],
                'terminal_id': None,
                'trust_payment_id': 'trust_payment_id',
                'type': 'compensation',
                'updated': datetime.datetime(2016, 8, 4, 20, 0, 0),
                'compensation_made_at': None,
            },
            [
                {
                    'args': (
                        'card', 'uid', '127.0.0.1', 'RUB',
                        [
                            {
                                'price': 10.0,
                                'service_order_id': 'ride_id',
                            }
                        ],
                        'compensation'
                    ),
                    'kwargs': {'log_extra': None}
                }
            ]
        ),
        (  # Order with currency other than RUB
            {
                'nz': 'almaty',
                'user_locale': 'ru',
                'user_uid': 'uid',
                'request': {
                    'requirements': {},
                    'payment': {
                        'type': 'cash'
                    }
                },
                'billing_tech': {
                    'service_orders': {
                        'ride': 'ride_id',
                    }
                },
                'payment_tech': {
                    'last_known_ip': '127.0.0.1'
                },
                'performer': {
                    'tariff': {
                        'currency': 'KZT'
                    }
                }
            },
            100000,
            {
                'billing_response': None,
                'created': datetime.datetime(2016, 8, 4, 20, 0, 0),
                'owner_uid': 'uid',
                'status': 'compensation_init',
                'sum': {'ride': 100000},
                'refunds': [],
                'terminal_id': None,
                'trust_payment_id': 'trust_payment_id',
                'type': 'compensation',
                'updated': datetime.datetime(2016, 8, 4, 20, 0, 0),
                'compensation_made_at': None,
            },
            [
                {
                    'args': (
                        'card', 'uid', '127.0.0.1', 'KZT',
                        [
                            {'price': 10.0, 'service_order_id': 'ride_id'}
                        ],
                        'compensation'
                    ),
                    'kwargs': {'log_extra': None}
                }
            ]
        )
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_create_compensation_object(
        patch, order_doc, compensation_sum,
        expected_obj, expected_create_basket_calls):

    order_doc = dbh.orders.Doc(order_doc)

    @patch('taxi.internal.dbh.tariff_settings.Doc.find_by_home_zone')
    @async.inline_callbacks
    def find_one_by_home_zone(zone_name):
        if zone_name == 'moscow':
            doc = dbh.tariff_settings.Doc({'country': 'rus'})
        elif zone_name == 'almaty':
            doc = dbh.tariff_settings.Doc({'country': 'kaz'})
        else:
            raise dbh.tariff_settings.NotFound('Unknown zone %s' % zone_name)
        yield
        async.return_value(doc)

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value('trust_payment_id')

    obj = yield payment_handler.create_compensation_object(
        order_doc, const.COMPENSATION_RIDE, {
            'ride': compensation_sum
        }
    )
    assert obj == expected_obj
    assert create_basket.calls == expected_create_basket_calls


class PayableMock(object):
    def __init__(self, is_decoupling):
        self.is_decoupling = is_decoupling
        self.order_doc = {'city': 'moscow', 'payment_tech': {}}

    @async.inline_callbacks
    def tlog(self, client_to_hold, driver_to_hold, agent_to_hold, log_extra=None):
        yield

    @property
    def doc(self):
        return self.order_doc

    @property
    def is_vat_included(self):
        return False

    @property
    def sum_to_pay(self):
        return {'ride': 1200000}

    @property
    def user_to_pay(self):
        return {'ride': 1200000}

    @property
    def without_vat_to_pay(self):
        return {'ride': 1000000}

    @property
    def driver_without_vat_to_pay(self):
        return {'ride': 1000000}

    @async.inline_callbacks
    def hold(
            self, to_hold, hold_options, payment_method, previous_index,
            log_extra=None,
    ):
        yield

    @property
    def transactions(self):
        return []


@pytest.mark.parametrize('payable,lazy_create_order,expected_num_calls', [
    (
        PayableMock(is_decoupling=False),
        True,
        1,
    ),
    (
        PayableMock(is_decoupling=False),
        False,
        0,
    ),
    (
        PayableMock(is_decoupling=True),
        True,
        1,
    ),
    (
        PayableMock(is_decoupling=True),
        False,
        0,
    ),
])
@pytest.inline_callbacks
def test_update_dirty_transactions(
        patch, payable, lazy_create_order, expected_num_calls
):
    @patch('taxi.internal.order_kit.payment_handler.try_fill_service_orders')
    @async.inline_callbacks
    def try_fill_service_orders(**kwargs):
        assert kwargs == {
            'payable': payable,
            'processing': processing,
            'log_extra': None,
        }
        yield

    processing = invoices.processing_via_py2()
    yield payment_handler.update_dirty_transactions(
        payable=payable,
        processing=processing,
        hold_options=payment_handler.HoldOptions(True, True),
        lazy_create_order=lazy_create_order,
        can_clear=True,
        log_extra=None,
    )
    assert len(try_fill_service_orders.calls) == expected_num_calls


@pytest.mark.parametrize(
    'order_doc,compensation,check_status,expected_status,'
    'expected_check_basket_call',
    [
        (
            {
                '_id': 'order',
                'user_uid': 'uid',
                'payment_tech': {
                    'last_known_ip': '213.180.219.63'
                }
            },
            {
                'trust_payment_id': 'trust-id',
                'status': 'compensation_pending',
            },
            'success',
            'compensation_success',
            {
                'args': ('card', 'uid', '213.180.219.63', 'trust-id'),
                'kwargs': {'log_extra': None}
            },
        ),
        (
            {
                '_id': 'order',
                'user_uid': 'uid',
                'payment_tech': {
                    'last_known_ip': '213.180.219.63'
                }
            },
            {
                'trust_payment_id': 'trust-id',
                'status': 'compensation_pending',
            },
            'cancelled',
            'compensation_fail',
            {
                'args': ('card', 'uid', '213.180.219.63', 'trust-id'),
                'kwargs': {'log_extra': None}
            },
        )
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_check_compensation(
        patch, order_doc, compensation, check_status, expected_status,
        expected_check_basket_call):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({'status': check_status})

    yield payment_handler._check_compensation(
        order_doc, compensation
    )
    assert check_basket.call == expected_check_basket_call
    assert compensation['status'] == expected_status


@pytest.mark.parametrize(
    'order_doc,compensation,check_status,expected_compensation_date',
    [
        (
            {
                '_id': 'order',
                'user_uid': 'uid',
                'payment_tech': {
                    'last_known_ip': '213.180.219.63'
                }
            },
            {
                'trust_payment_id': 'trust-id',
                'status': 'compensation_pending',
                'compensation_made_at': None,
            },
            'success',
            datetime.datetime(2016, 8, 4, 20, 0, 0)
        ),
        (
            {
                '_id': 'order',
                'user_uid': 'uid',
                'payment_tech': {
                    'last_known_ip': '213.180.219.63'
                }
            },
            {
                'trust_payment_id': 'trust-id',
                'status': 'compensation_pending',
                'compensation_made_at': None,
            },
            'cancelled',
            None
        )
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_compensation_date_is_saved_on_compensation_success(
        patch, order_doc, compensation, check_status,
        expected_compensation_date):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({'status': check_status})

    yield payment_handler._check_compensation(
        order_doc, compensation
    )
    assert compensation['compensation_made_at'] == expected_compensation_date


@pytest.mark.parametrize(
    'order_doc,compensation,expected_pay_basket_call',
    [
        (
            {
                '_id': 'order',
                'user_uid': 'uid',
                'payment_tech': {
                    'last_known_ip': '213.180.219.63'
                }
            },
            {
                'trust_payment_id': 'trust-id',
            },
            {
                'args': ('card', 'uid', '213.180.219.63', 'trust-id'),
                'kwargs': {'log_extra': None}
            },
        ),
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_pay_compensation(
        patch, order_doc, compensation, expected_pay_basket_call):
    @patch('taxi.external.billing.pay_basket')
    @async.inline_callbacks
    def pay_basket(*args, **kwargs):
        yield

    yield payment_handler._pay_compensation(
        order_doc, compensation
    )
    assert pay_basket.call == expected_pay_basket_call


@pytest.mark.parametrize(
    (
        # argument names
        'payable,transaction,refund_sum,'
        'expected_obj,expected_create_refund_calls'
    ),
    [
        # argument list
        (
            payment_handler.PayableOrder({
                '_id': 'order',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '127.0.0.1'
                },
                'billing_tech': {'service_orders': {'ride': 'ride_service_id'}},
            }),
            {
                'card_owner_uid': 'uid',
                'trust_payment_id': 'trust_payment_id',
            },
            120000,
            {
                'billing_response': None,
                'created': datetime.datetime(2016, 8, 4, 20, 0),
                'data': None,
                'refund_made_at': None,
                'status': 'refund_pending',
                'sum': {'ride': 120000},
                'trust_refund_id': 'trust_refund_id',
                'updated': datetime.datetime(2016, 8, 4, 20, 0)
            },
            [
                {
                    'args': (
                        'card', 'uid', '127.0.0.1', 'appeal',
                        'trust_payment_id', [
                            {
                                'delta_amount': 12.0,
                                'service_order_id': 'ride_service_id'
                            }
                        ],
                    ),
                    'kwargs': {'log_extra': None},
                }
            ]
        ),
        (
            payment_handler.PayableInvoice({
                'billing_tech': {'service_orders': {'ride': 'ride_service_id'}},
                'tv': 'data'
            }),
            {
                'card_owner_uid': 'uid',
                'trust_payment_id': 'trust_payment_id',
            },
            120000,
            {
                'billing_response': None,
                'created': datetime.datetime(2016, 8, 4, 20, 0),
                'data': {'tv': 'data'},
                'status': 'refund_pending',
                'sum': {'ride': 120000},
                'trust_refund_id': 'trust_refund_id',
                'updated': datetime.datetime(2016, 8, 4, 20, 0)
            },
            [
                {
                    'args': (
                        'donate', 'uid', '127.0.0.1', 'appeal',
                        'trust_payment_id', [
                            {
                                'delta_amount': 12.0,
                                'service_order_id': 'ride_service_id'
                            }
                        ],
                    ),
                    'kwargs': {'log_extra': None},
                }
            ]
        )
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_create_refund_object(patch, payable, transaction, refund_sum,
                              expected_obj, expected_create_refund_calls):
    @patch('taxi.external.billing.create_refund')
    @async.inline_callbacks
    def create_refund(*args, **kwargs):
        yield
        async.return_value('trust_refund_id')

    obj = yield payment_handler._create_refund_object(
        payable, transaction, {'ride': refund_sum},
    )

    assert obj == expected_obj
    assert create_refund.calls == expected_create_refund_calls


@pytest.mark.parametrize(
    'payable,transaction,check_status,expected_refund_obj',
    [
        (
            payment_handler.PayableOrder({
                '_id': 'order-refund-success',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '213.180.219.63',
                    'type': 'card',
                }
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-refund-success-refund-id',
                    'refund_made_at': None,
                    'status': 'refund_pending',
                }],
            },
            'success',
            {
                'refund_made_at': datetime.datetime(2016, 8, 4, 20, 0, 0),
                'status': 'refund_success',
                'updated': datetime.datetime(2016, 8, 4, 20, 0, 0),
                'trust_refund_id': 'order-refund-success-refund-id',
                'billing_response': {'status': 'success'},
            }
        ),
        (
            payment_handler.PayableOrder({
                '_id': 'order-refund-still-pending',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '213.180.219.63',
                    'type': 'card',
                }
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-refund-still-pending-refund-id',
                    'refund_made_at': None,
                    'status': 'refund_pending',
                }],
            },
            'cancelled',
            {
                'refund_made_at': None,
                'status': 'refund_pending',
                'trust_refund_id': 'order-refund-still-pending-refund-id',
            },
        ),
        (
            payment_handler.PayableInvoice({
                'order_id': 'order-invoice-success',
                'clid': 'clid',
                'currency': 'RUB',
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-invoice-success-refund-id',
                    'status': 'refund_pending',
                }],
            },
            'success',
            {
                'billing_response': {'status': 'success'},
                'status': 'refund_success',
                'trust_refund_id': 'order-invoice-success-refund-id',
                'updated': datetime.datetime(2016, 8, 4, 20, 0, 0),
            },
        ),
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_refund_date_is_saved_on_refund_success(
        patch, payable, transaction, check_status, expected_refund_obj):
    @patch('taxi.external.billing.do_refund')
    @async.inline_callbacks
    def do_refund(*args, **kwargs):
        yield
        async.return_value({'status': check_status})

    yield payment_handler._do_refund(
        payable,
        payment_handler.RefundableTransaction(transaction),
        log_extra=None
    )
    refund = transaction['refunds'][-1]
    assert refund == expected_refund_obj, payable


@pytest.inline_callbacks
def test_create_transaction_object(patch):
    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value('trust_payment_id')

    class _PayableBase(object):
        ip = '127.0.0.1'
        service_orders = {
            'ride': 'ride_service_id',
            'tips': 'tips_service_id'
        }
        data = 'data'
        currency = 'RUB'

        @property
        def payment_method(self):
            return 'payment_method_type'

        @property
        def doc(self):
            return {}

        @async.inline_callbacks
        def get_billing(self, log_extra=None):
            yield
            async.return_value('card')

    class _PayableOrder(_PayableBase):
        needs_initial_transaction_sum_to_be_saved = True

    class _PayableInvoice(_PayableBase):
        needs_initial_transaction_sum_to_be_saved = False

    payable_order = _PayableOrder()
    payable_invoice = _PayableInvoice()
    hold_sum = {'ride': 8990000, 'tips': 1000000}
    order_transaction = yield payment_handler._create_transaction_object(
        payable_order,
        owner_uid='owner_uid',
        paymethod_id='paymethod_id',
        billing_id='billing_id',
        payment_id='payment_id',
        hold_sum=hold_sum,
        payment_method_type='payment_method_type'
    )
    assert order_transaction['initial_sum'] == order_transaction['sum']
    assert order_transaction['terminal_id'] is None

    invoice_transaction = yield payment_handler._create_transaction_object(
        payable_invoice,
        owner_uid='owner_uid',
        paymethod_id='paymethod_id',
        billing_id='billing_id',
        payment_id='payment_id',
        hold_sum=hold_sum,
        payment_method_type='payment_method_type'
    )
    assert 'initial_sum' not in invoice_transaction
    assert order_transaction['terminal_id'] is None


@pytest.mark.parametrize('order_id,to_hold,expected_calls', [
    (
        'order-hold-check',
        {'ride': 100000},
        [
            {
                'args': (
                    'card', '123', '127.0.0.1', 'RUB',
                    [
                        {
                            'fiscal_nds': 'nds_0',
                            'fiscal_title': 'Taxi ride',
                            'price': 10.0,
                            'service_order_id': None
                        }
                    ],
                    'card-1234'
                ),
                'kwargs': {
                    'log_extra': None,
                    'user_phone': '+71234567890',
                    'uber_uid': 'uber1234',
                    'pass_params': {
                        'taxi_user_phone_id': (
                            '83e3f99680f78bcc74e4677d4b43789cb11728bb0d3d9912f'
                            'b136e0e62f78154'
                        ),
                        'device_id': 'device_0',
                        'taxi_driver_license': (
                            'f2feac01b4b07cab969ed264ae957ed993e8cd77babad1080'
                            'a85e9f9d52d7780'
                        ),
                        'taxi_car_number': (
                            '959f4488338b25a1471fad52a9c953495cf653790e7cd89e6'
                            'bfc944740bc3885'
                        ),
                        'card_id': 'qwertyuiop',
                        'debt_payment': 0,
                        'order_source': 'iphone',
                        'order_source_lat': 57.4,
                        'order_source_lon': 33.7,
                        'order_tarif': 'business',
                        'order_tips': 15,
                        'park_id': u'park-test',
                        'payed_by': 'cash',
                        'performer_id': 'park-test_driver-test',
                        'sum_to_pay': 100,
                        'travel_distance_km': 0.87,
                        'travel_time_min': 12.8,
                        'uid_creation_dt': '2016-08-04T20:00:00+0000',
                        'order_id': 'order-hold-check',
                        'order_created': '2019-09-16T11:50:00+0000',
                        'taxi_order_city': 'Moscow',
                        'taxi_plan_travel_time_min': 96.96123316418395,
                        'taxi_plan_travel_distance_km': 49.11545359063148,
                        'taxi_plan_order_destination_point_cnt': 1,
                        'taxi_plan_order_cost': 371,
                        'taxi_driver_wait_time_min': 4,
                        'taxi_driver_search_duration_sec': 268,
                    },
                    'check_card': True,
                    'wait_for_cvn_timeout': None,
                    'order_tag': None
                }
            }
        ]
    ),
    (
        'order-hold-check-yandex-card',
        {'ride': 100000},
        [
            {
                'args': (
                    'card', '123', '127.0.0.1', 'RUB',
                    [
                        {
                            'fiscal_nds': 'nds_0',
                            'fiscal_title': 'Taxi ride',
                            'price': 10.0,
                            'service_order_id': None
                        }
                    ],
                    'card-1234'
                ),
                'kwargs': {
                    'log_extra': None,
                    'user_phone': '+71234567890',
                    'uber_uid': 'uber1234',
                    'pass_params': {
                        'taxi_user_phone_id': (
                            '83e3f99680f78bcc74e4677d4b43789cb11728bb0d3d9912f'
                            'b136e0e62f78154'
                        ),
                        'device_id': 'device_0',
                        'taxi_driver_license': (
                            'f2feac01b4b07cab969ed264ae957ed993e8cd77babad1080'
                            'a85e9f9d52d7780'
                        ),
                        'taxi_car_number': (
                            '959f4488338b25a1471fad52a9c953495cf653790e7cd89e6'
                            'bfc944740bc3885'
                        ),
                        'card_id': 'qwertyuiop',
                        'debt_payment': 0,
                        'order_source': 'iphone',
                        'order_source_lat': 57.4,
                        'order_source_lon': 33.7,
                        'order_tarif': 'business',
                        'order_tips': 15,
                        'park_id': u'park-test',
                        'payed_by': 'yandex_card',
                        'performer_id': 'park-test_driver-test',
                        'sum_to_pay': 100,
                        'travel_distance_km': 0.87,
                        'travel_time_min': 12.8,
                        'uid_creation_dt': '2016-08-04T20:00:00+0000',
                        'order_id': 'order-hold-check-yandex-card',
                        'order_created': '2019-09-16T11:50:00+0000',
                        'taxi_order_city': 'Moscow',
                        'taxi_plan_travel_time_min': 96.96123316418395,
                        'taxi_plan_travel_distance_km': 49.11545359063148,
                        'taxi_plan_order_destination_point_cnt': 1,
                        'taxi_plan_order_cost': 371,
                        'taxi_driver_wait_time_min': 4,
                        'taxi_driver_search_duration_sec': 268,
                    },
                    'check_card': True,
                    'wait_for_cvn_timeout': None,
                    'order_tag': None
                }
            }
        ]
    ),
    (
        'nds-check',
        {'ride': 100000},
        [
            {
                'args': (
                    'card', '123', '127.0.0.1', 'RUB',
                    [
                        {
                            'fiscal_nds': 'nds_none',
                            'fiscal_inn': '123456',
                            'fiscal_title': 'Taxi ride',
                            'price': 10.0,
                            'service_order_id': None
                        }
                    ],
                    'card-1234'
                ),
                'kwargs': {
                    'log_extra': None,
                    'user_phone': '+71234567890',
                    'uber_uid': None,
                    'pass_params': {
                        'taxi_user_phone_id': (
                            '83e3f99680f78bcc74e4677d4b43789cb11728bb0d3d9912f'
                            'b136e0e62f78154'
                        ),
                        'device_id': 'device_0',
                        'taxi_driver_license': (
                            'f2feac01b4b07cab969ed264ae957ed993e8cd77babad1080'
                            'a85e9f9d52d7780'
                        ),
                        'taxi_car_number': (
                            '959f4488338b25a1471fad52a9c953495cf653790e7cd89e6'
                            'bfc944740bc3885'
                        ),
                        'card_id': 'asdfghjkl',
                        'debt_payment': 0,
                        'order_source': 'iphone',
                        'order_source_lat': 57.4,
                        'order_source_lon': 33.7,
                        'order_tarif': 'business',
                        'order_tips': 15,
                        'park_id': u'park-test_1',
                        'payed_by': 'card',
                        'performer_id': 'park-test_1_driver-test_1',
                        'sum_to_pay': 100,
                        'travel_distance_km': 0.87,
                        'travel_time_min': 12.8,
                        'uid_creation_dt': '2016-08-04T20:00:00+0000',
                        'order_id': 'nds-check',
                        'order_created': None,
                        'taxi_plan_order_destination_point_cnt': 0,
                    },
                    'check_card': True,
                    'wait_for_cvn_timeout': None,
                    'order_tag': None,
                }
            }
        ]
    ),
])
@pytest.mark.translations([
    ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'Taxi ride'),
])
@pytest.mark.config(
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    PASS_INN_TO_RECEIPT=True,
    AFS_PASS_ADDITIONAL_PARAMS_TO_TRUST=True,
)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_hold_card(patch, order_id, to_hold, expected_calls):
    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield async.return_value({})

    order_doc = yield db.orders.find_one({'_id': order_id})

    yield payment_handler._hold_card(
        order_doc, to_hold, with_cvn=False, previous_index=None, log_extra=None
    )
    assert create_basket.calls == expected_calls
    assert order_doc['billing_tech']['transactions']
    for transaction in order_doc['billing_tech']['transactions']:
        assert transaction['initial_sum'] == transaction['sum']


@pytest.mark.parametrize('enable_pass_params', [True, False])
@pytest.mark.parametrize('order_id,to_hold,expected_call', [
    (
        'order-hold-check',
        {'ride': 100000},
        {
            'args': (
                'card', '123', '127.0.0.1', 'RUB',
                [
                    {
                        'fiscal_nds': 'nds_0',
                        'fiscal_title': 'Taxi ride',
                        'price': 10.0,
                        'service_order_id': None
                    }
                ],
                'card-1234'
            ),
            'kwargs': {
                'check_card': True,
                'log_extra': None,
                'order_tag': '1234',
                'user_phone': '+71234567890',
                'uber_uid': None,
                'wait_for_cvn_timeout': None
            }
        }
    ),
])
@pytest.mark.translations([
    ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'Taxi ride'),
])
@pytest.mark.config(BILLING_FISCAL_RECEIPT_ENABLED=True)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_hold_apple(
        patch, order_id, to_hold, expected_call, enable_pass_params):
    yield config.TRUST_ENABLE_PASS_PARAMS_FOR_TOKEN_PAYMENTS.save(
        enable_pass_params)

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._hold_apple(
        order_doc, to_hold, previous_index=None, log_extra=None
    )
    calls = create_basket.calls
    assert len(calls) == 1
    actual_call = calls[0]
    if enable_pass_params:
        assert actual_call['kwargs'].pop('pass_params') is not None
    else:
        assert actual_call['kwargs'].pop('pass_params') is None
    assert actual_call == expected_call
    assert order_doc['billing_tech']['transactions']
    for transaction in order_doc['billing_tech']['transactions']:
        assert transaction['initial_sum'] == transaction['sum']


@pytest.mark.parametrize('enable_pass_params', [True, False])
@pytest.mark.parametrize('order_id,to_hold,expected_call', [
    (
        'order-hold-check',
        {'ride': 100000},
        {
            'args': (
                'card', '123', '127.0.0.1', 'RUB',
                [
                    {
                        'fiscal_nds': 'nds_0',
                        'fiscal_title': 'Taxi ride',
                        'price': 10.0,
                        'service_order_id': None
                    }
                ],
                'card-1234'
            ),
            'kwargs': {
                'check_card': True,
                'log_extra': None,
                'order_tag': '1234',
                'user_phone': '+71234567890',
                'uber_uid': None,
                'wait_for_cvn_timeout': None
            }
        }
    ),
])
@pytest.mark.translations([
    ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'Taxi ride'),
])
@pytest.mark.config(BILLING_FISCAL_RECEIPT_ENABLED=True)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_hold_google(
        patch, order_id, to_hold, expected_call, enable_pass_params):
    yield config.TRUST_ENABLE_PASS_PARAMS_FOR_TOKEN_PAYMENTS.save(
        enable_pass_params)

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._hold_google(
        order_doc, to_hold, previous_index=None, log_extra=None
    )
    calls = create_basket.calls
    assert len(calls) == 1
    actual_call = calls[0]
    if enable_pass_params:
        assert actual_call['kwargs'].pop('pass_params') is not None
    else:
        assert actual_call['kwargs'].pop('pass_params') is None
    assert actual_call == expected_call
    assert order_doc['billing_tech']['transactions']
    for transaction in order_doc['billing_tech']['transactions']:
        assert transaction['initial_sum'] == transaction['sum']


@pytest.mark.parametrize('order_id,to_hold,expected_calls', [
    (
        'order-hold-check',
        {'ride': 100000},
        [
            {
                'args': (
                    'card', '123', '127.0.0.1', 'RUB',
                    [
                        {
                            'price': 10.0,
                            'service_order_id': None
                        }
                    ],
                    'cash'
                ),
                'kwargs': {
                    'check_card': True,
                    'log_extra': None,
                    'order_tag': None,
                    'pass_params': None,
                    'user_phone': None,
                    'uber_uid': None,
                    'wait_for_cvn_timeout': None
                }
            }
        ]
    ),
])
@pytest.mark.translations([
    ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'Taxi ride'),
])
@pytest.mark.config(BILLING_FISCAL_RECEIPT_ENABLED=True)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_hold_corp(patch, order_id, to_hold, expected_calls):
    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._hold_corp(
        order_doc, to_hold, log_extra=None
    )
    assert create_basket.calls == expected_calls
    assert order_doc['billing_tech']['transactions']
    for transaction in order_doc['billing_tech']['transactions']:
        assert transaction['initial_sum'] == transaction['sum']


def generate_custom_entries(
        client_id,
        user_id,
        currency,
        payment_amount,
        vat_amount,
        is_combo_order=False,
):
    entries = [
        {
            'entity_external_id': 'corp/client/{}'.format(client_id),
            'agreement_id': 'taxi/orders',
            'sub_account': 'payment',
            'currency': currency,
            'amount': payment_amount,
        },
        {
            'entity_external_id': 'corp/client/{}'.format(client_id),
            'agreement_id': 'taxi/orders',
            'sub_account': 'payment/vat',
            'currency': currency,
            'amount': vat_amount,
        },
    ]
    if not is_combo_order:
        entries.extend(
            [
                {
                    'entity_external_id': 'corp/client_employee/{}/{}'.format(
                        client_id, user_id,
                    ),
                    'agreement_id': 'taxi/orders/limit',
                    'sub_account': 'payment',
                    'currency': currency,
                    'amount': payment_amount,
                    'event_at': '2016-08-04T19:00:00+00:00',
                    'reverse_entry_event_at': (
                        '2016-08-04T19:00:00+00:00'
                    ),
                },
                {
                    'entity_external_id': 'corp/client_employee/{}/{}'.format(
                        client_id, user_id,
                    ),
                    'agreement_id': 'taxi/orders/limit',
                    'sub_account': 'payment/vat',
                    'currency': currency,
                    'amount': vat_amount,
                    'event_at': '2016-08-04T19:00:00+00:00',
                    'reverse_entry_event_at': (
                        '2016-08-04T19:00:00+00:00'
                    ),
                },
                {
                    'entity_external_id': 'corp/client_employee/{}/{}'.format(
                        client_id, user_id,
                    ),
                    'agreement_id': 'taxi/orders/limit',
                    'sub_account': 'num_orders',
                    'currency': 'XXX',
                    'amount': '1.0',
                    'event_at': '2016-08-04T19:00:00+00:00',
                    'reverse_entry_event_at': (
                        '2016-08-04T19:00:00+00:00'
                    ),
                },
                {
                    'entity_external_id': 'corp/client_employee/{}/{}'.format(
                        client_id, user_id,
                    ),
                    'agreement_id': 'taxi/orders',
                    'sub_account': 'payment',
                    'currency': currency,
                    'amount': payment_amount,
                },
                {
                    'entity_external_id': 'corp/client_employee/{}/{}'.format(
                        client_id, user_id,
                    ),
                    'agreement_id': 'taxi/orders',
                    'sub_account': 'payment/vat',
                    'currency': currency,
                    'amount': vat_amount,
                },

            ]
        )
    entries.extend(
        [

            {
                'entity_external_id': (
                    'corp/client_department/'
                    '{}/department_id_1'.format(client_id)
                ),
                'agreement_id': 'taxi/orders/limit',
                'sub_account': 'payment',
                'currency': currency,
                'amount': payment_amount,
                'event_at': '2016-08-04T19:00:00+00:00',
                'reverse_entry_event_at': (
                    '2016-08-04T19:00:00+00:00'
                ),
            },
            {
                'entity_external_id': (
                    'corp/client_department/'
                    '{}/department_id_1'.format(client_id)
                ),
                'agreement_id': 'taxi/orders/limit',
                'sub_account': 'payment/vat',
                'currency': currency,
                'amount': vat_amount,
                'event_at': '2016-08-04T19:00:00+00:00',
                'reverse_entry_event_at': (
                    '2016-08-04T19:00:00+00:00'
                ),
            },
            {
                'entity_external_id': (
                    'corp/client_department/'
                    '{}/department_id_2'.format(client_id)
                ),
                'agreement_id': 'taxi/orders/limit',
                'sub_account': 'payment',
                'currency': currency,
                'amount': payment_amount,
                'event_at': '2016-08-04T19:00:00+00:00',
                'reverse_entry_event_at': (
                    '2016-08-04T19:00:00+00:00'
                ),
            },
            {
                'entity_external_id': (
                    'corp/client_department/'
                    '{}/department_id_2'.format(client_id)
                ),
                'agreement_id': 'taxi/orders/limit',
                'sub_account': 'payment/vat',
                'currency': currency,
                'amount': vat_amount,
                'event_at': '2016-08-04T19:00:00+00:00',
                'reverse_entry_event_at': (
                    '2016-08-04T19:00:00+00:00'
                ),
            },
        ]
    )
    return entries


def generate_tlog_entry(service_id, billing_id, ride_sum):
    return {
        'created': NOW,
        'updated': NOW,
        'billing_response': {},
        'billing_service_id': service_id,
        'card_billing_id': billing_id,
        'card_owner_uid': None,
        'card_payment_id': None,
        'clear_attempts': 0,
        'data': None,
        'holded': None,
        'payment_method_type': 'corp',
        'refunds': [],
        'status': 'clear_success',
        'sum': {'ride': ride_sum},
        'trust_payment_id': '',
        'wait_for_cvn': None
    }


def generate_tlog_refund_entry(refund_sum=None, refund_rebate=None):
    sum_ = {}
    if refund_sum:
        sum_['ride'] = refund_sum
    if refund_rebate:
        sum_['rebate'] = refund_rebate
    return [{
        'created': NOW,
        'updated': NOW,
        'status': 'refund_success',
        'sum': sum_,
        'trust_refund_id': '',
        'billing_response': {},
        'data': None,
    }]


def generate_tlog_transaction_object(
        billing_client_id,
        billing_park_id,
        ride_sum_client,
        ride_sum_park,
        rebate_client=None,
        rebate_park=None,
        refund_sum=None,
        refund_rebate=None,
):
    client_transaction = generate_tlog_entry(
        service_id='650',
        billing_id=billing_client_id,
        ride_sum=ride_sum_client
    )
    park_transaction = generate_tlog_entry(
        service_id='651',
        billing_id=billing_park_id,
        ride_sum=ride_sum_park,
    )

    if rebate_client:
        client_transaction['sum']['rebate'] = rebate_client
    if rebate_park:
        park_transaction['sum']['rebate'] = rebate_park
    if refund_sum:
        park_transaction['refunds'] = generate_tlog_refund_entry(
            refund_sum,
            refund_rebate
        )
    return [client_transaction, park_transaction]


def generate_tlog_agent_transaction_object(
        billing_client_id,
        billing_park_id,
        ride_sum_client,
        ride_sum_park,
        ride_sum_agent=None,
        refund_sum_client=None,
        refund_sum_park=None,
):
    transactions = []

    # client agent payment
    client_transaction = generate_tlog_entry(
        service_id='1183',
        billing_id=billing_client_id,
        ride_sum=ride_sum_client,
    )
    transactions.append(client_transaction)

    # agent reward
    if ride_sum_agent:
        transactions.append(generate_tlog_entry(
            service_id='1181',
            billing_id=billing_client_id,
            ride_sum=ride_sum_agent,
        ))

    # park agent payment
    park_transaction = generate_tlog_entry(
        service_id='1182',
        billing_id=billing_park_id,
        ride_sum=ride_sum_park,
    )
    transactions.append(park_transaction)

    if refund_sum_client:
        client_transaction['refunds'] = generate_tlog_refund_entry(refund_sum_client)
    if refund_sum_park:
        park_transaction['refunds'] = generate_tlog_refund_entry(refund_sum_park)

    return transactions


@pytest.mark.parametrize(
    [
        'order_id',
        'client_to_hold',
        'driver_to_hold',
        'agent_to_hold',
        'expected_send',
        'expected_transactions',
    ],
    [
        (
            'order-tlog1',
            ({'ride': 5400000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            {
                'data': {
                    'alias_id': 'alias_id',
                    'is_test_trip': False,
                    'nearest_zone': 'moscow',
                    'tariff_class': 'econom',
                    'order_completed_at': "2016-08-04T20:20:00+00:00",
                    'client_payment': {
                        'billing_id': 'billing_id_1234',
                        'contract_currency': 'RUB',
                        'contract_currency_rate': '1',
                        'ride_cost': '500.0'
                    },
                    'due': '2016-08-04T20:00:00+00:00',
                    'order_currency': 'RUB',
                    'order_id': 'order-tlog1',
                    'custom_entries': generate_custom_entries(
                        client_id='client_id_1',
                        user_id='user_id_1',
                        currency='RUB',
                        payment_amount='500.0000',
                        vat_amount='40.0000',
                    ),
                    'park_payment': {
                        'billing_id': '100000',
                        'clid': 'park-test',
                        'contract_currency': 'RUB',
                        'contract_currency_rate': '1',
                        'db_id': 'some_db_id',
                        'driver_uuid': 'driver-test',
                        'ride_cost': '500.0',
                        'vat': '1.0'
                    },
                    'version': 0
                },
                'event_at': '2016-08-04T20:00:00+00:00',
                'external_event_ref': 'taxi/b2b_trip_payment/alias_id/0',
                'external_obj_id': 'taxi/b2b_trip_payment/alias_id',
                'kind': 'b2b_trip_payment',
                'tvm_src_service': 'stq',
                'log_extra': None,
                'reason': ''
            },
            generate_tlog_transaction_object(
                billing_client_id=u'billing_id_1234',
                billing_park_id=u'100000',
                ride_sum_client=5400000,
                ride_sum_park=5000000,
            ),
        ),
        (
            'order-tlog2',
            ({'ride': 100000}, {}),
            ({}, {'ride': 100000}),
            ({}, {}),
            {
                'data': {
                    'alias_id': 'alias_id',
                    'is_test_trip': True,
                    'nearest_zone': 'moscow',
                    'tariff_class': 'business',
                    'order_completed_at': "2016-08-04T20:20:00+00:00",
                    'client_payment': {
                        'billing_id': 'billing_id_1234',
                        'contract_currency': 'RUB',
                        'contract_currency_rate': '1',
                        'ride_cost': '550.0'
                    },
                    'due': '2016-08-04T20:00:00+00:00',
                    'order_currency': 'RUB',
                    'order_id': 'order-tlog2',
                    'custom_entries': generate_custom_entries(
                        client_id='client_id_2',
                        user_id='user_id_2',
                        currency='RUB',
                        payment_amount='550.0000',
                        vat_amount='-60.0000',
                        is_combo_order=True,
                    ),
                    'park_payment': {
                        'billing_id': '100000',
                        'clid': 'park-test',
                        'contract_currency': 'RUB',
                        'contract_currency_rate': '1',
                        'db_id': 'some_db_id',
                        'driver_uuid': 'driver-test',
                        'ride_cost': '490.0',
                        'vat': '1.0'
                    },
                    'version': 0
                },
                'event_at': '2016-08-04T20:00:00+00:00',
                'external_event_ref': 'taxi/b2b_trip_payment/alias_id/0',
                'external_obj_id': 'taxi/b2b_trip_payment/alias_id',
                'kind': 'b2b_trip_payment',
                'tvm_src_service': 'stq',
                'log_extra': None,
                'reason': '',
            },
            list(
                itertools.chain.from_iterable(
                    [
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_1234',
                            billing_park_id='100000',
                            ride_sum_client=5400000,
                            ride_sum_park=5000000,
                        ),
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_1234',
                            billing_park_id='100000',
                            ride_sum_client=100000,
                            ride_sum_park=0,
                            refund_sum=100000,
                        ),
                    ],
                ),
            ),
        ),
        (
            'order-tlog3',
            ({'ride': 6000000}, {}),
            ({'ride': 4500000, 'rebate': 500000}, {}),
            ({}, {}),
            {
                'data': {
                    'alias_id': 'alias_id',
                    'is_test_trip': False,
                    'nearest_zone': 'astana',
                    'tariff_class': 'econom',
                    'order_completed_at': "2016-08-04T20:20:00+00:00",
                    'client_payment': {
                        'billing_id': 'billing_id_kaz_1234',
                        'contract_currency': 'KZT',
                        'contract_currency_rate': '1',
                        'ride_cost': '600.0'
                    },
                    'due': '2016-08-04T20:00:00+00:00',
                    'order_currency': 'KZT',
                    'order_id': 'order-tlog3',
                    'custom_entries': generate_custom_entries(
                        client_id='client_id_3',
                        user_id='user_id_3',
                        currency='KZT',
                        payment_amount='600.0000',
                        vat_amount='108.0000',
                    ),
                    'park_payment': {
                        'billing_id': '100000',
                        'clid': 'park-test',
                        'contract_currency': 'KZT',
                        'contract_currency_rate': '1',
                        'db_id': 'some_db_id',
                        'driver_uuid': 'driver-test',
                        'ride_cost': '500.0',
                        'vat': '1.18',
                        'rebate': '50.0',
                    },
                    'version': 0
                },
                'event_at': '2016-08-04T20:00:00+00:00',
                'external_event_ref': 'taxi/b2b_trip_payment/alias_id/0',
                'external_obj_id': 'taxi/b2b_trip_payment/alias_id',
                'kind': 'b2b_trip_payment',
                'tvm_src_service': 'stq',
                'log_extra': None,
                'reason': ''
            },
            generate_tlog_transaction_object(
                billing_client_id='billing_id_kaz_1234',
                billing_park_id='100000',
                ride_sum_client=6000000,
                ride_sum_park=4500000,
                rebate_park=500000,
            ),
        ),
        (
            'order-tlog4',
            ({}, {}),
            ({}, {'ride': 500000, 'rebate': 50000}),
            ({}, {}),
            {
                'data': {
                    'alias_id': 'alias_id',
                    'is_test_trip': False,
                    'nearest_zone': 'astana',
                    'tariff_class': 'econom',
                    'order_completed_at': "2016-08-04T20:20:00+00:00",
                    'client_payment': {
                        'billing_id': 'billing_id_kaz_1234',
                        'contract_currency': 'KZT',
                        'contract_currency_rate': '1',
                        'ride_cost': '600.0'
                    },
                    'due': '2016-08-04T20:00:00+00:00',
                    'order_currency': 'KZT',
                    'order_id': 'order-tlog4',
                    'custom_entries': generate_custom_entries(
                        client_id='client_id_3',
                        user_id='user_id_3',
                        currency='KZT',
                        payment_amount='600.0000',
                        vat_amount='108.0000',
                    ),
                    'park_payment': {
                        'billing_id': '100000',
                        'clid': 'park-test',
                        'contract_currency': 'KZT',
                        'contract_currency_rate': '1',
                        'db_id': 'some_db_id',
                        'driver_uuid': 'driver-test',
                        'ride_cost': '445.0',
                        'vat': '1.18',
                        'rebate': '45.0',
                    },
                    'version': 0
                },
                'event_at': '2016-08-04T20:00:00+00:00',
                'external_event_ref': 'taxi/b2b_trip_payment/alias_id/0',
                'external_obj_id': 'taxi/b2b_trip_payment/alias_id',
                'kind': 'b2b_trip_payment',
                'tvm_src_service': 'stq',
                'log_extra': None,
                'reason': ''
            },
            list(
                itertools.chain.from_iterable(
                    [
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_kaz_1234',
                            billing_park_id='100000',
                            ride_sum_client=6000000,
                            ride_sum_park=4500000,
                            rebate_park=500000,
                        ),
                        [{
                            'created': NOW,
                            'updated': NOW,
                            'billing_response': {},
                            'billing_service_id': '651',
                            'card_billing_id': u'100000',
                            'card_owner_uid': None,
                            'card_payment_id': None,
                            'clear_attempts': 0,
                            'data': None,
                            'holded': None,
                            'payment_method_type': 'corp',
                            'status': 'clear_success',
                            'sum': {'ride': 0, 'rebate': 0},
                            'refunds': [{
                                'created': NOW,
                                'updated': NOW,
                                'status': 'refund_success',
                                'sum': {'ride': 500000, 'rebate': 50000},
                                'trust_refund_id': '',
                                'billing_response': {},
                                'data': None,
                            }],
                            'trust_payment_id': '',
                            'wait_for_cvn': None
                        }],
                    ],
                ),
            ),
        ),
        (
            'order-tlog_isr',
            ({'ride': 5500000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            {
                'data': {
                    'alias_id': 'alias_id',
                    'is_test_trip': False,
                    'nearest_zone': 'tel_aviv',
                    'tariff_class': 'econom',
                    'order_completed_at': "2016-08-04T20:20:00+00:00",
                    'client_payment': {
                        'billing_id': 'billing_id_isr_1234',
                        'contract_currency': 'ILS',
                        'contract_currency_rate': '1',
                        'ride_cost': '470.09'
                    },
                    'due': '2016-08-04T20:00:00+00:00',
                    'order_currency': 'ILS',
                    'order_id': 'order-tlog_isr',
                    'custom_entries': generate_custom_entries(
                        client_id='client_id_4',
                        user_id='user_id_4',
                        currency='ILS',
                        payment_amount='470.0900',
                        vat_amount='79.9100',
                    ),
                    'park_payment': {
                        'billing_id': '100000',
                        'clid': 'park-test',
                        'contract_currency': 'ILS',
                        'contract_currency_rate': '1',
                        'db_id': 'some_db_id',
                        'driver_uuid': 'driver-test',
                        'ride_cost': '427.35',
                        'vat': '1.17'
                    },
                    'version': 0
                },
                'event_at': '2016-08-04T20:00:00+00:00',
                'external_event_ref': 'taxi/b2b_trip_payment/alias_id/0',
                'external_obj_id': 'taxi/b2b_trip_payment/alias_id',
                'kind': 'b2b_trip_payment',
                'tvm_src_service': 'stq',
                'log_extra': None,
                'reason': ''
            },
            generate_tlog_transaction_object(
                billing_client_id='billing_id_isr_1234',
                billing_park_id='100000',
                ride_sum_client=5500000,
                ride_sum_park=5000000,
            ),
        ),
    ]
)
@pytest.mark.filldb(orders='for_test_tlog_corp')
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_tlog_corp_b2b_trip_payment(
        patch,
        patch_corp_clients,
        order_id,
        client_to_hold,
        driver_to_hold,
        agent_to_hold,
        expected_send,
        expected_transactions,
):
    @patch('taxi.external.billing_orders.send_doc')
    @async.inline_callbacks
    def send_doc(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.external.corp_integration_api.get_departments')
    @async.inline_callbacks
    def get_departments(*args, **kwargs):
        departments = [{'_id': 'department_id_1'}, {'_id': 'department_id_2'}]
        yield async.return_value({'departments': departments})

    @patch('taxi.internal.city_manager.get_city_tz')
    def test_get_city_tz(*args, **kwargs):
        return 'Europe/Moscow'

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._tlog_corp(
        order_doc, client_to_hold, driver_to_hold, agent_to_hold
    )

    assert send_doc.calls[0]['kwargs'] == expected_send
    assert order_doc['billing_tech']['transactions'] == expected_transactions


@pytest.mark.parametrize(
    [
        'order_id',
        'client_to_hold',
        'driver_to_hold',
        'agent_to_hold',
        'expected_transactions',
    ],
    [
        (
            'order-tlog1',
            ({'ride': 5400000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            generate_tlog_transaction_object(
                billing_client_id=u'billing_id_1234',
                billing_park_id=u'100000',
                ride_sum_client=5400000,
                ride_sum_park=5000000,
            ),
        ),
        (
            'order-tlog2',
            ({'ride': 100000}, {}),
            ({}, {'ride': 100000}),
            ({}, {}),
            list(
                itertools.chain.from_iterable(
                    [
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_1234',
                            billing_park_id='100000',
                            ride_sum_client=5400000,
                            ride_sum_park=5000000,
                        ),
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_1234',
                            billing_park_id='100000',
                            ride_sum_client=100000,
                            ride_sum_park=0,
                            refund_sum=100000,
                        ),
                    ],
                ),
            ),
        ),
        (
            'order-tlog3',
            ({'ride': 6000000}, {}),
            ({'ride': 4500000, 'rebate': 500000}, {}),
            ({}, {}),
            generate_tlog_transaction_object(
                billing_client_id='billing_id_kaz_1234',
                billing_park_id='100000',
                ride_sum_client=6000000,
                ride_sum_park=4500000,
                rebate_park=500000,
            ),
        )
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_corp')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_V2_PAYMENT_EVENTS_SETTINGS={
        '__default__': {
            'periods': [
                {
                    'from': '2001-01-01T00:00:00+00:00',
                    'to': '2099-12-31T23:59:59+00:00'
                },
            ],
        },
    },
)
@pytest.inline_callbacks
def test_tlog_corp_v2_events(
        load,
        patch,
        patch_corp_clients,
        order_id,
        client_to_hold,
        driver_to_hold,
        agent_to_hold,
        expected_transactions,
):
    @patch('taxi.external.billing_orders.process_event_async')
    @async.inline_callbacks
    def process_event_async(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.external.agglomerations.get_mvp_oebs_id')
    @async.inline_callbacks
    def get_mvp_oebs_id(tariff_zone, *args, **kwargs):
        yield async.return_value(
            {
                'moscow': 'MSKc',
                'astana': 'AST',
                'tel_aviv': 'TELAVIV',
            }[tariff_zone]
        )

    @patch('taxi.external.billing_replication.get_active_contracts')
    @async.inline_callbacks
    def get_active_contracts(client_id, *args, **kwargs):
        if '650' in kwargs['service_ids']:
            yield async.return_value(
                [
                    {
                        'ID': 'corp_contract_id',
                        'DT': None,
                        'FIRM_ID': 13
                    },
                ]
            )

        elif '651' in kwargs['service_ids']:
            yield async.return_value(
                [
                    {
                        'ID': 'park_contract_id',
                        'DT': None,
                        'FIRM_ID': 13
                    },
                ]
            )

    @patch('taxi.internal.city_manager.get_city_tz')
    def test_get_city_tz(*args, **kwargs):
        return 'Europe/Moscow'

    @patch('taxi.external.corp_integration_api.get_departments')
    @async.inline_callbacks
    def get_departments(*args, **kwargs):
        departments = [{'_id': 'department_id_1'}, {'_id': 'department_id_2'}]
        yield async.return_value({'departments': departments})

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._tlog_corp(
        order_doc, client_to_hold, driver_to_hold, agent_to_hold,
    )
    expected = json.loads(
        load('excepted_for_test_tlog_corp_v2_events_{}.json'.format(order_id)),
        object_hook=helpers.bson_object_hook
    )

    calls = list(process_event_async.calls)
    assert calls[0]['kwargs'] == expected['b2b_partner_payment']
    assert calls[1]['kwargs'] == expected['b2b_client_payment']
    assert order_doc['billing_tech']['transactions'] == expected_transactions


@pytest.mark.parametrize(
    [
        'order_id',
        'client_to_hold',
        'driver_to_hold',
        'agent_to_hold',
        'expected_transactions',
    ],
    [
        (
            'order_id_1',
            ({'ride': 5000000}, {}),
            ({'ride': 5000000}, {}),
            ({'ride': 10000}, {}),
            generate_tlog_agent_transaction_object(
                billing_client_id=u'billing_id_1234',
                billing_park_id=u'100000',
                ride_sum_client=5000000,
                ride_sum_park=5000000,
                ride_sum_agent=10000,
            ),
        ),
        (
            'order_id_2',
            ({'ride': 100000}, {}),
            ({}, {'ride': 100000}),
            ({}, {}),
            list(
                itertools.chain.from_iterable(
                    [
                        generate_tlog_agent_transaction_object(
                            billing_client_id=u'billing_id_1234',
                            billing_park_id=u'100000',
                            ride_sum_client=5000000,
                            ride_sum_park=5000000,
                            ride_sum_agent=10000,
                        ),
                        generate_tlog_agent_transaction_object(
                            billing_client_id=u'billing_id_1234',
                            billing_park_id=u'100000',
                            ride_sum_client=100000,
                            ride_sum_park=0,
                            refund_sum_park=100000,
                        ),
                    ],
                ),
            ),
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_corp_agent_no_vat')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_V2_PAYMENT_EVENTS_SETTINGS={
        '__default__': {
            'periods': [
                {
                    'from': '2001-01-01T00:00:00+00:00',
                    'to': '2099-12-31T23:59:59+00:00'
                },
            ],
        },
    },
)
@pytest.inline_callbacks
def test_tlog_corp_agent_no_vat(
        load,
        patch,
        patch_corp_clients,
        order_id,
        client_to_hold,
        driver_to_hold,
        agent_to_hold,
        expected_transactions,
):
    @patch('taxi.external.billing_orders.process_event_async')
    @async.inline_callbacks
    def process_event_async(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.external.agglomerations.get_mvp_oebs_id')
    @async.inline_callbacks
    def get_mvp_oebs_id(tariff_zone, *args, **kwargs):
        yield async.return_value(
            {
                'moscow': 'MSKc',
                'astana': 'AST',
                'tel_aviv': 'TELAVIV',
            }[tariff_zone]
        )

    @patch('taxi.external.billing_replication.get_active_contracts')
    @async.inline_callbacks
    def get_active_contracts(client_id, *args, **kwargs):
        if '1183' in kwargs['service_ids']:
            yield async.return_value(
                [
                    {
                        'ID': 'corp_contract_id',
                        'DT': None,
                        'FIRM_ID': 13
                    },
                ]
            )

        elif '1182' in kwargs['service_ids']:
            yield async.return_value(
                [
                    {
                        'ID': 'park_contract_id',
                        'DT': None,
                        'FIRM_ID': 13
                    },
                ]
            )

    @patch('taxi.internal.city_manager.get_city_tz')
    def test_get_city_tz(*args, **kwargs):
        return 'Europe/Moscow'

    @patch('taxi.external.corp_integration_api.get_departments')
    @async.inline_callbacks
    def get_departments(*args, **kwargs):
        departments = [{'_id': 'department_id_1'}, {'_id': 'department_id_2'}]
        yield async.return_value({'departments': departments})

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._tlog_corp(
        order_doc, client_to_hold, driver_to_hold, agent_to_hold,
    )
    expected = json.loads(
        load('excepted_for_test_tlog_corp_agent_no_vat_events_{}.json'.format(order_id)),
        object_hook=helpers.bson_object_hook
    )

    calls = list(process_event_async.calls)
    assert calls[0]['kwargs'] == expected['b2b_partner_payment']
    assert calls[1]['kwargs'] == expected['b2b_client_payment']
    assert order_doc['billing_tech']['transactions'] == expected_transactions


@pytest.mark.parametrize(
    [
        'order_id',
        'client_to_hold',
        'driver_to_hold',
        'agent_to_hold',
    ],
    [
        (
            'order-tlog2',
            ({'ride': 100000}, {}),
            ({}, {'ride': 100000}),
            ({}, {}),
        )
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_corp')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_RESALE_LOGISTICS_TO_TAXI_BY_COUNTRIES={
        'rus': {
            'is_enabled': True,
        },
        '__default__': {
            'is_enabled': False,
        },
    },
    CORP_TECHNICAL_RESALE_SETTINGS_BY_COUNTRY={
        'rus': {
            '651': {
                'client_id': '100000',
                'contract_id': 'park_contract_id',
            },
            '718': {
                'client_id': 'logistic_client_id',
                'contract_id': 'logistic_contract_id',
            },
        }
    },
    CORP_LOGISTIC_PAYMENTS_SETTINGS={
        '__default__': {
            'enabled_since': '1990-01-01T00:00:00+00:00',
            'enabled_to': '2099-12-31T23:59:59+00:00'
        },
    },
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'business': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
        'logistic_business': {
            'client': 'delivery_client_b2b_logistics_payment',
            'partner': 'delivery_park_b2b_logistics_payment',
        },
    }
)
@pytest.inline_callbacks
def test_tlog_v2_events_resale(
        load,
        patch,
        patch_corp_clients,
        order_id,
        client_to_hold,
        driver_to_hold,
        agent_to_hold,
):
    @patch('taxi.external.billing_orders.process_event_async')
    @async.inline_callbacks
    def process_event_async(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.external.agglomerations.get_mvp_oebs_id')
    @async.inline_callbacks
    def get_mvp_oebs_id(tariff_zone, *args, **kwargs):
        yield async.return_value(
            {
                'moscow': 'MSKc',
                'astana': 'AST',
                'tel_aviv': 'TELAVIV',
            }[tariff_zone]
        )

    @patch('taxi.external.billing_replication.get_active_contracts')
    @async.inline_callbacks
    def get_active_contracts(client_id, *args, **kwargs):
        if '650' in kwargs['service_ids']:
            yield async.return_value(
                [
                    {
                        'ID': 'corp_contract_id',
                        'DT': None,
                        'FIRM_ID': 13
                    },
                ]
            )

        elif '651' in kwargs['service_ids']:
            yield async.return_value(
                [
                    {
                        'ID': 'park_contract_id',
                        'DT': None,
                        'FIRM_ID': 13,
                        'SERVICES': [719]
                    },
                ]
            )

    @patch('taxi.internal.city_manager.get_city_tz')
    def test_get_city_tz(*args, **kwargs):
        return 'Europe/Moscow'

    @patch('taxi.external.corp_integration_api.get_departments')
    @async.inline_callbacks
    def get_departments(*args, **kwargs):
        departments = [{'_id': 'department_id_1'}, {'_id': 'department_id_2'}]
        yield async.return_value({'departments': departments})

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._tlog_corp(
        order_doc, client_to_hold, driver_to_hold, agent_to_hold,
    )
    expected = json.loads(
        load('excepted_for_test_tlog_logistic_v2_events_{}.json'.format(order_id)),
        object_hook=helpers.bson_object_hook
    )

    calls = list(process_event_async.calls)
    assert calls[0]['kwargs'] == expected['b2b_agent_taxi_expense']
    assert calls[1]['kwargs'] == expected['b2b_agent_logistics_revenue']
    assert calls[2]['kwargs'] == expected['b2b_partner_payment']
    assert calls[3]['kwargs'] == expected['b2b_client_payment']


@pytest.mark.config(
    CORP_TECHNICAL_RESALE_SETTINGS_BY_COUNTRY={
        'rus': {
            '651': {
                'client_id': 'taxi_client_id',
                'contract_id': 'taxi_contract_id',
            },
            '718': {
                'client_id': 'logistic_client_id',
                'contract_id': 'logistic_contract_id',
            },
        }
    },
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'econom': {
            'client': 'cargo_multi_client_b2b_trip_payment',
            'partner': 'cargo_multi_park_b2b_trip_payment',
        },
        'business': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
        'logistic_econom': {
            'client': 'cargo_client_b2b_logistics_payment',
            'partner': 'cargo_park_b2b_logistics_payment',
        },
        'logistic_business': {
            'client': 'delivery_client_b2b_logistics_payment',
            'partner': 'delivery_park_b2b_logistics_payment',
        },
    },
    CORP_BILLING_LOGISTIC_PAYMENTS_REBATE_SETTINGS={
        'start_from': '2016-08-25T20:00:00+00:00',
        'tariffs': [
            {
                'name': 'econom',
                'prefix': 'cargo',
                'action': 'add_rebate',
            },
            {
                'name': 'business',
                'prefix': 'delivery',
                'action': 'skip',
            },
        ],
        'unknown_tariff_action': 'raise_no_payment_kind',
        'unknown_tariff_prefix': '',
    },
)
@pytest.mark.parametrize(
    [
        'has_logistic_contract',
        'order_id',
        'client_to_hold',
        'driver_to_hold',
        'agent_to_hold',
        'expected_send',
        'expected_transactions',
    ],
    [
        (
            True,
            'order-tlog1',
            ({'ride': 5400000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            {
                'kind': 'b2b_partner_payment',
                'topic': 'taxi/b2b_partner_payment_logistics/alias_id',
                'external_ref': '0',
                'event_at': '2016-08-04T20:00:00+00:00',
                'data': {
                    'schema_version': 'v1',
                    'event_version': 0,
                    'topic_begin_at': '2016-08-04T20:00:00+00:00',
                    'driver_income': {
                        'alias_id': 'alias_id',
                        'components': [
                            {
                                'amount': '500.0000',
                                'currency': 'RUB',
                                'kind': 'payment/corp',
                            },
                        ],
                        'driver': {
                            'db_id': 'some_db_id',
                            'driver_uuid': 'driver-test',
                        },
                        'order_event_at': '2016-08-04T20:00:00+00:00',
                    },
                    'payments': [
                        {
                            'payment_kind': 'cargo_park_b2b_logistics_payment',
                            'amount': '500.0000',
                            'currency': 'RUB',
                            'billing_client_id': '100000',
                            'contract_id': 'park_contract_id',
                            'invoice_date': '2016-08-04T20:20:00+00:00',
                            'payload': {
                                'agglomeration': 'MSKc',
                                'alias_id': 'alias_id',
                                'amount_details': {
                                    'base_amount': '500.0',
                                    'base_currency': 'RUB',
                                    'contract_currency_rate': '1',
                                    'vat': '0.0000',
                                },
                                'driver_details': {
                                    'clid': 'park-test',
                                    'db_id': 'some_db_id',
                                    'uuid': 'driver-test',
                                },
                                'tariff_class': 'econom',
                                'nearest_zone': 'moscow',
                                'order_id': 'order-tlog1',
                            },
                        },
                    ],
                },
                'tags': ['taxi/alias_id/alias_id'],
                'tvm_src_service': 'stq',
                'log_extra': None,
            },
            generate_tlog_transaction_object(
                billing_client_id=u'billing_id_1234',
                billing_park_id=u'100000',
                ride_sum_client=5400000,
                ride_sum_park=5000000,
            ),
        ),
        (
            True,
            'order-tlog2',
            ({'ride': 100000}, {}),
            ({}, {'ride': 100000}),
            ({}, {}),
            {
                'kind': 'b2b_partner_payment',
                'topic': 'taxi/b2b_partner_payment_logistics/alias_id',
                'external_ref': '0',
                'event_at': '2016-08-04T20:00:00+00:00',
                'data': {
                    'schema_version': 'v1',
                    'event_version': 0,
                    'topic_begin_at': '2016-08-04T20:00:00+00:00',
                    'driver_income': {
                        'alias_id': 'alias_id',
                        'components': [
                            {
                                'amount': '490.0000',
                                'currency': 'RUB',
                                'kind': 'payment/corp',
                            },
                        ],
                        'driver': {
                            'db_id': 'some_db_id',
                            'driver_uuid': 'driver-test',
                        },
                        'order_event_at': '2016-08-04T20:00:00+00:00',
                    },
                    'payments': [
                        {
                            'payment_kind': 'delivery_park_b2b_logistics_payment_test',
                            'amount': '490.0000',
                            'currency': 'RUB',
                            'billing_client_id': '100000',
                            'contract_id': 'park_contract_id',
                            'invoice_date': '2016-08-04T20:20:00+00:00',
                            'payload': {
                                'agglomeration': 'MSKc',
                                'alias_id': 'alias_id',
                                'amount_details': {
                                    'base_amount': '490.0',
                                    'base_currency': 'RUB',
                                    'contract_currency_rate': '1',
                                    'vat': '0.0000',
                                },
                                'driver_details': {
                                    'clid': 'park-test',
                                    'db_id': 'some_db_id',
                                    'uuid': 'driver-test',
                                },
                                'tariff_class': 'business',
                                'nearest_zone': 'moscow',
                                'order_id': 'order-tlog2',
                            },
                        },
                    ],
                },
                'tags': ['taxi/alias_id/alias_id'],
                'tvm_src_service': 'stq',
                'log_extra': None,
            },
            list(
                itertools.chain.from_iterable(
                    [
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_1234',
                            billing_park_id='100000',
                            ride_sum_client=5400000,
                            ride_sum_park=5000000,
                        ),
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_1234',
                            billing_park_id='100000',
                            ride_sum_client=100000,
                            ride_sum_park=0,
                            refund_sum=100000,
                        ),
                    ],
                ),
            ),
        ),
        (
            False,
            'order-tlog3',
            ({'ride': 6000000}, {}),
            ({'ride': 4500000, 'rebate': 500000}, {}),
            ({}, {}),
            {
                'kind': 'b2b_partner_payment',
                'topic': 'taxi/b2b_partner_payment/alias_id',
                'external_ref': '0',
                'event_at': '2016-08-04T20:00:00+00:00',
                'data': {
                    'schema_version': 'v1',
                    'event_version': 0,
                    'topic_begin_at': '2016-08-04T20:00:00+00:00',
                    'driver_income': {
                        'alias_id': 'alias_id',
                        'components': [
                            {
                                'amount': '590.0000',
                                'currency': 'KZT',
                                'kind': 'payment/corp',
                            },
                        ],
                        'driver': {
                            'db_id': 'some_db_id',
                            'driver_uuid': 'driver-test',
                        },
                        'order_event_at': '2016-08-04T20:00:00+00:00',
                    },
                    'payments': [
                        {
                            'payment_kind': 'cargo_multi_park_b2b_trip_payment',
                            'amount': '590.0000',
                            'currency': 'KZT',
                            'billing_client_id': '100000',
                            'contract_id': 'park_contract_id',
                            'invoice_date': '2016-08-04T20:20:00+00:00',
                            'payload': {
                                'agglomeration': 'AST',
                                'alias_id': 'alias_id',
                                'amount_details': {
                                    'base_amount': '500.0',
                                    'base_currency': 'KZT',
                                    'contract_currency_rate': '1',
                                    'vat': '90.0000',
                                },
                                'driver_details': {
                                    'clid': 'park-test',
                                    'db_id': 'some_db_id',
                                    'uuid': 'driver-test',
                                },
                                'tariff_class': 'econom',
                                'nearest_zone': 'astana',
                                'order_id': 'order-tlog3',
                            },
                        },
                    ],
                },
                'tags': ['taxi/alias_id/alias_id'],
                'tvm_src_service': 'stq',
                'log_extra': None,
            },
            generate_tlog_transaction_object(
                billing_client_id='billing_id_kaz_1234',
                billing_park_id='100000',
                ride_sum_client=6000000,
                ride_sum_park=4500000,
                rebate_park=500000,
            ),
        ),
        (
            False,
            'order-tlog4',
            ({}, {}),
            ({}, {'ride': 500000, 'rebate': 50000}),
            ({}, {}),
            {
                'kind': 'b2b_partner_payment',
                'topic': 'taxi/b2b_partner_payment/alias_id',
                'external_ref': '0',
                'event_at': '2016-08-04T20:00:00+00:00',
                'data': {
                    'schema_version': 'v1',
                    'event_version': 0,
                    'topic_begin_at': '2016-09-04T20:00:00+00:00',
                    'driver_income': {
                        'alias_id': 'alias_id',
                        'components': [
                            {
                                'amount': '525.1000',
                                'currency': 'KZT',
                                'kind': 'payment/corp',
                            },
                        ],
                        'driver': {
                            'db_id': 'some_db_id',
                            'driver_uuid': 'driver-test',
                        },
                        'order_event_at': '2016-09-04T20:00:00+00:00',
                    },
                    'payments': [
                        {
                            'payment_kind': 'cargo_multi_park_b2b_trip_payment',
                            'amount': '525.1000',
                            'currency': 'KZT',
                            'billing_client_id': '100000',
                            'contract_id': 'park_contract_id',
                            'invoice_date': '2016-08-04T20:20:00+00:00',
                            'payload': {
                                'agglomeration': 'AST',
                                'alias_id': 'alias_id',
                                'amount_details': {
                                    'base_amount': '445.0',
                                    'base_currency': 'KZT',
                                    'contract_currency_rate': '1',
                                    'vat': '80.1000',
                                },
                                'driver_details': {
                                    'clid': 'park-test',
                                    'db_id': 'some_db_id',
                                    'uuid': 'driver-test',
                                },
                                'tariff_class': 'econom',
                                'nearest_zone': 'astana',
                                'order_id': 'order-tlog4',
                            },
                        },
                        {
                            'amount': '-53.1000',
                            'billing_client_id': '100000',
                            'contract_id': 'park_contract_id',
                            'currency': 'KZT',
                            'invoice_date': '2016-08-04T20:20:00+00:00',
                            'payload': {
                                'agglomeration': 'AST',
                                'alias_id': 'alias_id',
                                'amount_details': {
                                    'base_amount': '45.0000',
                                    'base_currency': 'KZT',
                                    'contract_currency_rate': '1',
                                    'vat': '8.1000',
                                },
                                'driver_details': {
                                    'clid': 'park-test',
                                    'db_id': 'some_db_id',
                                    'uuid': 'driver-test',
                                },
                                'nearest_zone': 'astana',
                                'order_id': 'order-tlog4',
                                'tariff_class': 'econom',
                                'transaction_type': 'refund',
                            },
                            'payment_kind': (
                                'cargo_multi_rebate_park_b2b_trip_payment'
                            ),
                        },
                    ],
                },
                'tags': ['taxi/alias_id/alias_id'],
                'tvm_src_service': 'stq',
                'log_extra': None,
            },
            list(
                itertools.chain.from_iterable(
                    [
                        generate_tlog_transaction_object(
                            billing_client_id='billing_id_kaz_1234',
                            billing_park_id='100000',
                            ride_sum_client=6000000,
                            ride_sum_park=4500000,
                            rebate_park=500000,
                        ),
                        [{
                            'created': NOW,
                            'updated': NOW,
                            'billing_response': {},
                            'billing_service_id': '651',
                            'card_billing_id': u'100000',
                            'card_owner_uid': None,
                            'card_payment_id': None,
                            'clear_attempts': 0,
                            'data': None,
                            'holded': None,
                            'payment_method_type': 'corp',
                            'status': 'clear_success',
                            'sum': {'ride': 0, 'rebate': 0},
                            'refunds': [{
                                'created': NOW,
                                'updated': NOW,
                                'status': 'refund_success',
                                'sum': {'ride': 500000, 'rebate': 50000},
                                'trust_refund_id': '',
                                'billing_response': {},
                                'data': None,
                            }],
                            'trust_payment_id': '',
                            'wait_for_cvn': None
                        }],
                    ],
                ),
            ),
        ),
        (
            False,
            'order-tlog_isr',
            ({'ride': 5500000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            {
                'kind': 'b2b_partner_payment',
                'topic': 'taxi/b2b_partner_payment/alias_id',
                'external_ref': '0',
                'event_at': '2016-08-04T20:00:00+00:00',
                'data': {
                    'schema_version': 'v1',
                    'event_version': 0,
                    'topic_begin_at': '2016-08-04T20:00:00+00:00',
                    'driver_income': {
                        'alias_id': 'alias_id',
                        'components': [
                            {
                                'amount': '499.9995',
                                'currency': 'ILS',
                                'kind': 'payment/corp',
                            },
                        ],
                        'driver': {
                            'db_id': 'some_db_id',
                            'driver_uuid': 'driver-test',
                        },
                        'order_event_at': '2016-08-04T20:00:00+00:00',
                    },
                    'payments': [
                        {
                            'payment_kind': 'cargo_multi_park_b2b_trip_payment',
                            'amount': '499.9995',
                            'currency': 'ILS',
                            'billing_client_id': '100000',
                            'contract_id': 'park_contract_id',
                            'invoice_date': '2016-08-04T20:20:00+00:00',
                            'payload': {
                                'agglomeration': 'TELAVIV',
                                'alias_id': 'alias_id',
                                'amount_details': {
                                    'base_amount': '427.35',
                                    'base_currency': 'ILS',
                                    'contract_currency_rate': '1',
                                    'vat': '72.6495',
                                },
                                'driver_details': {
                                    'clid': 'park-test',
                                    'db_id': 'some_db_id',
                                    'uuid': 'driver-test',
                                },
                                'tariff_class': 'econom',
                                'nearest_zone': 'tel_aviv',
                                'order_id': 'order-tlog_isr',
                            },
                        },
                    ],
                },
                'tags': ['taxi/alias_id/alias_id'],
                'tvm_src_service': 'stq',
                'log_extra': None,
            },
            generate_tlog_transaction_object(
                billing_client_id='billing_id_isr_1234',
                billing_park_id='100000',
                ride_sum_client=5500000,
                ride_sum_park=5000000,
            ),
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_corp_b2b_partner_payment')
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_tlog_corp_b2b_partner_payment(
        patch,
        patch_corp_clients,
        order_id,
        client_to_hold,
        driver_to_hold,
        agent_to_hold,
        expected_send,
        expected_transactions,
        has_logistic_contract,
):
    @patch('taxi.external.billing_orders.process_event_async')
    @async.inline_callbacks
    def process_event_async(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.external.agglomerations.get_mvp_oebs_id')
    @async.inline_callbacks
    def get_mvp_oebs_id(tariff_zone, *args, **kwargs):
        yield async.return_value(
            {
                'moscow': 'MSKc',
                'astana': 'AST',
                'tel_aviv': 'TELAVIV',
            }[tariff_zone]
        )

    @patch('taxi.external.billing_replication.get_active_contracts')
    @async.inline_callbacks
    def get_active_contracts(client_id, service_ids, *args, **kwargs):
        if not has_logistic_contract:
            service_ids.remove('719')
        yield async.return_value(
            [
                {
                    'ID': 'park_contract_id',
                    'DT': None,
                    'SERVICES': [
                        int(service_id) for service_id in service_ids
                    ]
                },
            ]
        )

    @patch('taxi.internal.city_manager.get_city_tz')
    def test_get_city_tz(*args, **kwargs):
        return 'Europe/Moscow'

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    yield payment_handler._tlog_corp(
        order_doc, client_to_hold, driver_to_hold, agent_to_hold,
    )

    assert process_event_async.calls[-1]['kwargs'] == expected_send
    assert order_doc['billing_tech']['transactions'] == expected_transactions


@pytest.mark.parametrize(
    'transaction,expected_delta',
    [
        (
            {'initial_sum': {}, 'sum': {'ride': 100000}},
            {'ride': 100000}
        ),
        (
            {'initial_sum': {}, 'sum': {'tips': 100000}},
            {'tips': 100000}
        ),
        (
            {
                'initial_sum': {'ride': 200000},
                'sum': {'ride': 200000, 'tips': 100000}
            },
            {'ride': 0, 'tips': 100000}
        ),
        (
            {
                'initial_sum': {'ride': 200000, 'tips': 100000},
                'sum': {'ride': 200000, 'tips': 0}
            },
            {'ride': 0, 'tips': -100000}
        ),
        (
            {
                'initial_sum': {'ride': 200000, 'tips': 100000},
                'sum': {'ride': 0, 'tips': 100000}
            },
            {'ride': -200000, 'tips': 0}
        ),
        (
            {
                'initial_sum': {'ride': 200000, 'tips': 100000},
                'sum': {}
            },
            {'ride': -200000, 'tips': -100000}
        ),
    ]
)
def test_calc_transaction_resize_delta(transaction, expected_delta):
    delta = payment_handler.calc_transaction_resize_delta(transaction)
    assert delta == expected_delta


@pytest.mark.parametrize(
    'transaction,expected_result',
    [
        ({'status': 'hold_pending'}, False),
        ({'status': 'hold_success'}, False),
        ({'status': 'clear_success'}, False),
        (
            {
                'initial_sum': {'ride': 2840000},
                'sum': {'ride': 3840000},
                'status': 'hold_pending',
            },
            False
        ),
        (
            {
                'sum': {'ride': 3840000},
                'status': 'hold_success',
            },
            False
        ),
        (
            {
                'initial_sum': {'ride': 2840000},
                'sum': {'ride': 2840000},
                'status': 'hold_success',
            },
            False
        ),
        (
            {
                'initial_sum': {'ride': 2840000},
                'sum': {'ride': 2840000},
                'status': 'clear_success',
            },
            False
        ),
        (
            {
                'initial_sum': {'ride': 2840000},
                'sum': {'ride': 2840000, 'tips': 1000000},
                'status': 'clear_success',
            },
            True
        ),
        (
            {
                'initial_sum': {'ride': 2840000, 'tips': 1000000},
                'sum': {'ride': 2840000},
                'status': 'clear_success',
            },
            True
        ),
        (
            {
                'initial_sum': {'ride': 2840000},
                'sum': {'ride': 3840000},
                'status': 'hold_success',
            },
            True
        ),
        (
            {
                'initial_sum': {'ride': 2840000},
                'sum': {'ride': 3840000},
                'status': 'clear_success',
            },
            True
        ),
    ]
)
def test_can_calculate_transaction_resize_delta(transaction, expected_result):
    can_calculate_delta = (
        payment_handler.can_calculate_transaction_resize_delta(transaction)
    )
    assert can_calculate_delta == expected_result


@pytest.mark.now('2017-09-12 10:00:00.00+03')
@pytest.inline_callbacks
def test_store_billing_transaction_stats():
    yield payment_handler._store_billing_transaction_stats('card', 'technical_error')
    docs = yield db.event_stats.find().run()
    assert len(docs) == 1
    doc = docs[0]
    del doc['_id']
    assert doc == {
        'created': datetime.datetime(2017, 9, 12, 7, 0),
        'name': 'billing_transaction_stats',
        'detailed': {
            'card': {
                'technical_error': 1
            }
        },
        'technical_error': 1
    }


@pytest.mark.now('2017-09-12 10:00:00.00+03')
@pytest.inline_callbacks
def test_store_payment_resp_code():
    yield payment_handler._store_payment_resp_code('card', 'expired_card')
    docs = yield db.event_stats.find().run()
    assert len(docs) == 1
    doc = docs[0]
    del doc['_id']
    assert doc == {
        'created': datetime.datetime(2017, 9, 12, 7, 0),
        'name': 'billing_transaction_stats',
        'payment_resp_code': {
            'card': {
                'expired_card': 1
            }
        },
    }


def _invoice_with_maybe_cashback_and_toll_road(cashback=None, toll_road=None):
    return _make_invoice_doc(
            transactions=[
                _make_transaction(
                    status='hold_success',
                    tv=None,
                    refunds=[],
                    ride=50,
                    tips=1,
                    cashback=cashback,
                    toll_road=toll_road,
                )
            ],
            tv=None,
            extra_data={
                'request': {
                    'requirements': {
                        'creditcard': True,
                    }
                },
                'cost': 117,
            },
        )


@pytest.mark.parametrize('order_doc,max_inner_ride_sum,expected_sum', [
    (
        _invoice_with_maybe_cashback_and_toll_road(),
        40,
        {
            'ride': 40,
            'tips': 1,
        }
    ),
    (
        _invoice_with_maybe_cashback_and_toll_road(cashback=50),
        40,
        {
            'ride': 40,
            'tips': 1,
        }
    ),
    (
        _invoice_with_maybe_cashback_and_toll_road(toll_road=10),
        40,
        {
            'ride': 40,
            'toll_road': 10,
            'tips': 1,
        }
    )
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_get_paid_to_park_sum(order_doc, max_inner_ride_sum, expected_sum):
    actual_sum = payment_handler.get_paid_to_park_sum(
        order_doc, max_inner_ride_sum
    )
    assert actual_sum == expected_sum


@pytest.mark.parametrize('order_id,expected_index', [
    ('no_ride_order_id', None),
    ('ride_order_id', 0),
    ('cashback_order_id', 1),
    ('toll_road_order_id', 1),
])
@pytest.mark.filldb(
    orders='for_test_get_last_failed_ride_hold'
)
@pytest.inline_callbacks
def test_get_last_failed_ride_hold(order_id, expected_index):
    order_doc = yield _fetch_order(order_id)
    actual = payment_handler.get_last_failed_ride_hold(order_doc)
    transactions = order_doc['billing_tech']['transactions']
    if expected_index is None:
        assert actual is None
    else:
        assert transactions[expected_index] == actual


@pytest.mark.parametrize(
    'order_id,payment_id,billing_id,expected_index',
    (
        ('without_transactions', 'card-x1234', 'x1234', None),
        ('with_transactions', 'card-x1234', 'x1234', 1),
        ('with_transactions', 'card-x2222', 'x2222', 2),
        ('with_transactions', 'card-x3333', 'x3333', None),
    )
)
@pytest.mark.filldb(orders='for_test_get_last_transaction')
@pytest.inline_callbacks
def test_get_last_transaction(order_id, payment_id, billing_id, expected_index):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    order_doc['payment_tech']['main_card_payment_id'] = payment_id
    order_doc['payment_tech']['main_card_billing_id'] = billing_id
    transactions = order_doc['billing_tech']['transactions']

    last_transaction = payment_handler.get_last_transaction(order_doc)
    if expected_index is None:
        assert last_transaction is None
    else:
        assert last_transaction == transactions[expected_index]


@async.inline_callbacks
def _fetch_order(order_id):
    order_doc = yield db.orders.find_one(order_id)
    assert order_doc is not None, 'order {} doesn\'t exist'.format(order_id)
    async.return_value(order_doc)


@pytest.mark.parametrize('order_id,items,expected', [
    ('paid_only_ride_order_id', ['ride'], True),
    ('paid_only_ride_order_id', ['ride', 'cashback'], False),
    ('paid_only_ride_order_id', ['ride', 'toll_road'], False),
    ('all_paid_order_id', ['ride', 'cashback'], True),
])
@pytest.mark.filldb(
    orders='for_test_all_items_paid'
)
@pytest.inline_callbacks
def test_all_items_paid(order_id, items, expected):
    order_doc = yield _fetch_order(order_id)
    assert payment_handler.all_items_paid(order_doc, items) is expected


@pytest.mark.parametrize('order_id,expected', [
    ('unpaid_ride_order_id', False),
    ('paid_only_ride_order_id', True),
    ('all_paid_order_id', True),
])
@pytest.mark.filldb(
    orders='for_test_all_items_paid'
)
@pytest.inline_callbacks
def test_is_ride_paid(order_id, expected):
    order_doc = yield _fetch_order(order_id)
    assert payment_handler.is_ride_paid(order_doc) is expected


@pytest.mark.parametrize(
    'payable,transaction',
    [
        (
            payment_handler.PayableOrder({
                '_id': 'order-refund-success',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '213.180.219.63',
                    'type': 'card',
                }
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-refund-success-refund-id',
                    'refund_made_at': None,
                    'status': 'refund_pending',
                }],
            }
        ),
        (
            payment_handler.PayableOrder({
                '_id': 'order-refund-still-pending',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '213.180.219.63',
                    'type': 'card',
                }
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-refund-still-pending-refund-id',
                    'refund_made_at': None,
                    'status': 'refund_pending',
                }],
            }
        ),
        (
            payment_handler.PayableInvoice({
                'order_id': 'order-invoice-success',
                'clid': 'clid',
                'currency': 'RUB',
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-invoice-success-refund-id',
                    'status': 'refund_pending',
                }],
            }
        ),
    ]
)
@pytest.inline_callbacks
def test_billing_timeout(patch, payable, transaction):
    @patch('taxi.external.billing._call_billing')
    @async.defer_or_result
    def _call_billing(*args, **kwargs):
        raise billing.TimeoutError

    store_calls = []

    @patch('taxi.external.billing._store_billing_stats')
    def _store_billing_stats(billing_service, method, status, log_extra=None):
        store_calls.append((billing_service, method, status))

    try:
        yield payment_handler._do_refund(
            payable,
            payment_handler.RefundableTransaction(transaction),
            log_extra=None
        )
    except billing.TimeoutError:
        pass
    else:
        assert False

    assert len(store_calls) == 1
    assert store_calls[0] == (
        (yield payable.get_billing()), 'DoRefund', 'timeout',
    )


@pytest.mark.parametrize(
    'payable,transaction',
    [
        (
            payment_handler.PayableOrder({
                '_id': 'order-refund-success',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '213.180.219.63',
                    'type': 'card',
                }
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-refund-success-refund-id',
                    'refund_made_at': None,
                    'status': 'refund_pending',
                }],
            }
        ),
        (
            payment_handler.PayableOrder({
                '_id': 'order-refund-still-pending',
                'user_uid': 'uid',
                'performer': {'clid': 'clid'},
                'payment_tech': {
                    'last_known_ip': '213.180.219.63',
                    'type': 'card',
                }
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-refund-still-pending-refund-id',
                    'refund_made_at': None,
                    'status': 'refund_pending',
                }],
            }
        ),
        (
            payment_handler.PayableInvoice({
                'order_id': 'order-invoice-success',
                'clid': 'clid',
                'currency': 'RUB',
            }),
            {
                'trust_payment_id': 'trust-id',
                'card_owner_uid': 'uid',
                'status': 'refund_pending',
                'holded': datetime.datetime(2016, 8, 4, 19, 0, 0),
                'refunds': [{
                    'trust_refund_id': 'order-invoice-success-refund-id',
                    'status': 'refund_pending',
                }],
            }
        ),
    ]
)
@pytest.inline_callbacks
def test_billing_response_timeout(patch, payable, transaction):
    @patch('taxi.external.billing._call_billing')
    @async.inline_callbacks
    def _call_billing(*args, **kwargs):
        yield async.return_value({'status': 'error', 'status_desc': 'timed out billing'})

    store_calls = []

    @patch('taxi.external.billing._store_billing_stats')
    def _store_billing_stats(billing_service, method, status, log_extra=None):
        store_calls.append((billing_service, method, status))

    try:
        yield payment_handler._do_refund(
            payable,
            payment_handler.RefundableTransaction(transaction),
            log_extra=None
        )
    except billing.TimeoutError:
        pass
    else:
        assert False

    assert len(store_calls) == 1
    assert store_calls[0] == (
        (yield payable.get_billing()), 'DoRefund', 'timeout',
    )


@pytest.mark.now(PAYMENT_NOT_FOUND_AT.isoformat())
@pytest.mark.parametrize(
    'recheck_basket,max_transaction_age,'
    'expected_trans_statuses,expected_comp_statuses',
    [
        (
            False,
            0,
            ['hold_fail', 'hold_success'],
            [
                'compensation_success',
                'compensation_fail',
                'compensation_fail',
                'compensation_success',
            ]
        ),
        # all not found transactions/compensations are not too old,
        # so we don't touch them
        (
            True,
            86400,
            ['hold_pending', 'hold_success'],
            [
                'compensation_success',
                'compensation_init',
                'compensation_pending',
                'compensation_waiting_for_refunds',
            ]
        ),
        # pending transaction is too old, so we fail it
        (
            True,
            3600,
            ['hold_fail', 'hold_success'],
            [
                'compensation_success',
                'compensation_init',
                'compensation_pending',
                'compensation_waiting_for_refunds',
            ]
        ),
    ]
)
@pytest.inline_callbacks
def test_payment_not_found(patch, recheck_basket, max_transaction_age,
                           expected_trans_statuses, expected_comp_statuses):
    @patch('taxi.external.billing._call_simple')
    @async.defer_or_result
    def _call_simple(*args, **kwargs):
        raise billing.PaymentNotFoundError

    yield config.BILLING_RECHECK_BASKET_ON_NOT_FOUND.save(recheck_basket)
    yield config.BILLING_MAX_NOT_FOUND_BASKET_AGE.save(max_transaction_age)

    order_doc = yield db.orders.find_one({'_id': 'pay_basket_check'})
    payable = payment_handler.PayableOrder(order_doc)
    payment_handler.refresh_pending_transactions(payable)
    payment_handler.refresh_pending_compensations(order_doc)

    trans_statuses = []
    comp_statuses = []
    for tran in order_doc['billing_tech']['transactions']:
        trans_statuses.append(tran['status'])
    for comp in order_doc['billing_tech']['compensations']:
        comp_statuses.append(comp['status'])

    assert trans_statuses == expected_trans_statuses
    assert comp_statuses == expected_comp_statuses


@pytest.mark.parametrize(
    'check_status,expected_compensation_statuses,raises_exc',
    [
        (
            'success',
            ['compensation_pending', 'compensation_waiting_for_refunds'],
            True,
        ),
        (
            'waiting',
            ['compensation_pending', 'compensation_success'],
            False,
        ),
        (
            'cancelled',
            ['compensation_pending', 'compensation_success'],
            False,
        )
    ]
)
@pytest.inline_callbacks
def test_check_for_compensation_refunds_is_initiated(
        patch, check_status, expected_compensation_statuses, raises_exc):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield async.return_value({'status': check_status})

    order_doc = yield db.orders.find_one({'_id': 'check_for_compensations'})
    payable = payment_handler.PayableOrder(order_doc)
    if raises_exc:
        with pytest.raises(payment_handler.TransactionInProgress):
            yield payment_handler.refresh_pending_transactions(payable)
    else:
        payment_handler.refresh_pending_transactions(payable)
        comp_statuses = []
        for comp in order_doc['billing_tech']['compensations']:
            comp_statuses.append(comp['status'])
            if comp['status'] == 'compensation_waiting_for_refunds':
                assert comp['check_for_refunds_attempts'] == 0
        assert comp_statuses == expected_compensation_statuses


@pytest.mark.parametrize(
    'billing_response,expected_compensations',
    [
        (
            {},  # no refunds
            [
                {
                    'status': 'compensation_waiting_for_refunds',
                    'sum': {'ride': 2990000},
                    'trust_payment_id': 'compensation_1',
                    'check_for_refunds_attempts': 1,
                    'compensation_made_at': datetime.datetime(2018, 1, 11, 12),
                    'updated': datetime.datetime(2018, 1, 11, 15),
                },
                {
                    'status': 'compensation_waiting_for_refunds',
                    'sum': {'ride': 2990000},
                    'trust_payment_id': 'compensation_2',
                    'check_for_refunds_attempts': 1,
                    'compensation_made_at': datetime.datetime(2018, 1, 11, 12),
                    'updated': datetime.datetime(2018, 1, 11, 15),
                    'refunds': [
                        {
                            'created': datetime.datetime(2018, 1, 11, 13),
                            'data': None,
                            'refund_made_at': (
                                datetime.datetime(2018, 1, 11, 14)
                            ),
                            'status': 'refund_success',
                            'sum': {'ride': 100000},
                            'trust_refund_id': 'refund_1',
                            'updated': datetime.datetime(2018, 1, 11, 14),
                        }
                    ]
                },
                {
                   'status': 'compensation_success',
                   'sum': {'ride': 2990000},
                   'trust_payment_id': 'compensation_3',
                   'check_for_refunds_attempts': 3,
                   'compensation_made_at': datetime.datetime(2018, 1, 11, 12),
                   'updated': datetime.datetime(2018, 1, 11, 15),
                }
            ]
        ),
        (
            {  # two refunds
                'refunds': [
                    {'trust_refund_id': 'refund_1', 'amount': '10.0'},
                    {'trust_refund_id': 'refund_2', 'amount': '20.0'}
                ]
            },
            [
                {
                    'status': 'compensation_waiting_for_refunds',
                    'sum': {'ride': 2990000},
                    'trust_payment_id': 'compensation_1',
                    'check_for_refunds_attempts': 1,
                    'compensation_made_at': datetime.datetime(2018, 1, 11, 12),
                    'updated': datetime.datetime(2018, 1, 11, 15),
                    'refunds': [
                        {
                            'created': datetime.datetime(2018, 1, 11, 15),
                            'data': None,
                            'refund_made_at': None,
                            'status': 'refund_pending',
                            'sum': {'ride': 100000},
                            'trust_refund_id': 'refund_1',
                            'updated': datetime.datetime(2018, 1, 11, 15),
                        },
                        {
                            'created': datetime.datetime(2018, 1, 11, 15),
                            'data': None,
                            'refund_made_at': None,
                            'status': 'refund_pending',
                            'sum': {'ride': 200000},
                            'trust_refund_id': 'refund_2',
                            'updated': datetime.datetime(2018, 1, 11, 15),
                        }
                    ]
                },
                {
                    'status': 'compensation_waiting_for_refunds',
                    'sum': {'ride': 2990000},
                    'trust_payment_id': 'compensation_2',
                    'check_for_refunds_attempts': 1,
                    'compensation_made_at': datetime.datetime(2018, 1, 11, 12),
                    'updated': datetime.datetime(2018, 1, 11, 15),
                    'refunds': [
                        {
                            'created': datetime.datetime(2018, 1, 11, 13),
                            'data': None,
                            'refund_made_at': (
                                datetime.datetime(2018, 1, 11, 14)
                            ),
                            'status': 'refund_success',
                            'sum': {'ride': 100000},
                            'trust_refund_id': 'refund_1',
                            'updated': datetime.datetime(2018, 1, 11, 14),
                        },
                        {
                            'created': datetime.datetime(2018, 1, 11, 15),
                            'data': None,
                            'refund_made_at': None,
                            'status': 'refund_pending',
                            'sum': {'ride': 200000},
                            'trust_refund_id': 'refund_2',
                            'updated': datetime.datetime(2018, 1, 11, 15),
                        }
                    ]
                },
                {
                   'status': 'compensation_success',
                   'sum': {'ride': 2990000},
                   'trust_payment_id': 'compensation_3',
                   'check_for_refunds_attempts': 3,
                   'compensation_made_at': datetime.datetime(2018, 1, 11, 12),
                   'updated': datetime.datetime(2018, 1, 11, 15),
                   'refunds': [
                        {
                            'created': datetime.datetime(2018, 1, 11, 15),
                            'data': None,
                            'refund_made_at': None,
                            'status': 'refund_pending',
                            'sum': {'ride': 100000},
                            'trust_refund_id': 'refund_1',
                            'updated': datetime.datetime(2018, 1, 11, 15),
                        },
                        {
                            'created': datetime.datetime(2018, 1, 11, 15),
                            'data': None,
                            'refund_made_at': None,
                            'status': 'refund_pending',
                            'sum': {'ride': 200000},
                            'trust_refund_id': 'refund_2',
                            'updated': datetime.datetime(2018, 1, 11, 15),
                        }
                    ]
                }
            ]
        ),
    ]
)
@pytest.mark.now('2018-01-11T15:00:00')
@pytest.mark.config(BILLING_COMPENSATION_REFUND_CHECK_ATTEMPTS=3)
@pytest.inline_callbacks
def test_check_for_compensation_refunds(
        patch, billing_response, expected_compensations):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield async.return_value(billing_response)

    order_doc = yield db.orders.find_one({
        '_id': 'check_for_compensation_refunds'
    })
    payment_handler.refresh_pending_compensations(order_doc)
    for compensation in order_doc['billing_tech']['compensations']:
        del compensation['billing_response']
        for refund in compensation.get('refunds', []):
            del refund['billing_response']
    assert order_doc['billing_tech']['compensations'] == expected_compensations


@pytest.mark.parametrize(
    'billing_response,expected_refunds',
    [
        (
            {'status': 'success'},
            [
                {
                    'created': datetime.datetime(2018, 1, 11, 14),
                    'data': None,
                    'refund_made_at': datetime.datetime(2018, 1, 11, 15),
                    'billing_response': {'status': 'success'},
                    'status': 'refund_success',
                    'sum': {'ride': 100000},
                    'trust_refund_id': 'refund_1',
                    'updated': datetime.datetime(2018, 1, 11, 15),
                }
            ]
        ),
        (
            {'status': 'waiting'},
            [
                {
                    'created': datetime.datetime(2018, 1, 11, 14),
                    'data': None,
                    'refund_made_at': None,
                    'billing_response': None,
                    'status': 'refund_pending',
                    'sum': {'ride': 100000},
                    'trust_refund_id': 'refund_1',
                    'updated': datetime.datetime(2018, 1, 11, 14),
                }
            ]
        )
    ]
)
@pytest.mark.now('2018-01-11T15:00:00')
@pytest.mark.config(BILLING_COMPENSATION_REFUND_CHECK_ATTEMPTS=3)
@pytest.inline_callbacks
def test_compensation_refund_processing(
        patch, billing_response, expected_refunds):
    @patch('taxi.external.billing.do_refund')
    @async.inline_callbacks
    def do_refund(*args, **kwargs):
        yield async.return_value(billing_response)

    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({
            'status': 'success',
            'terminal': {'id': 42},
        })

    order_doc = yield db.orders.find_one({
        '_id': 'compensation_refund_processing'
    })
    payment_handler.refresh_pending_compensations(order_doc)
    refunds = order_doc['billing_tech']['compensations'][0]['refunds']
    assert refunds[0] == expected_refunds[0]
    if billing_response == 'success':
        comp = order_doc['billing_tech']['compensations'][0]
        assert comp['terminal_id'] == 42


@pytest.inline_callbacks
def test_pending_compensation_and_pending_hold(patch):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({'status': 'success'})

    order_id = 'compensation_pending_hold_pending'
    yield invoice_handler._update_transactions_iteration(order_id)
    order_doc = yield db.orders.find_one({'_id': order_id})
    assert check_basket.calls[0]['args'] == (
        'card', 'multitrans_user_uid', '2a02:6b8:0:845::1:2', 'compensation_1')
    assert order_doc['billing_tech']['compensations'][0]['status'] == (
        'compensation_success')
    assert order_doc['billing_tech']['transactions'][1]['status'] == (
        'hold_pending')

    yield invoice_handler._update_transactions_iteration(order_id)
    order_doc = yield db.orders.find_one({'_id': order_id})
    assert check_basket.calls[0]['args'] == (
        'card', 'owner_uid', '2a02:6b8:0:845::1:2', 'transaction_1')
    assert order_doc['billing_tech']['compensations'][0]['status'] == (
        'compensation_waiting_for_refunds')
    assert order_doc['billing_tech']['transactions'][1]['status'] == (
        'hold_success')
    assert order_doc['payment_tech']['debt'] is False


@pytest.mark.parametrize(
    'order_id',
    [
        'terminal_id_everywhere_hold_pending',
        'terminal_id_everywhere_clear_pending',
        'terminal_id_everywhere_compensation_pending',
        'terminal_id_everywhere_refund_pending',
    ],
)
@pytest.mark.config(REQUEST_TERMINAL_ID_WHEN_REFUNDING=True)
@pytest.inline_callbacks
def test_terminal_id_everywhere(patch, order_id):
    @patch('taxi.external.billing._do_basket')
    @async.inline_callbacks
    def do_basket(*args, **kwargs):
        yield
        async.return_value({'status': 'success', 'terminal': {'id': 42}})

    @patch('taxi.internal.order_kit.payment_handler._do_refund')
    @async.inline_callbacks
    def do_refund(*args, **kwargs):
        yield
        async.return_value(True)

    yield invoice_handler._update_transactions_iteration(order_id)
    assert do_basket.calls[0]['kwargs']['with_terminal_info'] == 1

    order_doc = yield db.orders.find_one({'_id': order_id})
    billing_tech = order_doc['billing_tech']
    print(billing_tech)
    try:
        assert billing_tech['transactions'][0]['terminal_id'] == 42
    except IndexError:
        assert billing_tech['compensations'][0]['terminal_id'] == 42


@pytest.mark.now('2019-09-12T09:09:24.000')
@pytest.mark.config(BILLING_COMPENSATION_REFUND_CHECK_ATTEMPTS=1)
@pytest.inline_callbacks
def test_refunded_compensation_and_pending_hold(patch):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value(
            {
                'status': 'refund',
                'real_postauth_ts': '2019-09-05T10:27:42+03:00',
                'refunds': [
                    {
                        'confirm_ts': '2019-09-05T10:32:00+03:00',
                        'description': 'CompensationRefund',
                        'create_ts_msec': '1567668720732',
                        'trust_refund_id': '5d70b9f05a39511fe8848a55',
                        'confirm_ts_msec': '1567668720000',
                        'amount': '72.00',
                        'create_ts': '2019-09-05T10:32:00+03:00',
                    },
                ],
            }
        )

    order_id = 'compensation_pending_hold_pending'
    yield invoice_handler._update_transactions_iteration(order_id)
    order_doc = yield db.orders.find_one({'_id': order_id})
    assert order_doc['billing_tech']['compensations'][0]['status'] == (
        'compensation_success')
    assert order_doc['billing_tech']['compensations'][0]['refunds'] == [
        {
            'status': 'refund_pending',
            'billing_response': None,
            'updated': datetime.datetime(2019, 9, 12, 9, 9, 24),
            'created': datetime.datetime(2019, 9, 12, 9, 9, 24),
            'sum': {'ride': 720000},
            'trust_refund_id': '5d70b9f05a39511fe8848a55',
            'refund_made_at': None,
            'data': None,
        }
    ]
    assert order_doc['billing_tech']['transactions'][1]['status'] == (
        'hold_pending')


@pytest.mark.config(RETRY_HOLD_ON_TECHNICAL_ERRORS=True)
@pytest.inline_callbacks
def test_dont_commit_transactions_on_technical_error(patch):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({
            'status': 'cancelled',
            'status_desc': 'http 500 Internal Server Error'
        })

    @patch('taxi.internal.order_kit.payment_handler.PayableOrder.commit_payments')
    @async.inline_callbacks
    def commit_payments(*args, **kwargs):
        yield

    order_doc = yield db.orders.find_one({'_id': 'pay_basket_check'})
    payable = payment_handler.PayableOrder(order_doc)
    payment_handler.refresh_pending_transactions(payable)
    assert len(commit_payments.calls) == 0


COOP_RESPONSE = coop_client.PaymentResponse(
    owner_uid='123',
    payment_method_id='payment_id',
    billing_id='billing_id',
    persistent_id='persistent_id',
)


@pytest.mark.filldb(orders='coop_account')
@pytest.inline_callbacks
def test_payable_coop_init(patch):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        async.return_value(COOP_RESPONSE)

    order_doc = yield db.orders.find_one({'_id': 'order-hold-coop'})
    payable = coop_payable.PayableOrderCoop(order_doc)
    yield payable.init_payment()

    assert (yield payable.get_payment_uid()) == '123'
    assert (yield payable.persistent_id) == 'persistent_id'


@pytest.mark.filldb(orders='coop_account')
@pytest.inline_callbacks
def test_payable_coop_init_fallback(patch):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        raise coop_client.ClientError

    order_doc = yield db.orders.find_one({'_id': 'order-coop-fallback'})
    payable = coop_payable.PayableOrderCoop(order_doc)
    yield payable.init_payment()

    assert payable._owner_uid == '12345'
    assert payable._payment_method_id == 'payment_id'
    assert payable._billing_id == 'billing_id'


@pytest.mark.parametrize('order_id,to_hold,expected_call', [
    (
            'order-hold-coop',
            {'ride': 100000},
            {
                'args': (
                        'card', '123', '127.0.0.1', 'RUB',
                        [
                            {
                                'fiscal_nds': 'nds_0',
                                'fiscal_title': 'Taxi ride',
                                'price': 10.0,
                                'service_order_id': None
                            }
                        ],
                        'payment_id'
                ),
                'kwargs': {
                    'check_card': True,
                    'log_extra': None,
                    'order_tag': None,
                    'pass_params': None,
                    'user_phone': None,
                    'uber_uid': None,
                    'wait_for_cvn_timeout': None
                }
            }
    ),
])
@pytest.mark.translations([
    ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'Taxi ride'),
])
@pytest.mark.filldb(orders='coop_account')
@pytest.mark.config(BILLING_FISCAL_RECEIPT_ENABLED=True)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_coop_account_hold(patch, order_id, to_hold, expected_call):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        async.return_value(COOP_RESPONSE)

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value('trust_payment_id')

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)

    payable = coop_payable.PayableOrderCoop(order_doc)
    yield payable.init_payment()
    assert (yield payable.get_payment_uid()) == COOP_RESPONSE.owner_uid

    hold_options = payment_handler.HoldOptions(can_hold=True, with_cvn=False)
    yield payable.hold(to_hold, hold_options, None, None, log_extra=None)

    call = create_basket.calls[0]
    assert call['args'] == expected_call['args']
    assert call['kwargs']['pass_params']['payed_by'] == 'coop_account'

    assert order_doc['billing_tech']['transactions']
    for transaction in order_doc['billing_tech']['transactions']:
        assert transaction['initial_sum'] == transaction['sum']
        assert transaction['status'] == const.HOLD_INIT
        assert transaction['card_payment_id'] == COOP_RESPONSE.payment_method_id
        assert transaction['card_billing_id'] == COOP_RESPONSE.billing_id
        assert transaction['payment_method_type'] == 'card'


@pytest.mark.filldb(
    orders='family',
    cards='family',
    users='family',
    phones_confirmations='family',
)
@pytest.mark.config(DEBTS_ENABLED_PROCESSING_PY2=True)
@pytest.mark.now('2019-02-07 20:00:00.00+03')
@pytest.mark.parametrize('has_owner_family_info', [False, True])
@pytest.mark.parametrize('order_id', ['order-family-member', 'order-family-owner'])
@pytest.inline_callbacks
def test_family_card_debt(
    patch,
    order_id,
    has_owner_family_info,
):

    if not has_owner_family_info:
        yield db.cards.update(
            {'owner_uid': 'family_owner_uid'}, {'$unset': {'family': 1}}
        )

    @patch('taxi.config.COOP_ACCOUNT_IGNORE_DEBT.get')
    @async.inline_callbacks
    def get_config_ignore_debt():
        yield
        async.return_value(False)

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value('trust_payment_id')

    @patch('taxi.external.userapi.users_search')
    @async.inline_callbacks
    def users_search(yandex_uid=None, phone_ids=None, fields=None, **kwargs):
        assert fields == ['id', 'updated']
        assert len(phone_ids) == 1
        assert yandex_uid
        items = yield dbh.users.Doc.find_many(
            query={
                'phone_id': bson.ObjectId(phone_ids[0]),
                'yandex_uid': yandex_uid
            },
            fields=['_id', 'updated'],
        )
        for item in items:
            item['id'] = item.pop('_id')
        async.return_value({'items': items})

    @patch('taxi_stq._client.put')
    @pytest.inline_callbacks
    def mock_debts_processing(queue, eta=None, task_id=None, args=None, kwargs=None):
        assert queue == 'debts_processing'
        assert args == (order_id, 'set_debt', datetime.datetime(2019, 2, 7, 12, 0))
        if order_id == 'order-family-member' and has_owner_family_info:
            assert kwargs['locked_phone_id'] == '70686f6e655f696450000006'
        else:
            assert kwargs.get('locked_phone_id') is None
        yield

    order_doc = db.orders.find_one(order_id).result
    payment_fail = yield antifraud.PaymentFail.from_last_transaction(
        order_doc, None,
    )
    yield invoice_handler._mark_ride_as_debt(order_doc, payment_fail, None)
    order_doc = db.orders.find_one(order_id).result

    unpaid_order_ids_device = yield dbh.phonelocks.Doc.get_unpaid_order_ids(
        order_doc['user_phone_id']
    )
    unpaid_order_ids_phone = yield dbh.devicelocks.Doc.get_unpaid_order_ids(
        order_doc['user_id']
    )
    unpaid_order_ids_card = yield dbh.cardlocks.Doc.get_unpaid_order_ids(
        order_doc['payment_tech']['main_card_persistent_id']
    )

    if order_id == 'order-family-member' and has_owner_family_info:
        # Owner locked
        assert (yield dbh.devicelocks.Doc.get_unpaid_order_ids('family_owner_user_id'))
        assert (yield dbh.phonelocks.Doc.get_unpaid_order_ids(bson.ObjectId('70686f6e655f696450000006')))
        # owner card has the same persistent_id and is blocked
        assert unpaid_order_ids_card
        assert not unpaid_order_ids_phone
        assert not unpaid_order_ids_device
    else:
        assert unpaid_order_ids_card
        assert unpaid_order_ids_phone
        assert unpaid_order_ids_device

    assert len(mock_debts_processing.calls) == 1


@pytest.mark.filldb(orders='coop_account')
@pytest.inline_callbacks
def test_coop_account_4xx(patch):
    @patch('taxi.external.billing.pay_basket')
    @async.inline_callbacks
    def _pay_basket(*args, **kwargs):
        yield
        async.return_value({})

    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        raise coop_client.ClientError

    yield invoice_handler._update_transactions_iteration('coop-account-4xx')

    order_doc = yield dbh.orders.Doc.find_one_by_id('coop-account-4xx')
    payable = coop_payable.PayableOrderCoop(order_doc)
    for tran in payable.transactions:
        assert tran['status'] == const.HOLD_FAIL
    assert payable.doc['payment_tech']['debt']


@pytest.inline_callbacks
def test_coop_account_activate(patch):
    @patch('taxi.internal.coop_account.client.activate_account')
    @async.inline_callbacks
    def _activate_account(account_id, order_id, **kwargs):
        yield
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id('order_coop_1')
    coop_payable.activate_coop_account(order_doc)
    assert _activate_account.calls[0]['args'] == ('coop_account_id', )


@pytest.inline_callbacks
def test_coop_account_deactivate(patch):
    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        async.return_value(COOP_RESPONSE)

    @patch('taxi.internal.coop_account.client.deactivate_account')
    @async.inline_callbacks
    def _deactivate_account(account_id, order_id, **kwargs):
        yield
        assert account_id == 'coop_account_id'
        async.return_value({})

    order_doc = yield dbh.orders.Doc.find_one_by_id('order_coop_1')

    coop_payable.deactivate_coop_account(order_doc)
    assert _deactivate_account.calls[0]['args'] == ('coop_account_id', )


@pytest.mark.filldb(orders='coop_account')
@pytest.mark.now('2019-02-07 20:00:00.00+03')
@pytest.mark.config(BILLING_COOP_ACCOUNT_ENABLED=True)
@pytest.mark.config(COOP_ACCOUNT_GET_DEBTS_FROM_LOCKS=True)
@pytest.mark.parametrize(
    'config_ignore_debt,config_send_order_id',
    [
        (True, True),
        (True, False),
        (False, False),
    ],
)
@pytest.inline_callbacks
def test_coop_account_debt(patch, config_ignore_debt, config_send_order_id):
    debt_order_id = 'coop-account-empty' if config_send_order_id else None

    @patch('taxi.config.COOP_ACCOUNT_IGNORE_DEBT.get')
    @async.inline_callbacks
    def get_config_ignore_debt():
        yield
        async.return_value(config_ignore_debt)

    @patch('taxi.config.COOP_ACCOUNT_DO_SEND_ORDER_ID.get')
    @async.inline_callbacks
    def get_config_send_order_id():
        yield
        async.return_value(config_send_order_id)

    @patch('taxi.internal.coop_account.client.deactivate_account')
    @async.inline_callbacks
    def _deactivate_account(account_id, order_id, **kwargs):
        yield
        assert order_id == debt_order_id
        async.return_value({})

    @patch('taxi.internal.coop_account.client.payment_info')
    @async.inline_callbacks
    def _payment_info(*args, **kwargs):
        yield
        async.return_value(COOP_RESPONSE)

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        async.return_value('trust_payment_id')

    yield invoice_handler._update_transactions_iteration('coop-account-empty')
    order_doc = db.orders.find_one('coop-account-empty').result
    payable = coop_payable.PayableOrderCoop(order_doc)

    for transaction in payable.transactions:
        assert transaction['status'] == 'hold_fail'

    assert payable.order_doc['payment_tech']['debt'] is True
    can_hold, _ = yield payable.get_hold_options(None)
    assert can_hold is False

    unpaid_order_ids_device = yield dbh.phonelocks.Doc.get_unpaid_order_ids(
        payable.order_doc['user_phone_id']
    )
    unpaid_order_ids_phone = yield dbh.devicelocks.Doc.get_unpaid_order_ids(
        payable.order_doc['user_id']
    )
    unpaid_order_ids_card = yield dbh.cardlocks.Doc.get_unpaid_order_ids(
        COOP_RESPONSE.persistent_id
    )
    if config_ignore_debt:
        call_0 = _deactivate_account.calls[0]
        assert call_0['args'] == ('coop-1234',)
        assert call_0['kwargs'] == {
            'order_id': debt_order_id,
            'total_price': order_doc.get('current_prices', {}).get('user_total_price'),
            'user_uid': order_doc.get('user_uid'),
        }
        assert not unpaid_order_ids_phone
        assert not unpaid_order_ids_device
        assert unpaid_order_ids_card

        # Owner locked
        assert (yield dbh.devicelocks.Doc.get_unpaid_order_ids('user_id_1'))
        assert (yield dbh.phonelocks.Doc.get_unpaid_order_ids(bson.ObjectId('70686f6e655f696450000004')))
    else:
        assert not _deactivate_account.calls
        assert unpaid_order_ids_phone
        assert unpaid_order_ids_device
        assert not unpaid_order_ids_card


@pytest.mark.parametrize('order_doc,expected_billing_service', [
    ({'payment_tech': {'type': 'corp'}}, 'corp'),
    ({'payment_tech': {'type': 'card'}}, 'card'),
    ({}, 'card'),
    ({'source': 'yandex'}, 'card'),
    ({'source': 'yandex', 'statistics': {'application': 'android'}}, 'card'),
    (
        {'source': 'yauber', 'statistics': {'application': 'uber_android'}},
        'uber'
    ),
])
@pytest.mark.parametrize('billing_by_brand_enabled', [False, True])
@pytest.inline_callbacks
def test_payable_order_get_billing(
        order_doc, expected_billing_service, billing_by_brand_enabled,
):
    yield config.BILLING_SERVICE_NAME_MAP_BY_BRAND_ENABLED.save(
        billing_by_brand_enabled,
    )
    payable_order = payment_handler.PayableOrder(order_doc)
    assert (yield payable_order.get_billing()) == expected_billing_service


@pytest.mark.parametrize('order_doc,expected', [
    (
        {
            'payment_tech': {
                'complements': [
                    {
                        'type': 'personal_wallet',
                        'payment_method_id': 'wallet_id/2',
                    }
                ]
            }
        },
        [
            payable_module.ComplementPaymentMethod(
                type='personal_wallet',
                id='wallet_id/2',
                withdraw_amount=None,
            )
        ],
    ),
    (
            {
                'payment_tech': {
                    'complements': [
                        {
                            'type': 'personal_wallet',
                            'payment_method_id': 'wallet_id/2',
                            'withdraw_amount': 99.99
                        }
                    ]
                }
            },
            [
                payable_module.ComplementPaymentMethod(
                    type='personal_wallet',
                    id='wallet_id/2',
                    withdraw_amount=99.99,
                )
            ],
    ),
    ({'payment_tech': {}}, []),
])
def test_payable_complements(order_doc, expected):
    payable = payment_handler.PayableOrder(order_doc)
    assert payable.complements == expected


@pytest.mark.parametrize(
    (
        'order_id,'
        'is_py2_processing,'
        'expected_just_closed,'
        'expected_to_resize_or_refund,'
        'expected_result,'
        'num_resize_or_refund_calls,'
        'num_try_update_from_just_closed_calls,'
    ),
    [
        (
            'just_closed_wallet_order_id',
            True,
            None,
            {'ride': 600000},
            True,
            1,
            0,
        ),
        (
            'just_closed_wallet_order_id',
            False,
            None,
            {'ride': 600000},
            True,
            0,
            1,
        ),
        (
            'just_closed_cash_order_id',
            True,
            True,
            None,
            False,
            0,
            0,
        ),
        (
            'not_just_closed_wallet_order_id',
            True,
            None,
            None,
            False,
            0,
            0,
        ),
    ]
)
@pytest.mark.filldb(orders='for_test_payable_before_update_transactions_dirty')
@pytest.inline_callbacks
def test_payable_before_update_transactions_dirty(
        patch,
        order_id,
        is_py2_processing,
        expected_just_closed,
        expected_to_resize_or_refund,
        expected_result,
        num_resize_or_refund_calls,
        num_try_update_from_just_closed_calls,
        mock_send_event,
):
    @patch('taxi.internal.order_kit.payment_handler._resize_or_refund')
    @async.inline_callbacks
    def _resize_or_refund(payable, to_resize_or_refund, log_extra=None):
        assert to_resize_or_refund == expected_to_resize_or_refund
        yield

    expected_intent = 'test_intent'

    @patch(
        'taxi.internal.payment_kit.invoices.InvoiceV2.'
        'try_update_from_just_closed'
    )
    @async.inline_callbacks
    def try_update_from_just_closed(
            payable_order, need_cvn, intent=None, log_extra=None):
        assert not need_cvn
        assert intent == expected_intent
        async.return_value(True)
        yield

    @patch('taxi.internal.order_kit.payment_handler.PayableOrder.payment_split')
    @async.inline_callbacks
    def payment_split(to_hold, log_extra=None):
        split = plus_wallet_service.PaymentSplit(
            elements=[
                plus_wallet_service.SplitElement(
                    type='personal_wallet',
                    payment_method_id='wallet_id/2',
                    sum=decimal.Decimal('60'),
                    sum_type='ride',
                ),
                plus_wallet_service.SplitElement(
                    type='card',
                    payment_method_id='card-2',
                    sum=decimal.Decimal('40'),
                    sum_type='ride',
                )
            ],
            currency='RUB',
        )
        async.return_value(split)
        yield

    if is_py2_processing:
        processing = invoices.processing_via_py2()
    else:
        processing = invoices.processing_via_transactions(
            invoices.InvoiceV2({})
        )

    payable = yield payable_from_order_id(order_id)
    result = yield payable.before_update_transactions_dirty(
        processing=processing,
        intent=expected_intent,
        log_extra=None,
    )
    assert result is expected_result

    just_closed = payable.order_doc['payment_tech'].get(
        'just_closed'
    )
    assert just_closed is expected_just_closed
    assert len(_resize_or_refund.calls) == num_resize_or_refund_calls
    assert len(try_update_from_just_closed.calls) == (
            num_try_update_from_just_closed_calls
    )


@pytest.mark.parametrize('order_id,expected_index', [
    ('happy_path_order_id', 0),
    ('successful_order_id', 1),
    ('second_with_next_order_id', 2),
    ('no_next_order_id', None),
])
@pytest.mark.filldb(orders='for_test_get_transaction_with_pending_next')
@pytest.inline_callbacks
def test_get_transaction_with_pending_next(order_id, expected_index):
    payable = yield payable_from_order_id(order_id)
    i, transaction = payment_handler._get_transaction_with_pending_next(
        payable
    )
    assert i == expected_index
    if expected_index is None:
        assert transaction is None
    else:
        assert payable.transactions[i] is transaction


@pytest.mark.parametrize('order_id,expected', [
    ('not_composite_order_id', False),
    ('not_finished_order_id', True),
    ('with_composite_transactions_order_id', True),
    ('changed_by_support_order_id', False),
    ('without_composite_transactions_order_id', True),
])
@pytest.mark.filldb(orders='for_test_need_to_ask_for_split')
@pytest.inline_callbacks
def test_needs_to_ask_for_split(order_id, expected):
    payable = yield payable_from_order_id(order_id)
    assert payable.needs_to_ask_for_split is expected


@pytest.mark.parametrize('order_id,expected', [
    (
        'composite_order_id',
        [
            {
                'id_for_tests': 2,
                'payment_method_type': 'card'
            },
            {
                'id_for_tests': 3,
                'payment_method_type': 'card'
            },
            {
                'id_for_tests': 1,
                'payment_method_type': 'personal_wallet'
            }
        ]
    )
])
@pytest.mark.filldb(orders='for_test_transactions_in_refund_order')
@pytest.inline_callbacks
def test_transactions_in_refund_order(order_id, expected):
    payable = yield payable_from_order_id(order_id)
    assert payable.transactions_in_refund_order == expected


@pytest.mark.parametrize(
    'order_id,expected_num_complements,expected_refund_calls', [
        ('composite_failed_with_previous_order_id', 0, 1),
        ('composite_failed_no_previous_order_id', 1, 0),
    ]
)
@pytest.mark.filldb(orders='for_test_on_hold_fail')
@pytest.inline_callbacks
def test_on_hold_fail(
        patch, order_id, expected_num_complements, expected_refund_calls
):
    @patch(
        'taxi.internal.order_kit.personal_wallet_payment_gateway.'
        'start_new_refund'
    )
    def start_new_refund(payable, tran, refund_sum, log_extra=None):
        assert payable is payable_order
        assert refund_sum == {'ride': 300000}
        assert tran is payable_order.transactions[0]
    payable_order = yield payable_from_order_id(order_id)
    yield payable_order.on_hold_fail(payable_order.transactions[1])
    assert len(payable_order.complements) == expected_num_complements
    assert len(start_new_refund.calls) == expected_refund_calls


@pytest.mark.parametrize(
    'order_id,expected_num_complements,expected_num_split_attempts', [
        ('exceeded_order_id', 0, 5),
        ('not_exceeded_order_id', 1, 3),
    ]
)
@pytest.mark.filldb(orders='for_test_on_plus_wallet_service_error')
@pytest.inline_callbacks
def test_on_plus_wallet_service_error(
        order_id, expected_num_complements, expected_num_split_attempts):
    payable = yield payable_from_order_id(order_id)
    yield payable.on_plus_wallet_service_error(ValueError())
    payable = yield payable_from_order_id(order_id)
    actual_num_split_attempts = (
        payable.order_doc['billing_tech']['split_attempts']
    )
    assert actual_num_split_attempts == expected_num_split_attempts
    assert len(payable.complements) == expected_num_complements


@async.inline_callbacks
def payable_from_order_id(order_id):
    order_doc = yield invoice_handler._get_order_doc(order_id)
    msg = 'can\'t find order with id `{}`'.format(order_id)
    assert order_doc is not None, msg
    payable = payment_handler.PayableOrder(order_doc)
    async.return_value(payable)


@pytest.mark.parametrize('order_id,tariff,user_locale,to_hold,expected_fiscal_title', [
    ('order-fiscal-title', 'econom', 'ru', {'ride': 100000}, 'Taxi ride'),
    ('order-fiscal-title', 'econom', 'fr', {'ride': 100000}, 'EN Taxi ride'),
    ('order-fiscal-title', 'express', 'ru', {'ride': 100000}, 'Taxi ride express'),
    ('order-fiscal-title', 'cargo', 'ru', {'ride': 100000}, 'Taxi ride cargo'),
])
@pytest.mark.translations([
    ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'Taxi ride'),
    ('client_messages', 'fiscal_receipt.title.rus', 'en', 'EN Taxi ride'),
    ('client_messages', 'fiscal_receipt.title.rus.express', 'ru', 'Taxi ride express'),
    ('client_messages', 'fiscal_receipt.title.rus.cargo', 'ru', 'Taxi ride cargo'),
])
@pytest.mark.filldb(orders='fiscal_title')
@pytest.mark.config(
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    FISCAL_TITLE_TARIFF_CLASSES=['express', 'cargo']
)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_fiscal_title(patch, order_id, tariff, user_locale, to_hold, expected_fiscal_title):
    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield async.return_value({})

    order_doc = yield db.orders.find_one({'_id': order_id})
    order_doc['performer']['tariff']['class'] = tariff
    order_doc['user_locale'] = user_locale
    yield payment_handler._hold_card(
        order_doc, to_hold, with_cvn=False, previous_index=None,
        log_extra=None
    )
    assert create_basket.calls[0]['args'][4][0]['fiscal_title'] == expected_fiscal_title


class NoExpectation(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.parametrize('order_id,validate_decoupling,expectation', [
    ('isr_new_order_id', False, NoExpectation()),
    ('isr_old_order_id', False, NoExpectation()),
    ('isr_decoupling_order_id', False, NoExpectation()),
    ('isr_decoupling_order_id', True, NoExpectation()),
    (
        'default_new_order_id',
        False,
        pytest.raises(payment_handler.CorpViaTrustDisabledError)
    ),
    ('default_card_order_id', False, NoExpectation()),
    ('default_old_order_id', False, NoExpectation()),
    ('default_decoupling_order_id', False, NoExpectation()),
    (
        'default_decoupling_order_id',
        True,
        pytest.raises(payment_handler.CorpViaTrustDisabledError)
    ),
    ('rus_new_order_id', False, NoExpectation()),
    ('rus_old_order_id', False, NoExpectation()),
    ('rus_decoupling_order_id', False, NoExpectation()),
    ('rus_decoupling_order_id', True, NoExpectation()),
])
@pytest.mark.config(
    CORP_VIA_TRUST={
        '__default__': {
            'since_due': '2020-03-06T00:00:00+00:00',
            'level': 'disabled'
        },
        'isr': {
            'since_due': '2020-03-06T00:00:00+00:00',
            'level': 'enabled'
        },
        'rus': {
            'since_due': '2020-03-06T00:00:00+00:00',
            'level': 'just_logging'
        }

    }
)
@pytest.mark.filldb(
    orders='for_test_validate_corp_via_trust',
    tariff_settings='for_test_validate_corp_via_trust',
)
@pytest.inline_callbacks
def test_validate_corp_via_trust(order_id, validate_decoupling, expectation):
    order_doc = yield db.orders.find_one({'_id': order_id})
    with expectation:
        yield payment_handler.validate_corp_via_trust(
            order_doc,
            validate_decoupling=validate_decoupling,
            log_extra=None,
        )


@pytest.mark.parametrize(
    'order_id,expected_options', [
        ('agent_order', payment_handler.HoldOptions(True, False)),
        (
            'personal_wallet_success_order',
            payment_handler.HoldOptions(True, False),
        ),
        (
            'personal_wallet_fail_order',
            payment_handler.HoldOptions(False, False),
        ),
        ('card_like_order_unbound', payment_handler.HoldOptions(False, False)),
        ('card_like_order_invalid', payment_handler.HoldOptions(False, False)),
        (
            'card_like_order_hold_initiated',
            payment_handler.HoldOptions(True, False),
        ),
        ('card_like_order_tips', payment_handler.HoldOptions(True, False)),
        ('card_like_order_failed', payment_handler.HoldOptions(False, False)),
        (
            'card_like_order_failed_fix_search',
            payment_handler.HoldOptions(False, False),
        ),
        ('card_like_order_success', payment_handler.HoldOptions(True, True)),
    ]
)
@pytest.mark.filldb(orders='for_test_get_hold_options')
@pytest.inline_callbacks
def test_get_hold_options(
        mock_fix_change_payment_in_py2_config, order_id, expected_options,
):
    if order_id == 'card_like_order_failed_fix_search':
        mock_fix_change_payment_in_py2_config(is_enabled=True)
        order_id = 'card_like_order_failed'
    order_doc = yield db.orders.find_one({'_id': order_id})
    payable = payment_handler.PayableOrder(order_doc)
    hold_options = yield payable.get_hold_options(None)
    assert hold_options == expected_options


@pytest.mark.parametrize(
    'order_id,expected_options', [
        (
            'coop_account_order_invalid',
            payment_handler.HoldOptions(False, False),
        ),
        ('coop_account_order_fail', payment_handler.HoldOptions(False, False)),
        (
            'coop_account_order_fail_fix_search',
            payment_handler.HoldOptions(False, False),
        ),
        ('coop_account_order', payment_handler.HoldOptions(True, False)),
    ]
)
@pytest.mark.filldb(orders='for_test_get_hold_options')
@pytest.inline_callbacks
def test_coop_get_hold_options(
        mock_fix_change_payment_in_py2_config, order_id, expected_options,
):
    if order_id == 'coop_account_order_fail_fix_search':
        mock_fix_change_payment_in_py2_config(is_enabled=True)
        order_id = 'coop_account_order_fail'
    order_doc = yield db.orders.find_one({'_id': order_id})
    payable = coop_payable.PayableOrderCoop(order_doc)
    hold_options = yield payable.get_hold_options(None)
    assert hold_options == expected_options


@pytest.mark.filldb(
    orders='for_test_build_transactions_antifraud_payload',
    users='for_test_build_transactions_antifraud_payload',
)
@pytest.inline_callbacks
def test_build_transactions_antifraud_payload():
    expected_result = {
        'order_city': 'test_city',
        'main_card_persistent_id': 'test_payment_tech_main_card_persistent_id',
        'performer_driver_id': 'test_performer_clid_test_performer_uuid',
        'sum_to_pay_tips': 123.456,
        'sum_to_pay_toll_road': 123.456,
        'sum_to_pay_ride': 234.567,
        'plan_order_cost': 132.354,
        'request_destinations_count': 3,
        'travel_time_s': 12300.123,
        'travel_distance_m': 3123.123,
        'uid_creation_dt': '2021-02-26T08:28:21+0000',
        'car_number': 'test_performer_car_number',
        'user_phone_id': '3db2856b7974b5db628e79a1',
        'user_fixed_price': 142.3,
        'billing_currency_rate': 'test_billing_contract_currency_rate',
        'updated': 1614328156.789,
        'plan_transporting_distance_m': 2005.123,
        'source_geopoint': [123.123, 234.234],
        'order_cost': 678.901,
        'status_updated': 1614328156.956,
        'driver_fixed_price': 132.35,
        'request_classes': [
            'test_request_class1',
            'test_request_class2',
            'test_request_class3',
        ],
        'tips_value': 847.123,
        'rating_value': 5,
        'source_country': 'test_request_source_country',
        'nearest_zone': 'test_nz',
        'tips_type': 'test_creditcard_tips_type',
        'application': 'test_statistics_application',
        'plan_transporting_time_s': 125.256,
        'order_tariff': 'test_performer_tariff_class',
        'status': 'test_status',
        'performer_db_id': 'test_performer_db_id',
        'driver_license_personal_id': 'test_performer_driver_license_personal_id',
        'user_locale': 'test_user_locale',
        'taxi_status': 'test_taxi_status',
        'device_id': 'test_device_id',
        'driver_position': [3.3, 3.3],
        'driver_cost_calc_method': 'test_driver_cost_calc_method',
        'created': 1614328156.639,
        'performer_uuid': 'test_performer_uuid',
        'request_destinations_geopoints': [[1.1, 2.2], [3.3, 4.4], [5.5, 6.6]],
        'main_card_payment_id': 'test_payment_tech_main_card_payment_id',
        'alias_id': 'test_performer_taxi_alias_id',
        'performer_clid': 'test_performer_clid',
    }

    order_doc = yield db.orders.find_one({'_id': 'full_order'})

    result = yield payment_handler.build_transactions_antifraud_payload(
        order_doc, const.CARD, None,
    )

    assert result == expected_result


@pytest.mark.parametrize(
    'order_doc, config_enabled, expected_enabled',
    (
        ({}, False, False),
        ({'_id': '73'}, True, False),
        (
            {'_id': '73', 'created': datetime.datetime(2021, 5, 3, 18, 5, 1)},
            True,
            True,
        ),
        (
            {'_id': '73', 'created': datetime.datetime(2021, 5, 3, 18, 4, 59)},
            True,
            False,
        ),
        (
            {'_id': '42', 'created': datetime.datetime(2021, 5, 3, 18, 5, 1)},
            True,
            False,
        ),
    ),
)
@pytest.inline_callbacks
def test_enable_fix_change_payment_config(
        patch, order_doc, config_enabled, expected_enabled,
):
    @patch('taxi.config.FIX_CHANGE_PAYMENT_IN_PY2.get')
    def _config_value_get():
        if config_enabled:
            return {
                'enable': True,
                'order_groups': [
                    {
                        'percent': 20,
                        'salt': 'salt',
                        'start_time': '2021-05-03T18:05:00Z',
                    },
                ],
            }
        return {'enable': False, 'order_groups': []}

    enabled = yield payment_handler.enable_fix_change_payment(order_doc, None)
    assert enabled == expected_enabled


@pytest.mark.parametrize('payment_method_id', [
    'existing_card_id', 'non_existing_card_id'
])
@pytest.mark.parametrize('experiments_enabled', [
    True, False
])
@pytest.inline_callbacks
def test_get_card_for_payment_debts_without_cvv(patch, payment_method_id, experiments_enabled):

    def _patch_request(
        patch, expected_path, expected_headers, expected_json_request, response
    ):
        @patch('taxi.external.card_filter._request')
        @async.inline_callbacks
        def _request(method, path, headers, log_extra, json):
            assert method == 'POST'
            assert path == expected_path
            assert headers == expected_headers
            assert json == expected_json_request
            async.return_value(response)
            yield

        return _request

    def _patch_get_card(user_yandex_uid, payment_method_id):
        @patch('taxi.internal.card_operations.get_card')
        def get_card(*args, **kwargs):
            return card_operations.create_card_object(
                owner=user_yandex_uid,
                card_id=payment_method_id,
                system='visa',
                number='1234-5678-0987-6543',
                billing_card_id='card_id',
                currency='rub',
                name='',
                blocking_reason='',
                valid=True,
                service_labels=[
                    'taxi:persistent_id:persistent_id-' + payment_method_id
                ],
                persistent_id='persistent_id-' + payment_method_id,
                region_id='moscow',
                possible_moneyless=False,
                from_db=True,
            )
        return get_card

    def _patch_billing_service():
        @patch('taxi.internal.order_kit.payment_helpers.billing_service_type_from_order')
        @async.inline_callbacks
        def billing_service_type_from_order(order, check_roaming=True, log_extra=None):
            async.return_value(None)
            yield

        return billing_service_type_from_order

    def _patch_experiments(experiments_enabled):
        @patch('taxi.internal.order_kit.payment_handler.is_paying_debts_without_cvv_enabled')
        @async.inline_callbacks
        def is_paying_debts_without_cvv_enabled(order_id, phone_id, log_extra=None):
            async.return_value(experiments_enabled)
            yield

        return is_paying_debts_without_cvv_enabled

    def _create_cards():
        return {
            'available_cards':
            [
                {
                    'id': 'existing_card_id',
                },
                {
                    'id': 'another_card_id',
                }
            ],
        }

    user_yandex_uid = 'user_yandex_uid'
    user_id = 'user_id'
    user_login_id = 'user_login_id'

    _patch_request(
        patch=patch,
        expected_path='v1/filteredcards/legacy',
        expected_headers={'X-Yandex-UID': user_yandex_uid},
        expected_json_request={
            'yandex_uid': user_yandex_uid,
            'user_id': user_id,
            'yandex_login_id': user_login_id,
        },
        response=_create_cards(),
    )

    _patch_get_card(user_yandex_uid, payment_method_id)
    _patch_billing_service()
    _patch_experiments(experiments_enabled)

    order_id = 'order_id'
    order = {
        'order_id': order_id,
        'user_phone_id': 'user_phone_id',
    }

    if payment_method_id == 'non_existing_card_id' and experiments_enabled:
        with pytest.raises(card_operations.CardNotAvailable):
            yield payment_handler.card_is_in_user_cards(
                order=order,
                order_id=order_id,
                user_id=user_id,
                user_login_id=user_login_id,
                user_yandex_uid=user_yandex_uid,
                payment_method_id=payment_method_id,
            )
    else:
        yield payment_handler.card_is_in_user_cards(
            order=order,
            order_id=order_id,
            user_id=user_id,
            user_login_id=user_login_id,
            user_yandex_uid=user_yandex_uid,
            payment_method_id=payment_method_id,
        )


@pytest.mark.filldb(orders='for_test_on_hold_fail')
@pytest.mark.config(SHOULD_SEND_COMPOSITE_DROP_PY2=True)
@pytest.mark.now('2020-09-08 17:12:53+03')
@pytest.inline_callbacks
def test_solomon_push_composite_failed(patch):
    @patch(
        'taxi.internal.order_kit.personal_wallet_payment_gateway.'
        'start_new_refund'
    )
    def start_new_refund(payable, tran, refund_sum, log_extra=None):
        assert payable is payable_order
        assert refund_sum == {'ride': 300000}
        assert tran is payable_order.transactions[0]

    @patch('taxi.core.arequests.post')
    def solomon_request(url, json=None, **kwargs):
        pass

    order_id = 'composite_failed_with_previous_order_id'
    payable_order = yield payable_from_order_id(order_id)

    yield payment_handler._send_complement_disabled_in_solomon(payable_order)
    calls = solomon_request.calls
    assert len(calls) == 1
    sensors = calls[0]['json']['sensors']
    assert len(sensors) == 1
    assert sensors[0] == {
        'kind': 'IGAUGE',
        'labels': {'application': 'taxi_maintenance', 'currency': 'RUB', 'sensor': 'complements_dropped'},
        'ts': 1599574373,
        'value': 1
    }


@pytest.mark.config(
    CORP_RESALE_LOGISTICS_TO_TAXI_BY_COUNTRIES={
        'rus': {
            'is_enabled': True,
        },
        '__default__': {
            'is_enabled': False,
        },
    },
    CORP_TECHNICAL_RESALE_SETTINGS_BY_COUNTRY={
        'rus': {
            '651': {
                'client_id': 'taxi_client_id',
                'contract_id': 'taxi_contract_id',
            },
            '718': {
                'client_id': 'logistic_client_id',
                'contract_id': 'logistic_contract_id',
            },
            '650': {
                'client_id': 'taxi_client_id',
                'contract_id': 'taxi_contract_id',
            },
            '719': {
                'client_id': 'logistic_client_id',
                'contract_id': 'logistic_contract_id',
            },
        }
    },
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'econom': {
            'client': 'cargo_multi_client_b2b_trip_payment',
            'partner': 'cargo_multi_park_b2b_trip_payment',
        },
        'business': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
        'logistic_econom': {
            'client': 'cargo_client_b2b_logistics_payment',
            'partner': 'cargo_park_b2b_logistics_payment',
        },
        'logistic_business': {
            'client': 'delivery_client_b2b_logistics_payment',
            'partner': 'delivery_park_b2b_logistics_payment',
        },
    },
    CORP_BILLING_LOGISTIC_PAYMENTS_REBATE_SETTINGS={
        'start_from': '2016-08-25T20:00:00+00:00',
        'tariffs': [
            {
                'name': 'econom',
                'prefix': 'cargo',
                'action': 'add_rebate',
            },
            {
                'name': 'business',
                'prefix': 'delivery',
                'action': 'skip',
            },
        ],
        'unknown_tariff_action': 'raise_no_payment_kind',
        'unknown_tariff_prefix': '',
    },
    CORP_CARGO_RESALE_CLIENT_PRICE_SETTINGS={
        'mode': 'enabled',
    },
)
@pytest.mark.parametrize(
    [
        'order_id',
        'client_to_hold',
        'driver_to_hold',
        'agent_to_hold',
        'expected_send',
        'is_resale_taxi_to_logistics',
    ],
    [
        (
            'order-tlog1',
            ({'ride': 5400000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            [
                {
                    'data': {
                        'event_version': 0,
                        'payments': [
                            {
                                'amount': '840.0000',
                                'billing_client_id': 'taxi_client_id',
                                'contract_id': 'taxi_contract_id',
                                'currency': 'RUB',
                                'invoice_date': '2016-08-04T20:20:00+00:00',
                                'payload': {
                                    'agglomeration': 'MSKc',
                                    'alias_id': 'alias_id',
                                    'nearest_zone': 'moscow',
                                    'order_id': 'order-tlog1',
                                    'tariff_class': 'econom',
                                    'transaction_type': 'payment',
                                    'driver_details': {
                                        'clid': 'park-test',
                                        'db_id': 'some_db_id',
                                        'uuid': 'driver-test'
                                    },
                                    'amount_details': {
                                        'base_amount': '840.0',
                                        'base_currency': 'RUB',
                                        'contract_currency_rate': '1',
                                        'vat': '140.0000'
                                    },
                                    'detailed_product': 'b2b_agent_taxi_expense',
                                    'product': 'b2b_agent_taxi_expense',
                                    'service_id': 651
                                },
                                'payment_kind': 'b2b_agent_taxi_expense'
                            }
                        ],
                        'schema_version': 'v2',
                        'template_entries': [],
                        'topic_begin_at': '2016-08-04T20:00:00+00:00'
                    },
                    'event_at': '2016-08-04T20:00:00+00:00',
                    'external_ref': '0',
                    'kind': 'arbitrary_payout',
                    'log_extra': None,
                    'tags': ['taxi/alias_id/alias_id'],
                    'topic': 'taxi/b2b_agent_taxi_expense/alias_id',
                    'tvm_src_service': 'stq'
                },
                {
                    'data': {
                        'event_version': 0,
                        'payments': [
                            {
                                'amount': '700.0000',
                                'billing_client_id': 'logistic_client_id',
                                'contract_id': 'logistic_contract_id',
                                'currency': u'RUB',
                                'invoice_date': '2016-08-04T20:20:00+00:00',
                                'payload': {
                                    'agglomeration': 'MSKc',
                                    'alias_id': 'alias_id',
                                    'nearest_zone': 'moscow',
                                    'order_id': 'order-tlog1',
                                    'tariff_class': 'econom',
                                    'transaction_type': 'payment',
                                    'driver_details': {
                                        'clid': 'park-test',
                                        'db_id': 'some_db_id',
                                        'uuid': 'driver-test'
                                    },
                                    'amount_details': {
                                        'base_amount': '700.0',
                                        'base_currency': u'RUB',
                                        'contract_currency_rate': '1',
                                        'vat': '140.0000'
                                    },
                                    'detailed_product': 'b2b_agent_logistics_revenue',
                                    'product': 'b2b_agent_logistics_revenue',
                                    'service_id': 718
                                },
                                'payment_kind': 'b2b_agent_logistics_revenue'
                            }
                        ],
                        'schema_version': 'v2',
                        'template_entries': [],
                        'topic_begin_at': '2016-08-04T20:00:00+00:00'
                    },
                    'event_at': '2016-08-04T20:00:00+00:00',
                    'external_ref': '0',
                    'kind': 'arbitrary_payout',
                    'log_extra': None,
                    'tags': ['taxi/alias_id/alias_id'],
                    'topic': 'taxi/b2b_agent_logistics_revenue/alias_id',
                    'tvm_src_service': 'stq'
                },
                {
                    'kind': 'b2b_partner_payment',
                    'topic': 'taxi/b2b_partner_payment_logistics/alias_id',
                    'external_ref': '0',
                    'event_at': '2016-08-04T20:00:00+00:00',
                    'data': {
                        'schema_version': 'v1',
                        'event_version': 0,
                        'topic_begin_at': '2016-08-04T20:00:00+00:00',
                        'driver_income': {
                            'alias_id': 'alias_id',
                            'components': [
                                {
                                    'amount': '500.0000',
                                    'currency': 'RUB',
                                    'kind': 'payment/corp',
                                },
                            ],
                            'driver': {
                                'db_id': 'some_db_id',
                                'driver_uuid': 'driver-test',
                            },
                            'order_event_at': '2016-08-04T20:00:00+00:00',
                        },
                        'payments': [
                            {
                                'payment_kind': 'cargo_park_b2b_logistics_payment',
                                'amount': '500.0000',
                                'currency': 'RUB',
                                'billing_client_id': '100000',
                                'contract_id': 'park_contract_id',
                                'invoice_date': '2016-08-04T20:20:00+00:00',
                                'payload': {
                                    'agglomeration': 'MSKc',
                                    'alias_id': 'alias_id',
                                    'amount_details': {
                                        'base_amount': '500.0',
                                        'base_currency': 'RUB',
                                        'contract_currency_rate': '1',
                                        'vat': '0.0000',
                                    },
                                    'driver_details': {
                                        'clid': 'park-test',
                                        'db_id': 'some_db_id',
                                        'uuid': 'driver-test',
                                    },
                                    'tariff_class': 'econom',
                                    'nearest_zone': 'moscow',
                                    'order_id': 'order-tlog1',
                                },
                            },
                        ],
                    },
                    'tags': ['taxi/alias_id/alias_id'],
                    'tvm_src_service': 'stq',
                    'log_extra': None,
                },
            ],
            True,
        ),
        (
            'order-tlog-with-logistics',
            ({'ride': 5400000}, {}),
            ({'ride': 5000000}, {}),
            ({}, {}),
            [
                {
                    'data': {
                        'event_version': 0,
                        'payments': [
                            {
                                'amount': '360.0000',
                                'billing_client_id': 'logistic_client_id',
                                'contract_id': 'logistic_contract_id',
                                'currency': 'RUB',
                                'invoice_date': '2016-08-04T20:20:00+00:00',
                                'payload': {
                                    'agglomeration': 'MSKc',
                                    'alias_id': 'alias_id',
                                    'nearest_zone': 'moscow',
                                    'order_id': 'order-tlog-with-logistics',
                                    'tariff_class': 'econom',
                                    'transaction_type': 'payment',
                                    'driver_details': {
                                        'clid': 'park-test',
                                        'db_id': 'some_db_id',
                                        'uuid': 'driver-test'
                                    },
                                    'amount_details': {
                                        'base_amount': '360.0',
                                        'base_currency': 'RUB',
                                        'contract_currency_rate': '1',
                                        'vat': '60.0000'
                                    },
                                    'detailed_product': 'b2b_agent_logistics_expense',
                                    'product': 'b2b_agent_logistics_expense',
                                    'service_id': 719
                                },
                                'payment_kind': 'b2b_agent_logistics_expense'
                            }
                        ],
                        'schema_version': 'v2',
                        'template_entries': [],
                        'topic_begin_at': '2016-08-04T20:00:00+00:00'
                    },
                    'event_at': '2016-08-04T20:00:00+00:00',
                    'external_ref': '0',
                    'kind': 'arbitrary_payout',
                    'log_extra': None,
                    'tags': ['taxi/alias_id/alias_id'],
                    'topic': 'taxi/b2b_agent_logistics_expense/alias_id',
                    'tvm_src_service': 'stq'
                },
                {
                    'data': {
                        'event_version': 0,
                        'payments': [
                            {
                                'amount': '300.0000',
                                'billing_client_id': 'taxi_client_id',
                                'contract_id': 'taxi_contract_id',
                                'currency': 'RUB',
                                'invoice_date': '2016-08-04T20:20:00+00:00',
                                'payload': {
                                    'agglomeration': 'MSKc',
                                    'alias_id': 'alias_id',
                                    'nearest_zone': 'moscow',
                                    'order_id': 'order-tlog-with-logistics',
                                    'tariff_class': 'econom',
                                    'transaction_type': 'payment',
                                    'driver_details': {
                                        'clid': 'park-test',
                                        'db_id': 'some_db_id',
                                        'uuid': 'driver-test'
                                    },
                                    'amount_details': {
                                        'base_amount': '300.0',
                                        'base_currency': u'RUB',
                                        'contract_currency_rate': '1',
                                        'vat': '60.0000'
                                    },
                                    'detailed_product': 'b2b_agent_taxi_revenue',
                                    'product': 'b2b_agent_taxi_revenue',
                                    'service_id': 650
                                },
                                'payment_kind': 'b2b_agent_taxi_revenue'
                            }
                        ],
                        'schema_version': 'v2',
                        'template_entries': [],
                        'topic_begin_at': '2016-08-04T20:00:00+00:00'
                    },
                    'event_at': '2016-08-04T20:00:00+00:00',
                    'external_ref': '0',
                    'kind': 'arbitrary_payout',
                    'log_extra': None,
                    'tags': ['taxi/alias_id/alias_id'],
                    'topic': 'taxi/b2b_agent_taxi_revenue/alias_id',
                    'tvm_src_service': 'stq'
                },
                {
                    'kind': 'b2b_partner_payment',
                    'topic': 'taxi/b2b_partner_payment/alias_id',
                    'external_ref': '0',
                    'event_at': '2016-08-04T20:00:00+00:00',
                    'data': {
                        'schema_version': 'v1',
                        'event_version': 0,
                        'topic_begin_at': '2016-08-04T20:00:00+00:00',
                        'driver_income': {
                            'alias_id': 'alias_id',
                            'components': [
                                {
                                    'amount': '500.0000',
                                    'currency': 'RUB',
                                    'kind': 'payment/corp',
                                },
                            ],
                            'driver': {
                                'db_id': 'some_db_id',
                                'driver_uuid': 'driver-test',
                            },
                            'order_event_at': '2016-08-04T20:00:00+00:00',
                        },
                        'payments': [
                            {
                                'payment_kind': 'cargo_multi_park_b2b_trip_payment',
                                'amount': '500.0000',
                                'currency': 'RUB',
                                'billing_client_id': '100000',
                                'contract_id': 'park_contract_id',
                                'invoice_date': '2016-08-04T20:20:00+00:00',
                                'payload': {
                                    'agglomeration': 'MSKc',
                                    'alias_id': 'alias_id',
                                    'amount_details': {
                                        'base_amount': '500.0',
                                        'base_currency': 'RUB',
                                        'contract_currency_rate': '1',
                                        'vat': '0.0000',
                                    },
                                    'driver_details': {
                                        'clid': 'park-test',
                                        'db_id': 'some_db_id',
                                        'uuid': 'driver-test',
                                    },
                                    'tariff_class': 'econom',
                                    'nearest_zone': 'moscow',
                                    'order_id': 'order-tlog-with-logistics',
                                },
                            },
                        ],
                    },
                    'tags': ['taxi/alias_id/alias_id'],
                    'tvm_src_service': 'stq',
                    'log_extra': None,
                },
            ],
            False,
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_corp_b2b_partner_payment')
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_tlog_corp_b2b_partner_payment_with_resale_payments(
        patch,
        patch_corp_clients,
        order_id,
        client_to_hold,
        driver_to_hold,
        agent_to_hold,
        expected_send,
        is_resale_taxi_to_logistics,
):
    @patch('taxi.external.billing_orders.process_event_async')
    @async.inline_callbacks
    def process_event_async(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.external.agglomerations.get_mvp_oebs_id')
    @async.inline_callbacks
    def get_mvp_oebs_id(tariff_zone, *args, **kwargs):
        yield async.return_value(
            {
                'moscow': 'MSKc',
                'astana': 'AST',
                'tel_aviv': 'TELAVIV',
            }[tariff_zone]
        )

    @patch('taxi.external.billing_replication.get_active_contracts')
    @async.inline_callbacks
    def get_active_contracts(client_id, service_ids, *args, **kwargs):
        service_id = 651
        if is_resale_taxi_to_logistics:
            service_id = 719
        yield async.return_value(
            [
                {
                    'ID': 'park_contract_id',
                    'DT': None,
                    'SERVICES': [
                        service_id,
                    ]
                },
            ]
        )

    @patch('taxi.external.cargo_claims.claims_payment_info')
    @async.inline_callbacks
    def claims_payments_info(request, *args, **kwargs):
        yield async.return_value(
            {
                'claims': [
                    {
                        'final_price': '100',
                        'final_price_mult': '120',
                        'claim_id': '1',
                        'is_logistic_contract': True,

                    },
                    {
                        'final_price': '200',
                        'final_price_mult': '240',
                        'claim_id': '2',
                        'is_logistic_contract': True,
                    },
                    {
                        'final_price': '300',
                        'final_price_mult': '360',
                        'claim_id': '3',
                        'is_logistic_contract': False,
                    },
                    {
                        'final_price': '400',
                        'final_price_mult': '480',
                        'claim_id': '4',
                        'is_logistic_contract': False,
                    },
                ],
            }
        )

    @patch('taxi.internal.city_manager.get_city_tz')
    def test_get_city_tz(*args, **kwargs):
        return 'Europe/Moscow'

    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield payment_handler._tlog_corp(
        order_doc, client_to_hold, driver_to_hold, agent_to_hold
    )

    calls = process_event_async.calls
    assert calls[0]['kwargs'] == expected_send[0]
    assert calls[1]['kwargs'] == expected_send[1]
    assert calls[2]['kwargs'] == expected_send[2]
