import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/cars/models/list'
ENDPOINT_URL = '/v1/parks/cars/models/list'

REQUEST = {'query': {'park': {'id': '228'}, 'brand': {'name': 'BMW'}}}

CAR_MODELS = {'models': [{'name': 'X6'}, {'name': 'i8'}, {'name': 'M5'}]}


def test_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return CAR_MODELS

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(REQUEST),
    )

    assert response.status_code == 200
    assert response.json() == CAR_MODELS

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == REQUEST


@pytest.mark.parametrize(
    'status_code,response_text,expected_response',
    [
        (
            404,
            json.dumps(utils.format_parks_error('brand not found')),
            utils.format_error('brand not found'),
        ),
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
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(REQUEST),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == status_code
    assert response.json() == expected_response
