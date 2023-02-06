import datetime

import pytest

from . import utils


@pytest.mark.now('2020-12-21T17:30:00.00+00:00')
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@utils.queue_length_config3(offset=20)
async def test_queue_length(
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        now_utc,
        experiments3,
        mocked_time,
):
    """
      В тесте в очередь магазина отдаются заказы, которые находятся в статусах
      new, waiting_dispatch, dispatching. Из ответа удаляется заказ ко времени,
      который необходимо начать собирать более, чем 20 минут после now
    """

    experiments3.add_config(**utils.picking_in_advance_settings(True, 1, True))

    place_ids = environment.create_places(2)
    picker_orders = []
    for place_id in place_ids:
        create_place(
            place_id,
            working_intervals=[
                (now_utc(), now_utc() + datetime.timedelta(hours=8)),
            ],
        )
        picker_ids = environment.create_pickers(place_id, count=6)

        statuses = [
            'new',
            'waiting_dispatch',
            'dispatching',
            'assigned',
            'picking',
        ]
        orders = [
            environment.create_orders(
                place_id,
                count=1,
                created_at=utils.to_string(
                    now_utc() - datetime.timedelta(minutes=10 * i),
                ),
                status=statuses[i - 1],
                status_updated_at=utils.to_string(
                    now_utc() - datetime.timedelta(minutes=10 * i),
                ),
                estimated_picking_time=600 * i,
            )[0]
            for i in range(1, 6)
        ]

        orders[0]['is_asap'] = False
        orders[0]['estimated_delivery_time'] = utils.to_string(
            now_utc() + datetime.timedelta(minutes=70, microseconds=1),
        )
        environment.assign_picker_order(picker_ids[0], orders[3])
        environment.start_picking_order(picker_ids[1], orders[4])

        picker_orders.extend(orders)

    mocked_time.sleep(600)
    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/places/queue-length',
        json={'place_ids': list(map(str, place_ids))},
    )
    assert response.status == 200

    orders = response.json()['orders']
    orders = sorted(orders, key=lambda order: order['eats_id'])
    assert orders == [
        {
            'eats_id': '201221-000001',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 1200,
            'place_id': '0',
            'remaining_picking_time': 1200,
            'status': 'waiting_dispatch',
            'status_created_at': '2020-12-21T17:10:00+00:00',
        },
        {
            'eats_id': '201221-000002',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 1800,
            'place_id': '0',
            'remaining_picking_time': 1800,
            'status': 'dispatching',
            'status_created_at': '2020-12-21T17:00:00+00:00',
        },
        {
            'eats_id': '201221-000003',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 2400,
            'place_id': '0',
            'remaining_picking_time': 2400,
            'status': 'assigned',
            'status_created_at': '2020-12-21T17:30:00+00:00',
        },
        {
            'eats_id': '201221-000004',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 3000,
            'place_id': '0',
            'remaining_picking_time': 2400,
            'status': 'picking',
            'status_created_at': '2020-12-21T17:30:00+00:00',
        },
        {
            'eats_id': '201221-000006',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 1200,
            'place_id': '1',
            'remaining_picking_time': 1200,
            'status': 'waiting_dispatch',
            'status_created_at': '2020-12-21T17:10:00+00:00',
        },
        {
            'eats_id': '201221-000007',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 1800,
            'place_id': '1',
            'remaining_picking_time': 1800,
            'status': 'dispatching',
            'status_created_at': '2020-12-21T17:00:00+00:00',
        },
        {
            'eats_id': '201221-000008',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 2400,
            'place_id': '1',
            'remaining_picking_time': 2400,
            'status': 'assigned',
            'status_created_at': '2020-12-21T17:30:00+00:00',
        },
        {
            'eats_id': '201221-000009',
            'estimated_dispatch_attempt_time': '2020-12-21T17:40:00+00:00',
            'estimated_picking_time': 3000,
            'place_id': '1',
            'remaining_picking_time': 2400,
            'status': 'picking',
            'status_created_at': '2020-12-21T17:30:00+00:00',
        },
    ]

    places_load_info = response.json()['places_load_info']
    places_load_info = sorted(
        places_load_info,
        key=lambda place_load_info: place_load_info['place_id'],
    )
    assert places_load_info == [
        {
            'brand_id': 1,
            'city': 'Москва',
            'country_id': 1,
            'enabled': True,
            'estimated_waiting_time': 0,
            'free_pickers_count': 3,
            'is_place_closed': False,
            'is_place_overloaded': False,
            'place_id': 0,
            'region_id': 1,
            'time_zone': 'Europe/Moscow',
            'total_pickers_count': 6,
            'working_intervals': [
                {
                    'end': '2020-12-22T01:30:00+00:00',
                    'start': '2020-12-21T17:30:00+00:00',
                },
            ],
        },
        {
            'brand_id': 1,
            'city': 'Москва',
            'country_id': 1,
            'enabled': True,
            'estimated_waiting_time': 0,
            'free_pickers_count': 3,
            'is_place_closed': False,
            'is_place_overloaded': False,
            'place_id': 1,
            'region_id': 1,
            'time_zone': 'Europe/Moscow',
            'total_pickers_count': 6,
            'working_intervals': [
                {
                    'end': '2020-12-22T01:30:00+00:00',
                    'start': '2020-12-21T17:30:00+00:00',
                },
            ],
        },
    ]
