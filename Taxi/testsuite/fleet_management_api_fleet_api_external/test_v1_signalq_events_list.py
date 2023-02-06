import json

from fleet_management_api import utils
from . import auth

OK_REQUEST = {
    'period': {
        'from': '2020-02-27T00:00:00+00',
        'to': '2020-02-27T13:00:00+00',
    },
    'limit': 1,
    'filter': {'serial_numbers': ['AB2', 'AB3', 'AB9']},
}

OK_RESPONSE = {
    'events': [
        {
            'event_at': '2020-02-27T12:00:00+00:00',
            'id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            'type': 'sleep',
            'vehicle': {
                'id': 'c1',
                'plate_number': 'K444AB55',
                'brand': 'lol',
                'model': 'kek',
            },
            'driver': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'id': 'd2',
                'license_number': '7723306794',
                'phones': ['+79265975310'],
            },
        },
    ],
}

PARK_ID = 'park_id_test'

ENDPOINT_URL = 'v1/signalq/events/list'
MOCK_URL = (
    '/signal_device_api_admin/external/signal-device-api-admin/v1/events/list'
)
HEADERS = {'X-Park-ID': PARK_ID, **auth.HEADERS}


def test_ok(taxi_fleet_api_external, mockserver, api_keys):
    expected_mock_headers = {
        'X-Fleet-API-Client-ID': auth.CLIENT_ID,
        'X-Fleet-API-Key-ID': str(auth.KEY_ID),
    }

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return OK_RESPONSE

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL, headers=HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == OK_RESPONSE
    assert mock_callback.times_called == 1
    assert api_keys.has_calls
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == OK_REQUEST
    for (header, value) in expected_mock_headers.items():
        assert mock_request.headers.get(header) == value


def test_bad_request(taxi_fleet_api_external, mockserver):
    error_code = 'invalid_period'
    error_response = utils.format_error(error_code, error_code)

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(json.dumps(error_response), 400)

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL, headers=HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error_response
    assert mock_callback.times_called == 1
