import pytest

from . import auth
from . import utils

MOCK_URL = '/taximeter-xservice.taxi.yandex.net/fm-api/users'
ENDPOINT_URL = '/v1/users'

PARK_ID = '123'
TAXIMETER_RESPONSE = [
    {
        'id': 'fst',
        'sms_confirmation': True,
        'ip_restrictions': [{'start': 'string', 'end': 'string'}],
    },
    {'id': 'snd'},
]


def test_ok(taxi_fleet_management_api, mockserver, dispatcher_access_control):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return TAXIMETER_RESPONSE

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params={'park_id': PARK_ID}, headers=auth.HEADERS,
    )

    assert response.status_code == 200, response.text
    assert response.json() == TAXIMETER_RESPONSE

    assert dispatcher_access_control.times_called == 1
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'GET'
    assert mock_request.args.get('park_id') == PARK_ID
    assert mock_request.args.get('service_id') == auth.OPTEUM_SERVICE_ID
    utils.check_headers(mock_request.headers, utils.X_REAL_IP_HEADERS)


@pytest.mark.parametrize(
    'params, status_code, expected_response',
    [
        ({}, 400, utils.format_error('parameter park_id must be set')),
        (
            {'park_id': 'b\n'},
            400,
            utils.format_error('parameter park_id data is invalid'),
        ),
    ],
)
def test_bad_request(
        taxi_fleet_management_api,
        mockserver,
        params,
        status_code,
        expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=params,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == status_code, response.text
    assert response.json() == expected_response
