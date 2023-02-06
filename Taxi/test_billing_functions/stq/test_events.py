import datetime as dt

from billing.docs import service

from billing_functions.functions.core import types
from billing_functions.stq import events


async def test_scheduler(
        do_mock_billing_docs, stq3_context, patched_stq_queue,
):
    now = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)
    docs = do_mock_billing_docs()
    scheduler = events.Scheduler(
        stq3_context.docs,
        stq3_context.stq,
        now_provider=lambda: now,
        jitter_provider=lambda _: dt.timedelta(seconds=1),
        enabled=types.TRUE,
    )
    event = service.CreateDocRequest(
        kind='kind',
        topic='topic',
        external_ref='external_ref',
        event_at=now,
        process_at=now,
        data={},
        status='new',
        tags=[],
    )
    doc_id = await scheduler.schedule(
        'billing_functions_taxi_order', event=event, jitter_seed='seed',
    )
    assert doc_id.value == 5000
    assert docs.created_docs == [
        {
            'data': {},
            'event_at': '2021-01-01T00:00:00+00:00',
            'external_event_ref': 'external_ref',
            'external_obj_id': 'topic',
            'journal_entries': [],
            'kind': 'kind',
            'process_at': '2021-01-01T00:00:00+00:00',
            'service': 'billing-functions',
            'status': 'new',
            'tags': [],
        },
    ]
    assert patched_stq_queue.pop_calls() == [
        {
            'args': [5000],
            'eta': '2021-01-01T00:00:01.000000Z',
            'kwargs': {},
            'task_id': 'doc_id/5000',
        },
    ]
