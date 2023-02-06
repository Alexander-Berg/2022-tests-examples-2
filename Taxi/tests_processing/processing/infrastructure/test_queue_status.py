import pytest


@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.experiments3(filename='use_ydb.json')
async def test_queue_status(processing, ydb, stq, testpoint):
    @testpoint('ProcessingNgQueue::DoProcessingIteration::QueueStatus')
    def queue_status_tp(data):
        pass

    queue = processing.testsuite.foo
    item_id = '56789'
    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'create'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    assert queue_status_tp.times_called == 1
    await queue.call(item_id)
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    assert queue_state == 'kHandledInYDB'
