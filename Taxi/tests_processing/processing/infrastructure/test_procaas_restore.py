import dataclasses
import datetime
import json

import pytest


@dataclasses.dataclass
class ProcessingEvent:
    scope: str
    queue: str
    item_id: str
    event_id: str
    order_key: int
    created: datetime.datetime
    payload: dict
    idempotency_token: str
    need_handle: bool
    updated: datetime.datetime
    is_archivable: bool
    due: datetime.datetime
    is_malformed: bool
    handling_order_key: int
    extra_order_key: int


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_empty_events_data.yaml'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.config(PROCESSING_REPLICATION_MARGIN=0)
@pytest.mark.parametrize('replicated', [True, False])
async def test_procaas_restore_empty_yt(
        processing, yt_apply, pgsql, mocked_time, testpoint, replicated,
):
    event_id = await processing.testsuite.foo.send_event(
        item_id='0123456789', payload={'kind': 'foo'},
    )
    from_pg = await _fetch_events_from_pg(pgsql)
    assert len(from_pg) == 1
    assert from_pg[0].is_malformed
    assert from_pg[0].event_id == event_id

    # second call to processing (disposing malformed events)
    if replicated:
        mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))

    @testpoint('ProcessingNgQueue::DoProcessingIteration::LastReplicated')
    def _processing_iteration_tp(data):
        return {'last_replicated': f'{mocked_time.now().isoformat()}Z'}

    await processing.testsuite.foo.call(item_id='0123456789')
    from_pg = await _fetch_events_from_pg(pgsql)
    assert len(from_pg) == (0 if replicated else 1)


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_malformed_data.yaml'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize(
    'payload,idempotency_token,expected_events',
    [
        ({'kind': 'foo'}, 'idempotency_token_42', 2),
        ({'kind': 'seen'}, 'idempotency_token_1', 1),
    ],
)
@pytest.mark.parametrize('replicated', [True, False])
@pytest.mark.config(PROCESSING_REPLICATION_MARGIN=0)
async def test_procaas_restore_malformed(
        processing,
        yt_apply,
        pgsql,
        testpoint,
        mocked_time,
        payload,
        idempotency_token,
        expected_events,
        replicated,
):
    await processing.testsuite.foo.send_event(
        item_id='0123456789',
        payload=payload,
        idempotency_token=idempotency_token,
    )
    from_pg = await _fetch_events_from_pg(pgsql)
    assert len(from_pg) == expected_events
    assert all([i.is_malformed for i in from_pg])

    # second call to processing (disposing malformed events)
    if replicated:
        mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))

    @testpoint('ProcessingNgQueue::DoProcessingIteration::LastReplicated')
    def _processing_iteration_tp(data):
        return {'last_replicated': f'{mocked_time.now().isoformat()}Z'}

    await processing.testsuite.foo.call(item_id='0123456789')
    from_pg = await _fetch_events_from_pg(pgsql)
    assert len(from_pg) == (0 if replicated else expected_events)


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_handling_order.yaml'],
)
@pytest.mark.parametrize(
    'order_id,send_events,expected_handling_order',
    [
        (
            '0000_order_id',
            ['idempotency_token_1'],
            [('idempotency_token_0', -1), ('idempotency_token_1', 0)],
        ),
        (
            '0000_order_id',
            ['idempotency_token_1', 'idempotency_token_2'],
            [
                ('idempotency_token_0', -1),
                ('idempotency_token_1', 0),
                ('idempotency_token_2', 1),
            ],
        ),
        (
            # idempotency_token_0 don't have handling_order_key
            # so will be executed accoring order_key
            '0001_order_id',
            ['idempotency_token_1'],
            [('idempotency_token_0', -1), ('idempotency_token_1', 0)],
        ),
        (
            # events in YT don't have handling_order_key (old ones)
            '0002_order_id',
            ['idempotency_token_2', 'idempotency_token_3'],
            [
                ('idempotency_token_0', -2),
                ('idempotency_token_1', -1),
                ('idempotency_token_2', 0),
                ('idempotency_token_3', 1),
            ],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procass_restore_handling_order(
        processing,
        yt_apply,
        pgsql,
        order_id,
        send_events,
        expected_handling_order,
):
    for new_idempotency_token in send_events:
        await processing.testsuite.foo.send_event(
            item_id=order_id,
            payload={'kind': 'foo'},
            idempotency_token=new_idempotency_token,
        )
    result = await _fetch_events_from_pg(pgsql)
    sequence = sorted(
        [(i.idempotency_token, i.handling_order_key) for i in result],
        key=lambda i: i[1],
    )
    assert sequence == expected_handling_order


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'], dyn_table_data=['yt_events_data.yaml'],
)
@pytest.mark.parametrize('already_replicated', [False, True])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore(
        processing, yt_apply, pgsql, load_yaml, yt_client, already_replicated,
):
    # this simulates replication from PG to YT
    async def _extra_row_insert(event_id):
        yt_client.insert_rows(
            '//home/testsuite/processing_events',
            await _fetch_events_from_pg_for_yt(pgsql),
        )

    extra_action = _extra_row_insert if already_replicated else None

    # create re-open event
    assert (await _fetch_events_from_pg(pgsql)) == []
    await processing.testsuite.foo.send_event(
        item_id='0123456789',
        payload={'kind': 'reopen'},
        idempotency_token='idempotency_token_3',
        extra_action=extra_action,
    )

    # check postconditions
    samples = load_yaml('yt_events_data.yaml')[0]['values']
    expected_events = [
        ProcessingEvent(
            scope=i['scope'],
            queue=i['queue'],
            item_id=i['item_id'],
            event_id=i['event_id'],
            order_key=i['order_key'] - len(samples),
            created=datetime.datetime.fromtimestamp(
                i['created'], datetime.timezone.utc,
            ),
            payload=json.loads(i['payload']),
            idempotency_token=i['idempotency_token'],
            need_handle=i['need_handle'],
            updated=datetime.datetime.fromtimestamp(
                i['updated'], datetime.timezone.utc,
            ),
            is_archivable=True,
            due=datetime.datetime.fromtimestamp(
                i['due'], datetime.timezone.utc,
            ),
            is_malformed=False,  # not yet replicated to YT
            handling_order_key=i['handling_order_key'] - len(samples) + 1
            if i['handling_order_key'] is not None
            else i['order_key'] - len(samples),
            extra_order_key=i['extra_order_key'],
        )
        for i in samples
    ]
    from_pg = await _fetch_events_from_pg(pgsql)
    assert len(from_pg) == 4
    assert len(from_pg) == len(expected_events) + 1
    for i, _ in enumerate(from_pg[:-1]):
        # NOTE 'updated' replaced by NOW() when restored
        assert from_pg[i].updated > expected_events[i].updated
        from_pg[i].updated = expected_events[i].updated
    assert from_pg[:-1] == expected_events

    reopen = from_pg[-1]
    assert reopen.scope == 'testsuite'
    assert reopen.queue == 'foo'
    assert reopen.item_id == '0123456789'
    assert reopen.order_key == 0


async def _fetch_events_from_pg(pgsql):
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT scope, queue, item_id, event_id, order_key, created, payload, '
        'idempotency_token, need_handle, updated, is_archivable, '
        'due, is_malformed, handling_order_key, extra_order_key '
        'FROM processing.events ORDER BY order_key',
    )
    return [ProcessingEvent(*i) for i in cursor]


async def _fetch_events_from_pg_for_yt(pgsql):
    events = await _fetch_events_from_pg(pgsql)
    return [
        {
            'scope': i.scope,
            'queue': i.queue,
            'item_id': i.item_id,
            'event_id': i.event_id,
            'order_key': i.order_key,
            'created': i.created.timestamp(),
            'payload': json.dumps(i.payload),
            'idempotency_token': i.idempotency_token,
            'need_handle': i.need_handle,
            'updated': i.updated.timestamp(),
            'due': i.due.timestamp(),
            'handling_order_key': i.handling_order_key,
            'extra_order_key': i.extra_order_key,
        }
        for i in events
    ]
