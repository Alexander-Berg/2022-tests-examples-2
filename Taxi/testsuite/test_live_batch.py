import time
import asyncio

DUMMY_GEOAREA_POLYGON = [
    [76.74773, 43.15562],
    [76.77794, 43.35862],
    [77.04439, 43.37310],
    [77.03340, 43.15062],
    [76.74773, 43.15562]
]


async def test_live_batch(
        create_segment,
        dummy_candidates,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
        mock_waybill_propose,
        create_waybill,
        mockserver,
        execute_pg_query,
        propositions_manager,
        rt_robot_execute,
        testpoint
):
    dummy_candidates(position=[76.881441, 43.222585])

    first_segment_id = create_segment(template='test_live_batch/segment_seg1.json')
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[len('logistic-dispatch/'):]

    create_waybill(waybill_ref=external_ref, segment_id=first_segment_id, template='test_live_batch/waybill_info_response.json')
    await rt_robot_execute('propositions_journal')

    # make sure that a courier has been assigned to the order
    planned_actions_rows = execute_pg_query('select internal_contractor_id, (basic_plan is not null) as have_plan from planned_actions',)
    assert planned_actions_rows == [[proposition_id, True], [proposition_id, True]]

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        response = {
            'candidates': [],
        }
        return response

    time.sleep(1)
    await rt_robot_execute('state_watcher')
    default_cache_rows = execute_pg_query('select key from default_cache where key like \'%position%\'',)
    assert ['/position/61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'] in default_cache_rows

    time.sleep(1)
    await rt_robot_execute('estimation_watcher')
    default_cache_rows = execute_pg_query('select key from default_cache where key like \'%estimation%\'',)
    assert ['/estimation/61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'] in default_cache_rows

    time.sleep(1)
    second_segment_id = create_segment(template='test_live_batch/segment_seg2.json')
    await rt_robot_execute('segments_journal')

    expected_segments = {first_segment_id: False, second_segment_id: False}

    @testpoint('ld::p2p::report_assignment')
    def report_assignment_handler(data):
        assert data['cargo_ref_id'] in expected_segments
        assert data['driver_id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
        assert data['assignment_type'] == 'live_batch'
        expected_segments[data['cargo_ref_id']] = True

    await rt_robot_execute('p2p_allocation')
    assert report_assignment_handler.times_called == 2
    assert expected_segments == {first_segment_id: True, second_segment_id: True}


async def test_live_batch_on_slot(
        create_segment,
        dummy_geoareas,
        dummy_candidates,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
        mock_waybill_propose,
        create_waybill,
        mockserver,
        execute_pg_query,
        propositions_manager,
        rt_robot_execute,
        testpoint
):
    await dummy_geoareas(employer_names=['default'], order_sources=['B2B'], polygon=DUMMY_GEOAREA_POLYGON)
    await asyncio.sleep(5)  # Waiting for the completion of the cache update

    dummy_candidates(position=[76.881441, 43.222585])

    first_segment_id = create_segment(template='test_live_batch/segment_seg1.json', employer='default')
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[len('logistic-dispatch/'):]

    create_waybill(waybill_ref=external_ref, segment_id=first_segment_id, template='test_live_batch/waybill_info_response.json')
    await rt_robot_execute('propositions_journal')

    # make sure that a courier has been assigned to the order
    planned_actions_rows = execute_pg_query('select internal_contractor_id, (basic_plan is not null) as have_plan from planned_actions',)
    assert planned_actions_rows == [[proposition_id, True], [proposition_id, True]]

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        response = {
            'candidates': [],
        }
        return response

    time.sleep(1)
    await rt_robot_execute('state_watcher')
    default_cache_rows = execute_pg_query('select key from default_cache where key like \'%position%\'',)
    assert ['/position/61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'] in default_cache_rows

    time.sleep(1)
    await rt_robot_execute('estimation_watcher')
    default_cache_rows = execute_pg_query('select key from default_cache where key like \'%estimation%\'',)
    assert ['/estimation/61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'] in default_cache_rows

    # The value will be ignored and taken from the database
    # We expect that the next order will be assigned according to the old conditions 'default' and 'B2B'
    await dummy_geoareas(employer_names=['grocery'], order_sources=['C2C'], polygon=DUMMY_GEOAREA_POLYGON)
    time.sleep(5)  # Waiting for the completion of the cache update

    second_segment_id = create_segment(template='test_live_batch/segment_seg2.json', employer='default')
    await rt_robot_execute('segments_journal')

    expected_segments = {first_segment_id: False, second_segment_id: False}

    @testpoint('ld::p2p::report_assignment')
    def report_assignment_handler(data):
        assert data['cargo_ref_id'] in expected_segments
        assert data['driver_id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
        assert data['assignment_type'] == 'live_batch'
        expected_segments[data['cargo_ref_id']] = True

    await rt_robot_execute('p2p_allocation')
    assert report_assignment_handler.times_called == 2
    assert expected_segments == {first_segment_id: True, second_segment_id: True}


async def test_chain(
        dummy_candidates,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
        mock_waybill_propose,
        create_waybill,
        mockserver,
        execute_pg_query,
        propositions_manager,
        rt_robot_execute,
        testpoint,
        read_waybill,
        update_waybill,
        create_segment
):
    dummy_candidates()
    first_segment_id = create_segment(template='test_chain/segment.json')

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[len('logistic-dispatch/'):]

    waybill_ref = create_waybill(
        waybill_ref=external_ref,
        segment_id=first_segment_id,
        resolution='',
        status='processing',
        template='test_chain/waybill.json'
    )

    await rt_robot_execute('propositions_journal')

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        response = {
            'candidates': [],
        }
        return response

    # make waybill in status processing and with one resolved point
    current_waybill = read_waybill(waybill_ref=waybill_ref)
    current_waybill['dispatch']['resolution'] = ''
    current_waybill['dispatch']['status'] = 'processing'
    current_waybill['execution']['points'][0]['is_resolved'] = True
    current_waybill['execution']['points'][0]['resolution']['is_visited'] = True
    update_waybill(waybill=current_waybill)

    await rt_robot_execute('propositions_journal')

    # make sure that the courier has passed the first point
    planned_actions_rows = execute_pg_query(
        'select internal_contractor_id, requested_action from planned_actions',
    )
    assert planned_actions_rows == [[proposition_id, 'put_resource']]

    time.sleep(1)
    await rt_robot_execute('state_watcher')
    default_cache_rows = execute_pg_query('select key from default_cache where key like \'%position%\'',)
    assert ['/position/61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'] in default_cache_rows

    time.sleep(1)
    await rt_robot_execute('estimation_watcher')
    default_cache_rows = execute_pg_query('select key from default_cache where key like \'%estimation%\'',)
    assert ['/estimation/61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'] in default_cache_rows

    time.sleep(1)
    second_segment_id = create_segment(template='test_chain/segment.json')
    await rt_robot_execute('segments_journal')

    expected_segments = {first_segment_id: False, second_segment_id: False}

    @testpoint('ld::p2p::report_assignment')
    def report_assignment_handler(data):
        assert data['cargo_ref_id'] in expected_segments
        assert data['driver_id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
        assert data['assignment_type'] == 'chain'
        expected_segments[data['cargo_ref_id']] = True

    await rt_robot_execute('p2p_allocation')
    assert report_assignment_handler.times_called == 2
    assert expected_segments == {first_segment_id: True, second_segment_id: True}
