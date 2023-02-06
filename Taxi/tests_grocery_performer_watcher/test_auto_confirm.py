# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from datetime import timedelta, datetime

import pytest

from tests_grocery_performer_watcher.configs import EVENT_BUS_SETTINGS
from tests_grocery_performer_watcher.constants import (
    PERFORMER_ID,
    DEPOT_ID,
    DEPOT_LOCATION,
    WAYBILL_REF,
    WAYBILL_REF_1,
    WAYBILL_REF_2,
    CLAIM_ID,
    MATCHED_EVENT,
    TASK_ID,
    TS,
    PARK_ID,
    PROFILE_ID,
)
from tests_grocery_performer_watcher.plugins.delivery_repository import (
    DeliveryRepository,
    DeliveryPoint,
    Point,
    Delivery,
    DeliveryStatus,
)
from tests_grocery_performer_watcher.plugins.claims_repository import (
    ClaimsRepository,
    Claim,
)
from tests_grocery_performer_watcher.plugins.mock_cargo_claims import (
    CargoClaimsContext,
)
from tests_grocery_performer_watcher.plugins.mock_cargo_dispatch import (
    CargoDispatchContext,
    WaybillPoint,
    VisitStatus,
)
from tests_grocery_performer_watcher.plugins.mock_driver_trackstory import (
    DriverTrackstoryContext,
)
from tests_grocery_performer_watcher.utils import is_subdict

# pylint: disable=invalid-name
pytestmark = [EVENT_BUS_SETTINGS, pytest.mark.now(TS.isoformat())]

# -----------------------------------------------------------
# ROUTE from static/default/delivery.geojson (you can try it on geojson.io)
# -----------------------------------------------------------
#
# DEPOT_SRC = 79m => POINT_1 = 40m => POINT_2 = 110m =>
# => POINT_3 == 30m ==> CLIENT
#
# -----------------------------------------------------------

DEPOT_SRC = DeliveryPoint(0, Point(*DEPOT_LOCATION))
POINT_1 = Point(37.656283378601074, 55.73603938737597)
POINT_2 = Point(37.65651471912861, 55.735703199778044)
POINT_3 = Point(37.6573884487152, 55.73485186393785)
CLIENT_DST = DeliveryPoint(1, Point(37.65782833099365, 55.73494851319819))
DEPOT_DST = DeliveryPoint(5, Point(37.656090259552, 55.73674252164294))
DEPOT_RETURN = DeliveryPoint(6, Point(37.656090259552, 55.73674252164294))

# Radiuses for points according to route above
PICKUP_RADIUS = 79
ARRIVE_RADIUS = 30
RETURN_RADIUS = 80


@pytest.mark.experiments3(filename='experiments3.json')
async def test_position_tracking_stop_on_config_timeout(
        testpoint,
        stq_runner,
        driver_trackstory: DriverTrackstoryContext,
        cargo_dispatch: CargoDispatchContext,
        deliveries,
        mocked_time,
):
    # mock settings
    driver_trackstory.position.position = [0, 0]
    driver_trackstory.position.timestamp = TS
    driver_trackstory.position.performer_id = PERFORMER_ID

    @testpoint('stop_position_tracking')
    def stop_position_tracking(data):
        assert data['tracking_id'] == TASK_ID

    # not finished status require next_point
    sample_point = DEPOT_SRC

    # finished delivery
    delivery = Delivery(
        status=DeliveryStatus('delivering'),
        status_ts=TS,
        next_point=sample_point,
        waybill_ref=WAYBILL_REF,
        performer_id=PERFORMER_ID,
        depot_id=DEPOT_ID,
    )
    deliveries.add(delivery)

    await stq_runner.grocery_performer_watcher_position_tracking.call(
        task_id=TASK_ID, kwargs={'delivery_id': str(delivery.id)},
    )
    assert stop_position_tracking.times_called == 0

    mocked_time.sleep(43201)

    await stq_runner.grocery_performer_watcher_position_tracking.call(
        task_id=TASK_ID, kwargs={'delivery_id': str(delivery.id)},
    )
    assert stop_position_tracking.times_called == 1


@pytest.mark.parametrize(
    'delivery_status, next_point, performer_position, '
    'radius, init_radius_ts, expected_radius_ts, is_confirm, is_arrive',
    [
        (
            'pickuping',
            DEPOT_SRC,
            POINT_1,
            PICKUP_RADIUS,
            None,
            TS,
            False,
            False,
        ),
        (
            'pickuping',
            DEPOT_SRC,
            POINT_1,
            PICKUP_RADIUS + 1,
            TS,
            None,
            False,
            False,
        ),
        (
            'pickuping',
            DEPOT_SRC,
            POINT_1,
            PICKUP_RADIUS,
            TS - timedelta(seconds=10),
            TS - timedelta(seconds=10),
            False,
            False,
        ),
        (
            'pickuping',
            DEPOT_SRC,
            POINT_1,
            PICKUP_RADIUS,
            TS - timedelta(seconds=21),
            None,
            True,
            False,
        ),
        (
            'pickuping',
            DEPOT_SRC,
            POINT_1,
            PICKUP_RADIUS,
            TS - timedelta(seconds=9),
            TS - timedelta(seconds=9),
            False,
            False,
        ),
        (
            'delivering',
            CLIENT_DST,
            POINT_3,
            ARRIVE_RADIUS,
            None,
            TS,
            False,
            False,
        ),
        (
            'delivering',
            CLIENT_DST,
            POINT_3,
            ARRIVE_RADIUS - 1,
            TS,
            None,
            False,
            False,
        ),
        (
            'delivering',
            CLIENT_DST,
            POINT_3,
            ARRIVE_RADIUS,
            TS - timedelta(seconds=10),
            None,
            False,
            True,
        ),
        (
            'delivering',
            CLIENT_DST,
            POINT_3,
            ARRIVE_RADIUS,
            TS - timedelta(seconds=9),
            TS - timedelta(seconds=9),
            False,
            False,
        ),
        (
            'delivery_arrived',
            CLIENT_DST,
            POINT_3,
            ARRIVE_RADIUS,
            None,
            None,
            False,
            False,
        ),
        (
            'delivery_arrived',
            CLIENT_DST,
            POINT_3,
            ARRIVE_RADIUS,
            TS,
            TS,
            False,
            False,
        ),
        (
            'returning',
            DEPOT_DST,
            POINT_1,
            RETURN_RADIUS,
            None,
            TS,
            False,
            False,
        ),
        (
            'returning',
            DEPOT_DST,
            POINT_1,
            RETURN_RADIUS - 1,
            TS,
            None,
            False,
            False,
        ),
        (
            'returning',
            DEPOT_DST,
            POINT_1,
            RETURN_RADIUS,
            TS - timedelta(seconds=10),
            TS - timedelta(seconds=10),
            False,
            False,
        ),
        (
            'returning',
            DEPOT_DST,
            POINT_1,
            RETURN_RADIUS,
            TS - timedelta(seconds=20),
            None,
            True,
            False,
        ),
        (
            'returning',
            DEPOT_DST,
            POINT_1,
            RETURN_RADIUS,
            TS - timedelta(seconds=9),
            TS - timedelta(seconds=9),
            False,
            False,
        ),
    ],
)
async def test_auto_confirm_happy_path(
        driver_trackstory: DriverTrackstoryContext,
        cargo_dispatch: CargoDispatchContext,
        stq_runner,
        load_json,
        deliveries,
        experiments3,
        radius,
        delivery_status,
        next_point,
        performer_position,
        init_radius_ts,
        expected_radius_ts,
        is_confirm,
        is_arrive,
):
    # parametrize experiment3
    exp = load_json('experiments3.json')
    # hit radius duration
    exp['configs'][1]['default_value']['duration'] = 10
    # radius
    exp['configs'][1]['default_value']['radius'] = radius
    experiments3.add_experiments_json(exp)

    # mock settings
    driver_trackstory.position.position = performer_position.coords
    driver_trackstory.position.timestamp = TS
    driver_trackstory.position.performer_id = PERFORMER_ID

    cargo_dispatch.v1_waybill_arrive_at_point.point_id = next_point.id
    cargo_dispatch.v1_waybill_arrive_at_point.driver_id = PROFILE_ID
    cargo_dispatch.v1_waybill_arrive_at_point.park_id = PARK_ID

    # current delivery
    delivery = Delivery(
        status=delivery_status,
        prev_point=DEPOT_SRC if next_point != DEPOT_SRC else None,
        next_point=next_point,
        next_after_next_point=DEPOT_RETURN,
        radius_ts=init_radius_ts,
        waybill_ref=WAYBILL_REF,
        performer_id=PERFORMER_ID,
        depot_id=DEPOT_ID,
    )
    deliveries.add(delivery)

    await stq_runner.grocery_performer_watcher_position_tracking.call(
        task_id=TASK_ID, kwargs={'delivery_id': str(delivery.id)},
    )

    delivery = deliveries.fetch_by_performer_id(PERFORMER_ID)
    assert delivery.radius_ts == expected_radius_ts
    assert cargo_dispatch.v1_waybill_exchange_confirm.mock.times_called == (
        1 if is_confirm else 0
    )
    assert cargo_dispatch.v1_waybill_arrive_at_point.mock.times_called == (
        1 if is_arrive else 0
    )


# On new point visit radius_ts reset and points are updated
@pytest.mark.experiments3(filename='experiments3.json')
async def test_auto_confirm_reset_time_on_new_point(
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
        load_json,
        deliveries,
        experiments3,
):
    # parametrize experiment3
    exp = load_json('experiments3.json')
    # radius
    exp['configs'][1]['default_value']['radius'] = 500
    experiments3.add_experiments_json(exp)

    waybill_points_visit_statuses = [
        VisitStatus.VISITED,
        VisitStatus.PENDING,
        VisitStatus.PENDING,
        VisitStatus.PENDING,
    ]
    cargo_claims.claim_id = CLAIM_ID
    for idx, point in enumerate(
            [DEPOT_SRC, CLIENT_DST, DEPOT_DST, DEPOT_RETURN],
    ):
        cargo_dispatch.v1_waybill_info.waybill_points.append(
            WaybillPoint(
                claim_point_id=point.id,
                visit_status=waybill_points_visit_statuses[idx],
                coords=point.point.coords,
            ),
        )
    cargo_dispatch.waybill_ref = WAYBILL_REF

    # current delivery
    delivery = Delivery(
        status=DeliveryStatus.PICKUPING,
        prev_point=None,
        next_point=DEPOT_SRC,
        next_after_next_point=CLIENT_DST,
        radius_ts=TS - timedelta(seconds=5),
        waybill_ref=WAYBILL_REF,
        performer_id=PERFORMER_ID,
        depot_id=DEPOT_ID,
    )
    deliveries.add(delivery)

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    delivery = deliveries.fetch_by_performer_id(PERFORMER_ID)
    assert delivery.status == DeliveryStatus.DELIVERING
    assert delivery.radius_ts is None
    assert delivery.prev_point == DEPOT_SRC
    assert delivery.next_point == CLIENT_DST
    assert delivery.next_after_next_point == DEPOT_DST
    assert cargo_dispatch.v1_waybill_exchange_confirm.mock.times_called == 0
    assert cargo_dispatch.v1_waybill_arrive_at_point.mock.times_called == 0
