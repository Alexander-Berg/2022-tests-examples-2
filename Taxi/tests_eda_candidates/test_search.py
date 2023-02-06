import pytest


@pytest.mark.parametrize(
    'request_body', [({}), ({'limit': 3}), ({'point': [55, 35]})],
)
async def test_bad_request(taxi_eda_candidates, request_body):
    response = await taxi_eda_candidates.post('search', json=request_body)
    assert response.status_code == 400


async def test_sample(taxi_eda_candidates, courier_positions):
    await courier_positions(
        [
            {'id': 'id1', 'position': [37.625344, 55.755430]},
            {'id': 'id2', 'position': [37.625172, 55.756506]},
            {'id': 'id3', 'position': [37.625129, 55.757644]},
            {'id': 'id4', 'position': [37.625033, 55.761528]},
        ],
    )
    request_body = {'limit': 3, 'point': [35, 55]}
    response = await taxi_eda_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 3
    assert candidates[0]['id'] == 'id1'
    assert candidates[1]['id'] == 'id2'
    assert candidates[2]['id'] == 'id3'
