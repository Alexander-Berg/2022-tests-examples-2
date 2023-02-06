import json
import typing

import pytest

from . import auth
from . import utils

ENDPOINT_URL = '/v1/parks/orders/track'
MOCK_URL = '/driver_orders/v1/parks/orders/track'


PARAMS: typing.List = [
    ({}, None, None, 400, {'message': 'parameter park_id must be set'}),
    (
        {'park_id': ''},
        None,
        None,
        400,
        {'message': 'parameter park_id must be set'},
    ),
    (
        {'park_id': 'a'},
        None,
        None,
        400,
        {'message': 'parameter order_id must be set'},
    ),
    (
        {'park_id': 'a', 'order_id': ''},
        None,
        None,
        400,
        {'message': 'parameter order_id must be set'},
    ),
    (
        {'park_id': 'a', 'order_id': 'b'},
        404,
        {'code': '404', 'message': 'order not found'},
        404,
        {'code': '404', 'message': 'order not found'},
    ),
    (
        {'park_id': 'a', 'order_id': 'b'},
        404,
        {'code': 'order_not_found', 'message': 'order not found'},
        404,
        {'code': 'order_not_found', 'message': 'order not found'},
    ),
    ({'park_id': 'a', 'order_id': 'b'}, 400, {}, 500, utils.INTERNAL_ERROR),
    ({'park_id': 'a', 'order_id': 'b'}, 500, {}, 500, utils.INTERNAL_ERROR),
    (
        {'park_id': 'a', 'order_id': 'b'},
        429,
        'xxx',
        429,
        utils.TOO_MANY_REQUESTS_ERROR,
    ),
    (
        {'park_id': 'a', 'order_id': 'b'},
        200,
        {'track': []},
        200,
        {'track': []},
    ),
]


@pytest.mark.parametrize(
    'params, mock_code, mock_response_json, code, response_json', PARAMS,
)
def test_bad_request(
        taxi_fleet_management_api,
        mockserver,
        params,
        mock_code,
        mock_response_json,
        code,
        response_json,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps(mock_response_json), mock_code,
        )

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, params=params, headers=auth.HEADERS,
    )

    assert response.status_code == code, response.text
    assert response.json() == response_json

    if mock_code:
        assert mock_callback.has_calls
        assert mock_callback.next_call()['request'].args.to_dict() == params
    else:
        assert not mock_callback.has_calls
