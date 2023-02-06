import pytest


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
)
@pytest.mark.experiments3(
    is_config=True,
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'tariff_zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='use_route_predicted_contractor_positions',
    consumers=['candidates/user'],
    default_value={'enabled': True},
)
async def test_basic(
        taxi_candidates, driver_positions_route_predicted, chain_busy_drivers,
):
    await driver_positions_route_predicted(
        [
            {
                'dbid_uuid': 'dbid0_uuid1',
                'positions': [
                    {'position': [37.624826, 55.755331], 'shift': 0},
                    {'position': [37.624826, 55.755331], 'shift': 10},
                    {'position': [37.625618, 55.752399], 'shift': 20},
                    {'position': [37.625120, 55.757644], 'shift': 30},
                    {'position': [37.625110, 55.757624], 'shift': 40},
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
    assert len(response.json()['candidates']) == 1
    candidate = response.json()['candidates'][0]
    assert candidate['position'] == [37.624826, 55.755331]
    assert candidate['position_info']['probable_positions'] == [
        {
            'position': [37.62512, 55.757644],
            'route_info': {'distance': 0, 'time': 0},
            'shift': 30,
        },
        {
            'position': [37.625618, 55.752399],
            'route_info': {'distance': 3330, 'time': 326},
            'shift': 20,
        },
    ]


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
)
@pytest.mark.experiments3(
    is_config=True,
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'tariff_zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='use_route_predicted_contractor_positions',
    consumers=['candidates/user'],
    default_value={'enabled': True, 'shift': 20},
)
async def test_shift_exp(
        taxi_candidates, driver_positions_route_predicted, chain_busy_drivers,
):
    await driver_positions_route_predicted(
        [
            {
                'dbid_uuid': 'dbid0_uuid1',
                'positions': [
                    {'position': [37.624826, 55.755331], 'shift': 0},
                    {'position': [37.624826, 55.755331], 'shift': 10},
                    {'position': [37.625618, 55.752399], 'shift': 20},
                    {'position': [37.625120, 55.757644], 'shift': 30},
                    {'position': [37.625110, 55.757624], 'shift': 40},
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
    assert len(response.json()['candidates']) == 1
    candidate = response.json()['candidates'][0]
    assert candidate['position'] == [37.625618, 55.752399]
    assert candidate['position_info']['probable_positions'] == [
        {
            'position': [37.62512, 55.757644],
            'route_info': {'distance': 0, 'time': 0},
            'shift': 30,
        },
        {
            'position': [37.625618, 55.752399],
            'route_info': {'distance': 3330, 'time': 326},
            'shift': 20,
        },
    ]


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True},
    CANDIDATES_FEATURE_SWITCHES={
        'skip_route_predicted_missing_position_on_edge': True,
    },
)
@pytest.mark.experiments3(
    is_config=True,
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'tariff_zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='use_route_predicted_contractor_positions',
    consumers=['candidates/user'],
    default_value={'enabled': True},
)
async def test_disable_attract_positions(
        taxi_candidates, driver_positions_route_predicted, chain_busy_drivers,
):
    await driver_positions_route_predicted(
        [
            {
                'dbid_uuid': 'dbid0_uuid1',
                'positions': [
                    {'position': [37.625135, 55.757644], 'shift': 0},
                    {'position': [37.625129, 55.757644], 'shift': 10},
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
    assert not response.json()['candidates']
