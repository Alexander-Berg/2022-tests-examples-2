"""
    Populates circle with N online candidates.
"""

from typing import List

from simulator.core import structures
from simulator.core.utils import randomize_coordinates
from tests_united_dispatch.plugins import candidates_manager


def make_candidates(
        *,
        candidates_count: int,
        center: structures.Point,
        radius: int,
        **candidate_kwargs,
) -> List[structures.DispatchCandidate]:
    candidates = []
    for _ in range(candidates_count):
        candidate_info = candidates_manager.make_candidate(
            position=randomize_coordinates.by_center(
                center=center, radius=radius,
            ).to_list(),
            **candidate_kwargs,
        )
        candidate = structures.DispatchCandidate(info=candidate_info)
        candidates.append(candidate)
    return candidates
