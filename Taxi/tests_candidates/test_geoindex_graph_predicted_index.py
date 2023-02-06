import pytest


@pytest.mark.experiments3(
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
    name='use_predicted_driver_position',
    consumers=['candidates/user'],
    default_value={'enabled': True},
)
@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_use_graph(taxi_candidates, driver_positions):
    positions = [
        {
            'dbid_uuid': 'dbid0_uuid0',
            'positions': [
                {'position': [37.625344, 55.755430], 'shift': 0},
                {'position': [37.63, 55.76], 'shift': 10},
            ],
        },
    ]
    await driver_positions(positions)
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 0,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 1
    cand = candidates[0]
    # Check that shifted position was used
    assert cand['position'] == positions[0]['positions'][1]['position']
