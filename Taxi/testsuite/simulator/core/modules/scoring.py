"""
    Describes driver-scoring model.
"""
from typing import List
from typing import Tuple

from simulator.core import config
from simulator.core import docs
from simulator.core import structures
from tests_united_dispatch.plugins import candidates_manager


class ScoringModel:
    # bonuses and retention_score are not supported yet

    @classmethod
    def score_candidates(
            cls,
            candidates: List[
                Tuple[
                    structures.DispatchCandidate, candidates_manager.Candidate,
                ]
            ],
            request: docs.OrderSearchRequest,
    ) -> Tuple[List[float], float]:
        scores = []
        alpha = config.settings.scoring.alpha
        beta = config.settings.scoring.beta
        for performer, candidate in candidates:
            tag_score_coeff = cls.get_tags_score_coeff(performer.tags)
            score = tag_score_coeff * (
                (1 - alpha) * candidate.route_info.time
                + alpha * beta * candidate.route_info.distance
            )
            scores.append(score)
        return (scores, -1000)

    @classmethod
    def get_tags_score_coeff(cls, tags: List[str]) -> float:
        current = 1.0
        for tag in tags:
            current = min(
                current,
                config.settings.scoring.tag_score_coeffs.get(tag, current),
            )
        return current
