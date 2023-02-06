import pytest


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='candidates_reposition_intercity_settings',
    consumers=['candidates/user'],
    default_value={
        'preferred': {'econom': 1},
        'max_line_dist': 1000,
        'modes': ['test'],
    },
)
@pytest.mark.parametrize(
    'mode_name,destination_point,check_required,reposition',
    [
        ('test', [55.01, 35.01], True, True),
        ('test', [56.01, 35.01], True, False),
        ('test1', [55.01, 35.01], True, False),
        ('test', [55.01, 35.01], False, False),
    ],
)
async def test_basic(
        taxi_candidates,
        driver_positions,
        mock_reposition_index,
        mode_name,
        destination_point,
        check_required,
        reposition,
):
    mock_reposition_index.set_response(
        drivers=[
            {
                'driver_id': 'uuid0',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': check_required,
                'mode_name': mode_name,
                'destination_point': destination_point,
            },
        ],
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55.01, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55.01, 35]},
        ],
    )

    body = {
        'limit': 1,
        'zone_id': 'moscow',
        'point': [55, 35],
        'order': {
            'intercity': {'enabled': True},
            'request': {
                'source': {'geopoint': [55, 35]},
                'destinations': [{'geopoint': [55.01, 35.01]}],
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    if reposition:
        assert candidates[0]['uuid'] == 'uuid0'
    else:
        assert candidates[0]['uuid'] == 'uuid1'
