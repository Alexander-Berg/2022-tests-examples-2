import datetime

import pytest

from . import utils


DB_ORDERS_UPDATE_OFFSET = 5
EATS_ETA_FALLBACKS = {
    'router_type': 'car',
    'courier_speed': 10,
    'courier_arrival_duration': 1000,
    'place_cargo_waiting_time': 300,
    'delivery_duration': 1200,
    'cooking_duration': 300,
    'estimated_picking_time': 1200,
    'picking_duration': 1800,
    'picking_queue_length': 600,
    'place_waiting_duration': 300,
    'customer_waiting_duration': 300,
    'picker_waiting_time': 100,
    'picker_dispatching_time': 100,
}


def handle(estimation):
    return f'v1/eta/order/{estimation}?consumer=testsuite'.replace('_', '-')


def estimation_field(estimation):
    if estimation.endswith('_duration'):
        return 'duration'
    if estimation.endswith('_at'):
        return 'expected_at'
    raise Exception('Unknown estimation')


def check_value(estimation, response, redis_value):
    value = response[estimation_field(estimation)]
    if estimation_field(estimation) == 'expected_at':
        assert utils.parse_datetime(value) == utils.parse_datetime(redis_value)
    else:
        assert value == int(redis_value)


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize(
    'estimation',
    [
        'picking_duration',
        'picked_up_at',
        'courier_arrival_duration',
        'courier_arrival_at',
        'cooking_duration',
        'cooking_finishes_at',
        'place_waiting_duration',
        'delivery_starts_at',
        'delivery_duration',
        'delivery_at',
        'complete_at',
    ],
)
@pytest.mark.parametrize('check_status', [False, True])
async def test_get_eta_order_not_found(
        taxi_eats_eta,
        check_metrics,
        check_redis_value,
        estimation,
        check_status,
):
    await taxi_eats_eta.tests_control(reset_metrics=True)
    order_nr = 'order-nr'

    response = await taxi_eats_eta.post(
        handle(estimation), json={'order_nr': order_nr, 'check_status': True},
    )
    assert response.status == 404

    for key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order_nr, key, '')

    await check_metrics(requests=1, get_order_not_found_from_postgres=1)


@pytest.mark.redis_store(
    *[
        ['set', utils.make_redis_key(key, 'order-nr'), '']
        for key in utils.ORDER_CREATED_REDIS_KEYS
    ],
)
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize(
    'estimation, order_type',
    [
        ['picking_duration', 'shop'],
        ['picked_up_at', 'shop'],
        ['courier_arrival_duration', 'shop'],
        ['courier_arrival_duration', 'native'],
        ['courier_arrival_at', 'shop'],
        ['courier_arrival_at', 'native'],
        ['cooking_duration', 'native'],
        ['cooking_finishes_at', 'native'],
        ['place_waiting_duration', 'native'],
        ['place_waiting_duration', 'shop'],
        ['delivery_starts_at', 'native'],
        ['delivery_starts_at', 'shop'],
        ['delivery_duration', 'native'],
        ['delivery_duration', 'shop'],
        ['delivery_at', 'native'],
        ['delivery_at', 'shop'],
        ['complete_at', 'native'],
        ['complete_at', 'shop'],
    ],
)
@pytest.mark.parametrize('check_status', [False, True])
async def test_get_eta_order_not_found_cached(
        now_utc,
        taxi_eats_eta,
        check_metrics,
        redis_store,
        make_order,
        make_place,
        db_insert_order,
        db_insert_place,
        estimation,
        order_type,
        check_status,
):
    await taxi_eats_eta.tests_control(reset_metrics=True)
    order_nr = 'order-nr'
    place_id = 1
    order = make_order(
        order_nr=order_nr,
        place_id=place_id,
        order_type=order_type,
        shipping_type='delivery',
        order_status='confirmed',
        delivery_type='native',
    )
    place = make_place(id=place_id)
    db_insert_order(order)
    db_insert_place(make_place(**place))

    response = await taxi_eats_eta.post(
        handle(estimation),
        json={'order_nr': order_nr, 'check_status': check_status},
    )
    assert response.status == 404

    await check_metrics(requests=1, get_order_not_found_from_redis=1)

    redis_store.flushall()
    await taxi_eats_eta.tests_control(reset_metrics=True)

    response = await taxi_eats_eta.post(
        handle(estimation),
        json={'order_nr': order_nr, 'check_status': check_status},
    )
    assert response.status == 200
    assert utils.parse_datetime(response.json()['calculated_at']) == now_utc

    await check_metrics(requests=1, get_eta_from_postgres=1)


@pytest.mark.now('2021-10-08T12:00:00+03:00')
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize(
    'estimation, order_type, estimation_status',
    [
        ['picking_duration', 'shop', 'in_progress'],
        ['picked_up_at', 'shop', 'in_progress'],
        ['courier_arrival_duration', 'shop', 'in_progress'],
        ['courier_arrival_duration', 'native', 'in_progress'],
        ['courier_arrival_at', 'shop', 'in_progress'],
        ['courier_arrival_at', 'native', 'in_progress'],
        ['cooking_duration', 'native', 'in_progress'],
        ['cooking_finishes_at', 'native', 'in_progress'],
        ['place_waiting_duration', 'native', 'not_started'],
        ['place_waiting_duration', 'shop', 'not_started'],
        ['delivery_starts_at', 'native', 'not_started'],
        ['delivery_starts_at', 'shop', 'not_started'],
        ['delivery_duration', 'native', 'not_started'],
        ['delivery_duration', 'shop', 'not_started'],
        ['delivery_at', 'native', 'not_started'],
        ['delivery_at', 'shop', 'not_started'],
        ['complete_at', 'native', 'not_started'],
        ['complete_at', 'shop', 'not_started'],
    ],
)
@pytest.mark.parametrize('check_status', [False, True])
@pytest.mark.parametrize(
    'estimations_source', ['service', 'partial_fallback', 'fallback'],
)
async def test_get_eta_ok(
        now_utc,
        taxi_eats_eta,
        check_metrics,
        redis_store,
        load_json,
        estimation,
        order_type,
        check_status,
        estimation_status,
        estimations_source,
):
    redis_updated_at = now_utc - datetime.timedelta(hours=1)
    await taxi_eats_eta.tests_control(reset_metrics=True)
    order_nr = 'order-nr'

    redis_values = load_json('redis.json')
    redis_values['order_type'] = order_type
    utils.store_estimations_to_redis(
        redis_store,
        order_nr,
        redis_values,
        redis_updated_at,
        estimations_source=estimations_source,
    )

    response = await taxi_eats_eta.post(
        handle(estimation),
        json={'order_nr': order_nr, 'check_status': check_status},
    )
    assert response.status == 200
    response_body = response.json()
    check_value(estimation, response_body, redis_values[estimation])
    assert (
        utils.parse_datetime(response_body['calculated_at'])
        == redis_updated_at
    )
    assert response_body['source'] == estimations_source
    assert response_body['status'] == estimation_status

    await check_metrics(requests=1, get_eta_from_redis=1)


@pytest.mark.now('2021-10-08T12:00:00+03:00')
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize(
    'estimation, check_status, estimation_status, redis_update',
    [
        ['picking_duration', False, 'skipped', {'order_type': 'native'}],
        [
            'picking_duration',
            True,
            'finished',
            {
                'order_type': 'retail',
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'picking_duration',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['picked_up_at', False, 'skipped', {'order_type': 'native'}],
        [
            'picked_up_at',
            True,
            'finished',
            {
                'order_type': 'retail',
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'picked_up_at',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        [
            'courier_arrival_duration',
            True,
            'skipped',
            {'shipping_type': 'pickup'},
        ],
        [
            'courier_arrival_duration',
            True,
            'finished',
            {
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'courier_arrival_duration',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['courier_arrival_at', True, 'skipped', {'shipping_type': 'pickup'}],
        [
            'courier_arrival_at',
            True,
            'finished',
            {
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'courier_arrival_at',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['cooking_duration', False, 'skipped', {'order_type': 'shop'}],
        [
            'cooking_duration',
            True,
            'finished',
            {
                'order_type': 'native',
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        ['cooking_finishes_at', False, 'skipped', {'order_type': 'shop'}],
        [
            'cooking_finishes_at',
            True,
            'finished',
            {
                'order_type': 'native',
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'place_waiting_duration',
            True,
            'skipped',
            {'shipping_type': 'pickup'},
        ],
        [
            'place_waiting_duration',
            True,
            'finished',
            {
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'place_waiting_duration',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['delivery_starts_at', True, 'skipped', {'shipping_type': 'pickup'}],
        [
            'delivery_starts_at',
            True,
            'finished',
            {
                'order_status': 'taken',
                'delivery_started_at': '2021-01-01T12:03:00+0000',
            },
        ],
        [
            'delivery_starts_at',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['delivery_duration', True, 'skipped', {'shipping_type': 'pickup'}],
        ['delivery_duration', True, 'finished', {'order_status': 'complete'}],
        [
            'delivery_duration',
            True,
            'finished',
            {'order_status': 'auto_complete'},
        ],
        ['delivery_duration', True, 'skipped', {'order_status': 'cancelled'}],
        [
            'delivery_duration',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['delivery_at', True, 'skipped', {'shipping_type': 'pickup'}],
        ['delivery_at', True, 'finished', {'order_status': 'complete'}],
        ['delivery_at', True, 'finished', {'order_status': 'auto_complete'}],
        ['delivery_at', True, 'skipped', {'order_status': 'cancelled'}],
        [
            'delivery_at',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
        ['complete_at', True, 'finished', {'order_status': 'complete'}],
        ['delivery_at', True, 'finished', {'order_status': 'auto_complete'}],
        ['complete_at', True, 'skipped', {'order_status': 'cancelled'}],
        [
            'complete_at',
            True,
            'skipped',
            {'order_type': 'retail', 'picking_status': 'cancelled'},
        ],
    ],
)
async def test_get_eta_bad_state(
        now_utc,
        taxi_eats_eta,
        check_metrics,
        redis_store,
        load_json,
        estimation,
        check_status,
        redis_update,
        estimation_status,
):
    redis_updated_at = now_utc - datetime.timedelta(hours=1)
    await taxi_eats_eta.tests_control(reset_metrics=True)
    order_nr = 'order-nr'

    redis_values = load_json('redis.json')
    redis_values.update(redis_update)
    utils.store_estimations_to_redis(
        redis_store, order_nr, redis_values, redis_updated_at,
    )

    response = await taxi_eats_eta.post(
        handle(estimation), json={'order_nr': order_nr, 'check_status': True},
    )
    assert response.status == 412

    await check_metrics(requests=1, get_eta_from_redis=1)

    await taxi_eats_eta.tests_control(reset_metrics=True)

    response = await taxi_eats_eta.post(
        handle(estimation), json={'order_nr': order_nr, 'check_status': False},
    )
    if check_status:
        assert response.status == 200
        response_body = response.json()
        check_value(estimation, response_body, redis_values[estimation])
        assert (
            utils.parse_datetime(response_body['calculated_at'])
            == redis_updated_at
        )
        assert response_body['status'] == estimation_status
    else:
        assert response.status == 412

    await check_metrics(requests=1, get_eta_from_redis=1)


@pytest.mark.now('2021-10-08T12:00:00+03:00')
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize(
    'estimation, redis_update',
    [
        [
            estimation,
            {
                'shipping_type': 'delivery',
                'order_status': order_status,
                estimation: None,
            },
        ]
        for order_status in ('created', 'paid', 'confirmed')
        for estimation in (
            'courier_arrival_duration',
            'courier_arrival_at',
            'place_waiting_duration',
        )
    ]
    + [
        [
            estimation,
            {
                'shipping_type': 'delivery',
                'order_status': order_status,
                'picking_status': 'picking',
                estimation: None,
            },
        ]
        for order_status in ('created', 'paid', 'confirmed', 'taken')
        for estimation in (
            'delivery_duration',
            'delivery_starts_at',
            'delivery_at',
            'complete_at',
        )
    ]
    + [
        [
            estimation,
            {
                'order_status': order_status,
                'order_type': order_type,
                estimation: None,
            },
        ]
        for order_type in ('retail', 'shop')
        for order_status in ('created', 'paid', 'confirmed')
        for estimation in ('picking_duration', 'picked_up_at')
    ]
    + [
        [
            estimation,
            {
                'order_status': order_status,
                'order_type': order_type,
                estimation: None,
            },
        ]
        for order_type in ('native', 'fast_food')
        for order_status in ('created', 'paid', 'confirmed')
        for estimation in ('cooking_duration', 'cooking_finishes_at')
    ]
    + [
        [
            estimation,
            {
                'shipping_type': 'delivery',
                'delivery_type': 'native',
                'claim_status': None,
            },
        ]
        for estimation in (
            'courier_arrival_duration',
            'delivery_duration',
            'complete_at',
        )
    ]
    + [
        [
            estimation,
            {
                'shipping_type': 'delivery',
                'delivery_type': 'native',
                'claim_status': 'performer_found',
                'place_visit_status': place_visit_status,
                'customer_visit_status': customer_visit_status,
            },
        ]
        for estimation in (
            'courier_arrival_duration',
            'delivery_duration',
            'complete_at',
        )
        for place_visit_status, customer_visit_status in (
            (None, 'pending'),
            ('pending', None),
        )
    ],
)
async def test_get_expired_eta(
        taxi_eats_eta,
        check_metrics,
        redis_store,
        load_json,
        estimation,
        redis_update,
):
    await taxi_eats_eta.tests_control(reset_metrics=True)
    order_nr = 'order-nr'

    redis_values = load_json('redis.json')
    redis_values.update(redis_update)
    utils.store_estimations_to_redis(redis_store, order_nr, redis_values)

    response = await taxi_eats_eta.post(
        handle(estimation), json={'order_nr': order_nr, 'check_status': False},
    )
    assert response.status == 404

    await check_metrics(requests=1, get_order_not_found_from_postgres=1)


@pytest.mark.parametrize(
    'order_status', ['complete', 'auto_complete', 'cancelled'],
)
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_get_eta_no_requests_for_terminal_statuses(
        taxi_eats_eta, now_utc, make_order, db_insert_order, order_status,
):
    order = make_order(
        id=0,
        order_nr='order_nr-0',
        status_changed_at=now_utc,
        delivery_type='native',
        order_status=order_status,
        claim_status='pickuped',
        place_point_eta_updated_at=now_utc - datetime.timedelta(days=1),
        customer_point_eta_updated_at=now_utc - datetime.timedelta(days=1),
        picking_status='picking',
        picking_duration_updated_at=now_utc - datetime.timedelta(days=1),
        picking_start_updated_at=now_utc - datetime.timedelta(days=1),
    )
    db_insert_order(order)

    response = await taxi_eats_eta.post(
        handle('complete_at'),
        json={'order_nr': order['order_nr'], 'check_status': True},
    )
    assert response.status == 412


@pytest.mark.parametrize('send_to_logbroker', [False, True])
@pytest.mark.parametrize(
    'force_first_update',
    [
        pytest.param(False),
        pytest.param(
            True, marks=pytest.mark.update_mode('force_first_update'),
        ),
    ],
)
async def test_update_and_get_eta(
        testpoint,
        experiments3,
        redis_store,
        now_utc,
        eta_testcase,
        check_metrics,
        taxi_eats_eta,
        check_redis_value,
        db_select_orders,
        send_to_logbroker,
        force_first_update,
):
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_send_to_logbroker_config3(send_to_logbroker), None,
    )
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_handlers_settings_config3(
            force_first_update=force_first_update,
        ),
        None,
    )

    @testpoint('eats-eta::message-pushed')
    def after_push(_):
        pass

    messages_pushed = 0

    for testcase_order in eta_testcase['orders']:
        order = testcase_order['order']
        expected_estimations = testcase_order['expected_estimations']

        if 'order_update' in testcase_order:
            order.update(testcase_order['order_update'])

        for key, data in expected_estimations.items():
            value = data['value']
            redis_store.flushall()
            await taxi_eats_eta.tests_control(reset_metrics=True)
            response = await taxi_eats_eta.post(
                handle(key),
                json={'order_nr': order['order_nr'], 'check_status': True},
            )
            metrics = {'requests': 1, 'get_eta_from_postgres': 1}
            metrics.update(testcase_order.get('metrics', {}))
            metrics.update(data.get('metrics', {}))
            await check_metrics(**metrics)
            if value is None:
                assert response.status in (412, 500), (key, value)
            else:
                assert response.status == 200
                response_body = response.json()
                assert (
                    utils.parse_datetime(response_body['calculated_at'])
                    == now_utc
                )
                assert response_body['status'] == data['status']
                if 'source' in data:
                    assert response_body['source'] == data['source']
                if isinstance(value, datetime.datetime):
                    assert value == utils.parse_datetime(
                        response_body['expected_at'],
                    )
                else:
                    assert value.total_seconds() == response_body['duration']
                    expected_remaining_duration = (
                        utils.make_remaining_duration(
                            now_utc, order, expected_estimations, key, value,
                        )
                    )
                    if expected_remaining_duration is not None:
                        assert (
                            response_body['remaining_duration']
                            == expected_remaining_duration.total_seconds()
                        )

            for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
                check_redis_value(
                    order['order_nr'], redis_key, order[redis_key],
                )

            message_pushed = send_to_logbroker and key in (
                'delivery_at',
                'complete_at',
            )
            messages_pushed += int(message_pushed)
            assert after_push.times_called == messages_pushed
            await taxi_eats_eta.post(
                handle(key),
                json={'order_nr': order['order_nr'], 'check_status': True},
            )
            if data.get('cached', True):
                metrics['get_eta_from_redis'] = 1
            else:
                metrics['get_eta_from_postgres'] += 1
                for metric_key, metric_value in data.get(
                        'metrics', {},
                ).items():
                    metrics[metric_key] += metric_value
                messages_pushed += int(message_pushed)
            metrics['requests'] += 1
            await check_metrics(**metrics)
            assert after_push.times_called == messages_pushed

        assert db_select_orders(order_nr=order['order_nr']) == [order]
