import collections
import copy
import datetime
import datetime as dt
import decimal
import json
import operator

import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.conf import settings
from taxi.external import archive
from taxi.external import plus_wallet
from taxi.external import experiments3
from taxi.external import transactions
from taxi.internal import dbh
from taxi.internal.order_kit import payment_handler
from taxi.internal.order_kit import payment_helpers
from taxi.internal.order_kit.payables import coop
from taxi.internal.order_kit import exceptions
from taxi.internal.payment_kit import invoices


_WILL_BE_SET_INSIDE_TEST = object()
_NO_PAYMENTS = object()
_PRODUCTS = {
    ('card', 'ride'): 'ride_product',
    ('card', 'cashback'): 'cashback_product',
    ('card', 'toll_road'): 'toll_road_product',
    ('card', 'tips'): 'tips_product',
    ('coop_account', 'ride'): 'ride_product',
    ('coop_account', 'toll_road'): 'toll_road_product',
    ('coop_account', 'tips'): 'tips_product',
    ('personal_wallet', 'ride'): 'ride_product',
    ('personal_wallet', 'toll_road'): 'toll_road_product',
    ('personal_wallet', 'tips'): 'tips_product',
    ('applepay', 'ride'): 'ride_product',
    ('googlepay', 'ride'): 'ride_product',
    ('agent', 'ride'): None,
    ('yandex_card', 'ride'): 'ride_product',
    ('yandex_card', 'cashback'): 'cashback_product',
}
_DEFAULT_FISCAL_RECEIPT_INFO = transactions.FiscalReceiptInfo(
    personal_tin_id='some_personal_tin_id',
    vat='nds_18',
    title='some_title',
    cashregister_params=None,
)
_CASHBACK_FISCAL_RECEIPT_INFO = transactions.FiscalReceiptInfo(
    personal_tin_id='cashback_personal_tin_id',
    vat='nds_20',
    title='cashback_title',
    cashregister_params=None,
)
_CASHBACK_FISCAL_RECEIPT_INFO_WITH_FOOTER = transactions.FiscalReceiptInfo(
    personal_tin_id='cashback_personal_tin_id',
    vat='nds_20',
    title='cashback_title',
    cashregister_params={
        'receipt_footer': 'receipt footer text'
    },
)

_FISCAL_RECEIPT_INFOS = collections.defaultdict(
    (lambda: _DEFAULT_FISCAL_RECEIPT_INFO),
    {'cashback': _CASHBACK_FISCAL_RECEIPT_INFO}
)
_FISCAL_RECEIPT_INFOS_WITH_FOOTER = collections.defaultdict(
  (lambda: _DEFAULT_FISCAL_RECEIPT_INFO),
  {'cashback': _CASHBACK_FISCAL_RECEIPT_INFO_WITH_FOOTER}
)
_MISSING = object()
_NEW_TRUST_INTEGRATION = 'new_integration'


def _operation_statuses(*statuses):
    operations = [{'status': a_status} for a_status in statuses]
    invoice_dict = {'operations': operations}
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _transactions_ready(value):
    invoice_dict = {
        'transactions_ready': value
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _independent_compensations():
    invoice_dict = {
        'compensation': {
            'version': 8,
            'operations': [],
        }
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _ride_100_operation(merchant=None):
    item = {
        'item_id': 'ride',
        'amount': '100',
    }

    if merchant is not None:
        item['merchant'] = merchant

    invoice_dict = {
        'operations': [
            {
                'sum_to_pay': [
                    {
                        'payment_type': 'card',
                        'items': [item]
                    }
                ]
            }
        ]
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _payable_pending_compensations():
    order_doc = {
        '_id': 'some_order_id',
        'billing_tech': {
            'compensations': [{'status': 'compensation_init'}]
        }
    }
    return payment_handler.PayableOrder(order_doc)


def _transaction_statuses(*statuses):
    transactions = [{'status': a_status} for a_status in statuses]
    invoice_dict = {'transactions': transactions}
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _operations_missing():
    return invoices.InvoiceV2(_with_required_fields({}))


def _transactions_empty():
    invoice_dict = {'transactions': []}
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _with_required_fields(invoice_dict):
    result = copy.deepcopy(invoice_dict)
    if 'transactions' not in result:
        result['transactions'] = []
    return result


def _composite_invoice():
    invoice_dict = {
        'sum_to_pay': [
            {
                'items': [
                    {'item_id': 'food', 'amount': '80'},
                    {'item_id': 'food', 'amount': '5'},
                ],
                'payment_type': 'personal_wallet',
            },
            {
                'items': [{'item_id': 'tips', 'amount': '10'}],
                'payment_type': 'card',
            },
        ],
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _composite_sum():
    personal_wallet_sum = invoices.Sum({'food': decimal.Decimal(85)})
    card_sum = invoices.Sum({'tips': decimal.Decimal(10)})
    sum_by_type = {'personal_wallet': personal_wallet_sum, 'card': card_sum}
    return invoices.CompositeSum(sum_by_type)


def _food_100():
    return invoices.Sum({'food': decimal.Decimal(100)})


def _food_0():
    return invoices.Sum({'food': decimal.Decimal(0)})


def _food_200():
    return invoices.Sum({'food': decimal.Decimal(200)})


def _food_20_tips_1():
    return invoices.Sum(
        {'food': decimal.Decimal(20), 'tips': decimal.Decimal(1)},
    )


def _food_120_tips_1():
    return invoices.Sum(
        {'food': decimal.Decimal(120), 'tips': decimal.Decimal(1)},
    )


def _failed_card():
    invoice_dict = {
        'transactions': [
            {
                'operation_id': 'failed_operation_id',
                'status': 'clear_success',
                'payment_method_type': 'personal_wallet',
            },
            {
                'operation_id': 'failed_operation_id',
                'status': 'hold_fail',
                'payment_method_type': 'card',
            },
        ],
        'operations': [
            _failed_composite_operation(),
            _successful_operation(),
        ],
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _failed_card_from_different_operation():
    invoice_dict = {
        'transactions': [
            {
                'operation_id': 'another_operation_id',
                'status': 'clear_success',
                'payment_method_type': 'personal_wallet',
            },
            {
                'operation_id': 'another_operation_id',
                'status': 'hold_fail',
                'payment_method_type': 'card',
            },
        ],
        'operations': [_failed_composite_operation()],
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _failed_personal_wallet():
    invoice_dict = {
        'transactions': [
            {
                'operation_id': 'failed_operation_id',
                'status': 'hold_fail',
                'payment_method_type': 'personal_wallet',
            },
        ],
        'operations': [_failed_composite_operation()],
    }
    return invoices.InvoiceV2(_with_required_fields(invoice_dict))


def _make_payment_items_list(
        items_by_type, fiscal_receipt_infos=_MISSING, merchant=None):
    items_by_payment_type = []
    for payment_type, amount_by_item_id in _items_in_deterministic_order(
            items_by_type
    ):
        if payment_type in ['card', 'applepay', 'googlepay', 'coop_account', 'personal_wallet', 'yandex_card']:
            if fiscal_receipt_infos is _MISSING:
                effective_fiscal_receipt_infos = _FISCAL_RECEIPT_INFOS
            else:
                effective_fiscal_receipt_infos = fiscal_receipt_infos
            region_id = 225
        else:
            region_id = None
            effective_fiscal_receipt_infos = collections.defaultdict(lambda: None)
        items = [
            transactions.Item(
                item_id=item_id,
                product_id=_PRODUCTS[(payment_type, item_id)],
                amount=decimal.Decimal(amount),
                region_id=region_id,
                fiscal_receipt_info=effective_fiscal_receipt_infos[item_id],
                merchant=merchant,
            )
            for item_id, amount in _items_in_deterministic_order(
                amount_by_item_id
            )
        ]
        items_by_payment_type.append(
            transactions.PaymentItemsList(payment_type, items)
        )
    return items_by_payment_type


def _items_in_deterministic_order(a_dict):
    return sorted(a_dict.iteritems(), key=operator.itemgetter(0), cmp=invoices.payment_items_compare)


def _failed_composite_operation():
    return {
        'id': 'failed_operation_id',
        'status': 'failed',
        'sum_to_pay': [
            {
                'items': [{'item_id': 'food', 'amount': '100'}],
                'payment_type': 'personal_wallet',
            },
            {
                'items': [{'item_id': 'tips', 'amount': '10'}],
                'payment_type': 'card',
            },
        ],
    }


def _successful_operation():
    return {
        'id': 'successful_operation_id',
        'status': 'done',
        'sum_to_pay': [
            {
                'items': [{'item_id': 'food', 'amount': '100'}],
                'payment_type': 'personal_wallet',
            },
            {
                'items': [{'item_id': 'tips', 'amount': '10'}],
                'payment_type': 'card',
            },
        ]
    }


def _card_split(sum_, sum_type):
    return plus_wallet.SplitElement(
        type='card',
        payment_method_id='card-1',
        sum=decimal.Decimal(sum_),
        sum_type=sum_type,
    )


def _wallet_split(sum_, sum_type):
    return plus_wallet.SplitElement(
        type='personal_wallet',
        payment_method_id='w/long-hash',
        sum=decimal.Decimal(sum_),
        sum_type=sum_type,
    )


@pytest.mark.parametrize(
    'invoice,expected',
    [
        (_operation_statuses('init'), True),
        (_operation_statuses('processing'), True),
        (_operation_statuses('done', 'obsolete', 'failed'), False),
        (_operation_statuses('init', 'done', 'obsolete', 'failed'), True),
        (_operations_missing(), False),
    ],
)
@pytest.mark.filldb(_fill=False)
def test_invoice_has_pending_operations(invoice, expected):
    assert invoice.has_pending_operations is expected


@pytest.mark.parametrize('invoice,expected', [
    (_ride_100_operation(merchant={'id': 'some_merchant_id'}), True),
    (_ride_100_operation(), False),
])
@pytest.mark.filldb(_fill=False)
def test_invoice_has_merchant(invoice, expected):
    assert invoice._has_merchant is expected


@pytest.mark.parametrize('config_value,invoice,payable_order,expected', [
    # should ignore config value if invoice already has merchant
    (
        False,
        _ride_100_operation(merchant={'id': 'some_merchant_id'}),
        payment_handler.PayableOrder(
            {
                'performer': {
                    'clid': 'some_clid',
                    'uuid': 'some_uuid',
                    'taxi_alias': {
                        'id': 'some_alias_id',
                    }
                },
                'billing_tech': {
                    'transactions': [],
                }
            }
        ),
        transactions.Merchant('some_clid_some_uuid', 'some_alias_id'),
    ),
    # should return None if invoice has py2 transaction
    (
        True,
        _ride_100_operation(),
        payment_handler.PayableOrder(
            {
                'performer': {
                    'clid': 'some_clid',
                    'uuid': 'some_uuid',
                    'taxi_alias': {
                        'id': 'some_alias_id',
                    }
                },
                'billing_tech': {
                    'transactions': [{}]
                }
            }
        ),
        None,
    ),
    # should return merchant if there are no py2 transactions
    (
        True,
        _ride_100_operation(merchant={'id': 'some_merchant_id'}),
        payment_handler.PayableOrder(
            {
                'performer': {
                    'clid': 'some_clid',
                    'uuid': 'some_uuid',
                    'taxi_alias': {
                        'id': 'some_alias_id',
                    }
                },
                'billing_tech': {
                    'transactions': [{'request_id': 'some_request_id'}]
                }
            }
        ),
        transactions.Merchant('some_clid_some_uuid', 'some_alias_id'),
    ),
    # should return last merchant if there's no performer
    (
        False,
        _ride_100_operation(merchant={
            'id': 'some_merchant_id',
            'order_id': 'some_merchant_order_id'
        }),
        payment_handler.PayableOrder({}),
        transactions.Merchant('some_merchant_id', 'some_merchant_order_id'),
    ),
    # should return None for invoice with operations without merchant
    (
        True,
        _ride_100_operation(merchant=None),
        payment_handler.PayableOrder(
            {
                'performer': {
                    'clid': 'some_clid',
                    'uuid': 'some_uuid',
                    'taxi_alias': {
                        'id': 'some_alias_id',
                    }
                },
                'billing_tech': {
                    'transactions': [],
                }
            }
        ),
        None,
    ),
    # should return None when disabled via config
    (
        False,
        invoices.InvoiceV2(_with_required_fields({})),
        payment_handler.PayableOrder(
            {
                'performer': {
                    'clid': 'some_clid',
                    'uuid': 'some_uuid',
                    'taxi_alias': {
                        'id': 'some_alias_id',
                    }
                },
                'billing_tech': {
                    'transactions': [],
                }
            }
        ),
        None,
    ),
])
@pytest.inline_callbacks
def test_invoice_get_merchant(config_value, invoice, payable_order, expected):
    yield config.TRANSACTIONS_PASS_MERCHANT_INFO.save(config_value)
    actual = yield invoice._get_merchant(payable_order)
    assert actual == expected


@pytest.mark.parametrize('invoice,payable,expected', [
    (
        _independent_compensations(),
        payment_handler.PayableOrder({'_id': 'some_order_id'}),
        invoices.CompensationParams('v3', 8)
    ),
    (
        invoices.InvoiceV2(_with_required_fields({})),
        payment_handler.PayableOrder({'_id': 'some_order_id'}),
        invoices.CompensationParams('v3', 1)
    ),
    (
        invoices.InvoiceV2(_with_required_fields(
            {'operation_info': {'version': 1}})
        ),
        _payable_pending_compensations(),
        invoices.CompensationParams('v2', 1)
    ),
])
@pytest.mark.config(
    TRANSACTIONS_INDEPENDENT_COMPENSATIONS_ROLLOUT=100,
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_invoice_get_compensation_params(invoice, payable, expected):
    actual = yield invoice._get_compensation_params(payable)
    assert actual == expected


@pytest.mark.parametrize(
    'invoice,expected',
    [
        (_transaction_statuses('hold_pending'), True),
        (_transaction_statuses('hold_fail'), False),
        (_transaction_statuses('hold_success'), False),
        (_transaction_statuses('clear_success'), False),
        (_transaction_statuses('clear_fail'), False),
        (_transactions_empty(), False),
    ],
)
@pytest.mark.filldb(_fill=False)
def test_invoice_has_pending_transactions(invoice, expected):
    assert invoice.has_pending_transactions is expected


@pytest.mark.parametrize(
    'invoice,expected', [(_composite_invoice(), _composite_sum())],
)
@pytest.mark.filldb(_fill=False)
def test_invoice_sum_to_pay(invoice, expected):
    assert invoice.sum_to_pay == expected


@pytest.mark.parametrize(
    'left,op,right,expected',
    [
        (
            _food_100(),
            operator.add,
            _food_20_tips_1(),
            invoices.Sum(
                {'food': decimal.Decimal(120), 'tips': decimal.Decimal(1)},
            ),
        ),
        (
            _food_100(),
            operator.sub,
            _food_20_tips_1(),
            invoices.Sum(
                {'food': decimal.Decimal(80), 'tips': decimal.Decimal(-1)},
            ),
        ),
    ],
)
@pytest.mark.filldb(_fill=False)
def test_sum_arithmetic(left, op, right, expected):
    assert op(left, right) == expected


@pytest.mark.parametrize(
    'left,op,right,expected',
    [
        (
            invoices.CompositeSum(
                {'personal_wallet': _food_100(), 'card': _food_20_tips_1()},
            ),
            operator.add,
            invoices.CompositeSum({'personal_wallet': _food_100()}),
            invoices.CompositeSum(
                {'personal_wallet': _food_200(), 'card': _food_20_tips_1()},
            ),
        ),
        (
            invoices.CompositeSum(
                {'personal_wallet': _food_100(), 'card': _food_20_tips_1()},
            ),
            operator.sub,
            invoices.CompositeSum({'personal_wallet': _food_100()}),
            invoices.CompositeSum(
                {'personal_wallet': _food_0(), 'card': _food_20_tips_1()},
            ),
        ),
    ],
)
@pytest.mark.filldb(_fill=False)
def test_composite_sum_arithmetic(left, op, right, expected):
    assert op(left, right) == expected


@pytest.mark.parametrize(
    'sum_,expected',
    [(_food_0(), True), (_food_100(), False), (invoices.Sum({}), True)],
)
def test_sum_is_zero(sum_, expected):
    assert sum_.is_zero() is expected


@pytest.mark.parametrize(
    'composite_sum,expected',
    [
        (invoices.CompositeSum({'card': _food_0()}), True),
        (invoices.CompositeSum({'card': _food_100()}), False),
        (invoices.CompositeSum({}), True),
    ],
)
def test_composite_sum_is_zero(composite_sum, expected):
    assert composite_sum.is_zero() is expected


@pytest.mark.parametrize(
    'operand,expected',
    [
        (
            invoices.CompositeSum({'card': _food_100()}),
            invoices.CompositeSum({'card': _food_100()}),
        ),
        (
            invoices.CompositeSum({
                'card': _food_100(), 'coop_account': _food_20_tips_1(),
            }),
            invoices.CompositeSum({'card': _food_120_tips_1()}),
        ),
        (
            invoices.CompositeSum({'coop_account': _food_100()}),
            invoices.CompositeSum({'card': _food_100()}),
        ),
    ],
)
@pytest.mark.filldb(_fill=False)
def test_composite_sum_replace_payment_type(operand, expected):
    old_type = 'coop_account'
    new_type = 'card'
    assert operand.with_replaced_payment_type(old_type, new_type) == expected


@pytest.mark.parametrize(
    'invoice,expected',
    [
        (_failed_card_from_different_operation(), False),
        (_failed_card(), True),
        (_failed_personal_wallet(), False),
        (_operations_missing(), False),
    ],
)
@pytest.mark.filldb(_fill=False)
def test_needs_to_disable_composite(invoice, expected):
    assert invoice.needs_to_disable_composite is expected


@pytest.mark.parametrize('invoice,expected', [
    (_transactions_ready(True), True),
    (_transactions_ready(False), False),
])
@pytest.mark.filldb(_fill=False)
def test_is_transactions_ready(invoice, expected):
    assert invoice.is_transactions_ready is expected


@pytest.mark.parametrize('order_id', [
    'some_order_id'
])
@pytest.mark.filldb(orders='for_test_try_process_invoice_config_disabled')
@pytest.inline_callbacks
def test_try_process_invoice_config_disabled(monkeypatch, order_id):
    payable_order = yield _fetch_payable_order(order_id)
    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', 'stq')
    processing = yield invoices.try_process_invoice(payable_order)
    assert not processing.via_transactions


class NoException(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.parametrize('order_id,expected', [
    ('many_ops_order_id', True),
    ('few_ops_order_id', False),
    ('many_ops_order_id_custom_limit', False),
])
@pytest.mark.config(MAX_INVOICE_OPERATIONS=2)
@pytest.mark.filldb(orders='for_test_will_have_too_many_operations')
@pytest.inline_callbacks
def test_will_have_too_many_operations(patch, order_id, expected):
    payable_order = yield _fetch_payable_order(order_id)
    _patch_v2_invoice_retrieve(patch, payable_order)
    client = invoices._Client(payable_order, 'stq')
    invoice = yield client.fetch_invoice()
    actual = yield invoice.will_have_too_many_operations(payable_order)
    assert actual == expected


@pytest.mark.parametrize('order_id,invoice,archive_response,expected', [
        ('missing_order_proc_id', None, None, None),
        (
            'missing_order_proc_id',
            None,
            {
                'doc': {
                    'order': {'user_login_id': 'some_archive_user_login_id'}
                }
            },
            'some_archive_user_login_id'
        ),
         (
            'missing_order_proc_id',
            None,
            {
                'doc': {}
            },
            None
        ),
        (
            'missing_order_proc_id',
            invoices.InvoiceV2(_with_required_fields(
                {'login_id': 'some_invoice_user_login_id'}
            )),
            None,
            'some_invoice_user_login_id'
        ),
        ('some_order_proc_without_login_id', None, None, None),
        ('some_order_proc_with_login_id', None, None, 'some_user_login_id'),
    ])
@pytest.mark.config(
    TRANSACTIONS_SEND_LOGIN_ID=True,
    TRANSACTIONS_FETCH_LOGIN_ID_FROM_ARCHIVE=True,
)
@pytest.mark.filldb(
    order_proc='for_test_get_user_login_id'
)
@pytest.inline_callbacks
def test_get_user_login_id(
        patch, order_id, invoice, archive_response, expected
):
    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(
            order_id, lookup_yt=True, src_tvm_service=None,
            log_extra=None):
        if archive_response is None:
            raise archive.NotFoundError
        async.return_value(archive_response)
        yield
    login_id = yield invoices._get_user_login_id(
        order_id=order_id,
        invoice=invoice,
        log_extra=None,
    )

    assert login_id == expected


@pytest.mark.parametrize('order_id,expected', [
    ('many_ops_order_id', True),
    ('few_ops_order_id', False),
    ('many_ops_order_id_custom_limit', False),
])
@pytest.mark.config(MAX_INVOICE_COMPENSATION_OPERATIONS=2)
@pytest.mark.filldb(
    orders='for_test_will_have_too_many_compensation_operations'
)
@pytest.inline_callbacks
def test_will_have_too_many_compensation_operations(patch, order_id, expected):
    payable_order = yield _fetch_payable_order(order_id)
    _patch_v2_invoice_retrieve(patch, payable_order)
    client = invoices._Client(payable_order, 'stq')
    invoice = yield client.fetch_invoice()
    actual = yield invoice.will_have_too_many_compensation_operations(
        payable_order
    )
    assert actual == expected


def _cashback_order_fields(cashback_cost):
    return {
        'fields': {
            'order': {
                'cashback_cost': cashback_cost,
            },
            'extra_data': {
                'cashback': {
                    'is_cashback': True
                }
            }
        }
    }


def _missing_cashback_order_fields():
    return {
        'fields': {
        }
    }


def _composite_v2_invoice_update_call(
        id_, items_by_payment_type, need_cvn, operation_id=None, payments=None,
        pass_params=None, transaction_payload_params=None, intent=None, antifraud_payload=None
):
    if payments is None:
        payments = payment_with_card_and_wallet()
    elif payments is _NO_PAYMENTS:
        payments = None

    if antifraud_payload is None:
        antifraud_payload = {'some_antifraud_param': 'some_value'}
    if pass_params is None:
        pass_params = {'some_pass_param': 'some_value'}

    return {
        'args': (),
        'kwargs': {
            'id_': id_,
            'items_by_payment_type': items_by_payment_type,
            'operation_id': operation_id or 'invoice/version/2',
            'need_cvn': need_cvn,
            'originator': 'processing',
            'version': 2,
            'user_ip': '::1/128',
            'yandex_uid': 'some_user_uid',
            'pass_params': pass_params,
            'antifraud_payload': antifraud_payload,
            'payments': payments,
            'tvm_src_service': 'stq',
            'transaction_payload': transaction_payload_params,
            'user_login_id': None,
            'intent': intent,
            'log_extra': None,
        }
    }


def _compensation_create_call(
        api_version,
        id_,
        operation_id,
        version,
        product_id,
        region_id,
        gateway_name=None,
        pass_params=None,
):
    return {
        'args': (),
        'kwargs': {
            'api_version': api_version,
            'invoice_id': id_,
            'operation_id': operation_id,
            'originator': 'processing',
            'version': version,
            'gross_amount': decimal.Decimal(100),
            'acquiring_rate': decimal.Decimal('0.02'),
            'product_id': product_id,
            'region_id': region_id,
            'tvm_src_service': 'stq',
            'gateway_name': gateway_name,
            'pass_params': pass_params,
            'log_extra': None,
        },
    }


def _compensation_refund_call(
        api_version, id_, operation_id, trust_payment_id, net_amount, version):
    return {
        'args': (),
        'kwargs': {
            'api_version': api_version,
            'invoice_id': id_,
            'operation_id': operation_id,
            'originator': 'processing',
            'version': version,
            'trust_payment_id': trust_payment_id,
            'net_amount': decimal.Decimal(net_amount),
            'tvm_src_service': 'stq',
            'log_extra': None,
        }
    }


def _composite_v2_invoice_create_call(id_, due=None, payments=None, billing_service='card'):
    return {
        'args': (),
        'kwargs': {
            'id_': id_,
            'invoice_due': due or dt.datetime(2019, 1, 1),
            'billing_service': billing_service,
            'payments': payments or payment_with_card_and_wallet(),
            'currency': 'RUB',
            'user_ip': '::1/128',
            'yandex_uid': 'some_user_uid',
            'pass_params': {},
            'invoice_tz_id': 'Europe/Moscow',
            'country_id': 'rus',
            'personal_phone_id': 'some_personal_phone_id',
            'automatic_clear_delay': 10800,
            'tvm_src_service': 'stq',
            'service': 'taxi',
            'log_extra': None,
            'user_login_id': None,
        },
    }


def payment_with_card_and_wallet():
    return [
        transactions.CardLikePayment(
            type_='card',
            method='1',
            billing_id='card-1',
        ),
        transactions.WalletPayment(
            method='w/long-hash',
            service='13',
            account_id='w/long-hash'
        ),
    ]


def payment_with_coop_account():
    return [
        transactions.CardLikePayment(
            type_='coop_account',
            method='1',
            billing_id='card-1',
        ),
    ]


def payment_with_card():
    return [
        transactions.CardLikePayment(
            type_='card',
            method='1',
            billing_id='card-1',
        ),
    ]


def payment_with_agent():
    return [transactions.AgentPayment(agent_id='007')]


def card_like_payment(payment_type, omit_billing_id=None):
    return [
        transactions.CardLikePayment(
            type_=payment_type,
            method='1',
            billing_id=(None if omit_billing_id else 'card-1'),
        ),
    ]


@pytest.mark.parametrize(
    'order_id,is_in_experiment,is_trust_preferred_processing_exp,'
    'expected_processing,expected_create_calls,expected_exception', [
        (
            'some_pending_order_id',
            True,
            False,
            invoices.Processing(
                via_transactions=True,
                invoice=_WILL_BE_SET_INSIDE_TEST,
            ),
            [],
            NoException(),
        ),
        (
            'some_composite_order_id',
            False,
            False,
            invoices.Processing(
                via_transactions=True,
                invoice=_WILL_BE_SET_INSIDE_TEST,
            ),
            [],
            NoException(),
        ),
        (
            'some_composite_not_migrated_order_id',
            True,
            False,
            invoices.Processing(
                via_transactions=True,
                invoice=_WILL_BE_SET_INSIDE_TEST,
            ),
            [],
            NoException(),
        ),
        (
            'some_pending_order_id',  # with_trust_exp
            True,
            True,
            invoices.Processing(
                via_transactions=True,
                invoice=_WILL_BE_SET_INSIDE_TEST,
            ),
            [],
            NoException(),
        ),
        (
            'agent_without_id_order_id',
            False,
            False,
            None,
            [],
            pytest.raises(invoices.BadPaymentMethod),
        ),
        (
            'agent_with_unknown_id_order_id',
            False,
            False,
            None,
            [],
            pytest.raises(invoices.BadPaymentMethod),
        ),
        (
            'yandex_card_order_id',
            True,
            False,
            invoices.Processing(
                via_transactions=True,
                invoice=_WILL_BE_SET_INSIDE_TEST,
            ),
            [],
            NoException(),
        ),
])
@pytest.mark.config(
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
    USE_TRANSACTIONS_FROM_PY2=True,
    FETCH_USE_TRANSACTIONS_EXPERIMENT=True,
    BILLING_AGENT_IDS=['007'],
)
@pytest.mark.filldb(
    orders='for_test_try_process_invoice',
)
@pytest.inline_callbacks
def test_try_process_invoice(
        monkeypatch, patch, order_id, is_in_experiment,
        is_trust_preferred_processing_exp, expected_processing,
        expected_create_calls, expected_exception,
):
    _patch_experiments3_get_values(patch, is_in_experiment, is_trust_preferred_processing_exp)
    payable_order = yield _fetch_payable_order(order_id)
    if expected_processing is not None:
        expected_processing = expected_processing._replace(
            invoice=invoices.InvoiceV2(payable_order.order_doc['invoice']),
        )

    _patch_v2_invoice_retrieve(patch, payable_order)
    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', 'stq')
    create_mock = _patch_v2_invoice_create(patch, payable_order)

    processing = None
    with expected_exception:
        processing = yield invoices.try_process_invoice(payable_order)
    assert processing == expected_processing
    assert create_mock.calls == expected_create_calls


@pytest.mark.parametrize(
    'order_id, hold_options, expected, expected_create_calls, '
    'expected_update_calls, extra_params',
    [
        (
            'some_composite_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '120', 'tips': '10'},
                            'personal_wallet': {'ride': '80'}
                        },
                        fiscal_receipt_infos=_FISCAL_RECEIPT_INFOS_WITH_FOOTER,
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        ),
                    ),
                    False,
                )
            ],
            {}
        ),
        (
            'some_composite_order_id',
            payment_handler.HoldOptions(can_hold=False, with_cvn=False),
            False,
            [],
            [],
            {},
        ),
        (
            'some_composite_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            None,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '120', 'tips': '10'},
                            'personal_wallet': {'ride': '80'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        ),
                    ),
                    False,
                )
            ],
            {
                'transactions_exception': transactions.ConflictError,
                'expectation': exceptions.RaceConditionError,
            },
        ),
        (
            'some_composite_toll_road_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_toll_road_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '120', 'toll_road': '50', 'tips': '10'},
                            'personal_wallet': {'ride': '80'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {}
        ),
        (
            'some_composite_toll_road_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            None,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_toll_road_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '120', 'toll_road': '50', 'tips': '10'},
                            'personal_wallet': {'ride': '80'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {
                'transactions_exception': transactions.ConflictError,
                'expectation': exceptions.RaceConditionError,
            },
        ),
        (
                'some_composite_withdraw_amount_part_order_id',
                payment_handler.HoldOptions(can_hold=True, with_cvn=False),
                True,
                [],
                [
                    _composite_v2_invoice_update_call(
                        'some_composite_withdraw_amount_part_order_id',
                        _make_payment_items_list(
                            {
                                'card': {'ride': '125', 'tips': '10'},
                                'personal_wallet': {'ride': '75'}
                            },
                            merchant=transactions.Merchant(
                                'some_park_id_some_uuid',
                                'some_alias_id',
                            )
                        ),
                        False,
                    )
                ],
                {
                    'plus_wallet_split': plus_wallet.PaymentSplit(
                        elements=[
                            _card_split(25, 'ride'),
                            _wallet_split(5, 'ride'),
                        ],
                        currency='RUB',
                    )
                },
        ),
        (
            'some_composite_withdraw_amount_full_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_withdraw_amount_full_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '130', 'tips': '10'},
                            'personal_wallet': {'ride': '70'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {
                'plus_wallet_split': plus_wallet.PaymentSplit(
                    elements=[
                        _card_split(30, 'ride'),
                        _wallet_split(0, 'ride'),
                    ],
                    currency='RUB',
                )
            },
        ),
        (
                'some_composite_withdraw_amount_extra_order_id',
                payment_handler.HoldOptions(can_hold=True, with_cvn=False),
                True,
                [],
                [
                    _composite_v2_invoice_update_call(
                        'some_composite_withdraw_amount_extra_order_id',
                        _make_payment_items_list(
                            {
                                'card': {'ride': '130', 'tips': '10'},
                                'personal_wallet': {'ride': '70'}
                            },
                            merchant=transactions.Merchant(
                                'some_park_id_some_uuid',
                                'some_alias_id',
                            )
                        ),
                        False,
                    )
                ],
                {
                    'plus_wallet_split': plus_wallet.PaymentSplit(
                        elements=[
                            _card_split(30, 'ride'),
                            _wallet_split(0, 'ride'),
                        ],
                        currency='RUB',
                    )
                },
        ),
        (
            'some_composite_cashback_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            None,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_cashback_order_id',
                    _make_payment_items_list(
                        {
                            'card': {
                                'ride': '120', 'cashback': '50', 'tips': '10'
                            },
                            'personal_wallet': {'ride': '80'}
                        }, fiscal_receipt_infos=_FISCAL_RECEIPT_INFOS_WITH_FOOTER,
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {
                'transactions_exception': transactions.ConflictError,
                'expectation': exceptions.RaceConditionError,
            },
        ),
        (
            'some_composite_refund_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_composite_refund_order_id'
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_refund_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '30', 'tips': '10'},
                            'personal_wallet': {'ride': '170'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {},
        ),
        (
            'some_composite_refund_order_id',
            payment_handler.HoldOptions(can_hold=False, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_composite_refund_order_id'
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_refund_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '30', 'tips': '10'},
                            'personal_wallet': {'ride': '170'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        ),
                    ),
                    False,
                )
            ],
            {},
        ),
        (
            'some_composite_partial_refund_both_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_partial_refund_both_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'tips': '10'},
                            'personal_wallet': {'ride': '50'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {},
        ),
        (
            'some_composite_full_refund_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_full_refund_order_id',
                    _make_payment_items_list(
                        {
                            'card': {},
                            'personal_wallet': {}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {},
        ),
        (
            'some_composite_hold_and_refund_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'some_composite_hold_and_refund_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '120'},
                            'personal_wallet': {'ride': '80'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {},
        ),
        (
            'some_same_sum_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            False,
            [],
            [],
            {},
        ),
        (
            'some_future_composite_coop_account_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_future_composite_coop_account_order_id',
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_future_composite_coop_account_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '30', 'tips': '10'},
                            'personal_wallet': {'ride': '170'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {},
        ),
        (
            'some_old_coop_account_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_old_coop_account_order_id',
                    due=dt.datetime(2018, 1, 1),
                    payments=payment_with_coop_account(),
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_old_coop_account_order_id',
                    _make_payment_items_list(
                        {
                            'coop_account': {'ride': '30', 'tips': '10'},
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                    payments=payment_with_coop_account(),
                )
            ],
            {},
        ),
        (
            'some_future_composite_coop_account_order_id',  # with_trust_exp
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_future_composite_coop_account_order_id',
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_future_composite_coop_account_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '30', 'tips': '10'},
                            'personal_wallet': {'ride': '170'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                    pass_params={'some_pass_param': 'some_value',
                                 'terminal_route_data':
                                     {'preferred_processing_cc': _NEW_TRUST_INTEGRATION}},
                )
            ],
            {
                'is_trust_preferred_processing_exp': True,
                'is_processing_exp_old_active_from': True,
            },
        ),
        (
            'some_future_composite_coop_account_order_id',  # with_trust_exp
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_future_composite_coop_account_order_id',
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_future_composite_coop_account_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '30', 'tips': '10'},
                            'personal_wallet': {'ride': '170'}
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                )
            ],
            {
                'is_trust_preferred_processing_exp': True,
            },
        ),
        (
            'cash_with_transactions_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    'cash_with_transactions_order_id',
                    _make_payment_items_list(
                        {
                            'card': {},
                        },
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    False,
                    payments=_NO_PAYMENTS,
                )
            ],
            {},
        ),
        (
            'cash_with_sum_to_pay_with_transactions_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [],
            {
                'transactions_exception': None,
                'expectation': ValueError,
            },
        ),
        (
            'agent_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'agent_order_id', payments=payment_with_agent(),
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    id_='agent_order_id',
                    items_by_payment_type=_make_payment_items_list(
                        {'agent': {'ride': '123.45'}},
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    need_cvn=False,
                    payments=payment_with_agent(),
                )
            ],
            {},
        ),
        (
            'yandex_card_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'yandex_card_order_id', payments=card_like_payment('yandex_card'),
                    due=datetime.datetime(2021, 8, 3, 13, 22)
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    id_='yandex_card_order_id',
                    items_by_payment_type=_make_payment_items_list(
                        {'yandex_card': {'ride': '123.45'}},
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    need_cvn=False,
                    payments=card_like_payment('yandex_card'),
                )
            ],
            {},
        ),
        (
            'some_cargo_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_cargo_order_id', payments=card_like_payment('yandex_card'),
                    due=datetime.datetime(2021, 8, 3, 13, 22),
                    billing_service='cargo'
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    id_='some_cargo_order_id',
                    items_by_payment_type=_make_payment_items_list(
                        {'yandex_card': {'ride': '123.45'}},
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        )
                    ),
                    need_cvn=False,
                    payments=card_like_payment('yandex_card'),
                )
            ],
            {},
        ),
        (
            'coop_account_prehold_order_id',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            [],
            [
                _composite_v2_invoice_update_call(
                    id_='coop_account_prehold_order_id',
                    payments=card_like_payment('card', omit_billing_id=True),
                    items_by_payment_type=_make_payment_items_list(
                        items_by_type={'card': {}},
                        fiscal_receipt_infos=_FISCAL_RECEIPT_INFOS,
                        merchant=transactions.Merchant(
                            'some_park_id_some_uuid',
                            'some_alias_id',
                        ),
                    ),
                    need_cvn=False,
                    antifraud_payload={},
                    pass_params={},
                )
            ],
            {}
        )
    ]
)
@pytest.mark.config(
    BILLING_CASHBACK_OPERATOR={
        'product_id': 'cashback_product',
        'personal_tin_id': 'cashback_personal_tin_id',
        'vat': 'nds_20',
    },
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    BILLING_RECEIPT_FOOTER_FOR_PLUS=True,
    BILLING_FISCAL_RECEIPT_COUNTRIES=['rus'],
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'yataxi': {
            'RUB': '13',
        }
    },
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
    TRANSACTIONS_PASS_MERCHANT_INFO=True,
    MIN_DUE_TO_STOP_USING_COOP_ACCOUNT_PAYMENT=(
        '2018-12-31T00:00:00.000000+00:00'
    ),
    BILLING_AGENT_IDS=['007'],
    BILLING_TIME_BEFORE_CLEAR_HOLDED={'rus': 10800}
)
@pytest.mark.translations(
    [
        ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'some_title'),
        (
            'client_messages',
            'fiscal_receipt.cashback.title',
            'ru',
            'cashback_title',
        ),
        (
            'client_messages',
            'fiscal_receipt.cashback.footer',
            'ru',
            'receipt footer text',
        ),
    ]
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_order',
    orders='for_test_try_process_invoice',
    parks='for_test_try_update_from_order',
    tariff_settings='for_test_try_update_from_order',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_order',
)
@pytest.inline_callbacks
def test_try_update_from_order(
        monkeypatch, patch, order_id, hold_options, expected,
        expected_create_calls, expected_update_calls, extra_params,
):
    transactions_exception = extra_params.get('transactions_exception')
    expectation = (
        pytest.raises(extra_params['expectation'])
        if 'expectation' in extra_params
        else NoException()
    )
    is_trust_preferred_processing_exp = (
        'is_trust_preferred_processing_exp' in extra_params
    )
    is_processing_exp_old_active_from = (
        'is_processing_exp_old_active_from' in extra_params
    )
    plus_wallet_split = extra_params.get('plus_wallet_split')

    _patch_experiments3_get_values(
        patch,
        True,
        is_trust_preferred_processing_exp,
        is_processing_exp_old_active_from,
    )
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch, patch, payable_order, transactions_exception,
        plus_wallet_split
    )
    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    with expectation:
        updated = yield invoice.try_update_from_order(
            payable_order, hold_options, None
        )
        assert updated == expected
    assert invoice.is_transactions_ready
    assert create_mock.calls == expected_create_calls
    assert update_mock.calls == expected_update_calls


_COMPENSATION_UPDATE = {
    'compensation': {
        'operations': [],
        'version': 3,
    }
}


@pytest.mark.parametrize(
    'order_id,use_v3,update_on_create,expected_is_transactions_ready,'
    'transactions_exception,'
    'expectation,'
    'expected_create_calls,'
    'expected_compensate_calls,expected_refund_calls,expected', [
        (
            'some_already_compensated_order_id',
            False,
            {},
            False,
            None,
            NoException(),
            [],
            [],
            [],
            False,
        ),
        (
            'some_already_independently_compensated_order_id',
            False,
            {},
            False,
            None,
            NoException(),
            [],
            [],
            [],
            False,
        ),
        (
            'some_compensation_order_id',
            False,
            _COMPENSATION_UPDATE,
            True,
            None,
            NoException(),
            [
                _composite_v2_invoice_create_call(
                    'some_compensation_order_id'
                )
            ],
            [
                _compensation_create_call(
                    api_version='v3',
                    id_='some_compensation_order_id',
                    operation_id='compensation_operation_id',
                    version=3,
                    product_id=None,
                    region_id=None,
                )
            ],
            [],
            True,
        ),
        (
            'too_many_operations_order_id',
            False,
            _COMPENSATION_UPDATE,
            True,
            None,
            pytest.raises(invoices.TooManyOperationsError),
            [
                _composite_v2_invoice_create_call(
                    'too_many_operations_order_id'
                )
            ],
            [],
            [],
            True,
        ),
        (
            'some_compensation_order_id',
            True,
            _COMPENSATION_UPDATE,
            True,
            None,
            NoException(),
            [
                _composite_v2_invoice_create_call(
                    'some_compensation_order_id'
                )
            ],
            [
                _compensation_create_call(
                    api_version='v3',
                    id_='some_compensation_order_id',
                    operation_id='compensation_operation_id',
                    version=3,
                    product_id=None,
                    region_id=None,
                )
            ],
            [],
            True,
        ),
        (
            'some_compensation_order_id',
            False,
            _COMPENSATION_UPDATE,
            True,
            transactions.ConflictError,
            pytest.raises(exceptions.RaceConditionError),
            [
                _composite_v2_invoice_create_call(
                    'some_compensation_order_id'
                )
            ],
            [
                _compensation_create_call(
                    api_version='v3',
                    id_='some_compensation_order_id',
                    operation_id='compensation_operation_id',
                    version=3,
                    product_id=None,
                    region_id=None,
                )
            ],
            [],
            True,
        ),
        (
            'some_compensation_with_additional_params',
            False,
            {},
            True,
            None,
            NoException(),
            [
                _composite_v2_invoice_create_call(
                    'some_compensation_with_additional_params'
                )
            ],
            [
                _compensation_create_call(
                    api_version='v2',
                    id_='some_compensation_with_additional_params',
                    operation_id='compensation_operation_id',
                    version=2,
                    product_id='taxi_100500_ride',
                    region_id=225,
                    gateway_name='tlog',
                    pass_params={
                        'agent_id': 'agent_gepard',
                    },
                ),
            ],
            [],
            True,
        ),
        (
            'some_compensation_refund_order_id',
            False,
            {},
            True,
            None,
            NoException(),
            [],
            [],
            [
                _compensation_refund_call(
                    api_version='v3',
                    id_='some_compensation_refund_order_id',
                    operation_id='compensation_refund_operation_id',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='0',
                    version=3,
                )
            ],
            True,
        ),
        (
            'some_compensation_refund_order_id',
            True,
            {},
            True,
            None,
            NoException(),
            [],
            [],
            [
                _compensation_refund_call(
                    api_version='v3',
                    id_='some_compensation_refund_order_id',
                    operation_id='compensation_refund_operation_id',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='0',
                    version=3,
                )
            ],
            True,
        ),
        (
            'some_compensation_refund_order_id',
            False,
            {},
            True,
            transactions.ConflictError,
            pytest.raises(exceptions.RaceConditionError),
            [],
            [],
            [
                _compensation_refund_call(
                    api_version='v3',
                    id_='some_compensation_refund_order_id',
                    operation_id='compensation_refund_operation_id',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='0',
                    version=3,
                )
            ],
            True,
        ),
    ]
)
@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'yataxi': {
            'RUB': '13',
        }
    }
)
@pytest.mark.filldb(
    orders='for_test_try_compensate',
    tariff_settings='for_test_try_compensate',
)
@pytest.inline_callbacks
def test_try_compensate(
        monkeypatch, patch, order_id, use_v3,
        update_on_create,
        transactions_exception,
        expectation,
        expected_is_transactions_ready,
        expected_create_calls,
        expected_compensate_calls, expected_refund_calls, expected
):
    if use_v3:
        yield config.TRANSACTIONS_INDEPENDENT_COMPENSATIONS_ROLLOUT.save(100)
    _patch_experiments3_get_values(patch, True)
    payable_order = yield _fetch_payable_order(order_id)

    _patch_userapi_get_user_phone(patch)
    _patch_build_pass_params(patch)
    _patch_build_antifraud_payload(patch)
    _patch_v2_invoice_retrieve(patch, payable_order)
    create_mock = _patch_v2_invoice_create(
        patch, payable_order, update_on_create
    )

    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', 'stq')
    compensate_mock, refund_mock = _patch_compensations(
        patch, transactions_exception
    )
    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    with expectation:
        actual = yield invoice.try_compensate(payable_order, None)
        assert actual is expected
    assert invoice.is_transactions_ready is expected_is_transactions_ready
    assert create_mock.calls == expected_create_calls
    assert compensate_mock.calls == expected_compensate_calls
    assert refund_mock.calls == expected_refund_calls


def _patch_compensations(patch, exception):
    @patch('taxi.external.transactions.invoice_compensation_create')
    @async.inline_callbacks
    def invoice_compensation_create(
            api_version, invoice_id, operation_id, originator, version,
            gross_amount, acquiring_rate, product_id, region_id,
            gateway_name, pass_params, tvm_src_service, log_extra=None,
    ):
        if exception is not None:
            raise exception
        async.return_value()
        yield

    @patch('taxi.external.transactions.invoice_compensation_refund')
    @async.inline_callbacks
    def invoice_compensation_refund(
            api_version, invoice_id, operation_id, originator, version,
            trust_payment_id, net_amount, tvm_src_service, log_extra=None,
    ):
        if exception is not None:
            raise exception
        async.return_value()
        yield
    return invoice_compensation_create, invoice_compensation_refund


@pytest.mark.config(
    REFUND_COMPENSATIONS_SINCE='1999-01-01T00:00:00+00:00'
)
@pytest.mark.parametrize(
    ('order_id,use_ng,transactions_exception,expectation,expected_calls,'
     'expected_updated'), [
        (
            'some_no_transactions_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_rounding_refund_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_same_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_hold_fail_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_compensation_fail_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_hold_before_compensation_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_pending_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_refund_fail_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_refund_fail_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/2',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=2,
                )
            ],
            True,
        ),
        (
            'some_first_refund_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_first_refund_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=2,
                )
            ],
            True,
        ),
        (
                'too_many_operations_order_id',
                False,
                None,
                pytest.raises(invoices.TooManyOperationsError),
                [],
                False,
        ),
        (
            'some_independent_compensation_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v3',
                    id_='some_independent_compensation_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=4,
                )
            ],
            True,
        ),
        (
            'some_independent_compensation_order_id',
            True,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v3',
                    id_='some_independent_compensation_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=4,
                )
            ],
            True,
        ),
        (
            'some_independent_compensation_py2_order_id',
            True,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v3',
                    id_='some_independent_compensation_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=4,
                )
            ],
            True,
        ),
        (
            'some_later_independent_compensation_order_id',
            False,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_later_independent_compensation_order_id',
            True,
            None,
            NoException(),
            [],
            False,
        ),
        (
            'some_transactions_after_py2_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_transactions_after_py2_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=2,
                )
            ],
            True,
        ),
        (
            'some_first_refund_order_id',
            False,
            transactions.ConflictError,
            pytest.raises(exceptions.RaceConditionError),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_first_refund_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=2,
                )
            ],
            None,
        ),
        (
            'some_personal_wallet_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_personal_wallet_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=2,
                )
            ],
            True,
        ),
        (
            'some_first_refund_cleared_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_first_refund_cleared_order_id',
                    operation_id='compensation/refund/tpi/some_trust_payment_id/1',
                    trust_payment_id='some_trust_payment_id',
                    net_amount='100',
                    version=2,
                )
            ],
            True,
        ),
        (
            'some_split_refund_first_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_split_refund_first_order_id',
                    operation_id='compensation/refund/tpi/first_trust_payment_id/1',
                    trust_payment_id='first_trust_payment_id',
                    net_amount='100',
                    version=2,
                ),
            ],
            True,
        ),
        (
            'some_split_refund_second_order_id',
            False,
            None,
            NoException(),
            [
                _compensation_refund_call(
                    api_version='v2',
                    id_='some_split_refund_second_order_id',
                    operation_id='compensation/refund/tpi/second_trust_payment_id/1',
                    trust_payment_id='second_trust_payment_id',
                    net_amount='101',
                    version=2,
                ),
            ],
            True,
        )
    ]
)
@pytest.mark.filldb(
    orders='for_test_try_refund_compensations_after_hold',
)
@pytest.inline_callbacks
def test_try_refund_compensations_after_hold(
        monkeypatch, patch, order_id, use_ng, transactions_exception,
        expectation, expected_calls, expected_updated,
):
    yield config.COMPENSATION_REFUND_ORDER_NG.save(use_ng)
    _patch_experiments3_get_values(patch, True)
    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', 'stq')
    _, refund_mock = _patch_compensations(patch, transactions_exception)
    payable_order = yield _fetch_payable_order(order_id)
    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    with expectation:
        actual_updated = yield invoice.try_refund_compensations_after_hold(
            payable_order,
            log_extra=None
        )
        assert actual_updated is expected_updated
    assert refund_mock.calls == expected_calls


def _patch_for_try_update_from_sum_to_work(
        monkeypatch, patch, payable_order, transactions_exception,
        split=None, expected_intent=None
):
    _patch_userapi_get_user_phone(patch)
    _patch_build_pass_params(patch)
    _patch_build_antifraud_payload(patch)
    _patch_v2_invoice_retrieve(patch, payable_order)
    create_mock = _patch_v2_invoice_create(patch, payable_order)
    update_mock = _patch_v2_invoice_update(patch, transactions_exception, expected_intent=expected_intent)
    _patch_build_pass_params(patch)
    _patch_cashback_payment_split(patch, split=split)
    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', 'stq')
    return create_mock, update_mock


@pytest.mark.parametrize(
    'split,order_id,expected_updated,expected_is_transactions_ready,'
    'expected_create_calls,expected_update_calls', [
        (
            plus_wallet.PaymentSplit(
                elements=[
                    _card_split(20, 'ride'),
                    _card_split(0, 'tips'),
                    _wallet_split(0, 'ride'),
                ],
                currency='RUB',
            ),
            'some_same_sum_order_id',
            False,
            False,
            [],
            [],
        ),
        (
            plus_wallet.PaymentSplit(
                elements=[
                    _card_split(0, 'ride'),
                    _card_split(0, 'tips'),
                ],
                currency='RUB',
            ),
            'some_refund_sum_order_id',
            True,
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_refund_sum_order_id'
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_refund_sum_order_id',
                    _make_payment_items_list(
                        {
                            # 'card': {'ride': '20'},
                            'personal_wallet': {'ride': '35'}
                        },
                        fiscal_receipt_infos=collections.defaultdict(lambda: None),
                    ),
                    True,
                    'one_time/update_just_closed',
                    intent='test_intent',
                ),
            ],
        ),
        (
            plus_wallet.PaymentSplit(
                elements=[
                    _card_split(20, 'ride'),
                    _card_split(0, 'tips'),
                    _wallet_split(10, 'ride'),
                ],
                currency='RUB',
            ),
            'some_different_sum_order_id',
            True,
            True,
            [
                _composite_v2_invoice_create_call(
                    'some_different_sum_order_id'
                )
            ],
            [
                _composite_v2_invoice_update_call(
                    'some_different_sum_order_id',
                    _make_payment_items_list(
                        {
                            'card': {'ride': '20'},
                            'personal_wallet': {'ride': '15'}
                        },
                        fiscal_receipt_infos=collections.defaultdict(lambda: None),
                    ),
                    True,
                    'one_time/update_just_closed',
                    intent='test_intent',
                ),
            ],
        ),
    ]
)
@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'yataxi': {
            'RUB': '13',
        }
    },
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_just_closed',
    orders='for_test_try_update_from_just_closed',
    tariff_settings='for_test_try_update_from_just_closed',
    parks='for_test_try_update_from_just_closed',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_just_closed',
)
@pytest.inline_callbacks
def test_try_update_from_just_closed(
        monkeypatch, patch, split, order_id,
        expected_updated, expected_is_transactions_ready,
        expected_create_calls, expected_update_calls,
):
    _patch_experiments3_get_values(patch, True)
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch=monkeypatch,
        patch=patch,
        payable_order=payable_order,
        transactions_exception=None,
        split=split,
        expected_intent='test_intent',
    )
    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    updated = yield invoice.try_update_from_just_closed(payable_order, True, intent='test_intent')
    assert invoice.is_transactions_ready is expected_is_transactions_ready
    assert updated == expected_updated
    assert create_mock.calls == expected_create_calls
    assert update_mock.calls == expected_update_calls


@pytest.mark.parametrize('order_id,expected', [
    (
        'card_order_id',
        transactions.CardLikePayment('card', 'card-1', '1'),
    ),
    (
        'apple_order_id',
        transactions.CardLikePayment('applepay', 'apple-2', '2'),
    ),
    (
        'google_order_id',
        transactions.CardLikePayment('googlepay', 'google-3', '3'),
    ),
    (
        'wallet_order_id',
        transactions.WalletPayment('w/long-hash', '13', 'w/long-hash'),
    ),
])
@pytest.mark.filldb(
    orders='for_test_get_main_payment',
)
@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'yataxi': {
            'RUB': '13',
        }
    }
)
@pytest.inline_callbacks
def test_get_main_payment(order_id, expected):
    payable_order = yield _fetch_payable_order(order_id)
    actual = yield invoices.get_main_payment_or_none(payable_order, log_extra=None)
    assert actual == expected


@pytest.mark.parametrize('order_id,expected', [
    (
        'coop_order_id',
        transactions.CardLikePayment('coop_account', 'card', '28'),
    ),
    (
        'future_coop_order_id',
        transactions.CardLikePayment('card', 'card', '28'),
    ),
]
)
@pytest.mark.config(
    MIN_DUE_TO_STOP_USING_COOP_ACCOUNT_PAYMENT=(
        '2020-08-12T00:00:00.000000+00:00'
    ),
)
@pytest.mark.filldb(orders='for_test_get_main_payment')
@pytest.inline_callbacks
def test_get_main_payment_coop_account(order_id, expected):
    payable_order = yield _fetch_payable_order(order_id)
    coop_payable = coop.PayableOrderCoop(payable_order.order_doc)
    coop_payable._payment_method_id = 'card'
    coop_payable._billing_id = '28'
    actual = yield invoices.get_main_payment_or_none(coop_payable)
    assert actual == expected


@pytest.mark.parametrize('order_id,expected', [
    ('synced_order_id', True),
    ('not_synced_order_id', False),
])
@pytest.mark.filldb(orders='for_test_is_synced_with')
@pytest.inline_callbacks
def test_is_synced_with(order_id, expected, patch):
    _patch_experiments3_get_values(patch, True)
    payable_order = yield _fetch_payable_order(order_id)
    invoice = invoices.InvoiceV2(payable_order.order_doc['invoice'])
    assert invoice.is_synced_with(payable_order) is expected


@pytest.mark.parametrize(
    'order_id,is_crutch,is_in_experiment,use_transactions_by_default,refund_cash_via_transactions,expected',
    [
        ('touched_by_py2_order_id', False, False, False, False, False),
        (
            'active_py2_transaction_migrated_order_id',
            False,
            False,
            False,
            False,
            False,
        ),
        ('py2_transaction_migrated_order_id', False, False, False, False, True),
        (
            'py2_transaction_active_transactions_refund_order_id',
            False,
            False,
            False,
            False,
            True
        ),
        ('py2_transaction_migrated_order_id', False, False, False, False, True),
        (
            'py2_transaction_active_transactions_old_refund_order_id',
            False,
            False,
            False,
            False,
            True
        ),
        (
            'active_py2_compensation_migrated_order_id',
            False,
            False,
            False,
            False,
            False,
        ),
        (
            'py2_compensation_migrated_order_id',
            False,
            False,
            False,
            False,
            True,
        ),
        ('cashback_order_id', False, False, False, False, True),
        ('composite_transactions_order_id', False, False, False, False, True),
        ('transactions_order_id', False, False, False, False, True),
        ('composite_transactions_order_id', True, False, False, False, False),
        (
            'composite_transactions_order_id',
            False,
            experiments3.Experiments3RequestError,
            False,
            False,
            True
        ),
        (
            'with_hold_success_transactions_transaction_order_id',
            False,
            False,
            False,
            False,
            True,
        ),
        (
            'with_clear_success_transactions_transaction_order_id',
            False,
            False,
            False,
            False,
            False,
        ),
        (
            'with_clear_fail_transactions_transaction_order_id',
            False,
            False,
            False,
            False,
            False
        ),
        ('composite_py2_order_id', False, False, False, False, False),
        ('composite_fresh_order_id', False, True, False, False, True),
        ('composite_fresh_with_py2_compensation_order_id', False, True, False,
         False, False),
        (
            'composite_fresh_with_py2_compensation_refund_order_id',
            False,
            True,
            False,
            False,
            False,
        ),
        ('composite_fresh_order_id', False, False, False, False, False),
        (
            'composite_fresh_with_transactions_compensation_order_id',
            False,
            False,
            False,
            False,
            True,
        ),
        (
            'composite_fresh_with_transactions_inactive_compensation_order_id',
            False,
            False,
            False,
            False,
            True,
        ),
        (
            'composite_fresh_with_transactions_compensation_refund_order_id',
            False,
            False,
            False,
            False,
            True,
        ),
        (
            'composite_fresh_with_transactions_inactive_compensation_refund_order_id',
            False,
            False,
            False,
            False,
            True,
        ),
        (
            'composite_fresh_order_id',
            False,
            experiments3.Experiments3RequestError,
            False,
            False,
            False,
        ),
        (
            'composite_very_fresh_order_id',
            False,
            experiments3.Experiments3RequestError,
            False,
            False,
            True,
        ),
        ('corp_order_id', False, True, False, False, False),
        ('personal_wallet_order_id', False, True, False, False, True),
        # DEFAULT cases
        ('touched_by_py2_order_id', False, False, True, False, True),
        ('active_py2_transaction_order_id', False, False, True, False, False),
        ('active_py2_compensation_order_id', False, False, True, False, False),
        ('active_py2_compensation_refund_order_id', False, False, True, False, False),
        ('composite_transactions_order_id', True, False, True, False, False),
        (
            'with_clear_success_transactions_transaction_order_id',
            False,
            False,
            True,
            False,
            True,
        ),
        ('composite_py2_order_id', False, False, True, False, True),
        (
            'composite_fresh_with_py2_compensation_order_id',
            False,
            True,
            True,
            False,
            True,
        ),
        ('corp_order_id', False, True, True, False, False),
        (
            'migrated_to_cash_order_without_transactions_id',
            False,
            False,
            True,
            False,
            False,
        ),
        (
            'non_migrated_to_cash_order_with_transactions_id',
            False,
            False,
            True,
            False,
            False,
        ),
        (
            'migrated_to_cash_order_with_transactions_id',
            False,
            False,
            True,
            False,
            False,
        ),
        (
            'migrated_to_cash_order_without_transactions_id',
            False,
            False,
            True,
            True,
            False,
        ),
        (
            'non_migrated_to_cash_order_with_transactions_id',
            False,
            False,
            True,
            True,
            False,
        ),
        (
            'migrated_to_cash_order_with_transactions_id',
            False,
            False,
            True,
            True,
            True,
        ),
        (
            'migrated_to_cash_order_with_sum_to_pay',
            False,
            False,
            True,
            True,
            False,
        ),
        (
            'agent_order',
            False,
            False,
            False,
            False,
            True,
        )
    ]
)
@pytest.mark.filldb(
    orders='for_test_transactions_enabled',
)
@pytest.mark.config(
    USE_TRANSACTIONS_FROM_PY2=True,
    FETCH_USE_TRANSACTIONS_EXPERIMENT=True,
    SEND_TO_TRANSACTIONS_SINCE_DUE='2025-01-01T00:00:00+00:00'
)
@pytest.inline_callbacks
def test_transactions_enabled(
        monkeypatch, patch, order_id, is_crutch, is_in_experiment,
        use_transactions_by_default, refund_cash_via_transactions, expected):
    monkeypatch.setattr(settings, 'CRUTCH', is_crutch)
    yield config.USE_TRANSACTIONS_FROM_PY2_BY_DEFAULT.save(
        use_transactions_by_default,
    )
    yield config.BILLING_REFUND_CASH_VIA_TRANSACTIONS.save(
        refund_cash_via_transactions,
    )
    _patch_experiments3_get_values(patch, is_in_experiment)
    payable_order = yield _fetch_payable_order(order_id)
    actual = yield invoices.transactions_enabled(payable_order, None)
    assert actual is expected


@pytest.mark.filldb(orders='for_test_ensure_purchase_tokens')
@pytest.inline_callbacks
def test_ensure_purchase_tokens(patch, load):
    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({'purchase_token': '6'})

    order_id = '42'
    payable_order = yield _fetch_payable_order(order_id)
    yield invoices._ensure_purchase_tokens(payable_order)
    actual = yield dbh.orders.Doc.find_one_by_id(order_id)
    actual.pop('updated')

    expected = json.loads(load("expected_ensure_purchase_tokens.json"))
    assert actual == expected


@pytest.mark.parametrize(
    'order_id,refund_non_refundable,expected,expected_update_calls', [
        (
            # Expect to refund non-refundable order
            'non_refundable_order_id',
            True,
            True,
            [
                _composite_v2_invoice_update_call(
                    'non_refundable_order_id',
                    _make_payment_items_list(
                        {
                            'card': {},
                        }
                    ),
                    False,
                    payments=payment_with_card(),
                )
            ],
        ),
        (
            # Expect to NOT refund non-refundable order when config is disabled
            'non_refundable_order_id',
            False,
            False,
            [],
        ),
        (
            # Expect to refund refundable order
            'refundable_order_id',
            True,
            True,
            [
                _composite_v2_invoice_update_call(
                    'refundable_order_id',
                    _make_payment_items_list(
                        {
                            'card': {},
                        }
                    ),
                    False,
                    payments=payment_with_card(),
                )
            ],
        ),
        (
            # Expect to refund refundable order when config is disabled
            'refundable_order_id',
            False,
            True,
            [
                _composite_v2_invoice_update_call(
                    'refundable_order_id',
                    _make_payment_items_list(
                        {
                            'card': {},
                        }
                    ),
                    False,
                    payments=payment_with_card(),
                )
            ],
        ),
        (
            # Expect to NOT refund non-refundable order when config is disabled
            'manually_refunded_non_refundable_order_id',
            False,
            True,
            [
                _composite_v2_invoice_update_call(
                    id_='manually_refunded_non_refundable_order_id',
                    items_by_payment_type=_make_payment_items_list(
                        {
                            'card': {},
                        }
                    ),
                    need_cvn=False,
                    payments=payment_with_card(),
                    operation_id='<manual_op_id>',
                )
            ],
        ),
    ]
)
@pytest.mark.config(
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    BILLING_FISCAL_RECEIPT_COUNTRIES=['rus'],
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'yataxi': {
            'RUB': '13',
        }
    },
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
    MIN_DUE_TO_STOP_USING_COOP_ACCOUNT_PAYMENT=(
        '2018-12-31T00:00:00.000000+00:00'
    ),
)
@pytest.mark.translations(
    [
        ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'some_title'),
    ]
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_order',
    orders='for_test_try_process_invoice',
    parks='for_test_try_update_from_order',
    tariff_settings='for_test_try_update_from_order',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_order',
)
@pytest.inline_callbacks
def test_non_refundable(
        monkeypatch, patch, order_id, refund_non_refundable,
        expected, expected_update_calls,
):
    _patch_experiments3_get_values(patch, True)
    yield config.BILLING_PY2_REFUND_NON_REFUNDABLE.save(refund_non_refundable)
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch=monkeypatch,
        patch=patch,
        payable_order=payable_order,
        transactions_exception=None,
    )

    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    hold_options = payment_handler.HoldOptions(can_hold=True, with_cvn=False)
    updated = yield invoice.try_update_from_order(
        payable_order, hold_options, None
    )
    assert updated == expected
    assert invoice.is_transactions_ready
    assert create_mock.calls == []
    assert update_mock.calls == expected_update_calls


@pytest.mark.parametrize(
    'order_id,hold_options,expected,extra_params',
    [
        (
            'same_merchant_id_and_same_composite_sum',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            False,
            {},
        ),
        (
            'same_merchant_id_and_not_same_composite_sum',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            {},
        ),
        (
            'not_same_merchant_id_and_same_composite_sum',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            {},
        ),
        (
            'not_same_merchant_id_and_same_zero_composite_sum',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            False,
            {},
        ),
        (
            'not_same_merchant_id_and_not_same_composite_sum',
            payment_handler.HoldOptions(can_hold=True, with_cvn=False),
            True,
            {}
        ),
    ]
)
@pytest.mark.config(
    BILLING_CASHBACK_OPERATOR={
        'product_id': 'cashback_product',
        'personal_tin_id': 'cashback_personal_tin_id',
        'vat': 'nds_20',
    },
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    UPDATE_TRANSACTIONS_IGNORE_MERCHANT_IF_SUMS_ARE_ZERO=True,
    BILLING_RECEIPT_FOOTER_FOR_PLUS=True,
    BILLING_FISCAL_RECEIPT_COUNTRIES=['rus'],
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'yataxi': {
            'RUB': '13',
        }
    },
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
    TRANSACTIONS_PASS_MERCHANT_INFO=True,
    MIN_DUE_TO_STOP_USING_COOP_ACCOUNT_PAYMENT=(
        '2018-12-31T00:00:00.000000+00:00'
    ),
    BILLING_AGENT_IDS=['007'],
    BILLING_TIME_BEFORE_CLEAR_HOLDED={'rus': 10800}
)
@pytest.mark.translations(
    [
        ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'some_title'),
        (
            'client_messages',
            'fiscal_receipt.cashback.title',
            'ru',
            'cashback_title',
        ),
        (
            'client_messages',
            'fiscal_receipt.cashback.footer',
            'ru',
            'receipt footer text',
        ),
    ]
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_order',
    orders='for_test_try_process_invoice',
    parks='for_test_try_update_from_order',
    tariff_settings='for_test_try_update_from_order',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_order',
)
@pytest.inline_callbacks
def test_try_update_from_sum_with_check_for_same_driver(
        monkeypatch, patch, order_id, hold_options, expected, extra_params,
):
    _patch_experiments3_get_values(patch, True)
    transactions_exception = extra_params.get('transactions_exception')
    expectation = (
        pytest.raises(extra_params['expectation'])
        if 'expectation' in extra_params
        else NoException()
    )
    plus_wallet_split = extra_params.get('plus_wallet_split')
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch, patch, payable_order, transactions_exception,
        plus_wallet_split
    )
    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    with expectation:
        updated = yield invoice.try_update_from_order(
            payable_order, hold_options, None
        )
        assert updated == expected


@pytest.mark.parametrize(
    'order_id', [
        ('some_composite_order_id'),
    ]
)
@pytest.mark.config(
    MAX_INVOICE_OPERATIONS=0,
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_order',
    orders='for_test_try_process_invoice',
    parks='for_test_try_update_from_order',
    tariff_settings='for_test_try_update_from_order',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_order',
)
@pytest.inline_callbacks
def test_too_many_operations(
        monkeypatch, patch, order_id,
):
    _patch_experiments3_get_values(patch, True)
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch=monkeypatch,
        patch=patch,
        payable_order=payable_order,
        transactions_exception=None,
    )

    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    hold_options = payment_handler.HoldOptions(can_hold=True, with_cvn=False)
    with pytest.raises(invoices.TooManyOperationsError):
        yield invoice.try_update_from_order(
            payable_order, hold_options, None
        )
    assert create_mock.calls == []
    assert update_mock.calls == []


@pytest.mark.parametrize('order_id,expected', [
    ('empty_main_payment_order_id', [])
])
@pytest.mark.filldb(orders='for_test_get_payments')
@pytest.inline_callbacks
def test_get_payments(order_id, expected):
    payable_order = yield _fetch_payable_order(order_id)
    actual = yield invoices.get_payments(payable_order)
    assert actual == expected


@pytest.inline_callbacks
def test_get_compensations_api_version_v2():
    api_version = yield invoices._get_compensations_api_version('some_order_id')
    assert api_version == 'v2'


@pytest.mark.config(
    TRANSACTIONS_INDEPENDENT_COMPENSATIONS_ROLLOUT=100
)
@pytest.inline_callbacks
def test_get_compensations_api_version_v3():
    api_version = yield invoices._get_compensations_api_version('some_order_id')
    assert api_version == 'v3'


@pytest.mark.parametrize('order_id,expected', [
    ('empty_main_payment_composite_order_id', [])
])
@pytest.mark.filldb(orders='for_test_get_payments')
@pytest.inline_callbacks
def test_get_payments_failure(order_id, expected):
    payable_order = yield _fetch_payable_order(order_id)
    with pytest.raises(RuntimeError):
        yield invoices.get_payments(payable_order)


@pytest.mark.parametrize('omit_billing_id', [False, True])
@pytest.mark.parametrize(
    'payment_type', ['card', 'coop_account', 'applepay', 'googlepay'],
)
@pytest.mark.config(
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    BILLING_FISCAL_RECEIPT_COUNTRIES=['rus'],
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
)
@pytest.mark.translations(
    [
        ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'some_title'),
    ]
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_order',
    orders='for_test_try_process_invoice',
    parks='for_test_try_update_from_order',
    tariff_settings='for_test_try_update_from_order',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_order',
)
@pytest.inline_callbacks
def test_omit_billing_id(monkeypatch, patch, payment_type, omit_billing_id):
    order_id = 'some_card_order_id'
    _patch_experiments3_get_values(patch, True)
    yield config.TRANSACTIONS_OMIT_BILLING_ID.save(omit_billing_id)
    yield db.orders.update(
        {'_id': order_id}, {'$set': {'payment_tech.type': payment_type}},
    )
    payments = card_like_payment(payment_type, omit_billing_id=omit_billing_id)
    payment_items_list = _make_payment_items_list(
        {payment_type: {'ride': '123'}},
    )
    expected_create_calls = [
        _composite_v2_invoice_create_call(
            order_id, payments=payments,
        )
    ]
    expected_update_calls = [
        _composite_v2_invoice_update_call(
            order_id, payment_items_list, False, payments=payments,
        )
    ]
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch=monkeypatch,
        patch=patch,
        payable_order=payable_order,
        transactions_exception=None,
    )

    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    hold_options = payment_handler.HoldOptions(can_hold=True, with_cvn=False)
    updated = yield invoice.try_update_from_order(
        payable_order, hold_options, None
    )
    assert updated
    assert invoice.is_transactions_ready
    assert create_mock.calls == expected_create_calls
    assert update_mock.calls == expected_update_calls


@pytest.mark.parametrize(
    'order_id',
    [
        'transaction_payload_order_id_with_db_id',
        'transaction_payload_order_id_without_db_id',
    ],
)
@pytest.mark.config(
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    BILLING_FISCAL_RECEIPT_COUNTRIES=['rus'],
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
)
@pytest.mark.translations(
    [
        ('client_messages', 'fiscal_receipt.title.rus', 'ru', 'some_title'),
    ]
)
@pytest.mark.filldb(
    cities='for_test_try_update_from_order',
    orders='for_test_try_process_invoice',
    parks='for_test_try_update_from_order',
    tariff_settings='for_test_try_update_from_order',
)
@pytest.mark.load_data(
    countries='for_test_try_update_from_order',
)
@pytest.inline_callbacks
def test_get_transaction_payload(monkeypatch, patch, order_id):
    omit_billing_id = True
    payment_type = 'card'
    _patch_experiments3_get_values(patch, True)
    _patch_send_transaction_payload_exp3(patch, True)
    yield config.TRANSACTIONS_OMIT_BILLING_ID.save(omit_billing_id)
    yield db.orders.update(
        {'_id': order_id}, {'$set': {'payment_tech.type': payment_type}},
    )
    payments = card_like_payment(payment_type, omit_billing_id=omit_billing_id)
    payment_items_list = _make_payment_items_list(
        {payment_type: {'ride': '123'}},
    )
    expected_create_calls = [
        _composite_v2_invoice_create_call(
            order_id, payments=payments,
        )
    ]
    transaction_payload_params = {
        'alias_id': 'some_alias_id',
        'tariff_class': 'some_tariff_class',
        'driver': {
            'clid': 'some_park_id',
            'driver_profile_id': 'some_driver_id',
        }
    }
    if order_id == 'transaction_payload_order_id_with_db_id':
        transaction_payload_params['driver']['park_id'] = 'some_park_id'
    expected_update_calls = [
        _composite_v2_invoice_update_call(
            order_id, payment_items_list, False, payments=payments,
            transaction_payload_params=transaction_payload_params,
        )
    ]
    payable_order = yield _fetch_payable_order(order_id)
    create_mock, update_mock = _patch_for_try_update_from_sum_to_work(
        monkeypatch=monkeypatch,
        patch=patch,
        payable_order=payable_order,
        transactions_exception=None,
    )
    invoice = invoices.InvoiceV2(
        copy.deepcopy(payable_order.order_doc['invoice'])
    )
    hold_options = payment_handler.HoldOptions(can_hold=True, with_cvn=False)
    updated = yield invoice.try_update_from_order(
        payable_order, hold_options, None
    )
    assert updated
    assert invoice.is_transactions_ready
    assert create_mock.calls == expected_create_calls
    assert update_mock.calls == expected_update_calls


def _patch_v2_invoice_retrieve(patch, payable_order):
    @patch('taxi.external.transactions.v2_invoice_retrieve')
    @async.inline_callbacks
    def v2_invoice_retrieve(
            id_,
            prefer_transactions_data,
            tvm_src_service,
            log_extra=None,
    ):
        assert prefer_transactions_data
        assert tvm_src_service == 'stq'
        async.return_value(payable_order.order_doc['invoice'])
        yield


def _patch_v2_invoice_create(patch, payable_order, extra_update=None, expected_billing_service=None):
    """
    :param patch:
    :type payable_order: taxi.internal.order_kit.payment_handler.PayableOrder
    """
    @patch('taxi.external.transactions.v2_invoice_create')
    @async.inline_callbacks
    def v2_invoice_create(
            id_, invoice_due, billing_service, payments, currency, user_ip,
            yandex_uid, pass_params, invoice_tz_id, country_id, personal_phone_id,
            automatic_clear_delay, tvm_src_service, service, log_extra=None,
            user_login_id=None,
    ):
        if expected_billing_service:
            assert billing_service == expected_billing_service

        payable_order.doc['invoice']['transactions_ready'] = True
        payable_order.doc['invoice'].update(extra_update or {})
        async.return_value({})
        yield
    return v2_invoice_create


def _patch_v2_invoice_update(patch, exception=None, expected_intent=None):
    @patch('taxi.external.transactions.v2_invoice_update')
    @async.inline_callbacks
    def v2_invoice_update(
            id_, operation_id, originator,
            items_by_payment_type, version, user_ip, yandex_uid, pass_params,
            antifraud_payload, payments, need_cvn, tvm_src_service,
            transaction_payload, user_login_id=None, intent=None, log_extra=None,
    ):
        assert intent == expected_intent
        if exception is not None:
            raise exception
        async.return_value()
        yield
    return v2_invoice_update


def _patch_cashback_payment_split(patch, split=None):
    @patch('taxi.external.plus_wallet.payment_split')
    @async.inline_callbacks
    def payment_split(
            sum_to_pay, payment, *args, **kwargs
    ):
        if split is None:
            result = plus_wallet.PaymentSplit(
                elements=[
                    _card_split(20, 'ride'),
                    _wallet_split(10, 'ride'),
                ],
                currency='RUB',
            )
        else:
            withdraw_amount_request = payment.complements[0].withdraw_amount
            if withdraw_amount_request is not None:
                assert withdraw_amount_request == split.elements[1].sum
            result = split

        _assert_split_matches_sum_to_pay(result, sum_to_pay)
        async.return_value(result)
        yield


def _assert_split_matches_sum_to_pay(split, sum_to_pay):
    sum_from_split = invoices._convert_split_to_composite_sum(split).as_flat_sum()
    sum_from_sum_to_pay = invoices._convert_inner_sum_to_pay_to_sum(
        _convert_cashback_sum_to_pay_to_inner_sum_to_pay(sum_to_pay)
    )
    assert sum_from_split == sum_from_sum_to_pay


def _convert_cashback_sum_to_pay_to_inner_sum_to_pay(sum_to_pay):
    result = {
        'ride': payment_helpers.decimal_to_inner(sum_to_pay.ride)
    }
    if sum_to_pay.tips is not None:
        result['tips'] = payment_helpers.decimal_to_inner(sum_to_pay.tips)
    return result


def _patch_build_pass_params(patch):
    @patch('taxi.internal.order_kit.payment_handler._build_common_pass_params')
    @async.inline_callbacks
    def build_pass_params(
            order_doc, persistent_id, payment_method_type,
            preferred_processing=None, log_extra=None
    ):
        pass_params = {'some_pass_param': 'some_value'}
        if preferred_processing:
            pass_params.update({'terminal_route_data':
                                {'preferred_processing_cc': _NEW_TRUST_INTEGRATION}})
        async.return_value(pass_params)
        yield


def _patch_build_antifraud_payload(patch):
    @patch('taxi.internal.order_kit.payment_handler.build_transactions_antifraud_payload')
    @async.inline_callbacks
    def build_transactions_antifraud_payload(
            order_doc, payment_method_type, log_extra=None,
    ):
        async.return_value({'some_antifraud_param': 'some_value'})
        yield


@async.inline_callbacks
def _fetch_payable_order(order_id):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    payable_order = payment_handler.PayableOrder(order)
    async.return_value(payable_order)


def _patch_experiments3_get_values(patch, is_in_experiment,
                                   is_trust_preferred_processing_exp=False,
                                   is_processing_exp_old_active_from=True):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def get_values(
            consumer, experiments_args, retries=3,
            delay=0, log_extra=None,
    ):
        result = []
        assert consumer == 'stq/update_transactions'
        if is_in_experiment is experiments3.Experiments3RequestError:
            raise experiments3.Experiments3RequestError
        if is_in_experiment:
            result = [
                experiments3.ExperimentsValue(
                    name='use_transactions_from_update_transactions',
                    value={},
                )
            ]
        if is_trust_preferred_processing_exp:
            active_from = '2020-01-01T00:00:00'
            if is_processing_exp_old_active_from:
                active_from = '2000-01-01T00:00:00'
            result.append(
                experiments3.ExperimentsValue(
                    name='use_trust_preferred_processing',
                    value={
                        'preferred_processing_cc': _NEW_TRUST_INTEGRATION,
                        'active_from': active_from,
                    },
                ))
        async.return_value(result)
        yield
    return get_values


def _patch_send_transaction_payload_exp3(patch, is_transaction_payload):
    @patch('taxi.internal.payment_kit.invoices.is_sending_transaction_payload_enabled')
    @async.inline_callbacks
    def is_sending_transaction_payload_enabled(
        order_id, phone_id, log_extra=None
    ):
        async.return_value(is_transaction_payload)
        yield
    return is_sending_transaction_payload_enabled


def _patch_userapi_get_user_phone(patch):
    @patch('taxi.internal.userapi.get_user_phone')
    @async.inline_callbacks
    def get_user_phone(
            phone_id,
            primary_replica=False,
            fields=None,
            log_extra=None
    ):
        user_phone_doc = {'personal_phone_id': 'some_personal_phone_id'}
        async.return_value(dbh.user_phones.Doc(user_phone_doc))
        yield


@pytest.mark.filldb(
    orders='for_test_ensure_park_has_products',
    parks='for_test_ensure_park_has_products',
)
@pytest.inline_callbacks
def test_ensure_park_has_products_happy_path(patch):
    @patch('taxi.internal.park_manager.create_billing_products')
    @async.inline_callbacks
    def create_billing_products(
            billing_service, park_doc, billing_client_id,
            billing_client_id_start, operator_uid,
            log_extra=None):
        assert False, 'create_billing_products should not be called'
        yield

    payable_order = yield _fetch_payable_order('some_card_order_id')
    park_doc = yield invoices.ensure_park_has_products(
        park_id=payable_order.park_id,
        payable_order=payable_order,
        log_extra=None,
    )
    assert park_doc['_id'] == 'some_park_id'


@pytest.mark.filldb(
    cities='for_test_ensure_park_has_products',
    orders='for_test_ensure_park_has_products',
    parks='for_test_ensure_park_has_products',
)
@pytest.mark.load_data(
    countries='for_test_ensure_park_has_products',
)
@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_AUTOMATIC_PRODUCTS=['cargo']
)
@pytest.mark.parametrize('order_id,expected_cargo_products', [
    # create billing_cargo_product_ids
    (
        'some_cargo_order_id',
        [
            [
                dt.datetime(2020, 1, 1), None,
                {
                    'ride': 'some_park_id_some_billing_client_id_ride',
                    'tips': 'some_park_id_some_billing_client_id_tips'
                }
            ]
        ]
    ),
    # append to billing_cargo_product_ids
    (
        'another_cargo_order_id',
        [
            [
                dt.datetime(2020, 1, 1),
                dt.datetime(2021, 2, 2),
                {
                    'ride': 'another_park_id_some_billing_client_id_ride',
                    'tips': 'another_park_id_some_billing_client_id_tips'
                }
            ],
            [
                dt.datetime(2021, 2, 2), None,
                {
                    'ride': 'ride_product',
                    'tips': 'tips_product'
                }
            ]
        ]
    )
])
@pytest.inline_callbacks
def test_ensure_park_has_products_change_cargo_products(
        patch, order_id, expected_cargo_products):
    @patch('taxi.external.billing.create_partner')
    @async.inline_callbacks
    def create_partner(
            billing_service, operator_uid, billing_client_id, name, email,
            phone, region_id, url=None, log_extra=None):
        yield

    @patch('taxi.external.billing.create_service_product')
    @async.inline_callbacks
    def create_service_product(
            billing_service, partner_id, product_id, product_name,
            service_fee=None, log_extra=None):
        yield

    payable_order = yield _fetch_payable_order(order_id)
    park_doc = yield invoices.ensure_park_has_products(
        park_id=payable_order.park_id,
        payable_order=payable_order,
        log_extra=None,
    )
    assert park_doc['billing_cargo_product_ids'] == expected_cargo_products


@pytest.mark.filldb(
    orders='for_test_ensure_park_has_products',
    parks='for_test_ensure_park_has_products',
)
@pytest.inline_callbacks
def test_ensure_park_has_products_skip_creating_products():
    payable_order = yield _fetch_payable_order('some_cargo_order_id')
    park_doc = yield invoices.ensure_park_has_products(
        park_id=payable_order.park_id,
        payable_order=payable_order,
        log_extra=None,
    )
    assert 'billing_cargo_product_ids' not in park_doc
