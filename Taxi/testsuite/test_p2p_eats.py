import time


DUMMY_DRIVER_FOR_ORDER_REQUEST = {
    'aliases': [],
    'allowed_classes': ['courier'],
    'excluded_car_numbers': [],
    'excluded_ids': [],
    'excluded_license_ids': [],
    'lookup': {'generation': 1, 'version': 1, 'wave': 1},
    'order_id': 'taxi-order',
}


async def test_route_info_via_eats_eta(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
):
    @mockserver.json_handler('/v1/configs')
    def experiments(request):
        content = request.json
        if 'logistic-dispatcher/simple_p2p_tactic_apply' != content['consumer']:
            return {}

        kwargs = {x['name']: x for x in content['args']}
        assert 'performer_tariff_class_set' in kwargs
        assert 'order_tariff_class' in kwargs
        return {
            'items': [
                {
                    'name': 'eta_flow',
                    'value': {
                        'ld': {
                            'calc_eta_from': ['logistic-dispatcher', 'eats-eta'],
                            'return_eta_from': 'eats-eta'
                        }
                    }
                },
            ],
            'version': 0,
        }

    @mockserver.json_handler('/v2/eta')
    def mock_eats_eta_v2_eta(request):
        assert len(request.json['sources']) == 1
        assert request.json['sources'][0]['position'] == [37.510000, 55.760000]
        assert request.json['destination']['position'] == [37.632745, 55.774532]
        print(str(request.json))
        return {'etas': [{'time': 3600, 'distance': 6000}]}

    dummy_candidates()
    segment = create_segment()
    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
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
    route_info = candidates[0]['route_info']
    assert route_info['time'] == 3600
    assert route_info['distance'] == 6000
    assert order_info.times_called == 1


def _eats_eta_v1_eta_routes_estimate_reply(request):
    route = request.json['routes'][0]
    actions = route['action_points']

    nodes = [
        {
            'type': 'start',
            'position': route['initial_courier_position'],
            'estimated_visit_time': route['initial_time'],
            'mileage': 0,
        }
    ]
    edges = []
    for action in actions:
        edges.append({'duration': 10, 'type': 'moving'})
        nodes.append({
            'type': 'arrival',
            'position': action['position'],
            'estimated_visit_time': nodes[-1]['estimated_visit_time'],
            'mileage': nodes[-1]['mileage'] + 2000,
        })
        edges.append({'duration': 10, 'type': 'parking'})
        nodes.append({
            'type': 'edges_separator',
            'position': action['position'],
            'estimated_visit_time': nodes[-1]['estimated_visit_time'],
            'mileage': nodes[-1]['mileage'],
        })
        edges.append({'duration': 10, 'type': action['type']})
        nodes.append({
            'type': 'departure',
            'position': action['position'],
            'estimated_visit_time': nodes[-1]['estimated_visit_time'],
            'mileage': nodes[-1]['mileage'],
        })

    for i in range(len(nodes)):
        if i > 0:
            nodes[i]['prev_edge_idx'] = i - 1
        if i + 1 < len(nodes):
            nodes[i]['next_edge_idx'] = i

    for i in range(len(edges)):
        edges[i]['from_node_idx'] = i
        edges[i]['to_node_idx'] = i + 1

    resp = {
        'routes_estimations': [{
            'route_id': route['id'],
            'is_precise': True,
            'edges': edges,
            'nodes': nodes
        }]
    }
    return resp


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
        logistic_dispatcher_client,
        create_segment
):
    initial_courier_position = [37.51, 55.76]

    @mockserver.json_handler('/v1/configs')
    def experiments(request):
        content = request.json
        if 'logistic-dispatcher/simple_p2p_tactic_apply' != content['consumer']:
            return {}

        kwargs = {x['name']: x for x in content['args']}
        assert 'performer_tariff_class_set' in kwargs
        assert 'order_tariff_class' in kwargs
        return {
            'items': [
                {
                    'name': 'eta_flow',
                    'value': {
                        'ld': {
                            'calc_eta_from': ['eats-eta-routes'],
                            'return_eta_from': 'eats-eta-routes'
                        }
                    }
                },
            ],
            'version': 0,
        }

    @mockserver.json_handler('/v1/eta/routes/estimate')
    def mock_eats_eta_v1_eta_routes_estimate(request):
        assert len(request.json['routes']) == 1
        route = request.json['routes'][0]

        assert route['initial_courier_position'] == initial_courier_position
        actions = route['action_points']
        assert len(actions) == 1
        assert actions[0]['position'] == [37.632745, 55.774532]

        return _eats_eta_v1_eta_routes_estimate_reply(request)

    dummy_candidates(position=initial_courier_position)
    first_segment_id = create_segment(template='test_p2p_eats/segment1.json')

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert mock_eats_eta_v1_eta_routes_estimate.times_called == 1

    @mockserver.json_handler('/internal/order/info')
    def order_info(request):
        assert request.json == {'order_id': 'taxi-order'}
        return {
            'waybill_ref': propositions_manager.propositions[-1][
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
    route_info = candidates[0]['route_info']
    assert route_info['time'] == 20

    external_ref = propositions_manager.propositions[0]['external_ref']
    proposition_id = external_ref[len('logistic-dispatch/'):]

    waybill_ref = create_waybill(
        waybill_ref=external_ref,
        segment_id=first_segment_id,
        resolution='',
        status='processing',
        template='test_p2p_eats/waybill.json'
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
    time.sleep(1)
    await rt_robot_execute('estimation_watcher')

    @mockserver.json_handler('/v1/eta/routes/estimate')
    def mock_eats_eta_v1_eta_routes_estimate(request):
        assert len(request.json['routes']) == 1
        route = request.json['routes'][0]

        # assert route['initial_courier_position'] == initial_courier_position
        print('initial_courier_position', route['initial_courier_position'])
        actions = route['action_points']
        assert len(actions) == 2
        assert actions[0]['position'] == [37.63223287, 55.76815715]
        assert actions[0]['type'] == 'dropoff'
        assert actions[1]['position'] == [37.632741, 55.774531]
        assert actions[1]['type'] == 'pickup'

        return _eats_eta_v1_eta_routes_estimate_reply(request)

    time.sleep(1)
    second_segment_id = create_segment(template='test_p2p_eats/segment2.json')
    expected_segments = {first_segment_id: False, second_segment_id: False}

    @testpoint('ld::p2p::report_assignment')
    def report_assignment_handler(data):
        assert data['cargo_ref_id'] in expected_segments
        assert data['driver_id'] == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
        assert data['assignment_type'] == 'chain'
        expected_segments[data['cargo_ref_id']] = True

    await rt_robot_execute('segments_journal')
    await rt_robot_execute('p2p_allocation')
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert report_assignment_handler.times_called == 2
    assert expected_segments == {first_segment_id: True, second_segment_id: True}
    assert mock_eats_eta_v1_eta_routes_estimate.times_called == 1

    response = await logistic_dispatcher_client.post(
        '/driver-for-order', json=DUMMY_DRIVER_FOR_ORDER_REQUEST,
    )
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    route_info = candidates[0]['route_info']
    assert route_info['time'] == 50
