import json


def mock_bigb(mockserver, ticket, return_value=None, status_code=200):
    @mockserver.json_handler('/bigb')
    def route_bigb(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        if status_code == 200:
            return return_value
        else:
            return mockserver.make_response(status=status_code)

    return route_bigb


def validate_candidates(candidates):
    assert candidates
    for c in candidates:
        assert 'ml_score' in c
        assert 'id' in c


def test_ml_expected_destinations(tvm2_client, taxi_ml, load_json, mockserver):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    mock_bigb(mockserver, 'ticket')
    request = load_json('request.json')
    response = taxi_ml.post('navi/expected_destinations/v2', json=request)
    assert response.status_code == 200
    validate_candidates(response.json()['candidates'])
