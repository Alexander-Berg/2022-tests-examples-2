# pylint: disable=import-only-modules
import datetime

import pytest

from tests_reposition_matcher.utils import select_named


# TODO(sandyre): good solution for wait_until in testsuite
@pytest.mark.now('2050-12-01T00:00:00')
@pytest.mark.config(
    ROUTER_YAMAPS_TVM_QUOTAS_MAPPING={'reposition-matcher': 'reposition'},
)
@pytest.mark.pgsql(
    'reposition_matcher',
    files=['main/config.sql', 'main/data.sql', 'main/verdicts.sql'],
)
@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
@pytest.mark.parametrize('use_matrix', [False, True])
@pytest.mark.parametrize('is_fallback', [False, True])
@pytest.mark.parametrize('verdicts_cache', ['ro', 'wo', 'rw'])
async def test_main(
        match_orders_drivers,
        reposition_share_cache,
        taxi_config,
        pgsql,
        testpoint,
        mock_reposition_api_bulk_state,
        mock_router_regular,
        mock_router_matrix,
        load_json,
        use_matrix,
        is_fallback,
        now,
        verdicts_cache,
):
    @testpoint('handler::store_verdicts_end')
    def store_verdicts_end(data):
        pass

    taxi_config.set_values(
        {
            'REPOSITION_MATCHER_ROUTER_REQUEST_PARAMS': {
                '__default__': {
                    'max_rps': 0,
                    'wait_until': 0,
                    'enable_matrix': use_matrix,
                    'matrix_max_rps': 0,
                    'matrix_wait_until': 0,
                },
            },
            'REPOSITION_MATCHER_BULK_STATE_REQUEST_PARAMS': {
                '__default__': {'timeout-ms': 400, 'attempts': 1},
            },
            'REPOSITION_MATCHER_VERDICTS_CACHE_PARAMS': {
                '__default__': {
                    'store_verdict': 'w' in verdicts_cache,
                    'use_verdict': 'r' in verdicts_cache,
                    'verdict_ttl_s': 60,
                },
            },
        },
    )

    router_data = {
        # regular
        60.00: {'time': 1200, 'distance': 4200},
        60.10: {'time': 150, 'distance': 500},
        # regular offer
        60.20: {'time': 1200, 'distance': 4200},
        60.30: {'time': 150, 'distance': 500},
        # surge
        60.40: {'time': 1200, 'distance': 4200},
        60.50: {'time': 150, 'distance': 300},
        # area
        60.60: {'time': 300, 'distance': 1000},
        60.70: {'time': 300, 'distance': 1000},
        # destination district
        60.80: {'time': 1200, 'distance': 2000},
        60.90: {'time': 3600, 'distance': 60000},
    }

    mock_router_regular.set_data(router_data)
    mock_router_matrix.set_data(router_data)
    mock_reposition_api_bulk_state.set_data(
        load_json('main/bulk_state_response.json'),
    )

    if is_fallback:
        zones = ['moscow', 'spb']
        share = {'econom': 80, 'comfort': 70}
        fallbacks = {
            '__default__': {
                '__default__': {'threshold': 50},
                '__total__': {'threshold': 75},
            },
            'spb': {'__default__': {'threshold': 75}},
            'moscow': {'__default__': {'threshold': 75}},
        }

        await reposition_share_cache.update(zones, share, fallbacks)

    request = load_json('main/request.json')

    actual = await match_orders_drivers(request)
    expected = load_json('main/response.json')

    if is_fallback:
        expected = load_json('main/response_fallback.json')

    assert actual == expected

    await store_verdicts_end.wait_call()

    rows = select_named(
        """
        SELECT order_id, session_id, formula_id, suitable, score, valid_until
        FROM state.verdicts ORDER BY verdict_id
        """,
        pgsql['reposition_matcher'],
    )

    def sorted_rows(rows):
        return sorted(rows, key=lambda x: x['order_id'])

    if 'w' in verdicts_cache:
        if not is_fallback:
            assert sorted_rows(rows) == sorted_rows(
                [
                    {
                        'formula_id': 'destination_district_mode_1',
                        'order_id': 'any_9',
                        'session_id': '8DKgl9avmeG1vzAp',
                        'suitable': False,
                        'score': None,
                        'valid_until': now,
                    },
                    {
                        'formula_id': 'area_mode_1',
                        'order_id': 'any_7',
                        'session_id': 'M7Vl4zbq2dprOZqE',
                        'suitable': False,
                        'score': None,
                        'valid_until': now + datetime.timedelta(seconds=60),
                    },
                    {
                        'formula_id': 'surge_mode_1',
                        'order_id': 'any_5',
                        'session_id': 'QABWJxbojagwOL0E',
                        'suitable': False,
                        'score': None,
                        'valid_until': now + datetime.timedelta(seconds=60),
                    },
                    {
                        'formula_id': 'regular_mode_1',
                        'order_id': 'any_1',
                        'session_id': 'O3GWpmbk5ezJn4KR',
                        'suitable': False,
                        'score': None,
                        'valid_until': now + datetime.timedelta(seconds=60),
                    },
                    {
                        'formula_id': 'regular_offer_mode_1',
                        'order_id': 'any_3',
                        'session_id': 'rm0wMvbmOeYAlO1n',
                        'suitable': False,
                        'score': None,
                        'valid_until': now + datetime.timedelta(seconds=60),
                    },
                ],
            )
        else:
            assert sorted_rows(rows) == sorted_rows(
                [
                    {
                        'formula_id': 'destination_district_mode_1',
                        'order_id': 'any_9',
                        'session_id': '8DKgl9avmeG1vzAp',
                        'suitable': False,
                        'score': None,
                        'valid_until': now,
                    },
                    {
                        'formula_id': 'area_mode_1',
                        'order_id': 'any_7',
                        'session_id': 'M7Vl4zbq2dprOZqE',
                        'suitable': False,
                        'score': None,
                        'valid_until': now + datetime.timedelta(seconds=60),
                    },
                ],
            )
    elif verdicts_cache == 'ro':
        assert rows == [
            {
                'formula_id': 'destination_district_mode_1',
                'order_id': 'any_9',
                'session_id': '8DKgl9avmeG1vzAp',
                'suitable': False,
                'score': None,
                'valid_until': now,
            },
        ]


# TODO(sandyre): good solution for wait_until in testsuite
@pytest.mark.now('2050-12-01T00:00:00')
@pytest.mark.pgsql(
    'reposition_matcher', files=['main/config.sql', 'main/data.sql'],
)
@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
@pytest.mark.parametrize('formulas_overrides', [False, True])
async def test_main_formulas_overrides(
        match_orders_drivers,
        mock_reposition_api_bulk_state,
        mock_router_regular,
        mock_router_matrix,
        load_json,
        experiments3,
        formulas_overrides,
):
    if formulas_overrides:
        experiments3.add_experiment(
            consumers=['reposition-matcher/formulas-overrides'],
            name='reposition_matcher_formulas_overrides',
            match={
                'enabled': True,
                'consumers': [
                    {'name': 'reposition-matcher/formulas-overrides'},
                ],
                'predicate': {'type': 'true', 'init': {}},
            },
            clauses=[
                {
                    'title': 'dbid0_uuid0',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'arg_name': 'driver_id',
                            'arg_type': 'string',
                            'value': 'dbid0_uuid0',
                        },
                    },
                    'value': {
                        'regular': {'score_calculation': {'alpha': 0.5}},
                    },
                },
                {
                    'title': 'dbid1_uuid1',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'arg_name': 'driver_id',
                            'arg_type': 'string',
                            'value': 'dbid1_uuid1',
                        },
                    },
                    'value': {
                        'regular': {
                            'home_distance_ratio': 3.0,
                            'home_time_ratio': 3.0,
                            'min_home_distance_ratio': -1.0,
                            'min_home_time_ratio': -1.0,
                            'min_order_distance': 200,
                            'min_order_time': 100,
                            'new_calculation_method': {
                                'a': 2.0,
                                'b': 600.0,
                                'c': 1.0,
                                'd': 0.0,
                                'max_coef': 3.0,
                            },
                            'score_calculation': {'alpha': 0.5},
                        },
                        'regular_offer': {
                            'home_distance_ratio': 3.0,
                            'home_time_ratio': 3.0,
                            'min_home_distance_ratio': -1.0,
                            'min_home_time_ratio': -1.0,
                            'min_order_distance': 200,
                            'min_order_time': 100,
                        },
                        'surge': {'min_b_surge': 2.0},
                        'destination_district': {
                            'max_bh_air_dist': 1001,
                            'max_bh_time': 1001,
                        },
                    },
                },
                {
                    'title': 'dbid2_uuid2',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'arg_name': 'driver_id',
                            'arg_type': 'string',
                            'value': 'dbid2_uuid2',
                        },
                    },
                    'value': {
                        'regular': {
                            'home_distance_ratio': 3.0,
                            'home_time_ratio': 3.0,
                            'min_home_distance_ratio': -1.0,
                            'min_home_time_ratio': -1.0,
                            'min_order_distance': 200,
                            'min_order_time': 100,
                        },
                        'regular_offer': {
                            'home_distance_ratio': 3.0,
                            'home_time_ratio': 3.0,
                            'min_home_distance_ratio': -1.0,
                            'min_home_time_ratio': -1.0,
                            'min_order_distance': 200,
                            'min_order_time': 100,
                            'new_calculation_method': {
                                'a': 1.0,
                                'b': 0.0,
                                'c': 1.0,
                                'd': 0.0,
                                'max_coef': 3.0,
                            },
                        },
                        'surge': {'min_b_surge': 2.0},
                        'destination_district': {
                            'max_bh_air_dist': 1001,
                            'max_bh_time': 1001,
                        },
                    },
                },
                {
                    'title': 'rest',
                    'predicate': {'type': 'true', 'init': {}},
                    'value': {
                        'regular': {
                            'home_distance_ratio': 3.0,
                            'home_time_ratio': 3.0,
                            'min_home_distance_ratio': -1.0,
                            'min_home_time_ratio': -1.0,
                            'min_order_distance': 200,
                            'min_order_time': 100,
                        },
                        'regular_offer': {
                            'home_distance_ratio': 3.0,
                            'home_time_ratio': 3.0,
                            'min_home_distance_ratio': -1.0,
                            'min_home_time_ratio': -1.0,
                            'min_order_distance': 200,
                            'min_order_time': 100,
                        },
                        'surge': {'min_b_surge': 2.0},
                        'destination_district': {
                            'max_bh_air_dist': 1001,
                            'max_bh_time': 1001,
                        },
                    },
                },
            ],
        )

    router_data = {
        # regular
        60.00: {'time': 1200, 'distance': 4200},
        60.10: {'time': 150, 'distance': 500},
        # regular offer
        60.20: {'time': 1200, 'distance': 4200},
        60.30: {'time': 150, 'distance': 500},
        # surge
        60.40: {'time': 1200, 'distance': 4200},
        60.50: {'time': 150, 'distance': 300},
        # area
        60.60: {'time': 300, 'distance': 1000},
        60.70: {'time': 300, 'distance': 1000},
        # destination district
        60.80: {'time': 1200, 'distance': 2000},
        60.90: {'time': 3600, 'distance': 60000},
    }

    mock_router_regular.set_data(router_data)
    mock_router_matrix.set_data(router_data)
    mock_reposition_api_bulk_state.set_data(
        load_json('main/bulk_state_formulas_overrides_response.json'),
    )

    request = load_json('main/request.json')

    actual = await match_orders_drivers(request)
    expected = load_json('main/response.json')

    if formulas_overrides:
        expected = load_json('main/response_formulas_overrides.json')

    assert actual == expected


@pytest.mark.config(
    ROUTER_YAMAPS_TVM_QUOTAS_MAPPING={'reposition-matcher': 'reposition'},
)
@pytest.mark.pgsql(
    'reposition_matcher', files=['bonus/config.sql', 'bonus/data.sql'],
)
@pytest.mark.parametrize('active', [False, True])
@pytest.mark.parametrize('use_matrix', [False, True])
async def test_bonus(
        match_orders_drivers,
        taxi_config,
        mock_reposition_api_bulk_state,
        mock_router_regular,
        mock_router_matrix,
        load_json,
        active,
        use_matrix,
):
    taxi_config.set_values(
        {
            'REPOSITION_MATCHER_ROUTER_REQUEST_PARAMS': {
                '__default__': {
                    'max_rps': 0,
                    'wait_until': 10000,
                    'enable_matrix': use_matrix,
                    'matrix_max_rps': 0,
                    'matrix_wait_until': 10000,
                },
            },
        },
    )

    router_data = {
        # surge
        60.40: {'time': 200, 'distance': 1000},
        60.50: {'time': 200, 'distance': 1000},
        # area
        60.60: {'time': 300, 'distance': 1000},
        60.70: {'time': 300, 'distance': 1000},
    }

    mock_router_regular.set_data(router_data)
    mock_router_matrix.set_data(router_data)

    bulk_state_response = load_json('bonus/bulk_state_response.json')
    bulk_state_response['states'][1]['active'] = active
    mock_reposition_api_bulk_state.set_data(bulk_state_response)

    request = load_json('bonus/request.json')

    actual = await match_orders_drivers(request)
    expected = load_json('bonus/response.json')

    assert actual == expected


@pytest.mark.config(
    ROUTER_YAMAPS_TVM_QUOTAS_MAPPING={'reposition-matcher': 'reposition'},
)
@pytest.mark.pgsql(
    'reposition_matcher', files=['submode/config.sql', 'submode/data.sql'],
)
@pytest.mark.parametrize('use_matrix', [False, True])
async def test_submode(
        match_orders_drivers,
        taxi_config,
        mock_reposition_api_bulk_state,
        mock_router_regular,
        mock_router_matrix,
        load_json,
        use_matrix,
):
    taxi_config.set_values(
        {
            'REPOSITION_MATCHER_ROUTER_REQUEST_PARAMS': {
                '__default__': {
                    'max_rps': 0,
                    'wait_until': 10000,
                    'enable_matrix': use_matrix,
                    'matrix_max_rps': 0,
                    'matrix_wait_until': 10000,
                },
            },
        },
    )

    router_data = {
        # regular
        60.00: {'time': 1200, 'distance': 4200},
        60.10: {'time': 1200, 'distance': 4200},
        60.20: {'time': 1200, 'distance': 4200},
        # area
        60.60: {'time': 300, 'distance': 1000},
        60.70: {'time': 300, 'distance': 1000},
    }

    mock_router_regular.set_data(router_data)
    mock_router_matrix.set_data(router_data)
    mock_reposition_api_bulk_state.set_data(
        load_json('submode/bulk_state_response.json'),
    )

    request = load_json('submode/request.json')

    actual = await match_orders_drivers(request)
    expected = load_json('submode/response.json')

    assert actual == expected


@pytest.mark.config(
    ROUTER_YAMAPS_TVM_QUOTAS_MAPPING={'reposition-matcher': 'reposition'},
)
@pytest.mark.pgsql(
    'reposition_matcher',
    files=['route_reuse/config.sql', 'route_reuse/data.sql'],
)
@pytest.mark.parametrize('active', [False, True])
@pytest.mark.parametrize('use_matrix', [False, True])
@pytest.mark.parametrize('reuse_da_route', [True, False])
async def test_route_reuse(
        match_orders_drivers,
        taxi_config,
        mock_reposition_api_bulk_state,
        mock_router_regular,
        mock_router_matrix,
        load_json,
        active,
        use_matrix,
        reuse_da_route,
):
    base_regular_router_calls = 17
    da_routes_count = 3
    base_matrix_router_calls = 6

    taxi_config.set_values(
        {
            'REPOSITION_MATCHER_ROUTER_REQUEST_PARAMS': {
                '__default__': {
                    'max_rps': 0,
                    'wait_until': 10000,
                    'enable_matrix': use_matrix,
                    'matrix_max_rps': 0,
                    'matrix_wait_until': 10000,
                    'reuse_da_route': reuse_da_route,
                },
            },
        },
    )

    router_data = {
        # regular
        60.00: {'time': 1200, 'distance': 4200},
        60.10: {'time': 1200, 'distance': 4200},
        60.20: {'time': 1200, 'distance': 4200},
        # area
        60.60: {'time': 300, 'distance': 1000},
        60.70: {'time': 300, 'distance': 1000},
    }

    mock_router_regular.set_data(router_data)
    mock_router_matrix.set_data(router_data)

    bulk_state_response = load_json('route_reuse/bulk_state_response.json')
    mock_reposition_api_bulk_state.set_data(bulk_state_response)

    request = load_json('route_reuse/request.json')

    actual = await match_orders_drivers(request)
    expected = load_json('route_reuse/response.json')

    assert actual == expected

    assert mock_router_regular.times_called() == (
        base_regular_router_calls
        - (base_matrix_router_calls if use_matrix else 0)
        - (da_routes_count if reuse_da_route else 0)
    )
    assert mock_router_matrix.times_called() == (
        base_matrix_router_calls if use_matrix else 0
    )
