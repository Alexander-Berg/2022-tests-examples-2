import json

from fleet_management_api import utils
from . import auth

OK_REQUEST = {'limit': 1}

OK_RESPONSE = {
    'devices': [
        {
            'device_id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            'device_serial_number': '22384DAD323SDAS',
            'status': {
                'status_at': '2020-02-27T12:00:00+00:00',
                'status': 'closed',
                'gnss': {
                    'lat': 54.99250000,
                    'lon': 73.36861111,
                    'speed_kmph': 34.437895,
                    'accuracy_m': 0.61340,
                    'direction_deg': 245.895,
                },
            },
        },
    ],
}

PARK_ID = 'park_id_test'

ENDPOINT_URL = 'v1/signalq/devices/list'
MOCK_URL = (
    '/signal_device_api_admin/external/signal-device-api-admin/v1/devices/list'
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
    error_code = 'invalid_cursor'
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
