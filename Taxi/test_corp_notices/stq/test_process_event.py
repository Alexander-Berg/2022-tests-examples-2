# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
import asyncio
import dataclasses

import pytest

from taxi.stq import async_worker_ng as async_worker

from corp_notices.events import db as events_db
from corp_notices.stq import process_event


@pytest.fixture
def do_process_mock(patch):
    @patch('corp_notices.events.base.EventBroker.do_process')
    async def _do_process(*args, **kwargs):
        pass

    return _do_process


@pytest.fixture
def event_mock():
    from corp_notices.events import base
    from corp_notices.events import models
    from corp_notices.events import registry

    @dataclasses.dataclass
    class TestEventData(models.EventData):
        field: int

    class TestBroker(base.EventBroker):
        event_name = 'TestEvent'
        event_data_cls = TestEventData

        async def do_process(self, event_data: models.EventData) -> None:
            await super().do_process(event_data)

    registry.add(TestBroker)


@pytest.mark.parametrize(
    'event_name, event_data, has_calls',
    [
        pytest.param('UnknownEvent', {}, False, id='unknown event'),
        pytest.param('TestEvent', {'field': 1}, True, id='TestEvent true'),
        pytest.param('TestEvent', {'unknown': 1}, False, id='TestEvent false'),
    ],
)
async def test_process_event(
        stq3_context,
        do_process_mock,
        event_mock,
        event_name,
        event_data,
        has_calls,
):
    task_info = async_worker.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='corp_notices_process_event',
    )

    await process_event.task(
        stq3_context,
        task_info=task_info,
        event_name=event_name,
        data=event_data,
    )
    assert bool(do_process_mock.calls) == has_calls


async def test_process_event_idempotency(
        stq3_context, do_process_mock, event_mock,
):
    client_id = 'client_id_1'
    idempotency_token = 'task_id_1'

    event_name = 'TestEvent'
    event_data = {'field': 1, 'client_id': client_id}

    task_info = async_worker.TaskInfo(
        id=idempotency_token,
        exec_tries=0,
        reschedule_counter=0,
        queue='corp_notices_process_event',
    )

    await asyncio.gather(
        process_event.task(
            stq3_context,
            task_info=task_info,
            event_name=event_name,
            data=event_data,
        ),
        process_event.task(
            stq3_context,
            task_info=task_info,
            event_name=event_name,
            data=event_data,
        ),
    )

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )

    assert len(do_process_mock.calls) == 1
    assert len(events) == 1
    assert events[0].idempotency_token == idempotency_token
