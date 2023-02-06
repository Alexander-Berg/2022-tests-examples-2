import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [({}, 400), ({'tl': [37.62, 55.75], 'br': [37.62, 55.75]}, 200)],
)
async def test_response_code(
        taxi_candidates, request_body, response_code, driver_status_request,
):
    response = await taxi_candidates.post('count', json=request_body)
    assert response.status_code == response_code


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_response_format(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.680517, 55.787963]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.559667, 55.685688]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.559667, 55.685688]},
        ],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 100,
                'left_distance': 1000,
                'destination': [37.627852, 55.753021],
                'approximate': False,
            },
        ],
    )
    request_body = {
        'tl': [37.308020, 55.903174],
        'br': [37.921881, 55.565338],
        'allowed_classes': ['econom', 'vip'],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('count', json=request_body)
    assert response.status_code == 200
    assert 'total' in response.json()
    assert 'on_order' in response.json()
    assert 'free' in response.json()
    assert 'free_chain' in response.json()
    assert response.json()['total'] == 3
    assert response.json()['on_order'] == 1
    assert response.json()['free'] == 2
    assert response.json()['free_chain'] == 1
