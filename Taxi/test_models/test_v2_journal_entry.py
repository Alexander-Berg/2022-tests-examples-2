import decimal
import json

import dateutil.parser
import pytest

from taxi.billing import util

from taxi_billing_accounts import models


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'json_str, expected',
    [
        # required only fields
        (
            {
                'account_id': 100123,
                'doc_ref': 'uniq_doc_ref/1',
                'amount': '12.2345',
                'event_at': '2019-07-18T17:26:31.000000+03:00',
            },
            models.V2JournalEntry(
                account_id=100123,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('12.2345'),
                event_at=dateutil.parser.parse('2019-07-18T14:26:31'),
                idempotency_key='100123',
            ),
        ),
        # empty details
        (
            {
                'account_id': 100123,
                'doc_ref': 'uniq_doc_ref/1',
                'amount': '12.2345',
                'event_at': '2019-07-18T17:26:31.000000+03:00',
                'reason': 'empty details',
                'details': {},
            },
            models.V2JournalEntry(
                account_id=100123,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('12.2345'),
                event_at=dateutil.parser.parse('2019-07-18T14:26:31'),
                reason='empty details',
                details={},
                idempotency_key='100123',
            ),
        ),
        # details
        (
            {
                'account_id': 100123,
                'doc_ref': 'uniq_doc_ref/1',
                'amount': '12.2345',
                'event_at': '2019-07-18T17:26:31.000000+03:00',
                'reason': 'client payment',
                'details': {'alias_id': 'order_alias_id'},
            },
            models.V2JournalEntry(
                account_id=100123,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('12.2345'),
                event_at=dateutil.parser.parse('2019-07-18T14:26:31'),
                reason='client payment',
                details={'alias_id': 'order_alias_id'},
                idempotency_key='100123',
            ),
        ),
    ],
)
def test_v2_journal_entry_from_json(json_str, expected):
    entry = models.V2JournalEntry.from_json(json_str)
    assert entry == expected


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'entry, expected',
    [
        # no entry_id, details, created
        (
            models.V2JournalEntry(
                account_id=100234,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('12.2345'),
                event_at=dateutil.parser.parse('2019-07-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
            {
                'account_id': 100234,
                'doc_ref': 'uniq_doc_ref/1',
                'amount': '12.2345',
                'event_at': '2019-07-18T17:26:31.000000+00:00',
                'idempotency_key': 'idempotency_key',
            },
        ),
        # no nulls
        (
            models.V2JournalEntry(
                account_id=100234,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('12.2345'),
                event_at=dateutil.parser.parse('2019-07-18T17:26:31'),
                entry_id=10000000234,
                reason='client payment',
                details={'alias_id': 'some_alias_id'},
                created=dateutil.parser.parse('2019-03-18T10:26:31.223'),
                idempotency_key='idempotency_key',
            ),
            {
                'account_id': 100234,
                'doc_ref': 'uniq_doc_ref/1',
                'amount': '12.2345',
                'event_at': '2019-07-18T17:26:31.000000+00:00',
                'idempotency_key': 'idempotency_key',
                'entry_id': 10000000234,
                'reason': 'client payment',
                'details': {'alias_id': 'some_alias_id'},
                'created': '2019-03-18T10:26:31.223000+00:00',
            },
        ),
    ],
)
def test_v2_journal_entry_to_json(entry, expected):
    assert util.to_json(entry) == json.dumps(expected)
