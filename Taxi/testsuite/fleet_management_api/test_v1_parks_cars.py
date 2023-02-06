# coding=utf-8
import json
import uuid

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/cars'
ENDPOINT_URL = '/v1/parks/cars'

CAR_CREATE_PARAMS = [
    (
        {'park_id': '1488'},
        1,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        200,
        {'car_id': 'new_car_id'},
    ),
    (
        None,
        0,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        400,
        utils.format_error('parameter park_id must be set'),
    ),
    (
        {'park_id': '1488'},
        1,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        500,
        utils.INTERNAL_ERROR,
    ),
]


@pytest.mark.parametrize(
    'query_params,mock_callback_count,'
    'parks_json_request,expected_code,expected_response',
    CAR_CREATE_PARAMS,
)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_car_create(
        taxi_fleet_management_api,
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

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers={**auth.HEADERS, 'X-Idempotency-Token': idempotency_token},
        params=query_params,
        data=json.dumps(parks_json_request),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response

    assert mock_callback.times_called == mock_callback_count
    if mock_callback_count > 0:
        mock_request = mock_callback.next_call()['request']
        assert mock_request.method == 'POST'
        auth.check_user_ticket_headers(mock_request.headers)
        assert mock_request.headers['X-Idempotency-Token'] == idempotency_token
        mock_json_request = json.loads(mock_request.get_data())
        utils.check_categories_filter(mock_json_request)
        assert mock_json_request == parks_json_request


CAR_MODIFY_PARAMS = [
    (
        {'id': '00033693fa67429588f09de95f4aaa9c', 'park_id': '1488'},
        1,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        200,
        {'car_id': '00033693fa67429588f09de95f4aaa9c'},
    ),
    (
        {'park_id': '1488'},
        0,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        400,
        utils.format_error('parameter id must be set'),
    ),
    (
        {'id': '00033693fa67429588f09de95f4aaa9c', 'park_id': '1488'},
        1,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        400,
        utils.format_error('unknown error'),
    ),
    (
        {'id': '00033693fa67429588f09de95f4aaa9c', 'park_id': '1488'},
        1,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
        },
        500,
        utils.INTERNAL_ERROR,
    ),
]


@pytest.mark.parametrize(
    'query_params,mock_callback_count,'
    'parks_json_request,expected_code,expected_response',
    CAR_MODIFY_PARAMS,
)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_car_modify(
        taxi_fleet_management_api,
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

    response = taxi_fleet_management_api.put(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params=query_params,
        data=json.dumps(parks_json_request),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response

    assert mock_callback.times_called == mock_callback_count
    if mock_callback_count > 0:
        mock_request = mock_callback.next_call()['request']
        assert mock_request.method == 'PUT'
        auth.check_user_ticket_headers(mock_request.headers)
        mock_json_request = json.loads(mock_request.get_data())
        utils.check_categories_filter(mock_json_request)
        assert mock_json_request == parks_json_request
