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


@pytest.mark.now('2020-01-16T10:20:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passengers',
        },
        'route3': {
            'driver': 'shuttle_control.routes.route3.name_for_driver',
            'passenger': 'shuttle_control.routes.route3.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'dbid, uuid, expected_status_code, expected_response',
    [
        [
            '111',
            '888',
            200,
            {
                'schedule': [
                    {
                        'date': '2020-01-16',
                        'shifts': [
                            {
                                'id': '427a330d-2506-464a-accf-346b31e288b0',
                                'status': 'finished',
                                'subtitle': 'route2',
                                'title': '17:00-19:00',
                            },
                        ],
                    },
                    {
                        'date': '2020-01-17',
                        'shifts': [
                            {
                                'id': '427a330d-2506-464a-accf-346b31e288b8',
                                'status': 'ongoing',
                                'subtitle': 'route1',
                                'title': '17:00-21:00',
                            },
                        ],
                    },
                    {
                        'date': '2020-01-18',
                        'shifts': [
                            {
                                'id': '427a330d-2506-464a-accf-346b31e288c1',
                                'status': 'planned',
                                'subtitle': 'route3',
                                'title': '17:00-19:00',
                            },
                        ],
                    },
                    {'date': '2020-01-19', 'shifts': []},
                    {'date': '2020-01-20', 'shifts': []},
                    {'date': '2020-01-21', 'shifts': []},
                    {'date': '2020-01-22', 'shifts': []},
                ],
            },
        ],
        [
            '111',
            '882',
            200,
            {
                'schedule': [
                    {
                        'date': '2020-01-16',
                        'shifts': [
                            {
                                'id': '427a330d-2506-464a-accf-346b31e288b0',
                                'status': 'missed',
                                'subtitle': 'route2',
                                'title': '17:00-19:00',
                            },
                        ],
                    },
                    {'date': '2020-01-17', 'shifts': []},
                    {'date': '2020-01-18', 'shifts': []},
                    {'date': '2020-01-19', 'shifts': []},
                    {'date': '2020-01-20', 'shifts': []},
                    {'date': '2020-01-21', 'shifts': []},
                    {'date': '2020-01-22', 'shifts': []},
                ],
            },
        ],
    ],
)
async def test_main(
        taxi_shuttle_control,
        dbid,
        uuid,
        expected_status_code,
        expected_response,
):
    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = dbid
    headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    response = await taxi_shuttle_control.get(
        '/driver/v1/shuttle-control/v1/shifts/schedule', headers=HEADERS,
    )
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        assert response.json() == expected_response
