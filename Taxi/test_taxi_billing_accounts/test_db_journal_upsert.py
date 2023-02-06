import decimal
from typing import Dict
from typing import Tuple

import dateutil.parser
import pytest

from taxi_billing_accounts import config as ba_config
from taxi_billing_accounts import db
from taxi_billing_accounts import models


def _by_id(items) -> Dict[Tuple[str, str], models.V2JournalEntry]:
    return {(it.doc_ref, it.idempotency_key): it for it in items}


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'journal@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'journal@1.sql'))
@pytest.mark.parametrize(
    'entries',
    [
        # single entries
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T18:26:31'),
                reason='some comment',
                details={'alias_id': 'some_alias_id'},
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('2001.3400'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('0.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='zero amount',
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='one',
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('0.0001'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min non zero abs amount'},
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/4',
                amount=decimal.Decimal('-999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min amount'},
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/5',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'max amount'},
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/6',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={},
                idempotency_key='idempotency_key',
            ),
        ],
        # all in one, set 1
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key_1',
            ),
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T18:26:31'),
                reason='some comment',
                details={'alias_id': 'some_alias_id'},
                idempotency_key='idempotency_key_2',
            ),
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('2001.3400'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key_3',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('0.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='zero amount',
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'one'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('0.0001'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min non zero abs amount'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/4',
                amount=decimal.Decimal('-999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min amount'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/5',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'max amount'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/6',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={},
                idempotency_key='idempotency_key',
            ),
        ],
        # all in one, set 2
        [
            models.V2JournalEntry(
                account_id=50000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1.12'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='50000',
            ),
            models.V2JournalEntry(
                account_id=10001,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('2.1200'),
                event_at=dateutil.parser.parse('2018-10-18T18:26:31'),
                details={
                    'reason': 'some comment',
                    'alias_id': 'some_alias_id',
                },
                idempotency_key='10001',
            ),
            models.V2JournalEntry(
                account_id=10001,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('3'),
                event_at=dateutil.parser.parse('2018-10-18T18:26:32'),
                details={
                    'reason': 'some comment',
                    'alias_id': 'some_alias_id',
                },
                idempotency_key='10001',
            ),
            models.V2JournalEntry(
                account_id=20001,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('2001.3400'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='20001',
            ),
            models.V2JournalEntry(
                account_id=10002,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('21.3400'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='10002',
            ),
            models.V2JournalEntry(
                account_id=10003,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('21.300'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='10003',
            ),
            models.V2JournalEntry(
                account_id=20003,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1.300'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='20003',
            ),
            models.V2JournalEntry(
                account_id=30003,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('5.5300'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='30003',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('0.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'zero amount'},
                idempotency_key='40004',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'one'},
                idempotency_key='40004',
            ),
            models.V2JournalEntry(
                account_id=140004,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('0.0001'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min non zero abs amount'},
                idempotency_key='140004',
            ),
            models.V2JournalEntry(
                account_id=140004,
                doc_ref='uniq_doc_ref/4',
                amount=decimal.Decimal('-999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min amount'},
                idempotency_key='140004',
            ),
            models.V2JournalEntry(
                account_id=140004,
                doc_ref='uniq_doc_ref/5',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='max amount',
                idempotency_key='140004',
            ),
            models.V2JournalEntry(
                account_id=10005,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('9999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={},
                idempotency_key='10005',
            ),
        ],
    ],
)
async def test_db_journal_upsert(billing_accounts_storage, entries):
    store = db.JournalEntryStore(
        storage=billing_accounts_storage, config=ba_config.Config(),
    )
    upserted = await store.upsert(entries, log_extra={})
    assert len(upserted) == len(entries)

    entries_by_key = _by_id(entries)
    upserted_by_key = _by_id(upserted)

    assert upserted_by_key.keys() == entries_by_key.keys()
    checked = 0
    for key, ups in upserted_by_key.items():
        entry = entries_by_key[key]
        assert ups.entry_id
        assert ups.created
        assert ups.amount == entry.amount
        assert ups.event_at == entry.event_at
        assert (entry.reason if entry.reason else '') == ups.reason
        assert entry.details == ups.details
        checked += 1
    assert checked == len(entries)


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'journal@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'journal@1.sql'))
@pytest.mark.parametrize(
    'entries',
    [
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T18:26:31'),
                details={
                    'reason': 'some comment',
                    'alias_id': 'some_alias_id',
                },
                idempotency_key='idempotency_key',
            ),
        ],
        [
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('0.0001'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min non zero abs amount'},
                idempotency_key='idempotency_key',
            ),
        ],
        # all in one
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T18:26:31'),
                details={
                    'reason': 'some comment',
                    'alias_id': 'some_alias_id',
                },
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('2001.3400'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('0.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'zero amount'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/2',
                amount=decimal.Decimal('1.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='one',
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/3',
                amount=decimal.Decimal('0.0001'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='min non zero abs amount',
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/4',
                amount=decimal.Decimal('-999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'min amount'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/5',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={'reason': 'max amount'},
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=40004,
                doc_ref='uniq_doc_ref/6',
                amount=decimal.Decimal('999999999999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={},
                idempotency_key='idempotency_key',
            ),
        ],
    ],
)
async def test_db_journal_upsert_idemp(billing_accounts_storage, entries):
    store = db.JournalEntryStore(
        storage=billing_accounts_storage, config=ba_config.Config(),
    )
    first = _by_id(await store.upsert(entries, log_extra={}))
    second = _by_id(await store.upsert(entries, log_extra={}))
    assert first == second


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'journal@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'journal@1.sql'))
@pytest.mark.parametrize(
    'entries',
    [
        # foreign key constraint violation
        [
            models.V2JournalEntry(
                account_id=10000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
        ],
        # all in one
        [
            models.V2JournalEntry(
                account_id=40000,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('1001.1200'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=10004,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('0.0000'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                reason='no such account',
                idempotency_key='idempotency_key',
            ),
            models.V2JournalEntry(
                account_id=10005,
                doc_ref='uniq_doc_ref/1',
                amount=decimal.Decimal('9999999.9999'),
                event_at=dateutil.parser.parse('2018-10-18T17:26:31'),
                details={},
                idempotency_key='idempotency_key',
            ),
        ],
    ],
)
async def test_db_journal_upsert_exc(billing_accounts_storage, entries):
    store = db.JournalEntryStore(
        storage=billing_accounts_storage, config=ba_config.Config(),
    )
    with pytest.raises(db.JournalIntegrityConstraintViolationError):
        await store.upsert(entries, log_extra={})
