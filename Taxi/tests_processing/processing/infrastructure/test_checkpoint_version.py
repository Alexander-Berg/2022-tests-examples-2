import pytest


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
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
@pytest.mark.parametrize('change_cp,expected_calls', [(True, 2), (False, 1)])
async def test_checkpoint_version(
        processing, testpoint, ydb, stq, change_cp, expected_calls, use_ydb,
):
    item_id = 'foo'
    queue = processing.testsuite.example

    @testpoint('solid-testpoint')
    def solid_testpoint(data):
        return {}

    # first run will fail and create a checkpoint
    @testpoint('flaky-testpoint')
    def _flaky_testpoint(data):
        return {'simulated-error': 'simulate fail on first run'}

    event_id = await queue.send_event(
        item_id, {'kind': 'create'}, expect_fail=True,
    )
    checkpoint = await queue.checkpoint(item_id)
    assert checkpoint
    assert checkpoint['event_id'] == event_id
    assert checkpoint[
        'handle_by_version'
    ]  # the contents is unpredictable, so, just checking that it is non-empty

    # now simulate non-compatibility (when need)
    if change_cp:
        ydb.execute('UPDATE processing_state SET handle_by_version=\'nope\'')

    # second run will succeed but a checkpoint will be dropped (or not)
    @testpoint('flaky-testpoint')
    def _nonflaky_testpoint(data):
        return {}

    with stq.flushing():
        await queue.call(item_id, expect_fail=False)
    assert solid_testpoint.times_called == expected_calls
