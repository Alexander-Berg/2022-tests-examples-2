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


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'waybill_points_visit_statuses, expected_delivery_status, expected_prev_point, expected_next_point',
    [
        (['pending', 'pending', 'pending', 'pending'], 'new', None, DEPOT_SRC),
        (['arrived', 'pending', 'pending', 'pending'], 'new', None, DEPOT_SRC),
        (
            ['visited', 'pending', 'pending', 'pending'],
            'delivering',
            DEPOT_SRC,
            CLIENT_DST,
        ),
        (
            ['visited', 'arrived', 'pending', 'pending'],
            'delivery_arrived',
            DEPOT_SRC,
            CLIENT_DST,
        ),
        (
            ['visited', 'visited', 'pending', 'skipped'],
            'returning',
            CLIENT_DST,
            DEPOT_DST,
        ),
        (
            ['visited', 'visited', 'arrived', 'skipped'],
            'returning',
            CLIENT_DST,
            DEPOT_DST,
        ),
        (
            ['visited', 'visited', 'skipped', 'pending'],
            'returning',
            DEPOT_DST,
            DEPOT_RETURN,
        ),
        (
            ['visited', 'visited', 'skipped', 'arrived'],
            'returning',
            DEPOT_DST,
            DEPOT_RETURN,
        ),
        (
            ['visited', 'visited', 'visited', 'skipped'],
            'finished',
            DEPOT_RETURN,
            None,
        ),
        (
            ['skipped', 'skipped', 'skipped', 'skipped'],
            'finished',
            DEPOT_RETURN,
            None,
        ),
    ],
)
async def test_updating_delivery_by_waybill_tracker(
        deliveries: DeliveryRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
        waybill_points_visit_statuses,
        expected_delivery_status,
        expected_prev_point,
        expected_next_point,
):
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

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    delivery = deliveries.fetch_by_performer_id(performer_id=PERFORMER_ID)
    assert delivery is not None
    assert delivery.depot_id == DEPOT_ID
    assert delivery.waybill_ref == WAYBILL_REF
    assert delivery.status == expected_delivery_status
    assert delivery.prev_point == expected_prev_point
    assert delivery.next_point == expected_next_point
    assert delivery.radius_ts is None


@pytest.mark.experiments3(filename='experiments3.json')
async def test_updating_delivery_points_waybill_tracker(
        deliveries: DeliveryRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
):
    waybill_points_visit_statuses = [
        VisitStatus.PENDING,
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

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    delivery = deliveries.fetch_by_performer_id(performer_id=PERFORMER_ID)
    assert delivery is not None
    assert delivery.depot_id == DEPOT_ID
    assert delivery.waybill_ref == WAYBILL_REF
    assert delivery.status == 'new'
    assert delivery.prev_point is None
    assert delivery.next_point == DEPOT_SRC
    assert delivery.next_after_next_point == CLIENT_DST

    # visit DEPOT_SRC
    cargo_dispatch.v1_waybill_info.waybill_points[
        0
    ].visit_status = VisitStatus.VISITED
    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    delivery = deliveries.fetch_by_performer_id(performer_id=PERFORMER_ID)
    assert delivery is not None
    # assert delivery.status == 'new'
    assert delivery.prev_point == DEPOT_SRC
    assert delivery.next_point == CLIENT_DST
    assert delivery.next_after_next_point == DEPOT_DST


@pytest.mark.experiments3(filename='experiments3.json')
async def test_waybill_tracking_stq_run_on_order_matched_event(
        stq, process_event,
):
    await process_event(MATCHED_EVENT)

    assert stq.grocery_performer_watcher_waybill_tracking.times_called == 1
    assert is_subdict(
        stq.grocery_performer_watcher_waybill_tracking.next_call()['kwargs'],
        {
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'waybill_points_visit_statuses,  is_stop',
    [
        (
            ['pending', 'pending', 'pending', 'pending'],
            False,
        ),  # not finished waybill
        (
            ['visited', 'visited', 'visited', 'skipped'],
            True,
        ),  # finished waybill
    ],
)
async def test_stop_waybill_tracking_on_waybill_finished(
        waybill_points_visit_statuses,
        stq_runner,
        testpoint,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims,
        is_stop,
):
    @testpoint('stop_waybill_tracking')
    def stop_waybill_tracking(data):
        assert data['tracking_id'] == TASK_ID

    cargo_claims.claim_id = CLAIM_ID

    cargo_dispatch.waybill_ref = WAYBILL_REF
    # all visited points treat as finished
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

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    assert stop_waybill_tracking.times_called == (1 if is_stop else 0)


@pytest.mark.experiments3(filename='experiments3.json')
async def test_stop_waybill_tracking_on_timeout(
        stq_runner,
        testpoint,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims,
        mocked_time,
        deliveries,
):
    @testpoint('stop_waybill_tracking')
    def stop_waybill_tracking(data):
        assert data['tracking_id'] == TASK_ID

    cargo_claims.claim_id = CLAIM_ID

    cargo_dispatch.waybill_ref = WAYBILL_REF
    # all visited points treat as finished
    for _, point in enumerate(
            [DEPOT_SRC, CLIENT_DST, DEPOT_DST, DEPOT_RETURN],
    ):
        cargo_dispatch.v1_waybill_info.waybill_points.append(
            WaybillPoint(
                claim_point_id=point.id,
                visit_status=VisitStatus('pending'),
                coords=point.point.coords,
            ),
        )

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    assert stop_waybill_tracking.times_called == 0

    delivery = deliveries.fetch_by_performer_id(PERFORMER_ID)
    delivery.status_ts = TS
    deliveries.add(delivery)

    mocked_time.sleep(43201)

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    assert stop_waybill_tracking.times_called == 1


@pytest.mark.experiments3(filename='experiments3.json')
async def test_stop_waybill_tracking_on_unable_to_fetch_waybill(
        stq_runner,
        testpoint,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
):
    cargo_claims.claim_id = CLAIM_ID
    cargo_dispatch.v1_waybill_info.raise_only_error(404)

    @testpoint('stop_waybill_tracking')
    def stop_waybill_tracking(data):
        assert data['tracking_id'] == TASK_ID

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    assert await stop_waybill_tracking.wait_call()

    cargo_dispatch.v1_waybill_info.raise_only_error(400)

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    assert await stop_waybill_tracking.wait_call()

    cargo_dispatch.v1_segment_info.raise_only_error(404)

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )
    assert await stop_waybill_tracking.wait_call()


@pytest.mark.experiments3(filename='experiments3.json')
async def test_position_tracking_stq_run_on_waybill_fetching(
        stq, stq_runner, cargo_claims, cargo_dispatch, deliveries,
):
    cargo_claims.claim_id = CLAIM_ID

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    assert stq.grocery_performer_watcher_position_tracking.times_called == 1
    delivery = deliveries.fetch_by_performer_id(PERFORMER_ID)

    assert is_subdict(
        stq.grocery_performer_watcher_position_tracking.next_call()['kwargs'],
        {'delivery_id': str(delivery.id)},
    )


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'delivery_status,  is_stop',
    [
        ('pickuping', False),
        ('delivering', False),
        ('delivery_arrived', False),
        ('returning', False),
        ('finished', True),
    ],
)
async def test_position_tracking_stop_on_delivery_finished(
        testpoint,
        stq_runner,
        driver_trackstory: DriverTrackstoryContext,
        cargo_dispatch: CargoDispatchContext,
        deliveries,
        is_stop,
        delivery_status,
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
        status=delivery_status,
        next_point=sample_point,
        waybill_ref=WAYBILL_REF,
        performer_id=PERFORMER_ID,
        depot_id=DEPOT_ID,
    )
    deliveries.add(delivery)

    await stq_runner.grocery_performer_watcher_position_tracking.call(
        task_id=TASK_ID, kwargs={'delivery_id': str(delivery.id)},
    )
    assert stop_position_tracking.times_called == (1 if is_stop else 0)


@pytest.mark.parametrize('transport_type', ['rover', 'not rover', None])
async def test_check_transport_type_kwarg(
        driver_trackstory: DriverTrackstoryContext,
        cargo_dispatch: CargoDispatchContext,
        stq_runner,
        load_json,
        deliveries,
        experiments3,
        transport_type,
):
    # parametrize experiment3
    exp = load_json('experiments3.json')
    experiments3.add_experiments_json(exp)
    # mock settings
    driver_trackstory.position.position = POINT_1.coords
    driver_trackstory.position.timestamp = TS
    driver_trackstory.position.performer_id = PERFORMER_ID

    cargo_dispatch.v1_waybill_arrive_at_point.point_id = DEPOT_SRC.id
    cargo_dispatch.v1_waybill_arrive_at_point.driver_id = PROFILE_ID
    cargo_dispatch.v1_waybill_arrive_at_point.park_id = PARK_ID
    # current delivery
    delivery = Delivery(
        status=DeliveryStatus('pickuping'),
        next_point=DEPOT_SRC,
        radius_ts=None,
        waybill_ref=WAYBILL_REF,
        performer_id=PERFORMER_ID,
        depot_id=DEPOT_ID,
        transport_type=transport_type,
    )
    deliveries.add(delivery)

    exp3_recorder = experiments3.record_match_tries(
        'grocery_performer_watcher_auto_confirm',
    )

    await stq_runner.grocery_performer_watcher_position_tracking.call(
        task_id=TASK_ID, kwargs={'delivery_id': str(delivery.id)},
    )
    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    matched_qwargs = match_tries[0].kwargs
    if transport_type:
        assert matched_qwargs['transport_type'] == transport_type
    else:
        assert 'transport_type' not in matched_qwargs


@pytest.mark.experiments3(filename='experiments3.json')
async def test_insert_claim(
        claims: ClaimsRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
):
    cargo_claims.claim_id = CLAIM_ID
    cargo_dispatch.waybill_ref = WAYBILL_REF

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    claim = claims.fetch_by_claim_id(CLAIM_ID)
    assert claim is not None
    assert claim.claim_id == CLAIM_ID
    assert claim.waybill_ref == WAYBILL_REF_1
    assert claim.version == 0


@pytest.mark.experiments3(filename='experiments3.json')
async def test_claim_update_cancel_old_waybill_on_change(
        deliveries: DeliveryRepository,
        claims: ClaimsRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
):
    cargo_claims.claim_id = CLAIM_ID
    cargo_dispatch.waybill_ref = WAYBILL_REF_1

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    claim = claims.fetch_by_claim_id(CLAIM_ID)
    assert claim is not None
    assert claim.claim_id == CLAIM_ID
    assert claim.waybill_ref == WAYBILL_REF_1
    assert claim.version == 0

    delivery = deliveries.fetch_by_performer_id_and_waybill_ref(
        performer_id=PERFORMER_ID, waybill_ref=WAYBILL_REF_1,
    )
    assert delivery is not None
    assert delivery.depot_id == DEPOT_ID
    assert delivery.waybill_ref == WAYBILL_REF_1
    assert delivery.status == 'new'

    # Change waybill for claim_id
    cargo_dispatch.waybill_ref = WAYBILL_REF_2

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    claim = claims.fetch_by_claim_id(CLAIM_ID)
    assert claim is not None
    assert claim.claim_id == CLAIM_ID
    assert claim.waybill_ref == WAYBILL_REF_2
    assert claim.version == 1

    # old delivery
    delivery = deliveries.fetch_by_performer_id_and_waybill_ref(
        performer_id=PERFORMER_ID, waybill_ref=WAYBILL_REF_1,
    )
    assert delivery is not None
    assert delivery.depot_id == DEPOT_ID
    assert delivery.waybill_ref == WAYBILL_REF_1
    assert delivery.status == 'canceled'

    # new delivery
    delivery = deliveries.fetch_by_performer_id_and_waybill_ref(
        performer_id=PERFORMER_ID, waybill_ref=WAYBILL_REF_2,
    )
    assert delivery is not None
    assert delivery.depot_id == DEPOT_ID
    assert delivery.waybill_ref == WAYBILL_REF_2
    assert delivery.status == 'new'


@pytest.mark.experiments3(filename='experiments3.json')
async def test_stq_reschedule_on_claim_version_changed(
        claims: ClaimsRepository,
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
        testpoint,
):
    @testpoint('waybill_changed')
    def waybill_tracking_waybill_changed(data):
        claim = claims.fetch_by_claim_id(CLAIM_ID)
        claim.version += 1
        claims.add(claim)

    @testpoint('waybill_tracking_continue')
    def waybill_tracking_continue(data):
        pass

    @testpoint('waybill_tracking_stale_object_error')
    def waybill_tracking_stale_object_error(data):
        pass

    cargo_claims.claim_id = CLAIM_ID
    cargo_dispatch.waybill_ref = WAYBILL_REF_1

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
    )

    # Change waybill for claim_id
    cargo_dispatch.waybill_ref = WAYBILL_REF_2

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
        expect_fail=False,
    )

    assert waybill_tracking_waybill_changed.times_called == 1
    assert waybill_tracking_stale_object_error.times_called == 1
    assert waybill_tracking_continue.times_called == 2


@pytest.mark.experiments3(filename='experiments3.json')
async def test_stq_failed_on_timeout(
        cargo_dispatch: CargoDispatchContext,
        cargo_claims: CargoClaimsContext,
        stq_runner,
):
    cargo_claims.claim_id = CLAIM_ID
    cargo_dispatch.waybill_ref = WAYBILL_REF_1
    cargo_dispatch.v1_waybill_info.raise_only_error(500)

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
            'depot_id': DEPOT_ID,
        },
        expect_fail=True,
    )


@pytest.mark.experiments3(filename='experiments3.json')
async def test_position_tracking_send_notifications(
        stq_runner,
        driver_trackstory: DriverTrackstoryContext,
        cargo_dispatch: CargoDispatchContext,
        deliveries,
        stq,
):
    # mock settings
    driver_trackstory.position.position = [0, 0]
    driver_trackstory.position.timestamp = TS
    driver_trackstory.position.performer_id = PERFORMER_ID

    # not finished status require next_point
    sample_point = DEPOT_SRC

    # finished delivery
    delivery = Delivery(
        status=DeliveryStatus.PICKUPING,
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

    assert (
        stq.grocery_performer_communications_push_notification.times_called
        == 2
    )


# TODO: integrate with test_updating_delivery_by_waybill_tracker
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
async def test_updating_delivery_status_ts_by_waybill_tracker(
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

    await stq_runner.grocery_performer_watcher_waybill_tracking.call(
        task_id=TASK_ID,
        kwargs={
            'performer_id': PERFORMER_ID,
            'claim_id': CLAIM_ID,
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
async def test_idempotency_notifications(
        stq_runner,
        driver_trackstory: DriverTrackstoryContext,
        cargo_dispatch: CargoDispatchContext,
        deliveries,
        stq,
):
    # mock settings
    driver_trackstory.position.position = [0, 0]
    driver_trackstory.position.timestamp = TS
    driver_trackstory.position.performer_id = PERFORMER_ID

    # not finished status require next_point
    sample_point = DEPOT_SRC

    # finished delivery
    delivery = Delivery(
        status=DeliveryStatus.PICKUPING,
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
    await stq_runner.grocery_performer_watcher_position_tracking.call(
        task_id=TASK_ID, kwargs={'delivery_id': str(delivery.id)},
    )

    assert (
        stq.grocery_performer_communications_push_notification.times_called
        == 2
    )
