import pytest


@pytest.mark.config(PROCESSING_MAINTAIN_IS_ARCHIVABLE=False)
@pytest.mark.config(
    PROCESSING_ENABLE_CHECKPOINTS={'default': False, 'overrides': []},
)
@pytest.mark.processing_queue_config(
    'simple-example.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_ensure_checkpoint_wont_leak(
        processing, testpoint, ydb, stq, use_ydb, use_fast_flow,
):
    item_id = 'foo'
    queue = processing.testsuite.example

    # first try will fail and create a checkpoint
    @testpoint('flaky-testpoint')
    def _flaky_testpoint(data):
        return {'simulated-error': 'simulate fail on first run'}

    event_id = await queue.send_event(
        item_id, {'kind': 'create'}, expect_fail=True,
    )
    assert _checkpoint_exists(
        ydb, 'testsuite', 'example', item_id, event_id, use_ydb,
    )

    # second try will succeed and should cleanup checkpoint
    @testpoint('flaky-testpoint')
    def _reliable_testpoint(data):
        return {}

    with stq.flushing():
        await queue.call(item_id, expect_fail=False)
    assert not _checkpoint_exists(
        ydb, 'testsuite', 'example', item_id, event_id, use_ydb,
    )


def _checkpoint_exists(ydb, scope, queue, item_id, event_id, use_ydb):
    cursor = ydb.execute(
        """
    SELECT COUNT(*) AS cnt FROM processing_state
        WHERE scope='{}' AND queue='{}' AND
        item_id='{}' AND event_id='{}'
    """.format(
            scope, queue, item_id, event_id,
        ),
    )
    row_count = cursor[0].rows[0]['cnt']
    return row_count != 0
