import decimal
import typing

from test_payments_eda import consts

GROCERY_ORDER_ID = consts.GROCERY_ORDER_ID

DEFAULT_INVOICE = {
    'id': 'test_order',
    'created': '2020-08-14T13:31:47.150000+03:00',
    'invoice_due': '2020-08-14T13:31:47.150000+03:00',
    'operation_info': {},
    'status': 'held',
    'service': 'eats',
    # these fields are not exactly consistent, whatever
    'payment_types': ['card'],
    'sum_to_pay': [
        {
            'items': [{'amount': '100.00', 'item_id': 'food'}],
            'payment_type': 'card',
        },
    ],
    'held': [
        {
            'items': [{'amount': '10.00', 'item_id': 'food'}],
            'payment_type': 'card',
        },
    ],
    'cleared': [
        {
            'items': [{'amount': '10.00', 'item_id': 'food'}],
            'payment_type': 'card',
        },
    ],
    'debt': [
        {
            'items': [{'amount': '17.00', 'item_id': 'food'}],
            'payment_type': 'card',
        },
    ],
    'transactions': [],
    'currency': 'RUB',
    'yandex_uid': '123',
}


ITEM_PRICE_1 = decimal.Decimal('149.23')
ITEM_PRICE_2 = decimal.Decimal('100.45')
TIPS_PRICE = decimal.Decimal('5.5')

SUM_TWO_ITEMS = [
    {'item_id': '541989183', 'amount': str(ITEM_PRICE_1)},
    {'item_id': '541989181', 'amount': str(ITEM_PRICE_2)},
]

SUM_ONE_ITEM = [{'item_id': '541989183', 'amount': str(ITEM_PRICE_1)}]

SUM_TIPS = [{'item_id': 'tips', 'amount': str(TIPS_PRICE)}]

TRANSACTION: typing.Dict[str, typing.Any] = {
    'created': '2020-09-25T18:38:14.514000+03:00',
    'updated': '2020-09-25T18:38:27.532000+03:00',
    'sum': SUM_ONE_ITEM,
    'initial_sum': SUM_ONE_ITEM,
    'status': 'hold_success',
    'refunds': [],
    'external_payment_id': 'f6b6902f63b2325dd73d501a21d2dd76',
    'payment_type': 'card',
    'payment_method_id': 'card-xf6e28225990da6640dde32d3',
    'held': '2020-09-25T18:38:27.532000+03:00',
    'technical_error': False,
    'operation_id': 'create:e16d0a201d5c441ab87dcb2040b83282',
    'terminal_id': '95426005',
}

OPERATION_INFO = {'originator': 'processing', 'priority': 1, 'version': 3}

REFUND_ITEM_AMOUNT = '2809.12'
REFUND_SUM = [{'amount': REFUND_ITEM_AMOUNT, 'item_id': '232502224'}]
REFUNDS = [
    {
        'created': '2020-09-16T16:44:15.617000+03:00',
        'refunded': '2020-09-16T16:44:26.283000+03:00',
        'status': 'refund_success',
        'sum': REFUND_SUM,
        'updated': '2020-09-16T16:44:26.283000+03:00',
    },
]
