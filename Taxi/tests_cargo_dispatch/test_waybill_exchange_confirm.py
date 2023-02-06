import datetime

import psycopg2
import pytest

from testsuite.utils import matching


CLAIMS_POINT_BASE: dict = {'type': 'source', 'label': 'label', 'phones': []}

CLAIMS_ROUTE_POINT: dict = {
    'address': {'fullname': 'SEND IT TO ORDERS', 'coordinates': [1.0, 2.0]},
    **CLAIMS_POINT_BASE,
}

CLAIMS_NEW_ROUTE: list = [{'id': 1, **CLAIMS_ROUTE_POINT}]

CLAIMS_NEW_POINT: dict = {
    **CLAIMS_POINT_BASE,
    'need_confirmation': True,
    'visit_order': 1,
    'actions': [],
}


async def check_response_body(
        response_body,
        result: str = None,
        new_status: str = None,
        new_route: list = None,
        new_point: dict = None,
):
    if result is not None:
        assert response_body['result'] == result
    if new_status is not None:
        assert response_body['new_status'] == new_status
    if new_route is not None:
        assert response_body['new_route'] == new_route
    if new_point is not None:
        assert response_body.get('new_point') == new_point
    assert 'waybill_info' in response_body


def _check_response_points_eta(points, visit_order, eta):
    for point in points:
        if visit_order is not None and point['visit_order'] == visit_order:
            assert point['eta'] == eta
        else:
            assert 'eta' not in point


async def test_happy_path(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
):
    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point('waybill_fb_3')
    assert response.status_code == 200
    await check_response_body(response.json(), result='confirmed')


async def test_returning_to_delivered(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_exchange_confirm,
        dispatch_return_point,
        mock_claims_return,
        read_waybill_info,
        waybill_ref='waybill_fb_3',
):
    mock_claims_exchange_confirm(
        expected_request={
            'last_known_status': 'returning',
            'confirmation_code': '123456',
            'point_id': 32,
            'driver': {
                'driver_profile_id': matching.AnyString(),
                'park_id': matching.AnyString(),
            },
            'notify_taxi': False,
            'cargo_order_id': matching.AnyString(),
        },
        response={
            'result': 'confirmed',
            'new_status': 'complete',
            'new_claim_status': 'delivered',
        },
    )

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')
    response = await dispatch_return_point(waybill_ref, visit_order=2)

    response = await dispatch_confirm_point(
        waybill_ref, last_known_status='returning', visit_order=2,
    )
    assert response.status_code == 200


async def test_rejected(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
):
    mock_claims_exchange_confirm(
        response={
            'result': 'rejected',
            'new_status': 'pickup_confirmation',
            'new_claim_status': 'ready_for_pickup_confirmation',
            'new_route': CLAIMS_NEW_ROUTE,
        },
    )
    response = await dispatch_confirm_point('waybill_fb_3')
    assert response.status_code == 200
    await check_response_body(response.json(), result='rejected')


async def test_conflict(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        mockserver,
):
    mock_claims_exchange_confirm(
        response=mockserver.make_response(
            status=409,
            json={
                'code': 'state_mismatch',
                'message': 'confirmation conflict',
            },
        ),
    )
    response = await dispatch_confirm_point('waybill_fb_3')
    assert response.status_code == 409


async def test_destination_changes(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        mock_order_change_destination,
        run_notify_orders,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point(waybill_ref)
    assert response.status_code == 200

    await run_notify_orders()
    assert mock_order_change_destination.times_called == 1

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert mock_order_change_destination.next_call()['request'].json == {
        'order_id': matching.any_string,
        'dispatch_version': 2,
        'claim_id': 'claim_seg3',
        'segment_id': 'seg3',
        'claim_point_id': point['claim_point_id'],
        'idempotency_token': 'waybill_fb_3_32_2',
    }


async def test_new_point(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
):
    mock_claims_exchange_confirm(
        response={
            'result': 'rejected',
            'new_status': 'pickup_confirmation',
            'new_claim_status': 'ready_for_pickup_confirmation',
            'new_route': CLAIMS_NEW_ROUTE,
            'new_point': {'id': 2, **CLAIMS_NEW_POINT},
        },
    )
    response = await dispatch_confirm_point('waybill_fb_3')
    assert response.status_code == 200
    await check_response_body(response.json(), result='rejected')


async def test_send_driver(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    mock_claims_exchange_confirm(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'confirmation_code': '123456',
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'last_known_status': 'pickup_confirmation',
            'notify_taxi': False,
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_confirm_point('waybill_fb_3')
    assert response.status_code == 200


async def test_support(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_waybill_info,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    mock_claims_exchange_confirm(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'confirmation_code': '123456',
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'last_known_status': 'pickup_confirmation',
            'point_id': point['claim_point_id'],
            'support': {'comment': 'some comment', 'ticket': 'TICKET-100'},
            'notify_taxi': True,
        },
    )

    response = await dispatch_confirm_point(waybill_ref, with_support=True)
    assert response.status_code == 200

    waybill = await get_waybill_info(waybill_ref)
    assert waybill.json()['execution']['paper_flow']


async def test_paper_flow_410(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_waybill_info,
        waybill_ref='waybill_fb_3',
):
    mock_claims_exchange_confirm()

    response = await dispatch_confirm_point(waybill_ref, with_support=True)
    assert response.status_code == 200

    response = await dispatch_confirm_point(waybill_ref)
    assert response.status_code == 410


async def test_wrong_point(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        waybill_ref='waybill_fb_3',
):
    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point(waybill_ref, visit_order=2)
    assert response.status_code == 409


async def test_idempotency(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_exchange_confirm,
        waybill_ref='waybill_fb_3',
):
    mock_claims_exchange_confirm()

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')
    segment.set_point_visit_status('p2', 'visited')

    response = await dispatch_confirm_point(waybill_ref, visit_order=2)
    assert response.status_code == 200


@pytest.mark.parametrize('fail_logistics_dispatch', [False, True])
@pytest.mark.parametrize('is_approximate', [None, False, True])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={'enable': True, 'allow_no_eta_on_error': False},
)
@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_next_point_eta(
        mockserver,
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        fail_logistics_dispatch,
        is_approximate,
        taxi_cargo_dispatch,
        points_eta,
):
    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def _employee_timer(request):
        assert request.json == {
            'point_from': [37.5, 55.7],
            'point_to': [37.5, 55.7],
            'employer': 'eda',
            'park_driver_profile_id': 'park_id_1_driver_id_1',
        }
        if fail_logistics_dispatch:
            return mockserver.make_response(status=500, json={})
        return {
            'estimation_time_of_arrival': '2020-07-20T11:07:00+00:00',
            'estimation_distance': 7.77,
            'is_approximate': is_approximate,
        }

    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point('waybill_fb_3')
    if fail_logistics_dispatch:
        assert response.status_code == 500
    else:
        assert response.status_code == 200
        response_body = response.json()
        await check_response_body(
            response_body, result='confirmed', new_status='delivering',
        )
        _check_response_points_eta(
            response_body['waybill_info']['execution']['points'],
            2,
            '2020-07-20T11:07:00+00:00',
        )

    if fail_logistics_dispatch:
        assert points_eta('seg3_B1_p2', 'waybill_fb_3') == [(None, None, None)]
    else:
        pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
        assert points_eta('seg3_B1_p2', 'waybill_fb_3') == [
            (
                datetime.datetime(2020, 7, 20, 14, 7, tzinfo=pg_tz),
                7.77,
                is_approximate or False,
            ),
        ]

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/info', params={'waybill_external_ref': 'waybill_fb_3'},
    )
    assert response.status_code == 200
    response_body = response.json()
    if fail_logistics_dispatch:
        _check_response_points_eta(
            response_body['execution']['points'], None, None,
        )
    else:
        _check_response_points_eta(
            response_body['execution']['points'],
            2,
            '2020-07-20T11:07:00+00:00',
        )


@pytest.mark.parametrize('fail_logistics_dispatch', [False, True])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={'enable': True, 'allow_no_eta_on_error': True},
)
@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_next_point_eta__allow_no_eta_on_error(
        mockserver,
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        fail_logistics_dispatch,
):
    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def _employee_timer(request):
        assert request.json == {
            'point_from': [37.5, 55.7],
            'point_to': [37.5, 55.7],
            'employer': 'eda',
            'park_driver_profile_id': 'park_id_1_driver_id_1',
        }
        if fail_logistics_dispatch:
            return mockserver.make_response(status=500, json={})
        return {
            'estimation_time_of_arrival': '2020-07-20T11:07:00+00:00',
            'estimation_distance': 7.77,
        }

    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point('waybill_fb_3')
    assert response.status_code == 200
    response_body = response.json()
    await check_response_body(
        response_body, result='confirmed', new_status='delivering',
    )
    points = response_body['waybill_info']['execution']['points']
    if fail_logistics_dispatch:
        _check_response_points_eta(points, None, None)
    else:
        _check_response_points_eta(points, 2, '2020-07-20T11:07:00+00:00')


async def test_batch_order(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    mock_claims_exchange_confirm(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'confirmation_code': '123456',
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'notify_taxi': False,
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_confirm_point(waybill_ref)
    assert response.status_code == 200


async def test_updated_waybill(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    mock_claims_exchange_confirm(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'confirmation_code': '123456',
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'notify_taxi': False,
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_confirm_point(waybill_ref)
    assert response.status_code == 200


@pytest.mark.now('2020-07-20T11:09:40+00:00')
async def test_timers_calculated_for_chain(
        happy_path_chain_order,
        happy_path_claims_segment_db,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        read_waybill_info,
        mock_employee_timer,
        mock_order_cancel,
        mock_driver_trackstory,
        mock_claims_exchange_confirm,
        mock_order_change_destination,  # check this
        mock_order_set_eta,
        stq_runner,
        dispatch_confirm_point,
        segment_id='seg3',
        first_waybill_ref='waybill_fb_3',
        second_waybill_ref='waybill_smart_1',
):
    """
        Chain order for 'waybill_fb_3' (seg3) -> 'waybill_smart_1' (seg1, seg2)

        Check timers calculated for A1 point of 'waybill_smart_1'
        on completion of the 'waybill_fb_3'.
    """
    mock_employee_timer.expected_request = None
    # + 5sec + 50sec to arrive eta
    await exp_cargo_next_point_eta_settings(
        extra_eta_seconds=5, extra_eta_position_age_multiplier=0.5,
    )
    expected_eta = '2020-07-20T11:08:55+00:00'
    # pickuped
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_point_visit_status('p1', 'visited')

    # dropped off
    response = await dispatch_confirm_point(
        'waybill_fb_3', visit_order=2, driver_id='driver_id_1',
    )
    assert response.status_code == 200

    # check eta was calculated for first point of chain order
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=second_waybill_ref, visit_order=1,
    )
    assert next_point['eta'] == expected_eta
    assert mock_employee_timer.handler.times_called == 1
    assert mock_employee_timer.last_request['point_from'] == [
        37.57839202,
        55.7350642,  # driver-trackstory position
    ]

    # check eta is stored in cargo_orders for A1
    second_waybill = await read_waybill_info(second_waybill_ref)
    assert mock_order_set_eta.handler.times_called == 1
    assert (
        mock_order_set_eta.last_request['cargo_order_id']
        == second_waybill['diagnostics']['order_id']
    )
    assert (
        mock_order_set_eta.last_request['first_point_eta']['arrive_time']
        == expected_eta
    )
    assert (
        mock_order_set_eta.last_request['first_point_eta']['route_distance']
        == 8.88
    )


@pytest.mark.now('2020-07-20T11:09:40+00:00')
async def test_async_timers(
        happy_path_state_performer_found,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        taxi_cargo_dispatch,
        mock_employee_timer,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        experiments3,
        stq,
        mocked_time,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    """
        Async timers
    """
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

    response = await dispatch_confirm_point(
        'waybill_fb_3',
        visit_order=1,
        driver_id='driver_id_1',
        async_timer_supported=True,
    )
    assert response.status_code == 200

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
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
    assert stq_call['kwargs']['next_point_id'] == 32
    assert stq_call['kwargs']['waybill_ref'] == 'waybill_fb_3'

    stq_call = stq.cargo_courier_timers_calculation.next_call()
    assert stq_call['eta'] == mocked_time.now()
    assert stq_call['kwargs']['last_known_waybill_revision'] == 5
    assert stq_call['kwargs']['next_point_id'] == 32
    assert stq_call['kwargs']['waybill_ref'] == 'waybill_fb_3'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_pull_dispatch_settings',
    consumers=['cargo/pull-dispatch-settings'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {'init': {'arg_name': 'is_batch'}, 'type': 'bool'},
                        {
                            'init': {
                                'value': 6,
                                'arg_name': 'point_visit_order',
                                'arg_type': 'int',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enable': True,
                'confirm_both_same_points_together': True,
            },
        },
    ],
    default_value={'enable': True, 'confirm_both_same_points_together': False},
)
async def test_pull_dispatch(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        mock_claims_arrive_at_point,
        get_point_execution_by_visit_order,
        happy_path_claims_segment_db,
        waybill_ref='waybill_smart_1',
):
    # Prepare segments
    seg_1 = happy_path_claims_segment_db.get_segment('seg1')
    seg_1.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_1.set_point_visit_status('p1', 'visited')
    seg_1.set_point_visit_status('p2', 'visited')
    seg_1.set_point_visit_status('p3', 'visited')
    seg_1.set_point_visit_status('p4', 'visited')

    seg_2 = happy_path_claims_segment_db.get_segment('seg2')
    seg_2.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_2.set_point_visit_status('p1', 'visited')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=6,
    )
    mock_confirm = mock_claims_exchange_confirm()
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=7,
    )
    mock_arrive = mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'point_id': next_point['claim_point_id'],
        },
    )

    response = await dispatch_confirm_point(waybill_ref, visit_order=6)
    assert response.status_code == 200
    assert mock_arrive.times_called == 1

    first_confirm = mock_confirm.next_call()['request']
    assert first_confirm.json == {
        'cargo_order_id': matching.AnyString(),
        'confirmation_code': '123456',
        'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        'notify_taxi': False,
        'point_id': current_point['claim_point_id'],
    }
    assert first_confirm.query == {'segment_id': 'seg1'}

    second_confirm = mock_confirm.next_call()['request']
    assert second_confirm.json == {
        'cargo_order_id': matching.AnyString(),
        'confirmation_code': '123456',
        'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        'notify_taxi': False,
        'point_id': next_point['claim_point_id'],
    }
    assert second_confirm.query == {'segment_id': 'seg2'}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_pull_dispatch_settings',
    consumers=['cargo/pull-dispatch-settings'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {'init': {'arg_name': 'is_batch'}, 'type': 'bool'},
                        {
                            'init': {'arg_name': 'is_going_back'},
                            'type': 'bool',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enable': True,
                'confirm_both_same_points_together': True,
            },
        },
    ],
    default_value={'enable': True, 'confirm_both_same_points_together': False},
)
async def test_pull_dispatch_3_in_batch(
        happy_path_state_performer_found,
        create_seg_pull_dispatch,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        mock_claims_exchange_confirm,
        mock_claims_arrive_at_point,
        dispatch_confirm_point,
        waybill_from_segments_pull_dispatch,
        request_waybill_propose,
):
    waybill_ref = 'waybill_pull_dispatch'
    await create_seg_pull_dispatch(7)
    await create_seg_pull_dispatch(8)
    await create_seg_pull_dispatch(9)
    proposal = await waybill_from_segments_pull_dispatch(
        'fallback_router', 'waybill_pull_dispatch', 'seg7', 'seg8', 'seg9',
    )
    response = await request_waybill_propose(proposal)
    assert response.status_code == 200

    seg_1 = happy_path_claims_segment_db.get_segment('seg7')
    seg_1.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_1.set_point_visit_status('p1', 'visited')
    seg_1.set_point_visit_status('p2', 'visited')
    seg_1.set_point_visit_status('p3', 'visited')

    seg_2 = happy_path_claims_segment_db.get_segment('seg8')
    seg_2.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_2.set_point_visit_status('p1', 'visited')
    seg_2.set_point_visit_status('p2', 'visited')

    seg_3 = happy_path_claims_segment_db.get_segment('seg9')
    seg_3.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_3.set_point_visit_status('p1', 'visited')
    seg_3.set_point_visit_status('p2', 'visited')

    current_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=7,
    )
    mock_confirm = mock_claims_exchange_confirm()
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=8,
    )
    assert next_point['segment_id'] == 'seg8'
    mock_arrive = mock_claims_arrive_at_point()

    response = await dispatch_confirm_point(waybill_ref, visit_order=7)
    assert response.status_code == 200
    assert mock_arrive.times_called == 2

    first_confirm = mock_confirm.next_call()['request']
    assert first_confirm.json == {
        'confirmation_code': '123456',
        'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        'notify_taxi': False,
        'point_id': current_point['claim_point_id'],
    }
    assert first_confirm.query == {'segment_id': 'seg7'}

    second_confirm = mock_confirm.next_call()['request']
    assert second_confirm.json == {
        'confirmation_code': '123456',
        'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        'notify_taxi': False,
        'point_id': next_point['claim_point_id'],
    }
    assert second_confirm.query == {'segment_id': 'seg8'}

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=9,
    )
    third_confirm = mock_confirm.next_call()['request']
    assert third_confirm.json == {
        'confirmation_code': '123456',
        'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
        'notify_taxi': False,
        'point_id': next_point['claim_point_id'],
    }
    assert third_confirm.query == {'segment_id': 'seg9'}


async def test_waybill_mark_paper_flow(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    response = await dispatch_confirm_point(waybill_ref, True)
    assert response.status_code == 200
    assert response.json()['waybill_info']['execution']['paper_flow']


async def test_waybill_not_mark_paper_flow_if_no_conformation_needed(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_exchange_confirm,
        waybill_ref='waybill_smart_1',
):
    for segment_id in ('seg1', 'seg2', 'seg3'):
        segment = happy_path_claims_segment_db.get_segment(segment_id)
        for point in segment.json['points']:
            point['need_confirmation'] = False

    response = await dispatch_confirm_point(waybill_ref, True)
    assert response.status_code == 200
    assert not response.json()['waybill_info']['execution']['paper_flow']


async def test_batch_confirm_source_point_in_any_order(
        dispatch_confirm_point,
        happy_path_state_performer_found,
        mock_claims_exchange_confirm,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    # Confirm point A2
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    mock_claims_exchange_confirm(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'confirmation_code': '123456',
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'notify_taxi': False,
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_confirm_point(waybill_ref, visit_order=2)
    assert response.status_code == 200

    # Confirm point A1
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    mock_claims_exchange_confirm(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'confirmation_code': '123456',
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'notify_taxi': False,
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_confirm_point(waybill_ref, visit_order=1)
    assert response.status_code == 200
