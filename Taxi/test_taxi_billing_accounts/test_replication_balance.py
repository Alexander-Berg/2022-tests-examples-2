# pylint: disable=invalid-name,redefined-builtin,too-many-lines
import datetime as dt

import pytest

from taxi.billing import pgstorage
from taxi.billing.util import dates as billing_dates

from taxi_billing_accounts import db
from taxi_billing_accounts import models
from taxi_billing_accounts.replication import config_helper
from taxi_billing_accounts.replication import runner
from taxi_billing_accounts.replication.handlers import _api
from taxi_billing_accounts.replication.handlers import balance

TS_CREATED = dt.datetime(2018, 12, 31, 23, 59, 0)
LAST_ACCRUED_AT = dt.datetime(2018, 11, 1, 15, 32, 21)
LAST_ACCOUNT_ID = 22220010001

ID_0 = 22220100000  # not exists in records
ID_1 = 22220110000
ID_2 = 22220120000
ID_3 = 22220130000
ID_4 = 22220140000  # not exists in records

T_NEGATIVE_INF = dt.datetime(1, 1, 1)  # -inf
T_0 = dt.datetime(2019, 1, 1, 10, 10, 10)  # not exists in records
T_1 = dt.datetime(2019, 1, 1, 11, 11, 11)
T_2 = dt.datetime(2019, 1, 1, 12, 12, 12)
T_3 = dt.datetime(2019, 1, 1, 13, 13, 13)
T_4 = dt.datetime(2019, 1, 1, 14, 14, 14)  # not exists in records


#
# test classes
#
#############################################################################


async def test_BalanceReplicationChunk():
    obj = models.BalanceReplicationChunk(
        last_journal_id=12345,
        last_account_id=54321,
        last_accrued_at=LAST_ACCRUED_AT,
        count=20,
        created=TS_CREATED,
    )
    assert obj.last_journal_id == 12345
    assert obj.last_account_id == 54321
    assert obj.last_accrued_at == LAST_ACCRUED_AT
    assert obj.count == 20
    assert obj.created == TS_CREATED


#
# test storage structure
#
#############################################################################


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'balance_at@0.sql', 'balance_replication_chunks@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'balance_at@1.sql', 'balance_replication_chunks@1.sql'),
)
async def test_storage(accounts_cron_app):
    assert accounts_cron_app is not None
    assert accounts_cron_app.storage is not None
    balance_store = db.BalanceStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    assert balance_store is not None
    chunk_store = db.BalanceReplicationChunksStore(
        accounts_cron_app.storage, accounts_cron_app.config,
    )
    assert chunk_store is not None


#
# BalanceReplicationChunkStore
#
##############################################################################


#
# BalanceReplicationChunkStore::get_next_entries
#
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'balance_at@0.sql', 'rollups@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_get_next_entries_no_chunks_yet(accounts_cron_app):
    vid = 0
    store = db.BalanceReplicationChunksStore(
        accounts_cron_app.storage, accounts_cron_app.config,
    )
    result = await store.get_next_entries(
        vid, num_entries=15, window_size=1000010000, log_extra={},
    )
    assert len(result) == 15

    result = await store.get_next_entries(
        vid, num_entries=15, window_size=300020000, log_extra={},
    )
    assert len(result) == 10


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_get_next_entries(accounts_cron_app):
    vid = 0
    store = db.BalanceReplicationChunksStore(
        accounts_cron_app.storage, accounts_cron_app.config,
    )
    result = await store.get_next_entries(
        vid, num_entries=5, window_size=1000010000, log_extra={},
    )
    assert len(result) == 5


#
# BalanceReplicationChunkStore::save_chunk
#


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_save_chunk(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_chunks():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT last_journal_id, last_account_id, last_accrued_at
            FROM {schema}.balance_replication_chunks
            ORDER BY last_journal_id, last_account_id, last_accrued_at
        """,
            log_extra={},
        )

    before = await get_chunks()
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    result = await store.save_chunk(
        vid=vid,
        last_journal_id=123450000,
        last_account_id=543210000,
        last_accrued_at=dt.datetime(2019, 1, 1),
        count=123,
        log_extra={},
    )
    assert result.last_journal_id == 123450000
    assert result.last_account_id == 543210000
    assert result.last_accrued_at == dt.datetime(2019, 1, 1)
    assert result.count == 123
    after = await get_chunks()
    assert len(after) == len(before) + 1
    diff = [x for x in after if x not in before]
    diff0 = diff[0]
    assert diff0['last_journal_id'] == result.last_journal_id
    assert diff0['last_account_id'] == result.last_account_id
    assert diff0['last_accrued_at'] == result.last_accrued_at


#
# BalanceReplicationChunksStore::delete_replicated_entries
#


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'balance_at@0.sql', 'rollups@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_replicated_entries_no_chunks(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    before = await get_entries()
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    await store.delete_replicated_entries(
        vid=vid,
        threshold=dt.datetime(2019, 12, 12),
        chunk_size=5,
        sleep_time=0,
        dry_run=False,
        log_extra={},
    )
    after = await get_entries()
    assert after == before


# limit by chunks
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'balance_to_delete@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_replicated_entries_limit_by_chunks(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    threshold = dt.datetime(2019, 12, 12)
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    before = await get_entries()
    await store.delete_replicated_entries(
        vid=vid,
        threshold=threshold,
        chunk_size=5,
        sleep_time=0,
        dry_run=False,
        log_extra={},
    )
    after = await get_entries()

    assert len(before) == 40
    assert len(after) == 30

    # checkpoint: journal_id=300020000
    #             account_id=22199980009
    #             accrued_at=dt.datetime(2019, 1, 10, 12, 12, 12)

    removed = sorted(set(before) - set(after))
    assert [list(row.values()) for row in removed] == [
        [300010000, 22199920009, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22199930009, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200030000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200040000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200050000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200060000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200070000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200080000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200090000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22200100000, dt.datetime(2019, 1, 10, 11, 11, 11)],
    ]


# limit by threshold
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'balance_to_delete@0.sql',
        'rollups_fully_rolled@0.sql',
        'balance_replication_chunks_fully_replicated@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_replicated_entries_limit_by_threshold(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    threshold = dt.datetime(2019, 1, 10, 13, 13, 13)
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    before = await get_entries()
    await store.delete_replicated_entries(
        vid=vid,
        threshold=threshold,
        chunk_size=5,
        sleep_time=0,
        dry_run=False,
        log_extra={},
    )
    after = await get_entries()

    assert len(before) == 40
    assert len(after) == 38

    removed = sorted(set(before) - set(after))
    assert [list(row.values()) for row in removed] == [
        [300010000, 22199920009, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [300010000, 22199930009, dt.datetime(2019, 1, 10, 11, 11, 11)],
    ]


# no limit - kill all
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'balance_to_delete@0.sql',
        'rollups_fully_rolled@0.sql',
        'balance_replication_chunks_fully_replicated@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_replicated_entries_keep_last(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    threshold = dt.datetime(2019, 12, 1)
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    await store.delete_replicated_entries(
        vid=vid,
        threshold=threshold,
        chunk_size=5,
        sleep_time=0,
        dry_run=False,
        log_extra={},
    )
    after = await get_entries()
    assert [list(row.values()) for row in after] == [
        [300020000, 22199920009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199930009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199940009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199950009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199960009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199970009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199980009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22199990009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22200000009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300020000, 22200010009, dt.datetime(2019, 1, 10, 12, 12, 12)],
        [300200000, 22200010000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200020000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200030000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200040000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200050000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200060000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200070000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200080000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200090000, dt.datetime(2019, 1, 10, 14, 14, 14)],
        [300200000, 22200100000, dt.datetime(2019, 1, 10, 14, 14, 14)],
    ]


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'balance_to_delete_check_fail@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_replicated_entries_check_fail(
        accounts_cron_app, monkeypatch,
):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    threshold = dt.datetime(2019, 12, 12)
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    before = await get_entries()
    with pytest.raises(RuntimeError):
        await store.delete_replicated_entries(
            vid=vid,
            threshold=threshold,
            chunk_size=5,
            sleep_time=0,
            dry_run=False,
            log_extra={},
        )
    after = await get_entries()
    assert before == after


# limit by chunks
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_replicated_entries_dry_run(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    async def get_entries_to_delete():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT account_id, accrued_at
            FROM {schema}.balance_to_delete
            ORDER BY account_id, accrued_at
        """,
            log_extra={},
        )

    threshold = dt.datetime(2019, 12, 12)
    store = db.BalanceReplicationChunksStore(storage, accounts_cron_app.config)
    balances_before = await get_entries()
    balances_to_delete_before = await get_entries_to_delete()
    await store.delete_replicated_entries(
        vid=vid,
        threshold=threshold,
        chunk_size=5,
        sleep_time=0,
        dry_run=True,
        log_extra={},
    )
    balances_after = await get_entries()
    balances_to_delete_after = await get_entries_to_delete()

    assert balances_before == balances_after
    assert not balances_to_delete_before

    assert [list(row.values()) for row in balances_to_delete_after] == [
        [22199920009, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22199930009, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200010000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200020000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200030000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200030000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200040000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200040000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200050000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200050000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200060000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200060000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200070000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200070000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200080000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200080000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200090000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200090000, dt.datetime(2019, 1, 10, 13, 13, 13)],
        [22200100000, dt.datetime(2019, 1, 10, 11, 11, 11)],
        [22200100000, dt.datetime(2019, 1, 10, 13, 13, 13)],
    ]


#
# BalanceReplicationChunksStore::delete_old_chunks
#
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_old_chunks(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_chunks():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT last_journal_id, last_account_id, last_accrued_at
            FROM {schema}.balance_replication_chunks
            ORDER BY last_journal_id, last_account_id, last_accrued_at
        """,
            log_extra={},
        )

    before = await get_chunks()
    store = db.BalanceReplicationChunksStore(
        accounts_cron_app.storage, accounts_cron_app.config,
    )
    await store.delete_old_chunks(vid=vid, log_extra={})
    after = await get_chunks()
    assert len(after) == 1
    assert after[0] == before[-1]


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'balance_at@0.sql', 'rollups@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_delete_old_chunks_no_chunks(accounts_cron_app):
    vid = 0
    storage = accounts_cron_app.storage

    async def get_chunks():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT last_journal_id, last_account_id, last_accrued_at
            FROM {schema}.balance_replication_chunks
            ORDER BY last_journal_id, last_account_id, last_accrued_at
        """,
            log_extra={},
        )

    store = db.BalanceReplicationChunksStore(
        accounts_cron_app.storage, accounts_cron_app.config,
    )
    await store.delete_old_chunks(vid=vid, log_extra={})
    after = await get_chunks()
    assert not after


#
# replication.handlers.balance.*
#
##############################################################################

#
# BalanceRuleHandler::__init__
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_init(accounts_cron_app):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    assert handler.name == 'balance_at'
    assert handler.rule_name == 'billing_accounts_balance'


# BalanceRuleHandler::iter_chunks_to_replicate
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_iter_chunks_to_replicate(accounts_cron_app):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    async for chunk in handler.iter_chunks_to_replicate(
            app=accounts_cron_app, vid=0, chunk_size=5, log_extra={},
    ):
        assert chunk.chunk_id
        assert chunk.vid == 0
        assert len(chunk.items) == 5
        break


# no entries
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks_fully_replicated@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_iter_chunks_to_replicate_fully_replicated(
        accounts_cron_app,
):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    async for _ in handler.iter_chunks_to_replicate(  # ?? await
            app=accounts_cron_app, vid=0, chunk_size=5, log_extra={},
    ):
        assert False


# not enough data for new chunk
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_iter_chunks_to_replicate_not_enough_data(
        accounts_cron_app,
):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    async for _ in handler.iter_chunks_to_replicate(
            app=accounts_cron_app, vid=0, chunk_size=999, log_extra={},
    ):
        assert False


# BalanceRuleHandler::mark_as_replicated
# can used only after iter_chunks_to_replicate
#
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_mark_as_replicated(accounts_cron_app):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    chain = []
    async for chunk in handler.iter_chunks_to_replicate(
            app=accounts_cron_app, vid=0, chunk_size=5, log_extra={},
    ):
        ids = [x.item_id for x in chunk.items]
        last = chunk.items[-1].data
        ret = await handler.mark_as_replicated(
            app=accounts_cron_app, vid=0, ids=ids, log_extra={},
        )
        assert ret.last_journal_id == last['journal_id']
        assert ret.last_account_id == last['account_id']
        assert (
            billing_dates.microseconds_from_timestamp(ret.last_accrued_at)
            == last['accrued_at']
        )
        assert ret.count == 5
        chain.append([chunk, ret])
    assert chain


# BalanceRuleHandler::iter_chunks_to_reconcile
# just stub
#
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_iter_chunks_to_reconcile(accounts_cron_app):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    async for _ in handler.iter_chunks_to_reconcile(
            app=accounts_cron_app, vid=0, recheck_interval=10000, log_extra={},
    ):
        assert False


# BalanceRuleHandler::mark_as_reconciled
# also just stub
#
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_mark_as_reconciled(accounts_cron_app):
    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    await handler.mark_as_reconciled(
        app=accounts_cron_app, vid=0, chunk_id='fakeid', ids=[], log_extra={},
    )
    # do nothing. previous call must be done and that is enough


# BalanceRuleHandler::delete_old_chunks
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_BalanceRuleHandler_delete_old_chunks(accounts_cron_app):
    storage = accounts_cron_app.storage
    vid = 0

    async def get_chunks():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT last_journal_id, last_account_id, last_accrued_at
            FROM {schema}.balance_replication_chunks
            ORDER BY last_journal_id, last_account_id, last_accrued_at
        """,
            log_extra={},
        )

    async def get_entries():
        schema = storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(storage, vid)
        return await executor.fetch(
            f"""
            SELECT journal_id, account_id, accrued_at
            FROM {schema}.balance_at
            ORDER BY journal_id, account_id, accrued_at
        """,
            log_extra={},
        )

    handler = balance.BalanceRuleHandler(
        name='balance_at', rule_name='billing_accounts_balance',
    )
    await handler.delete_old_chunks(
        app=accounts_cron_app,
        vid=0,
        threshold=dt.datetime(2019, 1, 1),
        log_extra={},
    )
    chunks = await get_chunks()
    entries = await get_entries()
    assert len(chunks) == 1
    assert entries  # TODO add more detailed checks


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_get_rule_handler(accounts_cron_app):
    handler = _api.get_rule_handler('balance_at')
    assert isinstance(handler, balance.BalanceRuleHandler)


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_settings_default(accounts_cron_app):
    settings = config_helper.get_replication_settings(
        accounts_cron_app.config, 'billing_accounts_balance_at',
    )
    assert not settings.replication_enable
    assert not settings.cleanup_enable


@pytest.mark.config(
    BILLING_ACCOUNTS_REPLICATION_SETTINGS={
        '__default__': {
            'READ_CHUNK_SIZE': 1000,
            'WRITE_CHUNK_SIZE': 1000,
            'SLEEP_TIME': 1.0,
            'MAX_REPLICATION_TIME': 15 * 60,
            'RECHECK_INTERVAL': 30 * 60,
            'TTL': 1 * 365 * 24 * 60 * 60,
        },
        'billing_accounts_balance_at': {
            'READ_CHUNK_SIZE': 12,
            'WRITE_CHUNK_SIZE': 34,
            'SLEEP_TIME': 5.0,
            'MAX_REPLICATION_TIME': 678,
            'RECHECK_INTERVAL': 9990999,
            'TTL': 10101010,
        },
    },
    BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=True,
    BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=True,
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_settings_customized(accounts_cron_app):
    settings = config_helper.get_replication_settings(
        accounts_cron_app.config, 'billing_accounts_balance_at',
    )
    assert settings.read_chunk_size == 12
    assert settings.write_chunk_size == 34
    assert settings.sleep_time == 5.0
    assert settings.max_replication_time == 678
    assert settings.recheck_interval == 9990999
    assert settings.replication_enable
    assert settings.cleanup_enable


@pytest.mark.config(
    BILLING_ACCOUNTS_REPLICATION_SETTINGS={
        '__default__': {
            'READ_CHUNK_SIZE': 1000,
            'WRITE_CHUNK_SIZE': 1000,
            'SLEEP_TIME': 1.0,
            'MAX_REPLICATION_TIME': 15 * 60,
            'RECHECK_INTERVAL': 30 * 60,
            'TTL': 1 * 365 * 24 * 60 * 60,
        },
        'billing_accounts_balance_at': {
            'READ_CHUNK_SIZE': 1,
            'WRITE_CHUNK_SIZE': 1,
            'SLEEP_TIME': 0.0,
            'MAX_REPLICATION_TIME': 9999,
            'RECHECK_INTERVAL': 999999,
            'TTL': 1 * 365 * 24 * 60 * 60,
        },
    },
    BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=True,
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_put_data_on_replicate(
        mock_put_data_into_queue, accounts_cron_app,
):
    mocked_put_data_into_queue = mock_put_data_into_queue()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0
    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert mocked_put_data_into_queue.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=False)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_no_put_data_when_no_replicate(
        mock_put_data_into_queue, accounts_cron_app,
):
    mocked_put_data_into_queue = mock_put_data_into_queue()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert not mocked_put_data_into_queue.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=False)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_replicate_disabled(
        mock_iter_chunks_to_replicate, accounts_cron_app,
):
    mocked_iter_chunks_to_replicate = mock_iter_chunks_to_replicate()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert not mocked_iter_chunks_to_replicate.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=True)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_replicate_enabled(
        mock_iter_chunks_to_replicate, accounts_cron_app,
):
    mocked_iter_chunks_to_replicate = mock_iter_chunks_to_replicate()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert mocked_iter_chunks_to_replicate.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=False)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_reconcile_disabled(
        mock_iter_chunks_to_reconcile, accounts_cron_app,
):
    mocked_iter_chunks_to_reconcile = mock_iter_chunks_to_reconcile()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert not mocked_iter_chunks_to_reconcile.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=True)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_reconcile_enabled(
        mock_iter_chunks_to_reconcile, accounts_cron_app,
):
    mocked_iter_chunks_to_reconcile = mock_iter_chunks_to_reconcile()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert mocked_iter_chunks_to_reconcile.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=False)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_cleanup_store_disabled(
        mock_delete_replicated_entries_from_store,
        mock_delete_old_chunks_from_store,
        accounts_cron_app,
):
    mocked_delete_replicated_entries_from_store = (
        mock_delete_replicated_entries_from_store()
    )
    mocked_delete_old_chunks_from_store = mock_delete_old_chunks_from_store()

    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0
    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert not mocked_delete_replicated_entries_from_store.calls
    assert not mocked_delete_old_chunks_from_store.calls


@pytest.mark.config(
    BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=True,
    BILLING_OLD_JOURNAL_LIMIT_DAYS=100,
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_cleanup_store_enabled(
        mock_delete_replicated_entries_from_store,
        mock_delete_old_chunks_from_store,
        accounts_cron_app,
):
    mocked_delete_replicated_entries_from_store = (
        mock_delete_replicated_entries_from_store()
    )
    mocked_delete_old_chunks_from_store = mock_delete_old_chunks_from_store()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert mocked_delete_replicated_entries_from_store.calls
    assert mocked_delete_old_chunks_from_store.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=False)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_cleanup_disabled(
        mock_delete_old_chunks, accounts_cron_app,
):
    mocked_delete_old_chunks = mock_delete_old_chunks()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert not mocked_delete_old_chunks.calls


@pytest.mark.config(BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=True)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_cleanup_enabled(
        mock_delete_old_chunks, accounts_cron_app,
):
    mocked_delete_old_chunks = mock_delete_old_chunks()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert mocked_delete_old_chunks.calls


@pytest.mark.config(
    BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=False,
    BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=False,
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_run_all_disabled(
        mock_iter_chunks_to_replicate,
        mock_iter_chunks_to_reconcile,
        mock_delete_old_chunks,
        accounts_cron_app,
):
    mocked_iter_chunks_to_replicate = mock_iter_chunks_to_replicate()
    mocked_iter_chunks_to_reconcile = mock_iter_chunks_to_reconcile()
    mocked_delete_old_chunks = mock_delete_old_chunks()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert not mocked_iter_chunks_to_replicate.calls
    assert not mocked_iter_chunks_to_reconcile.calls
    assert not mocked_delete_old_chunks.calls


@pytest.mark.config(
    BILLING_ACCOUNTS_BALANCE_REPLICATION_ENABLE=True,
    BILLING_ACCOUNTS_BALANCE_CLEANUP_ENABLE=True,
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'balance_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_replication_runner_run_all_enabled(
        mock_iter_chunks_to_replicate,
        mock_iter_chunks_to_reconcile,
        mock_delete_old_chunks,
        accounts_cron_app,
):
    mocked_iter_chunks_to_replicate = mock_iter_chunks_to_replicate()
    mocked_iter_chunks_to_reconcile = mock_iter_chunks_to_reconcile()
    mocked_delete_old_chunks = mock_delete_old_chunks()
    rule = 'balance_at'
    handler = _api.get_rule_handler(rule=rule)
    shard_id = 0

    await runner.run(
        app=accounts_cron_app,
        handler=handler,
        shard_id=shard_id,
        log_extra={},
    )
    assert mocked_iter_chunks_to_replicate.calls
    assert mocked_iter_chunks_to_reconcile.calls
    assert mocked_delete_old_chunks.calls
