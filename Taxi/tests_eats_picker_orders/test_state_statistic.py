import datetime
import math

import pytest


@pytest.mark.config(
    EATS_PICKER_ORDERS_STATE_STATISTIC_SETTINGS={'period_seconds': 1},
)
async def test_current_state_statistic(
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        create_order,
        get_cursor,
):
    def change_order_state(cursor, order_id, state):
        cursor.execute(
            'UPDATE eats_picker_orders.orders '
            'SET state = %s WHERE id = %s RETURNING id',
            (state, order_id),
        )
        order_id = cursor.fetchone()[0]
        return order_id

    order_id = create_order(eats_id='210402-000001', state='new')
    create_order(eats_id='210402-000002', state='waiting_dispatch')
    create_order(eats_id='210402-000003', state='waiting_dispatch')
    create_order(eats_id='210402-000004', state='dispatching')
    create_order(eats_id='210402-000005', state='assigned')
    create_order(eats_id='210402-000006', state='confirmed')
    create_order(eats_id='210402-000007', state='confirmed')
    create_order(eats_id='210402-000008', state='confirmed')
    create_order(eats_id='210402-000009', state='complete')

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')

    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )
    metrics = metrics['current_states']
    assert metrics['new'] == 1
    assert metrics['waiting_dispatch'] == 2
    assert metrics['dispatching'] == 1
    assert metrics['dispatch_failed'] == 0
    assert metrics['assigned'] == 1
    assert metrics['picking'] == 0
    assert metrics['waiting_confirmation'] == 0
    assert metrics['confirmed'] == 3
    assert metrics['picked_up'] == 0
    assert metrics['receipt_processing'] == 0
    assert metrics['receipt_rejected'] == 0
    assert metrics['paid'] == 0
    assert metrics['packing'] == 0
    assert metrics['handing'] == 0
    assert metrics['cancelled'] == 0
    assert metrics['complete'] == 1

    cursor = get_cursor()
    ret_id = change_order_state(cursor, order_id, 'dispatch_failed')
    assert ret_id == order_id

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')
    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )
    metrics = metrics['current_states']

    assert metrics['new'] == 0
    assert metrics['dispatch_failed'] == 1


@pytest.mark.config(
    EATS_PICKER_ORDERS_STATE_STATISTIC_SETTINGS={'period_seconds': 1},
)
async def test_total_state_statistic(
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        create_order,
        create_order_status,
):
    order_id_0 = create_order(eats_id='0', state='new')
    create_order_status(order_id_0, state='waiting_dispatch')
    create_order_status(order_id_0, state='dispatching')

    order_id_1 = create_order(eats_id='1', state='new')
    create_order_status(order_id_1, state='waiting_dispatch')
    create_order_status(order_id_1, state='dispatching')
    create_order_status(order_id_1, state='new')
    create_order_status(order_id_1, state='dispatching')
    create_order_status(order_id_1, state='assigned')
    create_order_status(order_id_1, state='picking')

    order_id_2 = create_order(eats_id='2', state='new')
    create_order_status(order_id_2, state='waiting_dispatch')
    create_order_status(order_id_2, state='dispatching')
    create_order_status(order_id_2, state='dispatch_failed')
    create_order_status(order_id_2, state='cancelled')

    order_id_3 = create_order(eats_id='3', state='new')
    create_order_status(order_id_3, state='waiting_dispatch')
    create_order_status(order_id_3, state='dispatching')
    create_order_status(order_id_3, state='assigned')
    create_order_status(order_id_3, state='picking')
    create_order_status(order_id_3, state='picked_up')
    create_order_status(order_id_3, state='paid')
    create_order_status(order_id_3, state='complete')

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')

    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )
    metrics = metrics['total_states']
    assert metrics['new'] == 4
    assert metrics['waiting_dispatch'] == 4
    assert metrics['dispatching'] == 4
    assert metrics['dispatch_failed'] == 1
    assert metrics['assigned'] == 2
    assert metrics['picking'] == 2
    assert metrics['waiting_confirmation'] == 0
    assert metrics['confirmed'] == 0
    assert metrics['picked_up'] == 1
    assert metrics['receipt_processing'] == 0
    assert metrics['receipt_rejected'] == 0
    assert metrics['paid'] == 1
    assert metrics['packing'] == 0
    assert metrics['handing'] == 0
    assert metrics['cancelled'] == 1
    assert metrics['complete'] == 1

    create_order_status(order_id_0, state='assigned')

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')
    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )
    metrics = metrics['total_states']

    assert metrics['assigned'] == 3


@pytest.mark.config(
    EATS_PICKER_ORDERS_STATE_STATISTIC_SETTINGS={'period_seconds': 1},
)
async def test_time_before_picking(
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        create_order,
        create_order_status,
):
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        seconds=180,
    )
    order_id1 = create_order(
        eats_id='210823-000001', state='new', created_at=now,
    )
    order_id2 = create_order(
        eats_id='210823-000002', state='new', created_at=now,
    )
    order_id3 = create_order(
        eats_id='210823-000003', state='new', created_at=now,
    )
    order_id4 = create_order(
        eats_id='210823-000004', state='new', created_at=now,
    )

    create_order_status(
        order_id=order_id1, state='dispatch_failed', created_at=now,
    )
    create_order_status(
        order_id=order_id2,
        state='picking',
        created_at=now + datetime.timedelta(seconds=60),
    )
    create_order_status(
        order_id=order_id3,
        state='picking',
        created_at=now + datetime.timedelta(seconds=120),
    )
    create_order_status(
        order_id=order_id4,
        state='picking',
        created_at=now + datetime.timedelta(seconds=150),
    )

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')
    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )

    assert math.isclose(
        metrics['time_before_picking_avg'], 110.0, abs_tol=0.00001,
    )
    assert math.isclose(
        metrics['time_before_picking_median'], 120.0, abs_tol=0.00001,
    )


@pytest.mark.config(
    EATS_PICKER_ORDERS_STATE_STATISTIC_SETTINGS={'period_seconds': 1},
)
async def test_time_before_terminated(
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        create_order,
        create_order_status,
):
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        seconds=180,
    )
    order_id1 = create_order(
        eats_id='210823-000001', state='picking', created_at=now,
    )
    order_id2 = create_order(
        eats_id='210823-000002', state='picking', created_at=now,
    )
    order_id3 = create_order(
        eats_id='210823-000003', state='picking', created_at=now,
    )

    create_order_status(
        order_id=order_id1,
        state='picking',
        created_at=now + datetime.timedelta(seconds=30),
    )
    create_order_status(
        order_id=order_id2,
        state='picking',
        created_at=now + datetime.timedelta(seconds=60),
    )
    create_order_status(
        order_id=order_id3,
        state='picking',
        created_at=now + datetime.timedelta(seconds=70),
    )
    create_order_status(
        order_id=order_id1,
        state='cancelled',
        created_at=now + datetime.timedelta(seconds=120),
    )
    create_order_status(
        order_id=order_id2,
        state='complete',
        created_at=now + datetime.timedelta(seconds=120),
    )
    create_order_status(
        order_id=order_id3,
        state='complete',
        created_at=now + datetime.timedelta(seconds=120),
    )

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')
    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )

    assert math.isclose(
        metrics['time_before_terminated_avg'], 66.6, abs_tol=0.1,
    )

    assert math.isclose(
        metrics['time_before_terminated_median'], 60.0, abs_tol=0.00001,
    )


def create_order_items(
        create_order_item, order_id, items_count, first_id=1, version=0,
):
    items = []
    for i in range(first_id, first_id + items_count):
        items.append(
            create_order_item(
                order_id=order_id, eats_item_id=f'item{i}', version=version,
            ),
        )
    return items


def create_picked_items(create_picked_item, items, eats_id, picked_count):
    for i in range(0, picked_count):
        create_picked_item(order_item_id=items[i], eats_id=eats_id)


@pytest.mark.config(
    EATS_PICKER_ORDERS_STATE_STATISTIC_SETTINGS={'period_seconds': 1},
)
async def test_picking_fullness(
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        create_order,
        create_order_status,
        create_order_item,
        create_picked_item,
        init_measure_units,
        init_currencies,
):
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        seconds=180,
    )
    order_id1 = create_order(
        eats_id='210823-000001', state='complete', created_at=now,
    )
    create_order_status(order_id=order_id1, state='paid')

    order_id2 = create_order(
        eats_id='210823-000002', state='complete', created_at=now,
    )
    create_order_status(order_id=order_id2, state='paid')

    order_id3 = create_order(
        eats_id='210823-000003', state='complete', created_at=now,
    )
    create_order_status(order_id=order_id3, state='paid')

    order_items1 = create_order_items(
        create_order_item, order_id=order_id1, items_count=10,
    )
    order_items2 = create_order_items(
        create_order_item, order_id=order_id2, items_count=10, first_id=11,
    )
    order_items3 = create_order_items(
        create_order_item, order_id=order_id3, items_count=10, first_id=21,
    )
    create_picked_items(
        create_picked_item,
        items=order_items1,
        eats_id='210823-000001',
        picked_count=3,
    )
    create_picked_items(
        create_picked_item,
        items=order_items2,
        eats_id='210823-000002',
        picked_count=5,
    )
    create_picked_items(
        create_picked_item,
        items=order_items3,
        eats_id='210823-000003',
        picked_count=10,
    )

    await taxi_eats_picker_orders.run_task('periodic-state-statistic-task')
    metrics = await taxi_eats_picker_orders_monitor.get_metric(
        'periodic-state-statistic',
    )

    assert math.isclose(metrics['picking_fullness_avg'], 0.6, abs_tol=0.00001)
    assert math.isclose(
        metrics['picking_fullness_median'], 0.5, abs_tol=0.00001,
    )
