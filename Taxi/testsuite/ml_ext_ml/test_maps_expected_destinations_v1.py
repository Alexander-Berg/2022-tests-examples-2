def validate_candidate(candidate):
    assert 'ml_score' in candidate
    assert 'id' in candidate


def test_ml_expected_destinations(taxi_ml, load_json):
    request = load_json('simple_request.json')
    response = taxi_ml.post('maps/expected_destinations/v1', json=request)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    validate_candidate(candidates[0])
