import pytest

MOSCOW_AIRPORT_POINT = [26, 16]
MOSCOW_POINT = [37.1946401739712, 55.478983901730004]

EKB_AIRPORT_POINT = [66, 16]

AIRPORT_IN_GRAPH_INDEX_POINT = [37.584373, 55.817079]
CITY_ORDER_POINT = [37.646516, 55.665302]


def get_config(mix_city_orders):
    return {
        'moscow': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow_airport',
            'notification_area': 'moscow_airport_notification',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow_airport_waiting',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
            'mix_city_orders': mix_city_orders,
        },
    }


def get_request_body(uuids, point, zone_id, geoindex='kdtree'):
    request_body = {
        'driver_ids': [{'uuid': uuid, 'dbid': 'dbid0'} for uuid in uuids],
        'geoindex': geoindex,
        'max_distance': 9999999,
        'limit': 3,
        'filters': [
            'infra/fetch_driver',
            'efficiency/airport_queue_city_order',
        ],
        'point': point,
        'zone_id': zone_id,
    }

    return request_body


@pytest.mark.parametrize('mix_city_orders', [True, False])
@pytest.mark.geoareas(filename='airport_geoareas.json')
async def test_airport_idx(
        taxi_candidates, driver_positions, taxi_config, mix_city_orders,
):
    taxi_config.set_values(
        dict(DISPATCH_AIRPORT_ZONES=get_config(mix_city_orders)),
    )
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': MOSCOW_AIRPORT_POINT}],
    )

    request_body = get_request_body(
        uuids=['uuid0'],
        point=MOSCOW_AIRPORT_POINT,
        zone_id='moscow_airport',
        geoindex='airport-queue',
    )
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid0'


# if set_max_route_distance is false then filter is always created
# => driver is filtered
@pytest.mark.parametrize('set_max_route_distance', [True, False])
@pytest.mark.parametrize('mix_city_orders', [True, False])
@pytest.mark.geoareas(filename='airport_geoareas_graph_search.json')
async def test_airport_queued_driver_city_order_graph_search(
        taxi_candidates,
        driver_positions,
        taxi_config,
        mix_city_orders,
        set_max_route_distance,
):
    taxi_config.set_values(
        dict(DISPATCH_AIRPORT_ZONES=get_config(mix_city_orders)),
    )
    await driver_positions(
        [
            {
                'dbid_uuid': 'dbid0_uuid0',
                'position': AIRPORT_IN_GRAPH_INDEX_POINT,
            },
        ],
    )

    # line_distance(AIRPORT_IN_GRAPH_INDEX_POINT, CITY_ORDER_POINT) ~ 17km
    request_body = get_request_body(
        uuids=['uuid0'],
        point=CITY_ORDER_POINT,
        zone_id='moscow_airport',
        geoindex='graph',
    )
    if set_max_route_distance:
        request_body['max_route_distance'] = 25000
    request_body['max_route_time'] = 1800

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    if mix_city_orders and set_max_route_distance:
        assert len(json['drivers']) == 1
        assert json['drivers'][0]['uuid'] == 'uuid0'
    else:
        assert not json['drivers']


@pytest.mark.geoareas(filename='airport_geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_CACHE_TTL=10, DISPATCH_AIRPORT_ZONES=get_config(True),
)
async def test_dispatch_airport_timeout(
        taxi_candidates, driver_positions, mockserver, mocked_time,
):
    raise_timeout = False

    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        if raise_timeout:
            raise mockserver.TimeoutError()

        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                    ],
                    'driver_needs_predict': 10,
                },
            ],
        }

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': MOSCOW_AIRPORT_POINT}],
    )

    request_body = get_request_body(
        uuids=['uuid0'],
        point=MOSCOW_AIRPORT_POINT,
        zone_id='moscow_airport',
        geoindex='airport-queue',
    )

    async def _check_search_response(is_empty):
        await taxi_candidates.invalidate_caches(
            cache_names=['dispatch-airport-queues-cache'],
        )
        response = await taxi_candidates.post('search', json=request_body)
        assert response.status_code == 200
        json = response.json()
        assert 'drivers' in json
        if not is_empty:
            assert len(json['drivers']) == 1
            assert json['drivers'][0]['uuid'] == 'uuid0'
        else:
            assert not json['drivers']

    await _check_search_response(False)

    mocked_time.sleep(5)
    raise_timeout = True
    await _check_search_response(False)

    mocked_time.sleep(6)
    raise_timeout = True
    await _check_search_response(True)


@pytest.mark.parametrize(
    'is_airport_order, uuid, mix_city_orders, filtered',
    [
        (False, 'uuid0', False, True),
        (False, 'uuid0', True, False),
        (True, 'uuid0', False, False),
        (True, 'uuid0', True, False),
        (False, 'uuid1', False, False),
        (False, 'uuid1', True, False),
        (True, 'uuid1', True, False),
        (True, 'uuid1', False, False),
    ],
)
@pytest.mark.config(DISPATCH_AIRPORT_ZONES=get_config(False))
@pytest.mark.geoareas(filename='airport_geoareas.json')
async def test_kdtree_idx_mix_city_orders(
        taxi_candidates,
        driver_positions,
        is_airport_order,
        uuid,
        mix_city_orders,
        filtered,
        taxi_config,
):
    taxi_config.set_values(
        dict(DISPATCH_AIRPORT_ZONES=get_config(mix_city_orders)),
    )
    zone_id = 'moscow'
    point = MOSCOW_POINT
    if is_airport_order:
        zone_id = 'moscow_airport'
        point = MOSCOW_AIRPORT_POINT

    await driver_positions(
        [{'dbid_uuid': 'dbid0_' + uuid, 'position': MOSCOW_AIRPORT_POINT}],
    )

    request_body = get_request_body(uuids=[uuid], point=point, zone_id=zone_id)

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    ans_len = 0 if filtered else 1
    assert len(json['drivers']) == ans_len
    if not filtered:
        assert json['drivers'][0]['uuid'] == uuid


@pytest.mark.geoareas(filename='airport_geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_CACHE_TTL=10, DISPATCH_AIRPORT_ZONES=get_config(True),
)
@pytest.mark.parametrize('use_check_in_flow', [True, False])
async def test_dispatch_airport_check_in_order(
        taxi_candidates,
        driver_positions,
        mockserver,
        testpoint,
        use_check_in_flow,
):
    @testpoint('airport_queue_city_order_check_in_flow')
    def check_in_flow(_):
        return

    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                    ],
                    'driver_needs_predict': 10,
                },
            ],
        }

    await taxi_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': MOSCOW_AIRPORT_POINT}],
    )

    request_body = get_request_body(
        uuids=['uuid0'],
        point=MOSCOW_AIRPORT_POINT,
        zone_id='moscow_airport',
        geoindex='airport-queue',
    )
    if use_check_in_flow:
        request_body['dispatch_check_in'] = {'pickup_line': 'moscow'}

    await taxi_candidates.invalidate_caches(
        cache_names=['dispatch-airport-queues-cache'],
    )
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json

    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid0'

    assert check_in_flow.times_called == (1 if use_check_in_flow else 0)


@pytest.mark.geoareas(filename='airport_geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES={
        **get_config(True),
        'ekb': {
            'airport_title_key': 'ekb_airport_key',
            'enabled': True,
            'main_area': 'ekb_airport',
            'notification_area': 'ekb_airport_notification',
            'old_mode_enabled': False,
            'tariff_home_zone': 'ekb',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'ekb_airport_waiting',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
            'mix_city_orders': False,
        },
    },
)
@pytest.mark.parametrize(
    'fallback_search_main_areas', [None, [], ['moscow_airport']],
)
async def test_dispatch_airport_fallback_search_airports(
        taxi_candidates,
        driver_positions,
        mockserver,
        taxi_config,
        fallback_search_main_areas,
):
    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        if request.query['airport'] == 'ekb':
            return {'queues': []}

        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                    ],
                    'driver_needs_predict': 10,
                },
            ],
        }

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb'][
        'fallback_search_main_areas'
    ] = fallback_search_main_areas
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': MOSCOW_AIRPORT_POINT}],
    )

    request_body = get_request_body(
        uuids=['uuid0'],
        point=EKB_AIRPORT_POINT,
        zone_id='ekb_airport',
        geoindex='airport-queue',
    )

    await taxi_candidates.invalidate_caches()
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json

    if fallback_search_main_areas:
        assert len(json['drivers']) == 1
        assert json['drivers'][0]['uuid'] == 'uuid0'
    else:
        assert not json['drivers']


@pytest.mark.parametrize('is_airport_order', [False, True])
@pytest.mark.config(DISPATCH_AIRPORT_ZONES=get_config(False))
@pytest.mark.geoareas(filename='airport_geoareas.json')
async def test_filtered_drivers(
        taxi_candidates, driver_positions, is_airport_order, mockserver,
):
    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                    ],
                    'driver_needs_predict': 10,
                },
            ],
            'filtered': [
                {'dbid_uuid': 'dbid0_uuid1', 'reason': 'user_cancel'},
            ],
        }

    zone_id, point = ['moscow', MOSCOW_POINT]
    if is_airport_order:
        zone_id, point = ['moscow_airport', MOSCOW_AIRPORT_POINT]

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': MOSCOW_AIRPORT_POINT},
            {'dbid_uuid': 'dbid0_uuid1', 'position': MOSCOW_AIRPORT_POINT},
        ],
    )

    request_body = get_request_body(
        uuids=['uuid0', 'uuid1'], point=point, zone_id=zone_id,
    )

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    etalon = {
        'drivers': [
            {'position': [26.0, 16.0], 'dbid': 'dbid0', 'uuid': 'uuid1'},
        ],
    }
    if is_airport_order:
        etalon = {
            'drivers': [
                {'position': [26.0, 16.0], 'dbid': 'dbid0', 'uuid': 'uuid0'},
                {
                    'position': [26.0, 16.0],
                    'dbid': 'dbid0',
                    'uuid': 'uuid1',
                    'metadata': {
                        'airport_queue': {
                            'filtered': {'reason': 'user_cancel'},
                        },
                    },
                },
            ],
        }
    json['drivers'].sort(key=lambda x: x['uuid'])
    assert etalon == json
