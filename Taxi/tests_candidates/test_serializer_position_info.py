import pytest


@pytest.mark.now('2021-01-01T13:37:00+00:00')
@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
)
async def test_serializer(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.680517, 55.787963]}],
    )
    request_body = {
        'zone_id': 'moscow',
        'point': [37.680517, 55.787963],
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 1,
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert candidates[0]['position_info'] == {
        'timestamp': '2021-01-01T13:37:00+00:00',
    }
