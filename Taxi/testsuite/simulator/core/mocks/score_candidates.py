"""
    Mocks /driver_scoring/v2/score-candidates-bulk API
"""

import pytest

from simulator.core import docs
from simulator.core import modules
from tests_united_dispatch.plugins import candidates_manager


@pytest.fixture(name='mock_simulator_scoring')
def _mock_simulator_scoring(mockserver, mocked_time):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock(request):
        responses = []
        for req in request.json['requests']:
            search = docs.OrderSearchRequest(req['search'])
            candidates = []
            for candidate_info in req['candidates']:
                candidate = candidates_manager.parse_candidate(
                    candidate_info=candidate_info,
                    assigned_at=mocked_time.now(),
                )
                performer = modules.CandidatesModel.get(
                    candidate_id=candidate.id,
                )
                candidates.append((performer, candidate))

            scores, retention_score = modules.ScoringModel.score_candidates(
                candidates=candidates, request=search,
            )

            scoring = []
            assert len(scores) == len(candidates)
            for (_, candidate), score in zip(candidates, scores):
                scoring.append({'id': candidate.id, 'score': score})

            responses.append(
                {
                    'candidates': scoring,
                    'search': {'retention_score': retention_score},
                },
            )

        return {'responses': responses}

    return _mock
