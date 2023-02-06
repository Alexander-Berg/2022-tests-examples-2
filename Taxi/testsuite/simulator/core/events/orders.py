"""
    Describes simulation events with orders.
"""

import datetime
import logging
import uuid

from simulator.core import modules
from simulator.core import queue
from simulator.core import structures
from simulator.core.utils import distance
from . import candidates as candidates_events

LOG = logging.getLogger(__name__)


@queue.event_handler
async def new_order(
        waybill: structures.DispatchWaybill,
        *,
        timestamp: datetime.datetime = datetime.datetime.now(),
        **_,
):
    """
    Creates new candidate's order
    """
    if waybill.candidate is None:
        message = f'Empty candidate for waybill waybill {waybill.id}'
        LOG.warning(message)
        return message

    is_accepted = modules.CandidatesModel.is_order_accepted()
    if not is_accepted:
        return f'candidate {waybill.candidate.id} reject waybill {waybill.id}'
    if not modules.CandidatesModel.set_busy(waybill.candidate.id, waybill):
        return f'candidate {waybill.candidate.id} was busy, frozen race'

    waybill.is_accepted_by_candidate = True
    waybill.info.taxi_order_id = uuid.uuid4().hex
    waybill.info.set_performer()

    modules.OrdersModel.add_waybill(waybill)

    queue.EventQueue.put(
        timestamp, candidates_events.visit_point(candidate=waybill.candidate),
    )

    # update statistics
    candidate = modules.CandidatesModel.get(waybill.candidate.id)
    meters_to_pickup = distance.between_coordinates(
        structures.Point.from_list(waybill.info.points[0].coordinates),
        structures.Point.from_list(candidate.info.position),
    )

    candidate.stats.distances_to_pickup.append(meters_to_pickup)
    for waybill_segment in waybill.info.segments:
        segment = modules.OrdersModel.get_segment(waybill_segment.id)
        segment.on_candidate_found()

    left_free_candidates = len(modules.CandidatesModel.list_free_candidates())
    return (f'candidates left {left_free_candidates}', waybill)
