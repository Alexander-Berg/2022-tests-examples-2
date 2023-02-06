# coding=utf-8
import json

import pytest


@pytest.mark.config(
    DRIVER_PARTNER_DEFAULT_CATEGORIES={'econom': True},
    DRIVER_PARTNER_DEFAULT_SERVICES={'wifi': True},
    DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'],
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'car.error.title': {'en': 'Error title'},
        'car.error.bad_request': {'en': 'Incorrect format of request'},
    },
)
@pytest.mark.parametrize(
    'profile_response,expected_code,expected_response,'
    'mock_response,mock_status',
    [
        (
            {'driver_partner_source': 'yandex'},
            200,
            {'id': '12312423532453434'},
            {'id': '12312423532453434'},
            200,
        ),
        (
            {'driver_partner_source': 'bad_source'},
            401,
            {'id': '12312423532453434'},
            {'id': '12312423532453434'},
            200,
        ),
        (
            {'driver_partner_source': 'yandex'},
            400,
            {
                'error': {
                    'title': 'Error title',
                    'text': 'Incorrect field HR 43535',
                },
            },
            {'error': {'text': 'Incorrect field HR 43535'}},
            400,
        ),
    ],
)
def test_car_create(
        taxi_driver_protocol,
        mockserver,
        profile_response,
        expected_code,
        expected_response,
        mock_response,
        mock_status,
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

    @mockserver.json_handler('/parks/car-create')
    def mock_car_create(request):
        json_request = json.loads(request.data)
        assert 'callsign' in json_request
        json_request.pop('callsign')
        assert json_request == {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ 123124',
            'park_id': '777',
            'category': ['econom'],
            'amenities': ['wifi'],
            'status': 'working',
            'booster_count': 0,
            'mileage': 0,
            'registration_cert': 'QX25',
            'vin': 'ABCDEFG0123456789',
        }
        return mockserver.make_response(json.dumps(mock_response), mock_status)

    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    response = taxi_driver_protocol.post(
        '/driver/park/car-create',
        params={'db': '777', 'session': 'session_1'},
        json={
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ 123124',
            'registration_cert': 'QX25',
            'vin': 'ABCDEFG0123456789',
        },
        headers={'Accept-Language': 'en'},
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert response.status_code == expected_code
    response_json = response.json()
    if response.status_code in [200, 400]:
        assert mock_car_create.times_called == 1
        assert mock_car_create.next_call()['request'].method == 'POST'

        assert response_json == expected_response
