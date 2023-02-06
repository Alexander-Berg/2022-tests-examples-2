def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('suggest_support',
                             json={})
    assert response.status_code == 400

def test_comment_request(taxi_pyml):
    response = taxi_pyml.get('suggest_support',
                             json={'comment': ''})
    assert response.status_code == 200
