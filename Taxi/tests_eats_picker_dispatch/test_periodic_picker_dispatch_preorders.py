import datetime
import math

import pytest

from . import utils

PERIODIC_NAME = 'periodic-picker-dispatcher'


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize(
    'timeshift, orders_count', [(0, 1), (1, 0), (-3600, 2)],
)
async def test_dispatch_preorders_timeshift(
        taxi_eats_picker_dispatch,
        stq,
        environment,
        now,
        create_place,
        experiments3,
        timeshift,
        orders_count,
):
    experiments3.add_config(**utils.timeshift_exp3(timeshift))
    await taxi_eats_picker_dispatch.invalidate_caches()

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    environment.create_pickers(place_id, count=2)
    orders = environment.create_orders(
        place_id, count=2, is_asap=False, estimated_picking_time=1800,
    )
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )
        order['estimated_delivery_time'] = utils.to_string(
            now + datetime.timedelta(minutes=(60 * i)),
        )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == orders_count
    for i in range(0, orders_count):
        call_info = stq.eats_picker_assign.next_call()
        assert call_info['id'] == orders[i]['eats_id']
    assert environment.mock_eats_eta_orders_estimate.times_called == 1


@pytest.mark.now
@utils.periodic_dispatcher_config3()
async def test_dispatch_preorders_sorting(
        taxi_eats_picker_dispatch,
        stq,
        environment,
        now,
        create_place,
        experiments3,
):
    experiments3.add_config(
        name='eats_picker_dispatch_timeshift',
        match={
            'consumers': [{'name': 'eats-picker-dispatch/timeshift'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'elapsed_duration',
                        'arg_type': 'int',
                        'value': 3600,
                    },
                    'type': 'eq',
                },
                'title': '1',
                'value': {'timeshift': -3601},
                'enabled': True,
                'extension_method': 'replace',
            },
        ],
        default_value={'timeshift': 0},
    )
    await taxi_eats_picker_dispatch.invalidate_caches()

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    environment.create_pickers(place_id, count=2)

    orders = environment.create_orders(
        place_id, count=2, estimated_picking_time=1800,
    )
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )
        order['estimated_delivery_time'] = utils.to_string(
            now + datetime.timedelta(minutes=(60 * i)),
        )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 2
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == orders[1]['eats_id']
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == orders[0]['eats_id']
    assert environment.mock_eats_eta_orders_estimate.times_called == 1


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize(
    'picking_duration, delivery_duration, orders_count',
    [(1800, 1800, 1), (1800, 1799, 0)],
)
@pytest.mark.parametrize(
    'use_eta_for_picking, use_eta_for_delivery, use_initial_picking_duration',
    [
        (False, False, True),
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (True, True, False),
    ],
)
@pytest.mark.config(EATS_PICKER_DISPATCH_ETA_SETTINGS={'batch_size': 1})
@pytest.mark.parametrize(
    'cart_file', ['cart_stub.json', 'empty_cart_stub.json'],
)
async def test_dispatch_preorders_eta_fallbacks(
        taxi_eats_picker_dispatch,
        load_json,
        stq,
        environment,
        now,
        create_place,
        experiments3,
        picking_duration,
        delivery_duration,
        orders_count,
        mockserver,
        use_eta_for_picking,
        use_eta_for_delivery,
        use_initial_picking_duration,
        cart_file,
        taxi_config,
):

    taxi_config.set_values(
        {
            'EATS_PICKER_DISPATCH_PICKING_DURATION_FALLBACK_SETTINGS': {
                'time_estimator_tasks_count': 1,
                'time_estimator_batch_size': 1,
                'estimation_orders_tasks_count': 1,
                'estimation_orders_batch_size': 1,
            },
        },
    )

    experiments3.add_config(
        **utils.use_eta_config(
            use_eta_for_picking,
            use_eta_for_delivery,
            use_initial_picking_duration,
        ),
    )
    await taxi_eats_picker_dispatch.invalidate_caches()

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    (picker, _) = environment.create_pickers(place_id, count=2)
    (order, picking_order) = environment.create_orders(
        place_id,
        count=2,
        is_asap=False,
        estimated_picking_time=picking_duration,
    )
    order['created_at'] = utils.to_string(now)
    order['estimated_delivery_time'] = utils.to_string(
        now + datetime.timedelta(minutes=60),
    )
    environment.start_picking_order(picker, picking_order)

    @mockserver.json_handler('/eats-eta/v1/eta/orders/estimate')
    def eats_eta_orders_estimate(_):
        raise mockserver.TimeoutError()

    experiments3.add_config(
        **utils.delivery_duration_fallback(delivery_duration),
    )

    cart = load_json(cart_file)

    @mockserver.json_handler('/eats-picker-orders/api/v1/estimation-orders')
    async def mock_estimation_orders(request):
        is_picking = request.json['eats_ids'] == picking_order['eats_id']
        return mockserver.make_response(
            status=200,
            json={
                'estimation_orders': [
                    {
                        'eats_id': (
                            picking_order['eats_id']
                            if is_picking
                            else order['eats_id']
                        ),
                        'place_id': picking_order['place_id'],
                        'flow_type': picking_order['flow_type'],
                        'state': 'picking' if is_picking else 'new',
                        'items': [
                            {
                                'category_id': 'category-id',
                                'is_catch_weight': True,
                                'count': None,
                            },
                        ],
                        'picked_items': (
                            cart['picker_items'] if is_picking else []
                        ),
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/orders/estimate',
    )
    async def mock_order_estimate(request):
        estimations = []
        for request_order in request.json['orders']:
            if (
                    request_order['eats_id'] == picking_order['eats_id']
                    and cart['picker_items']
            ):
                assert len(request_order['picked_items']) == len(
                    cart['picker_items'],
                )
            else:
                assert request_order.get('picked_items', None) is None
            estimations.append(
                {
                    'eats_id': request_order['eats_id'],
                    'estimation': {'eta_seconds': picking_duration},
                },
            )
        return {'estimations': estimations}

    await taxi_eats_picker_dispatch.invalidate_caches()
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == orders_count
    if orders_count:
        call_info = stq.eats_picker_assign.next_call()
        assert call_info['id'] == order['eats_id']

    assert eats_eta_orders_estimate.times_called == (
        2 if use_eta_for_picking else int(use_eta_for_delivery)
    )
    if not use_initial_picking_duration:
        assert mock_estimation_orders.times_called == 2
        assert mock_order_estimate.times_called == 2
    assert environment.mock_get_picker_order.times_called == 0


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize(
    'time_estimator_tasks_count,time_estimator_batch_size',
    [(1, 1), (5, 2), (2, 5)],
)
async def test_dispatch_preorders_time_estimator_batching(
        taxi_config,
        experiments3,
        taxi_eats_picker_dispatch,
        environment,
        now,
        create_place,
        mockserver,
        time_estimator_tasks_count,
        time_estimator_batch_size,
):
    picking_duration = 1800
    experiments3.add_config(**utils.use_eta_config(False, False))
    taxi_config.set_values(
        {
            'EATS_PICKER_DISPATCH_PICKING_DURATION_FALLBACK_SETTINGS': {
                'time_estimator_tasks_count': time_estimator_tasks_count,
                'time_estimator_batch_size': time_estimator_batch_size,
                'estimation_orders_tasks_count': 1,
                'estimation_orders_batch_size': 10,
            },
        },
    )
    await taxi_eats_picker_dispatch.invalidate_caches()

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    orders_count = 10
    environment.create_orders(place_id, count=orders_count, is_asap=False)

    @mockserver.json_handler('/eats-picker-orders/api/v1/estimation-orders')
    async def mock_estimation_orders(request):
        return mockserver.make_response(
            status=200,
            json={
                'estimation_orders': [
                    {
                        'eats_id': eats_id,
                        'place_id': place_id,
                        'flow_type': 'picking_only',
                        'state': 'new',
                        'items': [
                            {
                                'category_id': 'category-id',
                                'is_catch_weight': True,
                                'count': None,
                            },
                        ],
                        'picked_items': [],
                    }
                    for eats_id in request.json['eats_ids']
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/orders/estimate',
    )
    async def mock_order_estimate(request):
        assert len(request.json['orders']) <= time_estimator_batch_size
        estimations = []
        for request_order in request.json['orders']:
            estimations.append(
                {
                    'eats_id': request_order['eats_id'],
                    'estimation': {'eta_seconds': picking_duration},
                },
            )
        return {'estimations': estimations}

    await taxi_eats_picker_dispatch.invalidate_caches()
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert mock_order_estimate.times_called == math.ceil(
        orders_count / time_estimator_batch_size,
    )
    assert mock_estimation_orders.times_called == 1
    assert environment.mock_get_picker_order.times_called == 0


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize('time_estimator_batch_size', [1, 2, 3])
@pytest.mark.parametrize(
    'estimation_orders_tasks_count,estimation_orders_batch_size',
    [(1, 1), (2, 5), (5, 2)],
)
async def test_dispatch_estimation_orders_batching(
        taxi_config,
        experiments3,
        taxi_eats_picker_dispatch,
        environment,
        now,
        create_place,
        mockserver,
        time_estimator_batch_size,
        estimation_orders_tasks_count,
        estimation_orders_batch_size,
):
    picking_duration = 1800
    experiments3.add_config(**utils.use_eta_config(False, False, False))
    taxi_config.set_values(
        {
            'EATS_PICKER_DISPATCH_PICKING_DURATION_FALLBACK_SETTINGS': {
                'time_estimator_tasks_count': 1,
                'time_estimator_batch_size': time_estimator_batch_size,
                'estimation_orders_tasks_count': estimation_orders_tasks_count,
                'estimation_orders_batch_size': estimation_orders_batch_size,
            },
        },
    )
    await taxi_eats_picker_dispatch.invalidate_caches()

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    orders_count = 10
    orders = environment.create_orders(
        place_id, count=orders_count, is_asap=False, state='new',
    )
    orders = {order['eats_id']: order for order in orders}

    @mockserver.json_handler('/eats-picker-orders/api/v1/estimation-orders')
    async def mock_estimation_orders(request):
        assert len(request.json['eats_ids']) == estimation_orders_batch_size
        return mockserver.make_response(
            status=200,
            json={
                'estimation_orders': [
                    {
                        'eats_id': eats_id,
                        'place_id': orders[eats_id]['place_id'],
                        'flow_type': orders[eats_id]['flow_type'],
                        'state': orders[eats_id]['state'],
                        'items': [
                            {
                                'category_id': 'category-id',
                                'is_catch_weight': False,
                                'count': 3,
                            },
                        ],
                        'picked_items': [
                            {
                                'id': 'picked-item-id',
                                'count': 3,
                                'weight': None,
                            },
                        ],
                    }
                    for eats_id in request.json['eats_ids']
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/orders/estimate',
    )
    async def mock_order_estimate(request):
        assert len(request.json['orders']) <= time_estimator_batch_size
        estimations = []
        for request_order in request.json['orders']:
            estimations.append(
                {
                    'eats_id': request_order['eats_id'],
                    'estimation': {'eta_seconds': picking_duration},
                },
            )
        return {'estimations': estimations}

    await taxi_eats_picker_dispatch.invalidate_caches()
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert mock_estimation_orders.times_called == math.ceil(
        orders_count / estimation_orders_batch_size,
    )
    assert mock_order_estimate.times_called == math.ceil(
        orders_count / time_estimator_batch_size,
    )
    assert environment.mock_get_picker_order.times_called == 0
