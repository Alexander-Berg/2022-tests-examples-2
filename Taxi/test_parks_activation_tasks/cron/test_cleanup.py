import pytest

# pylint: disable=redefined-outer-name
from parks_activation_tasks.generated.cron import run_cron


@pytest.fixture(autouse=True)
def mock_replication(mockserver):
    url = '/replication/state/min_ts/parks_activation_change_history'
    mocked_result = {
        'replicate_by': {},
        'queue_timestamp': '2010-01-01T12:00:00Z',
        'targets_timestamp': '2010-01-01T12:00:00Z',
    }

    @mockserver.handler(url)
    def _patched(request):
        return mockserver.make_response(json=mocked_result)


@pytest.mark.config(
    PARKS_ACTIVATION_HISTORY_CLEANUP_CONFIGS={
        'enabled': True,
        'history_ttl_days': 14,
        'chunk_size': 1,
        'chunk_interval_ms': 0,
    },
)
@pytest.mark.now('2010-02-01T12:00:01')
@pytest.mark.pgsql('parks_activation', files=('changes_history.sql',))
async def test_cleanup(pgsql):
    await run_cron.main(
        ['parks_activation_tasks.crontasks.cleanup', '-t', '0'],
    )
    cursor = pgsql['parks_activation'].cursor()
    cursor.execute('SELECT COUNT(*) FROM parks_activation.change_history')
    count = list(row[0] for row in cursor)
    assert count == [1]

    cursor.execute('SELECT id FROM parks_activation.change_history')
    ids = list(row[0] for row in cursor)
    assert len(ids) == 1
    assert ids == [3]
