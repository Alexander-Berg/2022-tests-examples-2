import datetime

from . import utils


PERIODIC_NAME = 'cooking-duration-updater'


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_cooking_duration_updater_no_orders_to_update(
        taxi_eats_eta,
        make_order,
        db_insert_order,
        db_select_orders,
        redis_store,
):
    orders = (
        [
            make_order(order_type=order_type, order_status='confirmed')
            for order_type in ('retail', 'shop')
        ]
        + [
            make_order(order_type='native', order_status=order_status)
            for order_status in (
                'taken',
                'cancelled',
                'complete',
                'auto_complete',
            )
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
async def test_cooking_duration_updater_no_ml_requests(
        taxi_eats_eta,
        make_order,
        db_insert_order,
        make_place,
        db_insert_place,
        db_select_orders,
        check_redis_value,
        now_utc,
):
    place_id = 1
    unknown_place_id = 2
    cooking_time = 1234
    average_preparation = 12
    extra_preparation = 34
    db_insert_place(
        make_place(
            id=place_id,
            average_preparation=average_preparation,
            extra_preparation=extra_preparation,
        ),
    )
    orders = [
        make_order(
            order_type='fast_food',
            order_status='confirmed',
            place_id=unknown_place_id,
        ),
        make_order(
            order_type='native',
            order_status='confirmed',
            place_id=unknown_place_id,
            delivery_coordinates='(11.22,33.44)',
        ),
        make_order(
            order_type='native', order_status='confirmed', place_id=place_id,
        ),
        make_order(
            order_type='native',
            order_status='confirmed',
            cooking_time=cooking_time,
            place_id=place_id,
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
        if order['cooking_time'] is not None:
            cooking_duration = order['cooking_time']
        elif order['place_id'] == place_id:
            cooking_duration = datetime.timedelta(
                seconds=average_preparation + extra_preparation,
            )
        else:
            cooking_duration = datetime.timedelta(
                seconds=utils.FALLBACKS['cooking_duration'],
            )
        if order['order_type'] != 'fast_food':
            cooking_duration = max(
                cooking_duration,
                utils.trunc_timedelta(now_utc - order['created_at']),
            )
        check_redis_value(
            order['order_nr'], 'cooking_duration', cooking_duration,
        )


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_cooking_duration_updater_ml_error(
        mockserver,
        taxi_eats_eta,
        make_order,
        db_insert_order,
        make_place,
        db_insert_place,
        db_select_orders,
        check_redis_value,
        revisions,
):
    place_id = 1
    average_preparation = 12
    extra_preparation = 34
    db_insert_place(
        make_place(
            id=place_id,
            average_preparation=average_preparation,
            extra_preparation=extra_preparation,
        ),
    )
    order = make_order(
        order_type='fast_food',
        order_status='confirmed',
        place_id=place_id,
        delivery_coordinates='(11.22,33.44)',
    )
    revisions.set_default(order['order_nr'], str(place_id))
    db_insert_order(order)

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def mock_umlaas(request):
        return mockserver.make_response(status=499)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == [order]
    assert revisions.mock_order_revision_list.times_called == 1
    assert revisions.mock_order_revision_details.times_called == 1
    assert mock_umlaas.times_called == 1

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'],
        'cooking_duration',
        average_preparation + extra_preparation,
    )


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_cooking_duration_updater_ok(
        mockserver,
        taxi_eats_eta,
        make_order,
        db_insert_order,
        make_place,
        db_insert_place,
        db_select_orders,
        check_redis_value,
        revisions,
):
    place_id = 1
    average_preparation = 12
    extra_preparation = 34
    cooking_time = 56
    delivery_time = 78
    total_time = 90
    ml_provider = 'ml'
    db_insert_place(
        make_place(
            id=place_id,
            average_preparation=average_preparation,
            extra_preparation=extra_preparation,
        ),
    )
    order = make_order(
        order_type='fast_food',
        order_status='confirmed',
        place_id=place_id,
        delivery_coordinates='(11.22,33.44)',
    )
    revisions.set_default(order['order_nr'], str(place_id))
    db_insert_order(order)

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def mock_umlaas(request):
        return utils.make_ml_response(
            place_id,
            cooking_time=cooking_time,
            delivery_time=delivery_time,
            total_time=total_time,
            request_id=request.query['request_id'],
            provider=ml_provider,
        )

    order['ml_provider'] = ml_provider
    order['cooking_time'] = datetime.timedelta(minutes=cooking_time)
    order['delivery_time'] = datetime.timedelta(minutes=delivery_time)
    order['total_time'] = datetime.timedelta(minutes=total_time)
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == [order]
    assert revisions.mock_order_revision_list.times_called == 1
    assert revisions.mock_order_revision_details.times_called == 1
    assert mock_umlaas.times_called == 1

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'], 'cooking_duration', order['cooking_time'],
    )
