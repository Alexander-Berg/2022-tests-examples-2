# pylint: disable=too-many-lines
import datetime

import pytest

from . import utils


DB_ORDERS_UPDATE_OFFSET = 5
BULK_HANDLE = 'v1/eta/orders/estimate?consumer=testsuite'
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
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': [estimation],
            'check_status': True,
        },
    )
    assert response.status == 200
    assert response.json() == {'orders': [], 'not_found_orders': [order_nr]}

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
    db_insert_place(place)

    response = await taxi_eats_eta.post(
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': [estimation],
            'check_status': True,
        },
    )
    assert response.status == 200
    assert response.json() == {'orders': [], 'not_found_orders': [order_nr]}

    await check_metrics(requests=1, get_order_not_found_from_redis=1)

    redis_store.flushall()
    await taxi_eats_eta.tests_control(reset_metrics=True)

    response = await taxi_eats_eta.post(
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': [estimation],
            'check_status': True,
        },
    )
    assert response.status == 200
    response_body = response.json()
    assert not response_body['not_found_orders']
    assert len(response_body['orders']) == 1
    response_order = response_body['orders'][0]
    assert response_order['order_nr'] == order_nr
    assert len(response_order['estimations']) == 1
    response_estimation = response_order['estimations'][0]
    assert response_estimation['name'] == estimation
    assert (
        utils.parse_datetime(response_estimation['calculated_at']) == now_utc
    )
    assert (response_estimation.get('expected_at', None) is not None) ^ (
        response_estimation.get('duration', None) is not None
    )

    await check_metrics(requests=1, get_eta_from_postgres=1)


@pytest.mark.now('2021-10-08T12:00:00+03:00')
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize('check_status', [False, True])
@pytest.mark.parametrize('tasks_count', [1, 2])
@pytest.mark.parametrize(
    'estimations_source', ['service', 'partial_fallback', 'fallback'],
)
async def test_get_eta_ok(
        testpoint,
        experiments3,
        now_utc,
        taxi_eats_eta,
        check_metrics,
        redis_store,
        load_json,
        check_status,
        tasks_count,
        estimations_source,
):
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_settings_config3(
            db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
            bulk_handlers_tasks_count=tasks_count,
        ),
        None,
    )
    redis_updated_at = now_utc - datetime.timedelta(hours=1)
    await taxi_eats_eta.tests_control(reset_metrics=True)

    order_types = {'order-1': 'native', 'order-2': 'shop'}
    estimation_statuses = {
        'order-1': {
            'courier_arrival_duration': 'in_progress',
            'courier_arrival_at': 'in_progress',
            'cooking_duration': 'in_progress',
            'cooking_finishes_at': 'in_progress',
            'picking_duration': 'skipped',
            'picked_up_at': 'skipped',
            'place_waiting_duration': 'not_started',
            'delivery_starts_at': 'not_started',
            'delivery_duration': 'not_started',
            'delivery_at': 'not_started',
            'complete_at': 'not_started',
        },
        'order-2': {
            'courier_arrival_duration': 'in_progress',
            'courier_arrival_at': 'in_progress',
            'cooking_duration': 'skipped',
            'cooking_finishes_at': 'skipped',
            'picking_duration': 'in_progress',
            'picked_up_at': 'in_progress',
            'place_waiting_duration': 'not_started',
            'delivery_starts_at': 'not_started',
            'delivery_duration': 'not_started',
            'delivery_at': 'not_started',
            'complete_at': 'not_started',
        },
    }
    orders = list(order_types.keys())
    estimations = [
        'courier_arrival_duration',
        'cooking_duration',
        'picking_duration',
        'courier_arrival_at',
        'cooking_finishes_at',
        'picked_up_at',
        'place_waiting_duration',
        'delivery_starts_at',
        'delivery_duration',
        'delivery_at',
        'complete_at',
    ]

    redis_values = load_json('redis.json')
    for order_nr, order_type in order_types.items():
        redis_values['order_type'] = order_type
        utils.store_estimations_to_redis(
            redis_store,
            order_nr,
            redis_values,
            redis_updated_at,
            estimations_source=estimations_source,
        )

    @testpoint('eats-eta::orders-chunk-estimated')
    def chunk_processed(_):
        pass

    response = await taxi_eats_eta.post(
        BULK_HANDLE,
        json={
            'orders': orders,
            'estimations': estimations,
            'check_status': True,
        },
    )
    assert response.status == 200
    response_body = response.json()
    assert not response_body['not_found_orders']
    assert len(response_body['orders']) == len(orders)
    response_orders = {
        order['order_nr']: order for order in response_body['orders']
    }
    assert response_orders.keys() == set(orders)
    for order_nr, order in response_orders.items():
        order_type = order_types[order_nr]
        order_estimations = {
            estimation['name']: estimation
            for estimation in order['estimations']
        }
        assert order_estimations.keys() == set(estimations)
        for estimation_name, estimation_value in order_estimations.items():
            assert (
                estimation_value['status']
                == estimation_statuses[order_nr][estimation_name]
            )
            if (
                    estimation_name in ('picking_duration', 'picked_up_at')
                    and order_type in ('native', 'fast_food')
                    or estimation_name
                    in ('cooking_duration', 'cooking_finishes_at')
                    and order_type in ('retail', 'shop')
            ):
                assert (
                    estimation_value['not_calculated_reason']
                    == f'order_type={order_type}'
                )
                for key in (
                        'calculated_at',
                        'duration',
                        'remaining_duration',
                        'expected_at',
                ):
                    assert key not in estimation_value
            else:
                check_value(
                    estimation_name,
                    estimation_value,
                    redis_values[estimation_name],
                )
                assert (
                    utils.parse_datetime(estimation_value['calculated_at'])
                    == redis_updated_at
                )
                assert estimation_value['source'] == estimations_source

    await check_metrics(requests=len(orders), get_eta_from_redis=len(orders))
    assert chunk_processed.times_called == min(tasks_count, len(orders))


@pytest.mark.now('2022-01-01T12:00:00+03:00')
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS)
@pytest.mark.parametrize('check_status', [False, True])
@pytest.mark.parametrize(
    'order_update, expected_estimations, redis_estimations, cargo_called, '
    'picker_orders_called, ml_called',
    [
        [
            {'order_type': 'retail', 'order_status': 'confirmed'},
            {
                'picking_duration': 100,
                'delivery_duration': 1200,
                'picked_up_at': '2022-01-01T09:00:00+00:00',
                'delivery_at': '2022-01-01T09:41:40+00:00',
            },
            {
                'picking_duration': 100,
                'picked_up_at': '2022-01-01T12:00:00+0300',
            },
            1,
            0,
            1,
        ],
        [
            {'order_type': 'retail', 'order_status': 'confirmed'},
            {
                'picking_duration': 1800,
                'delivery_duration': 1200,
                'picked_up_at': '2022-01-01T09:30:00+00:00',
                'delivery_at': '2022-01-01T09:50:00+00:00',
            },
            {'picked_up_at': '2022-01-01T12:00:00+0300'},
            1,
            1,
            1,
        ],
        [
            {'order_type': 'retail', 'order_status': 'confirmed'},
            {
                'picking_duration': 1800,
                'picked_up_at': '2022-01-01T09:30:00+00:00',
            },
            {'picked_up_at': '2022-01-01T12:00:00+0300'},
            0,
            1,
            0,
        ],
        [
            {'order_type': 'retail', 'order_status': 'confirmed'},
            {
                'picking_duration': 1800,
                'delivery_duration': 1200,
                'picked_up_at': '2022-01-01T09:30:00+00:00',
                'delivery_at': '2022-01-01T09:50:00+00:00',
            },
            {'picking_duration': 100},
            1,
            1,
            1,
        ],
        [
            {'order_type': 'retail', 'order_status': 'confirmed'},
            {
                'picking_duration': 100,
                'courier_arrival_duration': 200,
                'delivery_duration': 300,
                'picked_up_at': '2022-01-01T09:00:00+00:00',
                'delivery_at': '2022-01-01T09:13:20+00:00',
            },
            {
                'picking_duration': 100,
                'picked_up_at': '2022-01-01T12:00:00+0300',
                'courier_arrival_duration': 200,
                'delivery_duration': 300,
            },
            0,
            0,
            0,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'courier_arrival_duration': 100,
                'cooking_duration': 200,
                'courier_arrival_at': '2022-01-01T09:03:20+00:00',
            },
            {'courier_arrival_duration': 100, 'cooking_duration': 200},
            0,
            0,
            0,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'courier_arrival_duration': 100,
                'courier_arrival_at': '2022-01-01T09:33:20+00:00',
            },
            {'courier_arrival_duration': 100},
            0,
            0,
            1,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'cooking_duration': 100,
                'courier_arrival_at': '2022-01-01T09:16:40+00:00',
            },
            {'cooking_duration': 100},
            1,
            0,
            0,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'courier_arrival_duration': 1000,
                'cooking_duration': 2000,
                'delivery_duration': 1200,
                'delivery_at': '2022-01-01T09:58:20+00:00',
            },
            {'courier_arrival_duration': 100, 'cooking_duration': 200},
            1,
            0,
            1,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'courier_arrival_duration': 1000,
                'cooking_duration': 100,
                'delivery_duration': 1200,
                'delivery_at': '2022-01-01T09:41:40+00:00',
            },
            {'cooking_duration': 100, 'delivery_duration': 200},
            1,
            0,
            0,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'courier_arrival_duration': 100,
                'cooking_duration': 2000,
                'delivery_duration': 1200,
                'delivery_at': '2022-01-01T09:58:20+00:00',
            },
            {'courier_arrival_duration': 100, 'delivery_duration': 200},
            0,
            0,
            1,
        ],
        [
            {'order_type': 'native', 'order_status': 'confirmed'},
            {
                'courier_arrival_duration': 100,
                'cooking_duration': 200,
                'delivery_duration': 300,
                'delivery_at': '2022-01-01T09:13:20+00:00',
            },
            {
                'courier_arrival_duration': 100,
                'cooking_duration': 200,
                'delivery_duration': 300,
            },
            0,
            0,
            0,
        ],
        [
            {
                'order_type': 'native',
                'order_status': 'taken',
                'delivery_started_at': '2022-01-01T09:10:00+00:00',
            },
            {
                'courier_arrival_duration': 0,
                'delivery_duration': 300,
                'delivery_at': '2022-01-01T09:15:00+00:00',
            },
            {'delivery_duration': 300},
            0,
            0,
            0,
        ],
    ],
)
@utils.eats_eta_corp_clients_config3()
@utils.eats_eta_handlers_settings_config3(force_first_update=True)
async def test_get_eta_use_basic_estimations_from_redis(
        now_utc,
        taxi_eats_eta,
        redis_store,
        pickers,
        cargo,
        mockserver,
        make_order,
        make_place,
        db_insert_order,
        db_insert_place,
        check_status,
        order_update,
        expected_estimations,
        redis_estimations,
        cargo_called,
        picker_orders_called,
        ml_called,
):
    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1/order-revision/list',
    )
    def mock_order_revisions(_):
        return mockserver.make_response(status=500)

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    order_nr = 'order_nr'
    place_id = 1
    order = make_order(
        order_nr=order_nr,
        place_id=place_id,
        claim_id='1',
        claim_status='new',
        delivery_coordinates='(11.22,33.44)',
        **order_update,
    )
    place = make_place(id=place_id)
    db_insert_order(order)
    db_insert_place(place)

    redis_updated_at = now_utc - datetime.timedelta(hours=1)
    await taxi_eats_eta.tests_control(reset_metrics=True)

    utils.store_estimations_to_redis(
        redis_store, order_nr, redis_estimations, redis_updated_at,
    )

    response = await taxi_eats_eta.post(
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': list(expected_estimations.keys()),
            'check_status': check_status,
        },
    )
    assert response.status == 200
    response_body = response.json()
    response_estimations = response_body['orders'][0]['estimations']
    response_estimations = {
        estimation['name']: estimation.get(
            estimation_field(estimation['name']), 0,
        )
        for estimation in response_estimations
    }
    assert response_estimations == expected_estimations
    assert cargo.mock_cargo_claims_info.times_called == cargo_called
    assert (
        pickers.mock_picker_orders_get_order.times_called
        == picker_orders_called
    )
    assert mock_order_revisions.times_called == ml_called


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
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': [estimation],
            'check_status': True,
        },
    )
    assert response.status == 200
    response_body = response.json()
    estimation_value = response_body['orders'][0]['estimations'][0]
    assert estimation_value.get('not_calculated_reason', None) is not None
    assert estimation_value['status'] == estimation_status

    await check_metrics(requests=1, get_eta_from_redis=1)
    await taxi_eats_eta.tests_control(reset_metrics=True)

    response = await taxi_eats_eta.post(
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': [estimation],
            'check_status': False,
        },
    )
    assert response.status == 200
    response_body = response.json()
    estimation_value = response_body['orders'][0]['estimations'][0]
    assert estimation_value['status'] == estimation_status

    if check_status:
        check_value(estimation, estimation_value, redis_values[estimation])
        assert (
            utils.parse_datetime(estimation_value['calculated_at'])
            == redis_updated_at
        )
    else:
        assert estimation_value.get('not_calculated_reason', None) is not None

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
        BULK_HANDLE,
        json={
            'orders': [order_nr],
            'estimations': [estimation],
            'check_status': True,
        },
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body['not_found_orders'] == [order_nr]

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
        BULK_HANDLE,
        json={
            'orders': [order['order_nr']],
            'estimations': ['complete_at'],
            'check_status': True,
        },
    )
    assert response.status == 200
    response_body = response.json()
    assert (
        response_body['orders'][0]['estimations'][0].get(
            'not_calculated_reason', None,
        )
        is not None
    )


@pytest.mark.parametrize('send_to_logbroker', [False, True])
@utils.eats_eta_handlers_settings_config3(force_first_update=True)
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
        now_utc,
        eta_testcase,
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

    estimations = set()
    orders = set()
    for testcase_order in eta_testcase['orders']:
        orders.add(testcase_order['order']['order_nr'])
        estimations.update(testcase_order['expected_estimations'].keys())
    if send_to_logbroker and (estimations & {'delivery_at', 'complete_at'}):
        messages_pushed = len(orders)

    response = await taxi_eats_eta.post(
        BULK_HANDLE,
        json={
            'orders': list(orders),
            'estimations': list(estimations),
            'check_status': True,
        },
    )
    assert response.status == 200
    assert after_push.times_called == messages_pushed

    response_body = response.json()
    assert not response_body['not_found_orders']
    response_orders = {
        order['order_nr']: order for order in response_body['orders']
    }
    assert response_orders.keys() == orders
    for testcase_order in eta_testcase['orders']:
        order = testcase_order['order']
        expected_estimations = testcase_order['expected_estimations']
        response_order = response_orders[order['order_nr']]
        response_estimations = {
            estimation['name']: estimation
            for estimation in response_order['estimations']
        }

        if 'order_update' in testcase_order:
            order.update(testcase_order['order_update'])

        for key, data in expected_estimations.items():
            value = data['value']
            response_estimation = response_estimations[key]
            assert response_estimation['status'] == data['status']
            if 'source' in data:
                assert response_estimation['source'] == data['source']
            if value is None:
                assert (
                    response_estimation.get('not_calculated_reason', None)
                    is not None
                )
            else:
                assert (
                    utils.parse_datetime(response_estimation['calculated_at'])
                    == now_utc
                )
                if isinstance(value, datetime.datetime):
                    assert value == utils.parse_datetime(
                        response_estimation['expected_at'],
                    ), (order['order_nr'], key)
                else:
                    assert (
                        value.total_seconds()
                        == response_estimation['duration']
                    ), (order['order_nr'], key)
                    expected_remaining_duration = (
                        utils.make_remaining_duration(
                            now_utc, order, expected_estimations, key, value,
                        )
                    )
                    if expected_remaining_duration is not None:
                        assert (
                            response_estimation['remaining_duration']
                            == expected_remaining_duration.total_seconds()
                        ), (order['order_nr'], key)

        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])

        assert db_select_orders(order_nr=order['order_nr']) == [order]
