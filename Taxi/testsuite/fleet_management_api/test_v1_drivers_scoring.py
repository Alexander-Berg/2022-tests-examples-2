import json

from . import auth

MOCK_URL = '/taximeter-xservice.taxi.yandex.net/utils/scoring/driver'
ENDPOINT_URL = '/v1/drivers/scoring/retrieve'

PARK_ID = '123'
TAXIMETER_OK_RESPONSE = {'some': 'ok response'}
TAXIMETER_400_RESPONSE = {
    'message': 'invalid license personal id',
    'code': 'BAD_REQUEST',
}
REQUEST_BODY = {'some': 'body'}


def test_ok(taxi_fleet_management_api, mockserver, dispatcher_access_control):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return TAXIMETER_OK_RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        params={'park_id': PARK_ID},
        json=REQUEST_BODY,
        headers=auth.HEADERS,
    )

    assert response.status_code == 200, response.text
    assert response.json() == TAXIMETER_OK_RESPONSE

    assert dispatcher_access_control.times_called == 1
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert mock_request.args.get('park_id') == PARK_ID
    assert json.loads(mock_request.get_data()) == REQUEST_BODY


def test_bad_request(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps(TAXIMETER_400_RESPONSE), 400,
        )

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        params={'park_id': PARK_ID},
        json=REQUEST_BODY,
        headers=auth.HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'message': 'invalid license personal id',
        'code': 'BAD_REQUEST',
    }

    assert mock_callback.times_called == 1
