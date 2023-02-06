"""
    Describes simulation events with candidates.
"""
import datetime
import logging
from typing import Optional

from simulator.core import modules
from simulator.core import queue
from simulator.core import structures
from simulator.core.utils import distance
from tests_united_dispatch.plugins import candidates_manager


LOG = logging.getLogger(__name__)


@queue.event_handler
async def online(candidate: structures.DispatchCandidate, **_):
    """
    Creates new online candidate
    """
    modules.CandidatesModel.add(candidate)
    dispatch_candidate = modules.CandidatesModel.get(candidate.id)

    return dispatch_candidate


@queue.event_handler
async def visit_point(
        candidate: candidates_manager.Candidate,
        *,
        timestamp: datetime.datetime = datetime.datetime.now(),
        visit_order: Optional[int] = None,
        **_,
):
    """
    Candidate visits order point
    """

    dispatch_candidate = modules.CandidatesModel.get(candidate.id)
    waybill = dispatch_candidate.waybill
    assert waybill is not None

    if visit_order is not None:
        modules.OrdersModel.set_point_resolution(
            waybill_ref=waybill.id, visit_order=visit_order, is_visited=True,
        )

    dispatch_candidate.sync_position(timestamp=timestamp)

    next_visit_order, __ = waybill.get_current_point()

    if next_visit_order is not None:
        distance_between_pos = distance.between_coordinates(
            first=structures.Point.from_list(dispatch_candidate.info.position),
            second=structures.Point.from_list(
                waybill.points[next_visit_order].coordinates,
            ),
        )

        dispatch_candidate.destination = structures.CandidateDestination(
            visit_order=next_visit_order,
            start_coordinates=dispatch_candidate.info.position,
            end_coordinates=waybill.points[next_visit_order].coordinates,
            start_ts=timestamp,
            duration=datetime.timedelta(
                seconds=distance_between_pos / dispatch_candidate.speed,
            ),
        )
        assert dispatch_candidate.destination
        assert dispatch_candidate.destination.visit_order == next_visit_order

        queue.EventQueue.put(
            timestamp + dispatch_candidate.destination.duration,
            visit_point(candidate=candidate, visit_order=next_visit_order),
        )
        if visit_order is not None:
            return f'resolve point visit_order={visit_order}'
        return f'queue event visit_order={next_visit_order}'

    LOG.info('Candidate %s delivered order %s', candidate.id, waybill.id)
    modules.OrdersModel.resolve_waybill(waybill.id)
    modules.CandidatesModel.set_free(candidate.id)

    return f'resolve waybill {waybill.id}, and free candidate {candidate.id}'
