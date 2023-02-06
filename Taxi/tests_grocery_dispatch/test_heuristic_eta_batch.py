# flake8: noqa F401, IS001
# pylint: disable=C5521
import copy
import datetime
from math import cos, hypot, radians

import pytest
import pytz

from tests_grocery_dispatch.plugins import grocery_dispatch_pg as pg
from tests_grocery_dispatch.plugins.models import Point
from tests_grocery_dispatch.plugins.parse_timestamp import parse_timestamp
from tests_grocery_dispatch import models

LEGACY_DEPOT_ID = '123456'

CLAIM_ID_0 = 'claim_0'
CLAIM_ID_1 = 'claim_1'

HEURISTIC_PERFORMER_SPEED = 3.0
HEURISTIC_DROPOFF_TIME = 120
HEURISTIC_PICKUP_TIME = 60

ETA_SETTINGS = pytest.mark.experiments3(
    name='grocery_dispatch_eta_settings',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Performer not matched',
            'predicate': {
                'init': {
                    'set': ['idle', 'scheduled', 'matching', 'offered'],
                    'arg_name': 'dispatch_status',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'primary_calculator': 'heuristic_polyline',
                'heuristic_polyline': {
                    'heuristic_performer_speed_mps': HEURISTIC_PERFORMER_SPEED,
                    'heuristic_pickup_time': HEURISTIC_PICKUP_TIME,
                },
            },
        },
        {
            'title': 'Performer matched',
            'predicate': {
                'init': {
                    'set': [
                        'matched',
                        'delivering',
                        'delivery_arrived',
                        'ready_for_delivering_confirmation',
                    ],
                    'arg_name': 'dispatch_status',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'primary_calculator': 'heuristic_polyline',
                'heuristic_polyline': {
                    'heuristic_performer_speed_mps': HEURISTIC_PERFORMER_SPEED,
                    'heuristic_dropoff_time': HEURISTIC_DROPOFF_TIME,
                    'heuristic_pickup_time': HEURISTIC_PICKUP_TIME,
                    'performer_position_threshold': 5000,
                },
            },
        },
    ],
    is_config=True,
)


def spherical_projection_distance(pos1, pos2):
    lon1 = radians(pos1[0])
    lat1 = radians(pos1[1])

    lon2 = radians(pos2[0])
    lat2 = radians(pos2[1])

    k = (2 * 6378137.0 + 6378137.0 * (1.0 - (1.0 / 298.257223563))) / 3.0

    return k * hypot((lon2 - lon1) * cos((lat2 + lat1) / 2.0), lat2 - lat1)


NOW = datetime.datetime(2020, 2, 3, 20, 00, 00, tzinfo=datetime.timezone.utc)


@ETA_SETTINGS
@pytest.mark.now(NOW.isoformat())
async def test_matched_eta_heuristic_batch_order(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mockserver,
        cargo,
        cargo_pg,
        driver_trackstory,
        testpoint,
        grocery_dispatch_extra_pg,
        mocked_time,
        grocery_depots,
):
    order_0_position = [37.598562, 55.684961]
    order_1_position = [37.602466, 55.679112]

    performer_position = [37.592676, 55.685279]

    cargo_statuses = ['performer_found', 'performer_found']
    dispatch_statuses = ['matched', 'matched']

    prev_points_distance = 0.0
    current_point_distance = 0.0

    # pylint: disable=unused-variable
    @testpoint('test_eta_distance')
    def test_heuristic_eta_distance_(data):
        nonlocal prev_points_distance
        nonlocal current_point_distance
        prev_points_distance = data['prev_points_distance']
        current_point_distance = data['current_point_distance']

    depot_position = [37.588638, 55.680915]  # [lon, lat]
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(LEGACY_DEPOT_ID),
        location=depot_position,
        auto_add_zone=False,
    )
    await taxi_grocery_dispatch.invalidate_caches()

    performer = pg.PerformerInfo()

    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id,
        lon=performer_position[0],
        lat=performer_position[1],
    )

    order_created = NOW - datetime.timedelta(minutes=5)
    order_0 = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_0_position,
        created=order_created,
    )

    eta_seconds = 100500
    expected_eta_timestamp = NOW + datetime.timedelta(seconds=eta_seconds)
    dispatch_0 = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(
            cargo_dispatch={
                'claim_id': CLAIM_ID_0,
                'batch_claim_ids': [CLAIM_ID_0, CLAIM_ID_1],
                'batch_order_num': 0,
                'dispatch_in_batch': True,
                'dispatch_delivery_type': 'courier',
            },
        ),
        status=dispatch_statuses[0],
        performer=performer,
        order=order_0,
        dispatch_name='cargo_sync',
        eta_timestamp=expected_eta_timestamp,
    )
    dispatch_extra_0 = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch_0.dispatch_id,
    )

    order_1 = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_1_position,
        created=order_created,
    )

    dispatch_1 = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(
            cargo_dispatch={
                'claim_id': CLAIM_ID_1,
                'batch_claim_ids': [CLAIM_ID_0, CLAIM_ID_1],
                'batch_order_num': 1,
                'dispatch_in_batch': True,
                'dispatch_delivery_type': 'courier',
            },
        ),
        status=dispatch_statuses[0],
        performer=performer,
        order=order_1,
        dispatch_name='cargo_sync',
        eta_timestamp=expected_eta_timestamp,
    )
    dispatch_extra_1 = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch_1.dispatch_id,
    )

    order_0_point = Point(lon=order_0.location[0], lat=order_0.location[1])
    order_1_point = Point(lon=order_1.location[0], lat=order_1.location[1])
    cargo_pg.create_claim(
        dispatch_id=dispatch_0.dispatch_id,
        claim_id=CLAIM_ID_0,
        order_location=order_0_point,
        claim_status=cargo_statuses[0],
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_1.dispatch_id,
        claim_id=CLAIM_ID_1,
        order_location=order_1_point,
        claim_status=cargo_statuses[1],
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch_0.order.items),
        status=cargo_statuses[0],
        courier_name='test_courier_name',
    )

    cargo.add_performer(
        claim_id=CLAIM_ID_0,
        eats_profile_id=performer.eats_profile_id,
        driver_id=performer.driver_id,
        park_id=performer.park_id,
    )
    cargo.add_performer(
        claim_id=CLAIM_ID_1,
        eats_profile_id=performer.eats_profile_id,
        driver_id=performer.driver_id,
        park_id=performer.park_id,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status',
        {'dispatch_id': dispatch_0.dispatch_id},
    )

    assert response.json()['status'] == dispatch_statuses[0]
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra_0.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra_0.result_eta_timestamp - NOW).seconds
    )

    assert (
        abs(
            current_point_distance
            - spherical_projection_distance(depot_position, order_0_position),
        )
        < 0.1
    )
    expected_eta = (
        round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
        + HEURISTIC_PICKUP_TIME
    )

    assert (
        expected_eta == (dispatch_extra_0.result_eta_timestamp - NOW).seconds
    )
    expected_eta_timestamp = NOW + datetime.timedelta(seconds=expected_eta)

    assert expected_eta_timestamp == dispatch_extra_0.result_eta_timestamp

    cargo.set_data(
        items=cargo.convert_items(dispatch_1.order.items),
        status=cargo_statuses[1],
        courier_name='test_courier_name',
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status',
        {'dispatch_id': dispatch_1.dispatch_id},
    )

    assert response.status_code == 200
    assert response.json()['status'] == dispatch_statuses[1]
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra_1.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra_1.result_eta_timestamp - NOW).seconds
    )

    distance_ = spherical_projection_distance(depot_position, order_0_position)
    distance_ += spherical_projection_distance(
        order_0_position, order_1_position,
    )
    assert abs(current_point_distance + prev_points_distance - distance_) < 0.1

    # heuristic eta
    expected_eta = (
        round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
        + round(prev_points_distance / HEURISTIC_PERFORMER_SPEED)
        + HEURISTIC_DROPOFF_TIME
        + HEURISTIC_PICKUP_TIME
    )

    assert (
        expected_eta == (dispatch_extra_1.result_eta_timestamp - NOW).seconds
    )

    expected_eta_timestamp = NOW + datetime.timedelta(seconds=expected_eta)

    assert expected_eta_timestamp == dispatch_extra_1.result_eta_timestamp

    cargo_statuses = ['pickuped', 'pickuped']
    dispatch_statuses = ['delivering', 'delivering']

    cargo.set_data(
        items=cargo.convert_items(dispatch_0.order.items),
        status=cargo_statuses[0],
        courier_name='test_courier_name',
    )

    mocked_time.set(NOW + datetime.timedelta(seconds=60))

    # Заказ 0. Доставляется =======================================
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status',
        {'dispatch_id': dispatch_0.dispatch_id},
    )

    assert response.json()['status'] == dispatch_statuses[0]
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra_0.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra_0.result_eta_timestamp - mocked_time.now()).seconds
    )

    assert (
        abs(
            current_point_distance
            - spherical_projection_distance(
                performer_position, order_0_position,
            ),
        )
        < 0.1
    )
    expected_eta = round(current_point_distance / HEURISTIC_PERFORMER_SPEED)

    assert (
        expected_eta
        == (dispatch_extra_0.result_eta_timestamp - mocked_time.now()).seconds
    )
    # =============================================================

    cargo.set_data(
        items=cargo.convert_items(dispatch_1.order.items),
        status=cargo_statuses[1],
        courier_name='test_courier_name',
    )

    # Заказ 1. Доставляется =======================================
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status',
        {'dispatch_id': dispatch_1.dispatch_id},
    )

    assert response.json()['status'] == dispatch_statuses[1]
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra_1.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra_1.result_eta_timestamp - mocked_time.now()).seconds
    )

    assert (
        abs(
            prev_points_distance
            - spherical_projection_distance(
                performer_position, order_0_position,
            ),
        )
        < 0.0001
    )
    assert (
        abs(
            current_point_distance
            - spherical_projection_distance(
                order_0_position, order_1_position,
            ),
        )
        < 0.0001
    )

    expected_eta = (
        round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
        + round(prev_points_distance / HEURISTIC_PERFORMER_SPEED)
        + HEURISTIC_DROPOFF_TIME
    )

    assert (
        expected_eta
        == (dispatch_extra_1.result_eta_timestamp - mocked_time.now()).seconds
    )
    # =============================================================

    cargo_statuses = ['pickuped', 'pickuped']
    dispatch_statuses = ['delivered', 'delivering']

    # Когда первый заказ в батче доставлен, карго все еще возвращает для него статус pickuped
    # Но точка будет visited
    # В этом случае статус диспатча мы подменяем на delivered
    second_point = copy.deepcopy(models.CLIENT_POINT)
    second_point.visit_status = 'visited'

    return_point = copy.deepcopy(models.FIRST_POINT)
    return_point.type = 'return'

    cargo.set_data(
        items=cargo.convert_items(dispatch_0.order.items),
        status=cargo_statuses[0],
        courier_name='test_courier_name',
        route_points=[
            models.FIRST_POINT,
            second_point,
            models.RETURN_POINT,
            return_point,
        ],
    )

    mocked_time.set(NOW + datetime.timedelta(seconds=120))

    performer_position = [37.597482, 55.681261]
    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id,
        lon=performer_position[0],
        lat=performer_position[1],
    )

    # Заказ 0 доставлен. Заказ 1 Доставляется =====================
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status',
        {'dispatch_id': dispatch_0.dispatch_id},
    )
    assert response.json()['status'] == dispatch_statuses[0]
    assert response.status_code == 200

    cargo.set_data(
        items=cargo.convert_items(dispatch_1.order.items),
        status=cargo_statuses[1],
        courier_name='test_courier_name',
        route_points=[
            models.FIRST_POINT,
            models.CLIENT_POINT,
            models.RETURN_POINT,
            models.RETURN_POINT,
        ],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status',
        {'dispatch_id': dispatch_1.dispatch_id},
    )

    assert response.json()['status'] == dispatch_statuses[1]
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra_1.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra_1.result_eta_timestamp - mocked_time.now()).seconds
    )

    assert (
        abs(
            current_point_distance
            - spherical_projection_distance(
                performer_position, order_1_position,
            ),
        )
        < 0.0001
    )

    # =============================================================
