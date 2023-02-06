async def test_available(taxi_eda_candidates, courier_positions):
    await courier_positions(
        [
            {'id': '123', 'position': [37.625344, 55.755430]},
            {'id': '234', 'position': [37.625172, 55.756506]},
            {'id': '456', 'position': [37.625129, 55.757644]},
            {'id': '678', 'position': [37.625033, 55.761528]},
        ],
    )
    request_body = {
        'limit': 4,
        'point': [35, 55],
        'available_until': '2020-04-21T14:31:00+0300',
    }
    response = await taxi_eda_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['id'] == '456'

    request_body = {
        'limit': 4,
        'point': [35, 55],
        'available_until': '2020-04-21T14:30:00+0300',
    }
    response = await taxi_eda_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 2
    assert candidates[0]['id'] == '234'
    assert candidates[1]['id'] == '456'
