import pytest

from tests_pin_storage import common


def redis_store():
    return pytest.mark.redis_store(
        [
            'rpush',
            '1552003200',
            common.build_pin(
                [],
                'test_offer_id',
                'test_order_id',
                'test_phone_id0',
                0.123,
                0.456,
                12.7,
                45.8,
                'test_user_id0',
                'default',
                [],
                1552003200000,
            ),
        ],
        [
            'rpush',
            '1552003200',
            common.build_pin(
                [],
                'test_offer_id',
                'test_order_id',
                'test_phone_id1',
                10.124,
                10.457,
                12.8,
                45.9,
                'test_user_id1',
                'default',
                [],
                1552003200000,
            ),
        ],
        [
            'rpush',
            '1552003200',
            common.build_pin(
                [
                    {
                        'experiment_id': 'ex0',
                        'experiment_name': 'test_experiment_name',
                        'classes': [
                            {
                                'name': 'econom',
                                'cost': 1,
                                'estimated_waiting': 5,
                                'calculation_meta': {
                                    'counts': {
                                        # 'by_statuses': {},
                                        'free': 2,
                                        'free_chain': 3,
                                        'total': 4,
                                        'pins': 6,
                                        'radius': 7,
                                    },
                                    'smooth': {
                                        'point_a': {
                                            'value': 45,
                                            'is_default': False,
                                        },
                                    },
                                },
                                'surge': {
                                    'value': 8,
                                    'surcharge': {
                                        'alpha': 42,
                                        'beta': 43,
                                        'value': 44,
                                    },
                                },
                                'value_raw': 9,
                            },
                            {
                                'name': 'vip',
                                'cost': 11,
                                'estimated_waiting': 15,
                                'calculation_meta': {
                                    'counts': {
                                        # 'by_statuses': {},
                                        'free': 12,
                                        'free_chain': 13,
                                        'total': 14,
                                        'pins': 16,
                                        'radius': 17,
                                    },
                                    'smooth': {
                                        'point_a': {
                                            'value': 45,
                                            'is_default': False,
                                        },
                                    },
                                },
                                'surge': {
                                    'value': 18,
                                    'surcharge': {
                                        'alpha': 42,
                                        'beta': 43,
                                        'value': 44,
                                    },
                                },
                                'value_raw': 19,
                            },
                        ],
                    },
                ],
                'test_offer_id',
                'test_order_id',
                'test_phone_id2',
                20.125,
                20.458,
                12.9,
                45.0,
                'test_user_id2',
                'default',
                [
                    {
                        'name': 'econom',
                        'cost': 21,
                        'estimated_waiting': 25,
                        'calculation_meta': {
                            'counts': {
                                # 'by_statuses': {},
                                'free': 22,
                                'free_chain': 23,
                                'total': 24,
                                'pins': 26,
                                'radius': 27,
                            },
                            'smooth': {
                                'point_a': {'value': 45, 'is_default': False},
                                'point_b': {'value': 22, 'is_default': False},
                            },
                        },
                        'surge': {
                            'value': 28,
                            'surcharge': {
                                'alpha': 42,
                                'beta': 43,
                                'value': 44,
                            },
                        },
                        'value_raw': 29,
                    },
                    {
                        'name': 'vip',
                        'cost': 31,
                        'estimated_waiting': 35,
                        'calculation_meta': {
                            'counts': {
                                # 'by_statuses': {},
                                'free': 32,
                                'free_chain': 33,
                                'total': 34,
                                'pins': 36,
                                'radius': 37,
                            },
                            'smooth': {
                                'point_a': {'value': 45, 'is_default': False},
                                'point_b': {'value': 55, 'is_default': False},
                            },
                        },
                        'surge': {
                            'value': 38,
                            'surcharge': {
                                'alpha': 42,
                                'beta': 43,
                                'value': 44,
                            },
                        },
                        'value_raw': 39,
                    },
                ],
                1552003200000,
            ),
        ],
        [
            'rpush',
            '1552003200',
            common.build_pin(
                [],
                'test_offer_id',
                'test_order_id',
                'test_phone_id3',
                0.123,
                0.456,
                12.7,
                45.8,
                'test_user_id3',
                'default',
                [],
                1552003200000,
                use_point_a=True,
            ),
        ],
        [
            'rpush',
            '1552003200',
            common.build_pin(
                [],
                'test_offer_id',
                'test_order_id',
                'test_phone_id4',
                0.123,
                0.456,
                12.7,
                45.8,
                'test_user_id4',
                'alternative',
                [],
                1552003200000,
                use_point_a=True,
            ),
        ],
        ['rpush', 'test_key3', 'invalid'],
    )


# +5 min after pins' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@redis_store()
@pytest.mark.config(
    PIN_STORAGE_DUPLICATE={'coefficient': 0, 'ttl': 0},
    PIN_STORAGE_DYNAMIC_MAX_RADIUS=100,
)
@pytest.mark.parametrize(
    ['req_params', 'pins_cnt', 'prev_pins_override', 'reduce_expected'],
    [
        pytest.param(
            {'point': '0,0', 'radius': 60000, 'user_layer': 'default'},
            2,
            None,
            True,
            id='some match',
        ),
        pytest.param(
            {'point': '0,0', 'radius': 3200000, 'user_layer': 'default'},
            4,
            None,
            False,
            id='all default match',
        ),
        pytest.param(
            {'point': '0,0', 'radius': 3200000},
            5,
            None,
            False,
            id='all match',
        ),
        pytest.param(
            {'point': '0,0', 'radius': 3200000, 'user_layer': 'alternative'},
            1,
            None,
            True,
            id='all alternative match',
        ),
        pytest.param(
            {
                'point': '0,0',
                'radius': 3200000,
                'categories': 'econom',
                'user_layer': 'default',
            },
            4,
            356.65294924554183,
            False,
            id='filtered categories',
        ),
    ],
)
async def test_basic(
        taxi_pin_storage,
        req_params,
        pins_cnt,
        prev_pins_override,
        reduce_expected,
):
    expected = {
        'pins': pins_cnt,
        'pins_with_b': pins_cnt,
        'pins_with_order': pins_cnt,
        'pins_with_driver': 0,
        'prev_pins': 309.80930880830783,
        'values_by_category': {
            'econom': {
                'estimated_waiting': 25,
                'surge': 28,
                'surge_b': 22,
                'cost': 21,
                'trip': {'distance': 12.3, 'time': 45.6},
                'pins_order_in_tariff': 1,
                'pins_driver_in_tariff': 0,
            },
            'vip': {
                'estimated_waiting': 35,
                'surge': 38,
                'surge_b': 55,
                'cost': 31,
                'trip': {'distance': 12.3, 'time': 45.6},
                'pins_order_in_tariff': 0,
                'pins_driver_in_tariff': 0,
            },
        },
        'global_pins': 5,
        'global_pins_with_order': 5,
        'global_pins_with_driver': 0,
    }
    if prev_pins_override is not None:
        expected['prev_pins'] = prev_pins_override
    if 'categories' in req_params:
        for category in list(expected['values_by_category'].keys()):
            if category not in req_params['categories']:
                del expected['values_by_category'][category]

    if reduce_expected:
        expected['prev_pins'] = 0.0
        expected['values_by_category'] = {}

    response = await taxi_pin_storage.get(
        'v1/get_stats/radius', params=req_params,
    )
    assert response.status_code == 200
    data = response.json()
    stats = data['stats']
    assert stats == expected


@pytest.mark.now('2019-03-08T00:05:00Z')
@redis_store()
@pytest.mark.parametrize(
    'radius, limit, graph_distance, expected_point_ids, reversed_search',
    [
        (2500, 10, None, ['dea476', 'dea477', 'dea478', 'dea479'], False),
        (2, 10, 2500, ['dea476', 'dea477', 'dea478', 'dea479'], False),
        (200, 10, None, ['dea476', 'dea479'], False),
        (2500, 3, None, ['dea476', 'dea477', 'dea479'], False),
        (1000, 10, None, ['dea476', 'dea477', 'dea479'], True),
    ],
    ids=[
        'all_points',
        'separate_distance',
        'distance_limit',
        'count_limit',
        'reversed_search',
    ],
)
async def test_graph(
        taxi_pin_storage,
        taxi_config,
        radius,
        limit,
        graph_distance,
        expected_point_ids,
        reversed_search,
):
    taxi_config.set_values(
        dict(
            PIN_STORAGE_GRAPH_SETTINGS={
                'reversed_edges_mode': reversed_search,
            },
        ),
    )

    request_params = {
        'point': '37.642736,55.735422',
        'radius': radius,
        'user_layer': 'default',
        'graph_points': limit,
    }
    if graph_distance is not None:
        request_params['graph_distance'] = graph_distance

    response = await taxi_pin_storage.get(
        'v1/get_stats/radius', params=request_params,
    )
    assert response.status_code == 200
    data = response.json()
    fixed_points = data['stats'].get('graph_fixed_points')
    assert fixed_points is not None

    if reversed_search:
        dist = [902, 936, 1508, 828]
    else:
        dist = [176, 210, 2065, 102]

    expected_points = [
        pt
        for pt in [
            {'distance': dist[0], 'position_id': 'dea476'},
            {'distance': dist[1], 'position_id': 'dea477'},
            {'distance': dist[2], 'position_id': 'dea478'},
            {'distance': dist[3], 'position_id': 'dea479'},
        ]
        if pt['position_id'] in expected_point_ids
    ]
    actual_points = sorted(fixed_points, key=lambda t: t['position_id'])
    assert actual_points == expected_points


def redis_store_from_surge_values(values):
    args = []
    for idx, value in enumerate(values):
        args.append(
            [
                'rpush',
                '1552003200',
                common.build_pin(
                    [],
                    f'test_offer_id{idx}',
                    f'test_order_id{idx}',
                    f'test_phone_id{idx}',
                    20.125,
                    20.458,
                    12.9,
                    45.0,
                    f'test_user_id{idx}',
                    'default',
                    [
                        {
                            'name': 'econom',
                            'calculation_meta': {
                                'smooth': {
                                    'point_a': {
                                        'value': 1.0,
                                        'is_default': True,
                                    },
                                    'point_b': {
                                        'value': value,
                                        'is_default': False,
                                    },
                                },
                            },
                            'surge': {'value': 1.0},
                            'value_raw': 1.0,
                        },
                    ],
                    1552003200000,
                    use_point_a=True,
                ),
            ],
        )
    return pytest.mark.redis_store(*args)


@pytest.mark.now('2019-03-08T00:05:00Z')
@redis_store_from_surge_values([i / 10 for i in range(1, 101)])
async def test_point_b_percentiles(taxi_pin_storage):
    response = await taxi_pin_storage.get(
        'v1/get_stats/radius',
        params={
            'point': '0,0',
            'radius': 3200000,
            'high_surge_b': '1,10,30,50,70,95,98',
        },
    )

    assert response.status_code == 200
    data = response.json()
    stats = data['stats']

    expected = {
        'pins': 133,
        'pins_with_b': 133,
        'pins_with_order': 133,
        'pins_with_driver': 0,
        'prev_pins': 0.0,
        'values_by_category': {
            'econom': {
                'surge': 1.0,
                'surge_b': 5.05,
                'pins_order_in_tariff': 133,
                'pins_driver_in_tariff': 0,
                'pins_surge_b_percentiles': [
                    {'percentile': 1, 'value': 0.1},
                    {'percentile': 10, 'value': 1.0},
                    {'percentile': 30, 'value': 3.0},
                    {'percentile': 50, 'value': 5.0},
                    {'percentile': 70, 'value': 7.0},
                    {'percentile': 95, 'value': 9.5},
                    {'percentile': 98, 'value': 9.8},
                ],
            },
        },
        'global_pins': 100,
        'global_pins_with_order': 100,
        'global_pins_with_driver': 0,
    }
    stats['values_by_category']['econom']['pins_surge_b_percentiles'].sort(
        key=lambda t: t['percentile'],
    )
    del stats['values_by_category']['econom']['trip']
    assert stats == expected
