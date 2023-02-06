# pylint: disable=import-only-modules, import-error, redefined-outer-name
import datetime

import pytest

from tests_shuttle_control.utils import select_named


class AnyNumber:
    def __eq__(self, other):
        return isinstance(other, int)


HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


@pytest.fixture
def mocks_experiments(experiments3):
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
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'hour', 'value': 2},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                    },
                    'start_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 20},
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
                            'time_amount': {'unit': 'hour', 'value': 40},
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


@pytest.mark.parametrize(
    'now, response_code, expected_response_json',
    [
        (datetime.datetime(2020, 6, 4, 13, 55, 0), 200, 'response_main.json'),
        (datetime.datetime(2020, 6, 4, 12, 00, 0), 403, None),
    ],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        mockserver,
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        pgsql,
        load_json,
        mocked_time,
        response_code,
        expected_response_json,
        now,
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
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = 'dbid0'
    headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid0'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/finish-shift',
        headers=HEADERS,
        params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )

    assert response.status_code == response_code

    rows = select_named(
        """
        SELECT * FROM state.shuttles
        """,
        pgsql['shuttle_control'],
    )
    if response_code == 403:
        assert rows == [
            {
                'shuttle_id': 1,
                'driver_id': '(dbid0,uuid0)',
                'route_id': 1,
                'capacity': 16,
                'drw_state': 'Disabled',
                'is_fake': False,
                'revision': AnyNumber(),
                'ticket_check_enabled': False,
                'use_external_confirmation_code': False,
                'ticket_length': 3,
                'started_at': datetime.datetime(2020, 6, 3, 10, 15, 16),
                'ended_at': None,
                'work_mode': 'shuttle',
                'subscription_id': 1,
                'view_id': None,
                'vfh_id': None,
                'remaining_pauses': 0,
                'pause_state': 'inactive',
                'pause_id': None,
            },
        ]
    else:
        expected_response = load_json(expected_response_json)
        assert response.json() == expected_response

        assert rows == [
            {
                'shuttle_id': 1,
                'driver_id': '(dbid0,uuid0)',
                'route_id': 1,
                'capacity': 16,
                'drw_state': 'Disabled',
                'is_fake': False,
                'revision': AnyNumber(),
                'ticket_check_enabled': False,
                'use_external_confirmation_code': False,
                'ticket_length': 3,
                'started_at': datetime.datetime(2020, 6, 3, 10, 15, 16),
                'ended_at': now,
                'work_mode': 'shuttle',
                'subscription_id': 1,
                'view_id': None,
                'vfh_id': None,
                'remaining_pauses': 0,
                'pause_state': 'inactive',
                'pause_id': None,
            },
        ]


@pytest.mark.now('2020-06-04T14:20:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['retry.sql'])
async def test_client_retry(
        mockserver,
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        pgsql,
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
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = 'dbid0'
    headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid0'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/finish-shift',
        headers=HEADERS,
        params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )

    assert response.status_code == 200

    expected_response = load_json('response_retry.json')
    assert response.json() == expected_response

    rows = select_named(
        """
        SELECT * FROM state.shuttles
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'shuttle_id': 1,
            'driver_id': '(dbid0,uuid0)',
            'route_id': 1,
            'capacity': 16,
            'drw_state': 'Disabled',
            'is_fake': False,
            'revision': AnyNumber(),
            'ticket_check_enabled': False,
            'use_external_confirmation_code': False,
            'ticket_length': 3,
            'started_at': datetime.datetime(2020, 6, 3, 10, 15, 16),
            'ended_at': datetime.datetime(2020, 6, 3, 14, 15, 16),
            'work_mode': 'shuttle',
            'subscription_id': 1,
            'view_id': None,
            'vfh_id': None,
            'remaining_pauses': 0,
            'pause_state': 'inactive',
            'pause_id': None,
        },
    ]
