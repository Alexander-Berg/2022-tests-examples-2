"""
    Populates segments within interval [start, end].
"""
import datetime
from typing import Callable
from typing import List
from typing import Optional

from simulator.core import events
from simulator.core import queue
from simulator.core import structures
from simulator.core.utils import randomize_times


def by_interval(
        start,
        end,
        *,
        segments: List[structures.DispatchSegment],
        lookup_duration: Optional[datetime.timedelta] = None,
        cancel_delta: Optional[Callable] = None,
):
    for segment in segments:
        created_ts = randomize_times.by_interval(start, end)

        segment.info.created_ts = created_ts

        queue.EventQueue.put(
            created_ts, events.segments.new_segment(segment=segment),
        )

        if lookup_duration is not None:
            queue.EventQueue.put(
                created_ts + lookup_duration,
                events.segments.performer_not_found(segment_id=segment.id),
            )

        if cancel_delta is not None:
            queue.EventQueue.put(
                created_ts + cancel_delta(),
                events.segments.cancel_segment_long_search(
                    segment_id=segment.id,
                ),
            )
