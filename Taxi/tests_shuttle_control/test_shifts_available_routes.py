# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_main(taxi_shuttle_control, mockserver, experiments3):
    experiments3.add_config(
        name='shuttle_shifts_available_routes',
        consumers=['shuttle-control/shift_available_routes'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
        clauses=[
            {
                'title': 'first',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['route1', 'route2']},
            },
        ],
    )

    @mockserver.json_handler('driver-trackstory/position')
    def _mock_shorttrack(request):
        return {
            'position': {
                'lon': 37.642853,
                'lat': 55.735233,
                'timestamp': 1622202780,
            },
            'type': 'adjusted',
        }

    response = await taxi_shuttle_control.get(
        '/driver/v1/shuttle-control/v1/shifts/available-routes',
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert sorted(response.json()['routes'], key=lambda x: x['id']) == sorted(
        [
            {'name': 'route1', 'id': 'kP4UaDHpNCzrTj1C9B'},
            {'name': 'route2', 'id': 'JYXsE5HPdh18cxYC8N'},
        ],
        key=lambda x: x['id'],
    )


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_filtering(taxi_shuttle_control, mockserver, experiments3):
    experiments3.add_config(
        name='shuttle_shifts_available_routes',
        consumers=['shuttle-control/shift_available_routes'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
        clauses=[
            {
                'title': 'first',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['route1', 'route2']},
            },
        ],
    )

    @mockserver.json_handler('driver-trackstory/position')
    def _mock_shorttrack(request):
        return {
            'position': {'lon': 0, 'lat': 0, 'timestamp': 1622202780},
            'type': 'adjusted',
        }

    response = await taxi_shuttle_control.get(
        '/driver/v1/shuttle-control/v1/shifts/available-routes',
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'routes': []}
