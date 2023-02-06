"""
    Describes simulation events with segments.
"""

from simulator.core import modules
from simulator.core import queue
from simulator.core import structures


@queue.event_handler
async def new_segment(segment: structures.DispatchSegment, **_):
    """
    Creates new segment
    """
    modules.OrdersModel.add_segment(segment)

    return segment


@queue.event_handler
async def cancel_segment_long_search(segment_id: str, **_):
    """
    Cancel segment if no candidate assigned yet
    """
    segment = modules.OrdersModel.get_segment(segment_id=segment_id)
    if segment.info.chosen_waybill_ref:
        waybill = modules.OrdersModel.get_waybill(
            segment.info.chosen_waybill_ref,
        )
        if waybill.info.performer_id:
            # candidate was found, skip event
            return 'candidate was found'

    if segment.info.resolution:
        return f'Segment {segment_id} already resolved'
    modules.OrdersModel.resolve_segment(
        segment, resolution='cancelled_by_user', status='cancelled',
    )

    return f'cancel segment {segment_id}'


@queue.event_handler
async def performer_not_found(segment_id: str, **_):
    """
    Finish segment if no candidate assigned yet
    """
    segment = modules.OrdersModel.get_segment(segment_id=segment_id)
    if segment.info.chosen_waybill_ref:
        waybill = modules.OrdersModel.get_waybill(
            segment.info.chosen_waybill_ref,
        )
        if waybill.info.performer_id:
            # candidate was found, skip event
            return 'candidate was found'

    if segment.info.resolution:
        return f'Segment {segment_id} already resolved'
    modules.OrdersModel.resolve_segment(
        segment,
        resolution='performer_not_found',
        status='performer_not_found',
    )

    return f'finish segment {segment_id}'
