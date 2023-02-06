"""
    Populates planner execution.
"""
from simulator.core import events
from simulator.core import queue


def populate(start, *, planner_type: str):
    queue.EventQueue.put(
        start,
        events.dispatch.run_planner(
            planner_type=planner_type, start_timestamp=start,
        ),
    )
