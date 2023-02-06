import datetime as dt
import decimal

from billing.accounts import entries
from billing.accounts import service as aservice
from billing.generated.models import entries as models
from billing.tests import mocks


async def test_store():
    entities = mocks.TestEntities()
    accounts = mocks.TestAccounts()
    journal = mocks.TestJournal(
        accounts,
        now=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        max_entries_age_days=92,
        replication_lag_ms=1000,
    )
    entry_drafts = [
        models.JournalEntryDraft(
            agreement_id='a',
            amount='1',
            currency='RUB',
            entity_external_id='taximeter_driver_id/tdi',
            event_at=dt.datetime(2020, 1, 2),
            sub_account='s',
            details={},
            idempotency_key='1',
        ),
    ]
    appended = await entries.store(
        entities, accounts, journal, entry_drafts, 1,
    )
    assert appended == [
        aservice.AppendedEntry(
            id=1,
            account_id=1,
            amount=decimal.Decimal('1'),
            event_at=dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
            created=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
            details={},
            idempotency_key='1',
            doc_ref=1,
        ),
    ]
