# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from datetime import timedelta, datetime

import pytest

from tests_grocery_performer_watcher.configs import EVENT_BUS_SETTINGS
from tests_grocery_performer_watcher.constants import (
    PERFORMER_ID,
    DEPOT_ID,
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

DEPOT_SRC = DeliveryPoint(0, Point(37.656090259552, 55.73674252164294))
CLIENT_DST = DeliveryPoint(1, Point(37.65782833099365, 55.73494851319819))
DEPOT_DST = DeliveryPoint(5, Point(37.656090259552, 55.73674252164294))
DEPOT_RETURN = DeliveryPoint(6, Point(37.656090259552, 55.73674252164294))


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'was_ready_at, last_status_change_ts, src_depot_status, expected_status_ts, expected_status',
    [
        (None, '2021-12-20T09:05:00+00:00', 'pending', None, 'new'),
        (
            '2021-09-01T09:00:00+00:00',
            '2021-12-20T08:59:00+00:00',
            'pending',
            '2021-09-01T09:00:00+00:00',
            'pickuping',
        ),
        (
            None,
            '2021-12-20T09:05:00+00:00',
            'visited',
            '2021-12-20T09:05:00+00:00',
            'delivering',
        ),
    ],
)
async def test_grocery_performer_watcher_waybill_changes(
        deliveries: DeliveryRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
        was_ready_at,
        src_depot_status,
        last_status_change_ts,
        expected_status_ts,
        expected_status,
):
    was_ready_at = (
        datetime.fromisoformat(was_ready_at) if was_ready_at else None
    )
    cargo_claims.claim_id = CLAIM_ID
    # change depot src point
    cargo_dispatch.v1_waybill_info.waybill_points.append(
        WaybillPoint(
            claim_point_id=DEPOT_SRC.id,
            visit_status=src_depot_status,
            coords=DEPOT_SRC.point.coords,
            was_ready_at=was_ready_at,
            last_status_change_ts=datetime.fromisoformat(
                last_status_change_ts,
            ),
        ),
    )
    # change client point
    cargo_dispatch.v1_waybill_info.waybill_points.append(
        WaybillPoint(
            claim_point_id=CLIENT_DST.id,
            visit_status=VisitStatus.PENDING,
            coords=CLIENT_DST.point.coords,
        ),
    )
    cargo_dispatch.waybill_ref = WAYBILL_REF

    await stq_runner.grocery_performer_watcher_waybill_changes.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'waybill_ref': WAYBILL_REF,
            'depot_id': DEPOT_ID,
        },
    )

    delivery = deliveries.fetch_by_performer_id(performer_id=PERFORMER_ID)
    assert delivery is not None
    if expected_status_ts is None:
        assert delivery.status_ts is None
    else:
        assert delivery.status_ts == datetime.fromisoformat(expected_status_ts)

    assert delivery.status == expected_status


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize('is_pull_dispatch', [True, False, None])
async def test_grocery_performer_watcher_waybill_changes_not_run_taxi(
        deliveries: DeliveryRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
        stq,
        is_pull_dispatch,
):
    cargo_claims.claim_id = CLAIM_ID
    # change depot src point
    cargo_dispatch.v1_waybill_info.waybill_points.append(
        WaybillPoint(
            claim_point_id=DEPOT_SRC.id,
            visit_status=VisitStatus.PENDING,
            coords=DEPOT_SRC.point.coords,
            was_ready_at=None,
            last_status_change_ts=datetime.fromisoformat(
                '2021-12-20T09:05:00+00:00',
            ),
        ),
    )
    # change client point
    cargo_dispatch.v1_waybill_info.waybill_points.append(
        WaybillPoint(
            claim_point_id=CLIENT_DST.id,
            visit_status=VisitStatus.PENDING,
            coords=CLIENT_DST.point.coords,
        ),
    )
    cargo_dispatch.waybill_ref = WAYBILL_REF
    cargo_dispatch.v1_waybill_info.is_pull_dispatch = is_pull_dispatch

    await stq_runner.grocery_performer_watcher_waybill_changes.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'waybill_ref': WAYBILL_REF,
            'depot_id': DEPOT_ID,
        },
    )

    delivery = deliveries.fetch_by_performer_id(performer_id=PERFORMER_ID)
    assert delivery is not None
    if is_pull_dispatch is not None:
        assert delivery.is_pull_dispatch == is_pull_dispatch
    if is_pull_dispatch is None or is_pull_dispatch:
        assert (
            stq.grocery_performer_watcher_position_tracking.times_called == 1
        )
    else:
        assert (
            stq.grocery_performer_watcher_position_tracking.times_called == 0
        )
