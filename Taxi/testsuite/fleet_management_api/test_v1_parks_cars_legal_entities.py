from . import auth

MOCK_URL = '/parks/cars/legal-entities'
ENDPOINT_URL = '/v1/parks/cars/legal-entities'

PARAMS = {'park_id': 'park', 'car_id': 'car'}
RESPONSE = {
    'legal_entities': [
        {
            'registration_number': '1234-ab-45',
            'name': 'Organization',
            'address': 'Street',
            'work_hours': '9-18',
            'type': 'park',
            'entity_id': 'ok',
        },
    ],
}


def test_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, params=PARAMS,
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.args.to_dict() == PARAMS
    assert response.json() == RESPONSE
