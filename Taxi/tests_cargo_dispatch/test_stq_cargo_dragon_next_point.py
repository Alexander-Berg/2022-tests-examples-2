import datetime

import pytest


@pytest.mark.parametrize(
    ('segment_id', 'visit_order', 'sms_scheduled'),
    [
        ('seg3', ['p1'], True),
        ('seg3', ['p1', 'p2'], False),
        ('seg1', ['p1'], False),
        ('seg1', ['p1', 'p2', 'p3'], True),
    ],
)
async def test_sms_scheduled(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        segment_id,
        visit_order,
        sms_scheduled,
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point_id = None
    for point_id in visit_order:
        segment.set_point_visit_status(point_id, 'visited')
    point = segment.get_point(point_id)

    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': segment_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': False,
        },
    )
    if sms_scheduled:
        assert stq.cargo_claims_send_on_the_way_sms.times_called == 1
    else:
        assert stq.cargo_claims_send_on_the_way_sms.times_called == 0


@pytest.mark.parametrize(
    ('segment_id', 'visit_order', 'notify_taxi', 'expected_status'),
    [
        ('seg3', ['p1'], False, 'transporting'),
        ('seg3', ['p1', 'p2'], False, None),
        ('seg3', ['p1', 'p2'], True, 'complete'),
    ],
)
async def test_taxi_status_scheduled(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        segment_id,
        visit_order,
        notify_taxi,
        expected_status,
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point_id = None
    for point_id in visit_order:
        segment.set_point_visit_status(point_id, 'visited')
    point = segment.get_point(point_id)

    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': segment_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': notify_taxi,
        },
    )

    if expected_status is not None:
        assert stq.cargo_claims_xservice_change_status.times_called == 1
        stq_call = stq.cargo_claims_xservice_change_status.next_call()
        assert stq_call['kwargs']['new_status'] == expected_status
    else:
        assert stq.cargo_claims_xservice_change_status.times_called == 0


async def test_skipped_point(
        happy_path_state_performer_found,
        stq_runner,
        stq,
        dispatch_return_point,
        get_point_execution_by_visit_order,
        get_waybill_info,
        waybill_ref='waybill_smart_1',
        skipped_segment_id='seg1',
):
    # skip seg1
    waybill = (await get_waybill_info(waybill_ref)).json()
    cargo_order_id = waybill['diagnostics']['order_id']

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    response = await dispatch_return_point(
        waybill_ref, visit_order=1, comment='some performer comment',
    )
    assert response.status_code == 200

    # check for transporting if A1 skipped
    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': skipped_segment_id,
            'cargo_order_id': cargo_order_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': True,
        },
    )

    assert stq.cargo_claims_xservice_change_status.times_called == 1
    stq_call = stq.cargo_claims_xservice_change_status.next_call()
    assert stq_call['kwargs']['new_status'] == 'transporting'

    # no sms for A2
    assert stq.cargo_claims_send_on_the_way_sms.times_called == 0


@pytest.mark.skip('TODO fix claim_point_ids')
async def test_skipped_point_sms(
        happy_path_state_performer_found,
        stq_runner,
        stq,
        dispatch_return_point,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        get_waybill_info,
        waybill_ref='waybill_smart_1',
        skipped_segment_id='seg2',
):
    # set seg1 A1, A2 visited
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.set_point_visit_status('p1', 'visited')
    segment.set_point_visit_status('p2', 'visited')

    # skip seg2 A1
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    response = await dispatch_return_point(
        waybill_ref, visit_order=3, comment='some performer comment',
    )
    assert response.status_code == 200
    # fetch cargo_order_id
    waybill = (await get_waybill_info(waybill_ref)).json()
    cargo_order_id = waybill['diagnostics']['order_id']
    assert waybill == {}

    # check for transporting if A1 skipped
    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': skipped_segment_id,
            'cargo_order_id': cargo_order_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': False,
        },
    )

    # no need to change taxi status
    assert stq.cargo_claims_xservice_change_status.times_called == 0
    assert stq.cargo_claims_send_on_the_way_sms.times_called == 1


async def test_timers_calculated_for_chain(
        happy_path_chain_order,
        happy_path_claims_segment_db,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        mock_employee_timer,
        mock_order_cancel,
        mock_driver_trackstory,
        mock_claims_exchange_confirm,
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
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    # pickuped
    segment.set_point_visit_status('p1', 'visited')
    # dropped off
    segment.set_point_visit_status('p2', 'visited')

    point = await get_point_execution_by_visit_order(
        waybill_ref=first_waybill_ref, visit_order=2,
    )

    # cargo_dragon_next_point is set in segments/exchange/confirm
    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': segment_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': True,
        },
    )
    # check eta was calculated for first point of chain order
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=second_waybill_ref, visit_order=1,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'
    assert mock_employee_timer.handler.times_called == 1
    assert mock_employee_timer.last_request['point_from'] == [
        37.57839202,
        55.7350642,  # driver-trackstory position
    ]


@pytest.mark.parametrize(
    ('point_number', 'times_called'),
    [(0, 0), (1, 1), (2, 1), (3, 0), (4, 0), (5, 1), (6, 0)],
)
@pytest.mark.config(CARGO_DISPATCH_ENABLED_SET_CLAIM_EVENT_PROCESSING_STQ=True)
async def test_set_cargo_c2c_stq(
        happy_path_state_performer_found,
        stq_runner,
        stq,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        point_number,
        times_called,
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_C2_p6 (16) -> seg1_C1_p7 (17) ->
        seg2_C1_p3 (23)

    Here skip seq1.
    Tests eta would not be overwrited by notify_orders.
    """
    points = [
        {'segment': 'seg1', 'point': 'p1'},
        {'segment': 'seg1', 'point': 'p2'},
        {'segment': 'seg2', 'point': 'p1'},
        {'segment': 'seg1', 'point': 'p3'},
        {'segment': 'seg1', 'point': 'p4'},
        {'segment': 'seg1', 'point': 'p5'},
        {'segment': 'seg2', 'point': 'p2'},
    ]

    for i in range(point_number + 1):
        point = points[i]
        happy_path_claims_segment_db.get_segment(
            point['segment'],
        ).set_point_visit_status(point['point'], 'visited')

    point = await get_point_execution_by_visit_order(
        waybill_ref='waybill_smart_1', visit_order=point_number + 1,
    )

    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': point['segment_id'],
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': False,
        },
    )

    assert stq.claim_event_processing.times_called == times_called


async def test_payment_cancel_on_return(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        stq_runner,
        dispatch_confirm_point,
        dispatch_return_point,
        get_waybill_info,
        get_point_execution_by_visit_order,
        mock_claims_return,
        mock_claims_exchange_confirm,
        mock_payment_cancel,
        waybill_ref='waybill_smart_1',
):
    """
        Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_C2_p6 (16) -> seg1_C1_p7 (17) ->
        seg2_C1_p3 (23)

        Post payment order.
        Check payment is cancelled on driver /return.
    """
    waybill = (await get_waybill_info(waybill_ref)).json()
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.set_point_post_payment('p3')

    # Confirm all source points
    for visit_order in range(1, 4):
        await dispatch_confirm_point(waybill_ref, visit_order=visit_order)
    # Return on first destination point
    response = await dispatch_return_point(
        waybill_ref, visit_order=4, comment='some performer comment',
    )
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=4,
    )

    # check for transporting if A1 skipped
    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': 'seg1',
            'cargo_order_id': cargo_order_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': True,
        },
    )

    assert mock_payment_cancel.handler.times_called == 1
    assert mock_payment_cancel.requests[0].json == {
        'payment_id': '757849ca-2e29-45a6-84f7-d576603618bb',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_taxi_statuses_flow',
    consumers=['cargo-dispatch/taxi-statuses-flow'],
    clauses=[],
    default_value={'enabled': True, 'delay_ms': 1700},
    is_config=True,
)
async def test_change_status_delay(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mocked_time,
        segment_id='seg3',
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point_id = 'p1'
    segment.set_point_visit_status(point_id, 'visited')
    point = segment.get_point(point_id)

    await stq_runner.cargo_dragon_next_point.call(
        task_id='test',
        kwargs={
            'segment_id': segment_id,
            'claim_point_id': point['claim_point_id'],
            'notify_taxi': False,
        },
    )

    assert stq.cargo_claims_xservice_change_status.times_called == 1
    stq_call = stq.cargo_claims_xservice_change_status.next_call()
    assert stq_call['kwargs']['new_status'] == 'transporting'
    assert stq_call['eta'] == mocked_time.now() + datetime.timedelta(
        milliseconds=1700,
    )
