import datetime as dt

import pytest

from taxi_billing_docs.common import db
from taxi_billing_docs.common import models


NOW = dt.datetime(2019, 1, 30, 0, 0, 0, 0)


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=('doc@0.sql', 'event@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_last_chunk(docs_cron_app):
    store = db.DocReplicationChunksStore(
        storage=docs_cron_app.storage, config=docs_cron_app.config,
    )
    last_chunk = await store.get_last_chunk(vid=2, log_extra={})
    assert last_chunk.last_event_seq_id == 17


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=('doc@0.sql', 'event@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.parametrize(
    'start_event_seq_id, limit, '
    'expected_doc_ids, expected_max_event_seq_id, expected_events_count',
    [
        pytest.param(
            13,
            3,
            [70002, 80002, 90002],
            18,
            3,
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            9,
            3,
            [60002, 80002, 90002],
            17,
            3,
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            13,
            3,
            [80002, 90002, 100002],
            16,
            3,
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2000-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            9,
            3,
            [60002, 70002, 80002],
            12,
            3,
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2000-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            9,
            7,
            [60002, 70002, 80002, 90002, 100002],
            16,
            7,
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2000-01-01T00:00:00+00:00'
                ),
            ),
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_next_chunk(
        docs_cron_app,
        start_event_seq_id,
        limit,
        expected_doc_ids,
        expected_max_event_seq_id,
        expected_events_count,
):
    store = db.DocStore(
        storage=docs_cron_app.storage, config=docs_cron_app.config,
    )
    docs, max_event_seq_id, events_count = await store.get_next_chunk(
        vid=2,
        start_event_seq_id=start_event_seq_id,
        limit=limit,
        log_extra={},
    )
    assert sorted([doc.doc_id for doc in docs]) == expected_doc_ids
    assert max_event_seq_id == expected_max_event_seq_id
    assert events_count == expected_events_count


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=('doc@0.sql', 'event@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.parametrize(
    'chunk_id, expected_doc_ids',
    [
        pytest.param(
            8,
            [10002, 20002, 40002],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            13,
            [50002, 60002],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            13,
            [50002, 60002, 70002, 80002],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2000-01-01T00:00:00+00:00'
                ),
            ),
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_chunk_entries(docs_cron_app, chunk_id, expected_doc_ids):
    """
    First chunk; not first chunk
    Also see what happens if there's a second complete.
    """
    store = db.DocStore(
        storage=docs_cron_app.storage, config=docs_cron_app.config,
    )
    docs = await store.get_chunk_entries(
        vid=2, chunk_id=chunk_id, log_extra={},
    )
    assert sorted([doc.doc_id for doc in docs]) == expected_doc_ids


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=('doc@0.sql', 'event@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.parametrize(
    'since, expected_chunks',
    [
        pytest.param(
            dt.datetime(2018, 12, 31, 21, 0, 0),
            [
                models.DocReplicationChunk(
                    count=3,
                    created=dt.datetime(2019, 1, 30, 0, 0),
                    last_event_seq_id=8,
                    updated=dt.datetime(2019, 1, 30, 0, 0),
                ),
            ],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            dt.datetime(2018, 12, 31, 21, 0, 0),
            [
                models.DocReplicationChunk(
                    last_event_seq_id=8,
                    count=8,
                    created=dt.datetime(2019, 1, 30, 0, 0),
                    updated=dt.datetime(2019, 1, 30, 0, 0),
                ),
                models.DocReplicationChunk(
                    last_event_seq_id=13,
                    count=5,
                    created=dt.datetime(2019, 1, 30, 0, 0),
                    updated=dt.datetime(2019, 1, 30, 0, 0),
                ),
            ],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2000-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            dt.datetime(2019, 12, 31, 21, 0, 0),
            [],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_incomplete_chunks(docs_cron_app, since, expected_chunks):
    store = db.DocReplicationChunksStore(
        storage=docs_cron_app.storage, config=docs_cron_app.config,
    )
    chunks = await store.get_incomplete_chunks(
        vid=2, since=since, log_extra={},
    )
    sorted_chunks = sorted(chunks, key=lambda c: c.last_event_seq_id)
    assert sorted_chunks == expected_chunks


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=('doc@0.sql', 'event@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_get_chunks_to_delete(docs_cron_app):
    store = db.DocReplicationChunksStore(
        storage=docs_cron_app.storage, config=docs_cron_app.config,
    )
    chunks = await store.get_chunks_to_delete(
        vid=2,
        threshold=dt.datetime(2019, 12, 31, 21, 0, 0),
        offset=dt.datetime(2020, 1, 1, 21, 0, 0),
        log_extra={},
    )
    assert len(chunks) == 3
    assert chunks[0].last_event_seq_id == 8
    assert chunks[1].last_event_seq_id == 13
    assert chunks[2].last_event_seq_id == 17


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=('doc@0.sql', 'event@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.parametrize(
    'chunk_id,expected_alive_doc_ids,expected_alive_chunk_ids',
    [
        (
            8,
            [20002, 30002, 50002, 60002, 70002, 80002, 90002, 100002],
            [13, 17],
        ),
        (
            13,
            [10002, 20002, 30002, 40002, 70002, 80002, 90002, 100002],
            [8, 17],
        ),
        (
            17,
            [10002, 20002, 30002, 40002, 50002, 60002, 70002, 100002],
            [8, 13],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_delete_chunk(
        docs_cron_app,
        chunk_id,
        expected_alive_doc_ids,
        expected_alive_chunk_ids,
):
    async def fetch_doc_ids(vid):
        schema = docs_cron_app.storage.vshard_schema(vid)
        replica = await docs_cron_app.storage.replica(vid)
        rows = await replica.fetch(
            f"""
            SELECT id FROM {schema}.doc ORDER BY id
            """,
            log_extra={},
        )
        return [row['id'] for row in rows]

    async def fetch_chunk_ids(vid):
        schema = docs_cron_app.storage.vshard_schema(vid)
        replica = await docs_cron_app.storage.replica(vid)
        rows = await replica.fetch(
            f"""
                SELECT last_event_seq_id AS id
                  FROM {schema}.doc_replication_chunks
              ORDER BY last_event_seq_id
            """,
            log_extra={},
        )
        return [row['id'] for row in rows]

    store = db.DocStore(
        storage=docs_cron_app.storage, config=docs_cron_app.config,
    )
    await store.delete_chunk(vid=2, chunk_id=chunk_id, log_extra={})
    alive_doc_ids = await fetch_doc_ids(vid=2)
    alive_chunk_ids = await fetch_chunk_ids(vid=2)
    assert alive_doc_ids == expected_alive_doc_ids
    assert alive_chunk_ids == expected_alive_chunk_ids
