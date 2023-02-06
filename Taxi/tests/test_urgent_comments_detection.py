# coding=utf-8
import json

import pytest

from pymlaas.util import request_helpers
from pymlaas.models.urgent_comments_detection import required_formats

# TODO: Add international tests with mockserver.

def validate_response(response):
    request_helpers.validate_type(response, required_formats.RESPONSE)


def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('urgent_comments_detection',
                             json={})
    assert response.status_code == 400


def test_urgent(taxi_pyml, load_json):
    response = taxi_pyml.get('urgent_comments_detection',
                             json=load_json('urgent_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('urgency_probability') > 0.8


def test_unicode_urgent(taxi_pyml, load_json):
    response = taxi_pyml.get('urgent_comments_detection',
                             json=load_json('unicode_urgent_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('urgency_probability') > 0.7


def test_not_urgent(taxi_pyml, load_json):
    response = taxi_pyml.get('urgent_comments_detection',
                             json=load_json('not_urgent_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_response(data)
    assert data.get('urgency_probability') < 0.15
