"""
    Describes simulation events with dispatch planners
"""
import datetime
import logging
import time

from simulator.core import config
from simulator.core import modules
from simulator.core import queue
from simulator.core import structures
from simulator.core.utils import current_time
from . import orders as orders_events

LOG = logging.getLogger(__name__)


@queue.event_handler
async def run_planner(
        planner_type: str = 'delivery',
        start_timestamp: datetime.datetime = datetime.datetime.now(),
        *,
        timestamp: datetime.datetime = datetime.datetime.now(),
        **_,
):
    """
    Run planner, parse output and put new events
    """
    start = time.perf_counter()
    output = await modules.DispatchModel.run(
        planner_type=planner_type,
        segments=[
            s.info
            for s in modules.OrdersModel.list_active_segments(
                config.settings.dispatch.max_segments,
            )
        ],
        active_waybills=modules.OrdersModel.list_active_waybills(
            config.settings.dispatch.max_active_waybills,
        ),
    )
    elapsed_time = time.perf_counter() - start

    modules.DispatchModel.stats.add_result(
        structures.DispatchRunStats(
            propositions=len(output.propositions),
            assigned_candidates=len(output.assigned_candidates),
            passed_segments=len(output.passed_segment_ids),
            skipped_segments=len(output.skipped_segment_ids),
            elapsed_time=elapsed_time,
        ),
    )

    now = current_time.CurrentTime.get()
    # put proposition in events
    for proposition in output.propositions:
        queue.EventQueue.put(now, orders_events.new_order(waybill=proposition))

    # put assigned proposition in events
    for assigned_candidate in output.assigned_candidates:
        queue.EventQueue.put(
            now, orders_events.new_order(waybill=assigned_candidate),
        )

    # if there is some events or skipped segments then add planner run
    if (
            output.skipped_segment_ids
            or output.passed_segment_ids
            or not queue.EventQueue.is_empty()
    ):
        if now - start_timestamp >= config.settings.dispatch.total_timeout:
            LOG.error(
                'Cannot add new planner run because total timeout is reached'
                ' (start=%s, now=%s, delta=%s, timeout=%s)',
                start_timestamp,
                now,
                now - start_timestamp,
                config.settings.dispatch.total_timeout,
            )
        else:
            queue.EventQueue.put(
                timestamp + config.settings.dispatch.run_interval,
                run_planner(
                    planner_type=planner_type, start_timestamp=start_timestamp,
                ),
            )

    return output
