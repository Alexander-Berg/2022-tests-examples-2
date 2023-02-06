# pylint: disable=import-only-modules, too-many-lines
import copy
import datetime
import json

import pytest

from tests_shuttle_control.utils import select_named

MOCK_NOW = '2020-09-14T14:15:16+0000'
MOCK_NOW_DT = datetime.datetime(2020, 9, 14, 14, 15, 16)

MOCK_NOW_PLUS_15MIN = '2020-09-14T14:30:17+0000'

MOCK_NOW_MINUS_15MIN = '2020-09-14T14:00:16+0000'
MOCK_NOW_MINUS_15MIN_DT = datetime.datetime(2020, 9, 14, 14, 00, 16)

MOCK_NOW_PLUS_1H = '2020-09-14T15:15:16+0000'
MOCK_NOW_PLUS_1H_DT = datetime.datetime(2020, 9, 14, 15, 15, 16)

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
    SHUTTLE_CONTROL_SAVE_USERSTATS={'enabled': True},
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize(
    'available_routes',
    [['no_such_route1'], ['main_route', 'no_such_route_2']],
)
@pytest.mark.parametrize(
    'has_bookings,driver_profile_id', [(False, '888'), (True, '999')],
)
async def test_main(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        stq,
        stq_runner,
        load,
        available_routes,
        has_bookings,
        driver_profile_id,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_userapi(request):
        assert json.loads(request.get_data()) == {
            'primary_replica': False,
            'id': 'userid_2',
            'fields': ['application', 'phone_id', 'id'],
        }
        return {
            'items': [
                {
                    'id': 'userid_2',
                    'application': 'android',
                    'phone_id': '5da589137984b5db625a707f',
                },
            ],
        }

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle'}

    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': available_routes},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )

    expected_response = {
        'stops_display_limit': 3,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {
                        'type': 'deeplink',
                        'url': (
                            'taximeter://screen/stop_shuttle?'
                            'shuttle_id=Pmp80rQ23L4wZYxd'
                        ),
                    },
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': False,
            'is_dynamic': False,
            'route_name': 'main_route',
            'points': [
                {
                    'remaining_distance': 100,
                    'point': [37.642853, 55.735233],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.642933, 55.735054],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.643129, 55.734452],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.643148, 55.734349],
                    'type': 'stop',
                    'meta': {
                        'title': 'Двигайтесь к конечной остановке - stop4',
                        'name': 'stop4',
                        'passengers': [],
                    },
                },
            ],
        },
        'shuttle_id': 'Pmp80rQ23L4wZYxd',
        'state': 'en_route',
        'ticket_settings': {'length': 3},
        'work_mode_info': {
            'title': 'Режим дохода "Шаттл"',
            'text': 'Поиск пассажиров, двигайтесь по маршруту...',
            'icon': 'bus',
            'action_status': 'en_route',
        },
    }

    req_headers = copy.deepcopy(HEADERS)
    req_headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=req_headers,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    rows = select_named(
        f'SELECT sh.shuttle_id, sh.driver_id, sh.route_id, '
        f'sh.capacity, sh.started_at, '
        f'sh.ended_at, stp.begin_stop_id, stp.lap, '
        f'stp.next_stop_id, stp.end_stop_id, stp.end_lap, '
        f'stp.updated_at, sh.work_mode, sh.remaining_pauses, '
        f'sh.pause_state, sh.pause_id '
        f'FROM state.shuttles sh '
        f'INNER JOIN state.shuttle_trip_progress stp '
        f'ON sh.shuttle_id = stp.shuttle_id '
        f'WHERE sh.driver_id = '
        f'(\'111\',\'{driver_profile_id}\')::db.driver_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'shuttle_id': 2,
            'driver_id': '(111,' + driver_profile_id + ')',
            'route_id': 1,
            'capacity': 2,
            'started_at': MOCK_NOW_DT,
            'ended_at': None,
            'begin_stop_id': 1,
            'lap': 0,
            'end_stop_id': None,
            'end_lap': None,
            'next_stop_id': 1,
            'updated_at': MOCK_NOW_DT,
            'work_mode': 'shuttle',
            'remaining_pauses': 0,
            'pause_state': 'inactive',
            'pause_id': None,
        },
    ]

    if has_bookings:
        pgsql['shuttle_control'].cursor().execute(load('main_bookings.sql'))

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/stop_trip',
        headers=req_headers,
        params={'shuttle_id': 'Pmp80rQ23L4wZYxd'},
    )

    if has_bookings:
        assert (
            select_named(
                """
                SELECT booking_id, status, finished_at
                FROM state.passengers
                ORDER BY booking_id
                """,
                pgsql['shuttle_control'],
            )
            == [
                {
                    'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                    'status': 'cancelled',
                    'finished_at': MOCK_NOW_DT,
                },
                {
                    'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
                    'status': 'finished',
                    'finished_at': MOCK_NOW_DT,
                },
            ]
        )
        assert stq.shuttle_send_success_order_event.times_called == 1
        event = stq.shuttle_send_success_order_event.next_call()
        event.pop('id')
        event.pop('eta')
        event['kwargs'].pop('log_extra')
        assert event == {
            'queue': 'shuttle_send_success_order_event',
            'args': [],
            'kwargs': {
                'booking': {
                    'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
                    'created_at': '2022-01-20T16:00:00+0000',
                    'user_id': 'userid_2',
                    'yandex_uid': '012345679',
                    'payment_type': 'cash',
                },
            },
        }
        await stq_runner.shuttle_send_success_order_event.call(
            task_id='id',
            args=[],
            kwargs={
                'booking': {
                    'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
                    'created_at': '2022-01-20T16:00:00+0000',
                    'user_id': 'userid_2',
                    'yandex_uid': '012345679',
                    'payment_type': 'cash',
                },
            },
        )

        assert _mock_userapi.times_called == 1
        assert stq.userstats_order_complete.times_called == 1
        assert stq.success_shuttle_order_adjust_events.times_called == 1
        event = stq.userstats_order_complete.next_call()
        event.pop('id')
        event.pop('eta')
        event['kwargs'].pop('log_extra')
        assert event == {
            'queue': 'userstats_order_complete',
            'args': [],
            'kwargs': {
                'application': 'android',
                'phone_id': {'$oid': '5da589137984b5db625a707f'},
                'order_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
                'order_created': {'$date': '2022-01-20T16:00:00.000Z'},
                'tariff_class': 'shuttle',
                'payment_type': 'cash',
            },
        }
        event = stq.success_shuttle_order_adjust_events.next_call()
        event.pop('id')
        event.pop('eta')
        event['kwargs'].pop('log_extra')
        assert event == {
            'queue': 'success_shuttle_order_adjust_events',
            'args': [],
            'kwargs': {
                'app_name': 'android',
                'phone_id': '5da589137984b5db625a707f',
                'order_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
                'created_at': '2022-01-20T16:00:00.000000Z',
                'user_id': 'userid_2',
                'yandex_uid': '012345679',
            },
        }

        assert response.status_code == 200
        if len(available_routes) == 1:
            assert response.json() == {
                'panel_route_selection': {
                    'header': {'title': 'Выберите маршрут'},
                    'items': [],
                },
                'state': 'route_selection',
                'work_mode_info': {
                    'title': 'Режим дохода "Шаттл"',
                    'text': 'Выходите на линию, чтобы получать заказы',
                    'icon': 'bus',
                    'action_status': 'route_selection',
                },
            }
    else:
        rows = select_named(
            f'SELECT shuttle_id, driver_id, route_id, ended_at '
            f'FROM state.shuttles '
            f'WHERE driver_id = '
            f'(\'111\',\'{driver_profile_id}\')::db.driver_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'shuttle_id': 2,
                'driver_id': '(111,' + driver_profile_id + ')',
                'route_id': 1,
                'ended_at': MOCK_NOW_DT,
            },
        ]
        assert response.status_code == 200
        if len(available_routes) == 1:
            assert response.json() == {
                'panel_route_selection': {
                    'header': {'title': 'Выберите маршрут'},
                    'items': [],
                },
                'state': 'route_selection',
                'work_mode_info': {
                    'title': 'Режим дохода "Шаттл"',
                    'text': 'Выходите на линию, чтобы получать заказы',
                    'icon': 'bus',
                    'action_status': 'route_selection',
                },
            }
        else:
            assert response.json() == {
                'panel_route_selection': {
                    'header': {'title': 'Выберите маршрут'},
                    'items': [
                        {
                            'horizontal_divider_type': 'bottom_gap',
                            'payload': {
                                'type': 'deeplink',
                                'url': (
                                    'taximeter://screen/start_shuttle?'
                                    'route_id=gkZxnYQ73QGqrKyz'
                                ),
                            },
                            'title': 'main_route',
                            'type': 'tip_detail',
                            'right_icon': 'navigate',
                        },
                    ],
                },
                'state': 'route_selection',
                'work_mode_info': {
                    'title': 'Режим дохода "Шаттл"',
                    'text': 'Выходите на линию, чтобы получать заказы',
                    'icon': 'bus',
                    'action_status': 'route_selection',
                },
            }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize('vdh_id', [None, '0123456789'])
async def test_start_trip_with_vfh_id(
        taxi_shuttle_control, mockserver, experiments3, pgsql, vdh_id,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle'}

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    if vdh_id:
        experiments3.add_experiment(
            name='shuttle_mt_vfh_id',
            consumers=['shuttle-control/start_trip'],
            clauses=[],
            match={
                'enabled': True,
                'consumers': [{'name': 'shuttle-control/start_trip'}],
                'predicate': {'type': 'true', 'init': {}},
            },
            default_value={'vfh_id': vdh_id},
        )
        await taxi_shuttle_control.invalidate_caches()

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=HEADERS,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )
    assert response.status_code == 200

    rows = select_named(
        f'SELECT vfh_id FROM state.shuttles sh '
        f'WHERE sh.driver_id = (\'111\',\'888\')::db.driver_id',
        pgsql['shuttle_control'],
    )
    assert rows == [{'vfh_id': vdh_id}]


@pytest.mark.now(MOCK_NOW_PLUS_15MIN)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize('driver_profile_id', ['999'])
async def test_start_too_late_for_shift(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        driver_profile_id,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

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

    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['main_route']},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )

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
                'title': 'main_route',
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

    expected_response = {
        'code': '400',
        'message': 'You are 15 minutes late for shift',
    }

    req_headers = copy.deepcopy(HEADERS)
    req_headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=req_headers,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize('is_dry_run', [False, True])
async def test_start_restrictions(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        is_dry_run,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    @mockserver.json_handler('candidates/satisfy')
    def _mock_candidates(request):
        return {
            'drivers': [
                {
                    'dbid': '111',
                    'uuid': '888',
                    'is_satisfied': False,
                    'details': {'infra/blocking_reason': []},
                },
            ],
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle'}

    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['main_route']},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_driver_start_restrictions',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'candidates_satisfy_check': {
                        'enabled': True,
                        'dry_run': is_dry_run,
                        'reasons_prohibited': ['infra/blocking_reason'],
                    },
                },
            },
        ],
    )

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=HEADERS,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    if is_dry_run:
        assert response.status_code == 200
        return

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Access to orders is blocked. Check diagnostics page.',
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize(
    'has_bookings, driver_profile_id, remaining_pauses',
    [(False, '888', 0), (True, '999', 3)],
)
async def test_start_stop_shuttle_fix(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        has_bookings,
        driver_profile_id,
        remaining_pauses,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    # driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

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

    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['main_route']},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )

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
                'title': 'main_route',
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

    expected_response = {
        'stops_display_limit': 3,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {
                        'type': 'deeplink',
                        'url': (
                            'taximeter://screen/stop_shuttle?'
                            'shuttle_id=Pmp80rQ23L4wZYxd'
                        ),
                    },
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': False,
            'is_dynamic': False,
            'route_name': 'main_route',
            'points': [
                {
                    'remaining_distance': 100,
                    'point': [37.642853, 55.735233],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.642933, 55.735054],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.643129, 55.734452],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.643148, 55.734349],
                    'type': 'stop',
                    'meta': {
                        'title': 'Двигайтесь к конечной остановке - stop4',
                        'name': 'stop4',
                        'passengers': [],
                    },
                },
            ],
        },
        'shuttle_id': 'Pmp80rQ23L4wZYxd',
        'state': 'en_route',
        'ticket_settings': {'length': 3},
        'work_mode_info': {
            'title': (
                'Доход: 4 мин 2000 руб., '
                'Пассажиров в машине: 0, Ожидают впереди: 0'
            ),
            'text': 'Поиск пассажиров, двигайтесь по маршруту...',
            'icon': 'bus_time',
            'action_status': 'en_route',
        },
    }

    req_headers = copy.deepcopy(HEADERS)
    req_headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=req_headers,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    rows = select_named(
        f'SELECT sh.shuttle_id, sh.driver_id, sh.route_id,'
        f'sh.capacity, sh.started_at,'
        f'sh.ended_at, stp.begin_stop_id, stp.lap,'
        f'stp.next_stop_id, stp.end_stop_id, stp.end_lap,'
        f'stp.updated_at, sh.work_mode, sh.remaining_pauses '
        f'FROM state.shuttles sh '
        f'INNER JOIN state.shuttle_trip_progress stp '
        f'ON sh.shuttle_id = stp.shuttle_id '
        f'WHERE sh.driver_id = '
        f'(\'111\',\'{driver_profile_id}\')::db.driver_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'shuttle_id': 2,
            'driver_id': '(111,' + driver_profile_id + ')',
            'route_id': 1,
            'capacity': 2,
            'started_at': MOCK_NOW_DT,
            'ended_at': None,
            'begin_stop_id': 1,
            'lap': 0,
            'end_stop_id': None,
            'end_lap': None,
            'next_stop_id': 1,
            'updated_at': MOCK_NOW_DT,
            'work_mode': 'shuttle_fix',
            'remaining_pauses': remaining_pauses,
        },
    ]

    if has_bookings:
        pgsql['shuttle_control'].cursor().execute(load('main_bookings.sql'))

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/stop_trip',
        headers=req_headers,
        params={'shuttle_id': 'Pmp80rQ23L4wZYxd'},
    )

    rows = select_named(
        f'SELECT shuttle_id, driver_id, route_id, ended_at '
        f'FROM state.shuttles '
        f'WHERE driver_id = (\'111\',\'{driver_profile_id}\')::db.driver_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 2,
            'driver_id': '(111,' + driver_profile_id + ')',
            'route_id': 1,
            'ended_at': MOCK_NOW_DT,
        },
    ]

    if has_bookings:
        assert (
            select_named(
                """
                            SELECT booking_id, status, finished_at
                            FROM state.passengers
                            ORDER BY booking_id
                            """,
                pgsql['shuttle_control'],
            )
            == [
                {
                    'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                    'status': 'cancelled',
                    'finished_at': MOCK_NOW_DT,
                },
                {
                    'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
                    'status': 'finished',
                    'finished_at': MOCK_NOW_DT,
                },
            ]
        )

    assert response.status_code == 200
    assert response.json() == {
        'panel_route_selection': {
            'header': {'title': 'Выберите маршрут'},
            'items': [
                {
                    'horizontal_divider_type': 'bottom_gap',
                    'payload': {
                        'type': 'deeplink',
                        'url': (
                            'taximeter://screen/start_shuttle?'
                            'route_id=gkZxnYQ73QGqrKyz'
                        ),
                    },
                    'title': 'main_route',
                    'type': 'tip_detail',
                    'right_icon': 'navigate',
                },
            ],
        },
        'state': 'route_selection',
        'work_mode_info': {
            'title': (
                'Доход: 4 мин 2000 руб., '
                'Пассажиров в машине: 0, Ожидают впереди: 0'
            ),
            'text': 'Выходите на линию, чтобы получать доход',
            'icon': 'bus_time',
            'action_status': 'route_selection',
        },
    }


@pytest.mark.now(MOCK_NOW_MINUS_15MIN)  # чтобы не попадало в смену
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize(
    'has_bookings, driver_profile_id', [(False, '999'), (True, '999')],
)
async def test_start_shuttle_fix_out_of_workshift(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        has_bookings,
        driver_profile_id,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

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

    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['main_route']},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )

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
                'title': 'main_route',
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
                            'time_amount': {'unit': 'minute', 'value': 15},
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

    expected_response = {
        'stops_display_limit': 3,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {
                        'type': 'deeplink',
                        'url': (
                            'taximeter://screen/stop_shuttle?'
                            'shuttle_id=Pmp80rQ23L4wZYxd'
                        ),
                    },
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': False,
            'is_dynamic': False,
            'route_name': 'main_route',
            'points': [
                {
                    'remaining_distance': 100,
                    'point': [37.642853, 55.735233],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.642933, 55.735054],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.643129, 55.734452],
                    'type': 'via',
                },
                {
                    'remaining_distance': 100,
                    'point': [37.643148, 55.734349],
                    'type': 'stop',
                    'meta': {
                        'title': 'Двигайтесь к конечной остановке - stop4',
                        'name': 'stop4',
                        'passengers': [],
                    },
                },
            ],
        },
        'shuttle_id': 'Pmp80rQ23L4wZYxd',
        'state': 'en_route',
        'ticket_settings': {'length': 3},
        'work_mode_info': {
            'title': (
                'Доход: 4 мин 2000 руб., '
                'Пассажиров в машине: 0, Ожидают впереди: 0'
            ),
            'text': 'Ваша смена еще не началась',
            'icon': 'bus_time',
            'action_status': 'warning',
        },
    }

    req_headers = copy.deepcopy(HEADERS)
    req_headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=req_headers,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    rows = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap,
        stp.updated_at, sh.work_mode
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        WHERE sh.driver_id = ('111','888')::db.driver_id
        """,
        pgsql['shuttle_control'],
    )
    if driver_profile_id == '999':
        rows = select_named(
            """
            SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
            sh.capacity, sh.started_at,
            sh.ended_at, stp.begin_stop_id, stp.lap,
            stp.next_stop_id, stp.end_stop_id, stp.end_lap,
            stp.updated_at, sh.work_mode
            FROM state.shuttles sh
            INNER JOIN state.shuttle_trip_progress stp
            ON sh.shuttle_id = stp.shuttle_id
            WHERE sh.driver_id = ('111','999')::db.driver_id
            """,
            pgsql['shuttle_control'],
        )

    assert rows == [
        {
            'shuttle_id': 2,
            'driver_id': '(111,' + driver_profile_id + ')',
            'route_id': 1,
            'capacity': 2,
            'started_at': MOCK_NOW_MINUS_15MIN_DT,
            'ended_at': None,
            'begin_stop_id': 1,
            'lap': 0,
            'end_stop_id': None,
            'end_lap': None,
            'next_stop_id': 1,
            'updated_at': MOCK_NOW_MINUS_15MIN_DT,
            'work_mode': 'shuttle_fix',
        },
    ]

    if has_bookings:
        pgsql['shuttle_control'].cursor().execute(load('main_bookings.sql'))


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.translations(
    taximeter_backend_messages={
        'shuttle_control.request_stop_trip'
        '.forbidden_by_ongoing_workshift_title': {
            'ru': 'Не удалось выйти с маршрута',
        },
        'shuttle_control.request_stop_trip'
        '.forbidden_by_ongoing_workshift_body': {
            'ru': 'Ваша смена не закончена',
        },
    },
)
@pytest.mark.pgsql(
    'shuttle_control', files=['main_cyclic.sql', 'workshifts.sql'],
)
@pytest.mark.parametrize(
    'available_routes',
    [['no_such_route1'], ['main_route', 'no_such_route_2']],
)
@pytest.mark.parametrize(
    'stop_url, has_bookings',
    [('stop_trip', True), ('stop_trip', False), ('request_stop_trip', False)],
)
@pytest.mark.parametrize('driver_profile_id', (['999']))
async def test_main_cyclic(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        available_routes,
        has_bookings,
        stop_url,
        driver_profile_id,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.727534,
                'lon': 37.654193,
                'timestamp': 1600092916,
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 1999.85,
                'currency': 'RUB',
                'localized': '1999.85 руб.',
            },
            'cash_income': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
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

    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/' + stop_url],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/' + stop_url}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': available_routes},
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )
    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=[
            'shuttle-control/stop_trip',
            'shuttle-control/start_trip',
            'shuttle-control/polling',
        ],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/stop_trip'},
                {'name': 'shuttle-control/start_trip'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )

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
                'title': 'main_route',
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

    req_headers = copy.deepcopy(HEADERS)
    req_headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=req_headers,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'stops_display_limit': 3,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {
                        'type': 'deeplink',
                        'url': (
                            'taximeter://screen/stop_shuttle?'
                            'shuttle_id=gkZxnYQ73QGqrKyz'
                        ),
                    },
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'main_route',
            'points': [
                {
                    'point': [37.643055, 55.734163],
                    'remaining_distance': 100,
                    'type': 'via',
                },
                {
                    'point': [37.642023, 55.734035],
                    'remaining_distance': 100,
                    'type': 'via',
                },
                {
                    'point': [37.639663, 55.737276],
                    'remaining_distance': 100,
                    'type': 'via',
                },
                {
                    'point': [37.641867, 55.737651],
                    'remaining_distance': 100,
                    'type': 'via',
                },
                {
                    'point': [37.642853, 55.735233],
                    'remaining_distance': 100,
                    'type': 'via',
                },
                {
                    'point': [37.643129, 55.734452],
                    'remaining_distance': 100,
                    'type': 'via',
                },
            ],
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'ticket_settings': {'length': 3},
        'work_mode_info': {
            'action_status': 'en_route',
            'icon': 'bus_time',
            'text': 'Поиск пассажиров, двигайтесь по маршруту...',
            'title': (
                'Доход: 4 мин 1999.85 руб., '
                'Пассажиров в машине: 0, Ожидают впереди: 0'
            ),
        },
    }

    rows = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap,
        stp.updated_at
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'driver_id': '(111,' + driver_profile_id + ')',
            'route_id': 1,
            'capacity': 2,
            'started_at': MOCK_NOW_DT,
            'ended_at': None,
            'begin_stop_id': 3,
            'lap': 0,
            'end_stop_id': None,
            'end_lap': None,
            'next_stop_id': 3,
            'updated_at': MOCK_NOW_DT,
        },
    ]

    if has_bookings:
        pgsql['shuttle_control'].cursor().execute(
            load('main_cyclic_bookings.sql'),
        )

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/' + stop_url,
        headers=req_headers,
        params={'shuttle_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 200

    rows = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    ended_at = None
    if stop_url == 'stop_trip':
        ended_at = MOCK_NOW_DT

    assert rows == [
        {
            'shuttle_id': 1,
            'driver_id': '(111,' + driver_profile_id + ')',
            'route_id': 1,
            'capacity': 2,
            'started_at': MOCK_NOW_DT,
            'ended_at': ended_at,
            'begin_stop_id': 3,
            'lap': 0,
            'end_stop_id': None,
            'end_lap': None,
            'next_stop_id': 3,
        },
    ]

    if len(available_routes) == 1:
        if stop_url == 'request_stop_trip':
            assert response.json() == {
                'status': {
                    'shuttle_id': 'gkZxnYQ73QGqrKyz',
                    'route': {
                        'points': [
                            {
                                'point': [37.643055, 55.734163],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.642023, 55.734035],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.639663, 55.737276],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.641867, 55.737651],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.642853, 55.735233],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.643129, 55.734452],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                        ],
                        'is_cyclic': True,
                        'is_dynamic': False,
                        'route_name': 'main_route',
                    },
                    'panel_en_route': {
                        'items': [
                            {
                                'type': 'button',
                                'title': 'Завершить',
                                'accent': True,
                                'payload': {
                                    'type': 'deeplink',
                                    'url': (
                                        'taximeter://screen/stop_shuttle?'
                                        'shuttle_id=gkZxnYQ73QGqrKyz'
                                    ),
                                },
                            },
                        ],
                    },
                    'stops_display_limit': 3,
                    'ticket_settings': {'length': 3},
                    'work_mode_info': {
                        'action_status': 'en_route',
                        'icon': 'bus_time',
                        'text': 'Поиск пассажиров, двигайтесь по маршруту...',
                        'title': (
                            'Доход: 4 мин 1999.85 руб., '
                            'Пассажиров в машине: 0, Ожидают впереди: 0'
                        ),
                    },
                    'state': 'en_route',
                },
                'message': {
                    'title': 'Не удалось выйти с маршрута',
                    'body': 'Ваша смена не закончена',
                },
            }
        else:
            assert response.json() == {
                'panel_route_selection': {
                    'header': {'title': 'Выберите маршрут'},
                    'items': [],
                },
                'state': 'route_selection',
                'work_mode_info': {
                    'action_status': 'route_selection',
                    'icon': 'bus_time',
                    'text': 'Выходите на линию, чтобы получать доход',
                    'title': (
                        'Доход: 4 мин 1999.85 руб., '
                        'Пассажиров в машине: 0, Ожидают впереди: 0'
                    ),
                },
            }
    else:
        if stop_url == 'request_stop_trip':
            assert response.json() == {
                'status': {
                    'shuttle_id': 'gkZxnYQ73QGqrKyz',
                    'route': {
                        'points': [
                            {
                                'point': [37.643055, 55.734163],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.642023, 55.734035],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.639663, 55.737276],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.641867, 55.737651],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.642853, 55.735233],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.643129, 55.734452],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                        ],
                        'is_cyclic': True,
                        'is_dynamic': False,
                        'route_name': 'main_route',
                    },
                    'panel_en_route': {
                        'items': [
                            {
                                'type': 'button',
                                'title': 'Завершить',
                                'accent': True,
                                'payload': {
                                    'type': 'deeplink',
                                    'url': (
                                        'taximeter://screen/stop_shuttle?'
                                        'shuttle_id=gkZxnYQ73QGqrKyz'
                                    ),
                                },
                            },
                        ],
                    },
                    'stops_display_limit': 3,
                    'ticket_settings': {'length': 3},
                    'work_mode_info': {
                        'action_status': 'en_route',
                        'icon': 'bus_time',
                        'text': 'Поиск пассажиров, двигайтесь по маршруту...',
                        'title': (
                            'Доход: 4 мин 1999.85 руб., '
                            'Пассажиров в машине: 0, Ожидают впереди: 0'
                        ),
                    },
                    'state': 'en_route',
                },
                'message': {
                    'title': 'Не удалось выйти с маршрута',
                    'body': 'Ваша смена не закончена',
                },
            }
        else:
            assert response.json() == {
                'panel_route_selection': {
                    'header': {'title': 'Выберите маршрут'},
                    'items': [
                        {
                            'horizontal_divider_type': 'bottom_gap',
                            'payload': {
                                'type': 'deeplink',
                                'url': (
                                    'taximeter://screen/start_shuttle?'
                                    'route_id=gkZxnYQ73QGqrKyz'
                                ),
                            },
                            'title': 'main_route',
                            'type': 'tip_detail',
                            'right_icon': 'navigate',
                        },
                    ],
                },
                'state': 'route_selection',
                'work_mode_info': {
                    'action_status': 'route_selection',
                    'icon': 'bus_time',
                    'text': 'Выходите на линию, чтобы получать доход',
                    'title': (
                        'Доход: 4 мин 1999.85 руб., '
                        'Пассажиров в машине: 0, Ожидают впереди: 0'
                    ),
                },
            }


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'ticket_settings, expected_shuttle_ticket_length, '
    'expected_response_ticket_settings',
    [
        (
            {
                'enabled': True,
                'ticket_length': 3,
                'ticket_check_enabled': True,
            },
            3,
            {'length': 3},
        ),
        (
            {
                'enabled': True,
                'ticket_length': 4,
                'ticket_check_enabled': True,
            },
            4,
            {'length': 4},
        ),
        (
            {
                'enabled': True,
                'ticket_length': 4,
                'ticket_check_enabled': False,
            },
            4,
            None,
        ),
    ],
)
async def test_ticket_settings(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        ticket_settings,
        expected_shuttle_ticket_length,
        expected_response_ticket_settings,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle'}

    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': ticket_settings,
            },
        ],
    )

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/start_trip',
        headers=HEADERS,
        params={'route_id': 'gkZxnYQ73QGqrKyz'},
    )

    assert response.status_code == 200
    if not expected_response_ticket_settings:
        assert 'ticket_settings' not in response.json()
    else:
        assert (
            response.json()['ticket_settings']
            == expected_response_ticket_settings
        )
    rows = select_named(
        """
        SELECT shuttles.ticket_length
        FROM state.shuttles
        WHERE shuttle_id = 2
        """,
        pgsql['shuttle_control'],
    )
    assert len(rows) == 1
    row = rows[0]
    assert row == {'ticket_length': expected_shuttle_ticket_length}


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_stop_wrong_session(taxi_shuttle_control, mockserver, pgsql):
    headers_patched = copy.deepcopy(HEADERS)
    headers_patched['X-YaTaxi-Park-Id'] = 'dbid_0'
    headers_patched['X-YaTaxi-Driver-Profile-Id'] = 'uuid_0'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/stop_trip',
        headers=headers_patched,
        params={'shuttle_id': '3'},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Queried shuttle was not found',
    }


@pytest.mark.parametrize(
    'shuttle_id, driver_profile_id, on_workshift, expected_response',
    (
        pytest.param(
            '80vm7DQm7Ml24ZdO',
            '999',
            False,  # on workshift but stop allowed by config
            {
                'status': {
                    'panel_route_selection': {
                        'header': {'title': 'Выберите маршрут'},
                        'items': [
                            {
                                'type': 'tip_detail',
                                'title': 'main_route',
                                'right_icon': 'navigate',
                                'horizontal_divider_type': 'bottom_gap',
                                'payload': {
                                    'type': 'deeplink',
                                    'url': (
                                        'taximeter://screen/start_shuttle?'
                                        'route_id=gkZxnYQ73QGqrKyz'
                                    ),
                                },
                            },
                        ],
                    },
                    'work_mode_info': {
                        'title': (
                            'Доход: 4 мин 1999.85 руб., '
                            'Пассажиров в машине: 0, Ожидают впереди: 0'
                        ),
                        'text': 'Выходите на линию, чтобы получать доход',
                        'icon': 'bus_time',
                        'action_status': 'route_selection',
                    },
                    'state': 'route_selection',
                },
            },
            marks=[pytest.mark.now('2020-09-14T14:55:16+0000')],
        ),
        pytest.param(
            '80vm7DQm7Ml24ZdO',
            '999',
            True,
            {
                'status': {
                    'shuttle_id': '80vm7DQm7Ml24ZdO',
                    'route': {
                        'points': [
                            {
                                'point': [37.642853, 55.735233],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.642933, 55.735054],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.643129, 55.734452],
                                'remaining_distance': 100,
                                'type': 'via',
                            },
                            {
                                'point': [37.643148, 55.734349],
                                'remaining_distance': 100,
                                'meta': {
                                    'name': 'stop4',
                                    'title': (
                                        'Двигайтесь к '
                                        'конечной остановке - stop4'
                                    ),
                                    'passengers': [],
                                },
                                'type': 'stop',
                            },
                        ],
                        'is_cyclic': False,
                        'is_dynamic': False,
                        'route_name': 'main_route',
                    },
                    'panel_en_route': {
                        'items': [
                            {
                                'type': 'button',
                                'title': 'Завершить',
                                'accent': True,
                                'payload': {
                                    'type': 'deeplink',
                                    'url': (
                                        'taximeter://screen/stop_shuttle?'
                                        'shuttle_id=80vm7DQm7Ml24ZdO'
                                    ),
                                },
                            },
                        ],
                    },
                    'stops_display_limit': 3,
                    'work_mode_info': {
                        'title': (
                            'Доход: 4 мин 1999.85 руб., '
                            'Пассажиров в машине: 0, Ожидают впереди: 0'
                        ),
                        'text': 'Поиск пассажиров, двигайтесь по маршруту...',
                        'icon': 'bus_time',
                        'action_status': 'en_route',
                    },
                    'state': 'en_route',
                },
                'message': {
                    'title': 'Не удалось выйти с маршрута',
                    'body': 'Ваша смена не закончена',
                },
            },
            marks=[pytest.mark.now(MOCK_NOW)],
        ),
    ),
)
@pytest.mark.pgsql(
    'shuttle_control',
    files=['main.sql', 'workshifts.sql', 'extra_shuttles.sql'],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.translations(
    taximeter_backend_messages={
        'shuttle_control.request_stop_trip'
        '.forbidden_by_ongoing_workshift_title': {
            'ru': 'Не удалось выйти с маршрута',
        },
        'shuttle_control.request_stop_trip'
        '.forbidden_by_ongoing_workshift_body': {
            'ru': 'Ваша смена не закончена',
        },
    },
)
async def test_stop_ongoing_workshift(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        on_workshift,
        expected_response,
        driver_profile_id,
        shuttle_id,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 1999.85,
                'currency': 'RUB',
                'localized': '1999.85 руб.',
            },
            'cash_income': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
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

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_positions():
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.735200,
                'lon': 37.642900,
                'timestamp': 1600092910,
            },
        }

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
                'title': 'main_route',
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

    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['main_route', 'no_such_route_2']},
            },
        ],
    )

    rows_before = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    headers_patched = copy.deepcopy(HEADERS)
    headers_patched['X-YaTaxi-Park-Id'] = '111'
    headers_patched['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/request_stop_trip',
        headers=headers_patched,
        params={'shuttle_id': shuttle_id},
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    rows_after = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    if not on_workshift and driver_profile_id == '999':
        rows_before[2]['ended_at'] = datetime.datetime(2020, 9, 14, 14, 55, 16)

    assert rows_before == rows_after


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.translations(
    taximeter_backend_messages={
        'shuttle_control.request_stop_trip'
        '.forbidden_by_ongoing_workshift_title': {
            'ru': 'Не удалось выйти с маршрута',
        },
        'shuttle_control.request_stop_trip'
        '.forbidden_by_ongoing_workshift_body': {
            'ru': 'Ваша смена не закончена',
        },
    },
)
async def test_stop_routing_without_workshift(
        taxi_shuttle_control, mockserver, pgsql, experiments3,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 1999.85,
                'currency': 'RUB',
                'localized': '1999.85 руб.',
            },
            'cash_income': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
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

    experiments3.add_config(
        name='shuttle_available_routes',
        consumers=['shuttle-control/stop_trip'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/stop_trip'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'routes': ['main_route', 'no_such_route_2']},
            },
        ],
    )

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
                'title': 'main_route',
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

    rows_before = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    headers_patched = copy.deepcopy(HEADERS)
    headers_patched['X-YaTaxi-Park-Id'] = 'dbid_0'
    headers_patched['X-YaTaxi-Driver-Profile-Id'] = 'uuid_0'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/request_stop_trip',
        headers=headers_patched,
        params={'shuttle_id': 'gkZxnYQ73QGqrKyz'},
    )

    expected_response = {
        'status': {
            'panel_route_selection': {
                'header': {'title': 'Выберите маршрут'},
                'items': [
                    {
                        'type': 'tip_detail',
                        'title': 'main_route',
                        'right_icon': 'navigate',
                        'horizontal_divider_type': 'bottom_gap',
                        'payload': {
                            'type': 'deeplink',
                            'url': (
                                'taximeter://screen/start_shuttle?'
                                'route_id=gkZxnYQ73QGqrKyz'
                            ),
                        },
                    },
                ],
            },
            'work_mode_info': {
                'title': (
                    'Доход: 4 мин 1999.85 руб., '
                    'Пассажиров в машине: 0, Ожидают впереди: 0'
                ),
                'text': 'Выходите на линию, чтобы получать доход',
                'icon': 'bus_time',
                'action_status': 'route_selection',
            },
            'state': 'route_selection',
        },
    }

    assert response.status_code == 200
    assert response.json() == expected_response

    rows_after = select_named(
        """
        SELECT sh.shuttle_id, sh.driver_id, sh.route_id,
        sh.capacity, sh.started_at,
        sh.ended_at, stp.begin_stop_id, stp.lap,
        stp.next_stop_id, stp.end_stop_id, stp.end_lap
        FROM state.shuttles sh
        INNER JOIN state.shuttle_trip_progress stp
        ON sh.shuttle_id = stp.shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    rows_before[0]['ended_at'] = MOCK_NOW_DT

    assert rows_before == rows_after
