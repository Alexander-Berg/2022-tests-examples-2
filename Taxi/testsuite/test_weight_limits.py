import pytest
import time
import datetime


DUMMY_DRIVER_FOR_ORDER_REQUEST = {
    'aliases': [],
    'allowed_classes': ['courier', 'lavka'],
    'excluded_car_numbers': [],
    'excluded_ids': [],
    'excluded_license_ids': [],
    'lookup': {'generation': 1, 'version': 1, 'wave': 1},
    'order_id': 'taxi-order',
}

CUSTOM_CONTEXT_PD = {
    'depot_id': '149885',
    'brand_name': 'Лавка',
    'dispatch_type': 'pull-dispatch',
    'delivery_flags': None,
    'weight_restrictions': None,
    'external_feature_prices': {
        'external_order_created_ts': 1643450174
    },
    'lavka_has_market_parcel': False
}

shift_closes_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
COURIER_SHIFT_PD = {
    'shift_id': '5675142',
    'started_at': '2022-03-02T17:18:16+0000',
    'closes_at': shift_closes_at.strftime("%Y-%m-%dT%H:%M:%S"),
    'zone_id': '6476',
    'status': 'in_progress',
    'updated_ts': '2022-03-02T17:18:15+0000',
    'is_high_priority': False,
    'zone_group_id': '678',
    'meta_group_id': 'lavka'
}


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'p2p_tactic.skip_cross_cases_after_rejected_nested': 'false',
    },
)
@pytest.mark.parametrize('weight_gr', [20000, 30000])
async def test_pd_batch_max_weight(
        create_segment,
        weight_gr,
        rt_robot_execute,
        dummy_pedestrian_router,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        testpoint,
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        if weight_gr == 20000 and len(data['segments']) > 1:
            assert data['reject_reasons'] == ['too-heavy', 'too-heavy']
        else:
            assert data['reject_reasons'] is None

    dummy_candidates(shift=COURIER_SHIFT_PD, transport='bicycle')
    CUSTOM_CONTEXT_PD['weight_restrictions'] = [
        {'weight_gr': weight_gr, 'moving_behavior': 'bicycle'}
    ]

    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
                   custom_context=CUSTOM_CONTEXT_PD,
                   employer='grocery',
                   )
    await rt_robot_execute('segments_journal')
    time.sleep(5)

    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.47, 55.73372],
                   employer='grocery',
                   )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 1
    proposition_segment_count = len(propositions_manager.propositions[0]['segments'])
    assert proposition_segment_count == (1 if weight_gr == 20000 else 2)
    assert reject_reasons.times_called == 3


@pytest.mark.parametrize('weight_limit', [None, 2, 4])
async def test_pd_weight_limit(
        create_segment,
        weight_limit,
        rt_robot_execute,
        dummy_pedestrian_router,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        testpoint,
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        if weight_limit == 2:
            assert data['reject_reasons'] == ['too-heavy']
        else:
            assert data['reject_reasons'] is None

    dummy_candidates(shift=COURIER_SHIFT_PD, max_weight=weight_limit, transport='bicycle')
    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
                   custom_context=CUSTOM_CONTEXT_PD,
                   employer='grocery',
                   item_weight=1
                   )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 0 if weight_limit == 2 else 1
    assert reject_reasons.times_called == 1


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'p2p_tactic.skip_cross_cases_after_rejected_nested': 'false',
    },
)
@pytest.mark.parametrize('weight_limit', [None, 2, 4])
async def test_pd_batch_weight_limit(
        create_segment,
        weight_limit,
        rt_robot_execute,
        dummy_pedestrian_router,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        testpoint,
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        if weight_limit == 2 and len(data['segments']) > 1:
            assert data['reject_reasons'] == ['too-heavy', 'too-heavy']
        else:
            assert data['reject_reasons'] is None

    dummy_candidates(shift=COURIER_SHIFT_PD, max_weight=weight_limit, transport='bicycle')
    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
                   custom_context=CUSTOM_CONTEXT_PD,
                   employer='grocery',
                   item_weight=0.5
                   )
    await rt_robot_execute('segments_journal')
    time.sleep(5)

    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.47, 55.73372],
                   custom_context=CUSTOM_CONTEXT_PD,
                   employer='grocery',
                   item_weight=0.5
                   )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 1
    proposition_segment_count = len(propositions_manager.propositions[0]['segments'])
    assert proposition_segment_count == (1 if weight_limit == 2 else 2)
    assert reject_reasons.times_called == 3


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
        testpoint,
):
    dummy_candidates(position=[76.881441, 43.222585])

    custom_context = {"weight_restrictions": [{'weight_gr': 35000, 'moving_behavior': 'auto'}]}
    first_segment_id = create_segment(template='test_live_batch/segment_seg1.json', item_weight=15)
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
    second_segment_id = create_segment(template='test_live_batch/segment_seg2.json', custom_context=custom_context, item_weight=15)
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
