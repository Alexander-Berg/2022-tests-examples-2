async def test_empty(mock_waybill_dispatch_journal, rt_robot_execute):
    await rt_robot_execute('propositions_journal')


async def test_accept_proposition(
        create_segment,
        dummy_candidates,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
        mock_waybill_propose,
        create_waybill,
        execute_pg_query,
        propositions_manager,
        rt_robot_execute,
):
    dummy_candidates()
    segment_id = create_segment()

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    route_propositions_rows = execute_pg_query(
        'select * from route_propositions',
    )
    assert len(route_propositions_rows) == 1

    external_ref = propositions_manager.propositions[0]['external_ref']
    waybill_ref = create_waybill(
        waybill_ref=external_ref,
        segment_id=segment_id,
        resolution='',
        status='processing',
    )
    proposition_id = external_ref[
        external_ref.startswith('logistic-dispatch/')
        and len('logistic-dispatch/') :
    ]

    await rt_robot_execute('propositions_journal')
    assert mock_waybill_dispatch_journal.times_called
    assert mock_dispatch_waybill_info.times_called

    planned_actions_rows = execute_pg_query(
        'select internal_contractor_id, (basic_plan is not null) as have_plan from planned_actions',
    )
    assert planned_actions_rows == [
        [proposition_id, True],
        [proposition_id, True],
    ]

    route_propositions_rows = execute_pg_query(
        'select * from route_propositions',
    )
    assert not route_propositions_rows

    events_storage_rows = execute_pg_query(
        'select event, flow, key from events_storage order by timestamp',
    )
    assert len(events_storage_rows) == 3
    assert events_storage_rows[2] == ['accept', 'proposition', proposition_id]

    contractor_profiles_rows = execute_pg_query(
        'select current_proposition_id from contractor_profiles',
    )
    assert contractor_profiles_rows == [[proposition_id]]


async def test_resolved_complete(
        create_segment,
        dummy_candidates,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
        mock_waybill_propose,
        create_waybill,
        read_waybill,
        update_waybill,
        execute_pg_query,
        propositions_manager,
        rt_robot_execute,
):
    dummy_candidates()
    segment_id = create_segment()

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[
        external_ref.startswith('logistic-dispatch/')
        and len('logistic-dispatch/') :
    ]
    waybill_ref = create_waybill(
        waybill_ref=external_ref,
        segment_id=segment_id,
        resolution='',
        status='processing',
    )

    await rt_robot_execute('propositions_journal')
    planned_actions_rows = execute_pg_query(
        'select internal_contractor_id, requested_action from planned_actions order by requested_action',
    )
    assert planned_actions_rows == [
        [proposition_id, 'put_resource'],
        [proposition_id, 'take_resource'],
    ]

    # make waybill complete
    current_waybill = read_waybill(waybill_ref=waybill_ref)
    current_waybill['dispatch']['resolution'] = 'complete'
    current_waybill['dispatch']['status'] = 'resolved'
    update_waybill(waybill=current_waybill)

    await rt_robot_execute('propositions_journal')
    planned_actions_rows = execute_pg_query('select * from planned_actions')
    assert not planned_actions_rows


async def test_process_points(
        create_segment,
        dummy_candidates,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
        mock_waybill_propose,
        create_waybill,
        update_waybill,
        read_waybill,
        execute_pg_query,
        propositions_manager,
        rt_robot_execute,
):
    dummy_candidates()
    segment_id = create_segment()

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[
        external_ref.startswith('logistic-dispatch/')
        and len('logistic-dispatch/') :
    ]
    waybill_ref = create_waybill(
        waybill_ref=external_ref,
        segment_id=segment_id,
        resolution='',
        status='processing',
    )

    await rt_robot_execute('propositions_journal')

    # make waybill in status processing and with one resolved point
    current_waybill = read_waybill(waybill_ref=waybill_ref)
    current_waybill['dispatch']['resolution'] = ''
    current_waybill['dispatch']['status'] = 'processing'
    current_waybill['execution']['points'][0]['is_resolved'] = True
    current_waybill['execution']['points'][0]['resolution'][
        'is_visited'
    ] = True
    update_waybill(waybill=current_waybill)

    await rt_robot_execute('propositions_journal')

    planned_actions_rows = execute_pg_query(
        'select internal_contractor_id, requested_action from planned_actions',
    )
    assert planned_actions_rows == [[proposition_id, 'put_resource']]
