import json
import uuid

import pytest

from . import auth
from . import utils


ENDPOINT_URL = 'v2/parks/driver-profiles/transactions'
MOCK_URL = (
    '/fleet_transactions_api/v1/parks/driver-profiles/transactions/by-user'
)
IDEMPOTENCY_HEADERS = {'X-Idempotency-Token': uuid.uuid1().hex}
OK_HEADERS = {**auth.HEADERS, **IDEMPOTENCY_HEADERS}

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
        ENDPOINT_URL, headers=OK_HEADERS, data=json.dumps(query),
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)
    assert mock_callback.times_called == 0


def test_unauthorized(taxi_fleet_management_api, mockserver, load_json):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    headers = OK_HEADERS.copy()
    headers.pop(auth.USER_TICKET_HEADER)
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=headers,
        data=json.dumps(load_json('transaction.json')),
    )

    assert response.status_code == 401, response.text
    assert response.json() == utils.UNAUTHORIZED_ERROR
    assert mock_callback.times_called == 0


def test_ok(taxi_fleet_management_api, mockserver, load_json):
    transaction_json = load_json('transaction.json')

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return transaction_json

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=OK_HEADERS, data=json.dumps(transaction_json),
    )

    assert response.status_code == 200, response.text
    assert response.json() == transaction_json, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == transaction_json
    auth.check_user_ticket_headers(mock_request.headers)
    assert mock_request.headers.get('X-Yandex-UID') == '54591353'


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
    (400, 'not a json', utils.format_error('not a json')),
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
    ok_request = load_json('transaction.json')

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(mock_response_data, status_code)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=OK_HEADERS, data=json.dumps(ok_request),
    )

    assert response.status_code == status_code, response.text
    assert response.json() == response_json, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == ok_request
