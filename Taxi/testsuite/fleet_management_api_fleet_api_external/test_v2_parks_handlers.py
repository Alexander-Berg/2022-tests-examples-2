import json

import pytest

from fleet_management_api import utils
from . import auth

OK_REQUEST = {'request': 'body'}
OK_RESPONSE = {'response': 'id'}

PARK_ID = 'park_id_test'
CONTRACTOR_ID = 'driver_id_test'
VEHICLE_ID = 'vehicle_id'
IDEMPOTENCY_TOKEN = '67754336-d4d1-43c1-aadb-cabd06674ea6'
X_REAL_IP = '1.2.3.4'

CONTRACTOR_ENDPOINT_URL = 'v2/parks/contractors/driver-profile'
CONTRACTOR_MOCK_URL = (
    '/contractor_profiles_manager/fleet-api/contractors/driver-profile'
)

VEHICLE_ENDPOINT_URL = 'v2/parks/vehicles/car'
VEHICLE_MOCK_URL = '/vehicles_manager/fleet-api/v1/vehicles/car'

DRIVER_TRANSACTIONS_ENDPOINT_URL = 'v2/parks/driver-profiles/transactions'
DRIVER_TRANSACTIONS_MOCK_URL = (
    '/fleet_transactions_api/v1/parks/driver-profiles/transactions/'
    'by-fleet-api'
)
TRANSACTIONS_DATA = {
    'amount': '1234.43',
    'category_id': 'manual',
    'currency_code': 'RUB',
    'description': 'Описание',
    'driver_profile_id': '9c5e35',
    'park_id': '7ad35b',
}

TRANSACTIONS_ENDPOINT_URL = 'v2/parks/transactions/categories/list'
TRANSACTIONS_MOCK_URL = (
    '/fleet_transactions_api/v1/parks/transactions/categories/list/'
    'by-fleet-api'
)
TRANSACTIONS_OK_REQUEST = {
    'query': {
        'park': {'id': 'park_id_test'},
        'category': {'is_enabled': True},
    },
}

HEADERS = {'X-Park-ID': PARK_ID, **auth.HEADERS}


@pytest.mark.config(
    FLEET_API_DISABLED_PERMISSIONS={
        'internal': ['fleet-api:v2-parks-transactions-categories-list:POST'],
        'external': [],
    },
)
@pytest.mark.parametrize(
    'url, method, request_body, response_body, headers, params, mock_url',
    [
        (
            CONTRACTOR_ENDPOINT_URL,
            'post',
            OK_REQUEST,
            OK_RESPONSE,
            {'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
            {},
            CONTRACTOR_MOCK_URL,
        ),
        (
            CONTRACTOR_ENDPOINT_URL,
            'put',
            OK_REQUEST,
            {},
            {},
            {'contractor_profile_id': CONTRACTOR_ID},
            CONTRACTOR_MOCK_URL,
        ),
        (
            CONTRACTOR_ENDPOINT_URL,
            'get',
            {},
            OK_RESPONSE,
            {},
            {'contractor_profile_id': CONTRACTOR_ID},
            CONTRACTOR_MOCK_URL,
        ),
        (
            VEHICLE_ENDPOINT_URL,
            'post',
            OK_REQUEST,
            OK_RESPONSE,
            {'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
            {},
            VEHICLE_MOCK_URL,
        ),
        (
            VEHICLE_ENDPOINT_URL,
            'put',
            OK_REQUEST,
            {},
            {},
            {'vehicle_id': VEHICLE_ID},
            VEHICLE_MOCK_URL,
        ),
        (
            VEHICLE_ENDPOINT_URL,
            'get',
            {},
            OK_RESPONSE,
            {},
            {'vehicle_id': VEHICLE_ID},
            VEHICLE_MOCK_URL,
        ),
        (
            DRIVER_TRANSACTIONS_ENDPOINT_URL,
            'post',
            TRANSACTIONS_DATA,
            TRANSACTIONS_DATA,
            {'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
            {},
            DRIVER_TRANSACTIONS_MOCK_URL,
        ),
        (
            TRANSACTIONS_ENDPOINT_URL,
            'post',
            TRANSACTIONS_OK_REQUEST,
            OK_RESPONSE,
            {'Accept-Language': 'ru_Ru'},
            {},
            TRANSACTIONS_MOCK_URL,
        ),
    ],
)
def test_ok(
        taxi_fleet_api_external,
        mockserver,
        api_keys,
        url,
        method,
        request_body,
        response_body,
        headers,
        params,
        mock_url,
):
    @mockserver.json_handler(mock_url)
    def mock_callback(request):
        request.get_data()
        return response_body

    send_request = getattr(taxi_fleet_api_external, method)

    response = send_request(
        url,
        headers={**HEADERS, **headers},
        params=params,
        data=json.dumps(request_body),
        x_real_ip=X_REAL_IP,
    )

    assert response.status_code == 200, response.text
    assert response.json() == response_body
    assert mock_callback.times_called == 1
    assert api_keys.has_calls
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == method.upper()
    if mock_request.method != 'GET':
        assert json.loads(mock_request.get_data()) == request_body


@pytest.mark.parametrize(
    'url, method, request_body, headers, params, mock_url',
    [
        (
            CONTRACTOR_ENDPOINT_URL,
            'post',
            OK_REQUEST,
            {'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
            {},
            CONTRACTOR_MOCK_URL,
        ),
        (
            CONTRACTOR_ENDPOINT_URL,
            'put',
            OK_REQUEST,
            {},
            {'contractor_profile_id': CONTRACTOR_ID},
            CONTRACTOR_MOCK_URL,
        ),
        (
            VEHICLE_ENDPOINT_URL,
            'post',
            OK_REQUEST,
            {'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
            {},
            VEHICLE_MOCK_URL,
        ),
        (
            VEHICLE_ENDPOINT_URL,
            'put',
            OK_REQUEST,
            {},
            {'vehicle_id': VEHICLE_ID},
            VEHICLE_MOCK_URL,
        ),
    ],
)
def test_bad_request(
        taxi_fleet_api_external,
        mockserver,
        url,
        method,
        request_body,
        headers,
        params,
        mock_url,
):
    error_code = 'invalid_hire_date'
    error_response = utils.format_error(error_code, error_code)

    @mockserver.json_handler(mock_url)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(json.dumps(error_response), 400)

    send_request = getattr(taxi_fleet_api_external, method)

    response = send_request(
        url,
        headers={**HEADERS, **headers},
        params=params,
        data=json.dumps(request_body),
        x_real_ip=X_REAL_IP,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error_response
    assert mock_callback.times_called == 1


@pytest.mark.parametrize(
    'url, method, request_body, params, mock_url',
    [
        (
            CONTRACTOR_ENDPOINT_URL,
            'put',
            OK_REQUEST,
            {'contractor_profile_id': CONTRACTOR_ID},
            CONTRACTOR_MOCK_URL,
        ),
        (
            CONTRACTOR_ENDPOINT_URL,
            'get',
            {},
            {'contractor_profile_id': CONTRACTOR_ID},
            CONTRACTOR_MOCK_URL,
        ),
        (VEHICLE_ENDPOINT_URL, 'post', OK_REQUEST, {}, VEHICLE_MOCK_URL),
        (
            VEHICLE_ENDPOINT_URL,
            'put',
            OK_REQUEST,
            {'vehicle_id': VEHICLE_ID},
            VEHICLE_MOCK_URL,
        ),
        (
            VEHICLE_ENDPOINT_URL,
            'get',
            {},
            {'vehicle_id': VEHICLE_ID},
            VEHICLE_MOCK_URL,
        ),
    ],
)
def test_not_found(
        taxi_fleet_api_external,
        mockserver,
        url,
        method,
        request_body,
        params,
        mock_url,
):
    error_code = 'not_found'
    error_response = utils.format_error(error_code, error_code)

    @mockserver.json_handler(mock_url)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(json.dumps(error_response), 404)

    send_request = getattr(taxi_fleet_api_external, method)

    response = send_request(
        url,
        headers=HEADERS,
        params=params,
        data=json.dumps(request_body),
        x_real_ip=X_REAL_IP,
    )

    assert response.status_code == 404, response.text
    assert response.json() == error_response
    assert mock_callback.times_called == 1


def test_conflict_put(taxi_fleet_api_external, mockserver):
    error_code = 'conflict'
    error_response = utils.format_error(error_code, error_code)

    @mockserver.json_handler(CONTRACTOR_MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(json.dumps(error_response), 409)

    response = taxi_fleet_api_external.put(
        CONTRACTOR_ENDPOINT_URL,
        headers=HEADERS,
        params={'contractor_profile_id': CONTRACTOR_ID},
        data=json.dumps(OK_REQUEST),
        x_real_ip=X_REAL_IP,
    )

    assert response.status_code == 409, response.text
    assert response.json() == error_response
    assert mock_callback.times_called == 1


@pytest.mark.config(
    FLEET_API_DISABLED_PERMISSIONS={
        'external': ['fleet-api:v2-parks-transactions-categories-list:POST'],
        'internal': [],
    },
)
def test_disabled(taxi_fleet_api_external):
    response = taxi_fleet_api_external.post(
        TRANSACTIONS_ENDPOINT_URL,
        headers={**auth.HEADERS, **utils.ACCEPT_LANGUAGE_HEADERS},
        data=json.dumps(TRANSACTIONS_OK_REQUEST),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'message': (
            'The endpoint has been disabled. If you have any questions,'
            ' you may contact us on: api-taxi@yandex-team.ru.'
        ),
    }
