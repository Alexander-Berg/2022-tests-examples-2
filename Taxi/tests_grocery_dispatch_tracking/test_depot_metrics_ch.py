import datetime

import pytest
import pytz


from tests_grocery_dispatch_tracking import constants as const
from tests_grocery_dispatch_tracking import events

CLICKHOUSE_ON_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_tracking_db_chooser',
    consumers=['grocery_dispatch_tracking/db_chooser'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'depot_statistics': ['clickhouse'],
                'db_prefix': 'production',
            },
        },
    ],
    is_config=True,
)

CALC_SPEED_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_tracking_calc_speed',
    consumers=['grocery_dispatch_tracking/db_chooser'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={},
    is_config=True,
)


@CALC_SPEED_CONFIG
@CLICKHOUSE_ON_CONFIG
@pytest.mark.now('2021-03-19T10:00:40+03:00')
@pytest.mark.parametrize(
    'interval, order_limit, start_time, expected_statistics',
    [
        (
            None,
            None,
            None,
            [
                {
                    'legacy_depot_id': '12345',
                    'statistics': {
                        'average_between_order_pickup_ms': 5666,
                        'average_between_order_matched_ms': 5000,
                        'average_order_assembling_ms': 15000,
                        'average_between_order_assembling_ms': 5000,
                        'average_order_time_ms': 15000,
                        'average_cooking_time_ms': 2000,
                        'average_performer_speed': 3.6,
                    },
                },
            ],
        ),
        (
            None,
            2,  # exclude order_1 by order limit
            None,
            [
                {
                    'legacy_depot_id': '12345',
                    'statistics': {
                        'average_between_order_pickup_ms': 5500,
                        'average_between_order_matched_ms': 5000,
                        'average_order_assembling_ms': 17500,
                        'average_between_order_assembling_ms': 5000,
                        'average_order_time_ms': 17500,
                        'average_cooking_time_ms': 2500,
                        'average_performer_speed': 2.88,
                    },
                },
            ],
        ),
    ],
)
async def test_depot_metrics_ch(
        taxi_grocery_dispatch_tracking,
        mockserver,
        grocery_depots,
        stq_runner,
        process_event,
        interval,
        order_limit,
        start_time,
        expected_statistics,
        clickhouse,
        experiments3,
):
    @mockserver.json_handler('/grocery-orders/internal/v1/get-info-bulk')
    def _get_info_bulk(request):
        ret = []
        for order_id in request.json['order_ids']:
            ret.append(
                {
                    'order_id': order_id,
                    'location': {'lat': 0.0, 'lon': 12.0},
                    # next fields doesnt matter in this test
                    'status': 'closed',
                    'created': '2021-03-19T10:00:00+03:00',
                    'cart_id': '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
                },
            )
        return ret

    @mockserver.json_handler(
        '/grocery-routing/internal/grocery-routing/v1/route',
    )
    def _get_route(_request):
        return {'distance': 10, 'eta': 60}

    depot = grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=const.DEPOT_ID_LEGACY,
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_tracking_db_chooser',
    )

    depot_id = depot.legacy_depot_id
    order_id_1 = '1-grocery'
    order_id_2 = '2-grocery'
    order_id_3 = '3-grocery'

    ts1_start = '2021-03-19T10:00:00+03:00'
    ts2_start = '2021-03-19T10:00:05+03:00'
    ts3_start = '2021-03-19T10:00:15+03:00'

    ts1_pickup = '2021-03-19T10:00:01+03:00'  # ts1_start + 1 sec
    ts2_pickup = '2021-03-19T10:00:07+03:00'  # ts2_start + 2 sec
    ts3_pickup = '2021-03-19T10:00:18+03:00'  # ts3_start + 3 sec

    ts1_delivered = '2021-03-19T10:00:06+03:00'  # ts1_start + 6 sec
    ts2_delivered = '2021-03-19T10:00:17+03:00'  # ts2_start + 12 sec
    ts3_delivered = '2021-03-19T10:00:33+03:00'  # ts3_start + 18 sec

    ts1_end = '2021-03-19T10:00:10+03:00'  # ts1_start + 10 sec
    ts2_end = '2021-03-19T10:00:20+03:00'  # ts2_start + 15 sec
    ts3_end = '2021-03-19T10:00:35+03:00'  # ts3_start + 20 sec

    order_created_events = [
        events.GroceryOrderCreatedEvent(
            depot_id, order_id_1, timestamp=ts1_start,
        ),
        events.GroceryOrderCreatedEvent(
            depot_id, order_id_2, timestamp=ts2_start,
        ),
        events.GroceryOrderCreatedEvent(
            depot_id, order_id_3, timestamp=ts3_start,
        ),
    ]

    order_assemble_ready_events = [
        events.GroceryOrderAssembleReadyEvent(
            depot_id, order_id_1, timestamp=ts1_start,
        ),
        events.GroceryOrderAssembleReadyEvent(
            depot_id, order_id_2, timestamp=ts2_start,
        ),
        events.GroceryOrderAssembleReadyEvent(
            depot_id, order_id_3, timestamp=ts3_start,
        ),
    ]

    order_assembled_events = [
        events.GroceryOrderAssembledEvent(
            depot_id, order_id_1, timestamp=ts1_end,
        ),
        events.GroceryOrderAssembledEvent(
            depot_id, order_id_2, timestamp=ts2_end,
        ),
        events.GroceryOrderAssembledEvent(
            depot_id, order_id_3, timestamp=ts3_end,
        ),
    ]

    dispatch_request_events = [
        events.GroceryOrderDispatchRequestEvent(depot_id, order_id_1),
        events.GroceryOrderDispatchRequestEvent(depot_id, order_id_2),
        events.GroceryOrderDispatchRequestEvent(depot_id, order_id_3),
    ]

    dispatch_ready_events = [
        events.GroceryOrderDispatchReadyEvent(depot_id, order_id_1),
        events.GroceryOrderDispatchReadyEvent(depot_id, order_id_2),
        events.GroceryOrderDispatchReadyEvent(depot_id, order_id_3),
    ]

    order_matched_events = [
        events.GroceryOrderMatchedEvent(
            depot_id, order_id_1, timestamp=ts1_start,
        ),
        events.GroceryOrderMatchedEvent(
            depot_id, order_id_2, timestamp=ts2_start,
        ),
        events.GroceryOrderMatchedEvent(
            depot_id, order_id_3, timestamp=ts3_start,
        ),
    ]

    performer_pickup_order_events = [
        events.GroceryPerformerPickupOrderEvent(
            depot_id, order_id_1, ts1_pickup,
        ),
        events.GroceryPerformerPickupOrderEvent(
            depot_id, order_id_2, ts2_pickup,
        ),
        events.GroceryPerformerPickupOrderEvent(
            depot_id, order_id_3, ts3_pickup,
        ),
    ]

    order_delivered_order_events = [
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id_1, timestamp=ts1_delivered,
        ),
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id_2, timestamp=ts2_delivered,
        ),
        events.GroceryOrderDeliveredEvent(
            depot_id, order_id_3, timestamp=ts3_delivered,
        ),
    ]

    order_closed_events = [
        events.GroceryOrderClosedEvent(
            depot_id, order_id_1, timestamp=ts1_end,
        ),
        events.GroceryOrderClosedEvent(
            depot_id, order_id_2, timestamp=ts2_end,
        ),
        events.GroceryOrderClosedEvent(
            depot_id, order_id_3, timestamp=ts3_end,
        ),
    ]

    performer_shift_open_event = events.GroceryPerformerShiftUpdated(
        depot_id=depot_id, status=const.ShiftStatus.open,
    )

    await process_event(performer_shift_open_event)
    await process_event(order_created_events)
    await process_event(order_assemble_ready_events)
    await process_event(order_assembled_events)
    await process_event(dispatch_request_events)
    await process_event(dispatch_ready_events)
    await process_event(order_matched_events)
    await process_event(performer_pickup_order_events)

    await process_event(order_delivered_order_events)
    delivered_events = [
        {'order_id': order_id_1, 'timestamp': ts1_delivered},
        {'order_id': order_id_2, 'timestamp': ts2_delivered},
        {'order_id': order_id_3, 'timestamp': ts3_delivered},
    ]
    for event in delivered_events:
        await stq_runner.grocery_order_statistics_postprocessing.call(
            task_id=event['order_id'] + '_spp',
            kwargs={
                'order_id': event['order_id'],
                'depot_id': const.DEPOT_ID_LEGACY,
                'performer_id': const.PERFORMER_ID,
                'timestamp': event['timestamp'],
            },
        )

    await process_event(order_closed_events)

    # Make request
    request = {
        'legacy_depot_ids': [const.DEPOT_ID_LEGACY],
        'interval': interval,
        'order_limit': order_limit,
        'start_time': start_time,
    }

    response = await taxi_grocery_dispatch_tracking.post(
        '/internal/grocery-dispatch-tracking/v1/depot-statistics',
        json=request,
    )

    assert response.status_code == 200
    assert response.json()['depot_statistics'] == expected_statistics

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['region_id'] == 213
    assert match_tries[0].kwargs['country_iso3'] == 'RUS'

    res = clickhouse['events'].execute(
        """
    SELECT * FROM events
        .grocery_event_bus_events_production_grocery_order_assemble_ready
             ar
           WHERE ar.depot_id = '12345'
           ORDER BY timestamp
    """,
    )
    msk = pytz.timezone('Europe/Moscow')
    res = [
        (v[0], v[1], v[2].astimezone(msk).replace(tzinfo=None)) for v in res
    ]
    assert res == [
        ('1-grocery', '12345', datetime.datetime(2021, 3, 19, 10, 0)),
        ('2-grocery', '12345', datetime.datetime(2021, 3, 19, 10, 0, 5)),
        ('3-grocery', '12345', datetime.datetime(2021, 3, 19, 10, 0, 15)),
    ]


@CALC_SPEED_CONFIG
@CLICKHOUSE_ON_CONFIG
@pytest.mark.now('2021-03-19T10:00:40+03:00')
async def test_depot_metrics_ch_empty_speed(
        taxi_grocery_dispatch_tracking,
        mockserver,
        grocery_depots,
        stq_runner,
        process_event,
        clickhouse,
        experiments3,
):

    # Make request
    request = {'legacy_depot_ids': ['non_exist_depot']}

    response = await taxi_grocery_dispatch_tracking.post(
        '/internal/grocery-dispatch-tracking/v1/depot-statistics',
        json=request,
    )

    assert response.status_code == 200
