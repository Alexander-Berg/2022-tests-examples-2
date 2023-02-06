"""
    Mocks /candidates/order-search API
"""

import dataclasses
from typing import List
from typing import Set

import pytest

from simulator.core import config
from simulator.core import docs
from simulator.core import modules
from simulator.core import structures
from simulator.core.utils import distance
from tests_united_dispatch.plugins import candidates_manager
from tests_united_dispatch.plugins import cargo_dispatch_manager

# DELAYED_SEARCH = {}


def _get_active_special_requirements(
        segments: List[structures.DispatchSegment],
):
    return cargo_dispatch_manager.merge_special_requirements(
        [s.get_current_special_requirements() for s in segments],
    )


@pytest.fixture(name='mock_simulator_order_search')
def _mock_simulator_order_search(mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _mock(*, body_json):
        request = docs.OrderSearchRequest(body_json)

        allowed_classes: Set[str] = set()
        segments = []
        for segment_id in request.segment_ids:
            segment = modules.OrdersModel.get_segment(segment_id=segment_id)
            segments.append(segment)
            allowed_classes |= set(segment.info.taxi_classes)
        special_requirements = _get_active_special_requirements(segments)

        candidates = []
        for candidate in modules.CandidatesModel.list_free_candidates():
            meters_left = distance.between_coordinates(
                request.point,
                structures.Point(
                    lon=candidate.info.position[0],
                    lat=candidate.info.position[1],
                ),
            )
            if meters_left > config.settings.order_search.search_radius_m:
                continue

            seconds_left = meters_left / candidate.speed
            if seconds_left > config.settings.order_search.search_radius_sec:
                continue

            if not modules.VirtualTariffsModel.satisfy_candidate_classes(
                    special_requirements=special_requirements,
                    candidate=candidate,
                    allowed_classes=allowed_classes,
            ):
                continue

            candidates.append(
                {
                    'classes': candidate.info.classes,
                    'dbid': candidate.info.park_id,
                    'uuid': candidate.info.driver_profile_id,
                    'id': candidate.id,
                    'position': candidate.info.position,
                    'status': {'orders': [], 'status': 'online'},
                    'transport': {'type': candidate.info.transport_type},
                    'route_info': dataclasses.asdict(
                        candidates_manager.CandidateRouteInfo(
                            time=int(seconds_left),
                            distance=int(meters_left),
                            approximate=False,
                        ),
                    ),
                    'chain_info': (
                        candidate.info.chain_info
                        and dataclasses.asdict(candidate.info.chain_info)
                    ),
                },
            )

        candidates.sort(key=lambda x: x['route_info']['time'])
        candidates = candidates[
            : config.settings.order_search.candidates_limit
        ]

        return {'candidates': candidates}

    return _mock
