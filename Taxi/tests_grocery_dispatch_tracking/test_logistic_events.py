# pylint: disable=too-many-lines
from typing import List

import psycopg2.extras
import pytest

from tests_grocery_dispatch_tracking import constants as const
from tests_grocery_dispatch_tracking import events


def empty_stat(depot_id=const.DEPOT_ID_LEGACY):
    return {
        'await_orders': 0,
        'depot_id': depot_id,
        'free_performers': 0,
        'delivering_orders': 0,
        'delivering_performers': 0,
        'matched_orders': 0,
        'matched_performers': 0,
        'handing_orders': 0,
        'returning_orders': 0,
        'handing_performers': 0,
        'returning_performers': 0,
    }


def events_to_matched(
        depot_id=const.DEPOT_ID_LEGACY,
        performer_id=const.PERFORMER_ID,
        order_id=const.ORDER_ID,
) -> List[events.BaseEvent]:
    performer_shift_open_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id,
        status=const.ShiftStatus.open,
        performer_id=performer_id,
    )
    order_created_event = events.GroceryOrderCreatedEvent(depot_id, order_id)
    dispatch_request_event = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id,
    )
    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )
    order_matched_event = events.GroceryOrderMatchedEvent(
        depot_id, order_id, performer_id=performer_id,
    )
    return [
        performer_shift_open_event,
        order_created_event,
        dispatch_request_event,
        dispatch_ready_event,
        order_matched_event,
    ]


def events_to_pickup(
        depot_id=const.DEPOT_ID_LEGACY,
        performer_id=const.PERFORMER_ID,
        order_id=const.ORDER_ID,
):
    return events_to_matched(depot_id, performer_id, order_id) + [
        events.GroceryPerformerPickupOrderEvent(
            depot_id, order_id, performer_id=performer_id,
        ),
    ]


def events_to_arrived(
        depot_id=const.DEPOT_ID_LEGACY,
        performer_id=const.PERFORMER_ID,
        order_id=const.ORDER_ID,
):
    return events_to_pickup(depot_id, performer_id, order_id) + [
        events.GroceryPerformerDeliveringArrived(
            depot_id, order_id, performer_id=performer_id,
        ),
    ]


def events_to_delivered(
        depot_id=const.DEPOT_ID_LEGACY,
        performer_id=const.PERFORMER_ID,
        order_id=const.ORDER_ID,
):
    return events_to_pickup(depot_id, performer_id, order_id) + [
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id, performer_id=performer_id,
        ),
    ]


async def test_get_grocery_order_dispatch_ready(process_event):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )

    assert (await process_event(dispatch_ready_event))['events'] == [
        dispatch_ready_event.dict(),
    ]


async def test_get_grocery_order_delivered(process_event):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    order_delivered_event = events.GroceryOrderDeliveredEvent(
        depot_id, order_id,
    )
    assert (await process_event(order_delivered_event))['events'] == [
        order_delivered_event.dict(),
    ]


async def test_order_speed_statistics_base(process_event, pgsql, stq):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    order_delivered_event = events.GroceryOrderDeliveredEvent(
        depot_id, order_id,
    )
    assert (await process_event(order_delivered_event))['events'] == [
        order_delivered_event.dict(),
    ]
    assert stq.grocery_order_statistics_postprocessing.times_called == 1
    stq_args = stq.grocery_order_statistics_postprocessing.next_call()[
        'kwargs'
    ]
    assert stq_args['order_id'] == order_id
    assert stq_args['depot_id'] == depot_id


async def test_basic_statistics(stats_context, pgsql):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    stats = stats_context(initial_stats=empty_stat(depot_id))

    order_created_event = events.GroceryOrderCreatedEvent(depot_id, order_id)
    dispatch_request_event = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id,
    )
    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )
    order_matched_event = events.GroceryOrderMatchedEvent(depot_id, order_id)
    performer_pickup_order_event = events.GroceryPerformerPickupOrderEvent(
        depot_id, order_id,
    )
    performer_arrived_event = events.GroceryPerformerDeliveringArrived(
        depot_id, order_id,
    )
    order_delivered_event = events.GroceryOrderDeliveredEvent(
        depot_id, order_id,
    )
    order_closed_event = events.GroceryOrderClosedEvent(depot_id, order_id)
    performer_returned_event = events.GroceryPerformerReturnDepot(depot_id)

    performer_shift_open_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.open,
    )
    performer_shift_pause_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.pause,
    )
    performer_shift_unpause_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.unpause,
    )
    performer_shift_close_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.close,
    )

    # Performer open, pause and unpause
    await stats.check(
        [
            performer_shift_open_event,
            performer_shift_open_event,  # test duplicates
            performer_shift_pause_event,
            performer_shift_pause_event,
            performer_shift_unpause_event,
            performer_shift_unpause_event,
        ],
        [
            {'free_performers': 1},
            {},
            {'free_performers': 0},
            {},
            {'free_performers': 1},
            {},
        ],
    )

    # Order created
    await stats.check(order_created_event, {})
    await stats.check(order_created_event, {})  # test duplicates

    # Dispatch request
    await stats.check(dispatch_request_event, {})
    await stats.check(dispatch_request_event, {})

    # Dispatch ready
    await stats.check(dispatch_ready_event, {'await_orders': 1})
    await stats.check(dispatch_ready_event, {})

    # Order matched with performer
    await stats.check(
        order_matched_event,
        {
            'await_orders': 0,
            'matched_orders': 1,
            'free_performers': 0,
            'matched_performers': 1,
        },
    )
    await stats.check(order_matched_event, {})

    # Pick up order from depot
    await stats.check(
        performer_pickup_order_event,
        {
            'delivering_orders': 1,
            'delivering_performers': 1,
            'matched_orders': 0,
            'matched_performers': 0,
        },
    )
    await stats.check(performer_pickup_order_event, {})

    # Performer arrived
    await stats.check(
        performer_arrived_event,
        {
            'handing_orders': 1,
            'handing_performers': 1,
            'delivering_orders': 0,
            'delivering_performers': 0,
        },
    )

    # Order delivered
    await stats.check(
        order_delivered_event,
        {
            'handing_orders': 0,
            'handing_performers': 0,
            'returning_performers': 1,
        },
    )
    await stats.check(order_delivered_event, {})

    # Order closed
    await stats.check(order_closed_event, {})
    await stats.check(order_closed_event, {})

    # Performer returned to depot
    await stats.check(
        performer_returned_event,
        {'free_performers': 1, 'returning_performers': 0},
    )
    await stats.check(performer_returned_event, {})

    # Performer closed shift
    await stats.check(performer_shift_close_event, {'free_performers': 0})
    await stats.check(performer_shift_close_event, {})


async def test_grocery_order_assembled(stats_context):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    stats = stats_context(initial_stats=empty_stat(depot_id))

    order_created_event = events.GroceryOrderCreatedEvent(depot_id, order_id)
    dispatch_request_event = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id,
    )
    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )
    order_assembled_event = events.GroceryOrderAssembledEvent(
        depot_id, order_id,
    )

    await stats.check(order_created_event, {})
    await stats.check(dispatch_request_event, {})
    await stats.check(dispatch_ready_event, {'await_orders': 1})
    await stats.check(order_assembled_event, {})


async def test_two_depots_statistics_dont_intersect(stats_context, pgsql):
    depot_id_1 = const.DEPOT_ID_LEGACY
    depot_id_2 = const.DEPOT_ID_LEGACY_2

    order_id_1 = const.ORDER_ID
    order_id_2 = const.ORDER_ID_2

    stats_1 = stats_context(empty_stat(depot_id_1))

    stats_2 = stats_context(empty_stat(depot_id_2))

    order_created_event_1 = events.GroceryOrderCreatedEvent(
        depot_id_1, order_id_1,
    )
    order_created_event_2 = events.GroceryOrderCreatedEvent(
        depot_id_2, order_id_2,
    )

    dispatch_request_event_1 = events.GroceryOrderDispatchRequestEvent(
        depot_id_1, order_id_1,
    )
    dispatch_ready_event_1 = events.GroceryOrderDispatchReadyEvent(
        depot_id_1, order_id_1,
    )

    dispatch_request_event_2 = events.GroceryOrderDispatchRequestEvent(
        depot_id_2, order_id_2,
    )
    dispatch_ready_event_2 = events.GroceryOrderDispatchReadyEvent(
        depot_id_2, order_id_2,
    )

    await stats_1.check(order_created_event_1, {})
    await stats_2.check(order_created_event_2, {})
    await stats_1.check(dispatch_request_event_1, {})
    await stats_2.check(dispatch_request_event_2, {})
    await stats_1.check(dispatch_ready_event_1, {'await_orders': 1})
    await stats_2.check(dispatch_ready_event_2, {'await_orders': 1})


async def test_one_performer_two_orders_delivered(
        stats_context, process_event, pgsql,
):
    depot_id = const.DEPOT_ID_LEGACY

    order_id_1 = const.ORDER_ID
    order_id_2 = const.ORDER_ID_2

    performer_shift_open_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.open,
    )
    order_created_event_1 = events.GroceryOrderCreatedEvent(
        depot_id, order_id_1,
    )
    order_created_event_2 = events.GroceryOrderCreatedEvent(
        depot_id, order_id_2,
    )

    dispatch_request_event_1 = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id_1,
    )
    dispatch_request_event_2 = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id_2,
    )
    dispatch_ready_event_1 = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id_1,
    )
    dispatch_ready_event_2 = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id_2,
    )

    order_matched_event = events.GroceryOrderMatchedEvent(depot_id, order_id_1)
    order_matched_event_2 = events.GroceryOrderMatchedEvent(
        depot_id, order_id_2,
    )
    performer_pickup_order_event = events.GroceryPerformerPickupOrderEvent(
        depot_id, order_id_1,
    )
    performer_pickup_order_event_2 = events.GroceryPerformerPickupOrderEvent(
        depot_id, order_id_2,
    )
    performer_arrived_event = events.GroceryPerformerDeliveringArrived(
        depot_id, order_id_1,
    )
    performer_arrived_event_2 = events.GroceryPerformerDeliveringArrived(
        depot_id, order_id_2,
    )
    order_delivered_event = events.GroceryOrderDeliveredEvent(
        depot_id, order_id_1,
    )
    order_delivered_event_2 = events.GroceryOrderDeliveredEvent(
        depot_id, order_id_2,
    )
    order_closed_event = events.GroceryOrderClosedEvent(depot_id, order_id_1)
    order_closed_event_2 = events.GroceryOrderClosedEvent(depot_id, order_id_2)

    await process_event(performer_shift_open_event)
    await process_event(order_created_event_1)
    await process_event(order_created_event_2)
    await process_event(dispatch_request_event_1)
    await process_event(dispatch_request_event_2)
    await process_event(dispatch_ready_event_1)
    await process_event(dispatch_ready_event_2)
    await process_event(order_matched_event)
    await process_event(order_matched_event_2)
    await process_event(performer_pickup_order_event)
    await process_event(performer_pickup_order_event_2)
    await process_event(performer_arrived_event)

    stats = stats_context(
        initial_stats={
            'await_orders': 0,
            'depot_id': depot_id,
            'free_performers': 0,
            'delivering_orders': 1,
            'delivering_performers': 0,
            'matched_orders': 0,
            'matched_performers': 0,
            'handing_orders': 1,
            'returning_orders': 0,
            'handing_performers': 1,
            'returning_performers': 0,
        },
    )

    await stats.check(
        order_delivered_event,
        {
            'handing_orders': 0,
            'delivering_performers': 1,
            'handing_performers': 0,
        },
    )
    await stats.check(
        performer_arrived_event_2,
        {
            'handing_orders': 1,
            'delivering_performers': 0,
            'delivering_orders': 0,
            'handing_performers': 1,
        },
    )
    await stats.check(
        order_delivered_event_2,
        {
            'handing_orders': 0,
            'returning_performers': 1,
            'handing_performers': 0,
        },
    )

    await process_event(order_closed_event)
    await process_event(order_closed_event_2)


async def test_skipped_matched_status(stats_context):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    stats = stats_context(initial_stats=empty_stat(depot_id))

    order_created_event = events.GroceryOrderCreatedEvent(depot_id, order_id)
    dispatch_request_event = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id,
    )
    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )
    performer_pickup_order_event = events.GroceryPerformerPickupOrderEvent(
        depot_id, order_id,
    )
    order_closed_event = events.GroceryOrderClosedEvent(depot_id, order_id)

    performer_shift_open_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.open,
    )

    # Performer open, pause and unpause
    await stats.check(performer_shift_open_event, {'free_performers': 1})

    # Order created
    await stats.check(order_created_event, {})

    # Dispatch request
    await stats.check(dispatch_request_event, {})

    # Dispatch ready
    await stats.check(dispatch_ready_event, {'await_orders': 1})

    # Pick up order from depot
    await stats.check(
        performer_pickup_order_event,
        {
            'delivering_orders': 1,
            'await_orders': 0,
            'delivering_performers': 1,
            'free_performers': 0,
        },
    )

    # Order closed
    await stats.check(
        order_closed_event,
        {
            'delivering_orders': 0,
            'delivering_performers': 0,
            'returning_performers': 1,
        },
    )


async def test_cancel_delivery_delivering_order(
        stats_context, process_events, pgsql,
):
    depot_id = const.DEPOT_ID_LEGACY

    order_id = const.ORDER_ID

    await process_events(*events_to_pickup(order_id=order_id))

    order_canceled_event = events.GroceryOrderDeliveryCanceled(
        depot_id, order_id,
    )

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'delivering_orders': 1,
            'delivering_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event,
        {
            'delivering_performers': 0,
            'delivering_orders': 0,
            'returning_orders': 1,
            'returning_performers': 1,
        },
    )

    await stats.check(
        events.GroceryPerformerReturnDepot(),
        {
            'returning_performers': 0,
            'free_performers': 1,
            'await_orders': 1,
            'returning_orders': 0,
        },
    )

    await stats.check(events.GroceryOrderClosedEvent(), {'await_orders': 0})


async def test_cancel_delivery_matched_order(
        stats_context, process_events, pgsql,
):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    await process_events(*events_to_matched(order_id=order_id))
    order_canceled_event = events.GroceryOrderDeliveryCanceled(
        depot_id, order_id,
    )

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'matched_orders': 1,
            'matched_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event,
        {
            'matched_performers': 0,
            'matched_orders': 0,
            'await_orders': 1,
            'free_performers': 1,
        },
    )

    await stats.check(events.GroceryOrderClosedEvent(), {'await_orders': 0})


async def test_cancel_delivery_handing_order(
        stats_context, process_events, pgsql,
):

    await process_events(*events_to_arrived())
    order_canceled_event = events.GroceryOrderDeliveryCanceled()

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'handing_orders': 1,
            'handing_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event,
        {
            'handing_orders': 0,
            'handing_performers': 0,
            'returning_orders': 1,
            'returning_performers': 1,
        },
    )

    await stats.check(
        events.GroceryOrderClosedEvent(), {'returning_orders': 0},
    )


async def test_cancel_delivery_returning_order(
        stats_context, process_events, pgsql,
):

    await process_events(*events_to_pickup())
    order_canceled_event = events.GroceryOrderDeliveryCanceled()

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'delivering_orders': 1,
            'delivering_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event,
        {
            'delivering_orders': 0,
            'delivering_performers': 0,
            'returning_orders': 1,
            'returning_performers': 1,
        },
    )
    await stats.check(order_canceled_event, {})

    await stats.check(
        events.GroceryOrderClosedEvent(), {'returning_orders': 0},
    )


async def test_close_delivering_order(stats_context, process_events, pgsql):
    order_id = const.ORDER_ID

    await process_events(*events_to_pickup(order_id=order_id))

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'delivering_orders': 1,
            'delivering_performers': 1,
        },
    )

    await stats.check(
        events.GroceryOrderClosedEvent(),
        {
            'delivering_orders': 0,
            'delivering_performers': 0,
            'returning_performers': 1,
        },
    )

    await stats.check(
        events.GroceryPerformerReturnDepot(),
        {'returning_performers': 0, 'free_performers': 1},
    )


async def test_one_performer_two_orders_delivering_both_canceled(
        stats_context, process_events,
):
    order_id_1 = const.ORDER_ID
    order_id_2 = const.ORDER_ID_2

    await process_events(*events_to_pickup(order_id=order_id_1))
    await process_events(*events_to_pickup(order_id=order_id_2))

    order_canceled_event_1 = events.GroceryOrderDeliveryCanceled(
        order_id=order_id_1,
    )
    order_canceled_event_2 = events.GroceryOrderDeliveryCanceled(
        order_id=order_id_2,
    )

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'delivering_orders': 2,
            'delivering_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event_2,
        {'delivering_orders': 1, 'returning_orders': 1},
    )
    await stats.check(
        order_canceled_event_1,
        {
            'delivering_orders': 0,
            'returning_orders': 2,
            'returning_performers': 1,
            'delivering_performers': 0,
        },
    )


async def test_one_performer_two_orders_one_canceled_while_other_handing(
        stats_context, process_events, pgsql,
):
    order_id_1 = const.ORDER_ID
    order_id_2 = const.ORDER_ID_2

    await process_events(*events_to_pickup(order_id=order_id_1))
    await process_events(*events_to_pickup(order_id=order_id_2))

    performer_arrived_event = events.GroceryPerformerDeliveringArrived(
        order_id=order_id_1,
    )

    order_delivered_event_1 = events.GroceryOrderDeliveredEvent(
        order_id=order_id_1,
    )
    order_canceled_event_2 = events.GroceryOrderDeliveryCanceled(
        order_id=order_id_2,
    )
    await process_events(performer_arrived_event)

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'delivering_orders': 1,
            'handing_orders': 1,
            'handing_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event_2,
        {'delivering_orders': 0, 'returning_orders': 1},
    )

    # cursor = pgsql['grocery_dispatch_tracking'].cursor()
    # cursor.execute('select * from dispatch_tracking.delivery')
    # print('Hello', list(cursor))

    await stats.check(
        order_delivered_event_1,
        {
            'handing_orders': 0,
            'returning_performers': 1,
            'handing_performers': 0,
        },
    )

    order_closed_event = events.GroceryOrderClosedEvent(order_id=order_id_1)
    order_closed_event_2 = events.GroceryOrderClosedEvent(order_id=order_id_2)
    await process_events(order_closed_event, order_closed_event_2)


async def test_two_orders_one_canceled_while_handing_other_delivering(
        stats_context, process_events, pgsql,
):
    depot_id = const.DEPOT_ID_LEGACY

    order_id_1 = const.ORDER_ID
    order_id_2 = const.ORDER_ID_2

    await process_events(*events_to_pickup(order_id=order_id_1))
    await process_events(*events_to_pickup(order_id=order_id_2))

    performer_arrived_event_1 = events.GroceryPerformerDeliveringArrived(
        depot_id, order_id_1,
    )
    await process_events(performer_arrived_event_1)

    order_canceled_event_1 = events.GroceryOrderDeliveryCanceled(
        depot_id, order_id_1,
    )
    order_delivered_event_2 = events.GroceryOrderDeliveredEvent(
        depot_id, order_id_2,
    )

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'delivering_orders': 1,
            'handing_orders': 1,
            'handing_performers': 1,
        },
    )

    await stats.check(
        order_canceled_event_1,
        {
            'handing_orders': 0,
            'handing_performers': 0,
            'delivering_performers': 1,
            'returning_orders': 1,
        },
    )

    await stats.check(
        order_delivered_event_2,
        {
            'delivering_orders': 0,
            'delivering_performers': 0,
            'returning_performers': 1,
        },
    )

    order_closed_event = events.GroceryOrderClosedEvent(depot_id, order_id_1)
    order_closed_event_2 = events.GroceryOrderClosedEvent(depot_id, order_id_2)
    await process_events(order_closed_event, order_closed_event_2)


async def test_courier_returned_before_two_orders_delivered(
        stats_context, process_events, pgsql,
):
    depot_id = const.DEPOT_ID_LEGACY

    order_id_1 = const.ORDER_ID
    order_id_2 = const.ORDER_ID_2

    stats = stats_context(
        initial_stats={
            **empty_stat(),
            'handing_orders': 2,
            'handing_performers': 1,
        },
    )

    await process_events(*events_to_arrived(order_id=order_id_1))
    await process_events(*events_to_arrived(order_id=order_id_2))

    await stats.check(
        events.GroceryPerformerReturnDepot(),
        {'free_performers': 1, 'handing_performers': 0},
    )

    await stats.check(
        [
            events.GroceryOrderDeliveredEvent(depot_id, order_id_1),
            events.GroceryOrderDeliveredEvent(depot_id, order_id_2),
        ],
        [{'handing_orders': 1}, {'handing_orders': 0}],
    )
    await process_events(
        events.GroceryOrderClosedEvent(depot_id, order_id_1),
        events.GroceryOrderClosedEvent(depot_id, order_id_2),
    )


async def test_performer_delete_from_old_depots(stats_context):
    depot_id_1 = const.DEPOT_ID_LEGACY
    depot_id_2 = const.DEPOT_ID_LEGACY_2

    performer_id_1 = 'performer_1'
    performer_id_2 = 'performer_2'

    stats_1 = stats_context(empty_stat(depot_id_1))

    stats_2 = stats_context(empty_stat(depot_id_2))

    open_performer_1_depot_1_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id_1,
        status=const.ShiftStatus.open,
        performer_id=performer_id_1,
    )

    open_performer_1_depot_2_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id_2,
        status=const.ShiftStatus.open,
        performer_id=performer_id_1,
    )

    open_performer_2_depot_1_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id_1,
        status=const.ShiftStatus.open,
        performer_id=performer_id_2,
    )

    await stats_1.check(open_performer_1_depot_1_event, {'free_performers': 1})
    await stats_2.check(open_performer_1_depot_2_event, {'free_performers': 1})
    await stats_1.check(
        open_performer_2_depot_1_event,
        {'free_performers': 1},
        check_prev=False,
    )


async def test_two_consequence_shift_open_bug(stats_context):
    depot_id = const.DEPOT_ID_LEGACY
    performer_id = 'performer_1'

    stats = stats_context(empty_stat(depot_id))

    open_event_1 = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id,
        status=const.ShiftStatus.open,
        performer_id=performer_id,
    )

    open_event_2 = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id,
        status=const.ShiftStatus.open,
        performer_id=performer_id,
    )

    await stats.check(
        [open_event_1, open_event_2], [{'free_performers': 1}, {}],
    )


async def test_remove_performer_from_another_depots_when_open_shift(
        stats_context,
):
    depot_id = const.DEPOT_ID_LEGACY
    performer_id_1 = 'performer_1'
    performer_id_2 = 'performer_2'

    stats = stats_context(empty_stat(depot_id))

    open_event_1 = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id,
        status=const.ShiftStatus.open,
        performer_id=performer_id_1,
    )

    open_event_2 = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id,
        status=const.ShiftStatus.open,
        performer_id=performer_id_2,
    )

    close_event_1 = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id,
        status=const.ShiftStatus.close,
        performer_id=performer_id_1,
    )

    await stats.check(
        [open_event_1, open_event_2],
        [{'free_performers': 1}, {'free_performers': 2}],
    )
    await stats.check(close_event_1, {'free_performers': 1})


async def test_retry_postgres_error(process_event, testpoint):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    inject = True

    @testpoint('inject_pg_error')
    def inject_error(data):
        nonlocal inject
        res = {'is_inject_error': inject}
        inject = False  # don't inject on next invocation
        return res

    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )

    assert (await process_event(dispatch_ready_event))['events'] == [
        dispatch_ready_event.dict(),
    ]
    assert inject_error.times_called == 2


@pytest.mark.parametrize(
    'created_delivery_type, is_matched, matched_delivery_type, expected',
    [
        (None, False, None, None),
        ('dispatch', False, None, 'dispatch'),
        ('pickup', False, None, 'pickup'),
        ('rover', False, None, 'rover'),
        ('rover', True, None, 'rover'),
        ('dispatch', True, 'courier', 'courier'),
        ('dispatch', True, 'yandex_taxi', 'yandex_taxi'),
    ],
)
async def test_store_delivering_type_from_created_and_matched_events(
        process_event,
        pgsql,
        created_delivery_type,
        is_matched,
        matched_delivery_type,
        expected,
):
    depot_id = const.DEPOT_ID_LEGACY
    order_id = const.ORDER_ID

    order_created_event = events.GroceryOrderCreatedEvent(
        depot_id, order_id, delivery_type=created_delivery_type,
    )
    dispatch_request_event = events.GroceryOrderDispatchRequestEvent(
        depot_id, order_id,
    )
    dispatch_ready_event = events.GroceryOrderDispatchReadyEvent(
        depot_id, order_id,
    )
    order_matched_event = events.GroceryOrderMatchedEvent(
        depot_id, order_id, delivery_type=matched_delivery_type,
    )

    await process_event(order_created_event)
    await process_event(dispatch_request_event)
    await process_event(dispatch_ready_event)
    if is_matched:
        await process_event(order_matched_event)

    # TODO move to database related fixtures
    cursor = pgsql['grocery_dispatch_tracking'].cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    cursor.execute(
        f'SELECT delivery_type from dispatch_tracking.orders WHERE '
        f'order_id=\'{order_id}\'',
    )
    row = cursor.fetchone()

    assert row.delivery_type == expected
