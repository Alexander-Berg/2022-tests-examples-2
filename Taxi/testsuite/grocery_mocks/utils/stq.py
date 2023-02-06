import asyncio
import datetime
from typing import List
from typing import Optional

from testsuite.utils import callinfo

from . import helpers


class CreatedStqEvents:
    def __init__(self, events: List[dict]):
        self._events = events
        self._events_iter = iter(events)

    def __len__(self):
        return len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __getitem__(self, task_id: str) -> dict:
        event = self.find(task_id)
        assert event is not None, f'event {task_id} not exists'
        return event

    def find(self, task_id: str) -> Optional[dict]:
        for event in self._events:
            if event['id'] == task_id:
                return event

        return None

    def next(self) -> dict:
        return next(self._events_iter)

    def check_event(
            self,
            task_id: Optional[str] = None,
            task_eta: Optional[datetime.datetime] = None,
            times_called: Optional[None] = None,
            reschedule: bool = False,
            **kwargs,
    ):
        if times_called is not None:
            assert len(self._events) == times_called
            if times_called == 0:
                return

        if task_id is not None:
            event = self[task_id]
        else:
            event = self.next()

        if task_eta is not None:
            eta: datetime.datetime = event['eta']
            eta_utc = eta.replace(tzinfo=datetime.timezone.utc)
            assert eta_utc == task_eta

        if reschedule:
            assert event.get('kwargs') is None
            return

        helpers.assert_dict_contains(event.get('kwargs', {}), kwargs)

    async def run(self, stq_runner):
        futures = []
        for event in self._events:
            stq = getattr(stq_runner, event['queue'])
            future = stq.call(
                task_id=event.get('id'),
                kwargs=event.get('kwargs'),
                eta=event.get('eta'),
            )

            futures.append(future)

        if futures:
            await asyncio.wait(futures)


def created_events(stq_queue: callinfo.AsyncCallQueue):
    count = stq_queue.times_called
    events = [stq_queue.next_call() for _ in range(count)]
    return CreatedStqEvents(events)


async def gather(stq_runner, *stq_queues: callinfo.AsyncCallQueue):
    results: List[List[dict]] = [[] for _ in stq_queues]

    while any(it.has_calls for it in stq_queues):
        for index, stq_queue in enumerate(stq_queues):
            events = created_events(stq_queue)
            results[index].extend(events)
            await events.run(stq_runner)

    return map(CreatedStqEvents, results)
