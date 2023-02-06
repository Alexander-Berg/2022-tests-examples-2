import datetime

import psycopg2
import pytest

from testsuite.utils import matching


@pytest.fixture(name='get_waybill_point_comment')
async def _get_waybill_point_comment(pgsql):
    def _wrapper(segment_point_id: str):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            """
            SELECT performer_comment
            FROM cargo_dispatch.waybill_points
            WHERE point_id = %s
            """,
            (segment_point_id,),
        )
        return cursor.fetchall()[0][0]

    return _wrapper


async def check_response_body(
        response_body, result: str, new_status: str = None,
):
    assert response_body['result'] == result
    if new_status is not None:
        assert response_body['new_status'] == new_status
    assert 'waybill_info' in response_body


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_patch_setcar_version_settings',
    consumers=['cargo/patch-setcar-version-settings'],
    clauses=[],
    default_value={
        'update_on_performer_found': False,
        'update_on_return_with_support': True,
    },
)
@pytest.mark.parametrize('with_support', [False, True])
async def test_happy_path(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        get_point_execution_by_visit_order,
        with_support,
        stq,
        waybill_ref='waybill_fb_3',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )

    mock_expected_request = {
        'cargo_order_id': matching.AnyString(),
        'last_known_status': 'pickup_confirmation',
        'point_id': current_point['claim_point_id'],
    }

    support = None
    if with_support:
        support = {'ticket': '', 'comment': 'some comment'}
        mock_expected_request['support'] = support
    else:
        mock_expected_request['driver'] = {
            'driver_profile_id': '789',
            'park_id': 'park_id_1',
        }

    mock_claims_return(expected_request=mock_expected_request)
    stq.cargo_route_watch.flush()
    response = await dispatch_return_point(
        waybill_ref, visit_order=2, support=support, create_ticket=False,
    )
    assert response.status_code == 200
    await check_response_body(response.json(), result='confirmed')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert current_point['visit_status'] == 'skipped'
    assert current_point['is_resolved']
    assert current_point['is_return_required']

    assert stq.cargo_route_watch.times_called == 2
    assert (
        stq.cargo_route_watch.next_call()['kwargs']['reason'] == 'next_point'
    )

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called
        == with_support
    )
    if with_support:
        stq_call = (
            stq.cargo_increment_and_update_setcar_state_version.next_call()
        )
        assert stq_call['kwargs'] == {
            'cargo_order_id': matching.AnyString(),
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'log_extra': {'_link': matching.AnyString()},
        }


async def test_blocked_restriction(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        get_point_execution_by_visit_order,
        stq,
        waybill_ref='waybill_fb_3',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    mock_claims_return(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'last_known_status': 'pickup_confirmation',
            'point_id': current_point['claim_point_id'],
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        },
    )
    response = await dispatch_return_point(
        waybill_ref, visit_order=2, create_ticket=True,
    )
    assert response.status_code == 403
    expected_stq_kwargs = {
        'cargo_order_id': matching.AnyString(),
        'driver_phone_id': '+70000000000_id',
        'log_extra': {'_link': matching.AnyString()},
        'request_id': matching.AnyString(),
        'support_meta': {
            'description': (
                'Исполнитель решил инициировать возврат, необходимо '
                'подтверждение.'
            ),
            'queue': 'SUPPARTNERS',
            'summary': 'Возврат от исполнителя',
            'tags': [],
        },
        'taxi_order_id': matching.AnyString(),
        'waybill_ref': 'waybill_fb_3',
    }
    assert stq.support_info_cargo_callback_on_expired.times_called == 1
    assert (
        stq.support_info_cargo_callback_on_expired.next_call()['kwargs']
        == expected_stq_kwargs
    )


async def test_support_request(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    mock_claims_return(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'last_known_status': 'pickup_confirmation',
            'point_id': current_point['claim_point_id'],
            'support': {'comment': 'some_comment', 'ticket': 'TESTBAKEND-1'},
        },
    )
    response = await dispatch_return_point(
        waybill_ref,
        visit_order=2,
        support={'comment': 'some_comment', 'ticket': 'TESTBAKEND-1'},
    )
    assert response.status_code == 200
    await check_response_body(response.json(), result='confirmed')


@pytest.mark.parametrize('is_approximate', [None, False, True])
@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_next_point_eta(
        mockserver,
        pgsql,
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        mock_claims_return,
        mock_employee_timer,
        exp_cargo_next_point_eta_settings,
        is_approximate,
        points_eta,
        waybill_ref='waybill_smart_1',
        first_destination_visit_order=4,
):
    mock_employee_timer.is_approximate = is_approximate

    segment_1 = happy_path_claims_segment_db.get_segment('seg1')
    segment_1.set_point_visit_status('p1', 'visited')
    segment_1.set_point_visit_status('p2', 'visited')
    segment_2 = happy_path_claims_segment_db.get_segment('seg2')
    segment_2.set_point_visit_status('p1', 'visited')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=first_destination_visit_order,
    )
    mock_claims_return(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'point_id': current_point['claim_point_id'],
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        },
    )

    response = await dispatch_return_point(
        waybill_ref, visit_order=first_destination_visit_order,
    )
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )

    assert mock_employee_timer.handler.times_called == 1
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=first_destination_visit_order + 1,
    )

    pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
    assert points_eta(next_point['point_id'], waybill_ref) == [
        (
            datetime.datetime(2020, 7, 20, 14, 8, tzinfo=pg_tz),
            8.88,
            is_approximate or False,
        ),
    ]


async def test_batch_order(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
        first_destination_visit_order=4,
):
    segment_1 = happy_path_claims_segment_db.get_segment('seg1')
    segment_1.set_point_visit_status('p1', 'visited')
    segment_1.set_point_visit_status('p2', 'visited')
    segment_2 = happy_path_claims_segment_db.get_segment('seg2')
    segment_2.set_point_visit_status('p1', 'visited')

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=first_destination_visit_order,
    )
    mock_claims_return(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'point_id': point['claim_point_id'],
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        },
    )
    response = await dispatch_return_point(
        waybill_ref, visit_order=first_destination_visit_order,
    )
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )


async def test_batch_skip_source_point(
        happy_path_state_performer_found,
        dispatch_return_point,
        stq,
        get_waybill_info,
        get_point_execution_by_visit_order,
        get_waybill_point_comment,
        exp_cargo_next_point_eta_settings,
        mock_employee_timer,
        waybill_ref='waybill_smart_1',
):
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )

    # check for point status
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    assert point['is_resolved']
    assert point['visit_status'] == 'skipped'
    assert point['resolution'] == {'is_visited': False, 'is_skipped': True}
    assert stq.cargo_dragon_next_point.times_called == 2

    # check for segment status
    response = await get_waybill_info(waybill_ref)
    execution = response.json()['execution']
    for segment in execution['segments']:
        if segment['id'] == 'seg1':
            assert segment['is_skipped']
        else:
            assert not segment['is_skipped']

    # check eta is set for a3 (a1, a2 are skipped)
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'


@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_batch_skip_last_source_point(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_employee_timer,
        dispatch_return_point,
        stq,
        get_point_execution_by_visit_order,
        exp_cargo_next_point_eta_settings,
        waybill_ref='waybill_smart_1',
):
    segment_1 = happy_path_claims_segment_db.get_segment('seg1')
    segment_1.set_point_visit_status('p1', 'visited')
    segment_1.set_point_visit_status('p2', 'visited')

    response = await dispatch_return_point(waybill_ref, visit_order=3)
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )

    # check for point status
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    assert point['is_resolved']
    assert point['visit_status'] == 'skipped'
    assert point['resolution'] == {'is_visited': False, 'is_skipped': True}
    assert stq.cargo_dragon_next_point.times_called == 2
    assert (
        stq.cargo_dragon_next_point.next_call()['kwargs']['cargo_order_id']
        == matching.any_string
    )

    # seg1_A1, seg1_A2 are visited, seg2_A1 is skipped, check eta
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=4,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'


async def test_source_return_last_segment(
        happy_path_state_performer_found,
        dispatch_return_point,
        get_point_execution_by_visit_order,
        get_waybill_point_comment,
        waybill_ref='waybill_smart_1',
):
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200

    # check for last segment
    response = await dispatch_return_point(waybill_ref, visit_order=3)
    assert response.status_code == 409


async def test_source_return_comment(
        happy_path_state_performer_found,
        dispatch_return_point,
        stq,
        get_point_execution_by_visit_order,
        get_waybill_point_comment,
        waybill_ref='waybill_smart_1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    response = await dispatch_return_point(
        waybill_ref, visit_order=1, comment='some performer comment',
    )
    assert response.status_code == 200

    # check comment
    assert (
        get_waybill_point_comment(point['point_id'])
        == 'some performer comment'
    )


async def test_waybill_building_version(
        happy_path_state_performer_found,
        dispatch_return_point,
        mock_claims_return,
        run_choose_routers,
        propose_from_segments,
        run_choose_waybills,
        run_create_orders,
        mock_claim_bulk_update_state,
        taxi_cargo_dispatch_monitor,
        run_notify_claims,
        taxi_cargo_dispatch,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
        segment_id='seg1',
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200

    await run_choose_routers()
    await propose_from_segments(
        'smart_router', 'waybill_smart_1_2', segment_id,
    )
    result = await run_choose_waybills()
    assert result['stats']['accepted-waybills'] == 1
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await run_create_orders(should_set_stq=True)
    result = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert result['stats']['committed-orders'] == 1

    result = await run_notify_claims(should_set_stq=True)
    assert result['stats']['segments-updated-count'] > 0


async def test_skip_segment_idempotency(
        happy_path_state_performer_found,
        dispatch_return_point,
        get_point_execution_by_visit_order,
):
    waybill_ref = 'waybill_smart_1'

    # Skip segment
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )

    # Second request
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )


@pytest.fixture(name='reverse_happy_path_destinations')
def _reverse_happy_path_destinations(happy_path_context):
    happy_path_context.proposal.reverse_destinations = True


@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_batch_skip_last_source_point_eta_next_segment(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_employee_timer,
        dispatch_return_point,
        stq,
        get_point_execution_by_visit_order,
        exp_cargo_next_point_eta_settings,
        waybill_ref='waybill_smart_1',
):
    segment_1 = happy_path_claims_segment_db.get_segment('seg1')
    segment_1.set_point_visit_status('p1', 'visited')
    segment_1.set_point_visit_status('p2', 'visited')

    response = await dispatch_return_point(waybill_ref, visit_order=3)
    assert response.status_code == 200
    await check_response_body(
        response.json(), result='confirmed', new_status='segment_status',
    )

    # seg1_A1, seg1_A2 are visited, seg2_A1, seg2_B1 are skipped
    # check for eta on first destination point of first segment
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=4,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'


async def test_eta_for_return_points(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        mock_employee_timer,
        get_point_execution_by_visit_order,
        exp_cargo_next_point_eta_settings,
        waybill_ref='waybill_fb_3',
):
    """
        waybill_fb_3:
            seg3_A1_p1 (31) -> seg3_B1_p2 (32) -> seg3_A1_p3 (33)
    """
    mock_claims_return()

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    response = await dispatch_return_point(waybill_ref, visit_order=2)
    assert response.status_code == 200
    await check_response_body(response.json(), result='confirmed')

    # check for eta for return point
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'


async def test_eta_for_return_points_batch(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_employee_timer,
        mock_claims_return,
        mock_claims_exchange_confirm,
        dispatch_return_point,
        dispatch_confirm_point,
        stq,
        get_point_execution_by_visit_order,
        exp_cargo_next_point_eta_settings,
        waybill_ref='waybill_smart_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (12) -> seg1_A1_p7 (11) ->
        seg2_C1_p3 (23)

    Here skip seq1.
    """
    mock_claims_return()
    mock_claims_exchange_confirm()

    segment_1 = happy_path_claims_segment_db.get_segment('seg1')
    segment_1.set_point_visit_status('p1', 'visited')
    segment_1.set_point_visit_status('p2', 'visited')
    segment_2 = happy_path_claims_segment_db.get_segment('seg2')
    segment_2.set_point_visit_status('p1', 'visited')

    for visit_order in range(4, 10):
        point = await get_point_execution_by_visit_order(
            waybill_ref=waybill_ref, visit_order=visit_order,
        )

        if point['type'] == 'destination':
            response = await dispatch_return_point(
                waybill_ref, visit_order=visit_order,
            )
            assert response.status_code == 200
            await check_response_body(
                response.json(),
                result='confirmed',
                new_status='segment_status',
            )
        elif point['type'] == 'return':
            response = await dispatch_confirm_point(
                waybill_ref, visit_order=visit_order,
            )
            assert response.status_code == 200
            await check_response_body(
                response.json(), result='confirmed', new_status='delivering',
            )
        else:
            assert False, point['type'] + ' not expected'

        # check for eta on first destination point of first segment
        next_point = await get_point_execution_by_visit_order(
            waybill_ref=waybill_ref, visit_order=visit_order + 1,
        )
        point_id = next_point['point_id']
        assert (
            next_point.get('eta') == '2020-07-20T11:08:00+00:00'
        ), f'Bad eta for point #{visit_order + 1} : {point_id}'


@pytest.mark.now('2020-07-20T11:09:40+00:00')
async def test_async_timers(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        taxi_cargo_dispatch,
        mock_employee_timer,
        mock_claims_return,
        dispatch_return_point,
        experiments3,
        stq,
        mocked_time,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    """
        Async timers
    """
    mock_claims_return()
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_next_point_eta_settings',
        consumers=['cargo-dispatch/taximeter-actions'],
        clauses=[],
        default_value={
            'enable': True,
            'allow_no_eta_on_error': False,
            'async_eta_calculation_enabled': True,
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    # Set first point visited
    segment_1 = happy_path_claims_segment_db.get_segment(segment_id)
    segment_1.set_point_visit_status('p1', 'visited')

    response = await dispatch_return_point(
        waybill_ref,
        visit_order=2,
        driver_id='driver_id_1',
        async_timer_supported=True,
    )
    assert response.status_code == 200

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    assert 'eta' not in next_point
    assert next_point['eta_calculation_awaited']

    # Do not calculate timers right now
    assert mock_employee_timer.handler.times_called == 0

    # Set stq
    assert stq.cargo_courier_timers_calculation.times_called == 2

    stq_call = stq.cargo_courier_timers_calculation.next_call()
    assert stq_call['eta'] == mocked_time.now() + datetime.timedelta(
        milliseconds=10000,
    )
    assert stq_call['kwargs']['last_known_waybill_revision'] == 5
    assert stq_call['kwargs']['next_point_id'] == 33
    assert stq_call['kwargs']['waybill_ref'] == 'waybill_fb_3'

    stq_call = stq.cargo_courier_timers_calculation.next_call()
    assert stq_call['eta'] == mocked_time.now()
    assert stq_call['kwargs']['last_known_waybill_revision'] == 5
    assert stq_call['kwargs']['next_point_id'] == 33
    assert stq_call['kwargs']['waybill_ref'] == 'waybill_fb_3'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_patch_setcar_version_settings',
    consumers=['cargo/patch-setcar-version-settings'],
    clauses=[],
    default_value={
        'update_on_performer_found': False,
        'update_on_return_with_support': True,
    },
)
async def test_skip_not_current_point_with_support(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        get_point_execution_by_visit_order,
        stq,
        waybill_ref='waybill_smart_1',
):
    #  Client wants to skip random point (not current)
    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=5,
    )
    mock_claims_return(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'point_id': current_point['claim_point_id'],
            'support': {'comment': 'Клиент отменил заказ', 'ticket': ''},
        },
    )
    stq.cargo_route_watch.flush()
    response = await dispatch_return_point(
        waybill_ref,
        visit_order=5,
        support={'comment': 'Клиент отменил заказ', 'ticket': ''},
    )
    assert response.status_code == 200
    await check_response_body(response.json(), result='confirmed')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=5,
    )
    assert current_point['visit_status'] == 'skipped'
    assert current_point['is_resolved']
    assert current_point['is_return_required']

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    stq_call = stq.cargo_increment_and_update_setcar_state_version.next_call()
    assert stq_call['kwargs'] == {
        'cargo_order_id': matching.AnyString(),
        'driver_profile_id': 'driver_id_1',
        'park_id': 'park_id_1',
        'log_extra': {'_link': matching.AnyString()},
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_patch_setcar_version_settings',
    consumers=['cargo/patch-setcar-version-settings'],
    clauses=[],
    default_value={
        'update_on_performer_found': False,
        'update_on_return': True,
    },
)
async def test_skip_updates_setcar_version(
        dispatch_return_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_return,
        get_point_execution_by_visit_order,
        stq,
        waybill_ref='waybill_smart_1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    mock_claims_return(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'point_id': point['claim_point_id'],
        },
    )

    response = await dispatch_return_point(waybill_ref, visit_order=3)
    assert response.status_code == 200
    await check_response_body(response.json(), result='confirmed')

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    assert point['visit_status'] == 'skipped'
    assert point['is_resolved']
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
