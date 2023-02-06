import copy
import datetime
import decimal
import typing

import pytest

from . import consts
from . import models
from . import pytest_marks

# pylint: disable=invalid-name
Decimal = decimal.Decimal

COUNTRY = models.Country.Russia

DEFAULT_CREATED = consts.NOW
DEFAULT_HELD = (consts.NOW_DT + datetime.timedelta(minutes=10)).isoformat()
DEFAULT_CLEARED = (consts.NOW_DT + datetime.timedelta(minutes=20)).isoformat()
DEFAULT_REFUNDED = (consts.NOW_DT + datetime.timedelta(minutes=30)).isoformat()

DEFAULT_PAYMENT_ID = 'default-payment-id-123'

DEFAULT_ITEMS = [
    models.Item(item_id='111::sub1', quantity='1', price='50'),
    models.Item(item_id='111::sub2', quantity='1', price='70'),
    models.Item(item_id='111::sub3', quantity='1', price='80'),
    models.Item(item_id='222', quantity='1', price='100'),
]

EXTERNAL_PAYMENT_ID = '3b3c5abe337bcf0027c0a2827c9785e4'
DEFAULT_FISCAL_RECEIPT_URL = 'https://trust-test.yandex.ru/123'

DEFAULT_TRANSACTION = {
    'created': DEFAULT_CREATED,
    'external_payment_id': EXTERNAL_PAYMENT_ID,
    'held': DEFAULT_HELD,
    'cleared': DEFAULT_CLEARED,
    'initial_sum': [
        {'amount': '50', 'item_id': '111::sub1'},
        {'amount': '70', 'item_id': '111::sub2'},
        {'amount': '80', 'item_id': '111::sub3'},
        {'amount': '300', 'item_id': '222'},
    ],
    'operation_id': 'create:a5d66e1d57be46308d71ade837c199e',
    'payment_method_id': DEFAULT_PAYMENT_ID,
    'payment_type': 'card',
    'refunds': [],
    'status': 'hold_success',
    'sum': models.to_transaction_items(DEFAULT_ITEMS),
    'technical_error': False,
    'terminal_id': '95426005',
    'updated': '2021-02-10T11:52:33.262000+03:00',
    'fiscal_receipt_url': DEFAULT_FISCAL_RECEIPT_URL,
}

REFUND_EXTERNAL_PAYMENT_ID = '602fb67eb955d7fa1934e812'
DEFAULT_REFUND_STATUS = 'refund_success'
DEFAULT_REFUND = {
    'created': DEFAULT_CREATED,
    'updated': '2021-02-10T11:52:33.262000+03:00',
    'sum': models.to_transaction_items(DEFAULT_ITEMS),
    'status': DEFAULT_REFUND_STATUS,
    'refunded': DEFAULT_REFUNDED,
    'fiscal_receipt_refund_url': DEFAULT_FISCAL_RECEIPT_URL,
    'operation_id': 'create:a5d66e1d57be46308d71ade837c1992',
    'external_payment_id': REFUND_EXTERNAL_PAYMENT_ID,
}


@pytest.fixture(name='grocery_payments_retrieve')
def _grocery_payments_retrieve(taxi_grocery_payments):
    async def _inner(country=COUNTRY, **kwargs):
        return await taxi_grocery_payments.post(
            '/payments/v1/retrieve',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                **kwargs,
            },
        )

    return _inner


@pytest_marks.PAYMENT_TYPES
async def test_payment(grocery_payments_retrieve, transactions, payment_type):
    transaction = copy.deepcopy(DEFAULT_TRANSACTION)
    transaction['payment_type'] = payment_type.value

    transactions.retrieve.mock_response(transactions=[transaction])

    transactions.retrieve.check(id=consts.ORDER_ID)

    response = await grocery_payments_retrieve()
    assert response.status_code == 200

    assert transactions.retrieve.times_called == 1

    _check_transactions(
        response,
        'payment',
        [
            {
                'created': DEFAULT_CREATED,
                'external_payment_id': EXTERNAL_PAYMENT_ID,
                'held': DEFAULT_HELD,
                'cleared': DEFAULT_CLEARED,
                'items': _to_response_items(DEFAULT_ITEMS),
                'payment_method': {
                    'id': DEFAULT_PAYMENT_ID,
                    'type': payment_type.value,
                },
                'status': 'hold_success',
                'transaction_type': 'payment',
                'fiscal_receipt_url': DEFAULT_FISCAL_RECEIPT_URL,
            },
        ],
    )


@pytest_marks.PAYMENT_TYPES
async def test_refund(grocery_payments_retrieve, transactions, payment_type):
    transaction = copy.deepcopy(DEFAULT_TRANSACTION)
    transaction['payment_type'] = payment_type.value
    transaction['refunds'] = [DEFAULT_REFUND]

    transactions.retrieve.mock_response(transactions=[transaction])

    response = await grocery_payments_retrieve()
    assert response.status_code == 200

    _check_transactions(
        response,
        'refund',
        [
            {
                'created': DEFAULT_CREATED,
                'external_payment_id': REFUND_EXTERNAL_PAYMENT_ID,
                'cleared': DEFAULT_REFUNDED,
                'items': _to_response_items(DEFAULT_ITEMS),
                'payment_method': {
                    'id': DEFAULT_PAYMENT_ID,
                    'type': payment_type.value,
                },
                'status': DEFAULT_REFUND_STATUS,
                'transaction_type': 'refund',
                'fiscal_receipt_url': DEFAULT_FISCAL_RECEIPT_URL,
            },
        ],
    )


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_retrieve, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.retrieve.check(id=invoice_id)

    response = await grocery_payments_retrieve(
        originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.retrieve.times_called == 1


def _check_transactions(response, transaction_type, transactions):
    response_transactions = []
    for transaction in response.json()['transactions']:
        if transaction['transaction_type'] == transaction_type:
            response_transactions.append(transaction)

    assert response_transactions == transactions


def _to_response_item(item):
    res = {
        'item_id': item.typed_item_id(item.item_id, item.item_type),
        'amount': item.amount,
    }

    return res


def _to_response_items(items: typing.List[models.Item]):
    res_items: typing.Dict[str, typing.Any] = {}
    for item in items:
        transaction_item = item.to_transaction_item()
        if transaction_item['item_id'] in res_items.keys():
            res_item = res_items[transaction_item['item_id']]
            res_item['amount'] += transaction_item['amount']
            res_item['quantity'] = str(Decimal(res_item['quantity']) + 1)
            res_item['price'] = item.price
        else:
            transaction_item['quantity'] = '1'
            res_items[transaction_item['item_id']] = transaction_item
            res_items[transaction_item['item_id']]['price'] = item.price

    return [item for key, item in res_items.items()]
