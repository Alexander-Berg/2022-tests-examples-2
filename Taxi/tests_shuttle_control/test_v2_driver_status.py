# pylint: disable=too-many-lines
import copy

import pytest

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': 'dbid_0',
    'X-YaTaxi-Driver-Profile-Id': 'uuid_1',
    'Accept-Language': 'ru',
}

MOCK_ON_WORKSHIFT_TIME = '2020-06-04T11:15:16+0000'
MOCK_BEFORE_WORKSHIFT_TIME = '2020-06-04T10:15:16+0000'


@pytest.fixture(autouse=True)
def mocks(experiments3, mockserver, load_json):
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
    'before_workshift',
    [
        pytest.param(True, marks=pytest.mark.now(MOCK_BEFORE_WORKSHIFT_TIME)),
        pytest.param(False, marks=pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)),
    ],
)
@pytest.mark.parametrize(
    'subscribed',
    [
        pytest.param(
            True,
            marks=pytest.mark.pgsql(
                'shuttle_control', files=['workshifts.sql'],
            ),
        ),
        False,
    ],
)
@pytest.mark.parametrize('scheduling', [False, True])
async def test_main_scheduling(
        taxi_shuttle_control,
        experiments3,
        before_workshift,
        subscribed,
        scheduling,
        load_json,
):
    experiments3.add_config(
        name='shuttle_shifts_control_access',
        consumers=['shuttle-control/shuttle_shifts_control_access'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/shuttle_shifts_control_access'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'title',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'reserve_enabled': True, 'cancel_enabled': True},
            },
        ],
    )

    headers = copy.deepcopy(HEADERS)
    if scheduling:
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_0'
    else:
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_1'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=headers,
    )

    if not scheduling and not subscribed:
        assert response.status_code == 500
        return

    assert response.status_code == 200

    if scheduling:
        if not subscribed:
            expected_response = load_json('not_subscribed_response.json')
        else:
            if before_workshift:
                expected_response = load_json(
                    'before_scheduling_response.json',
                )
            else:
                expected_response = load_json('after_scheduling_response.json')
    else:
        expected_response = load_json('en_route_response.json')

    assert response.json() == expected_response


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
    'before_workshift',
    [
        pytest.param(True, marks=pytest.mark.now(MOCK_BEFORE_WORKSHIFT_TIME)),
        pytest.param(False, marks=pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)),
    ],
)
@pytest.mark.parametrize(
    'subscribed',
    [
        pytest.param(
            True,
            marks=pytest.mark.pgsql(
                'shuttle_control', files=['workshifts.sql'],
            ),
        ),
        False,
    ],
)
@pytest.mark.parametrize('scheduling', [False, True])
async def test_main_scheduling_disabled(
        taxi_shuttle_control,
        experiments3,
        before_workshift,
        subscribed,
        scheduling,
        load_json,
):
    experiments3.add_config(
        name='shuttle_shifts_control_access',
        consumers=['shuttle-control/shuttle_shifts_control_access'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/shuttle_shifts_control_access'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'title',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'reserve_enabled': False, 'cancel_enabled': True},
            },
        ],
    )

    headers = copy.deepcopy(HEADERS)
    if scheduling:
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_0'
    else:
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_1'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=headers,
    )

    if not scheduling and not subscribed:
        assert response.status_code == 500
        return

    assert response.status_code == 200

    if scheduling:
        if not subscribed:
            expected_response = load_json(
                'not_subscribed_response_reservation_disabled.json',
            )
        else:
            if before_workshift:
                expected_response = load_json(
                    'before_scheduling_response_reservation_disabled.json',
                )
            else:
                expected_response = load_json(
                    'after_scheduling_response_reservation_disabled.json',
                )
    else:
        expected_response = load_json('en_route_response.json')

    assert response.json() == expected_response


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
    'before_workshift',
    [
        pytest.param(True, marks=pytest.mark.now(MOCK_BEFORE_WORKSHIFT_TIME)),
        pytest.param(False, marks=pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)),
    ],
)
@pytest.mark.parametrize(
    'subscribed',
    [
        pytest.param(
            True,
            marks=pytest.mark.pgsql(
                'shuttle_control', files=['workshifts.sql'],
            ),
        ),
        False,
    ],
)
@pytest.mark.parametrize('scheduling', [False, True])
async def test_main_scheduling_non_shuttle_fix(
        mockserver,
        taxi_shuttle_control,
        experiments3,
        before_workshift,
        subscribed,
        scheduling,
        load_json,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle'}

    experiments3.add_config(
        name='shuttle_shifts_control_access',
        consumers=['shuttle-control/shuttle_shifts_control_access'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/shuttle_shifts_control_access'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'title',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'reserve_enabled': True, 'cancel_enabled': True},
            },
        ],
    )

    headers = copy.deepcopy(HEADERS)
    if scheduling:
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_0'
    else:
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_1'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=headers,
    )

    if not scheduling and not subscribed:
        assert response.status_code == 500
        return

    assert response.status_code == 200

    if scheduling:
        if not subscribed:
            expected_response = load_json(
                'not_subscribed_response_non_shuttle_fix.json',
            )
        else:
            if before_workshift:
                expected_response = load_json(
                    'before_scheduling_response_non_shuttle_fix.json',
                )
            else:
                expected_response = load_json('after_scheduling_response.json')
    else:
        expected_response = load_json('en_route_response.json')

    assert response.json() == expected_response


@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
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
@pytest.mark.pgsql(
    'shuttle_control', files=['main_en_route.sql', 'workshifts.sql'],
)
@pytest.mark.parametrize(
    'pass_via_before_stop,is_on_route,billing_error,is_out_of_workshift',
    [
        (False, True, False, False),
        (True, True, True, False),
        (True, False, True, False),
        (True, True, False, True),
    ],
)
async def test_main_en_route(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        load_json,
        pass_via_before_stop,
        is_on_route,
        billing_error,
        is_out_of_workshift,
):
    if billing_error:

        @mockserver.json_handler('/driver-fix/v1/internal/status')
        def _mock_billing(request):
            return mockserver.make_response(status=500)

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': pass_via_before_stop,
                    'remaining_distance': 100,
                    'stops_display_limit': 4,
                    'cyclic_route_points_limit_forward': 4,
                    'cyclic_route_points_limit_back': 4,
                },
            },
        ],
    )

    if not is_on_route:
        pgsql['shuttle_control'].cursor().execute(
            load('upd_shuttle_not_on_route.sql'),
        )
    if is_out_of_workshift:
        pgsql['shuttle_control'].cursor().execute(
            load('upd_shuttle_out_of_workshift.sql'),
        )

    expected_resp = load_json('main_en_route_response.json')

    if pass_via_before_stop:
        first_via_point = {
            'remaining_distance': 100,
            'point': [30.0, 60.0],
            'type': 'via',
        }
        expected_resp['route']['points'].insert(0, first_via_point)

    if billing_error:
        expected_resp['en_route_panels']['work_mode_info'][
            'title'
        ] = 'Произошла ошибка'

    if is_out_of_workshift:
        expected_resp['en_route_panels']['work_mode_info'][
            'action_status'
        ] = 'warning'
        expected_resp['en_route_panels']['work_mode_info'][
            'text'
        ] = 'Ваша смена еще не началась'
    elif not is_on_route:
        expected_resp['en_route_panels']['work_mode_info'][
            'action_status'
        ] = 'warning'
        expected_resp['en_route_panels']['work_mode_info'][
            'text'
        ] = 'Шаттл не на линии'

    for _ in range(2):
        headers = copy.deepcopy(HEADERS)
        response = await taxi_shuttle_control.post(
            '/driver/v1/shuttle-control/v2/shuttle/status', headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == expected_resp


@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
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
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic_route.sql'])
async def test_en_route_dynamic(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    def _mock_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.642853,
                        'lat': 55.735233,
                        'timestamp': 1591269316,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 4,
                    'cyclic_route_points_limit_forward': 2,
                    'cyclic_route_points_limit_back': 4,
                },
            },
        ],
    )

    expected_resp = load_json('main_en_route_dynamic_response.json')
    for _ in range(2):
        headers = copy.deepcopy(HEADERS)
        response = await taxi_shuttle_control.post(
            '/driver/v1/shuttle-control/v2/shuttle/status', headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == expected_resp


@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
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
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic_route_on_stop.sql'])
@pytest.mark.parametrize(
    'with_default',
    [True, False],
    ids=('`with default`', '`with stop specific`'),
)
@pytest.mark.parametrize('work_mode', ['shuttle', 'shuttle_fix'])
@pytest.mark.parametrize(
    'pickup_timestamp,on_stop_from_timestamp,expected_time_to_wait',
    [
        ('2020-06-04T11:16:00+0000', '2020-06-04T11:15:00+0000', 3),
        ('2020-06-04T11:15:00+0000', '2020-06-04T11:15:00+0000', 2),
        ('2020-06-04T11:12:00+0000', '2020-06-04T11:14:00+0000', 1),
        ('2020-06-04T11:13:00+0000', '2020-06-04T11:12:00+0000', None),
        ('2020-06-04T11:12:00+0000', '2020-06-04T11:13:00+0000', None),
    ],
    ids=(
        '`come before timestamp`',
        '`wait passenger`',
        '`miss timestamp`',
        '`no passenger`',
        '`no passenger and miss`',
    ),
)
async def test_en_route_dynamic_on_stop(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        load_json,
        with_default,
        work_mode,
        pickup_timestamp,
        on_stop_from_timestamp,
        expected_time_to_wait,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.642853,
                        'lat': 55.735233,
                        'timestamp': 1591269316,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    experiments3.add_config(
        name='shuttle_boarding_time_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': (
                    {
                        'enabled': True,
                        'settings': {'__default__': {'wait_time': 90}},
                    }
                    if with_default
                    else {
                        'enabled': True,
                        'settings': {
                            '__default__': {'wait_time': 0},
                            'main_stop': {'wait_time': 120},
                        },
                    }
                ),
            },
        ],
    )

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 4,
                    'cyclic_route_points_limit_forward': 2,
                    'cyclic_route_points_limit_back': 4,
                },
            },
        ],
    )

    pgsql['shuttle_control'].cursor().execute(
        f"""
        UPDATE state.shuttle_trip_progress
        SET advanced_at = '{on_stop_from_timestamp}'
        WHERE shuttle_id = 1
        """,
    )
    pgsql['shuttle_control'].cursor().execute(
        f"""
        UPDATE state.matching_offers
        SET pickup_timestamp = '{pickup_timestamp}'
        WHERE offer_id = '43bdb9b8-ee06-4eac-b430-665788b29d53'
        """,
    )
    pgsql['shuttle_control'].cursor().execute(
        f"""
        UPDATE state.shuttles
        SET work_mode = '{work_mode}'::db.driver_work_mode
        WHERE TRUE
        """,
    )

    expected_resp = load_json('main_en_route_dynamic_response_for_stop.json')
    if work_mode == 'shuttle':
        expected_resp['en_route_panels']['work_mode_info']['icon'] = 'bus'
        expected_resp['en_route_panels']['work_mode_info'][
            'title'
        ] = 'Режим дохода "Шаттл"'
    if expected_time_to_wait is not None:
        expected_resp['en_route_panels']['work_mode_info'][
            'text'
        ] = 'Ожидайте пассажира'
        expected_resp['en_route_panels']['work_mode_info'][
            'title'
        ] = f'Ожидайте на остановке {expected_time_to_wait} мин.'

    for _ in range(2):
        headers = copy.deepcopy(HEADERS)
        response = await taxi_shuttle_control.post(
            '/driver/v1/shuttle-control/v2/shuttle/status', headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == expected_resp


@pytest.mark.translations(notify={'helpers.month_6_part': {'ru': 'сентября'}})
@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
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
@pytest.mark.pgsql(
    'shuttle_control', files=['main_cyclic.sql', 'workshifts.sql'],
)
@pytest.mark.parametrize('stop_point_id', [0, 3, 6])
@pytest.mark.parametrize('offset', [0, 1, 2])
@pytest.mark.parametrize('stop_requested', [False, True])
async def test_cyclic_en_route(
        taxi_shuttle_control,
        taxi_config,
        mockserver,
        pgsql,
        experiments3,
        stop_point_id,
        offset,
        stop_requested,
        driver_trackstory_v2_shorttracks,
):
    points_resp = [
        {
            'remaining_distance': 120,
            'point': [37.642853, 55.735233],
            'type': 'stop',
            'meta': {
                'title': 'Высадите пассажира',
                'name': 'stop1',
                'passengers': [
                    {
                        'type': 'outgoing',
                        'background_color': 'main_red',
                        'code': '123',
                    },
                ],
            },
        },
        {
            'remaining_distance': 120,
            'point': [37.642933, 55.735054],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.643129, 55.734452],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.643037, 55.734242],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.642790, 55.734062],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.642023, 55.734035],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.639896, 55.737345],
            'type': 'stop',
            'meta': {
                'title': 'Заберите пассажира',
                'name': 'stop5',
                'passengers': [
                    {
                        'type': 'accepted',
                        'background_color': 'main_green',
                        'code': '123',
                    },
                    {'type': 'incoming', 'background_color': 'main_green'},
                ],
            },
        },
        {
            'remaining_distance': 120,
            'point': [37.641867, 55.737651],
            'type': 'via',
        },
    ]

    points_range = range(stop_point_id - offset, stop_point_id + 4)

    if 8 not in points_range:
        points_resp[0]['type'] = 'via'
        del points_resp[0]['meta']

    if 6 not in points_range:
        points_resp[6]['type'] = 'via'
        del points_resp[6]['meta']

    if stop_requested:
        query = (
            'UPDATE state.shuttle_trip_progress'
            ' SET end_lap = 3, end_stop_id = begin_stop_id'
        )
        pgsql['shuttle_control'].cursor().execute(query)

    has_passengers = set(range(6, 8)).intersection(points_range)

    if points_range.start < 0:  # fix range bounds
        points_range = range(points_range.start + 8, points_range.stop + 8)

    expected_resp = {
        'en_route_panels': {
            'work_mode_info': {
                'title': (
                    'Доход: 4 мин 2000 руб., '
                    'Пассажиров в машине: 1, Ожидают впереди: 1'
                ),
                'text': (
                    'Продолжайте движение по маршруту'
                    if has_passengers
                    else 'Поиск пассажиров, двигайтесь по маршруту...'
                ),
                'icon': 'bus_time',
                'action_status': 'en_route',
            },
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'main_route',
            'points': [points_resp[idx % 8] for idx in points_range],
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
        'settings': {'tickets': {'length': 3}},
        'available_actions': [
            {'action': 'stop', 'is_disabled': False, 'text': 'Закончить слот'},
        ],
    }

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': True,
                    'remaining_distance': 120,
                    'stops_display_limit': 4,
                    'cyclic_route_points_limit_forward': 4,
                    'cyclic_route_points_limit_back': offset,
                },
            },
        ],
    )

    def _mock_positions():
        positions = {
            # for the first stop we are riding from the end to the start
            0: {'lon': 37.642455, 'lat': 55.736419, 'timestamp': 1600092910},
            3: {'lon': 37.643037, 'lat': 55.734242, 'timestamp': 1600092910},
            6: {'lon': 37.641311, 'lat': 55.735033, 'timestamp': 1600092910},
        }
        return {
            'results': [
                {
                    'position': positions[stop_point_id],
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_resp


@pytest.mark.translations(notify={'helpers.month_6_part': {'ru': 'сентября'}})
@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql(
    'shuttle_control', files=['main_cyclic_on_stop.sql', 'workshifts.sql'],
)
async def test_cyclic_en_route_on_stop(
        taxi_shuttle_control,
        taxi_config,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    points_resp = [
        {
            'remaining_distance': 120,
            'point': [37.642853, 55.735233],
            'type': 'stop',
            'meta': {
                'title': 'Заберите пассажира',
                'name': 'stop1',
                'passengers': [
                    {
                        'type': 'accepted',
                        'background_color': 'main_green',
                        'code': '123',
                    },
                    {'type': 'incoming', 'background_color': 'main_green'},
                ],
            },
        },
        {
            'remaining_distance': 120,
            'point': [37.642933, 55.735054],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.643129, 55.734452],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.643037, 55.734242],
            'type': 'via',
        },
        {
            'remaining_distance': 120,
            'point': [37.642790, 55.734062],
            'type': 'stop',
            'meta': {
                'title': 'Высадите пассажира',
                'name': 'stop3',
                'passengers': [
                    {
                        'type': 'outgoing',
                        'background_color': 'main_red',
                        'code': '123',
                    },
                ],
            },
        },
        {
            'remaining_distance': 120,
            'point': [37.642023, 55.734035],
            'type': 'via',
        },
    ]

    expected_resp = {
        'en_route_panels': {
            'work_mode_info': {
                'title': (
                    'Доход: 4 мин 2000 руб., '
                    'Пассажиров в машине: 1, Ожидают впереди: 1'
                ),
                'text': 'Продолжайте движение по маршруту',
                'icon': 'bus_time',
                'action_status': 'en_route',
            },
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'route1',
            'points': points_resp,
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
        'settings': {'tickets': {'length': 3}},
        'available_actions': [
            {'action': 'stop', 'is_disabled': False, 'text': 'Закончить слот'},
        ],
    }

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': True,
                    'remaining_distance': 120,
                    'stops_display_limit': 5,
                    'cyclic_route_points_limit_forward': 5,
                    'cyclic_route_points_limit_back': 0,
                },
            },
        ],
    )

    def _mock_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.642853,
                        'lat': 55.735233,
                        'timestamp': 1600092910,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_resp


@pytest.mark.translations(notify={'helpers.month_6_part': {'ru': 'сентября'}})
@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql(
    'shuttle_control',
    files=['main_cyclic_on_last_stop.sql', 'workshifts.sql'],
)
async def test_cyclic_en_route_on_last_stop(
        taxi_shuttle_control,
        taxi_config,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    points_resp = [
        {
            'remaining_distance': 120,
            'point': [37.641867, 55.737651],
            'type': 'stop',
            'meta': {
                'title': 'Заберите пассажира',
                'name': 'stop6',
                'passengers': [
                    {'type': 'incoming', 'background_color': 'main_green'},
                ],
            },
        },
        {
            'remaining_distance': 120,
            'point': [37.642853, 55.735233],
            'type': 'stop',
            'meta': {
                'title': 'Высадите пассажира',
                'name': 'stop1',
                'passengers': [
                    {
                        'type': 'outgoing',
                        'background_color': 'main_red',
                        'code': '123',
                    },
                ],
            },
        },
        {
            'remaining_distance': 120,
            'point': [37.642933, 55.735054],
            'type': 'via',
        },
    ]

    expected_resp = {
        'en_route_panels': {
            'work_mode_info': {
                'title': (
                    'Доход: 4 мин 2000 руб., '
                    'Пассажиров в машине: 1, Ожидают впереди: 1'
                ),
                'text': 'Продолжайте движение по маршруту',
                'icon': 'bus_time',
                'action_status': 'en_route',
            },
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'route1',
            'points': points_resp,
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
        'settings': {'tickets': {'length': 3}},
        'available_actions': [
            {'action': 'stop', 'is_disabled': False, 'text': 'Закончить слот'},
        ],
    }

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': True,
                    'remaining_distance': 120,
                    'stops_display_limit': 2,
                    'cyclic_route_points_limit_forward': 2,
                    'cyclic_route_points_limit_back': 0,
                },
            },
        ],
    )

    def _mock_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.641867,
                        'lat': 55.737651,
                        'timestamp': 1600092910,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_resp


@pytest.mark.translations(notify={'helpers.month_6_part': {'ru': 'сентября'}})
@pytest.mark.now(MOCK_ON_WORKSHIFT_TIME)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.parametrize(
    'pause_state', ['inactive', 'requested', 'in_work', 'overtime'],
)
async def test_pause_states(
        taxi_shuttle_control,
        taxi_config,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
        load,
        load_json,
        pause_state,
):
    def arrange_response(resp):
        resp['available_actions'] = sorted(
            resp['available_actions'], key=lambda it: it['action'],
        )
        return resp

    queries = [
        load('shuttle_pause/config.sql'),
        load(f'shuttle_pause/{pause_state}.sql'),
    ]
    pgsql['shuttle_control'].apply_queries(queries)

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': (
                    {
                        'pass_via_before_stop': True,
                        'remaining_distance': 120,
                        'stops_display_limit': 2,
                        'cyclic_route_points_limit_forward': 2,
                        'cyclic_route_points_limit_back': 0,
                    }
                ),
            },
        ],
    )

    def _mock_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.641867,
                        'lat': 55.737651,
                        'timestamp': 1600092910,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/status', headers=HEADERS,
    )

    expected_resp = load_json(f'shuttle_pause/{pause_state}_response.json')

    assert response.status_code == 200
    assert arrange_response(response.json()) == arrange_response(expected_resp)
