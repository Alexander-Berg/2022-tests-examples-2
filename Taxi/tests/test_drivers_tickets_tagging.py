import json

import pytest

from pymlaas.util import request_helpers
from pymlaas.models.drivers_tickets_tagging import required_formats


def validate_response(response):
    request_helpers.validate_type(response, required_formats.RESPONSE)


# TODO: add the test back once TAXIBACKEND-21564 is completed.
@pytest.mark.skip(reason="should be fixed after completing TAXIBACKEND-21564")
def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('drivers_tickets_tagging',
                             json={})
    assert response.status_code == 400


def test_clear_spam(taxi_pyml, load_json):
    response = taxi_pyml.get('drivers_tickets_tagging',
                             json=load_json('clear_spam_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('spam_probability') > 0.85


def test_rude_not_spam(taxi_pyml, load_json):
    response = taxi_pyml.get('drivers_tickets_tagging',
                             json=load_json('rude_not_spam_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('spam_probability') < 0.2
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert data.get('most_likely_class_name') == 'dr_getting_requests'
    # Label 4 correpsonds to "driver is not getting order requests" label.
    assert class_num == 4
    assert tag_probabilities[class_num] > 0.5


def test_order_not_paid(taxi_pyml, load_json):
    response = taxi_pyml.get('drivers_tickets_tagging',
                             json=load_json('order_not_paid_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('spam_probability') < 0.05
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert (data.get('most_likely_class_name') ==
            'dr_fare_review_cash_trip_rider_error_not_payment')
    # Label 225 correpsonds to "client did not pay" label.
    assert class_num == 225
    assert tag_probabilities[class_num] > 0.85


def test_slot_unavailable(taxi_pyml, load_json):
    response = taxi_pyml.get('drivers_tickets_tagging',
                             json=load_json('slot_unavailable_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('spam_probability') < 0.05
    class_num = data.get('most_likely_class')
    tag_probabilities = data.get('tag_probabilities')
    assert tag_probabilities[class_num] == max(tag_probabilities)
    assert data.get('most_likely_class_name') == 'dr_slot_unavailable'
    # Label 45 correpsonds to "slot was unavailable" label.
    assert class_num == 45
    assert tag_probabilities[class_num] > 0.75
