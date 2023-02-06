# pylint: disable=import-error
import pytest
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary
import tests_candidates.route_info

# pylint: disable=redefined-outer-name
@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps', 'tigraph']},
        {
            'ids': ['moscow'],
            'routers': ['linear-fallback', 'yamaps', 'tigraph'],
        },
    ],
)
async def test_route_info(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [25, 25]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55.1, 35.1]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [75, 75]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 100,
        'filters': ['infra/route_info'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'max_route_time': 3600,
        'max_route_distance': 100000,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid1'


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps', 'tigraph']},
        {
            'ids': ['moscow'],
            'routers': ['linear-fallback', 'yamaps', 'tigraph'],
        },
    ],
)
async def test_chain_route_info(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings_mocks,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55.1, 35.1]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55.1, 35.1]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55.1, 35.1]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 500,
                'left_distance': 2000,
                'destination': [55.1, 35.1],
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
                            'MAX_ROBOT_TIME': 10,
                            'MAX_ROBOT_DISTANCE': 100000,
                            'QUERY_LIMIT_MAX_LINE_DIST': 100000,
                            'ORDER_CHAIN_MAX_TOTAL_TIME': 3600,
                            'ORDER_CHAIN_MAX_TOTAL_DISTANCE': 100000,
                        },
                    },
                ],
            },
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 100,
        'filters': ['infra/route_info'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid2'


@pytest.mark.parametrize('skip', [True, False])
async def test_route_info_skip_pedestrian_on_graph(
        taxi_candidates, taxi_config, driver_positions, mockserver, skip,
):
    def _proto_masstransit_summary(time, distance):
        response = ProtoMasstransitSummary.Summaries()
        item = response.summaries.add()
        item.weight.time.value = time
        item.weight.time.text = ''
        item.weight.walking_distance.value = distance
        item.weight.walking_distance.text = ''
        item.weight.transfers_count = 1
        return response.SerializeToString()

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=10, distance=11),
            status=200,
            content_type='application/x-protobuf',
        )

    taxi_config.set_values(
        {
            'CANDIDATES_FEATURE_SWITCHES': {
                'skip_pedestrian_positions_on_graph': skip,
            },
        },
    )
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid4', 'position': [37.625344, 55.755430]}],
    )

    request_body = {
        'geoindex': 'graph',
        'limit': 10,
        'filters': ['infra/fetch_route_info'],
        'point': [37.625344, 55.755430],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) != skip
    assert _mock_router.has_calls != skip


@pytest.mark.config(
    INFRAVER_LRU_ROUTER_CACHE_SETTINGS={
        '__default__': {'enabled': True, 'size': 1000, 'lifetime': 60},
    },
)
async def test_route_info_with_router_cache(
        taxi_candidates, driver_positions, mockserver,
):
    def _proto_masstransit_summary(time, distance):
        response = ProtoMasstransitSummary.Summaries()
        item = response.summaries.add()
        item.weight.time.value = time
        item.weight.time.text = ''
        item.weight.walking_distance.value = distance
        item.weight.walking_distance.text = ''
        item.weight.transfers_count = 1
        return response.SerializeToString()

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=10, distance=11),
            status=200,
            content_type='application/x-protobuf',
        )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid4', 'position': [37.625344, 55.755430]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['infra/fetch_route_info'],
        'point': [37.625344, 55.755430],
        'zone_id': 'moscow',
    }
    for _ in range(10):
        response = await taxi_candidates.post('search', json=request_body)
        assert response.status_code == 200
        json = response.json()
        assert 'drivers' in json
        assert json['drivers']

    assert _mock_router.times_called == 1

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['infra/fetch_route_info'],
        'point': [37.625341, 55.755439],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert json['drivers']
    assert _mock_router.times_called == 2


@pytest.mark.config(
    INFRAVER_LRU_ROUTER_CACHE_SETTINGS={
        '__default__': {'enabled': True, 'size': 1000, 'lifetime': 60},
    },
)
async def test_route_info_with_redis_router_cache(
        taxi_candidates,
        driver_positions,
        mockserver,
        route_infos,
        redis_store,
):
    def _proto_masstransit_summary(time, distance):
        response = ProtoMasstransitSummary.Summaries()
        item = response.summaries.add()
        item.weight.time.value = time
        item.weight.time.text = ''
        item.weight.walking_distance.value = distance
        item.weight.walking_distance.text = ''
        item.weight.transfers_count = 1
        return response.SerializeToString()

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=7, distance=11),
            status=200,
            content_type='application/x-protobuf',
        )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid4', 'position': [37.605344, 55.715430]}],
    )

    request_body = {
        'driver_ids': [{'uuid': 'uuid4', 'dbid': 'dbid0'}],
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['infra/fetch_route_info'],
        'point': [37.625341, 55.755439],
        'zone_id': 'moscow',
    }

    # [[37.605344, 55.715430], [37.625341, 55.755439]]
    await route_infos('ucfszwxmuh/ucfv0jvyvz/')

    for _ in range(3):
        response = await taxi_candidates.post(
            'order-satisfy', json=request_body,
        )
        assert response.status_code == 200
        json = response.json()
        assert 'candidates' in json
        assert json['candidates']
        route_info = json['candidates'][0]['route_info']
        assert route_info['time'] == 10
        assert route_info['distance'] == 20

    assert _mock_router.times_called == 0

    listener = redis_store.pubsub()
    listener.subscribe('channel:route_info')
    message = listener.get_message(timeout=1)
    assert message['type'] == 'subscribe'

    request_body = {
        'driver_ids': [{'uuid': 'uuid4', 'dbid': 'dbid0'}],
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['infra/fetch_route_info'],
        'point': [37.6256, 55.75545],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('order-satisfy', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert json['candidates']
    route_info = json['candidates'][0]['route_info']
    assert route_info['time'] == 7
    assert route_info['distance'] == 11
    assert _mock_router.times_called == 1

    msg = ''
    for _ in range(5):
        message = listener.get_message(timeout=1)
        if message:
            msg = message
            break
    assert msg['type'] == 'message'
    assert [
        {
            'time': 7,
            'distance': 11,
            'type': 1,
            'geohash': b'ucfszwxmuh/ucfv0jyph1/',
        },
    ] == tests_candidates.route_info.unpack_route_infos(msg['data'])
