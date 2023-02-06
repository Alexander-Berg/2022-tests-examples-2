from __future__ import print_function


def test_ml_user_order_fakeness_ok(taxi_ml, load_json):
    request = load_json('request.json')
    response = taxi_ml.post('user_order_fakeness', json=request)
    assert response.status_code == 200
    assert 0.0 <= response.json()['fake_order_prob'] <= 1.0
    assert len(response.json()['fake_order_verdicts']) == 3
    assert all(
        verdict['verdict'] in ['not_fake', 'fake']
        and verdict['strictness'] in ['soft', 'normal', 'hard']
        for verdict in response.json()['fake_order_verdicts']
    )


def test_ml_user_order_fakeness_empty_request(taxi_ml, load_json):
    response = taxi_ml.post('user_order_fakeness', json={})
    assert response.status_code == 400
    assert any(response.json()['error']['text'])
