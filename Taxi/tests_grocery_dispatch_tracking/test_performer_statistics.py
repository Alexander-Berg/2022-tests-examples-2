import pytest

from tests_grocery_dispatch_tracking import constants as const
from tests_grocery_dispatch_tracking import events


@pytest.mark.now('2021-03-19T10:00:30+03:00')
@pytest.mark.parametrize(
    'from_, to_, need_delivered_orders, expected_statistics',
    [
        (None, None, False, {}),
        (None, None, True, {'delivered_orders': 3}),
        (None, '2021-03-19T10:00:04+03:00', True, {'delivered_orders': 1}),
        (None, '2021-03-19T10:00:05+03:00', True, {'delivered_orders': 2}),
        ('2021-03-19T10:00:06+03:00', None, True, {'delivered_orders': 1}),
        (
            '2021-03-19T10:00:04+03:00',
            '2021-03-19T10:00:06+03:00',
            True,
            {'delivered_orders': 1},
        ),
    ],
)
async def test_depot_metrics(
        taxi_grocery_dispatch_tracking,
        process_event,
        pgsql,
        expected_statistics,
        from_,
        to_,
        need_delivered_orders,
):
    depot_id = const.DEPOT_ID_LEGACY
    performer_id = const.PERFORMER_ID
    order_id_1 = '1-grocery'
    order_id_2 = '2-grocery'
    order_id_3 = '3-grocery'

    ts1 = '2021-03-19T10:00:00+03:00'
    ts2 = '2021-03-19T10:00:05+03:00'
    ts3 = '2021-03-19T10:00:15+03:00'

    order_delivered_events = [
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id_1, performer_id=performer_id, timestamp=ts1,
        ),
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id_2, performer_id=performer_id, timestamp=ts2,
        ),
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id_3, performer_id=performer_id, timestamp=ts3,
        ),
    ]

    await process_event(order_delivered_events)

    # Make request
    params = {
        'performer_id': performer_id,
        'from': from_,
        'to': to_,
        'delivered-orders': need_delivered_orders,
    }
    # remove None values
    params = {k: v for k, v in params.items() if v is not None}

    response = await taxi_grocery_dispatch_tracking.post(
        '/internal/grocery-dispatch-tracking/v1/performer-statistics',
        params=params,
    )

    assert response.json() == expected_statistics
