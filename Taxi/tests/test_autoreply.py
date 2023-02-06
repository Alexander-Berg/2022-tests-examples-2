import json

# Classes for promocodes.
PROMO_SPEC_CLASSES = [
    '11781',  # promo50rub
    '11782',  # promo100rub
    '11783',  # promo200rub
    '11784',  # promo300rub
    '11785',  # promo400rub
    '11786',  # promo500rub
]
# Class for main promo
PROMO_CLASS = 11783
# Class for details request
DETAILS_CLASS = 11793
# Class for refund
REFUND_CLASS = 11789


def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('autoreply',
                             json={})
    assert response.status_code == 400

def test_no_user_id(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply',
                             json=load_json('no_user_id.json'))
    assert response.status_code == 400

def test_refund(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply',
                             json=load_json('refund_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('class_true') == REFUND_CLASS
    assert data.get('probs')[str(REFUND_CLASS)] > 0.3

def test_promo(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply',
                             json=load_json('promo_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('class_true') == PROMO_CLASS
    assert sum([data.get('probs')[num_prom] for
               num_prom in PROMO_SPEC_CLASSES]) > 0.6


def test_non_autoreply(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply',
                             json=load_json('non_autoreply_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('reason') == 'non_autoreplyable_predicted_class'

def test_details(taxi_pyml, load_json):
    response = taxi_pyml.get('autoreply',
                             json=load_json('details_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('class_true') == DETAILS_CLASS
    assert data.get('probs')[str(DETAILS_CLASS)] > 0.3
