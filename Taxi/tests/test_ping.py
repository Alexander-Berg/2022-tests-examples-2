import json


def test_ping(taxi_pyml):
    response = taxi_pyml.get('ping')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {
        'status': 'ok'
    }
