import json


from pymlaas.util import request_helpers
from pymlaas.protocol.handlers.eats import support_autoreply


LESS_THAN_10_MINUTES_SITUATION = 1
MORE_THAN_10_MINUTES_SITUATION = 2
TASTE_SITUATION = 9
FOREIGN_OBJECT_SITUATION = 20


def validate_response(response):
    request_helpers.validate_type(response,
                                  support_autoreply.REQUIRED_FIELDS_IN_REQUEST)


def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('eats_support_autoreply', json={})
    assert response.status_code == 400


def test_empty_message(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json('empty_message_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('situations') == list()


def test_empty_comments(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json('empty_comments_request.json'))
    assert response.status_code == 200


def test_less_than_10_minutes_lateness(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json(
                                 'less_than_10_minutes_lateness_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('situations') == [LESS_THAN_10_MINUTES_SITUATION]


def test_more_than_10_minutes_lateness(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json(
                                 'more_than_10_minutes_lateness_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('situations') == [MORE_THAN_10_MINUTES_SITUATION]


def test_incorrect_date_format(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json(
                                 'incorrect_date_format_request.json'))
    assert response.status_code == 400


def test_taste_message_and_comment(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json(
                                 'taste_message_and_comment_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('situations') == [TASTE_SITUATION]
    assert not data.get('urgent')


def test_different_date_formats(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json(
                                 'different_date_formats_request.json'))
    assert response.status_code == 400


def test_urgent_request(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json('urgent_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('situations') == [FOREIGN_OBJECT_SITUATION]
    assert data.get('urgent')


def test_not_for_autoreply_request(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json('not_for_autoreply_request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('situations') == []
    assert not data.get('urgent')


def test_several_predefined_comments_request(taxi_pyml, load_json):
    response = taxi_pyml.get('eats_support_autoreply',
                             json=load_json(
                                 'several_predefined_comments_request.json'))
    print response.status_code
    assert response.status_code == 200
