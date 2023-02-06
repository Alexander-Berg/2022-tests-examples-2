import pytest


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
async def test_disable_by_config(
        taxi_cargo_dispatch,
        some_cargo_order_id='00000000-0000-0000-0000-000000000000',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': some_cargo_order_id},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': 'disabled_by_config',
        'message': 'Метод отключен по конфигу',
    }


async def test_wrong_cargo_order_id(
        taxi_cargo_dispatch,
        wrong_cargo_order_id='00000000-0000-0000-0000-000000000000',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': wrong_cargo_order_id},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'order_not_found',
        'message': 'Заказ не найден',
    }


async def test_resolved_order_waybill(
        happy_path_cancelled_by_user,
        taxi_cargo_dispatch,
        cargo_orders_db,
        waybill_ref='waybill_fb_3',
):
    cargo_order_id = cargo_orders_db.order_id_from_waybill_ref(waybill_ref)
    assert cargo_order_id is not None

    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': cargo_order_id},
    )

    assert response.status_code == 200
    assert response.json() == {'path': []}


async def test_order_without_performer(
        happy_path_state_orders_created,
        taxi_cargo_dispatch,
        cargo_orders_db,
        mockserver,
        waybill_ref='waybill_fb_3',
):
    cargo_order_id = cargo_orders_db.order_id_from_waybill_ref(waybill_ref)
    assert cargo_order_id is not None

    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': cargo_order_id},
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': 'performer_not_found',
        'message': 'Исполнитель заказа не найден',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_waiting_times_by_point',
    consumers=['cargo-dispatch/cargo-route-watch'],
    clauses=[],
    default_value={
        'enabled': True,
        'source': 3,
        'destination': 3,
        'return': 3,
    },
)
async def test_happy_path(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        cargo_orders_db,
        mockserver,
        waybill_ref='waybill_fb_3',
):
    cargo_order_id = cargo_orders_db.order_id_from_waybill_ref(waybill_ref)
    assert cargo_order_id is not None

    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': cargo_order_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'path': [
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_B1_p2',
                'wait_time': 180,
            },
        ],
        'transport_type': 'car',
        'nearest_zone': 'moscow',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_waiting_times_by_point',
    consumers=['cargo-dispatch/cargo-route-watch'],
    clauses=[],
    default_value={
        'enabled': True,
        'source': 3,
        'destination': 3,
        'return': 3,
    },
)
# result path should be equal requesting it by child or parent order ids
@pytest.mark.parametrize(
    'waybill_ref',
    [
        'waybill_fb_3',  # parent_waybill_ref
        'waybill_smart_1',  # child_waybill_ref
    ],
)
async def test_chain_path(
        happy_path_chain_order,
        taxi_cargo_dispatch,
        cargo_orders_db,
        mockserver,
        waybill_ref,
):
    cargo_order_id = cargo_orders_db.order_id_from_waybill_ref(waybill_ref)
    assert cargo_order_id is not None

    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': cargo_order_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'path': [
            # Chain parent points
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_B1_p2',
                'wait_time': 180,
            },
            # Chain child points
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_A2_p2',
                'wait_time': 180,
            },
            {
                'order_id': 'seg2',
                'point': [37.5, 55.7],
                'point_id': 'seg2_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B1_p3',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B2_p4',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B3_p5',
                'wait_time': 180,
            },
            {
                'order_id': 'seg2',
                'point': [37.5, 55.7],
                'point_id': 'seg2_B1_p2',
                'wait_time': 180,
            },
        ],
        'transport_type': 'car',
        'nearest_zone': 'moscow',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_waiting_times_by_point',
    consumers=['cargo-dispatch/cargo-route-watch'],
    clauses=[],
    default_value={
        'enabled': True,
        'source': 3,
        'destination': 3,
        'return': 3,
        'pickup_time_source_in_sec': 1,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_geographically_matched_points',
    consumers=['cargo-dispatch/cargo-route-watch'],
    clauses=[],
    default_value={'enabled': True, 'max_distance': 50000},
)
async def test_geographically_matched_points(
        happy_path_chain_order,
        taxi_cargo_dispatch,
        cargo_orders_db,
        mockserver,
):
    cargo_order_id = cargo_orders_db.order_id_from_waybill_ref('waybill_fb_3')
    assert cargo_order_id is not None

    response = await taxi_cargo_dispatch.post(
        '/v1/route-watch/info',
        headers={'Accept-Language': 'ru'},
        json={'cargo_order_id': cargo_order_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'path': [
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_B1_p2',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_A1_p1',  # geographically_matched_point
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_A2_p2',  # geographically_matched_point
            },
            {
                'order_id': 'seg2',
                'point': [37.5, 55.7],
                'point_id': 'seg2_A1_p1',
                'wait_time': 182,  # 2 * 1 (pickup_time_source_in_sec) + 180
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B1_p3',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B2_p4',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B3_p5',
                'wait_time': 180,
            },
            {
                'order_id': 'seg2',
                'point': [37.5, 55.7],
                'point_id': 'seg2_B1_p2',
                'wait_time': 180,
            },
        ],
        'transport_type': 'car',
        'nearest_zone': 'moscow',
    }
