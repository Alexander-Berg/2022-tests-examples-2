import json

import pytest


def enable_version_experiment(experiments3):
    for exp_name in [
            'combo_outer_taximeter_version',
            'combo_taximeter_version',
    ]:
        experiments3.add_config(
            match={
                'predicate': {'type': 'true'},
                'enabled': True,
                'applications': [
                    {'name': 'taximeter', 'version_range': {'from': '8.0.0'}},
                    {
                        'name': 'taximeter-ios',
                        'version_range': {'from': '1.0.0'},
                    },
                ],
            },
            name=exp_name,
            consumers=['candidates/filters'],
            clauses=[
                {
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                    'enabled': True,
                },
            ],
            default_value={'enabled': False},
        )


@pytest.mark.parametrize(
    'zone_id, allowed_classes, expected_candidates',
    [
        ('moscow', ['econom'], ['dbid0_uuid1', 'dbid0_uuid2']),
        ('moscow', ['minivan'], ['dbid0_uuid1', 'dbid0_uuid2']),
        ('moscow', ['econom', 'comfort'], ['dbid0_uuid1', 'dbid0_uuid2']),
        ('spb', ['econom'], ['dbid0_uuid2']),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
        'spb': {'__default__': False},
    },
)
async def test_combo_free(
        taxi_candidates,
        driver_positions,
        combo_contractors,
        zone_id,
        allowed_classes,
        expected_candidates,
        experiments3,
):
    enable_version_experiment(experiments3)

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.63, 55.74]},
        ],
    )

    combo_contractors([{'dbid_uuid': 'dbid0_uuid1'}])

    request_body = {
        'limit': 10,
        'zone_id': zone_id,
        'allowed_classes': allowed_classes,
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
    }
    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]

    assert sorted(candidates) == expected_candidates


@pytest.mark.parametrize(
    'request_override,request_check, expected_candidates',
    [
        ({}, {}, ['dbid0_uuid1', 'dbid0_uuid2']),
        (
            {
                'order': {
                    'user_id': 'user_id',
                    'calc': {'alternative_type': 'combo_order'},
                },
            },
            {'calc_alternative_type': 'combo_order'},
            ['dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'order': {
                    'user_id': 'user_id',
                    'calc': {'alternative_type': 'combo_inner'},
                },
            },
            {'calc_alternative_type': 'combo_inner'},
            ['dbid0_uuid1'],
        ),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
    CANDIDATES_BULK_FETCHERS={
        '__default__': {
            'max_requests_in_flight': 10,
            'max_bulk_size': 2,
            'max_delay_ms': 200,
        },
    },
)
async def test_combo_info(
        taxi_candidates,
        driver_positions,
        mockserver,
        combo_contractors,
        request_override,
        request_check,
        expected_candidates,
        experiments3,
):
    enable_version_experiment(experiments3)

    @mockserver.handler('/combo-contractors/v1/match')
    def _mock_match(request):
        assert 'order' in request.json
        assert request.json.get('order').get(
            'calc_alternative_type',
        ) == request_check.get('calc_alternative_type')
        assert 'contractors' in request.json
        assert request.json.get('order').get('order_id') == 'order_id'
        assert request.json.get('order').get('user_id') == 'user_id'
        contractors = request.json['contractors']
        ids = set()
        for contractor in contractors:
            ids.add(contractor['dbid_uuid'])
        assert ids == {'dbid0_uuid0', 'dbid0_uuid1'}

        return mockserver.make_response(
            response=json.dumps(
                {
                    'contractors': [
                        {
                            'dbid_uuid': 'dbid0_uuid1',
                            'combo_info': {'active': True},
                        },
                    ],
                },
            ),
        )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.63, 55.74]},
        ],
    )

    combo_contractors(
        [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
    )

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'comfort'],
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
        'order_id': 'order_id',
        'order': {'user_id': 'user_id'},
    }
    request_body.update(request_override)
    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]

    assert sorted(candidates) == expected_candidates


@pytest.mark.parametrize('need_properties', [True, False, None])
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
    CANDIDATES_BULK_FETCHERS={
        '__default__': {
            'max_requests_in_flight': 10,
            'max_bulk_size': 2,
            'max_delay_ms': 200,
        },
    },
)
async def test_fetch_combo_info_atlas(
        taxi_candidates,
        driver_positions,
        mockserver,
        combo_contractors,
        experiments3,
        need_properties,
):
    enable_version_experiment(experiments3)
    match_parameters = {
        'is_filtered': False,
        'is_nested': True,
        'parameters': {
            'azimuth_ca_0': 337.0,
            'azimuth_ca_1': 173.0,
            'base_driving_time_0': 0.0,
            'base_driving_time_1': 0.0,
            'base_left_time_0': 9538.0,
            'base_left_time_1': 0.0,
            'base_past_time_0': 6960.0,
            'base_past_time_1': 0.0,
            'base_transporting_time_0': 16027.0,
            'base_transporting_time_1': 4821.0,
            'driving_time_0': 0.0,
            'driving_time_1': 2332.0,
            'left_time_0': 9544.0,
            'left_time_1': 7153.0,
            'past_time_0': 6960.0,
            'past_time_1': 0.0,
            'time_delta': 430.0,
            'transporting_time_0': 16219.0,
            'transporting_time_1': 4821.0,
        },
    }

    @mockserver.handler('/combo-contractors/v1/match')
    def _mock_match(request):
        assert (
            request.json.get('need_match_parameters', None) == need_properties
        )
        match_response = {
            'contractors': [
                {'dbid_uuid': 'dbid0_uuid1', 'combo_info': {'active': True}},
            ],
        }

        if need_properties:
            match_response['contractors'][0]['combo_info'].update(
                {'match_parameters': match_parameters},
            )

        return mockserver.make_response(response=json.dumps(match_response))

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
        ],
    )

    combo_contractors(
        [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
    )

    request_body = {
        'filtration': 'order',
        'point': [37.63, 55.74],
        'destination': [37.63, 55.76],
        'order': {'calc': {'alternative_type': 'combo_inner'}},
        'combo': {'need_inactive': True},
        'data_keys': [],
        'allowed_classes': ['econom'],
    }
    if need_properties is not None:
        request_body['combo']['need_properties'] = need_properties

    response = await taxi_candidates.post('list-profiles', json=request_body)

    assert response.status_code == 200

    metadata = {
        candidate['id']: candidate['metadata']
        for candidate in response.json()['drivers']
    }

    assert len(metadata) == 2
    assert metadata['dbid0_uuid0'] == {'combo': None}
    if need_properties:
        assert metadata['dbid0_uuid1'] == {
            'combo': {'active': True, 'match_parameters': match_parameters},
        }
    else:
        assert metadata['dbid0_uuid1'] == {'combo': {'active': True}}


@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
async def test_combo_counter(
        taxi_candidates,
        driver_positions,
        mockserver,
        experiments3,
        combo_contractors,
):
    enable_version_experiment(experiments3)

    experiments3.add_config(
        name='combo_preferred',
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
                'value': {'econom': 1},
            },
        ],
        default_value={},
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.624135, 55.751527]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.624800, 55.745778]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.624328, 55.736542]},
        ],
    )

    combo_contractors([{'dbid_uuid': 'dbid0_uuid2'}])

    request_body = {
        'limit': 2,
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'comfort'],
        'point': [37.624135, 55.751527],
        'destination': [37.64, 55.73],
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]

    assert sorted(candidates) == ['dbid0_uuid0', 'dbid0_uuid2']


@pytest.mark.parametrize(
    'request_override, expected_candidates',
    [
        ({}, []),
        (
            {'destination': [37.64, 55.73]},
            [{'id': 'dbid0_uuid0', 'metadata': {'combo': {'active': True}}}],
        ),
        (
            {'combo': {'need_inactive': True}},
            [
                {'id': 'dbid0_uuid0', 'metadata': {'combo': {'active': True}}},
                {'id': 'dbid0_uuid1', 'metadata': {'combo': {}}},
            ],
        ),
        (
            {'destination': [37.64, 55.73], 'combo': {'need_inactive': True}},
            [
                {'id': 'dbid0_uuid0', 'metadata': {'combo': {'active': True}}},
                {'id': 'dbid0_uuid1', 'metadata': {'combo': {}}},
            ],
        ),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
async def test_combo_inactive(
        taxi_candidates,
        driver_positions,
        mockserver,
        combo_contractors,
        experiments3,
        request_override,
        expected_candidates,
):
    enable_version_experiment(experiments3)

    @mockserver.handler('/combo-contractors/v1/match')
    def _mock_match(request):
        return mockserver.make_response(
            response=json.dumps(
                {
                    'contractors': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'combo_info': {'active': True},
                        },
                        {'dbid_uuid': 'dbid0_uuid1', 'combo_info': {}},
                    ],
                },
            ),
        )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
        ],
    )

    combo_contractors(
        [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
    )

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'comfort'],
        'point': [37.63, 55.74],
        'order_id': 'order_id',
        'order': {'user_id': 'user_id'},
        'filtration': 'order',
        'data_keys': [],
    }
    request_body.update(request_override)
    response = await taxi_candidates.post('list-profiles', json=request_body)

    assert response.status_code == 200

    candidates = [
        {'id': candidate['id'], 'metadata': candidate['metadata']}
        for candidate in response.json()['drivers']
    ]

    assert sorted(candidates, key=lambda x: x['id']) == expected_candidates


@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
    CANDIDATES_BULK_FETCHERS={
        '__default__': {
            'max_requests_in_flight': 10,
            'max_bulk_size': 2,
            'max_delay_ms': 200,
        },
    },
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
)
@pytest.mark.experiments3(
    is_config=True,
    name='use_route_predicted_contractor_positions',
    consumers=['candidates/user'],
    default_value={'enabled': True},
)
async def test_combo_info_predicted_positions(
        taxi_candidates,
        driver_positions,
        mockserver,
        combo_contractors,
        experiments3,
        driver_positions_route_predicted,
):
    enable_version_experiment(experiments3)

    await driver_positions_route_predicted(
        [
            {
                'dbid_uuid': f'dbid0_uuid{i}',
                'positions': [
                    {'position': [37.624826, 55.755331], 'shift': 0},
                    {'position': [37.624826, 55.755331], 'shift': 10},
                    {'position': [37.625618, 55.752399], 'shift': 20},
                    {'position': [37.625120, 55.757644], 'shift': 30},
                    {'position': [37.625110, 55.757624], 'shift': 40},
                ],
            }
            for i in range(3)
        ],
    )

    @mockserver.handler('/combo-contractors/v1/match')
    def _mock_match(request):
        assert 'order' in request.json
        assert 'contractors' in request.json
        assert request.json.get('order').get('order_id') == 'order_id'
        assert request.json.get('order').get('user_id') == 'user_id'
        contractors = request.json['contractors']
        ids = set()
        for contractor in contractors:
            ids.add(contractor['dbid_uuid'])
            assert 'predicted_positions' in contractor
        assert ids == {'dbid0_uuid0', 'dbid0_uuid1'}

        return mockserver.make_response(
            response=json.dumps(
                {
                    'contractors': [
                        {
                            'dbid_uuid': 'dbid0_uuid1',
                            'combo_info': {'active': True},
                        },
                    ],
                },
            ),
        )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.624826, 55.755331]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.624826, 55.755331]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.624826, 55.755331]},
        ],
    )

    combo_contractors(
        [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
    )

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'comfort'],
        'point': [37.63, 55.74],
        'destination': [37.63, 55.73],
        'order_id': 'order_id',
        'max_distance': 100000,
        'order': {'user_id': 'user_id'},
    }

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert sorted(candidates) == ['dbid0_uuid1', 'dbid0_uuid2']
