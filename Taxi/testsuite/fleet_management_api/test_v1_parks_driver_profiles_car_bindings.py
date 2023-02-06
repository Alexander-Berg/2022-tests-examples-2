import json

import pytest

from . import auth
from . import utils


MOCK_URL = '/parks/driver-profiles/car-bindings'
ENDPOINT_URL = '/v1/parks/driver-profiles/car-bindings'

PARAMS = {'park_id': 'park', 'driver_profile_id': 'driver', 'car_id': 'car'}
RESPONSE = {'some': 'response'}


@pytest.mark.parametrize('status', [200, 201])
def test_put_ok(taxi_fleet_management_api, mockserver, status):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(json.dumps(RESPONSE), status)

    response = taxi_fleet_management_api.put(
        ENDPOINT_URL, headers=auth.HEADERS, params=PARAMS,
    )

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'PUT'
    assert mock_request.args.to_dict() == PARAMS
    utils.check_headers(mock_request.headers, utils.X_REAL_IP_HEADERS)
    auth.check_user_ticket_headers(mock_request.headers)

    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE


def test_delete_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return RESPONSE

    response = taxi_fleet_management_api.delete(
        ENDPOINT_URL, headers=auth.HEADERS, params=PARAMS,
    )

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'DELETE'
    assert mock_request.args.to_dict() == PARAMS
    utils.check_headers(mock_request.headers, utils.X_REAL_IP_HEADERS)
    auth.check_user_ticket_headers(mock_request.headers)

    assert response.status_code == 200
    assert response.json() == RESPONSE


def test_unauthorized(taxi_fleet_management_api):
    headers = auth.HEADERS.copy()
    headers.pop(auth.USER_TICKET_HEADER)
    response = taxi_fleet_management_api.delete(
        ENDPOINT_URL, headers=headers, params=PARAMS,
    )
    assert response.status_code == 401
    assert response.json() == utils.UNAUTHORIZED_ERROR
