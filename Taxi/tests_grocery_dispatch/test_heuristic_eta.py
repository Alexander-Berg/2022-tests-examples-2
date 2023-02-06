# flake8: noqa F401, IS001
# pylint: disable=C5521
import datetime
from math import cos, hypot, radians

import pytest
import pytz

from tests_grocery_dispatch.plugins import grocery_dispatch_pg as pg
from tests_grocery_dispatch.plugins.models import Point
from tests_grocery_dispatch.plugins.parse_timestamp import parse_timestamp

LEGACY_DEPOT_ID = '123456'

CLAIM_ID_0 = 'claim_0'
CLAIM_ID_1 = 'claim_1'

HEURISTIC_PERFORMER_SPEED = 3.0
HEURISTIC_DROPOFF_TIME = 120
HEURISTIC_PICKUP_TIME = 60

SMOOTHING_PERIOD = 20
SMOOTHING_FACTOR = 0.15

ROUND_PRECISION = 11

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

ETA_SETTINGS_SMOOTHING = pytest.mark.experiments3(
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
                    'smooth_params': {
                        'eta_smoothing_factor': SMOOTHING_FACTOR,
                        'eta_smoothing_period': SMOOTHING_PERIOD,
                    },
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
                    'smooth_params': {
                        'eta_smoothing_factor': SMOOTHING_FACTOR,
                        'eta_smoothing_period': SMOOTHING_PERIOD,
                    },
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
ETA_SECONDS = 100500
ETA_TIMESTAMP = NOW + datetime.timedelta(seconds=ETA_SECONDS)


@pytest.mark.now(NOW.isoformat())
@ETA_SETTINGS
async def test_matched_eta_heuristic_single_order(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mockserver,
        driver_trackstory,
        testpoint,
        mocked_time,
        grocery_dispatch_extra_pg,
        grocery_depots,
):
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

    performer_position = [37.596494, 55.678895]  # [lon, lat]
    performer = pg.PerformerInfo()

    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id,
        lon=performer_position[0],
        lat=performer_position[1],
    )

    order_position = [37.599516, 55.671493]  # [lon, lat]
    order_created = NOW - datetime.timedelta(minutes=1)
    order = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_position,
        created=order_created,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(),
        status='matched',
        performer=performer,
        order=order,
        eta_timestamp=ETA_TIMESTAMP,
    )

    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra.result_eta_timestamp - NOW).seconds
    )
    assert round(current_point_distance, ROUND_PRECISION) == round(
        spherical_projection_distance(depot_position, order_position),
        ROUND_PRECISION,
    )
    assert prev_points_distance == 0.0

    # heuristic eta
    expected_eta = round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
    expected_eta += HEURISTIC_PICKUP_TIME
    expected_eta_ts = NOW + datetime.timedelta(seconds=expected_eta)

    assert expected_eta == (dispatch_extra.result_eta_timestamp - NOW).seconds
    assert expected_eta_ts == dispatch_extra.result_eta_timestamp
    assert dispatch_extra.result_eta_timestamp == expected_eta_ts
    assert (
        dispatch_extra.result_eta_timestamp
        == dispatch_extra.heuristic_polyline_eta_ts
    )
    assert (
        dispatch_extra.pickup_eta_seconds
        == NOW
        - order_created
        + datetime.timedelta(seconds=HEURISTIC_PICKUP_TIME)
    )
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(current_point_distance / HEURISTIC_PERFORMER_SPEED),
        )
    )
    assert (
        order_created
        + dispatch_extra.pickup_eta_seconds
        + dispatch_extra.deliver_current_eta_seconds
    ) == expected_eta_ts

    mocked_time.set(NOW + datetime.timedelta(seconds=60))
    dispatch.status = 'delivering'

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra.result_eta_timestamp - mocked_time.now()).seconds
    )

    assert round(current_point_distance, ROUND_PRECISION) == round(
        spherical_projection_distance(performer_position, order_position),
        ROUND_PRECISION,
    )
    expected_eta = round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
    expected_eta_ts = mocked_time.now() + datetime.timedelta(
        seconds=expected_eta,
    )

    assert (
        expected_eta
        == (dispatch_extra.result_eta_timestamp - mocked_time.now()).seconds
    )
    assert expected_eta_ts == dispatch_extra.result_eta_timestamp
    assert dispatch_extra.result_eta_timestamp == expected_eta_ts
    assert (
        dispatch_extra.result_eta_timestamp
        == dispatch_extra.heuristic_polyline_eta_ts
    )
    assert dispatch_extra.pickup_eta_seconds == (
        NOW - order_created + datetime.timedelta(seconds=HEURISTIC_PICKUP_TIME)
    )
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(current_point_distance / HEURISTIC_PERFORMER_SPEED),
        )
    )


@pytest.mark.now(NOW.isoformat())
@ETA_SETTINGS_SMOOTHING
async def test_matched_eta_heuristic_smoothing(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mockserver,
        driver_trackstory,
        testpoint,
        mocked_time,
        grocery_dispatch_extra_pg,
        grocery_depots,
):
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

    performer_position = [37.596494, 55.678895]  # [lon, lat]
    performer = pg.PerformerInfo()

    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id,
        lon=performer_position[0],
        lat=performer_position[1],
    )

    order_position = [37.599516, 55.671493]  # [lon, lat]
    order_created = NOW - datetime.timedelta(minutes=2)
    order = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_position,
        created=order_created,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(),
        status='matched',
        performer=performer,
        order=order,
        eta_timestamp=ETA_TIMESTAMP,
    )

    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra.result_eta_timestamp - NOW).seconds
    )
    assert round(current_point_distance, ROUND_PRECISION) == round(
        spherical_projection_distance(depot_position, order_position),
        ROUND_PRECISION,
    )
    assert prev_points_distance == 0.0

    # heuristic eta
    expected_eta = round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
    expected_eta += HEURISTIC_PICKUP_TIME
    expected_eta_ts = NOW + datetime.timedelta(seconds=expected_eta)

    assert expected_eta == (dispatch_extra.result_eta_timestamp - NOW).seconds
    assert dispatch_extra.result_eta_timestamp == expected_eta_ts
    assert (
        dispatch_extra.result_eta_timestamp
        == dispatch_extra.heuristic_polyline_eta_ts
    )
    assert dispatch_extra.pickup_eta_seconds == (
        NOW - order_created + datetime.timedelta(seconds=HEURISTIC_PICKUP_TIME)
    )
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(current_point_distance / HEURISTIC_PERFORMER_SPEED),
        )
    )
    assert (
        order_created
        + dispatch_extra.pickup_eta_seconds
        + dispatch_extra.deliver_current_eta_seconds
    ) == expected_eta_ts

    mocked_time.set(NOW + datetime.timedelta(seconds=60))
    dispatch.status = 'delivering'

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )

    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra.result_eta_timestamp - mocked_time.now()).seconds
    )

    assert current_point_distance == spherical_projection_distance(
        performer_position, order_position,
    )
    assert (
        dispatch_extra.result_eta_timestamp - mocked_time.now()
    ).seconds < expected_eta
    assert dispatch_extra.result_eta_timestamp < expected_eta_ts
    assert dispatch_extra.result_eta_timestamp <= expected_eta_ts
    assert (
        dispatch_extra.pickup_eta_seconds
        == NOW
        - order_created
        + datetime.timedelta(seconds=HEURISTIC_PICKUP_TIME)
    )
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(current_point_distance / HEURISTIC_PERFORMER_SPEED),
        )
    )


@ETA_SETTINGS
@pytest.mark.now(NOW.isoformat())
async def test_nonmatched_eta_heuristic(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mockserver,
        grocery_dispatch_extra_pg,
        grocery_depots,
):
    depot_position = [37.588638, 55.680915]  # [lon, lat]

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(LEGACY_DEPOT_ID),
        location=depot_position,
        auto_add_zone=False,
    )
    await taxi_grocery_dispatch.invalidate_caches()

    order_position = [37.599516, 55.671493]  # [lon, lat]
    order_created = NOW - datetime.timedelta(minutes=2)
    order = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_position,
        created=order_created,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(),
        status='matching',
        performer=pg.PerformerInfo(),
        order=order,
        eta_timestamp=ETA_TIMESTAMP,
    )

    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
        pickup_eta_seconds=HEURISTIC_PICKUP_TIME,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert dispatch.status == 'matching'
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra.result_eta_timestamp - NOW).seconds
    )

    expected_eta = (
        round(
            spherical_projection_distance(depot_position, order_position)
            / HEURISTIC_PERFORMER_SPEED,
        )
        + HEURISTIC_PICKUP_TIME
    )
    assert (dispatch_extra.result_eta_timestamp - NOW).seconds == expected_eta

    assert dispatch_extra.heuristic_polyline_eta_ts is not None
    assert (
        dispatch_extra.heuristic_polyline_eta_ts
        == dispatch_extra.result_eta_timestamp
    )

    expected_eta_ts = NOW + datetime.timedelta(seconds=expected_eta)
    assert dispatch_extra.result_eta_timestamp == expected_eta_ts
    assert (
        dispatch_extra.result_eta_timestamp
        == dispatch_extra.heuristic_polyline_eta_ts
    )
    assert dispatch_extra.pickup_eta_seconds == datetime.timedelta(
        seconds=(HEURISTIC_PICKUP_TIME + (NOW - order_created).seconds),
    )
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(
                spherical_projection_distance(depot_position, order_position)
                / HEURISTIC_PERFORMER_SPEED,
            ),
        )
    )
    assert (
        order_created
        + dispatch_extra.pickup_eta_seconds
        + dispatch_extra.deliver_current_eta_seconds
    ) == expected_eta_ts


@pytest.mark.now(NOW.isoformat())
@ETA_SETTINGS
async def test_return_previous_eta_if_no_performer_position(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mockserver,
        driver_trackstory,
        testpoint,
        mocked_time,
        grocery_dispatch_extra_pg,
        grocery_depots,
):
    status = 'delivering'
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

    performer_position = [37.596494, 55.678895]  # [lon, lat]
    performer = pg.PerformerInfo()

    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id,
        lon=performer_position[0],
        lat=performer_position[1],
    )

    order_position = [37.599516, 55.671493]  # [lon, lat]
    order_created = NOW - datetime.timedelta(minutes=5)
    order = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_position,
        created=order_created,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(),
        status=status,
        performer=performer,
        order=order,
        eta_timestamp=ETA_TIMESTAMP,
    )

    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
        pickup_eta_seconds=datetime.timedelta(seconds=180),
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )
    assert (
        response.json()['eta']
        == (dispatch_extra.result_eta_timestamp - NOW).seconds
    )

    assert current_point_distance == spherical_projection_distance(
        performer_position, order_position,
    )

    # NOW == created + 5min
    # picked_up == created + 3min == NOW - 2min

    # heuristic eta
    expected_eta = round(current_point_distance / HEURISTIC_PERFORMER_SPEED)
    expected_eta_ts = NOW + datetime.timedelta(seconds=expected_eta)

    assert dispatch_extra.result_eta_timestamp is not None
    assert (
        dispatch_extra.result_eta_timestamp
        == dispatch_extra.heuristic_polyline_eta_ts
    )
    assert expected_eta == (dispatch_extra.result_eta_timestamp - NOW).seconds
    assert dispatch_extra.result_eta_timestamp == expected_eta_ts
    assert dispatch_extra.pickup_eta_seconds == datetime.timedelta(seconds=180)
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(current_point_distance / HEURISTIC_PERFORMER_SPEED),
        )
    ) + datetime.timedelta(seconds=120)

    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id,
        lon=0.0,
        lat=0.0,
    )

    sleep_time_seconds = 60
    mocked_time.set(NOW + datetime.timedelta(seconds=sleep_time_seconds))
    next_expected_eta = expected_eta - sleep_time_seconds

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert response.json()['eta'] == next_expected_eta
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == dispatch_extra.result_eta_timestamp
    )

    assert dispatch_extra.result_eta_timestamp is not None
    assert (
        dispatch_extra.result_eta_timestamp
        == dispatch_extra.heuristic_polyline_eta_ts
    )
    assert dispatch_extra.result_eta_timestamp == expected_eta_ts
    assert dispatch_extra.pickup_eta_seconds == datetime.timedelta(seconds=180)
    assert dispatch_extra.deliver_prev_eta_seconds == datetime.timedelta(
        seconds=0,
    )
    assert dispatch_extra.deliver_current_eta_seconds == (
        datetime.timedelta(
            seconds=round(current_point_distance / HEURISTIC_PERFORMER_SPEED),
        )
    ) + datetime.timedelta(seconds=120)


@ETA_SETTINGS
@pytest.mark.now(NOW.isoformat())
async def test_nonmatched_eta_heuristic_no_depot_location_return_promise(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mocked_time,
        grocery_depots,
        grocery_dispatch_extra_pg,
):
    grocery_depots.clear_depots()
    await taxi_grocery_dispatch.invalidate_caches()

    order_position = [37.599516, 55.671493]  # [lon, lat]

    order = pg.OrderInfo(
        depot_id=LEGACY_DEPOT_ID,
        location=order_position,
        created=(NOW - datetime.timedelta(minutes=5)),
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(),
        status='matching',
        performer=pg.PerformerInfo(),
        order=order,
        eta_timestamp=ETA_TIMESTAMP,
    )
    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert dispatch.status == 'matching'

    promise = order.created + datetime.timedelta(seconds=order.max_eta)

    assert dispatch_extra.result_eta_timestamp == promise

    mocked_time.set(NOW + datetime.timedelta(minutes=60))
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert response.json()['eta'] == 0
    assert (
        parse_timestamp(response.json()['eta_timestamp']) == mocked_time.now()
    )
