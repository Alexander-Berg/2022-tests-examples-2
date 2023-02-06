import pytest

import tests_candidates.helpers


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.mark.parametrize(
    'request_override,fallback_time_threshold_sec,expected_candidates',
    [
        (
            {
                'order': {
                    'calc': {'alternative_type': 'perfect_chain'},
                    # 2022-06-02T17:06:35.9+0000
                    'created': 1654189595.9,
                },
            },
            30,
            [{'dbid': 'dbid0', 'uuid': 'uuid2'}],
        ),
        (
            {
                'order': {
                    'calc': {'alternative_type': 'perfect_chain'},
                    # 2022-06-02T16:49:55.9+0000
                    'created': 1654188595.9,
                },
            },
            30,
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        ),
        (
            {
                'order': {
                    'calc': {'alternative_type': 'non_perfect_chain'},
                    'created': 1654189595.9,
                },
            },
            30,
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        ),
        (
            {'order': {'created': 1654189595.9}},
            30,
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        ),
        (
            {},
            30,
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        ),
        (
            {
                'order': {
                    'calc': {'alternative_type': 'perfect_chain'},
                    'created': 1654189595.9,
                },
                'alt_offer_discount': {'is_long_search': True},
            },
            30,
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        ),
    ],
)
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
@pytest.mark.now('2022-06-02T17:07:05+00:00')
async def test_filter_perfect_chain(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        experiments3,
        request_override,
        fallback_time_threshold_sec,
        expected_candidates,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='perfect_chain_filter_settings',
        consumers=['candidates/user'],
        clauses=[
            {
                'title': 'order_age',
                'value': {'enabled': False},
                'enabled': True,
                'predicate': {
                    'init': {
                        'value': fallback_time_threshold_sec,
                        'arg_name': 'order_age_seconds',
                        'arg_type': 'int',
                    },
                    'type': 'gt',
                },
            },
        ],
        default_value={'enabled': True},
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625887, 55.755396]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625887, 55.755396]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.624826, 55.755333]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 20,
                'left_distance': 200,
                'destination': [37.625889, 55.755399],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    request_body = {
        'limit': 10,
        'filters': ['efficiency/perfect_chain'],
        'point': [37.625884, 55.755392],
        'zone_id': 'moscow',
    }
    request_body.update(request_override)
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected={'candidates': expected_candidates},
    )
    assert actual == expected
