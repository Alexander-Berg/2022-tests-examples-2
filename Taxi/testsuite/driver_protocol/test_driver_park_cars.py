import json

import pytest


CAR_FIELDS = {
    'car': [
        'id',
        'brand',
        'model',
        'color',
        'year',
        'number',
        'registration_cert',
        'vin',
    ],
}


@pytest.fixture(scope='function', autouse=True)
def parks_client(mockserver, load_json):
    @mockserver.json_handler('/parks/car-colors')
    def car_colors(request):
        return load_json('car_colors.json')


@pytest.mark.config(
    CAR_CACHE_COLORS_UPDATE_ENABLED=True,
    DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'],
)
@pytest.mark.parametrize(
    'mock_request,enable_for_all',
    [
        ({'driver_partner_source': 'yandex'}, False),
        ({'driver_partner_source': 'yandex'}, True),
    ],
)
def test_selfemployment_cars(
        taxi_driver_protocol,
        config,
        parks_client,
        mockserver,
        load_json,
        mock_request,
        enable_for_all,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    config.set_values(dict(ENABLE_DRIVER_CARS_FOR_ALL_SOURCES=enable_for_all))

    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_driver_profile(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == ['selfreg1']
        assert data['query']['park']['id'] == ['777']
        return {
            'profiles': [
                {
                    'driver': {'car_id': '29a3400392154e48991b4aae5cd90ff0'},
                    'park': mock_request,
                },
            ],
        }

    @mockserver.json_handler('/parks/cars/list')
    def mock_cars(request):
        json_request = json.loads(request.data)
        assert json_request == {
            'query': {'park': {'id': '777'}},
            'fields': CAR_FIELDS,
        }
        return load_json('parks_cars_list_response.json')

    response = taxi_driver_protocol.get(
        '/driver/park/cars',
        params={'db': '777', 'session': 'session_1'},
        headers={'Accept-Language': 'en'},
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert response.status_code == 200
    assert mock_cars.times_called == 1
    assert mock_cars.next_call()['request'].method == 'POST'

    response_json = response.json()
    assert response_json == load_json('selfemployment_expected_response.json')


@pytest.mark.config(
    CAR_CACHE_COLORS_UPDATE_ENABLED=True,
    DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'],
)
@pytest.mark.parametrize(
    'mock_request, enable_for_all, expected_code',
    [
        ({'driver_partner_source': 'bad_source'}, False, 401),
        ({}, False, 401),
        ({'driver_partner_source': 'bad_source'}, True, 200),
        ({}, True, 200),
    ],
)
def test_cars(
        taxi_driver_protocol,
        config,
        parks_client,
        mockserver,
        load_json,
        mock_request,
        enable_for_all,
        expected_code,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    config.set_values(dict(ENABLE_DRIVER_CARS_FOR_ALL_SOURCES=enable_for_all))

    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_driver_profile(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == ['driver']
        assert data['query']['park']['id'] == ['777']
        return {
            'profiles': [
                {
                    'driver': {'car_id': '29a3400392154e48991b4aae5cd90ff0'},
                    'park': mock_request,
                },
            ],
        }

    @mockserver.json_handler('/parks/cars/list')
    def mock_cars(request):
        json_request = json.loads(request.data)
        assert json_request == {
            'query': {
                'park': {
                    'id': '777',
                    'car': {'id': ['29a3400392154e48991b4aae5cd90ff0']},
                },
            },
            'fields': CAR_FIELDS,
        }
        return load_json('driver_car_response.json')

    response = taxi_driver_protocol.get(
        '/driver/park/cars',
        params={'db': '777', 'session': 'qwerty'},
        headers={'Accept-Language': 'en'},
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert response.status_code == expected_code
    if response.status_code == 200:
        assert mock_cars.times_called == 1
        assert mock_cars.next_call()['request'].method == 'POST'

        response_json = response.json()
        assert response_json == load_json('expected_response.json')


@pytest.mark.config(
    CAR_CACHE_COLORS_UPDATE_ENABLED=True,
    DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'],
    ENABLE_DRIVER_CARS_FOR_ALL_SOURCES=True,
)
@pytest.mark.parametrize(
    'mock_request', [{'driver_partner_source': 'bad_source'}, {}],
)
def test_driver_without_cars(
        taxi_driver_protocol,
        parks_client,
        mockserver,
        load_json,
        mock_request,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_driver_profile(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == ['driver']
        assert data['query']['park']['id'] == ['777']
        return {'profiles': [{'driver': {}, 'park': {}}]}

    @mockserver.json_handler('/parks/cars/list')
    def mock_cars(request):
        return load_json('driver_car_response.json')

    response = taxi_driver_protocol.get(
        '/driver/park/cars',
        params={'db': '777', 'session': 'qwerty'},
        headers={'Accept-Language': 'en'},
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert response.status_code == 200
    assert not mock_cars.times_called

    response_json = response.json()
    assert response_json == load_json('empty_response.json')


@pytest.mark.config(
    CAR_CACHE_COLORS_UPDATE_ENABLED=True,
    DRIVER_PARTNER_AVAILABLE_SOURCES=['yandex'],
    ENABLE_DRIVER_CARS_FOR_ALL_SOURCES=True,
    TAXIMETER_MARKETPLACE={
        'enable': True,
        'cities': [],
        'countries': [],
        'dbs': ['777'],
        'driver_url': 'https://garage.yandex/',
    },
)
def test_actions_without_cars(
        taxi_driver_protocol,
        parks_client,
        mockserver,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_driver_profile(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == ['driver']
        assert data['query']['park']['id'] == ['777']
        return {
            'profiles': [
                {'driver': {}, 'park': {'driver_partner_source': 'yandex'}},
            ],
        }

    @mockserver.json_handler('/parks/cars/list')
    def mock_cars(request):
        return {'cars': []}

    response = taxi_driver_protocol.get(
        '/driver/park/cars',
        params={'db': '777', 'session': 'qwerty'},
        headers={'Accept-Language': 'en'},
    )

    assert mock_driver_profile.times_called == 1
    assert mock_driver_profile.next_call()['request'].method == 'POST'

    assert response.status_code == 200
    assert mock_cars.times_called == 1

    response_json = response.json()
    assert response_json == load_json('response_with_actions.json')
