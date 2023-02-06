import time

import pytest


import tests_candidates.helpers


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


async def wait_workers(taxi_candidates, testpoint):
    @testpoint('statistic_worker_start')
    def worker_start(stats):
        return

    @testpoint('statistic_worker_finish')
    def worker_finished(stats):
        return stats

    await taxi_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    await worker_start.wait_call()
    await worker_finished.wait_call()


async def wait_workers_for_redis_store(redis_store):
    # wait for data store in redis
    cnt = 0
    while cnt != 10 and not redis_store.get(
            'candidates:driver_classes_statistic:data',
    ):
        time.sleep(0.1)
        cnt += 1


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_limit(
        taxi_candidates, driver_positions, chain_busy_drivers, load_json,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55.01, 35.01]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55.01, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 10,
                'left_distance': 100,
                'destination': [55, 35],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [55, 35],
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json('answer.json'),
    )
    assert actual == expected


@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_use_graph(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 0,  # if kdtree is used, it should find nothing
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1
    assert 'path' in candidates[0]['route_info']
    assert 'driver_edge_direction' in candidates[0]['route_info']


@pytest.mark.parametrize('max_route_distance,count', [(60000, 1), (1, 0)])
@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_graph_with_distance_limit(
        taxi_candidates, driver_positions, max_route_distance, count,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_route_distance': max_route_distance,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == count


@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_ignore_free_preferred(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625639, 55.754844]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625618, 55.752399]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 0,
                'left_distance': 0,
                'destination': [37.625296, 55.759285],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )
    body = {
        'limit': 2,
        'free_preferred': 2,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 10000,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    uuids = {x['uuid'] for x in candidates}
    assert uuids == {'uuid1', 'uuid2'}


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
    CANDIDATES_ORDER_SEARCH_USE_CLASSES_STATS={
        'require_empty_classes': False,
        'enable_hybrid_search': True,
        'min_hybrid_distance': 3500,
    },
    CANDIDATES_RARE_CLASSES_LIMITS={
        '__default__': {'absolute': 10, 'percent': 0},
    },
    CANDIDATES_FEATURE_SWITCHES={'enable_storage_filters': True},
)
async def test_kdtree_fallback_by_classes(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        testpoint,
        load_json,
        redis_store,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625639, 55.754844]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625618, 55.752399]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 0,
                'left_distance': 0,
                'destination': [37.625296, 55.759285],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    # initialize taxi_candidates by request
    response = await taxi_candidates.get('ping')
    assert response.status_code == 200

    # the stats for moscow zone should be:
    # "classes":{"uberx":1,"minivan":1,"uberblack":2,"econom":1}

    await wait_workers(taxi_candidates, testpoint)
    await wait_workers_for_redis_store(redis_store)
    await taxi_candidates.invalidate_caches(
        cache_names=['driver-classes-statistic-cache'],
    )

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 500,
        'max_route_distance': 4000,
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 5,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected=load_json('kdtree_fallback_answer.json'),
    )
    assert actual == expected


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': '1',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['moscow'],
                    'arg_name': 'tariff_zone',
                    'set_elem_type': 'string',
                },
            },
            'value': {'enabled': True, 'max_visited_edges_count': 200000},
        },
    ],
    name='candidates_graph_fallback',
    consumers=['candidates/user'],
    default_value={'enabled': False, 'max_visited_edges_count': 0},
)
async def test_kdtree_fallback(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [38.341818, 55.913833]}],
    )

    body = {
        'zone_id': 'moscow',
        'point': [37.841940, 55.786647],
        'max_route_time': 10000,
        'max_route_distance': 100000,
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 1,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert len(json['candidates']) == 1

    body['point'] = [38.341818, 55.913833]
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert len(json['candidates']) == 1


@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_diagnostic(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 0,  # if kdtree is used, it should find nothing
        'diagnostic': ['route_path', 'visualization'],
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1
    assert 'path' in candidates[0]['route_info']
    assert 'driver_edge_direction' in candidates[0]['route_info']
    assert 'diagnostic' in json
    assert 'visualization' in json['diagnostic']
    assert 'graph' in json['diagnostic']['visualization']


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    DISPATCH_AIRPORT_ZONES={
        'moscow_airport_id': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow',
            'notification_area': 'moscow',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow',
            'whitelist_classes': {},
        },
    },
)
@pytest.mark.parametrize(
    'allowed_classes,pickup_line_id,results_size',
    [
        # one candidate from usual airport queue
        # second from fallback regular search
        (None, None, 2),
        # one candidate from usual airport queue
        (['econom'], None, 1),
        # one candidate from usual airport queue
        (['uberx'], None, 1),
        # one candidate from check-in airport queue
        (['econom'], 'moscow_airport_id', 1),
        # one candidate from airport queue,
        # check-in order for not found airport
        # fallback regular search, but dbid0_uuid0 disallowed
        (['econom'], 'svo_d_line1', 0),
    ],
)
async def test_airport_queue(
        taxi_candidates,
        taxi_config,
        driver_positions,
        mockserver,
        allowed_classes,
        pickup_line_id,
        results_size,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625639, 55.754844]},
        ],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
        'diagnostic': ['route_path', 'visualization'],
    }
    if allowed_classes is not None:
        body['allowed_classes'] = allowed_classes
    if pickup_line_id:
        body['dispatch_check_in'] = {'pickup_line': pickup_line_id}
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == results_size

    if results_size > 0:
        aq_candidate = candidates[0]
        assert aq_candidate['id'] == 'dbid0_uuid0'

        if pickup_line_id is None or pickup_line_id == 'moscow_airport_id':
            # from airport queue
            assert 'airport_queue' in aq_candidate['metadata']
        else:
            # from fallback regular search
            assert 'airport_queue' not in aq_candidate.get('metadata', {})

        if allowed_classes is None:
            # second from fallback regular search
            fb_candidate = candidates[1]
            assert fb_candidate['id'] == 'dbid0_uuid1'
            assert 'airport_queue' not in fb_candidate.get('metadata', {})


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_dispatch_settings_override(taxi_candidates, driver_positions):
    # distance between dbid0_uuid0 and search point is about 1km
    # distance between dbid0_uuid1 and search point > 10km
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.612504, 55.738354]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.867315, 55.777181]},
        ],
    )

    # nothing found, short distance
    body = {
        'limit': 3,
        'max_distance': 700,
        'zone_id': 'moscow',
        'point': [37.628576, 55.740776],
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert not candidates

    # both found, long distance
    body['max_distance'] = 20000
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 2

    # one found, overriden default distance (10km)
    del body['max_distance']
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1


@pytest.mark.parametrize('use_graph', [False, True])
@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
)
async def test_graph_regional_settings(
        taxi_candidates, driver_positions, experiments3, use_graph,
):
    experiments3.add_config(
        name='graph_regional_settings',
        consumers=['candidates/user'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': 'moscow',
                                    'arg_name': 'tariff_zone',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'search': {'use_search_on_graph': use_graph},
                    'tracking': {'use_raw_positions_when_tracking': False},
                },
            },
        ],
        default_value={
            'search': {'use_search_on_graph': False},
            'tracking': {'use_raw_positions_when_tracking': False},
        },
    )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1
    assert 'path' in candidates[0]['route_info']
    assert (
        'driver_edge_direction' in candidates[0]['route_info']
    ) == use_graph


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
    # redefine processor queue settings to avoid candidates reordering
    CANDIDATES_PROCESSOR_QUEUE_SIZE={
        'min_size': 1,
        'max_size': 1,
        'coefficient': 1.0,
    },
)
async def test_perfect_chain(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings_mocks,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625618, 55.752399]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.624826, 55.755331]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.624826, 55.755331]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 500,
                'left_distance': 2000,
                'destination': [37.625618, 55.752399],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    dispatch_settings_mocks.set_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'NO_REPOSITION_PREFERRED': 0,
                            'CHAIN_PREFERRED': 1,
                            'PEDESTRIAN_DISABLED': True,
                            'ORDER_CHAIN_MAX_LINE_DISTANCE': 2000,
                            'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 3000,
                            'ORDER_CHAIN_MAX_ROUTE_TIME': 1000,
                            'ORDER_CHAIN_PAX_EXCHANGE_TIME': 120,
                        },
                    },
                ],
            },
        ],
    )

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_distance': 10000,
        'limit': 2,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'candidates': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        },
    )
    assert actual == expected


@pytest.mark.parametrize('stop_searching_through_bad_roads', [False, True])
@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_use_graph_with_search_restrictions(
        taxi_candidates,
        driver_positions,
        experiments3,
        stop_searching_through_bad_roads,
):
    experiments3.add_experiment(
        name='stop_searching_through_non_paved_or_poor_cond_roads',
        consumers=['candidates/user'],
        match={
            'predicate': {'type': 'true'},
            'enabled': stop_searching_through_bad_roads,
        },
        clauses=[],
        default_value={'enabled': True},
    )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1
    assert 'path' in candidates[0]['route_info']
    assert 'driver_edge_direction' in candidates[0]['route_info']


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_no_chains(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid2', 'position': [37.624826, 55.755331]}],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 10,
                'left_distance': 200,
                'destination': [37.625618, 55.752399],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_distance': 10000,
        'limit': 2,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 1

    body['__deprecated__'] = {'no_chains': True}
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    assert not response.json()['candidates']
