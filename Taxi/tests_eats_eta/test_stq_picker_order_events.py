import datetime

import pytest

from . import utils


PAYLOAD_STATUS_CHANGE = {
    'event_type': 'STATUS_CHANGE',
    'order_status': 'assigned',
    'order_nr': 'order_nr_0',
    'place_id': '42',
    'customer_id': None,
    'picker_id': 'picker_id_0',
    'customer_picker_phone_forwarding': None,
}
DB_ORDERS_UPDATE_OFFSET = 5


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_stq_picker_order_events_empty_db(stq_runner, db_select_orders):
    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert db_select_orders() == []


@utils.eats_eta_fallbacks_config3(picking_queue_length=42)
async def test_stq_picker_order_events_update_order_picking_only(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET + 1),
        order_type='retail',
        order_status='sent',
    )
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3(
    picker_waiting_time=42, picker_dispatching_time=13,
)
@pytest.mark.parametrize(
    'status', ['new', 'waiting_dispatch', 'dispatch_failed'],
)
async def test_stq_picker_order_events_update_order_waiting_for_dispatch(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        status,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
    )
    db_insert_order(order)

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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_dispatch_preceding_load.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3(
    picker_waiting_time=42, picker_dispatching_time=13,
)
async def test_stq_picker_order_events_update_order_dispatching(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
    )
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
    order['picking_starts_at'] = now_utc + datetime.timedelta(seconds=42 + 13)
    order['picking_duration'] = datetime.timedelta(
        seconds=picker_order['estimated_picking_time'],
    )

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3(picker_waiting_time=42)
async def test_stq_picker_order_events_update_order_assigned(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='confirmed',
    )
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'status', ['picking', 'waiting_confirmation', 'confirmed'],
)
async def test_stq_picker_order_events_update_order_picking(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        status,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='confirmed',
    )

    db_insert_order(order)

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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert pickers.mock_picker_orders_cart.times_called == 1
    assert pickers.mock_picker_time_estimate.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'status', ['picking', 'waiting_confirmation', 'confirmed'],
)
async def test_stq_picker_order_events_update_order_picking_empty_cart(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        status,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='confirmed',
    )

    del pickers.cart['created_at']
    pickers.cart['picker_items'].clear()

    db_insert_order(order)

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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert pickers.mock_picker_orders_cart.times_called == 1
    assert pickers.mock_picker_time_estimate.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'status',
    [
        'picked_up',
        'receipt_processing',
        'receipt_rejected',
        'paid',
        'packing',
        'handing',
        'complete',
    ],
)
async def test_stq_picker_order_events_update_order_picked(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        status,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='confirmed',
    )
    db_insert_order(order)

    flow_type = 'picking_handing'
    picker_order = load_json('picker_order.json')
    status_time = load_json('status_time.json')

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
    order['picking_duration'] = datetime.datetime.fromisoformat(
        picker_order['status_updated_at'],
    ) - datetime.datetime.fromisoformat(status_time['status_change_timestamp'])

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
async def test_stq_picker_order_events_update_order_cancelled(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order = make_order(
        id=1,
        order_nr='order_nr_0',
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 0
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
async def test_stq_picker_order_events_update_order_missing_picking_starts_at(
        stq_runner,
        mockserver,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order = make_order(
        id=1,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='confirmed',
    )
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert mock_picker_orders_status_time.times_called == 1
    assert db_select_orders() == [order]


@pytest.mark.parametrize(
    'picking_status', ['new', 'waiting_dispatch', 'dispatching', 'assigned'],
)
async def test_stq_picker_order_events_no_fallbacks_keep_picking_start(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_status,
):
    order = make_order(
        id=0,
        order_nr='order_nr_0',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        order_type='retail',
        order_status='sent',
        picking_status=picking_status,
        picking_starts_at=now_utc + datetime.timedelta(days=1),
        picking_start_updated_at=now_utc - datetime.timedelta(days=1),
    )

    db_insert_order(order)

    flow_type = 'picking_packing'
    picker_order = load_json('picker_order.json')

    pickers.add_order(
        order_nr=order['order_nr'], status=picking_status, flow_type=flow_type,
    )

    order['picking_flow_type'] = flow_type
    order['retail_order_created_at'] = datetime.datetime.fromisoformat(
        picker_order['created_at'],
    )
    order['picking_duration_updated_at'] = now_utc
    order['picking_duration'] = datetime.timedelta(
        seconds=picker_order['estimated_picking_time'],
    )

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 0
    assert pickers.mock_picker_orders_cart.times_called == 0
    assert pickers.mock_picker_time_estimate.times_called == 0
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'picking_duration', [None, datetime.timedelta(seconds=-1)],
)
async def test_stq_picker_order_eventsr_no_brand_id_keep_picking_duration(
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_duration,
):
    picking_status = 'picking'
    order = make_order(
        id=0,
        order_nr='order_nr_0',
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id='order_nr_0', kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert pickers.mock_picker_orders_cart.times_called == 0
    assert pickers.mock_picker_time_estimate.times_called == 0
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'picking_duration', [None, datetime.timedelta(seconds=-1)],
)
async def test_stq_picker_order_events_cart_error_keep_picking_duration(
        mockserver,
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_duration,
):
    picking_status = 'picking'
    order = make_order(
        id=1,
        order_nr='order_nr_0',
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id=order['order_nr'], kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert mock_picker_orders_cart.times_called == 1
    assert pickers.mock_picker_time_estimate.times_called == 0
    assert db_select_orders() == [order]


@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'picking_duration', [None, datetime.timedelta(seconds=-1)],
)
async def test_stq_picker_order_events_picking_time_estimator_error(
        mockserver,
        stq_runner,
        load_json,
        now_utc,
        pickers,
        make_order,
        db_insert_order,
        db_select_orders,
        picking_duration,
):
    picking_status = 'picking'
    order = make_order(
        id=1,
        order_nr='order_nr_0',
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

    await stq_runner.eats_eta_picker_order_events.call(
        task_id=order['order_nr'], kwargs=PAYLOAD_STATUS_CHANGE,
    )
    assert pickers.mock_picker_orders_get_order.times_called == 1
    assert pickers.mock_picker_orders_status_time.times_called == 1
    assert pickers.mock_picker_orders_cart.times_called == 1
    assert mock_picker_time_estimate.times_called == 1
    assert db_select_orders() == [order]
