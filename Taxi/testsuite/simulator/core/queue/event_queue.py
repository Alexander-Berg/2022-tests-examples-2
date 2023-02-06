"""
    Storage for events queue.
    Simple priority queue with timestamp as a key.
"""

import dataclasses
import datetime
import functools
import heapq
import itertools
import logging
from typing import Any
from typing import List


LOG = logging.getLogger(__name__)


class BaseError(Exception):
    """
    Base error
    """


class EventQueueEmptyError(BaseError):
    """
    Trying to pop value from empty queue
    """


@dataclasses.dataclass(order=True)
class Event:
    timestamp: datetime.datetime
    seq_no: int = dataclasses.field(
        default_factory=itertools.count().__next__, init=False,
    )

    handler: functools.partial = dataclasses.field(compare=False)

    def launch(self) -> Any:
        # pylint: disable=not-callable
        return self.handler(timestamp=self.timestamp, seq_no=self.seq_no)


class EventQueue:
    _EVENTS: List[Event] = []

    @classmethod
    def put(
            cls, timestamp: datetime.datetime, handler: functools.partial,
    ) -> None:
        event = Event(timestamp=timestamp, handler=handler)

        # LOG.info('Register event %s', event)

        heapq.heappush(cls._EVENTS, event)

    @classmethod
    def pop(cls) -> Event:
        if not cls._EVENTS:
            raise EventQueueEmptyError()

        event = heapq.heappop(cls._EVENTS)

        # LOG.info('Processing event %s', event)

        return event

    @classmethod
    def is_empty(cls) -> bool:
        return len(cls._EVENTS) == 0

    @classmethod
    def clear(cls):
        cls._EVENTS.clear()


def event_handler(func):
    def wrapper(*args, **kwargs):
        return functools.partial(func, *args, **kwargs)

    return wrapper
