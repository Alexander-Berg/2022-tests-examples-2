import datetime as dt

import pytest

from taxi_billing_docs.common import db


_NOW = dt.datetime(2020, 1, 10, 8, 0, 0)


@pytest.mark.pgsql(
    'billing_docs@0',
    files=('meta.sql', 'doc@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid,expected_lag',
    [
        pytest.param(
            0,
            10,
            id=(
                'vshard with doc replication chunks, use '
                'last replicated doc event to compute lag'
            ),
        ),
        pytest.param(
            1,
            100,
            id=(
                'vshard without doc replication chunks, use '
                'earliest doc event to compute lag'
            ),
        ),
    ],
)
async def test_replication_lag_success(docs_monrun_app, vid, expected_lag):
    store = db.DocReplicationChunksStore(
        storage=docs_monrun_app.storage, config=docs_monrun_app.config,
    )
    lag = await store.get_replication_lag(now=_NOW, vid=vid, log_extra=None)
    assert lag == expected_lag


@pytest.mark.pgsql(
    'billing_docs@0',
    files=('meta.sql', 'doc@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid',
    [
        pytest.param(
            0, id='last replicated doc event is fresher than now, use 0 lag',
        ),
    ],
)
async def test_negative_replication_lag(docs_monrun_app, vid):
    store = db.DocReplicationChunksStore(
        storage=docs_monrun_app.storage, config=docs_monrun_app.config,
    )
    lag = await store.get_replication_lag(
        now=_NOW - dt.timedelta(seconds=100), vid=vid, log_extra=None,
    )
    assert lag == 0


@pytest.mark.pgsql(
    'billing_docs@0',
    files=('meta.sql', 'doc@0.sql', 'doc_replication_chunks@0.sql'),
)
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.parametrize(
    'vid',
    [
        pytest.param(2, id='vshard where last replicated doc event is absent'),
        pytest.param(3, id='vshard without doc events or chunks at all'),
    ],
)
async def test_replication_lag_fail(docs_monrun_app, vid):
    store = db.DocReplicationChunksStore(
        storage=docs_monrun_app.storage, config=docs_monrun_app.config,
    )
    with pytest.raises(AssertionError):
        await store.get_replication_lag(now=_NOW, vid=vid, log_extra=None)
