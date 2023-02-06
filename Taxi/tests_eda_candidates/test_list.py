import pytest


@pytest.mark.parametrize(
    'request_body', [({}), ({'tl': [55, 35]}), ({'br': [55, 35]})],
)
async def test_bad_request(taxi_eda_candidates, request_body):
    response = await taxi_eda_candidates.post('list', json=request_body)
    assert response.status_code == 400


async def test_sample(taxi_eda_candidates, courier_positions):
    await courier_positions(
        [
            {'id': 'id1', 'position': [55, 35]},
            {'id': 'id2', 'position': [56, 36]},
            {'id': 'id3', 'position': [55, 35]},
            {'id': 'id4', 'position': [55, 35]},
        ],
    )
    request_body = {'tl': [54.5, 34.5], 'br': [55.5, 35.5]}
    response = await taxi_eda_candidates.post('list', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 3
    ids = [x['id'] for x in candidates]
    assert 'id2' not in ids


async def test_search_area(taxi_eda_candidates, courier_positions):
    await courier_positions(
        [
            {'id': 'id1', 'position': [37.721397, 55.804005]},
            {'id': 'id2', 'position': [37.6576996, 55.7147346]},
            {'id': 'id3', 'position': [38.099052, 55.964553]},
            {'id': 'id4', 'position': [37.485191, 55.608601]},
        ],
    )
    request_body = {
        'search_area': [
            [37.309394, 55.914744],
            [37.884803, 55.911659],
            [37.942481, 55.520175],
            [37.309394, 55.914744],
        ],
    }
    response = await taxi_eda_candidates.post('list', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 2
    ids = {x['id'] for x in candidates}
    assert ids == {'id1', 'id2'}
