# -*- coding: utf-8 -*-

import datetime
import pytest

from taxi.core import db
from taxi.internal import payments_stats
from taxi.internal.order_kit import payment_handler


@pytest.mark.now('2017-10-18T00:00:00')
@pytest.mark.config(PAYMENTS_STATS_TRANSACTION_TAIL=4)
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.inline_callbacks
def test_simple():
    payments = [
        ('00001', 5, 'USD', datetime.datetime(2017, 10, 18, 1, 24, 0), 1, False),
        ('00001', 10, 'USD', datetime.datetime(2017, 10, 18, 1, 25, 0), 2, False),
        ('00001', 25, 'USD', datetime.datetime(2017, 10, 18, 1, 26, 0), 3, False),
        ('00001', 30, 'USD', datetime.datetime(2017, 10, 18, 1, 27, 0), 4, False),
        ('00001', 50, 'USD', datetime.datetime(2017, 10, 18, 1, 28, 0), 5, False),
        ('00001', 100, 'USD', datetime.datetime(2017, 10, 18, 1, 29, 0), 6, False),
        ('00001', 200, 'USD', datetime.datetime(2017, 10, 18, 1, 17, 0), 7, False),
        ('00001', 300, 'USD', datetime.datetime(2017, 10, 18, 2, 31, 0), 8, False),
        ('00001', 400, 'RUB', datetime.datetime(2017, 10, 18, 3, 45, 0), 9, False),
        ('00001', 500, 'RUB', datetime.datetime(2017, 10, 18, 7, 15, 0), 10, False),
        ('00001', 600, 'USD', datetime.datetime(2017, 10, 18, 1, 36, 0), 11, False),
        ('00001', 700, 'USD', datetime.datetime(2017, 10, 19, 2, 15, 0), 12, False),
        ('00001', 700, 'USD', datetime.datetime(2017, 10, 19, 2, 15, 0), 12, False),
        ('00001', 700, 'USD', datetime.datetime(2017, 10, 19, 2, 15, 0), 12, False),
        ('00001', 800, 'RUB', datetime.datetime(2017, 10, 19, 2, 25, 0), 13, False),
        ('00001', 900, 'USD', datetime.datetime(2017, 10, 19, 3, 31, 0), 14, False),
        ('00001', 1000, 'RUB', datetime.datetime(2017, 10, 19, 13, 0, 0), 15, False),
        ('00001', 1100, 'USD', datetime.datetime(2017, 10, 19, 21, 0, 0), 16, False),
        ('00001', 900, 'USD', datetime.datetime(2017, 10, 19, 3, 31, 0), 14, False),
        ('00001', 1000, 'RUB', datetime.datetime(2017, 10, 19, 13, 0, 0), 15, False),
        ('00001', 1100, 'USD', datetime.datetime(2017, 10, 19, 21, 0, 0), 16, False),
        ('00001', 1200, 'EUR', datetime.datetime(2017, 10, 19, 21, 5, 0), 17, False),
        ('00001', 1300, 'EUR', datetime.datetime(2017, 10, 19, 14, 5, 0), 18, False),
        ('00001', 1300, 'EUR', datetime.datetime(2017, 10, 20, 14, 5, 0), 19, True),
    ]

    cases = [  # {'q': query, 'e': expected result}
        {
            'q': {},
            'e': {},
        },
        {
            'q': {'00001': datetime.datetime(2017, 10, 20, 0, 0, 0)},
            'e': {},
        },
        {
            'q': {'00001': datetime.datetime(2017, 10, 19, 21, 1, 0)},
            'e': {'00001': {'EUR': 1200, 'USD': 1100}},
        },
        {
            'q': {'00001': datetime.datetime(2017, 10, 19, 2, 0, 0)},
            'e': {'00001': {
                'EUR': 1200 + 1300,
                'USD': 700 + 900 + 1100,
                'RUB': 800 + 1000,
            }},
        },
        {
            'q': {'00001': datetime.datetime(2017, 10, 18, 2, 0, 0)},
            'e': {'00001': {
                'EUR': 1200 + 1300,
                'USD': 300 + 700 + 900 + 1100,
                'RUB': 400 + 500 + 800 + 1000,
            }},
        },
        {
            'q': {'00001': datetime.datetime(2017, 10, 18, 1, 0, 0)},
            'e': {'00001': {
                'EUR': 1200 + 1300,
                'USD': (
                    5 + 10 + 25 + 30 + 50 + 100 + 200 + 300 + 600 + 700 +
                    900 + 1100),
                'RUB': 400 + 500 + 800 + 1000,
            }},
        },
    ]

    # fill stats
    for payment in payments:
        yield payments_stats.register_payment(*payment)

    # exec queries
    for case in cases:
        result = yield payments_stats.aggregate_payments(case['q'])
        assert result == case['e']

    # ensure transactions tail is not bloated
    docs = yield db.cashless_payments_stats.find(
        {'clid': '00001'}, ['transactions', 'logistic_transactions']).run()
    for doc in docs:
        if 'transactions' in doc:
            assert len(doc['transactions']) <= 4
        else:
            assert 'logistic_transactions' in doc
            assert len(doc['logistic_transactions']) <= 4


@pytest.mark.parametrize('payable_clid,transaction,expected', [
    # should take park_id from order if transaction_payload is missing
    ('payable_clid', {}, 'payable_clid'),
    # should take park_id from transaction_payload if it's present
    (
        'payable_clid',
        {
            'transaction_payload': {'driver': {'clid': 'payload_clid'}}
        },
        'payload_clid'
    ),
])
def test_get_effective_park_id(payable_clid, transaction, expected):
    order_doc = {
        'performer': {
            'clid': payable_clid,
        }
    }
    payable = payment_handler.PayableOrder(order_doc)
    actual = payments_stats._get_effective_park_id(payable, transaction)
    assert actual == expected
