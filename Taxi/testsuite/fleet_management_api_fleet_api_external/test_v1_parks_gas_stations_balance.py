# encoding=utf-8
import json

import pytest

from fleet_management_api import utils
from . import auth


MOCK_URL = '/gas_stations/v1/parks/gas-stations/balance'
ENDPOINT_URL = '/v1/parks/gas-stations/balance'
PARK_ID = 'extra_super_park_id'

HEADERS = {**auth.HEADERS, 'X-Park-ID': PARK_ID}


def test_park_not_found(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        assert request.headers['X-Park-ID'] == PARK_ID
        error = utils.format_error('park not found', 'park_not_found')
        return mockserver.make_response(json.dumps(error), 404)

    response = taxi_fleet_api_external.get(ENDPOINT_URL, headers=HEADERS)

    assert mock_callback.has_calls
    assert response.status_code == 500


def test_offer_was_not_accepted(taxi_fleet_api_external, mockserver):
    error_response = utils.format_error(
        'offer was not accepted', 'offer_was_not_accepted',
    )

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        assert request.headers['X-Park-ID'] == PARK_ID
        return mockserver.make_response(json.dumps(error_response), 403)

    response = taxi_fleet_api_external.get(ENDPOINT_URL, headers=HEADERS)

    assert mock_callback.has_calls
    assert response.status_code == 403
    assert response.json() == error_response


@pytest.mark.parametrize(
    'expected_response',
    (
        {'balance': '1000.1', 'balance_limit': '20000'},
        {'balance': '300.25', 'balance_limit': '40000.1111'},
        {'balance': '40000.1111', 'balance_limit': '150.999'},
    ),
)
def test_ok(taxi_fleet_api_external, mockserver, expected_response):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        assert request.headers['X-Park-ID'] == PARK_ID
        return expected_response

    response = taxi_fleet_api_external.get(ENDPOINT_URL, headers=HEADERS)

    assert mock_callback.has_calls
    assert response.status_code == 200
    assert response.json() == expected_response
