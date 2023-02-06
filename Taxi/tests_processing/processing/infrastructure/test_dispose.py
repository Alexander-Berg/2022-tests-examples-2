import datetime

import pytest


@pytest.mark.config(PROCESSING_MAINTAIN_IS_ARCHIVABLE=False)
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize(
    'margin',
    [
        pytest.param(
            0, marks=[pytest.mark.config(PROCESSING_REPLICATION_MARGIN=0)],
        ),
        pytest.param(
            3600,
            marks=[pytest.mark.config(PROCESSING_REPLICATION_MARGIN=3600)],
        ),
    ],
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_empty_events_data.yaml'],
)
async def test_dispose_happy_path(
        processing, stq, testpoint, pgsql, mocked_time, margin, yt_apply,
):
    queue = processing.testsuite.foo
    item_id = '123'

    mocked_time.set(
        mocked_time.now()
        + datetime.timedelta(minutes=1)
        + datetime.timedelta(seconds=margin),
    )

    @testpoint('ProcessingNgQueue::DoProcessingIteration::LastReplicated')
    def processing_iteration_tp(data):
        # some point in future to guarantee it will be 'replicated'
        return {'last_replicated': f'{mocked_time.now().isoformat()}Z'}

    @testpoint('ProcessingNgQueue::DoProcessingIteration::QueueStatus')
    def queue_status_tp(data):
        pass

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'create'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    # call once more to dispose after handling
    await queue.call(item_id)

    assert processing_iteration_tp.times_called == 2

    assert queue_status_tp.times_called == 2
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    assert queue_state == 'kDisposable'

    events = await queue.events(item_id)
    assert not events['events']

    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    assert not list(cursor)


@pytest.mark.config(PROCESSING_MAINTAIN_IS_ARCHIVABLE=False)
@pytest.mark.config(PROCESSING_REPLICATION_MARGIN=5)
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_empty_events_data.yaml'],
)
async def test_laggy_replication(processing, stq, testpoint, mocked_time):
    queue = processing.testsuite.foo
    item_id = '123'

    mocked_time.set(mocked_time.now() - datetime.timedelta(minutes=4))

    @testpoint('ProcessingNgQueue::DoProcessingIteration::LastReplicated')
    def processing_iteration_tp_past(data):
        return {'last_replicated': f'{mocked_time.now().isoformat()}Z'}

    @testpoint('ProcessingNgQueue::DoProcessingIteration::QueueStatus')
    def queue_status_tp(data):
        pass

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'create'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    await queue.call(item_id)

    # won't be replicated
    assert queue_status_tp.times_called == 2
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    assert queue_state == 'kNotReplicated'
    assert processing_iteration_tp_past.times_called == 2
    events = await queue.events(item_id)
    assert events['events']

    # will be replicated
    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=6))

    @testpoint('ProcessingNgQueue::DoProcessingIteration::LastReplicated')
    def processing_iteration_tp_future(data):
        return {'last_replicated': f'{mocked_time.now().isoformat()}Z'}

    with stq.flushing():
        await queue.call(item_id)
    assert processing_iteration_tp_future.times_called == 1
    assert queue_status_tp.times_called == 1
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    assert queue_state == 'kDisposable'
    events = await queue.events(item_id)
    assert not events['events']
