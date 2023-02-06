"""
    Describes candidates model.

    Storage and API over simulation candidates.
"""
import copy
import random
from typing import Dict
from typing import List
from typing import Set

from simulator.core import config
from simulator.core import stats
from simulator.core import structures
from simulator.core.utils import helpers


class CandidatesModel:
    # all candidates. id -> candidate
    _CANDIDATES: Dict[str, structures.DispatchCandidate] = {}

    # free candidates. ids
    _FREE_CANDIDATE_IDS: Set[str] = set()

    @classmethod
    def add(cls, candidate: structures.DispatchCandidate):
        assert candidate.id not in cls._CANDIDATES

        cls._CANDIDATES[candidate.id] = candidate

        if candidate.info.status == 'online':
            cls._FREE_CANDIDATE_IDS.add(candidate.id)

    @classmethod
    def remove(cls, candidate_id: str):
        cls._CANDIDATES.pop(candidate_id, None)
        cls._FREE_CANDIDATE_IDS.discard(candidate_id)

    @classmethod
    def is_free(cls, candidate_id: str):
        return candidate_id in cls._FREE_CANDIDATE_IDS

    @classmethod
    def set_busy(cls, candidate_id: str, waybill: structures.DispatchWaybill):
        assert candidate_id in cls._CANDIDATES

        if candidate_id in cls._FREE_CANDIDATE_IDS:
            cls._FREE_CANDIDATE_IDS.remove(candidate_id)
            cls.get(candidate_id).set_busy(waybill=waybill.info)
            return True

        return False

    @classmethod
    def set_free(cls, candidate_id: str):
        candidate = cls.get(candidate_id)
        candidate.waybill = None
        candidate.destination = None
        candidate.info.delete_chain_info()

        candidate.set_free()
        cls._FREE_CANDIDATE_IDS.add(candidate_id)

    @classmethod
    def is_order_accepted(cls, *_) -> bool:
        return random.random() <= config.settings.candidates.acceptance_rate

    @classmethod
    def list_free_candidates(cls) -> List[structures.DispatchCandidate]:
        candidates = []
        candidate_id: str

        for candidate_id in helpers.sample(
                cls._FREE_CANDIDATE_IDS,
                config.settings.candidates.max_in_response,
        ):
            # TODO: maybe remove deepcopy because it is so slow
            candidates.append(copy.deepcopy(cls._CANDIDATES[candidate_id]))

        return candidates

    @classmethod
    def get(cls, candidate_id: str) -> structures.DispatchCandidate:
        return cls._CANDIDATES[candidate_id]

    @classmethod
    def clear(cls):
        cls._CANDIDATES.clear()
        cls._FREE_CANDIDATE_IDS.clear()

    @classmethod
    def gather_statistics(cls):
        agg = stats.CandidateStatsAggregation()
        for candidate in cls._CANDIDATES.values():
            agg.aggregate(candidate)

        return agg.gather()
