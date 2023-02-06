import copy
import datetime

import pytest

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': 'dbid_0',
    'X-YaTaxi-Driver-Profile-Id': 'uuid_1',
    'Accept-Language': 'ru',
}

MOCK_NOW = '2020-09-14T14:15:16+0000'
MOCK_NOW_DT = datetime.datetime(2020, 9, 14, 14, 15, 16)


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
@pytest.mark.parametrize('available_routes', [None, [], [' main_route ']])
@pytest.mark.parametrize('work_mode', ['shuttle', 'shuttle_fix'])
@pytest.mark.parametrize('dbid, uuid', [('dbid3', 'uuid3')])
async def test_main_route_selection(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        available_routes,
        work_mode,
        dbid,
        uuid,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': work_mode}

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

    if available_routes is not None:
        experiments3.add_config(
            name='shuttle_available_routes',
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
                    'value': {'routes': available_routes},
                },
            ],
        )

    expected_work_mode_info = {
        'title': 'Режим дохода "Шаттл"',
        'text': 'Выходите на линию, чтобы получать заказы',
        'icon': 'bus',
        'action_status': 'route_selection',
    }
    if work_mode == 'shuttle_fix':
        expected_work_mode_info = {
            'title': (
                'Доход: 4 мин 2000 руб., '
                'Пассажиров в машине: 0, Ожидают впереди: 0'
            ),
            'text': 'Выходите на линию, чтобы получать доход',
            'icon': 'bus_time',
            'action_status': 'route_selection',
        }

    req_headers = HEADERS.copy()
    req_headers['X-YaTaxi-Park-Id'] = dbid
    req_headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=req_headers,
    )

    assert response.status_code == 200
    assert response.headers['ETag'] == '"68rlbqMrALvp1ONW"'
    if available_routes != []:  # is None or ['main_route']
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
            'work_mode_info': expected_work_mode_info,
        }
    else:
        assert response.json() == {
            'panel_route_selection': {
                'header': {'title': 'Выберите маршрут'},
                'items': [],
            },
            'state': 'route_selection',
            'work_mode_info': expected_work_mode_info,
        }

    #  headers = copy.deepcopy(HEADERS)
    req_headers['If-None-Match'] = response.headers['ETag']

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=req_headers,
    )

    # no changes
    assert response.status_code == 200
    assert response.headers['ETag'] == '"68rlbqMrALvp1ONW"'
    if available_routes is None or available_routes:
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
            'work_mode_info': expected_work_mode_info,
        }
    else:
        assert response.json() == {
            'panel_route_selection': {
                'header': {'title': 'Выберите маршрут'},
                'items': [],
            },
            'state': 'route_selection',
            'work_mode_info': expected_work_mode_info,
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
@pytest.mark.parametrize(
    'is_etag_enabled,version,pass_via_before_stop,is_on_route,'
    'driver_fix_error,is_out_of_workshift',
    [
        (False, '8.45', False, True, False, False),
        (True, '9.47', True, True, True, False),
        (False, '10.46', True, False, True, False),
        (False, '10.46', True, True, False, True),
    ],
)
async def test_main_en_route(
        taxi_shuttle_control,
        taxi_config,
        mockserver,
        experiments3,
        load,
        pgsql,
        is_etag_enabled,
        version,
        pass_via_before_stop,
        is_on_route,
        driver_fix_error,
        is_out_of_workshift,
):
    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        if driver_fix_error:
            return mockserver.make_response(status=500)

        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 2000,
                'currency': 'RUB',
                'localized': '2000 руб.',
            },
            'cash_income': {
                'value': 10,
                'currency': 'RUB',
                'localized': '10 руб.',
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

    queries = [load('main_en_route.sql')]
    if not is_on_route:
        queries.append(load('upd_shuttle_not_on_route.sql'))
    if is_out_of_workshift:
        queries.append(load('upd_shuttle_out_of_workshift.sql'))
    pgsql['shuttle_control'].apply_queries(queries)

    work_mode_title = (
        'Доход: 4 мин 2000 руб., Пассажиров в машине: 1, Ожидают впереди: 2'
        if not driver_fix_error
        else 'Произошла ошибка'
    )
    work_mode_text = 'Продолжайте движение по маршруту'
    if is_out_of_workshift:
        work_mode_text = 'Ваша смена еще не началась'
    elif not is_on_route:
        work_mode_text = 'Шаттл не на линии'
    action_status = (
        'en_route' if is_on_route and not is_out_of_workshift else 'warning'
    )

    expected_fst_resp = {
        'stops_display_limit': 4,
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
            'is_cyclic': False,
            'is_dynamic': False,
            'route_name': 'main_route',
            'points': [
                {
                    'meta': {
                        'title': 'Заберите пассажира',
                        'name': 'first_stop',
                        'passengers': [
                            {
                                'type': 'accepted',
                                'background_color': 'main_green',
                                'code': '123',
                            },
                            {
                                'type': 'incoming',
                                'background_color': 'main_green',
                            },
                        ],
                    },
                    'remaining_distance': 120,
                    'point': [30.0, 61.0],
                    'type': 'stop',
                },
                {
                    'meta': {
                        'title': 'Заберите пассажира\nВысадите пассажира',
                        'name': 'second_stop',
                        'passengers': [
                            {
                                'type': 'outgoing',
                                'background_color': 'main_red',
                                'code': '123',
                            },
                            {
                                'type': 'incoming',
                                'background_color': 'main_green',
                            },
                        ],
                    },
                    'remaining_distance': 120,
                    'point': [30.0, 62.0],
                    'type': 'stop',
                },
                {
                    'remaining_distance': 120,
                    'point': [30.0, 63.0],
                    'type': 'stop',
                    'meta': {
                        'title': 'Двигайтесь к конечной остановке - Ласт стоп',
                        'name': 'Ласт стоп',
                        'passengers': [],
                    },
                },
            ],
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'work_mode_info': {
            'title': work_mode_title,
            'text': work_mode_text,
            'icon': 'bus_time',
            'action_status': action_status,
        },
    }

    if pass_via_before_stop is True:
        first_via_point = {
            'remaining_distance': 120,
            'point': [30.0, 60.0],
            'type': 'via',
        }

        expected_fst_resp['route']['points'].insert(0, first_via_point)

    experiments3.add_experiment(
        name='shuttle_control_etags',
        consumers=['shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/polling'}],
            'predicate': {'type': 'true', 'init': {}},
            'applications': [
                {
                    'name': 'taximeter',
                    'version_range': {'from': '9.0.0', 'to': '10.0.0'},
                },
            ],
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'enable': True},
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
                    'pass_via_before_stop': pass_via_before_stop,
                    'remaining_distance': 120,
                    'stops_display_limit': 4,
                    'cyclic_route_points_limit_forward': 4,
                    'cyclic_route_points_limit_back': 0,
                },
            },
        ],
    )

    headers = copy.deepcopy(HEADERS)
    headers['X-Request-Application-Version'] = version

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == expected_fst_resp

    headers['If-None-Match'] = response.headers['ETag']

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=headers,
    )

    if is_etag_enabled:
        assert response.status_code == 304
    else:
        assert response.status_code == 200
        assert response.json() == expected_fst_resp


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic.sql'])
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
            'remaining_distance': 120,
            'point': [37.639896, 55.737345],
            'type': 'stop',
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

    stop_url = 'taximeter://screen/stop_shuttle?shuttle_id=gkZxnYQ73QGqrKyz'

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
        'stops_display_limit': 4,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {'type': 'deeplink', 'url': stop_url},
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'route1',
            'points': [points_resp[idx % 8] for idx in points_range],
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'work_mode_info': {
            'title': 'Режим дохода "Шаттл"',
            'text': (
                'Продолжайте движение по маршруту'
                if has_passengers
                else 'Поиск пассажиров, двигайтесь по маршруту...'
            ),
            'icon': 'bus',
            'action_status': 'en_route',
        },
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

    def _mock():
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

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_resp


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic_on_stop.sql'])
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

    stop_url = 'taximeter://screen/stop_shuttle?shuttle_id=gkZxnYQ73QGqrKyz'

    expected_resp = {
        'stops_display_limit': 5,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {'type': 'deeplink', 'url': stop_url},
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'route1',
            'points': points_resp,
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'work_mode_info': {
            'title': 'Режим дохода "Шаттл"',
            'text': 'Продолжайте движение по маршруту',
            'icon': 'bus',
            'action_status': 'en_route',
        },
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

    def _mock():
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

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_resp


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic_on_last_stop.sql'])
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

    stop_url = 'taximeter://screen/stop_shuttle?shuttle_id=gkZxnYQ73QGqrKyz'

    expected_resp = {
        'stops_display_limit': 2,
        'panel_en_route': {
            'items': [
                {
                    'accent': True,
                    'payload': {'type': 'deeplink', 'url': stop_url},
                    'title': 'Завершить',
                    'type': 'button',
                },
            ],
        },
        'route': {
            'is_cyclic': True,
            'is_dynamic': False,
            'route_name': 'route1',
            'points': points_resp,
        },
        'shuttle_id': 'gkZxnYQ73QGqrKyz',
        'state': 'en_route',
        'work_mode_info': {
            'title': 'Режим дохода "Шаттл"',
            'text': 'Продолжайте движение по маршруту',
            'icon': 'bus',
            'action_status': 'en_route',
        },
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

    def _mock():
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

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/status', headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_resp
