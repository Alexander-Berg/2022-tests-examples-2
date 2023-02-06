import datetime
import decimal

import pytest

from . import consts
from . import helpers
from . import models
from .plugins import configs

# pylint: disable=invalid-name
Decimal = decimal.Decimal

TRUST_URL_TEMPLATE = 'trust-{}'
TRUST_URL_TEMPLATE_REFUND = 'trust-refund-{}'
TRUST_NAME = 'trust name'

TRANSACTIONS_URL = 'transactions-{}-{}'
TRANSACTIONS_NAME = 'transactions name'

GROCERY_PAYMENTS_ADMIN_URLS = pytest.mark.experiments3(
    name='grocery_payments_admin_urls',
    consumers=['grocery-payments'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {
                'params': [
                    {
                        'name': TRANSACTIONS_NAME,
                        'type': 'transactions',
                        'url_template': TRANSACTIONS_URL,
                    },
                    {
                        'name': TRUST_NAME,
                        'type': 'trust',
                        'url_template': TRUST_URL_TEMPLATE,
                        'url_template_refund': TRUST_URL_TEMPLATE_REFUND,
                    },
                ],
            },
        },
    ],
    is_config=True,
)

CREATED = consts.NOW
HELD = (consts.NOW_DT + datetime.timedelta(minutes=10)).isoformat()
CLEARED = (consts.NOW_DT + datetime.timedelta(minutes=20)).isoformat()
REFUNDED = (consts.NOW_DT + datetime.timedelta(minutes=30)).isoformat()

PAYMENT_ID = 'default-payment-id-123'

CARD_NUMBER = '465858****7039'
CARD_SYSTEM = 'VISA'

PRICE_1 = '23.13'
PRICE_2 = '47.24'

ITEM_1_SUB_0 = {'item_id': 'item_id_1::sub0', 'amount': PRICE_1}
ITEM_1_SUB_1 = {'item_id': 'item_id_1::sub1', 'amount': PRICE_1}
ITEM_1_SUB_2 = {'item_id': 'item_id_1::sub2', 'amount': PRICE_1}
ITEM_2 = {'item_id': 'item_id_2::sub0:tips', 'amount': PRICE_2}

EXTERNAL_PAYMENT_ID = '3b3c5abe337bcf0027c0a2827c9785e4'

EXTERNAL_REFUND_ID = '602fb67eb955d7fa1934e812'
REFUND_STATUS = 'refund_success'
REFUND = {
    'created': CREATED,
    'updated': '2021-02-10T11:52:33.262000+03:00',
    'sum': [ITEM_1_SUB_1],
    'status': REFUND_STATUS,
    'refunded': REFUNDED,
    'operation_id': 'create:a5d66e1d57be46308d71ade837c1992',
    'external_payment_id': EXTERNAL_REFUND_ID,
}

TRANSACTION_STATUS = 'hold_success'
TRANSACTION = {
    'created': CREATED,
    'external_payment_id': EXTERNAL_PAYMENT_ID,
    'held': HELD,
    'cleared': CLEARED,
    'initial_sum': [],
    'operation_id': 'create:a5d66e1d57be46308d71ade837c199e',
    'payment_method_id': PAYMENT_ID,
    'payment_type': 'card',
    'refunds': [REFUND],
    'status': TRANSACTION_STATUS,
    'sum': [ITEM_1_SUB_0, ITEM_1_SUB_1, ITEM_2],
    'technical_error': False,
    'terminal_id': '95426005',
    'updated': '2021-02-10T11:52:33.262000+03:00',
}

DEBT_TRANSACTION_STATUS = 'debt_pending'
DEBT_ITEM_1_CARD = {
    'item_id': 'item_id_1::sub0',
    'price': PRICE_1,
    'quantity': '2',
}
DEBT_ITEM_2_CARD = {
    'item_id': 'item_id_2::sub0:tips',
    'price': PRICE_2,
    'quantity': '1',
    'item_type': 'tips',
}
DEBT_ITEM_1_WALLET = {
    'item_id': 'item_id_1::sub0',
    'price': PRICE_1,
    'quantity': '1',
}
DEBT = {
    'debt_id': consts.ORDER_ID,
    'created': CREATED,
    'items': [
        {
            'items': [ITEM_1_SUB_0, ITEM_1_SUB_1, ITEM_1_SUB_2],
            'payment_type': 'card',
        },
        {'items': [ITEM_1_SUB_0], 'payment_type': 'personal_wallet'},
    ],
    'version': 1,
}


def _get_originators():
    return {it.request_name for it in models.InvoiceOriginator}


@pytest.fixture(name='grocery_payments_admin_retrieve')
def _grocery_payments_admin_retrieve(taxi_grocery_payments):
    async def _inner(**kwargs):
        return await taxi_grocery_payments.post(
            '/admin/payments/v1/retrieve',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': models.Country.Russia.country_iso3,
                **kwargs,
            },
        )

    return _inner


@configs.GROCERY_CURRENCY
@GROCERY_PAYMENTS_ADMIN_URLS
async def test_basic(
        grocery_payments_admin_retrieve, transactions, cardstorage,
):
    transactions.retrieve.mock_response(transactions=[TRANSACTION])

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )

    response = await grocery_payments_admin_retrieve()
    assert response.status == 200

    must_be_used = _get_originators()

    response_total = Decimal(0)
    for originator in response.json()['originators']:
        must_be_used.remove(originator.pop('originator'))

        transactions = [_get_payment(), _get_refund()]
        total = _get_transactions_total(transactions)

        assert originator == {
            'transactions': transactions,
            'total': _get_total_template(total),
        }

        response_total += Decimal(total)

    assert not must_be_used, 'Some originators was not used: ' + str(
        must_be_used,
    )
    assert response.json()['total'] == _get_total_template(response_total)


@configs.GROCERY_CURRENCY
@GROCERY_PAYMENTS_ADMIN_URLS
async def test_with_debt(
        grocery_payments_admin_retrieve,
        transactions,
        cardstorage,
        grocery_user_debts,
):
    transactions.retrieve.mock_response(
        transactions=[TRANSACTION], operations=[],
    )

    grocery_user_debts.retrieve.mock_response(**DEBT)

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )

    response = await grocery_payments_admin_retrieve()
    assert response.status == 200

    response_total = Decimal(0)
    for originator in response.json()['originators']:
        originator.pop('originator')

        transactions = [
            _get_debt_transaction(
                items=[
                    {
                        'item_id': 'item_id_1',
                        'item_type': 'product',
                        'price': PRICE_1,
                        'quantity': '3',
                    },
                ],
                payment_type='card',
            ),
            _get_debt_transaction(
                items=[
                    {
                        'item_id': 'item_id_1',
                        'item_type': 'product',
                        'price': PRICE_1,
                        'quantity': '1',
                    },
                ],
                payment_type='personal_wallet',
            ),
            _get_payment(),
            _get_refund(),
        ]
        total = _get_transactions_total(transactions)

        assert originator == {
            'transactions': transactions,
            'total': _get_total_template(total),
        }

        response_total += total

    assert response.json()['total'] == _get_total_template(response_total)


@configs.GROCERY_CURRENCY
@GROCERY_PAYMENTS_ADMIN_URLS
async def test_with_empty_debt(
        grocery_payments_admin_retrieve,
        transactions,
        cardstorage,
        grocery_user_debts,
):
    transactions.retrieve.mock_response(transactions=[TRANSACTION])

    grocery_user_debts.retrieve.mock_response(items=[])

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )

    response = await grocery_payments_admin_retrieve()
    assert response.status == 200

    for originator in response.json()['originators']:
        for transaction in originator['transactions']:
            assert transaction['transaction_type'] != 'debt'


@configs.GROCERY_CURRENCY
@GROCERY_PAYMENTS_ADMIN_URLS
async def test_with_debt_on_update(
        grocery_payments_admin_retrieve,
        transactions,
        cardstorage,
        grocery_user_debts,
):
    transactions.retrieve.mock_response(
        transactions=[TRANSACTION],
        operations=[
            helpers.make_operation(
                sum_to_pay=[{'items': [ITEM_1_SUB_0], 'payment_type': 'card'}],
            ),
        ],
    )

    grocery_user_debts.retrieve.mock_response(**DEBT)

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )

    response = await grocery_payments_admin_retrieve()
    assert response.status == 200

    response_total = Decimal(0)
    for originator in response.json()['originators']:
        originator.pop('originator')

        transactions = [
            _get_debt_transaction(
                items=[
                    {
                        'item_id': 'item_id_1',
                        'item_type': 'product',
                        'price': PRICE_1,
                        'quantity': '2',
                    },
                ],
                payment_type='card',
            ),
            _get_debt_transaction(
                items=[
                    {
                        'item_id': 'item_id_1',
                        'item_type': 'product',
                        'price': PRICE_1,
                        'quantity': '1',
                    },
                ],
                payment_type='personal_wallet',
            ),
            _get_payment(),
            _get_refund(),
        ]
        total = _get_transactions_total(transactions)

        assert originator == {
            'transactions': transactions,
            'total': _get_total_template(total),
        }

        response_total += total

    assert response.json()['total'] == _get_total_template(response_total)


@configs.GROCERY_CURRENCY
@GROCERY_PAYMENTS_ADMIN_URLS
async def test_admin_retrieve_not_count_failed_refund(
        taxi_grocery_payments, transactions, cardstorage,
):
    another_transaction = TRANSACTION.copy()
    another_refund = REFUND.copy()
    another_refund['status'] = 'refund_fail'
    another_refund['operation_id'] = 'create:a5d66e1d57be46308d71ade837c1994'
    another_refund['external_payment_id'] = '602fb67eb955d7fa1934e814'
    another_transaction['refunds'] = [REFUND, another_refund]

    transactions.retrieve.mock_response(transactions=[another_transaction])

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )
    cardstorage.check_card_request(card_id=PAYMENT_ID)

    response = await taxi_grocery_payments.post(
        '/admin/payments/v1/retrieve',
        json={
            'order_id': consts.ORDER_ID,
            'country_iso3': models.Country.Russia.country_iso3,
        },
    )
    assert response.status == 200

    transactions = [_get_payment(), _get_refund()]
    total = _get_transactions_total(transactions)

    response_total = total * len(response.json()['originators'])
    assert response.json()['total'] == _get_total_template(response_total)


@configs.GROCERY_CURRENCY
@GROCERY_PAYMENTS_ADMIN_URLS
async def test_cartstorage_request(
        grocery_payments_admin_retrieve, transactions, cardstorage,
):
    transactions.retrieve.mock_response(transactions=[TRANSACTION])

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )
    cardstorage.check_card_request(card_id=PAYMENT_ID)

    response = await grocery_payments_admin_retrieve()
    assert response.status == 200

    assert cardstorage.times_card_called() == 1


@GROCERY_PAYMENTS_ADMIN_URLS
async def test_admin_retrieve_not_get_one_card_twice(
        grocery_payments_admin_retrieve, transactions, cardstorage,
):
    another_transaction = TRANSACTION.copy()
    OTHER_CARD_ID = 'other_card_id'
    another_transaction['payment_method_id'] = OTHER_CARD_ID
    transactions.retrieve.mock_response(
        transactions=[TRANSACTION, TRANSACTION, another_transaction],
    )

    cardstorage.mock_card(
        card_id=PAYMENT_ID, number=CARD_NUMBER, system=CARD_SYSTEM,
    )
    cardstorage.check_card_request(card_id=PAYMENT_ID)

    cardstorage.mock_card(
        card_id=OTHER_CARD_ID, number=CARD_NUMBER, system='MASTERCARD',
    )
    cardstorage.check_card_request(card_id=OTHER_CARD_ID)

    response = await grocery_payments_admin_retrieve()
    assert response.status == 200

    assert cardstorage.times_card_called() == 2


def _apply_amount(items):
    for item in items:
        price = Decimal(item['price'])
        quantity = Decimal(item['quantity'])
        item['amount'] = str(price * quantity)
    return items


def _get_total_amount(items):
    return str(sum((Decimal(it['amount']) for it in items)))


def _get_refund():
    items = _apply_amount(
        [
            {
                'item_id': 'item_id_1',
                'item_type': 'product',
                'price': PRICE_1,
                'quantity': '1',
            },
        ],
    )

    return {
        'admin_urls': [
            {
                'name': TRUST_NAME,
                'type': 'trust',
                'url': TRUST_URL_TEMPLATE_REFUND.format(EXTERNAL_REFUND_ID),
            },
            {
                'name': TRANSACTIONS_NAME,
                'type': 'transactions',
                'url': TRANSACTIONS_URL.format(
                    'transactions-eda', consts.ORDER_ID,
                ),
            },
        ],
        'cleared': REFUNDED,
        'created': CREATED,
        'items': items,
        'payment_method': {
            'id': PAYMENT_ID,
            'type': 'card',
            'extra_data': {'number': CARD_NUMBER, 'system': CARD_SYSTEM},
        },
        'status': REFUND_STATUS,
        'total': _get_total_template(_get_total_amount(items)),
        'transaction_type': 'refund',
    }


def _get_payment():
    items = _apply_amount(
        [
            {
                'item_id': 'item_id_1',
                'item_type': 'product',
                'price': PRICE_1,
                'quantity': '2',
            },
            {
                'item_id': 'item_id_2',
                'item_type': 'tips',
                'price': PRICE_2,
                'quantity': '1',
            },
        ],
    )

    return {
        'admin_urls': [
            {
                'name': TRUST_NAME,
                'type': 'trust',
                'url': TRUST_URL_TEMPLATE.format(EXTERNAL_PAYMENT_ID),
            },
            {
                'name': TRANSACTIONS_NAME,
                'type': 'transactions',
                'url': TRANSACTIONS_URL.format(
                    'transactions-eda', consts.ORDER_ID,
                ),
            },
        ],
        'cleared': CLEARED,
        'created': CREATED,
        'held': HELD,
        'items': items,
        'payment_method': {
            'id': PAYMENT_ID,
            'type': 'card',
            'extra_data': {'number': CARD_NUMBER, 'system': CARD_SYSTEM},
        },
        'status': TRANSACTION_STATUS,
        'total': _get_total_template(_get_total_amount(items)),
        'transaction_type': 'payment',
    }


def _get_debt_transaction(*, items, payment_type):
    _apply_amount(items)

    return {
        'admin_urls': [],
        'created': CREATED,
        'items': items,
        'payment_method': {'id': '', 'type': payment_type},
        'status': DEBT_TRANSACTION_STATUS,
        'total': _get_total_template(_get_total_amount(items)),
        'transaction_type': 'debt',
    }


def _get_total_template(total):
    total_str = f'{total} $SIGN$$CURRENCY$'
    return total_str.replace('.', ',')


def _get_total_dec(obj):
    total_template = obj['total']
    total_str, _ = total_template.split(' ', 2)
    total_str = total_str.replace(',', '.')
    return Decimal(total_str)


def _get_transactions_total(transactions):
    result = Decimal(0)

    for transaction in transactions:
        total = _get_total_dec(transaction)

        if transaction['transaction_type'] == 'refund':
            total *= -1

        result += total

    return result
