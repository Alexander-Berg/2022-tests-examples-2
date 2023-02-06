# pylint: disable=too-many-lines
import datetime

import pytest

from . import utils


PERIODIC_NAME = 'picking-estimations-updater'
DB_ORDERS_UPDATE_OFFSET = 5


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_empty_db(
        taxi_eats_eta, db_select_orders, redis_store,
):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == []
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_no_orders_to_update(
        taxi_eats_eta,
        make_order,
        db_insert_order,
        db_select_orders,
        redis_store,
):
    orders = (
        [make_order(order_type='native', order_status='confirmed')]
        + [
            make_order(
                order_type='retail',
                order_status=order_status,
                picking_status='picking',
            )
            for order_status in (
                'taken',
                'cancelled',
                'complete',
                'auto_complete',
            )
        ]
        + [
            make_order(
                order_type='retail',
                order_status='confirmed',
                picking_status=picking_status,
            )
            for picking_status in ('cancelled', 'complete')
        ]
    )
    for i, order in enumerate(orders):
        order['id'] = i
        order['order_nr'] = f'order_nr-{i}'
        db_insert_order(order)
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == orders
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_no_picker_order_requests(
        taxi_eats_eta,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(order_type='shop', order_status='confirmed'),
        make_order(
            order_type='retail',
            order_status='created',
            picking_status='picking',
        ),
    ]
    for i, order in enumerate(orders):
        order['id'] = i
        order['order_nr'] = f'order_nr-{i}'
        db_insert_order(order)
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == orders
    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        picking_duration = datetime.timedelta(
            seconds=utils.FALLBACKS['picking_duration'],
        )
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['created_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
    retail_info_synchronizer_tasks_count=2,
)
@utils.eats_eta_fallbacks_config3(picking_queue_length=42)
async def test_picking_estimations_updater_update_order_picking_only(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET + 1),
            order_type='retail',
            order_status='sent',
        )
        for i in range(4)
    ]
    for order in orders:
        db_insert_order(order)

        status = 'new'
        flow_type = 'picking_only'
        picker_order = load_json('picker_order.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        ) + datetime.timedelta(seconds=42)
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == len(orders)
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        picking_duration = utils.trunc_timedelta(
            max(
                (
                    now_utc
                    + datetime.timedelta(
                        seconds=utils.FALLBACKS['minimal_remaining_duration'],
                    )
                    - order['picking_starts_at']
                ),
                order['picking_duration'],
            ),
        )
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(
    picker_waiting_time=42, picker_dispatching_time=13,
)
async def test_picking_estimations_updater_update_order_waiting_for_dispatch(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='sent',
        )
        for i in range(3)
    ]
    for i, order in enumerate(orders):
        db_insert_order(order)

        status = ['new', 'waiting_dispatch', 'dispatch_failed'][i]
        flow_type = 'picking_packing'
        picker_order = load_json('picker_order.json')
        place_load = load_json('place_load.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = (
            now_utc
            + datetime.timedelta(seconds=place_load['estimated_waiting_time'])
            + datetime.timedelta(seconds=42 + 13)
        )
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 3
    assert pickers.mock_dispatch_preceding_load.times_called == 3
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'], 'picking_duration', order['picking_duration'],
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + order['picking_duration'],
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(
    picker_waiting_time=42, picker_dispatching_time=13,
)
async def test_picking_estimations_updater_update_order_dispatching(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='sent',
        )
        for i in range(3)
    ]
    for i, order in enumerate(orders):
        db_insert_order(order)

        status = 'dispatching'
        flow_type = 'picking_packing'
        picker_order = load_json('picker_order.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = now_utc + datetime.timedelta(
            seconds=42 + 13,
        )
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 3
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'], 'picking_duration', order['picking_duration'],
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + order['picking_duration'],
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(picker_waiting_time=42)
async def test_picking_estimations_updater_update_order_assigned(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='confirmed',
        )
        for i in range(4)
    ]
    for order in orders:
        db_insert_order(order)

        status = 'assigned'
        flow_type = 'picking_packing'
        picker_order = load_json('picker_order.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = datetime.datetime.fromisoformat(
            picker_order['status_updated_at'],
        ) + datetime.timedelta(seconds=42)
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 4
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        picking_duration = utils.trunc_timedelta(
            max(
                (
                    now_utc
                    + datetime.timedelta(
                        seconds=utils.FALLBACKS['minimal_remaining_duration'],
                    )
                    - order['picking_starts_at']
                ),
                order['picking_duration'],
            ),
        )
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_update_order_picking(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='confirmed',
            picking_duration=datetime.timedelta(seconds=-1),
            picking_starts_at=now_utc,
            picking_duration_updated_at=now_utc
            - datetime.timedelta(seconds=1),
            picking_start_updated_at=now_utc - datetime.timedelta(seconds=1),
        )
        for i in range(3)
    ]
    for i, order in enumerate(orders):
        db_insert_order(order)

        status = ['picking', 'waiting_confirmation', 'confirmed'][i]
        flow_type = 'picking_packing'
        picker_order = load_json('picker_order.json')
        status_time = load_json('status_time.json')
        estimate = load_json('estimate.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = datetime.datetime.fromisoformat(
            status_time['status_change_timestamp'],
        )
        order['picking_duration'] = (
            now_utc
            + datetime.timedelta(seconds=estimate['eta_seconds'])
            - order['picking_starts_at']
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 3
    assert pickers.mock_picker_orders_status_time.times_called == 3
    assert pickers.mock_picker_orders_cart.times_called == 3
    assert pickers.mock_picker_time_estimate.times_called == 3
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        picking_duration = utils.trunc_timedelta(order['picking_duration'])
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_update_order_picking_empty_cart(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='confirmed',
        )
        for i in range(3)
    ]

    del pickers.cart['created_at']
    pickers.cart['picker_items'].clear()

    for i, order in enumerate(orders):
        db_insert_order(order)

        status = ['picking', 'waiting_confirmation', 'confirmed'][i]
        flow_type = 'picking_packing'
        picker_order = load_json('picker_order.json')
        status_time = load_json('status_time.json')
        estimate = load_json('estimate.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = datetime.datetime.fromisoformat(
            status_time['status_change_timestamp'],
        )
        order['picking_duration'] = (
            now_utc
            + datetime.timedelta(seconds=estimate['eta_seconds'])
            - order['picking_starts_at']
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 3
    assert pickers.mock_picker_orders_status_time.times_called == 3
    assert pickers.mock_picker_orders_cart.times_called == 3
    assert pickers.mock_picker_time_estimate.times_called == 3
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        picking_duration = utils.trunc_timedelta(order['picking_duration'])
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_update_order_picked(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    picking_statuses = [
        'picked_up',
        'receipt_processing',
        'receipt_rejected',
        'paid',
        'packing',
        'handing',
        'complete',
    ]
    orders = [
        make_order(
            id=i,
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='confirmed',
        )
        for i in range(len(picking_statuses))
    ]
    for i, order in enumerate(orders):
        db_insert_order(order)

        picking_status = picking_statuses[i]
        flow_type = 'picking_handing'
        picker_order = load_json('picker_order.json')
        status_time = load_json('status_time.json')

        pickers.add_order(
            order_nr=order['order_nr'],
            status=picking_status,
            flow_type=flow_type,
        )

        order['picking_status'] = picking_status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_start_updated_at'] = now_utc
        order['picking_starts_at'] = datetime.datetime.fromisoformat(
            status_time['status_change_timestamp'],
        )
        order['picking_duration'] = (
            datetime.datetime.fromisoformat(picker_order['status_updated_at'])
            - datetime.datetime.fromisoformat(
                status_time['status_change_timestamp'],
            )
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == len(orders)
    assert pickers.mock_picker_orders_status_time.times_called == len(orders)
    assert db_select_orders() == orders

    for order in orders:
        if order['picking_status'] == 'complete':
            picking_duration = utils.trunc_timedelta(order['picking_duration'])
        else:
            picking_duration = max(
                utils.trunc_timedelta(now_utc - order['picking_starts_at'])
                + datetime.timedelta(
                    seconds=utils.FALLBACKS['minimal_remaining_duration'],
                ),
                datetime.timedelta(
                    seconds=utils.FALLBACKS['picking_duration'],
                ),
            )
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['picking_starts_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_update_order_cancelled(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    order = make_order(
        id=1,
        order_nr='order_nr-1',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='confirmed',
    )
    db_insert_order(order)

    picking_status = 'cancelled'
    flow_type = 'picking_handing'
    picker_order = load_json('picker_order.json')

    pickers.add_order(
        order_nr=order['order_nr'], status=picking_status, flow_type=flow_type,
    )

    order['picking_status'] = picking_status
    order['picking_flow_type'] = flow_type
    order['retail_order_created_at'] = datetime.datetime.fromisoformat(
        picker_order['created_at'],
    )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 0
    assert db_select_orders() == [order]

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'], 'picking_duration', order['picking_duration'],
    )
    check_redis_value(order['order_nr'], 'picked_up_at', None)


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_picking_estimations_updater_missing_picking_starts_at(
        taxi_eats_eta,
        mockserver,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    orders = [
        make_order(
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            order_type='retail',
            order_status='confirmed',
        ),
    ]
    for order in orders:
        db_insert_order(order)

        status = 'complete'
        flow_type = 'picking_handing'
        picker_order = load_json('picker_order.json')

        pickers.add_order(
            order_nr=order['order_nr'], status=status, flow_type=flow_type,
        )

        order['picking_status'] = status
        order['picking_flow_type'] = flow_type
        order['retail_order_created_at'] = datetime.datetime.fromisoformat(
            picker_order['created_at'],
        )
        order['picking_duration_updated_at'] = now_utc
        order['picking_duration'] = (
            utils.parse_datetime(picker_order['status_updated_at'])
            - order['retail_order_created_at']
        )

    @mockserver.json_handler('/eats-picker-orders/api/v1/orders/status-time')
    def mock_picker_orders_status_time(request):
        assert request.method == 'POST'
        return mockserver.make_response(status=200, json={'timestamps': []})

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert mock_picker_orders_status_time.times_called == 1
    assert db_select_orders() == orders

    for order in orders:
        picking_duration = utils.trunc_timedelta(order['picking_duration'])
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'], 'picking_duration', picking_duration,
        )
        check_redis_value(
            order['order_nr'],
            'picked_up_at',
            order['retail_order_created_at'] + picking_duration,
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@pytest.mark.parametrize(
    'picking_status', ['new', 'waiting_dispatch', 'dispatching', 'assigned'],
)
async def test_picking_estimations_updater_no_fallbacks_no_update(
        taxi_eats_eta,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_status,
        redis_store,
):
    order = make_order(
        id=1,
        order_nr='order_nr',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
        picking_status=picking_status,
        picking_starts_at=now_utc + datetime.timedelta(days=1),
        picking_start_updated_at=now_utc - datetime.timedelta(days=1),
    )

    db_insert_order(order)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == [order]

    assert not redis_store.keys()


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'picking_duration', [None, datetime.timedelta(seconds=-1)],
)
async def test_picking_estimations_updater_no_brand_id_keep_picking_duration(
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_duration,
        check_redis_value,
):
    picking_status = 'picking'
    order = make_order(
        id=1,
        order_nr='order_nr',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
        picking_status=picking_status,
        picking_starts_at=now_utc + datetime.timedelta(days=1),
        picking_start_updated_at=now_utc - datetime.timedelta(days=1),
    )
    if picking_duration is not None:
        order['picking_duration'] = picking_duration
        order['picking_duration_updated_at'] = now_utc - datetime.timedelta(
            days=1,
        )

    db_insert_order(order)

    flow_type = 'picking_packing'
    picker_order = load_json('picker_order.json')
    status_time = load_json('status_time.json')
    pickers.add_order(
        order_nr=order['order_nr'],
        status=picking_status,
        flow_type=flow_type,
        brand_id=None,
    )

    order['picking_flow_type'] = flow_type
    order['retail_order_created_at'] = datetime.datetime.fromisoformat(
        picker_order['created_at'],
    )
    order['picking_starts_at'] = datetime.datetime.fromisoformat(
        status_time['status_change_timestamp'],
    )
    order['picking_start_updated_at'] = now_utc
    if picking_duration is None:
        order['picking_duration_updated_at'] = now_utc
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert pickers.mock_picker_orders_cart.times_called == 0
    assert pickers.mock_picker_time_estimate.times_called == 0
    assert db_select_orders() == [order]

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])

    picking_duration = max(
        utils.trunc_timedelta(now_utc - order['picking_starts_at'])
        + datetime.timedelta(
            seconds=utils.FALLBACKS['minimal_remaining_duration'],
        ),
        datetime.timedelta(seconds=utils.FALLBACKS['picking_duration']),
    )
    check_redis_value(order['order_nr'], 'picking_duration', picking_duration)
    check_redis_value(
        order['order_nr'],
        'picked_up_at',
        order['picking_starts_at'] + picking_duration,
    )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'picking_duration', [None, datetime.timedelta(seconds=-1)],
)
async def test_picking_estimations_updater_cart_error_keep_picking_duration(
        mockserver,
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_duration,
        check_redis_value,
):
    picking_status = 'picking'
    order = make_order(
        id=1,
        order_nr='order_nr',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
        picking_status=picking_status,
        picking_starts_at=now_utc + datetime.timedelta(days=1),
        picking_start_updated_at=now_utc - datetime.timedelta(days=1),
    )
    if picking_duration is not None:
        order['picking_duration'] = picking_duration
        order['picking_duration_updated_at'] = now_utc - datetime.timedelta(
            days=1,
        )

    db_insert_order(order)

    flow_type = 'picking_packing'
    picker_order = load_json('picker_order.json')
    status_time = load_json('status_time.json')
    pickers.add_order(
        order_nr=order['order_nr'], status=picking_status, flow_type=flow_type,
    )

    order['picking_flow_type'] = flow_type
    order['retail_order_created_at'] = datetime.datetime.fromisoformat(
        picker_order['created_at'],
    )
    order['picking_starts_at'] = datetime.datetime.fromisoformat(
        status_time['status_change_timestamp'],
    )
    order['picking_start_updated_at'] = now_utc
    if picking_duration is None:
        order['picking_duration_updated_at'] = now_utc
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/cart')
    def mock_picker_orders_cart(request):
        return mockserver.make_response(status=400)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert mock_picker_orders_cart.times_called == 1
    assert pickers.mock_picker_time_estimate.times_called == 0
    assert db_select_orders() == [order]

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])

    picking_duration = max(
        utils.trunc_timedelta(now_utc - order['picking_starts_at'])
        + datetime.timedelta(
            seconds=utils.FALLBACKS['minimal_remaining_duration'],
        ),
        datetime.timedelta(seconds=utils.FALLBACKS['picking_duration']),
    )
    check_redis_value(order['order_nr'], 'picking_duration', picking_duration)
    check_redis_value(
        order['order_nr'],
        'picked_up_at',
        order['picking_starts_at'] + picking_duration,
    )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'picking_duration', [None, datetime.timedelta(seconds=-1)],
)
async def test_picking_estimations_updater_picking_time_estimator_error(
        mockserver,
        taxi_eats_eta,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_duration,
        check_redis_value,
):
    picking_status = 'picking'
    order = make_order(
        id=1,
        order_nr='order_nr',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
        picking_status=picking_status,
        picking_starts_at=now_utc + datetime.timedelta(days=1),
        picking_start_updated_at=now_utc - datetime.timedelta(days=1),
    )
    if picking_duration is not None:
        order['picking_duration'] = picking_duration
        order['picking_duration_updated_at'] = now_utc - datetime.timedelta(
            days=1,
        )

    db_insert_order(order)

    flow_type = 'picking_packing'
    picker_order = load_json('picker_order.json')
    status_time = load_json('status_time.json')
    pickers.add_order(
        order_nr=order['order_nr'], status=picking_status, flow_type=flow_type,
    )

    order['picking_flow_type'] = flow_type
    order['retail_order_created_at'] = datetime.datetime.fromisoformat(
        picker_order['created_at'],
    )
    order['picking_starts_at'] = datetime.datetime.fromisoformat(
        status_time['status_change_timestamp'],
    )
    order['picking_start_updated_at'] = now_utc
    if picking_duration is None:
        order['picking_duration_updated_at'] = now_utc
        order['picking_duration'] = datetime.timedelta(
            seconds=picker_order['estimated_picking_time'],
        )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/order/estimate',
    )
    def mock_picker_time_estimate(request):
        return mockserver.make_response(status=400)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert pickers.mock_picker_orders_cart.times_called == 1
    assert mock_picker_time_estimate.times_called == 1
    assert db_select_orders() == [order]

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    picking_duration = max(
        utils.trunc_timedelta(now_utc - order['picking_starts_at'])
        + datetime.timedelta(
            seconds=utils.FALLBACKS['minimal_remaining_duration'],
        ),
        datetime.timedelta(seconds=utils.FALLBACKS['picking_duration']),
    )
    check_redis_value(order['order_nr'], 'picking_duration', picking_duration)
    check_redis_value(
        order['order_nr'],
        'picked_up_at',
        order['picking_starts_at'] + picking_duration,
    )
