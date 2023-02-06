"""
    Populates circle with N online candidates.
"""

from typing import List

from simulator.core import events
from simulator.core import queue
from simulator.core import structures


def allways_online(*, start, candidates: List[structures.DispatchCandidate]):
    for candidate in candidates:
        queue.EventQueue.put(
            start, events.candidates.online(candidate=candidate),
        )
