import json

def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('client_tickets_read_only',
                             json={})
    assert response.status_code == 400


def test_ro_request(taxi_pyml, load_json):
    response = taxi_pyml.get('client_tickets_read_only',
                             json=load_json('ro_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('model_need_response')['prob_need_response'] < 0.05

def test_non_ro_request(taxi_pyml, load_json):
    response = taxi_pyml.get('client_tickets_read_only',
                             json=load_json('non_ro_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('model_need_response')['prob_need_response'] > 0.9
