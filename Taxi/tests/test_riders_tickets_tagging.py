import json

import pytest

from pymlaas.util import request_helpers
from pymlaas.models.riders_tickets_tagging import required_formats


def validate_response(response):
    request_helpers.validate_type(response, required_formats.RESPONSE)


# TODO: add the test back once TAXIBACKEND-21564 is completed.
@pytest.mark.skip(reason="should be fixed after completing TAXIBACKEND-21564")
def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('riders_tickets_tagging',
                             json={})
    assert response.status_code == 400


def test_rude(taxi_pyml, load_json):
    response = taxi_pyml.get('riders_tickets_tagging',
                             json=load_json('rude_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert (data.get('most_likely_class_name').split('.')[-1] ==
            'rd_feedback_quality_professionalism_rude_driver')
    # Label 142 correpsonds to "driver was rude" label.
    assert class_num == 142
    assert tag_probabilities[class_num] > 0.7


def test_smell(taxi_pyml, load_json):
    response = taxi_pyml.get('riders_tickets_tagging',
                             json=load_json('smell_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert (data.get('most_likely_class_name').split('.')[-1] ==
            'rd_feedback_quality_vehicle_condition_smell_car')
    # Label 155 correpsonds to "vehicle smelled" label.
    assert class_num == 155
    assert tag_probabilities[class_num] > 0.8
    

def test_stops(taxi_pyml, load_json):
    response = taxi_pyml.get('riders_tickets_tagging',
                             json=load_json('stops_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert (data.get('most_likely_class_name').split('.')[-1] ==
            'rd_feedback_quality_professionalism_personal_stops')
    # Label 139 correpsonds to "personal stops" label.
    assert class_num == 139
    assert tag_probabilities[class_num] > 0.2
    
    
def test_cancel(taxi_pyml, load_json):
    response = taxi_pyml.get('riders_tickets_tagging',
                             json=load_json('cancel_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert (data.get('most_likely_class_name').split('.')[-1] ==
            'rd_fare_cancel_driver_canceled')
    # Label 28 correpsonds to "driver canceled" label.
    assert class_num == 28
    assert tag_probabilities[class_num] > 0.7
