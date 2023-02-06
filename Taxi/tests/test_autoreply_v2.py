def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('autoreply/v2',
                             json={})
    assert response.status_code == 400

def test_no_user_id(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply/v2',
                             json=load_json('no_user_id.json'))
    assert response.status_code == 400

def test_refund(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply/v2',
                             json=load_json('refund_request.json'))
    assert response.status_code == 200

def test_promo(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply/v2',
                             json=load_json('promo_request.json'))
    assert response.status_code == 200

def test_non_autoreply(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply/v2',
                             json=load_json('non_autoreply_request.json'))
    assert response.status_code == 200

def test_unicode(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply/v2',
                             json=load_json('unicode_request.json'))
    assert response.status_code == 200
