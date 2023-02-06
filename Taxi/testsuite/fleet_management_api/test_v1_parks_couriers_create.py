import json

import pytest

from . import auth
from . import utils


ENDPOINT_URL = 'v1/parks/couriers/create'
MOCK_URL = '/cargo_misc/couriers/v1/create'
OK_REQUEST = {
    'park_id': 'abcd',
    'last_name': 'Тодуа',
    'first_name': 'Антон',
    'middle_name': 'Романович',
    'phone': '+79275557777',
    'work_rule_id': 'xyz',
    'birth_date': '1994-01-01T00:00:00+03:00',
}
OK_RESPONSE = {'driver_profile_id': '1234', 'car_id': '5678'}

BAD_REQUEST_PARAMS = [
    (123, 'json root must be an object'),
    ({}, 'park_id must be present'),
    ({'park_id': ''}, 'park_id must be a non-empty utf-8 string without BOM'),
]


@pytest.mark.parametrize('query,error_text', BAD_REQUEST_PARAMS)
def test_bad_request(taxi_fleet_management_api, mockserver, query, error_text):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(query),
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)
    assert mock_callback.times_called == 0


def test_ok(taxi_fleet_management_api, mockserver, load_json):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return OK_RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == OK_RESPONSE, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == OK_REQUEST


MOCK_ERROR_PARAMS = [
    (
        400,
        json.dumps({'code': '400', 'message': 'bad message'}),
        utils.format_error('bad message', '400'),
    ),
    (
        400,
        json.dumps({'code': 'some-code', 'message': 'bad message'}),
        utils.format_error('bad message', 'some-code'),
    ),
    (
        500,
        json.dumps({'code': '500', 'message': 'internal error'}),
        utils.INTERNAL_ERROR,
    ),
    (500, 'not a json', utils.INTERNAL_ERROR),
]


@pytest.mark.parametrize(
    'status_code,mock_response_data,response_json', MOCK_ERROR_PARAMS,
)
def test_mock_error(
        taxi_fleet_management_api,
        mockserver,
        load_json,
        status_code,
        mock_response_data,
        response_json,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(mock_response_data, status_code)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == status_code, response.text
    assert response.json() == response_json, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == OK_REQUEST
