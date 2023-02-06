import datetime as dt

import pytest

from taxi_billing_accounts import db


_NOW = dt.datetime(2020, 1, 10, 8, 0, 0)


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'journal@0.sql', 'journal_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid,expected_lag',
    [
        pytest.param(
            0,
            10,
            id=(
                'vshard with journal replication chunks, use '
                'last replicated journal entry to compute lag'
            ),
        ),
        pytest.param(
            1,
            100,
            id=(
                'vshard without journal replication chunks, use '
                'earliest journal entry to compute lag'
            ),
        ),
    ],
)
async def test_replication_lag_success(accounts_monrun_app, vid, expected_lag):
    store = db.JournalReplicationChunksStore(
        storage=accounts_monrun_app.storage, config=accounts_monrun_app.config,
    )
    lag = await store.get_replication_lag(now=_NOW, vid=vid, log_extra=None)
    assert lag == expected_lag


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'journal@0.sql', 'journal_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid',
    [
        pytest.param(
            0,
            id='last replicated journal entry is fresher than now, use 0 lag',
        ),
    ],
)
async def test_negative_replication_lag(accounts_monrun_app, vid):
    store = db.JournalReplicationChunksStore(
        storage=accounts_monrun_app.storage, config=accounts_monrun_app.config,
    )
    lag = await store.get_replication_lag(
        now=_NOW - dt.timedelta(seconds=100), vid=vid, log_extra=None,
    )
    assert lag == 0


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'journal@0.sql', 'journal_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid',
    [
        pytest.param(
            2, id='vshard where last replicated journal entry is absent',
        ),
        pytest.param(3, id='vshard without journal entries or chunks at all'),
    ],
)
async def test_replication_lag_fail(accounts_monrun_app, vid):
    store = db.JournalReplicationChunksStore(
        storage=accounts_monrun_app.storage, config=accounts_monrun_app.config,
    )
    with pytest.raises(AssertionError):
        await store.get_replication_lag(now=_NOW, vid=vid, log_extra=None)
