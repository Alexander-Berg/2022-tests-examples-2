import pytest


@pytest.mark.parametrize(
    'request_body,response_code', [({}, 400), ({'ids': ['id1', 'id2']}, 200)],
)
async def test_response_codes(
        taxi_eda_candidates, request_body, response_code,
):
    response = await taxi_eda_candidates.post('list-by-ids', json=request_body)
    assert response.status_code == response_code


async def test_sample(taxi_eda_candidates, courier_positions):
    await courier_positions(
        [
            {'id': 'id1', 'position': [55, 35]},
            {'id': 'id2', 'position': [56, 36]},
        ],
    )
    request_body = {'ids': ['id1', 'id2', 'id3']}
    response = await taxi_eda_candidates.post('list-by-ids', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 2
    ids = [x['id'] for x in candidates]
    assert 'id3' not in ids
