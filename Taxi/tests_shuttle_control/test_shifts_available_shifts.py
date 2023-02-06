# pylint: disable=import-error,too-many-lines,import-only-modules
import pytest

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


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
        'route3': {
            'driver': 'shuttle_control.routes.route3.name_for_driver',
            'passenger': 'shuttle_control.routes.route3.name_for_passenger',
        },
    },
)
@pytest.mark.now('2020-01-19T20:50:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['workshifts.sql'])
@pytest.mark.parametrize(
    'driver_work_mode,body,expected_response',
    [
        (
            'shuttle_fix',
            {'route_ids': ['kP4UaDHpNCzrTj1C9B']},
            'single_route_response.json',
        ),
        (
            'shuttle_fix',
            {'route_ids': ['Ob1IVef2bH5kTVJsjW', 'JYXsE5HPdh18cxYC8N']},
            'several_route_response.json',
        ),
        (
            'shuttle_fix',
            {'route_ids': ['kP4UaDHpNCzrTj1C9B']},
            'single_route_response.json',
        ),
    ],
)
async def test_shifts(
        mockserver,
        taxi_shuttle_control,
        experiments3,
        driver_work_mode,
        body,
        expected_response,
        load_json,
):
    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 2000,
                'currency': 'RUB',
                'localized': '2000 руб.',
            },
            'cash_income': {
                'value': 12,
                'currency': 'RUB',
                'localized': '12 руб.',
            },
            'payoff': {'value': 0, 'currency': 'RUB', 'localized': '0 руб.'},
            'commission': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
            },
            'total_income': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': driver_work_mode}

    experiments3.add_config(
        name='shuttle_shift_time_control',
        consumers=['shuttle-control/shift_time_control'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/shift_time_control'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'reservation_available': {
                        'from': {
                            'starting_point': 'start_of_week',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'hour', 'value': 2},
                        },
                        'to': {
                            'starting_point': 'start_of_week',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                    },
                    'start_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                    'stop_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_end',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_end',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                    'cancel_reservation_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 30},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                },
            },
        ],
    )

    def arrange_response(resp):
        for item in resp['shifts_schedule']:
            item['routes'] = sorted(
                item['routes'], key=lambda it: it['route_name'],
            )
        return resp

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shifts/available-shifts',
        headers=HEADERS,
        json=body,
    )
    assert response.status_code == 200
    assert arrange_response(response.json()) == arrange_response(
        load_json(expected_response),
    )
