import pytest
import time
import json
import datetime
import asyncio

DUMMY_GEOAREA_POLYGON = [
    [37.44386, 55.69611],
    [37.45464, 55.85890],
    [37.80081, 55.87277],
    [37.77746, 55.67746],
    [37.44386, 55.69611]
]

DUMMY_DRIVER_FOR_ORDER_REQUEST = {
    'aliases': [],
    'allowed_classes': ['courier', 'lavka'],
    'excluded_car_numbers': [],
    'excluded_ids': [],
    'excluded_license_ids': [],
    'lookup': {'generation': 1, 'version': 1, 'wave': 1},
    'order_id': 'taxi-order',
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


async def test_basic(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config
):
    route_propositions_rows = execute_pg_query('select * from route_propositions')
    assert not route_propositions_rows

    dummy_candidates()
    segment_id = create_segment()
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')

    route_propositions_rows = execute_pg_query('select * from route_propositions')
    assert len(route_propositions_rows) == 1

    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[external_ref.startswith('logistic-dispatch/') and len('logistic-dispatch/'):]
    events_storage_rows = execute_pg_query('select event, flow, key from events_storage order by timestamp')
    assert len(events_storage_rows) == 2
    assert events_storage_rows[1] == ['add', 'proposition', proposition_id]

    assert len(propositions_manager.propositions) == 1
    assert propositions_manager.propositions[0]['segments'] == [
        {'segment_id': segment_id, 'waybill_building_version': 1},
    ]

    planned_actions_rows = execute_pg_query('select basic_plan from planned_actions')
    assert planned_actions_rows == [[''], ['']]

    @mockserver.json_handler('/internal/order/info')
    def order_info(request):
        assert request.json == {'order_id': 'taxi-order'}
        return {
            'waybill_ref': external_ref,
        }

    response = await logistic_dispatcher_client.post(
        '/driver-for-order', json=DUMMY_DRIVER_FOR_ORDER_REQUEST,
    )
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
    assert order_info.times_called == 1


async def test_pd_basic(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
):
    dummy_candidates(shift=COURIER_SHIFT_PD)
    segment = create_segment(
        template='cargo-dispatch/segment-pd.json',
        dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
        employer='grocery',
    )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 1
    assert propositions_manager.propositions[0]['segments'] == [
        {'segment_id': segment, 'waybill_building_version': 1},
    ]

    @mockserver.json_handler('/internal/order/info')
    def order_info(request):
        assert request.json == {'order_id': 'taxi-order'}
        return {
            'waybill_ref': propositions_manager.propositions[0][
                'external_ref'
            ],
        }

    response = await logistic_dispatcher_client.post(
        '/driver-for-order', json=DUMMY_DRIVER_FOR_ORDER_REQUEST,
    )
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
    assert order_info.times_called == 1


async def test_pd_batch_basic(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
):
    dummy_candidates(shift=COURIER_SHIFT_PD, transport='bicycle')
    segment1 = create_segment(template='cargo-dispatch/segment-pd.json',
                              dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
                              employer='grocery',
                              )
    await rt_robot_execute('segments_journal')
    time.sleep(5)
    segment2 = create_segment(template='cargo-dispatch/segment-pd.json',
                              dropoff_point_coordinates=[37.47686025394652, 55.73575309948215],
                              employer='grocery',
                              )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 1

    segment_ids = [segment1, segment2]
    segments = propositions_manager.propositions[0]['segments']
    assert len(segments) == 2
    assert segments[0]['segment_id'] in segment_ids
    assert segments[1]['segment_id'] in segment_ids
    assert segments[0]['segment_id'] != segments[1]['segment_id']

    @mockserver.json_handler('/internal/order/info')
    def order_info(request):
        assert request.json == {'order_id': 'taxi-order'}
        return {
            'waybill_ref': propositions_manager.propositions[0][
                'external_ref'
            ],
        }

    response = await logistic_dispatcher_client.post(
        '/driver-for-order', json=DUMMY_DRIVER_FOR_ORDER_REQUEST,
    )
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
    assert order_info.times_called == 1


@pytest.mark.parametrize('min_to_shift_ends', [20, 23, 25])
async def test_pd_batch_shift_soon_ends(
        create_segment,
        min_to_shift_ends,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        testpoint,
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        if min_to_shift_ends == 20 and len(data['segments']) > 1:
            assert data['reject_reasons'] == ['shift-soon-ends', 'shift-soon-ends']
        elif min_to_shift_ends == 23 and len(data['segments']) > 1:
            assert data['reject_reasons'] == ['shift-soon-ends']
        else:
            assert data['reject_reasons'] is None

    shift_closes_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=min_to_shift_ends,
    )
    COURIER_SHIFT_PD['closes_at'] = shift_closes_at.strftime("%Y-%m-%dT%H:%M:%S")
    dummy_candidates(shift=COURIER_SHIFT_PD, transport='bicycle', position=[37.493, 55.736])
    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.4928, 55.7359],
                   employer='grocery',
                   )
    await rt_robot_execute('segments_journal')
    time.sleep(5)
    create_segment(template='cargo-dispatch/segment-pd.json',
                   dropoff_point_coordinates=[37.487, 55.7],
                   employer='grocery',
                   )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 1
    proposition_segment_count = len(propositions_manager.propositions[0]['segments'])
    assert proposition_segment_count == (1 if min_to_shift_ends == 20 else 2)
    assert reject_reasons.times_called == 3


@pytest.mark.parametrize('with_chain_info', [True, False])
async def test_skip_chain_candidates(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
        with_chain_info,
        cargo_eta_flow_config
):
    """
        Check candidate on chain is not returned
        (without chain returned).
    """
    dummy_candidates(
        chain_info={
            'destination': [37.7, 55.7],
            'left_time': 1,
            'left_dist': 2,
            'order_id': '123',
        }
        if with_chain_info
        else None,
    )
    segment = create_segment()
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    if not with_chain_info:
        assert len(propositions_manager.propositions) == 1
        assert propositions_manager.propositions[0]['segments'] == [
            {'segment_id': segment, 'waybill_building_version': 1},
        ]
    else:
        assert not propositions_manager.propositions

    @mockserver.json_handler('/internal/order/info')
    def order_info(request):
        assert request.json == {'order_id': 'taxi-order'}
        if propositions_manager.propositions:
            return {
                'waybill_ref': propositions_manager.propositions[0][
                    'external_ref'
                ],
            }
        else:
            return mockserver.make_response(
                status=404, json={'code': 'not_found', 'message': 'no order'},
            )

    response = await logistic_dispatcher_client.post(
        '/driver-for-order', json=DUMMY_DRIVER_FOR_ORDER_REQUEST,
    )
    assert response.status_code == 200
    if with_chain_info:
        assert response.json() == {}
    else:
        assert 'candidates' in response.json()
        candidates = response.json()['candidates']
        assert len(candidates) == 1


@pytest.mark.parametrize('assign_rover', [False, True])
async def test_allow_rover(
        assign_rover,
        create_segment,
        mockserver,
        dummy_candidates,
        rt_robot_execute,
):
    context = {'delivery_flags': {'assign_rover': assign_rover}}

    create_segment(custom_context=context)
    await rt_robot_execute('segments_journal')

    @mockserver.json_handler('/candidates/order-search')
    def test_request(request):
        if assign_rover:
            assert request.json['logistic'] == {'include_rovers': True}
        else:
            assert 'logistic' not in request.json

        return dummy_candidates()

    await rt_robot_execute('p2p_allocation')


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'employer.grocery.pedestrian_route_mileage_limit': '1',
    },
)
async def test_pd_pedestrian_max_distance_grocery(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        dummy_masstransit_router,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
        testpoint,
        execute_pg_query,
        cargo_eta_flow_config,
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        assert data['reject_reasons'] == ['too-distant-by-router']

    dummy_candidates(shift=COURIER_SHIFT_PD, transport='pedestrian')
    create_segment(
        template='cargo-dispatch/segment-pd.json',
        dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
        employer='grocery',
    )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')

    assert reject_reasons.times_called == 1


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'employer.default.pedestrian_route_mileage_limit': '1',
    },
)
async def test_pd_pedestrian_max_distance_def(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        dummy_pedestrian_router,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
        testpoint,
        execute_pg_query,
        cargo_eta_flow_config,
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        assert data['reject_reasons'] == ['too-distant-by-router']

    dummy_candidates(transport='bicycle')
    create_segment(
        template='cargo-dispatch/segment-pd.json',
        dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
        employer='default',
    )
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation_pd')

    assert reject_reasons.times_called == 1


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'employer.eats.pedestrian_route_mileage_limit': '1',
    },
)
async def test_pedestrian_max_distance_eats(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        dummy_masstransit_router,
        mock_waybill_propose,
        testpoint,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        assert data['reject_reasons'] == ['too-distant-by-router']

    dummy_candidates(transport='pedestrian', position=[37.632745, 55.774532])
    create_segment(employer='eats',)

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')

    assert reject_reasons.times_called == 1


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'employer.eats.pedestrian_route_mileage_limit': '1',
        'employer.eats.pedestrian_route_classes_to_check': 'courier',
    },
)
async def test_pedestrian_max_distance_eats_with_classes_ok(
        create_segment,
        rt_robot_execute,
        create_candidate,
        dummy_masstransit_router,
        mock_waybill_propose,
        testpoint,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        assert data['reject_reasons'] == ['too-distant-by-router']

    create_candidate(
        dbid_uuid='courier_1',
        tariff_classes=['courier'],
        transport_type='pedestrian',
        position=[37.632745, 55.774532])
    create_segment(employer='eats',)

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')

    assert reject_reasons.times_called == 1


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'employer.eats.pedestrian_route_mileage_limit': '1',
        'employer.eats.pedestrian_route_classes_to_check': 'courier',
    },
)
async def test_pedestrian_max_distance_eats_with_classes_skip(
        create_segment,
        rt_robot_execute,
        create_candidate,
        dummy_masstransit_router,
        mock_waybill_propose,
        testpoint,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config
):
    @testpoint('ld::calc_l1_features::reject_reasons')
    def reject_reasons(data):
        assert data['reject_reasons'] == ['too-distant-by-router']

    create_candidate(
        dbid_uuid='courier_1',
        tariff_classes=['eda'],
        transport_type='pedestrian',
        position=[37.632745, 55.774532])
    create_segment(employer='eats',)

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')

    assert reject_reasons.times_called == 0


async def test_allowed_employers_on_slot(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        dummy_masstransit_router,
        mock_waybill_propose,
        testpoint,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config,
        propositions_manager,
        dummy_geoareas
):
    await dummy_geoareas(employer_names=['vkusvill', 'eats', 'grocery'], order_sources=['B2B'], polygon=DUMMY_GEOAREA_POLYGON)
    await asyncio.sleep(10)  # Waiting for the completion of the cache update

    dummy_candidates()
    segment_id = create_segment(employer='eats')

    @testpoint('ld::p2p::report_assignment')
    def report_assignment_handler(data):
        assert data['cargo_ref_id'] == segment_id
        assert data['driver_id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
        assert data['assignment_type'] == 'p2p'

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert propositions_manager.propositions
    assert report_assignment_handler.times_called == 1


async def test_not_allowed_employers_on_slot(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        dummy_masstransit_router,
        mock_waybill_propose,
        testpoint,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config,
        propositions_manager,
        dummy_geoareas
):
    await dummy_geoareas(employer_names=['vkusvill'], order_sources=['B2B'], polygon=DUMMY_GEOAREA_POLYGON)
    await asyncio.sleep(10)  # Waiting for the completion of the cache update

    dummy_candidates()
    segment_id = create_segment(employer='eats')

    @testpoint('ld::p2p::planner_segment_edges')
    def planner_segment_edges(data):
        response = json.loads(data['report'])
        assert response['edges'] == [{
            'driver_id': '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8',
            'cargo_ref_id': segment_id,
            'kind': 'l1-check-employers-failed',
            'position': [37.51, 55.76]
        }]

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert not propositions_manager.propositions
    assert planner_segment_edges.times_called == 2


async def test_c2c_driver_not_supported(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        dummy_masstransit_router,
        mock_waybill_propose,
        testpoint,
        mockserver,
        execute_pg_query,
        cargo_eta_flow_config,
        propositions_manager,
        dummy_geoareas
):
    await dummy_geoareas(order_sources=['C2C'], polygon=DUMMY_GEOAREA_POLYGON)
    await asyncio.sleep(10)  # Waiting for the completion of the cache update

    dummy_candidates()
    segment_id = create_segment(employer='eats')

    @testpoint('ld::p2p::planner_segment_edges')
    def planner_segment_edges(data):
        response = json.loads(data['report'])
        assert response['edges'] == [{
            'driver_id': '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8',
            'cargo_ref_id': segment_id,
            'kind': 'different-corp-client-ids',
            'position': [37.51, 55.76]
        }]

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert not propositions_manager.propositions
    assert planner_segment_edges.times_called == 2
