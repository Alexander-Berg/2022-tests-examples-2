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
    while cnt != 100 and not redis_store.get(
            'candidates:driver_classes_statistic:data',
    ):
        time.sleep(0.1)
        cnt += 1


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_class_limit(taxi_candidates, driver_positions):

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    body = {
        'class_limits': {'econom': {'limit': 3}},
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'car_number': '\u0425492\u041d\u041a77',
                    'classes': ['econom', 'minivan', 'uberx'],
                    'position': [55.0, 35.0],
                    'route_info': {
                        'distance': 0,
                        'time': 0,
                        'approximate': False,
                    },
                    'status': {
                        'driver': 'free',
                        'orders': [],
                        'status': 'online',
                        'taximeter': 'free',
                    },
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'license_id': 'AB0253_id',
                    'transport': {'type': 'car'},
                },
            ],
        },
    )
    assert actual == expected


@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_use_graph(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    body = {
        'class_limits': {'econom': {'limit': 3}},
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 0,  # if kdtree is used, it should find nothing
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1
    assert 'path' in candidates[0]['route_info']
    assert 'driver_edge_direction' in candidates[0]['route_info']


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
    CANDIDATES_ORDER_SEARCH_USE_CLASSES_STATS={
        'require_empty_classes': False,
        'enable_hybrid_search': True,
        'min_hybrid_distance': 2000,
    },
    CANDIDATES_RARE_CLASSES_LIMITS={
        '__default__': {'absolute': 1, 'percent': 0},
    },
)
async def test_hybrid_search(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        testpoint,
        load_json,
        redis_store,
):
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

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625639, 55.754844]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625618, 55.752399]},
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
        'max_route_distance': 2500,
        'allowed_classes': ['econom', 'uberblack'],
        'class_limits': {'econom': 5, 'uberblack': 5},
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json('hybrid_answer.json'),
    )
    assert actual == expected


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
        'class_limits': {'econom': 5, 'uberblack': 5},
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
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
        'class_limits': {'econom': 1, 'uberblack': 1},
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert len(json['candidates']) == 1

    body['point'] = [38.341818, 55.913833]
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert len(json['candidates']) == 1


@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES={
        'moscow': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow',
            'notification_area': 'moscow',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
        },
    },
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
)
async def test_airport_queue(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625639, 55.754844]},
        ],
    )
    body = {
        'class_limits': {'econom': 5, 'uberblack': 5},
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
    }

    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 2

    # first from airport queue
    aq_candidate = candidates[0]
    assert aq_candidate['id'] == 'dbid0_uuid0'
    assert 'airport_queue' in aq_candidate['metadata']

    # second from fallback regular search
    fb_candidate = candidates[1]
    assert fb_candidate['id'] == 'dbid0_uuid1'
    assert 'airport_queue' not in fb_candidate.get('metadata', {})


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_dispatch_settings_override_storage_limits(
        taxi_candidates, driver_positions, dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [{'values': {'QUERY_LIMIT_LIMIT_ETA': 2}}],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'vip',
                'parameters': [{'values': {'QUERY_LIMIT_LIMIT_ETA': 0}}],
            },
        ],
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.612504, 55.738354]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.867315, 55.777181]},
        ],
    )

    # nothing found, short distance
    body = {
        'max_distance': 20000,
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
        'point': [37.628576, 55.740776],
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_extended_radius_by_classes(
        taxi_candidates, driver_positions, dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'QUERY_LIMIT_LIMIT': 2,
                            'QUERY_LIMIT_MAX_LINE_DIST': 2000,
                            'MAX_ROBOT_TIME': 500,
                            'MAX_ROBOT_DISTANCE': 800,
                            'PAID_SUPPLY_MAX_ROUTE_DISTANCE': 2000,
                            'PAID_SUPPLY_MAX_ROUTE_TIME': 2000,
                        },
                    },
                ],
            },
        ],
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.612504, 55.738354]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.612504, 55.738354]},
        ],
    )

    # nothing found, short distance
    body = {
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
        'point': [37.628576, 55.740776],
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    assert not response.json()['candidates']

    body['order'] = {
        'fixed_price': {
            'paid_supply_price': 12,
            'paid_supply_info': {'time': 1000, 'distance': 2000},
        },
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 2

    body['search_settings'] = {'econom': {'extended_radius': True}}
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['uuid'] == 'uuid0'

    body['search_settings'] = {'vip': {'extended_radius': True}}
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['uuid'] == 'uuid1'

    body['search_settings'] = {
        'econom': {'extended_radius': True},
        'vip': {'extended_radius': True},
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(response.json()['candidates']) == 2


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_search_details(
        taxi_candidates, driver_positions, dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'QUERY_LIMIT_LIMIT': 1,
                            'QUERY_LIMIT_MAX_LINE_DIST': 2000,
                            'MAX_ROBOT_TIME': 500,
                            'MAX_ROBOT_DISTANCE': 800,
                            'PAID_SUPPLY_MAX_LINE_DISTANCE': 2001,
                            'PAID_SUPPLY_MAX_SEARCH_ROUTE_DISTANCE': 2001,
                            'PAID_SUPPLY_MAX_SEARCH_ROUTE_TIME': 2001,
                            'PEDESTRIAN_DISABLED': True,
                            'SUPPLY_ROUTE_DISTANCE_COEFF': 1.2,
                            'SUPPLY_ROUTE_TIME_COEFF': 1.4,
                            'PAID_SUPPLY_ROUTE_DISTANCE_COEFF': 1,
                            'PAID_SUPPLY_ROUTE_TIME_COEFF': 1,
                        },
                    },
                ],
            },
        ],
    )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.612504, 55.738354]}],
    )

    # nothing found, short distance
    body = {
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
        'point': [37.628576, 55.740776],
        'order': {'fixed_price': {'paid_supply_price': 12}},
    }

    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 1
    assert 'search_details' in response.json()
    assert response.json()['search_details'] == {
        'econom': {
            'preferred': {
                'line_distance': 800,
                'route_distance': 800,
                'route_time': 500,
            },
            'actual': {
                'line_distance': 2001,
                'route_distance': 2001,
                'route_time': 288,
            },
        },
    }


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_FEATURE_SWITCHES={'use_dynamic_storage': True},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
    CANDIDATES_ORDER_MULTISEARCH_DYNAMIC_LIMITS={
        '__default__': {
            'enabled': True,
            'min_count': 1,
            'extra_line_distance': 10,
            'extra_time': 5,
        },
        'vip': {
            'enabled': True,
            'min_count': 2,
            'extra_line_distance': 10,
            'extra_time': 5,
        },
    },
    # redefine processor queue settings to avoid candidates reordering
    CANDIDATES_PROCESSOR_QUEUE_SIZE={
        'min_size': 1,
        'max_size': 1,
        'coefficient': 1.0,
    },
)
async def test_search_limit_graph(
        taxi_candidates,
        driver_positions,
        dispatch_settings,
        chain_busy_drivers,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'QUERY_LIMIT_LIMIT': 10,
                            'QUERY_LIMIT_MAX_LINE_DIST': 40000,
                            'MAX_ROBOT_TIME': 40000,
                            'MAX_ROBOT_DISTANCE': 40000,
                            'PEDESTRIAN_DISABLED': True,
                        },
                    },
                ],
            },
        ],
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.628577, 55.740776]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.599099, 55.727753]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [37.628570, 55.740770]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [37.628577, 55.740777]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 0,
                'left_distance': 0,
                'destination': [37.603064, 55.720712],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    body = {
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
        'point': [37.628576, 55.740776],
    }

    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 2

    body = {
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
        'point': [37.628576, 55.740776],
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 3
