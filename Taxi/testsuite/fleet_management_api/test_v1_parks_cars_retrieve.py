import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/cars/retrieve'
ENDPOINT_URL = '/v1/parks/cars/retrieve'

OK_PARAMS = [
    (
        {
            'query': {'park': {'id': 'x', 'car': {'id': 'y'}}},
            'fields': {'car': utils.CAR_FIELDS},
        }
    ),
]

OK_RESPONSE = {'car': {'number': 'B001OP97'}}


@pytest.mark.parametrize('request_json', OK_PARAMS)
def test_ok(taxi_fleet_management_api, mockserver, request_json):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return OK_RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == OK_RESPONSE
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request == request_json


BAD_REQUEST_PARAMS = [
    ({}, 'query must be present'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
    ({'query': {'park': {'id': 'x'}}}, 'query.park.car must be present'),
    (
        {'query': {'park': {'id': 'x', 'car': {}}}},
        'query.park.car.id must be present',
    ),
    (
        {'query': {'park': {'id': 'x', 'car': {'id': ''}}}},
        'query.park.car.id must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'x', 'car': {'id': 'y'}}}},
        'fields must be present',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'car': {'id': 'y'}}},
            'fields': {'car': ['a', 'number', 'c', 'number']},
        },
        'fields.car must contain unique strings (error at `number`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'car': {'id': 'y'}}},
            'fields': {'car': []},
        },
        'fields must contain at least one field',
    ),
]


@pytest.mark.parametrize('request_json,error_text', BAD_REQUEST_PARAMS)
def test_bad_request(taxi_fleet_management_api, request_json, error_text):
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)


@pytest.mark.parametrize(
    'status_code,response_text,expected_response',
    [
        (
            400,
            json.dumps({'error': {'text': 'invalid'}}),
            utils.format_error('invalid'),
        ),
        (403, 'something', utils.UNKNOWN_ERROR),
        (500, 'unknown', utils.INTERNAL_ERROR),
    ],
)
def test_parks_not_ok(
        taxi_fleet_management_api,
        mockserver,
        status_code,
        response_text,
        expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(response_text, status_code)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps(
            {
                'query': {'park': {'id': 'x', 'car': {'id': 'y'}}},
                'fields': {'car': ['id']},
            },
        ),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == status_code
    assert response.json() == expected_response
