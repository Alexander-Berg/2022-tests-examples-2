import json

from . import auth
from . import utils

MOCK_URL = '/taximeter-xservice.taxi.yandex.net/utils/blacklist/drivers/check'
ENDPOINT_URL = '/v1/parks/driver-profiles/blacklist/check'


def test_post_ok(
        taxi_fleet_management_api, mockserver, dispatcher_access_control,
):
    request_body = {
        'query': {
            'park': {
                'id': 'some_value',
                'driver_profile': {'id': 'driver_id'},
            },
        },
        'locale': 'some locale',
    }
    response_body = {'some': 'response'}

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return response_body

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_body),
    )

    assert response.status_code == 200, response.text
    assert response.json() == response_body

    assert dispatcher_access_control.times_called == 1
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == request_body
    utils.check_headers(mock_request.headers, utils.X_REAL_IP_HEADERS)
