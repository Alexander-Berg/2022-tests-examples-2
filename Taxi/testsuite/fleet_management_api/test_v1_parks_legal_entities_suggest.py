from . import auth

MOCK_URL = '/parks/legal-entities/suggest'
ENDPOINT_URL = '/v1/parks/legal-entities/suggest'

RESPONSE = {'legal_entities': [{'name': 'asd'}, {'name': 'qwe'}]}


def test_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params={'park_id': '1', 'registration_number': '2'},
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.args.to_dict() == {
        'registration_number': '2',
        'park_id': '1',
    }
    assert response.json() == RESPONSE


def test_temporarily_unavailable(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response('error', 503)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params={'park_id': '1', 'registration_number': '2'},
    )

    assert response.status_code == 503, response.text
    assert mock_callback.times_called == 1
