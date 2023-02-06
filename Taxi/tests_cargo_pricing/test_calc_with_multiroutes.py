import copy


from tests_cargo_pricing import utils


async def test_calc_with_multiroutes_recalc_request(
        v1_calc_creator, mock_route, setup_two_routes_exp,
):
    mock_route.two_routes = True

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    mock_recalc = v1_calc_creator.mock_recalc
    assert mock_recalc.mock.times_called == 2
    assert len(mock_recalc.requests) == 2
    assert sorted(
        [
            len(mock_recalc.requests[0]['trip_info']['route']),
            len(mock_recalc.requests[1]['trip_info']['route']),
        ],
    ) == [92, 114]


async def test_recalc_with_multiroutes_recalc_request(
        v1_calc_creator, mock_route, setup_two_routes_exp,
):
    mock_route.two_routes = False

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    mock_recalc = v1_calc_creator.mock_recalc
    assert mock_recalc.mock.times_called == 1
    assert len(mock_recalc.request['trip_info']['route']) == 44

    mock_route.two_routes = True

    second_payload = v1_calc_creator.payload
    second_payload['previous_calc_id'] = response.json()['calc_id']

    # изменили состав точек
    waypoints = second_payload['waypoints']
    waypoints.insert(1, copy.deepcopy(waypoints[0]))
    waypoints[1]['position'][0] = waypoints[0]['position'][0] + 0.001
    waypoints[1]['id'] = 'clone_waypoint_1'

    second_response = await v1_calc_creator.execute()
    assert second_response.status_code == 200
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    assert mock_route.mock.times_called == 4
    assert len(mock_recalc.requests) == 3
    assert sorted(
        [
            len(mock_recalc.requests[1]['trip_info']['route']),
            len(mock_recalc.requests[2]['trip_info']['route']),
        ],
    ) == [114, 136]


async def test_calc_with_multiroutes_recalc_saving_one_route(
        v1_calc_creator, get_cached_edges, mock_route, setup_two_routes_exp,
):
    mock_route.two_routes = True

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    mock_recalc = v1_calc_creator.mock_recalc
    assert mock_recalc.mock.times_called == 2
    assert mock_route.mock.times_called == 2

    second_response = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=response.json()['calc_id'],
    )
    assert second_response.status_code == 200
    assert mock_route.mock.times_called == 2
    assert mock_recalc.mock.times_called == 3
    request_path_len = len(mock_recalc.request['trip_info']['route'])
    assert request_path_len in [92, 114]

    cached_edges = await get_cached_edges()
    assert len(cached_edges['path']) in [92, 114]


async def test_calc_with_multiroutes_router_request(
        v1_calc_creator, mock_route, setup_two_routes_exp,
):
    mock_route.two_routes = True

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert mock_route.mock.times_called == 2
    assert mock_route.request['results'] == '2'
