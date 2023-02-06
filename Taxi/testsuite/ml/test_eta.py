from __future__ import print_function

import pytest


def check_values(request, response):
    assert len(response.json()['pin']) == len(request['eta_formula'])
    assert len(response.json()['alt_pins']) == len(request['alt_pins'])

    request_pins = set(pin['class'] for pin in request['eta_formula'])
    response_pins = set(pin['class'] for pin in response.json()['pin'])
    assert len(request_pins.intersection(response_pins)) == len(
        request_pins.union(response_pins),
    )

    assert all(abs(pin['value']) <= 20 * 60 for pin in response.json()['pin'])


@pytest.mark.parametrize('model_version', ['eta_v1', 'eta_v2', 'eta_v3'])
def test_ml_eta_bulk_ok_without_candidates(taxi_ml, load_json, model_version):
    request = load_json('request_without_candidates.json')
    request['experiments'] = [model_version]
    response = taxi_ml.post('eta', json=request)
    assert response.status_code == 200
    check_values(request, response)


@pytest.mark.parametrize('model_version', ['eta_v1', 'eta_v2', 'eta_v3'])
def test_ml_eta_bulk_ok_with_candidates(taxi_ml, load_json, model_version):
    request = load_json('request_with_candidates.json')
    request['experiments'] = [model_version]
    response = taxi_ml.post('eta', json=request)
    assert response.status_code == 200
    check_values(request, response)


@pytest.mark.parametrize('model_version', ['eta_v1', 'eta_v2', 'eta_v3'])
def test_ml_eta_bulk_bad(taxi_ml, load_json, model_version):
    request = load_json('request_bad.json')
    request['experiments'] = [model_version]
    response = taxi_ml.post('eta', json=request)
    assert response.status_code == 400
    assert response.json()['error']['text'] == 'no geopoint'


def test_ml_eta_empty_request(taxi_ml, load_json):
    response = taxi_ml.post('eta_bulk', json={})
    assert response.status_code == 400
    assert any(response.json()['error']['text'])
