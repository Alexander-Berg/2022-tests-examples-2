import json
import uuid

import pytest

from fleet_management_api import utils
from fleet_management_api.test_v1_parks_cars import CAR_CREATE_PARAMS
from fleet_management_api.test_v1_parks_cars import CAR_MODIFY_PARAMS
from fleet_management_api.test_v1_parks_cars import ENDPOINT_URL
from fleet_management_api.test_v1_parks_cars import MOCK_URL
from . import auth


AUTH_HEADERS = {**auth.HEADERS, **utils.X_REAL_IP_HEADERS}
MOCK_AUTH_HEADERS = {
    'X-Fleet-API-Client-ID': auth.CLIENT_ID,
    'X-Fleet-API-Key-ID': str(auth.KEY_ID),
    **utils.X_REAL_IP_HEADERS,
}


@pytest.mark.parametrize(
    'query_params, mock_callback_count,'
    'parks_json_request, expected_code, expected_response',
    CAR_CREATE_PARAMS,
)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_car_create(
        taxi_fleet_api_external,
        mockserver,
        query_params,
        mock_callback_count,
        parks_json_request,
        expected_code,
        expected_response,
):
    idempotency_token = uuid.uuid1().hex

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(
            json.dumps(expected_response), expected_code,
        )

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL,
        headers={**AUTH_HEADERS, 'X-Idempotency-Token': idempotency_token},
        params=query_params,
        data=json.dumps(parks_json_request),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response

    assert mock_callback.times_called == mock_callback_count
    if mock_callback_count > 0:
        mock_request = mock_callback.next_call()['request']
        assert mock_request.method == 'POST'
        utils.check_headers(mock_request.headers, MOCK_AUTH_HEADERS)
        assert mock_request.headers['X-Idempotency-Token'] == idempotency_token
        mock_json_request = json.loads(mock_request.get_data())
        utils.check_categories_filter(mock_json_request)
        assert mock_json_request == parks_json_request


@pytest.mark.parametrize(
    'query_params, mock_callback_count,'
    'parks_json_request, expected_code, expected_response',
    CAR_MODIFY_PARAMS,
)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_car_modify(
        taxi_fleet_api_external,
        mockserver,
        query_params,
        mock_callback_count,
        parks_json_request,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(
            json.dumps(expected_response), expected_code,
        )

    response = taxi_fleet_api_external.put(
        ENDPOINT_URL,
        headers=AUTH_HEADERS,
        params=query_params,
        data=json.dumps(parks_json_request),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response

    assert mock_callback.times_called == mock_callback_count
    if mock_callback_count > 0:
        mock_request = mock_callback.next_call()['request']
        assert mock_request.method == 'PUT'
        utils.check_headers(mock_request.headers, MOCK_AUTH_HEADERS)
        mock_json_request = json.loads(mock_request.get_data())
        utils.check_categories_filter(mock_json_request)
        assert mock_json_request == parks_json_request
