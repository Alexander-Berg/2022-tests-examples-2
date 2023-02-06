import datetime

import pytest

from . import utils


def make_place_load_info(place_id, **kwargs):
    return dict(
        {
            'place_id': place_id,
            'brand_id': 1,
            'country_id': 1,
            'region_id': 1,
            'time_zone': 'Europe/Moscow',
            'city': 'Москва',
            'enabled': True,
            'estimated_waiting_time': 0,
            'free_pickers_count': 1,
            'total_pickers_count': 1,
            'is_place_closed': False,
            'is_place_overloaded': False,
        },
        **kwargs,
    )


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_free_picker(
        taxi_eats_picker_dispatch, environment, create_place, now, handle,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    (picker_one, _) = environment.create_pickers(
        place_id, count=2, available_until=now + datetime.timedelta(minutes=1),
    )
    (order_one, _) = environment.create_orders(
        place_id,
        count=2,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    environment.start_picking_order(picker_one, order_one)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id, free_pickers_count=1, total_pickers_count=2,
        ),
    ]


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_free_picker_db_empty(
        taxi_eats_picker_dispatch,
        environment,
        places_environment,
        get_places,
        now,
        handle,
):
    features = {
        'ignore_surge': False,
        'supports_preordering': False,
        'fast_food': False,
        'shop_picking_type': 'shop_picking',
    }
    place_id = places_environment.create_places(1, dict(features=features))[0]
    (delivery_zone,) = places_environment.create_delivery_zones(
        place_id,
        1,
        working_intervals=[
            {'from': now, 'to': now + datetime.timedelta(hours=10)},
        ],
    )

    (picker_one, _) = environment.create_pickers(
        place_id, count=2, available_until=now + datetime.timedelta(minutes=1),
    )
    (order_one, _) = environment.create_orders(
        place_id,
        count=2,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    environment.start_picking_order(picker_one, order_one)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    expected_response = make_place_load_info(
        place_id, free_pickers_count=1, total_pickers_count=2,
    )
    expected_response['shop_picking_type'] = 'shop_picking'
    assert places_load_info == [expected_response]

    assert places_environment.mock_retrieve_places.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 1
    expected_data = utils.make_expected_data(
        [places_environment.catalog_places[place_id]],
        {place_id: delivery_zone},
    )
    utils.compare_db_with_expected_data(get_places(), expected_data)


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_no_free_pickers(
        taxi_eats_picker_dispatch, environment, create_place, handle,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)

    (picker_one, _) = environment.create_pickers(place_id, count=2)
    (order_one, _) = environment.create_orders(
        place_id, estimated_picking_time=1000, count=2,
    )
    environment.create_orders(
        place_id, status='dispatching', estimated_picking_time=1500, count=1,
    )
    environment.start_picking_order(picker_one, order_one)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=1750,
            free_pickers_count=0,
            total_pickers_count=2,
        ),
    ]


async def test_admin_calculate_load_empty_body(
        taxi_eats_picker_dispatch, environment, create_place,
):
    response = await taxi_eats_picker_dispatch.post(
        '/admin/v1/places/calculate-load', json={},
    )
    assert response.status == 400


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_calculate_load_all_places(
        taxi_eats_picker_dispatch, environment, create_place,
):
    (place_1, place_2) = environment.create_places(2)
    create_place(place_1)
    create_place(place_2)

    (picker_one,) = environment.create_pickers(place_1, count=1)
    environment.create_pickers(place_2, count=1)
    (order_one,) = environment.create_orders(
        place_1, count=1, estimated_picking_time=1800,
    )
    environment.start_picking_order(picker_one, order_one)

    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/places/calculate-load', json={},
    )
    assert response.status == 200
    places_load_info = sorted(
        response.json()['places_load_info'], key=lambda item: item['place_id'],
    )
    assert all(
        len(place_load_info.pop('working_intervals')) == 1
        for place_load_info in places_load_info
    )
    assert places_load_info == [
        make_place_load_info(
            place_1,
            estimated_waiting_time=1800,
            free_pickers_count=0,
            total_pickers_count=1,
        ),
        make_place_load_info(
            place_2,
            estimated_waiting_time=0,
            free_pickers_count=1,
            total_pickers_count=1,
        ),
    ]


@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_empty_place_ids(
        taxi_eats_picker_dispatch, handle,
):
    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': []},
    )
    assert response.status == 400


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_place_overload(
        taxi_eats_picker_dispatch, environment, create_place, handle,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    pickers = environment.create_pickers(place_id, count=2)
    orders = environment.create_orders(
        place_id, count=5, estimated_picking_time=3600,
    )
    for i in range(2):
        environment.start_picking_order(pickers[i], orders[i])

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=9000,
            free_pickers_count=0,
            total_pickers_count=2,
            is_place_overloaded=True,
        ),
    ]


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_place_about_to_close_overload(
        taxi_eats_picker_dispatch, environment, create_place, now, handle,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[
            (
                now - datetime.timedelta(hours=10),
                now + datetime.timedelta(hours=1),
            ),
        ],
    )
    pickers = environment.create_pickers(
        place_id,
        count=2,
        available_until=now + datetime.timedelta(minutes=30),
    )
    orders = environment.create_orders(
        place_id,
        count=3,
        estimated_picking_time=3600,
        place_finishes_work_at=utils.to_string(
            now + datetime.timedelta(hours=1),
        ),
    )
    for i in range(2):
        environment.start_picking_order(pickers[i], orders[i])

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=5400,
            free_pickers_count=0,
            total_pickers_count=2,
            is_place_overloaded=True,
        ),
    ]


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_place_closed(
        taxi_eats_picker_dispatch, environment, now, create_place, handle,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[
            (
                now + datetime.timedelta(hours=10),
                now + datetime.timedelta(days=1),
            ),
        ],
    )
    environment.create_pickers(place_id, count=1, available_until=now)
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=3600,
        created_at=utils.to_string(now),
        place_finishes_work_at=utils.to_string(
            now + datetime.timedelta(hours=10),
        ),
    )

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=3600,
            free_pickers_count=0,
            total_pickers_count=1,
            is_place_closed=True,
        ),
    ]


@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_place_closed_no_next_interval(
        taxi_eats_picker_dispatch, environment, now, create_place, handle,
):
    (place_1,) = environment.create_places(1)
    create_place(
        place_1, working_intervals=[(now - datetime.timedelta(hours=10), now)],
    )
    environment.create_pickers(place_1, count=1, available_until=now)
    environment.create_orders(place_1, count=1)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_1]},
    )
    assert response.status == 200
    assert response.json() == {'places_load_info': []}


@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_place_disabled(
        taxi_eats_picker_dispatch, environment, now, create_place, handle,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        enabled=False,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    environment.create_pickers(place_id, count=1)
    environment.create_orders(place_id, count=1)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=0,
            free_pickers_count=1,
            total_pickers_count=1,
            enabled=False,
        ),
    ]


@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
@pytest.mark.parametrize('orders_count', [0, 1, 2])
async def test_calculate_load_no_pickers(
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        orders_count,
        handle,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_orders(
        place_id, count=orders_count, estimated_picking_time=3600,
    )

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=orders_count * 3600,
            free_pickers_count=0,
            total_pickers_count=0,
        ),
    ]


@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_no_place(
        taxi_eats_picker_dispatch, environment, places_environment, handle,
):
    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/places/calculate-load', json={'place_ids': [1]},
    )
    assert response.status == 200
    assert response.json() == {'places_load_info': []}


@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_picker_orders_failure(
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        mockserver,
        handle,
):
    @mockserver.json_handler(
        '/eats-picker-orders/api/v1/orders/select-for-dispatch',
    )
    def _picker_orders_select_orders_for_dispatch(request):
        raise mockserver.TimeoutError()

    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(place_id, count=1)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 500
    assert response.json() == {
        'code': 'INTERNAL_ERROR',
        'message': 'Error from eats-picker-orders',
    }


@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
async def test_calculate_load_picker_supply_failure(
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        mockserver,
        handle,
):
    @mockserver.json_handler(
        '/eats-picker-supply/api/v1/select-store-pickers/',
    )
    def _picker_supply_select_store_pickers(request):
        raise mockserver.TimeoutError()

    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(place_id, count=1)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 500
    assert response.json() == {
        'code': 'INTERNAL_ERROR',
        'message': 'Error from eats-picker-supply',
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
@pytest.mark.config(
    EATS_PICKER_DISPATCH_SYNC_PLACES_INFO_PARAMS={
        'period_seconds': 60,
        'working_intervals_limit': 7,
        'places_batch_size': 1,
    },
)
async def test_calculate_load_catalog_storage_failure(
        taxi_eats_picker_dispatch,
        mockserver,
        environment,
        places_environment,
        get_places,
        now,
        handle,
):
    (place_1_id, place_2_id) = places_environment.create_places(2)
    (delivery_zone,) = places_environment.create_delivery_zones(
        place_1_id,
        1,
        working_intervals=[
            {'from': now, 'to': now + datetime.timedelta(hours=10)},
        ],
    )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    async def mock_retrieve_places(request):
        if any(
                place_id not in (place_1_id, place_2_id)
                for place_id in request.json['place_ids']
        ):
            return mockserver.make_response(status=500)
        return await places_environment.mock_retrieve_places(request)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/delivery_zones/retrieve-by-place-ids',
    )
    async def mock_retrieve_delivery_zones(request):
        if any(
                place_id not in (place_1_id, 555)
                for place_id in request.json['place_ids']
        ):
            return mockserver.make_response(status=500)
        return await places_environment.mock_retrieve_delivery_zones(request)

    (picker_one, _) = environment.create_pickers(place_1_id, count=2)
    (order_one, _) = environment.create_orders(place_1_id, count=2)
    environment.start_picking_order(picker_one, order_one)

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [1, 2, place_1_id, 555, place_2_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    expected_response = make_place_load_info(
        place_1_id, free_pickers_count=1, total_pickers_count=2,
    )
    expected_response['shop_picking_type'] = 'our_picking'
    assert places_load_info == [expected_response]

    assert mock_retrieve_places.times_called == 5
    assert places_environment.mock_retrieve_places.times_called == 2
    assert mock_retrieve_delivery_zones.times_called == 2
    assert places_environment.mock_retrieve_delivery_zones.times_called == 1
    expected_data = utils.make_expected_data(
        [places_environment.catalog_places[place_1_id]],
        {place_1_id: delivery_zone},
    )
    utils.compare_db_with_expected_data(get_places(), expected_data)


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
@pytest.mark.parametrize('remaining_picking_duration', [100, 200])
async def test_expired_order(
        now_utc,
        mockserver,
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        mocked_time,
        remaining_picking_duration,
        handle,
):
    estimated_picking_time = 2000
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    picker_one, _ = environment.create_pickers(place_id, count=2)
    order_one, _ = environment.create_orders(
        place_id,
        count=2,
        estimated_picking_time=estimated_picking_time,
        status='dispatching',
    )
    environment.start_picking_order(picker_one, order_one)

    # Делаем так, что с момента старта сборки order_one прошло времени больше,
    # чем длительность его сборки
    mocked_time.sleep(2001)

    def eats_eta_picking_duration(order_nr):
        calculated_at = utils.to_string(now_utc())
        if order_nr == order_one['eats_id']:
            return {
                'name': 'picking_duration',
                'duration': estimated_picking_time,
                'remaining_duration': remaining_picking_duration,
                'calculated_at': calculated_at,
                'status': 'in_progress',
            }
        return {
            'name': 'picking_duration',
            'duration': estimated_picking_time,
            'remaining_duration': estimated_picking_time,
            'calculated_at': calculated_at,
            'status': 'not_started',
        }

    environment.get_picking_duration_response = eats_eta_picking_duration

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            estimated_waiting_time=(
                estimated_picking_time + remaining_picking_duration
            )
            // 2,
            free_pickers_count=0,
            total_pickers_count=2,
        ),
    ]


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_calculate_load_without_order_happy_path(
        mockserver, taxi_eats_picker_dispatch, environment, create_place, now,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=1000,
        created_at=utils.to_string(now - datetime.timedelta(seconds=2)),
    )
    (order_2, _) = environment.create_orders(
        place_id,
        count=2,
        estimated_picking_time=1000,
        created_at=utils.to_string(now - datetime.timedelta(seconds=1)),
    )
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=1000,
        created_at=utils.to_string(now),
    )

    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _picker_orders_get_order(request):
        return mockserver.make_response(
            status=200, json={'payload': order_2, 'meta': {}},
        )

    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/place/calculate-load-without-order',
        json={'eats_id': order_2['eats_id']},
    )
    assert response.status == 200

    place_load_info = response.json()
    assert len(place_load_info.pop('working_intervals')) == 1
    assert place_load_info == make_place_load_info(
        place_id,
        estimated_waiting_time=2000,  # order1 + order2
        free_pickers_count=0,
        total_pickers_count=0,
    )


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_calculate_load_without_order_order_not_found_with_place_id(
        mockserver, taxi_eats_picker_dispatch, environment, create_place, now,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    (picker_one,) = environment.create_pickers(
        place_id, count=1, available_until=now + datetime.timedelta(minutes=1),
    )
    (order_one,) = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=1000,
        created_at=utils.to_string(now - datetime.timedelta(minutes=1)),
    )
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=1000,
        created_at=utils.to_string(now),
    )
    environment.start_picking_order(picker_one, order_one)

    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _picker_orders_get_order(request):
        return mockserver.make_response(
            status=404, json={'code': 'code', 'message': 'message'},
        )

    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/place/calculate-load-without-order',
        json={
            'eats_id': order_one['eats_id'],
            'place_id': order_one['place_id'],
        },
    )
    assert response.status == 200

    place_load_info = response.json()
    assert len(place_load_info.pop('working_intervals')) == 1
    assert place_load_info == make_place_load_info(
        place_id,
        estimated_waiting_time=2000,
        free_pickers_count=0,
        total_pickers_count=1,
    )


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_calculate_load_without_order_order_not_found_no_place_id(
        mockserver, taxi_eats_picker_dispatch, environment, create_place, now,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _picker_orders_get_order(request):
        return mockserver.make_response(
            status=404, json={'code': 'code', 'message': 'message'},
        )

    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/place/calculate-load-without-order',
        json={'eats_id': 'eats_id'},
    )
    assert response.status == 404


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.parametrize(
    'handle',
    ['/api/v1/places/calculate-load', '/admin/v1/places/calculate-load'],
)
@pytest.mark.parametrize(
    'timeshift, estimated_waiting_time', [(0, 2400), (1, 1200)],
)
async def test_calculate_load_preorders(
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        now,
        experiments3,
        timeshift,
        estimated_waiting_time,
        handle,
):
    experiments3.add_config(
        name='eats_picker_dispatch_timeshift',
        match={
            'consumers': [{'name': 'eats-picker-dispatch/timeshift'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={'timeshift': timeshift},
    )
    await taxi_eats_picker_dispatch.invalidate_caches()
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    (picker_one,) = environment.create_pickers(
        place_id, count=1, available_until=now + datetime.timedelta(minutes=1),
    )
    orders = (
        environment.create_orders(
            place_id,
            count=1,
            place_finishes_work_at=utils.to_string(
                now - datetime.timedelta(minutes=1),
            ),
        )
        + environment.create_orders(
            place_id,
            count=1,
            place_finishes_work_at=utils.to_string(
                now - datetime.timedelta(minutes=1),
            ),
            estimated_delivery_time=utils.to_string(
                now + datetime.timedelta(minutes=50),
            ),
        )
    )

    environment.start_picking_order(picker_one, orders[0])

    response = await taxi_eats_picker_dispatch.post(
        handle, json={'place_ids': [place_id]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id,
            free_pickers_count=0,
            total_pickers_count=1,
            estimated_waiting_time=estimated_waiting_time,
        ),
    ]
