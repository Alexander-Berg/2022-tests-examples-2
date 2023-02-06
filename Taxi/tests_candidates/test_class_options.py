import pytest


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
)
async def test_class_strong_mode(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625618, 55.752399]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.624826, 55.755331]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.624826, 55.755331]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 0,
                'left_distance': 0,
                'destination': [37.625618, 55.752399],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    body = {
        'zone_id': 'moscow',
        'point': [37.625618, 55.752399],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'vip'],
        'limit': 3,
        'order': {'request': {'class_options': {'strong_mode': False}}},
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 3

    body['order']['request']['class_options']['strong_mode'] = True
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    assert len(response.json()['candidates']) == 2
