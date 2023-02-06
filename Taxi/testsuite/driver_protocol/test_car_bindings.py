import json

import pytest


PARAMS = {'db': '777', 'session': 'session_1', 'car_id': 'car'}
CLIENT_PARAMS = {
    'park_id': '777',
    'driver_profile_id': 'selfreg1',
    'car_id': 'car',
}


@pytest.mark.config(DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'])
@pytest.mark.parametrize(
    'profile_response,car_response,car_status,' 'response_status',
    [
        ({'driver_partner_source': 'yandex'}, {}, 200, 200),
        ({'driver_partner_source': 'yandex'}, {}, 201, 200),
        (
            {'driver_partner_source': 'yandex'},
            {'error': {'text': 'No such car_id'}},
            400,
            400,
        ),
        ({'driver_partner_source': 'bad_source'}, {}, 200, 401),
    ],
)
def test_car_bindings_put(
        taxi_driver_protocol,
        mockserver,
        profile_response,
        car_response,
        car_status,
        response_status,
        driver_authorizer_service,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_driver_profile(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == ['selfreg1']
        assert data['query']['park']['id'] == ['777']
        return {
            'profiles': [
                {
                    'driver': {'car_id': '29a3400392154e48991b4aae5cd90ff0'},
                    'park': profile_response,
                },
            ],
        }

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def mock_car_bindings(request):
        return mockserver.make_response(json.dumps(car_response), car_status)

    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    response = taxi_driver_protocol.put(
        '/driver/driver-profiles/car-bindings', params=PARAMS,
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert response.status_code == response_status
    if response.status_code in [200, 400]:
        assert mock_car_bindings.times_called == 1
        mock_request = mock_car_bindings.next_call()['request']
        assert mock_request.headers.get('X-YaTaxi-Driver-Id') == 'selfreg1'
        assert mock_request.args.to_dict() == CLIENT_PARAMS

        if response.status_code == 400:
            assert response.json() == car_response


@pytest.mark.config(DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'])
@pytest.mark.parametrize(
    'car_response,car_status,response_status',
    [({}, 200, 200), ({'error': {'text': 'No such car_id'}}, 400, 400)],
)
def test_car_bindings_delete(
        taxi_driver_protocol,
        mockserver,
        car_response,
        car_status,
        response_status,
        driver_authorizer_service,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_driver_profile(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == ['selfreg1']
        assert data['query']['park']['id'] == ['777']
        return {
            'profiles': [
                {
                    'driver': {'car_id': '29a3400392154e48991b4aae5cd90ff0'},
                    'park': {'driver_partner_source': 'yandex'},
                },
            ],
        }

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def mock_car_bindings(request):
        return mockserver.make_response(json.dumps(car_response), car_status)

    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    response = taxi_driver_protocol.delete(
        '/driver/driver-profiles/car-bindings', params=PARAMS,
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert mock_car_bindings.times_called == 1
    mock_car_request = mock_car_bindings.next_call()['request']
    assert mock_car_request.headers.get('X-YaTaxi-Driver-Id') == 'selfreg1'
    assert mock_car_request.args.to_dict() == CLIENT_PARAMS

    assert response.status_code == response_status
    response_json = response.json()
    if response.status_code == 200:
        assert response_json == {}
    else:
        assert response.json() == car_response
