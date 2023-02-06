import pytest

# pylint: disable=import-only-modules
from metadata_storage_tasks.crontasks.cleanup import TooOldYTReplicationError
# pylint: disable=redefined-outer-name
from metadata_storage_tasks.generated.cron import run_cron


@pytest.fixture(autouse=True)
def mock_replication(mockserver):
    url = '/replication/state/min_ts/metadata_storage'
    mocked_result = {
        'replicate_by': {},
        'queue_timestamp': '2010-01-01T12:00:00Z',
        'targets_timestamp': '2010-01-01T12:00:00Z',
    }

    @mockserver.handler(url)
    def _patched(request):
        return mockserver.make_response(json=mocked_result)


@pytest.mark.now('2010-02-01T12:00:00')
@pytest.mark.config(
    METADATA_STORAGE_DB_CLEANUP={
        'chunk_size': 10,
        'doc_ttl_hours': 1,
        'chunk_interval_sec': 1,
    },
)
async def test_cleanup_too_old(mockserver):
    with pytest.raises(TooOldYTReplicationError):
        await run_cron.main(
            ['metadata_storage_tasks.crontasks.cleanup', '-t', '0'],
        )


@pytest.mark.now('2010-01-01T12:00:00')
@pytest.mark.config(
    METADATA_STORAGE_DB_CLEANUP={
        'chunk_size': 2,
        'doc_ttl_hours': 2,
        'chunk_interval_sec': 1,
    },
)
@pytest.mark.mongodb_collections('metadata_storage')
async def test_cleanup(db, mockserver):
    await run_cron.main(
        ['metadata_storage_tasks.crontasks.cleanup', '-t', '0'],
    )

    new_db_count = await db.metadata_storage.count()
    assert new_db_count == 1
