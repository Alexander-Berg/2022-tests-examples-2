import datetime as dt
import typing as tp

import pytest

from taxi.billing import pgstorage

from taxi_billing_accounts import db
from taxi_billing_accounts.replication import config_helper


NOW = dt.datetime(2019, 1, 30, 0, 0, 0, 0)


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_app(accounts_cron_app):
    assert accounts_cron_app is not None
    assert accounts_cron_app.storage is not None
    store = db.JournalReplicationChunksStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    assert store is not None


@pytest.mark.parametrize(
    'vid,expected_id', [(0, 22220090000), (4, 22220080004)],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'journal_replication_chunks@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'journal_replication_chunks@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_last_chunk(accounts_cron_app, vid, expected_id):
    store = db.JournalReplicationChunksStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    last_chunk = await store.get_last_chunk(vid=vid, log_extra={})
    assert last_chunk.last_journal_id == expected_id


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'journal_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'journal_replication_chunks@1.sql',
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_next_chunk(accounts_cron_app):
    store = db.JournalEntryStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    entries = await store.get_next_chunk(
        vid=0, start_id=22220050000, limit=3, log_extra={},
    )
    assert len(entries) == 3
    assert sorted([x.entry_id for x in entries]) == [
        22220060000,
        22220070000,
        22220080000,
    ]
    entries = await store.get_next_chunk(
        vid=4, start_id=22220050000, limit=4, log_extra={},
    )
    assert len(entries) == 4
    assert sorted([x.entry_id for x in entries]) == [
        22220050004,
        22220060004,
        22220070004,
        22220080004,
    ]


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'journal_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'journal_replication_chunks@1.sql',
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_chunk_entries(accounts_cron_app):
    store = db.JournalEntryStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    entries = await store.get_chunk_entries(  # request for non-existent chunk
        vid=0, chunk_id=22220000000, log_extra={},
    )
    assert not entries
    entries = await store.get_chunk_entries(
        vid=0, chunk_id=22220020000, log_extra={},
    )  # first chunk
    assert len(entries) == 2
    assert sorted([x.entry_id for x in entries]) == [22220010000, 22220020000]
    entries = await store.get_chunk_entries(
        vid=4, chunk_id=22220050004, log_extra={},
    )  # 2nd chunk on 2th shard
    assert len(entries) == 3
    assert sorted([x.entry_id for x in entries]) == [
        22220030004,
        22220040004,
        22220050004,
    ]


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'journal_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'journal_replication_chunks@1.sql',
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_incomplete_chunks(accounts_cron_app):
    store = db.JournalReplicationChunksStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    chunks = await store.get_incomplete_chunks(  # last chunk is incomplete
        vid=0, since=dt.datetime(2018, 12, 31, 21, 0, 0), log_extra={},
    )
    assert len(chunks) == 1
    assert chunks[0].last_journal_id == 22220090000
    chunks = await store.get_incomplete_chunks(  # year after last created!
        vid=0, since=dt.datetime(2019, 12, 31, 21, 0, 0), log_extra={},
    )
    assert not chunks
    chunks = await store.get_incomplete_chunks(  # no incomplete chunks
        vid=4, since=dt.datetime(2018, 12, 31, 21, 0, 0), log_extra={},
    )
    assert not chunks


@pytest.mark.parametrize(
    'vid,start_id,expected_ids',
    [
        (0, 22220000000, [22220020000]),
        (4, 22220000004, [22220020004, 22220050004, 22220080004]),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'rollups@0.sql',
        'journal_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'rollups@1.sql',
        'journal_replication_chunks@1.sql',
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_chunks_to_delete(
        accounts_cron_app, vid, start_id, expected_ids,
):
    store = db.JournalReplicationChunksStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    chunks = await store.get_chunks_to_delete(
        vid=vid, after_journal_id=start_id, limit=9, log_extra={},
    )
    assert sorted(x.chunk.last_journal_id for x in chunks) == expected_ids


@pytest.mark.parametrize(
    'vid,chunk_id,expected_alive_journal_ids,expected_alive_chunk_ids',
    [
        (
            0,
            22220050000,
            [
                22220010000,
                22220020000,
                # 3,4,5 will deleted, but 5 will not because of rollups
                22220050000,
                22220060000,
                22220070000,
                22220080000,
                22220090000,
            ],
            [22220020000, 22220050000, 22220090000],  # no chunks deleted
        ),
        (
            4,
            22220050004,
            [
                22220010004,
                22220020004,
                22220060004,
                22220070004,
                22220080004,
                22220090004,
            ],
            [22220020004, 22220080004],
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'rollups@0.sql',
        'journal_replication_chunks@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'rollups@1.sql',
        'journal_replication_chunks@1.sql',
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_delete_chunk(
        accounts_cron_app,
        vid,
        chunk_id,
        expected_alive_journal_ids,
        expected_alive_chunk_ids,
):
    async def fetch_journal_ids(vid: int) -> tp.List[int]:
        schema = accounts_cron_app.storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(
            accounts_cron_app.storage, vid,
        )
        rows = await executor.fetch(
            f"""
            SELECT id FROM {schema}.journal ORDER BY id
            """,
            log_extra={},
        )
        return [row['id'] for row in rows]

    async def fetch_chunk_ids(vid: int) -> tp.List[int]:
        schema = accounts_cron_app.storage.vshard_schema(vid)
        executor = await pgstorage.Executor.create(
            accounts_cron_app.storage, vid,
        )
        rows = await executor.fetch(
            f"""
                SELECT last_journal_id AS id
                  FROM {schema}.journal_replication_chunks
              ORDER BY last_journal_id
            """,
            log_extra={},
        )
        return [row['id'] for row in rows]

    store = db.JournalEntryStore(
        storage=accounts_cron_app.storage, config=accounts_cron_app.config,
    )
    await store.delete_chunk(chunk_id=chunk_id, log_extra={})
    alive_journal_ids = await fetch_journal_ids(vid=vid)
    alive_chunk_ids = await fetch_chunk_ids(vid=vid)
    assert alive_journal_ids == expected_alive_journal_ids
    assert alive_chunk_ids == expected_alive_chunk_ids


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_default_settings(accounts_cron_app):
    settings = config_helper.get_replication_settings(
        accounts_cron_app.config, 'billing_accounts_journal',
    )
    assert not settings.replication_enable
    assert not settings.cleanup_enable
