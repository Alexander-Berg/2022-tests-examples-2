from testsuite.utils import matching


async def do_test_basic(
        happy_path_claims_segment_db,
        mock_order_cancel,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        get_segment_info,
        get_waybill_info,
        *,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    happy_path_claims_segment_db.cancel_segment_by_user(segment_id)
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    result = await run_notify_orders()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert result['stats']['waybills-for-handling'] == 1
    assert stats['stats']['resolved'] == 1

    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1

    assert mock_order_cancel.handler.times_called == 1

    segment = await get_segment_info(segment_id)
    waybill = (await get_waybill_info(waybill_ref)).json()

    assert segment['dispatch']['status'] == 'resolved'
    assert segment['dispatch']['resolved']

    assert waybill['dispatch']['resolution'] == 'cancelled'
    assert waybill['dispatch']['status'] == 'resolved'


async def test_basic_created(
        mock_order_cancel,
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        get_segment_info,
        get_waybill_info,
):
    await do_test_basic(
        happy_path_claims_segment_db,
        mock_order_cancel,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        get_segment_info,
        get_waybill_info,
    )


async def test_basic_performer_found(
        mock_order_cancel,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        get_segment_info,
        get_waybill_info,
):
    await do_test_basic(
        happy_path_claims_segment_db,
        mock_order_cancel,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        get_segment_info,
        get_waybill_info,
    )


async def test_cancel_segment_in_batch_1(
        mock_order_change_destination,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        get_segment_info,
        read_waybill_info,
        get_point_execution_by_visit_order,
        mock_driver_trackstory,
        mock_employee_timer,
        exp_cargo_next_point_eta_settings,
        stq,
        waybill_ref='waybill_smart_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (16) -> seg1_A1_p7 (17) ->
        seg2_C1_p3 (23)

    Here skip seq1.
    """
    mock_employee_timer.expected_request = None
    stq.cargo_route_watch.flush()

    # Client cancel claim with seg1
    happy_path_claims_segment_db.cancel_segment_by_user('seg1')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    # Check segments and waybill statuses
    cancelled_segment = await get_segment_info('seg1')
    assert cancelled_segment['dispatch']['status'] == 'resolved'
    assert cancelled_segment['dispatch']['resolved']

    second_segment = await get_segment_info('seg2')
    assert second_segment['dispatch']['status'] == 'wait_for_resolution'
    assert not second_segment['dispatch']['resolved']

    waybill = await read_waybill_info(waybill_ref)
    assert 'resolution' not in waybill['dispatch']
    assert waybill['dispatch']['status'] == 'processing'

    # Skip first point
    happy_path_claims_segment_db.get_segment('seg1')

    # instead of handle_processing job
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    result = await run_notify_orders()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert stats['stats']['resolved'] == 0

    assert mock_order_change_destination.times_called == 1
    assert mock_order_change_destination.next_call()['request'].json == {
        'order_id': matching.any_string,
        'dispatch_version': 2,
        'claim_id': 'claim_seg2',
        'segment_id': 'seg2',
        'claim_point_id': 21,
        'idempotency_token': 'waybill_smart_1_21_3',
    }

    # Initiate client ETAs recalculation
    assert stq.cargo_route_watch.times_called == 1
    route_watch_task_kwargs = stq.cargo_route_watch.next_call()['kwargs']
    assert route_watch_task_kwargs['waybill_ref'] == waybill_ref
    assert route_watch_task_kwargs['reason'] == 'waybill_changed'

    # Change taxi status to transporting
    assert stq.cargo_claims_xservice_change_status.times_called == 1
    stq_call = stq.cargo_claims_xservice_change_status.next_call()
    assert stq_call['kwargs']['new_status'] == 'transporting'
    assert stq_call['kwargs']['driver_id'] == 'driver_id_1'

    # check for eta on first point of second segment
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'
    assert mock_employee_timer.last_request['point_from'] == [
        37.57839202,
        55.7350642,  # driver-trackstory position
    ]


async def test_cancel_segment_in_batch_2(
        mock_order_change_destination,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_employee_timer,
        run_claims_segment_replication,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_notify_orders,
        get_segment_info,
        read_waybill_info,
        stq,
        waybill_ref='waybill_smart_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (12) -> seg1_A1_p7 (11) ->
        seg2_C1_p3 (23)

    Here skip seq2.
    """
    stq.cargo_route_watch.flush()

    # Client cancel claim with seg2
    happy_path_claims_segment_db.cancel_segment_by_user('seg2')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    # Check segments and waybill statuses
    cancelled_segment = await get_segment_info('seg2')
    assert cancelled_segment['dispatch']['status'] == 'resolved'
    assert cancelled_segment['dispatch']['resolved']

    second_segment = await get_segment_info('seg1')
    assert second_segment['dispatch']['status'] == 'wait_for_resolution'
    assert not second_segment['dispatch']['resolved']

    waybill = await read_waybill_info(waybill_ref)
    assert 'resolution' not in waybill['dispatch']
    assert waybill['dispatch']['status'] == 'processing'

    # instead of handle_processing job
    # Do not change destination because it is first point
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert stats['stats']['resolved'] == 0
    assert mock_order_change_destination.times_called == 0
    assert stq.cargo_claims_xservice_change_status.times_called == 0

    # Initiate client ETAs recalculation
    assert stq.cargo_route_watch.times_called == 1
    route_watch_task_kwargs = stq.cargo_route_watch.next_call()['kwargs']
    assert route_watch_task_kwargs['waybill_ref'] == waybill_ref
    assert route_watch_task_kwargs['reason'] == 'waybill_changed'


async def test_both_batch_segments_cancelled(
        mock_order_change_destination,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        read_waybill_info,
        stq,
        mock_order_cancel,
):
    stq.cargo_route_watch.flush()

    # Client cancel claim with seg2
    happy_path_claims_segment_db.cancel_segment_by_user('seg2')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    # First notify orders
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert mock_order_cancel.handler.times_called == 0

    # Client cancel claim with seg1
    happy_path_claims_segment_db.cancel_segment_by_user('seg1')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    # Instead of handle_processing job
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert stats['stats']['resolved'] == 1
    assert mock_order_cancel.handler.times_called == 0

    waybill = await read_waybill_info('waybill_smart_1')
    assert waybill['dispatch']['resolution'] == 'cancelled'
    assert waybill['dispatch']['status'] == 'resolved'

    # Second notify orders
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert mock_order_cancel.handler.times_called == 1

    assert mock_order_change_destination.times_called == 0
    assert stq.cargo_claims_xservice_change_status.times_called == 0


async def test_cancelled_with_items_on_hands(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_notify_orders,
        get_segment_info,
        get_waybill_info,
        mock_order_change_destination,
        stq,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    """
        Waybill 'waybill_fb_3':

        seg3_A1_p1 (31) -> seg3_B1_p2 (32) -> seg3_A1_p3 (33, return)

        Order with optional return, performer visit A1 after that client
        cancels A1.
        taxi_order_id should be completed (full price for performer)

        Job running order:
        run_notify_orders -> run_notify_orders
    """
    happy_path_claims_segment_db.set_segment_point_visit_status(
        'seg3', 'p1', 'visited', is_caused_by_user=True,
    )
    await run_claims_segment_replication()
    await run_notify_orders()
    await run_notify_orders()

    stq.cargo_route_watch.flush()

    happy_path_claims_segment_db.cancel_segment_by_user(segment_id)
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    # Instead of handle_processing job
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert stats['stats']['resolved'] == 1

    segment = await get_segment_info(segment_id)
    assert segment['dispatch']['status'] == 'resolved'
    assert segment['dispatch']['resolved']

    waybill = (await get_waybill_info(waybill_ref)).json()
    assert waybill['dispatch']['resolution'] == 'complete'
    assert waybill['dispatch']['status'] == 'resolved'

    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1

    # Change taxi status to complete
    assert stq.cargo_claims_xservice_change_status.times_called == 1
    stq_call = stq.cargo_claims_xservice_change_status.next_call()
    assert stq_call['kwargs']['new_status'] == 'complete'
    assert stq_call['kwargs']['driver_id'] == 'driver_id_1'

    # Stop watching for courier

    # TODO: we have duplicated call notify_orders:
    # https://st.yandex-team.ru/CARGODEV-12804
    # assert stq.cargo_route_watch.times_called == 1
    assert stq.cargo_route_watch.times_called >= 1
    route_watch_task_kwargs = stq.cargo_route_watch.next_call()['kwargs']
    assert route_watch_task_kwargs['waybill_ref'] == waybill_ref
    assert route_watch_task_kwargs['reason'] == 'waybill_changed'


async def test_batch_eta_no_overwrite(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_notify_orders,
        get_point_execution_by_visit_order,
        mock_order_change_destination,
        mock_claims_exchange_confirm,
        mock_driver_trackstory,
        mock_employee_timer,
        exp_cargo_next_point_eta_settings,
        dispatch_confirm_point,
        waybill_ref='waybill_smart_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (16) -> seg1_A1_p7 (17) ->
        seg2_C1_p3 (23)

    Here skip seq1.
    Tests eta would not be overwrited by notify_orders.
    """
    mock_employee_timer.expected_request = None
    mock_claims_exchange_confirm()

    # Client cancel claim with seg1
    happy_path_claims_segment_db.cancel_segment_by_user('seg1')

    mock_employee_timer.eta = '2020-07-20T11:09:00+00:00'
    response = await dispatch_confirm_point(waybill_ref, visit_order=3)
    assert response.status_code == 200

    mock_employee_timer.eta = '2020-08-20T11:08:11+11:00'
    await run_notify_orders()

    # check eta was not overwrited by notify_orders
    next_point = await get_point_execution_by_visit_order(
        waybill_ref='waybill_smart_1', visit_order=7,
    )
    assert next_point['eta'] == '2020-07-20T11:09:00+00:00'
    assert mock_employee_timer.handler.times_called == 1


async def test_timers_calculated_for_chain(
        happy_path_chain_order,
        happy_path_claims_segment_db,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        mock_employee_timer,
        mock_order_cancel,
        mock_driver_trackstory,
        mock_order_set_eta,
        run_claims_segment_replication,
        run_notify_orders,
        second_waybill_ref='waybill_smart_1',
):
    """
        Chain order for 'waybill_fb_3' (seg3) -> 'waybill_smart_1' (seg1, seg2)

        Check timers calculated for A1 point of 'waybill_smart_1'
        on cancellation of the 'waybill_fb_3's last segment (seg3).
    """
    mock_employee_timer.expected_request = None

    happy_path_claims_segment_db.cancel_segment_by_user('seg3')

    await run_claims_segment_replication()
    await run_notify_orders()
    await run_notify_orders()

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


async def test_timers_calculated_for_chain_complete(
        happy_path_chain_order,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_notify_orders,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        mock_order_change_destination,
        mock_employee_timer,
        mock_driver_trackstory,
        mock_order_set_eta,
        stq,
        segment_id='seg3',
        second_waybill_ref='waybill_smart_1',
):
    """
        Check chain order timers are updated on cancelled_with_items_on_hands.
    """
    mock_employee_timer.expected_request = None

    happy_path_claims_segment_db.set_segment_point_visit_status(
        segment_id, 'p1', 'visited', is_caused_by_user=True,
    )
    await run_claims_segment_replication()
    await run_notify_orders()

    happy_path_claims_segment_db.cancel_segment_by_user(segment_id)
    await run_claims_segment_replication()
    await run_notify_orders()
    await run_notify_orders()

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
