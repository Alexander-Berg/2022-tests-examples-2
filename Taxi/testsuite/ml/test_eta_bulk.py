from __future__ import print_function

import pytest


def check_values(request, response):
    assert len(response.json()['pins']) == len(request['pins'])
    request_pins = set(pin['id'] for pin in request['pins'])
    assert all(pin['id'] in request_pins for pin in response.json()['pins'])
    assert all(
        eta['show_value'] >= 0 and eta['show_value'] <= 20 * 60
        for pin in response.json()['pins']
        for eta in pin['eta']
    )


@pytest.mark.parametrize('model_version', ['eta_v1', 'eta_v2', 'eta_v3'])
def test_ml_eta_bulk_ok_without_candidates(taxi_ml, load_json, model_version):
    request = load_json('request_without_candidates.json')
    request['experiments'] = [model_version]
    response = taxi_ml.post('eta_bulk', json=request)
    assert response.status_code == 200
    check_values(request, response)


@pytest.mark.parametrize('model_version', ['eta_v1', 'eta_v2', 'eta_v3'])
def test_ml_eta_bulk_ok_with_candidates(taxi_ml, load_json, model_version):
    request = load_json('request_with_candidates.json')
    request['experiments'] = [model_version]
    response = taxi_ml.post('eta_bulk', json=request)
    assert response.status_code == 200
    check_values(request, response)


@pytest.mark.parametrize('model_version', ['eta_v1', 'eta_v2', 'eta_v3'])
def test_ml_eta_bulk_bad(taxi_ml, load_json, model_version):
    request = load_json('request_bad.json')
    request['experiments'] = [model_version]
    response = taxi_ml.post('eta_bulk', json=request)
    assert response.status_code == 400
    assert response.json()['error']['text'] == 'no geopoint'


def test_ml_eta_empty_request(taxi_ml, load_json):
    response = taxi_ml.post('eta_bulk', json={})
    assert response.status_code == 400
    assert any(response.json()['error']['text'])
