import datetime
import json

import pytest


@pytest.mark.config(PROCESSING_MAINTAIN_IS_ARCHIVABLE=False)
@pytest.mark.config(PROCESSING_REPLICATION_MARGIN=0)
@pytest.mark.experiments3(filename='enable_replication.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_empty_events_data.yaml'],
)
async def test_dispose_happy_path(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    queue = processing.testsuite.foo
    item_id = '123'

    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))

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

    assert processing_iteration_tp.times_called == 1

    assert queue_status_tp.times_called == 1
    await queue.call(item_id)
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    queue_state = queue_status_tp.next_call()['data']['queue_status']
    assert queue_state == 'kDisposable'

    events = await queue.events(item_id)
    assert not events['events']

    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    assert not list(cursor)

    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where event_id="{}"'.format(db_name, event_id),
    )
    assert len(cursor) == 1
    row = cursor[0].rows[0]
    assert row['item_id'].decode('utf-8') == item_id
    assert row['event_id'].decode('utf-8') == event_id
    json_payload = json.loads(row['payload_v2'])
    assert json_payload['kind'] == 'create'


@pytest.mark.config(PROCESSING_MAINTAIN_IS_ARCHIVABLE=False)
@pytest.mark.config(PROCESSING_REPLICATION_MARGIN=0)
@pytest.mark.config(PROCESSING_REPLICATION_WAITING_POLL_PERIOD=0)
@pytest.mark.experiments3(filename='enable_replication.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_empty_events_data.yaml'],
)
async def test_dispose_regular(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    queue = processing.testsuite.foo
    item_id = '123'

    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))

    @testpoint('ProcessingNgQueue::DoProcessingIteration::LastReplicated')
    def processing_iteration_tp(data):
        # some point in future to guarantee it will be 'replicated'
        return {'last_replicated': f'{mocked_time.now().isoformat()}Z'}

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'regular'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    # reschedule bes disposal
    assert processing_iteration_tp.times_called == 1
    await processing.testsuite.foo.call(item_id=item_id)

    events = await queue.events(item_id)
    assert not events['events']

    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    assert not list(cursor)

    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where event_id="{}"'.format(db_name, event_id),
    )
    assert len(cursor) == 1
    row = cursor[0].rows[0]
    assert row['item_id'].decode('utf-8') == item_id
    assert row['event_id'].decode('utf-8') == event_id
    json_payload = json.loads(row['payload_v2'])
    assert json_payload['kind'] == 'regular'
