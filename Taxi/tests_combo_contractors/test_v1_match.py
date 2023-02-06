# pylint: disable=import-error,C0302
import datetime
import json

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

NOW = datetime.datetime(2001, 9, 9, 1, 46, 39)


@pytest.mark.parametrize(
    'testcase',
    [
        'no_combo',
        'matched_with_parameters',
        'matched_without_parameters',
        'not_matched',
        'old_finished_order',
    ],
)
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_match(
        taxi_combo_contractors,
        mockserver,
        load_json,
        testpoint,
        redis_store,
        testcase,
):
    test_data = load_json('match_query_test_cases.json')[testcase]
    request_body = test_data['request']
    expected_contractors = test_data['response']

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_retrieve(request):
        return mockserver.make_response('{"profiles": []}', 200)

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()
    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )
    await geobus_payload_processed.wait_call()
    response = await taxi_combo_contractors.post(
        '/v1/match', json=request_body,
    )
    assert response.status_code == 200
    contractors = response.json()['contractors']

    assert (
        sorted(contractors, key=lambda x: x['dbid_uuid'])
        == expected_contractors
    )


@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_direction.json')
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_match_contractor_direction(
        taxi_combo_contractors, mockserver, testpoint, redis_store, load_json,
):
    requests_with_direction = 0

    @testpoint('on_perform_router_request')
    def on_perform_router_request(data):
        nonlocal requests_with_direction
        if data and 'source_direction' in data:
            assert data['source_direction'] == 43
            requests_with_direction += 1

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')

    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    response = await taxi_combo_contractors.post(
        '/v1/match',
        json={
            'contractors': [{'dbid_uuid': 'dbid_uuid0'}],
            'order': {
                'calc_alternative_type': 'combo',
                'order_id': 'order_id1',
                'route': [[37.522773, 56.193026], [37.550239, 55.89233]],
                'tariff_classes': ['econom'],
                'tariff_zone': 'moscow',
            },
        },
    )

    await on_perform_router_request.wait_call()

    assert requests_with_direction == 4

    assert response.status_code == 200
    contractors = response.json()['contractors']

    assert contractors == [
        {
            'combo_info': {
                'active': True,
                'batch_id': 'order_id0',
                'category': 'category0',
                'extra_properties': {'other_score': 0.9776777340086288},
                'route': [
                    {
                        'order_id': 'order_id0',
                        'passed_at': '2001-09-08T23:50:39+00:00',
                        'position': [37.201749, 56.722466],
                        'type': 'start',
                    },
                    {
                        'order_id': 'order_id1',
                        'position': [37.522773, 56.193026],
                        'type': 'start',
                    },
                    {
                        'order_id': 'order_id1',
                        'position': [37.550239, 55.89233],
                        'type': 'finish',
                    },
                    {
                        'order_id': 'order_id0',
                        'position': [37.583198, 55.744195],
                        'type': 'finish',
                    },
                ],
                'score': 0.9776777340086288,
            },
            'dbid_uuid': 'dbid_uuid0',
        },
    ]


@pytest.mark.parametrize(
    'request_override, times, azimuths, base_order_info',
    [
        (
            {'contractors': [{'dbid_uuid': 'dbid_uuid0'}]},
            {'order_id0': 16027, 'order_id1': 4821},
            {
                'azimuth_ca_1': 173.0,
                'azimuth_cb_1': 175.0,
                'azimuth_cb_0': 175.0,
                'azimuth_ca_0': 337.0,
            },
            {},
        ),
        (
            {'contractors': [{'dbid_uuid': 'dbid_uuid1'}]},
            {'order_id0': 16027, 'order_id1': 4821},
            {
                'azimuth_ca_1': 173.0,
                'azimuth_cb_1': 175.0,
                'azimuth_cb_0': 175.0,
                'azimuth_ca_0': 337.0,
            },
            {},
        ),
        (
            {'contractors': [{'dbid_uuid': 'dbid_uuid0'}]},
            {'order_id0': 111, 'order_id1': 4821},
            {
                'azimuth_ca_1': 173.0,
                'azimuth_cb_1': 175.0,
                'azimuth_cb_0': 175.0,
                'azimuth_ca_0': 337.0,
            },
            {'order_id0': {'d': 1111, 't': 111}},
        ),
    ],
)
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_base_transporting_time(
        taxi_combo_contractors,
        mockserver,
        load_json,
        testpoint,
        redis_store,
        request_override,
        times,
        azimuths,
        base_order_info,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_retrieve(request):
        return mockserver.make_response('{"profiles": []}', 200)

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    @testpoint('base_transporting_time')
    def base_transporting_time(data):
        assert data == times

    @testpoint('order_azimuths')
    def order_azimuths(data):
        assert data == azimuths

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    for key, value in base_order_info.items():
        redis_store.set('BaseOrderRoute:' + key, json.dumps(value))

    request_body = {
        'order': {
            'order_id': 'order_id1',
            'tariff_zone': 'moscow',
            'tariff_classes': ['econom'],
            'route': [[37.522773, 56.193026], [37.550239, 55.892330]],
        },
        'contractors': [{'dbid_uuid': 'dbid_uuid0'}],
    }
    request_body.update(request_override)
    response = await taxi_combo_contractors.post(
        '/v1/match', json=request_body,
    )
    assert response.status_code == 200
    await base_transporting_time.wait_call()
    await order_azimuths.wait_call()

    base_order1_info = redis_store.get('BaseOrderRoute:order_id1')
    assert base_order1_info == b'{"t":4821,"d":33479.405969428764}'


@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    COMBO_CONTRACTORS_V1_MATCH_USE_POSITION_FROM_REQUEST=True,
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(
    is_config=True,
    name='combo_contractors_use_predicted_positions',
    consumers=['combo_contractors/order'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'enabled': True,
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'phone_id',
                                'arg_type': 'string',
                                'value': 'user_phone_id1',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'user_id',
                                'arg_type': 'string',
                                'value': 'user_id1',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {'enabled': True, 'timeshift': 20},
        },
    ],
)
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_match_no_geobus(
        taxi_combo_contractors, testpoint, redis_store, load_json,
):
    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    geobus_response = [
        {
            'combo_info': {
                'active': True,
                'batch_id': 'order_id4',
                'category': 'category0',
                'route': [
                    {
                        'order_id': 'order_id4',
                        'passed_at': '2001-09-09T01:30:39+00:00',
                        'position': [37.176704, 56.695531],
                        'type': 'start',
                    },
                    {
                        'order_id': 'order_id1',
                        'position': [37.286567, 56.392697],
                        'type': 'start',
                    },
                    {
                        'order_id': 'order_id1',
                        'position': [37.451362, 56.050641],
                        'type': 'finish',
                    },
                    {
                        'order_id': 'order_id4',
                        'position': [37.627143, 55.693142],
                        'type': 'finish',
                    },
                ],
                'score': 1.0021654786610124,
            },
            'dbid_uuid': 'dbid_uuid4',
        },
    ]

    response = await taxi_combo_contractors.post(
        '/v1/match',
        json={
            'order': {
                'order_id': 'order_id1',
                'tariff_zone': 'moscow',
                'tariff_classes': ['econom'],
                'user_id': 'user_id1',
                'user_phone_id': 'user_phone_id1',
                'route': [[37.286567, 56.392697], [37.451362, 56.050641]],
                'calc_alternative_type': 'combo',
            },
            'contractors': [{'dbid_uuid': 'dbid_uuid4'}],
        },
    )
    assert response.status_code == 200

    contractors = response.json()['contractors']

    assert contractors == geobus_response

    # explicit positions
    response = await taxi_combo_contractors.post(
        '/v1/match',
        json={
            'order': {
                'order_id': 'order_id1',
                'tariff_zone': 'moscow',
                'tariff_classes': ['econom'],
                'user_id': 'user_id1',
                'user_phone_id': 'user_phone_id1',
                'route': [[37.286567, 56.392697], [37.451362, 56.050641]],
                'calc_alternative_type': 'combo',
            },
            'contractors': [
                {
                    'dbid_uuid': 'dbid_uuid4',
                    'predicted_positions': [
                        {
                            'position': [  # opposite to positions.json
                                37.617846,
                                55.497848,
                            ],
                            'timeshift': 20,
                        },
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200

    contractors = response.json()['contractors']
    assert contractors == [
        {
            'combo_info': {
                'category': 'category0',
                'route': [
                    {
                        'order_id': 'order_id4',
                        'passed_at': '2001-09-09T01:30:39+00:00',
                        'position': [37.176704, 56.695531],
                        'type': 'start',
                    },
                    {
                        'order_id': 'order_id4',
                        'position': [37.627143, 55.693142],
                        'type': 'finish',
                    },
                ],
            },
            'dbid_uuid': 'dbid_uuid4',
        },
    ]


@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    COMBO_CONTRACTORS_V1_MATCH_USE_POSITION_FROM_REQUEST=True,
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(
    is_config=True,
    name='combo_contractors_use_predicted_positions',
    consumers=['combo_contractors/order'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'clause',
            'predicate': {'type': 'true'},
            'value': {'enabled': True, 'timeshift': 20},
        },
    ],
)
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_match_no_geobus_approximate_position(taxi_combo_contractors):
    # 10 isn't exact but it will be chosen as closest predicted position
    response = await taxi_combo_contractors.post(
        '/v1/match',
        json={
            'order': {
                'order_id': 'order_id1',
                'tariff_zone': 'moscow',
                'tariff_classes': ['econom'],
                'route': [[37.286567, 56.392697], [37.451362, 56.050641]],
                'calc_alternative_type': 'combo',
            },
            'contractors': [
                {
                    'dbid_uuid': 'dbid_uuid4',
                    'predicted_positions': [
                        {'position': [37.617846, 55.497848], 'timeshift': 10},
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200

    contractors = response.json()['contractors']
    assert contractors == [
        {
            'combo_info': {
                'category': 'category0',
                'route': [
                    {
                        'order_id': 'order_id4',
                        'passed_at': '2001-09-09T01:30:39+00:00',
                        'position': [37.176704, 56.695531],
                        'type': 'start',
                    },
                    {
                        'order_id': 'order_id4',
                        'position': [37.627143, 55.693142],
                        'type': 'finish',
                    },
                ],
            },
            'dbid_uuid': 'dbid_uuid4',
        },
    ]


def enable_match_config(experiments3, value_override):
    value = {
        'category': 'category0',
        'filter': 'filter0',
        'parameters': {'time_delta': 99999999},
        'score': 'score0',
    }

    value.update(value_override)

    experiments3.add_config(
        match={'enabled': True, 'predicate': {'type': 'true'}},
        name='combo_contractors_match_config',
        consumers=['combo_contractors/order'],
        clauses=[
            {
                'enabled': True,
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'calc_alternative_type',
                                    'arg_type': 'string',
                                    'value': 'combo',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'passenger_index',
                                    'arg_type': 'int',
                                    'value': 1,
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': value,
            },
        ],
        default_value={},
    )


@pytest.mark.parametrize(
    'config_override, should_pass',
    [({'linear_filter': 'linear_filter0'}, False), ({}, True)],
)
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_least_angle_heuristic(
        taxi_combo_contractors,
        mockserver,
        load_json,
        testpoint,
        redis_store,
        experiments3,
        config_override,
        should_pass,
):
    request_body = load_json('request.json')

    enable_match_config(experiments3, config_override)

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()
    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )
    await geobus_payload_processed.wait_call()
    response = await taxi_combo_contractors.post(
        '/v1/match', json=request_body,
    )
    assert response.status_code == 200
    contractors = response.json()['contractors']

    assert len(contractors) == 1
    assert 'combo_info' in contractors[0]
    assert contractors[0]['dbid_uuid'] == 'dbid_uuid0'
    assert (
        'active' in contractors[0]['combo_info']
        and (contractors[0]['combo_info']['active'] or not should_pass)
        or not should_pass
    )


def enable_ordered_matching(experiments3):
    experiments3.add_config(
        match={'enabled': True, 'predicate': {'type': 'true'}},
        name='combo_contractors_match_start_points_ordered',
        consumers=['combo_contractors/order'],
        clauses=[
            {
                'enabled': True,
                'predicate': {'init': {}, 'type': 'true'},
                'value': {'enabled': True},
            },
        ],
        default_value={},
    )


@pytest.mark.parametrize(
    'ordered_matching, contractors',
    [
        (
            False,
            [
                {
                    'combo_info': {
                        'active': True,
                        'batch_id': 'order_id0',
                        'category': 'category0',
                        'route': [
                            {
                                'order_id': 'order_id1',
                                'position': [37.612984, 55.74176],
                                'type': 'start',
                            },
                            {
                                'order_id': 'order_id0',
                                'position': [37.607491, 55.786572],
                                'type': 'start',
                            },
                            {
                                'order_id': 'order_id0',
                                'position': [37.571026, 56.345312],
                                'type': 'finish',
                            },
                            {
                                'order_id': 'order_id1',
                                'position': [37.530388, 56.717674],
                                'type': 'finish',
                            },
                        ],
                        'score': 0.9998780388649484,
                    },
                    'dbid_uuid': 'dbid_uuid0',
                },
            ],
        ),
        (
            True,
            [
                {
                    'combo_info': {
                        'active': True,
                        'batch_id': 'order_id0',
                        'category': 'category0',
                        'route': [
                            {
                                'order_id': 'order_id0',
                                'position': [37.607491, 55.786572],
                                'type': 'start',
                            },
                            {
                                'order_id': 'order_id1',
                                'position': [37.612984, 55.74176],
                                'type': 'start',
                            },
                            {
                                'order_id': 'order_id0',
                                'position': [37.571026, 56.345312],
                                'type': 'finish',
                            },
                            {
                                'order_id': 'order_id1',
                                'position': [37.530388, 56.717674],
                                'type': 'finish',
                            },
                        ],
                        'score': 0.9447261273718983,
                    },
                    'dbid_uuid': 'dbid_uuid0',
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_match_in_driving(
        taxi_combo_contractors,
        mockserver,
        experiments3,
        testpoint,
        redis_store,
        load_json,
        ordered_matching,
        contractors,
):
    enable_match_config(experiments3, {})

    if ordered_matching:
        enable_ordered_matching(experiments3)

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    request_json = {
        'order': {
            'order_id': 'order_id1',
            'tariff_zone': 'moscow',
            'tariff_classes': ['econom'],
            'route': [[37.612984, 55.741760], [37.530388, 56.717674]],
            'calc_alternative_type': 'combo',
        },
        'contractors': [{'dbid_uuid': 'dbid_uuid0'}],
    }

    response = await taxi_combo_contractors.post(
        '/v1/match', json=request_json,
    )

    assert response.status_code == 200

    assert contractors == response.json()['contractors']


ROUTER_CALLS_PER_MATCH = 4


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_routing_cache(
        taxi_combo_contractors, mockserver, testpoint, redis_store, load_json,
):

    router_requests = 0

    @testpoint('on_perform_router_request')
    def on_perform_router_request(data):
        nonlocal router_requests
        router_requests += 1

    cache_updates = 0

    @testpoint('routing_cache_updated')
    def cache_updated(data):
        nonlocal cache_updates
        cache_updates += 1

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    request_json = {
        'contractors': [{'dbid_uuid': 'dbid_uuid0'}],
        'order': {
            'calc_alternative_type': 'combo',
            'order_id': 'order_id1',
            'route': [[37.522773, 56.193026], [37.550239, 55.89233]],
            'tariff_classes': ['econom'],
            'tariff_zone': 'moscow',
        },
    }

    for i in range(2):
        response = await taxi_combo_contractors.post(
            '/v1/match', json=request_json,
        )
        await on_perform_router_request.wait_call()
        assert response.status_code == 200

        # should not grow after first match
        assert router_requests == ROUTER_CALLS_PER_MATCH

        contractors = response.json()['contractors']
        assert (
            contractors
            and contractors[0]['combo_info']['active']
            and contractors[0]['dbid_uuid'] == 'dbid_uuid0'
        )

        # wait until all router responses are saved to redis
        while i == 0 and cache_updates < ROUTER_CALLS_PER_MATCH:
            await cache_updated.wait_call()


@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['linear-fallback']},
        {
            'routers': ['tigraph'],
            'target': 'tigraph',
            'service': 'combo-contractors',
        },
    ],
    ROUTER_TIGRAPH_USERVICES_ENABLED=True,
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
@pytest.mark.parametrize('use_tigraph', [True, False])
async def test_match_router_selection(
        taxi_combo_contractors,
        mockserver,
        load_json,
        testpoint,
        redis_store,
        experiments3,
        use_tigraph,
):
    test_data = load_json('match_query_test_cases.json')['no_combo']
    request_body = test_data['request']

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_retrieve(request):
        return mockserver.make_response('{"profiles": []}', 200)

    @mockserver.handler('tigraph-router/route')
    async def tigraph_router_handler(request):
        raise mockserver.TimeoutError()

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    if use_tigraph:
        experiments3.add_experiments_json(
            load_json('experiments3_routing_settings.json'),
        )

    await taxi_combo_contractors.enable_testpoints()
    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )
    await geobus_payload_processed.wait_call()
    response = await taxi_combo_contractors.post(
        '/v1/match', json=request_body,
    )
    assert response.status_code == 200

    if use_tigraph:
        assert tigraph_router_handler.has_calls
    else:
        assert not tigraph_router_handler.has_calls


@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'order_match_rules.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
@pytest.mark.parametrize('dry_run_enabled', [True, False])
async def test_match_with_dry_run(
        taxi_combo_contractors,
        mockserver,
        load_json,
        testpoint,
        redis_store,
        experiments3,
        dry_run_enabled,
):
    if dry_run_enabled:
        experiments3.add_experiments_json(
            load_json('experiments3_dry_run.json'),
        )

    test_data = load_json('match_query_test_cases.json')[
        'matched_with_parameters'
    ]
    request_body = test_data['request']
    expected_contractors = test_data['response']

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_retrieve(request):
        return mockserver.make_response('{"profiles": []}', 200)

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    @testpoint('match_dry_run')
    def match_dry_run(data):
        return data

    await taxi_combo_contractors.enable_testpoints()
    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )
    await geobus_payload_processed.wait_call()
    response = await taxi_combo_contractors.post(
        '/v1/match', json=request_body,
    )
    assert response.status_code == 200
    contractors = response.json()['contractors']

    assert (
        sorted(contractors, key=lambda x: x['dbid_uuid'])
        == expected_contractors
    )

    if dry_run_enabled:
        assert match_dry_run.times_called == 3
        dry_run_drivers = [match_dry_run.next_call()['data'] for _ in range(3)]
        dry_run_drivers = sorted(dry_run_drivers, key=lambda x: x['dbid_uuid'])
        assert dry_run_drivers == [
            {'dbid_uuid': 'dbid_uuid0', 'router_target': None},
            {'dbid_uuid': 'dbid_uuid2', 'router_target': 'tigraph'},
            {'dbid_uuid': 'dbid_uuid6', 'router_target': None},
        ]
    else:
        assert match_dry_run.times_called == 0
