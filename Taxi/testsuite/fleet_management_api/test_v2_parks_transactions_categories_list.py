import json

import pytest

from . import auth
from . import utils


ENDPOINT_URL = 'v2/parks/transactions/categories/list'
MOCK_URL = (
    '/fleet_transactions_api/v1/parks/transactions/categories/list/by-user'
)
OK_HEADERS = {**auth.HEADERS, **utils.ACCEPT_LANGUAGE_HEADERS}
OK_MOCK_HEADERS = {
    **utils.ACCEPT_LANGUAGE_HEADERS,
    **auth.USER_TICKET_HEADERS,
    'X-Yandex-UID': '54591353',
    'X-Fleet-API-Client-ID': None,
    'X-Fleet-API-Key-ID': None,
}
OK_REQUEST = {
    'query': {
        'park': {'id': 'park_id_test'},
        'category': {'is_enabled': True},
    },
}
OK_RESPONSE = {
    'categories': [
        {
            'id': 'cash_collected',
            'name': 'Наличная оплата',
            'is_enabled': True,
        },
    ],
}


BAD_REQUEST_PARAMS = [
    (123, 'json root must be an object'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
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


def test_unauthorized(taxi_fleet_management_api, mockserver, load_json):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    headers = OK_HEADERS.copy()
    headers.pop(auth.USER_TICKET_HEADER)
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=headers, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 401, response.text
    assert response.json() == utils.UNAUTHORIZED_ERROR
    assert mock_callback.times_called == 0


@pytest.mark.config(
    FLEET_API_DISABLED_PERMISSIONS={
        'external': ['fleet-api:v2-parks-transactions-categories-list:POST'],
        'internal': [],
    },
)
def test_ok(taxi_fleet_management_api, mockserver, load_json):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return OK_RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=OK_HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == OK_RESPONSE, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == OK_REQUEST
    for (header, value) in OK_MOCK_HEADERS.items():
        assert mock_request.headers.get(header) == value


MOCK_ERROR_PARAMS = [
    (
        400,
        json.dumps({'code': '400', 'message': 'bad message'}),
        utils.format_error('bad message', '400'),
    ),
    (400, 'not a json', utils.format_error('not a json')),
    (
        403,
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
    assert response.json() == response_json
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == OK_REQUEST


@pytest.mark.config(
    FLEET_API_DISABLED_PERMISSIONS={
        'external': [],
        'internal': ['fleet-api:v2-parks-transactions-categories-list:POST'],
    },
)
def test_disabled(taxi_fleet_management_api):
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=OK_HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 404, response.text
    assert response.json() == utils.ENDPOINT_DISABLED_ERROR
