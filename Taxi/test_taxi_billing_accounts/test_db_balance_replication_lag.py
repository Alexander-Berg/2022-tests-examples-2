import datetime as dt

import pytest

from taxi_billing_accounts import db


_NOW = dt.datetime(2020, 1, 10, 8, 0, 0)


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'rollups@0.sql', 'balance_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid,expected_lag',
    [
        pytest.param(
            0,
            10,
            id=(
                'vshard with balance replication chunks, use '
                'last replicated rollup to compute lag'
            ),
        ),
        pytest.param(
            1,
            100,
            id=(
                'vshard without balance replication chunks, use '
                'earliest rollup entry to compute lag'
            ),
        ),
    ],
)
async def test_replication_lag_success(accounts_monrun_app, vid, expected_lag):
    store = db.BalanceReplicationChunksStore(
        storage=accounts_monrun_app.storage, config=accounts_monrun_app.config,
    )
    lag = await store.get_replication_lag(now=_NOW, vid=vid, log_extra=None)
    assert lag == expected_lag


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'rollups@0.sql', 'balance_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid',
    [
        pytest.param(
            0, id='last replicated rollup is fresher than now, use 0 lag',
        ),
    ],
)
async def test_negative_replication_lag(accounts_monrun_app, vid):
    store = db.BalanceReplicationChunksStore(
        storage=accounts_monrun_app.storage, config=accounts_monrun_app.config,
    )
    lag = await store.get_replication_lag(
        now=_NOW - dt.timedelta(seconds=100), vid=vid, log_extra=None,
    )
    assert lag == 0


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'rollups@0.sql', 'balance_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid',
    [
        pytest.param(2, id='vshard where last replicated rollup is absent'),
        pytest.param(3, id='vshard without rollups or replication chunks'),
    ],
)
async def test_replication_lag_fail(accounts_monrun_app, vid):
    store = db.BalanceReplicationChunksStore(
        storage=accounts_monrun_app.storage, config=accounts_monrun_app.config,
    )
    with pytest.raises(AssertionError):
        await store.get_replication_lag(now=_NOW, vid=vid, log_extra=None)
