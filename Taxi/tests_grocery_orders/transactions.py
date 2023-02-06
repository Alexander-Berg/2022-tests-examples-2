import decimal

from . import consts

ID_NAMESPACE = 'grocery'

ITEM_PRICE_1 = decimal.Decimal('149.23')
ITEM_PRICE_2 = decimal.Decimal('100.45')

SUM = ITEM_PRICE_1 + ITEM_PRICE_2

SUM_TWO_ITEMS = [
    {'item_id': '541989183', 'amount': str(ITEM_PRICE_1)},
    {'item_id': consts.ITEM_ID, 'amount': str(ITEM_PRICE_2)},
]

OPERATION_INFO = {'originator': 'processing', 'priority': 1, 'version': 3}

REFUND_ITEM_AMOUNT = '2809.12'
REFUND_SUM = [{'amount': REFUND_ITEM_AMOUNT, 'item_id': consts.ITEM_ID}]
REFUND = {
    'created': '2020-09-16T16:44:15.617+00:00',
    'refunded': '2020-09-16T16:44:26.283+00:00',
    'status': 'refund_success',
    'sum': REFUND_SUM,
    'updated': '2020-09-16T16:44:26.283+00:00',
    'fiscal_receipt_refund_url': 'refund-receipt.html',
}

TRANSACTION = {
    'created': '2020-09-25T18:38:14.514+00:00',
    'updated': '2020-09-25T18:38:27.532+00:00',
    'sum': SUM_TWO_ITEMS,
    'initial_sum': SUM_TWO_ITEMS,
    'status': 'hold_success',
    'refunds': [REFUND],
    'external_payment_id': 'f6b6902f63b2325dd73d501a21d2dd76',
    'payment_type': 'card',
    'payment_method_id': 'card-xf6e28225990da6640dde32d3',
    'held': '2020-09-25T18:38:27.532+00:00',
    'technical_error': False,
    'operation_id': 'create:e16d0a201d5c441ab87dcb2040b83282',
    'terminal_id': '95426005',
    'fiscal_receipt_url': 'fiscal_receipt_url.html',
    'fiscal_receipt_clearing_url': 'fiscal_receipt_clearing_url.html',
}

DEFAULT_INVOICE = {
    'id': 'test_order',
    'invoice_due': '2020-08-14T13:31:47.150000+03:00',
    'operation_info': {'version': 2},
    'status': 'held',
    'service': 'eats',
    'payment_types': ['card'],
    'sum_to_pay': [{'items': SUM_TWO_ITEMS, 'payment_type': 'card'}],
    'held': [{'items': SUM_TWO_ITEMS, 'payment_type': 'card'}],
    'cleared': [{'items': SUM_TWO_ITEMS, 'payment_type': 'card'}],
    'debt': [],
    'transactions': [TRANSACTION],
    'currency': 'RUB',
    'yandex_uid': '123',
}
