# pylint: disable=too-many-lines
import copy
import datetime

import pytest

SESSION_10001 = {
    'park_id': 'some-dbid',
    'driver_profile_id': 'some-uuid',
    'session_id': 10001,
    'session_start': '1986-03-01T00:00:00.0+0000',
    'reposition_source_point': [37.619757, 55.753215],
    'reposition_dest_point': [37.6057, 55.7647],
    'reposition_dest_radius': 12,
    'mode_id': 'home',
    'tariff_class': 'econom',
    'settings_zones_checks': {},
}

SESSION_10005 = {
    'park_id': 'some-dbid',
    'driver_profile_id': 'some-uuid',
    'session_id': 10005,
    'session_start': '1986-03-01T00:00:00.0+0000',
    'reposition_source_point': [37.619757, 55.753215],
    'reposition_dest_point': [38, 56],
    'reposition_dest_radius': 12,
    'mode_id': 'home',
    'tariff_class': 'econom',
    'settings_zones_checks': {},
}

DURATION_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': True},
    'due': '2016-02-07T19:45:00.922+0000',
    'span': 3600,
    'left_time_deadline': 600,
    'left_time_coef': 0.1,
}

DURATION_CHECK2 = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': True},
    'due': '2016-02-07T19:45:00.000+0000',
    'span': 600,
}

ARRIVAL_CHECK = {
    'conditions': {'is_allowed_on_order': False},
    'config': {'dry_run': False},
    'eta': 300,
    'distance': 400,
    'air_distance': 500,
}

ARRIVAL_CHECK_2 = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': True},
    'eta': 600,
    'distance': 700,
    'air_distance': 200,
}

IMMOBILITY_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': False},
    'min_track_speed': 301,
    'position_threshold': 401,
    'max_immobility_time': 501,
}

SURGE_ARRIVAL_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': False},
    'coef_surge': -0.5,
    'min_local_surge': 1.1,
    'min_ride_time': 50,
}

OUT_OF_AREA_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': False, 'info_push_count': 3, 'warn_push_count': 4},
    'min_distance_from_border': 200,
    'time_out_of_area': 150,
}

ROUTE_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'check_interval': 105,
    'max_last_checks_count': 106,
    'max_violations_count': 107,
    'speed_dist_range': {
        'range': {'minimum': 1.2, 'maximum': 6.3},
        'abs_range': {'minimum': 1.5, 'maximum': 3.2},
    },
    'speed_eta_range': {
        'range': {'minimum': 2.5, 'maximum': 8.3},
        'abs_range': {'minimum': 1.8, 'maximum': 39.2},
    },
    'range_checks_compose_operator': 'AND',
    'speed_checks_compose_operator': 'OR',
}

ROUTE_CHECK_2 = copy.deepcopy(ROUTE_CHECK)
ROUTE_CHECK_2['check_interval'] = 205
ROUTE_CHECK_2['speed_dist_range'] = {
    'range': {'minimum': 11.2, 'maximum': 26.3},
    'abs_range': {'minimum': 31.5, 'maximum': 34.2},
}
ROUTE_CHECK_2['config'] = {
    'dry_run': True,
    'info_push_count': 6,
    'warn_push_count': 7,
}


SESSION_10004_WITH_CHECKS = copy.deepcopy(SESSION_10001)
SESSION_10004_WITH_CHECKS['session_id'] = 10004
SESSION_10004_WITH_CHECKS['settings_zones_checks'] = {
    'duration': DURATION_CHECK,
    'arrival': ARRIVAL_CHECK,
    'immobility': IMMOBILITY_CHECK,
    'surge_arrival_local': SURGE_ARRIVAL_CHECK,
    'out_of_area': OUT_OF_AREA_CHECK,
    'route': ROUTE_CHECK,
}

SESSION_10002_WITH_ROUTE_CHECK = copy.deepcopy(SESSION_10001)
SESSION_10002_WITH_ROUTE_CHECK['session_id'] = 10002
SESSION_10002_WITH_ROUTE_CHECK['settings_zones_checks'] = {
    'route': ROUTE_CHECK_2,
}

SESSION_10003_WITH_ARRIVAL_CHECK = copy.deepcopy(SESSION_10001)
SESSION_10003_WITH_ARRIVAL_CHECK['session_id'] = 10003
SESSION_10003_WITH_ARRIVAL_CHECK['settings_zones_checks'] = {
    'arrival': ARRIVAL_CHECK_2,
}

SESSION_10005_DUP_UUID = copy.deepcopy(SESSION_10001)
SESSION_10005_DUP_UUID['session_id'] = 10005

SESSION_10002_CONFIG_CHECKS = copy.deepcopy(SESSION_10001)
SESSION_10002_CONFIG_CHECKS['session_id'] = 10002
SESSION_10002_CONFIG_CHECKS['settings_zones_checks'] = {
    'duration': DURATION_CHECK2,
    'arrival': ARRIVAL_CHECK,
    'immobility': IMMOBILITY_CHECK,
    'out_of_area': OUT_OF_AREA_CHECK,
    'route': ROUTE_CHECK_2,
}


def get_db_str_for_point_array(point):
    return '({},{})'.format(point[0], point[1])


def get_db_str_for_range(range_dict):
    return '({},{})'.format(range_dict['minimum'], range_dict['maximum'])


def get_datetime_from_iso(datetime_iso):
    return datetime.datetime.strptime(
        datetime_iso, '%Y-%m-%dT%H:%M:%S.%f+0000',
    )


def get_existing_row_by_primary_key(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    return rows[0]


def common_validation(cursor, condition_id, config_id, check_rule):
    if 'conditions' in check_rule:
        assert condition_id is not None

        conditions = check_rule['conditions']

        db_conditions = get_existing_row_by_primary_key(
            cursor,
            'SELECT is_allowed_on_order, is_allowed_on_busy '
            'FROM checks.conditions '
            'WHERE condition_id = {}'.format(condition_id),
        )

        if 'is_allowed_on_order' in conditions:
            assert db_conditions[0] == conditions['is_allowed_on_order']
        if 'is_allowed_on_busy' in conditions:
            assert db_conditions[1] == conditions['is_allowed_on_busy']

    if 'config' in check_rule:
        assert config_id is not None

        config = check_rule['config']

        db_config = get_existing_row_by_primary_key(
            cursor,
            f"""
            SELECT
                dry_run,
                info_push_count,
                warn_push_count,
                send_push
            FROM
                checks.config
            WHERE
                config_id = {config_id}
            """,
        )

        assert db_config[0] == config['dry_run']
        if 'info_push_count' in config:
            assert db_config[1] == config['info_push_count']
        if 'warn_push_count' in config:
            assert db_config[2] == config['warn_push_count']
        if 'send_push' in config:
            assert db_config[3] == config['send_push']


def duration_check_validation(cursor, duration_id, duration_check):
    db_duration_check = get_existing_row_by_primary_key(
        cursor,
        ' SELECT'
        '   condition_id,'
        '   due,'
        '   span,'
        '   left_time_deadline,'
        '   left_time_coef,'
        '   config_id'
        ' FROM checks.duration '
        ' WHERE check_id = {}'.format(duration_id),
    )

    assert db_duration_check[1] == get_datetime_from_iso(duration_check['due'])
    assert db_duration_check[2] == datetime.timedelta(
        seconds=duration_check['span'],
    )
    left_time_deadline = (
        datetime.timedelta(seconds=duration_check['left_time_deadline'])
        if 'left_time_deadline' in duration_check
        else None
    )
    left_time_coef = (
        duration_check['left_time_coef']
        if 'left_time_coef' in duration_check
        else None
    )
    assert db_duration_check[3] == left_time_deadline
    assert db_duration_check[4] == left_time_coef

    common_validation(
        cursor,
        db_duration_check[0],
        db_duration_check[5],
        duration_check['conditions'],
    )


def arrival_check_validation(cursor, arrival_id, arrival_check):
    db_arrival_check = get_existing_row_by_primary_key(
        cursor,
        'SELECT condition_id, eta, distance, air_distance, config_id '
        'FROM checks.arrival WHERE check_id = {}'.format(arrival_id),
    )

    assert db_arrival_check[1] == datetime.timedelta(
        seconds=arrival_check['eta'],
    )
    assert db_arrival_check[2] == arrival_check['distance']
    assert db_arrival_check[3] == arrival_check['air_distance']

    common_validation(
        cursor, db_arrival_check[0], db_arrival_check[4], arrival_check,
    )


def immobility_check_validation(cursor, immobility_id, immobility_check):
    db_immobility_check = get_existing_row_by_primary_key(
        cursor,
        'SELECT condition_id, min_track_speed, position_threshold, '
        'max_immobility_time, config_id '
        'FROM checks.immobility WHERE check_id = {}'.format(immobility_id),
    )

    assert db_immobility_check[1] == immobility_check['min_track_speed']
    assert db_immobility_check[2] == immobility_check['position_threshold']
    assert db_immobility_check[3] == datetime.timedelta(
        seconds=immobility_check['max_immobility_time'],
    )

    common_validation(
        cursor,
        db_immobility_check[0],
        db_immobility_check[4],
        immobility_check,
    )


def surge_arrival_check_validation(
        cursor, surge_arrival_id, surge_arrival_check,
):
    db_surge_arriva_check = get_existing_row_by_primary_key(
        cursor,
        'SELECT condition_id, coef_surge, '
        'min_local_surge, min_ride_time, config_id '
        'FROM checks.surge_arrival WHERE check_id = {}'.format(
            surge_arrival_id,
        ),
    )

    assert db_surge_arriva_check[1] == surge_arrival_check['coef_surge']
    assert db_surge_arriva_check[2] == surge_arrival_check['min_local_surge']
    assert db_surge_arriva_check[3] == datetime.timedelta(
        seconds=surge_arrival_check['min_ride_time'],
    )

    common_validation(
        cursor,
        db_surge_arriva_check[0],
        db_surge_arriva_check[4],
        surge_arrival_check,
    )


def out_of_area_check_validation(cursor, out_of_area_id, out_of_area_check):
    db_out_of_area = get_existing_row_by_primary_key(
        cursor,
        'SELECT condition_id, min_distance_from_border, time_out_of_area, '
        'config_id FROM checks.out_of_area WHERE check_id = {}'.format(
            out_of_area_id,
        ),
    )

    assert db_out_of_area[1] == out_of_area_check['min_distance_from_border']
    assert db_out_of_area[2] == datetime.timedelta(
        seconds=out_of_area_check['time_out_of_area'],
    )

    common_validation(
        cursor, db_out_of_area[0], db_out_of_area[3], out_of_area_check,
    )


def route_check_validation(cursor, route_id, route_check):
    db_route = get_existing_row_by_primary_key(
        cursor,
        'SELECT condition_id, check_interval, max_last_checks_count, '
        'max_violations_count, speed_dist_range,'
        'speed_dist_abs_range, speed_eta_range, speed_eta_abs_range, '
        'range_checks_compose_operator, speed_checks_compose_operator,'
        ' config_id FROM checks.route WHERE check_id= {}'.format(route_id),
    )

    assert db_route[1] == datetime.timedelta(
        seconds=route_check['check_interval'],
    )
    assert db_route[2] == route_check['max_last_checks_count']
    assert db_route[3] == route_check['max_violations_count']
    speed_dist_range = route_check['speed_dist_range']
    assert db_route[4] == get_db_str_for_range(speed_dist_range['range'])
    assert db_route[5] == get_db_str_for_range(speed_dist_range['abs_range'])
    speed_eta_range = route_check['speed_eta_range']
    assert db_route[6] == get_db_str_for_range(speed_eta_range['range'])
    assert db_route[7] == get_db_str_for_range(speed_eta_range['abs_range'])
    assert db_route[8] == route_check['range_checks_compose_operator']
    assert db_route[9] == route_check['speed_checks_compose_operator']

    common_validation(cursor, db_route[0], db_route[10], route_check)


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(
    consumers=['reposition-watcher'],
    name='dry_run_checks',
    match={
        'enabled': True,
        'consumers': [{'name': 'reposition-watcher'}],
        'predicate': {
            'type': 'in_set',
            'init': {
                'set_elem_type': 'string',
                'arg_name': 'driver_id',
                'set': ['some-dbid_some-uuid'],
            },
        },
    },
    clauses=[
        {
            'title': 'mode_poi',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set_elem_type': 'string',
                    'arg_name': 'zone',
                    'set': ['will_not_match_exp'],
                },
            },
            'value': {
                'set_true': ['route', 'surge_arrival', 'out_of_area'],
                'set_false': ['duration'],
            },
        },
    ],
)
@pytest.mark.parametrize(
    'request_body',
    [
        SESSION_10001,
        SESSION_10002_WITH_ROUTE_CHECK,
        SESSION_10003_WITH_ARRIVAL_CHECK,
        SESSION_10004_WITH_CHECKS,
    ],
)
@pytest.mark.nofilldb()
async def test_v1_service_session_add(
        taxi_reposition_watcher, pgsql, request_body,
):
    request = request_body
    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=request,
    )
    assert response.status_code == 200
    cursor = pgsql['reposition_watcher'].cursor()
    session = get_existing_row_by_primary_key(
        cursor,
        'SELECT dbid_uuid, start, reposition_source_point, '
        'reposition_dest_point,'
        'duration_id, arrival_id, immobility_id, '
        'surge_arrival_id, out_of_area_id, route_id '
        'FROM state.sessions WHERE session_id = {}'.format(
            request['session_id'],
        ),
    )
    assert session[0] == '({},{})'.format(
        request['park_id'], request['driver_profile_id'],
    )

    assert session[1] == get_datetime_from_iso(request['session_start'])
    assert session[2] == get_db_str_for_point_array(
        request['reposition_source_point'],
    )
    assert session[3] == get_db_str_for_point_array(
        request['reposition_dest_point'],
    )

    settings_zones_checks = request['settings_zones_checks']
    if 'duration' in settings_zones_checks:
        duration_check_validation(
            cursor, session[4], settings_zones_checks['duration'],
        )
    else:
        assert session[4] is None

    if 'arrival' in settings_zones_checks:
        arrival_check_validation(
            cursor, session[5], settings_zones_checks['arrival'],
        )
    else:
        assert session[5] is None

    if 'immobility' in settings_zones_checks:
        immobility_check_validation(
            cursor, session[6], settings_zones_checks['immobility'],
        )
    else:
        assert session[6] is None

    if 'surge_arrival_local' in settings_zones_checks:
        surge_arrival_check_validation(
            cursor, session[7], settings_zones_checks['surge_arrival_local'],
        )
    else:
        assert session[7] is None

    if 'out_of_area' in settings_zones_checks:
        out_of_area_check_validation(
            cursor, session[8], settings_zones_checks['out_of_area'],
        )
    else:
        assert session[8] is None

    if 'route' in settings_zones_checks:
        route_check_validation(
            cursor, session[9], settings_zones_checks['route'],
        )
    else:
        assert session[9] is None

    state_checks = get_existing_row_by_primary_key(
        cursor,
        'SELECT session_id FROM state.checks '
        'WHERE session_id = {}'.format(request['session_id']),
    )
    assert state_checks[0] == request['session_id']


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.pgsql('reposition_watcher', files=['modes_zones.sql'])
@pytest.mark.experiments3(
    consumers=['reposition-watcher'],
    name='dry_run_checks',
    match={
        'enabled': True,
        'consumers': [{'name': 'reposition-watcher'}],
        'predicate': {
            'type': 'in_set',
            'init': {
                'set_elem_type': 'string',
                'arg_name': 'driver_id',
                'set': ['some-dbid_some-uuid'],
            },
        },
    },
    clauses=[
        {
            'title': 'mode_poi',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set_elem_type': 'string',
                    'arg_name': 'zone',
                    'set': ['moscow'],
                },
            },
            'value': {
                'set_true': ['route', 'surge_arrival', 'out_of_area'],
                'set_false': ['duration'],
            },
        },
    ],
)
@pytest.mark.nofilldb()
async def test_session_add_dry_run_experiment(taxi_reposition_watcher, pgsql):
    request = copy.deepcopy(SESSION_10004_WITH_CHECKS)
    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=request,
    )
    assert response.status_code == 200

    settings_zones_checks = request['settings_zones_checks']
    settings_zones_checks['duration']['config']['dry_run'] = False
    settings_zones_checks['surge_arrival_local']['config']['dry_run'] = True
    settings_zones_checks['out_of_area']['config']['dry_run'] = True
    settings_zones_checks['route']['config'] = {'dry_run': True}

    cursor = pgsql['reposition_watcher'].cursor()
    session = get_existing_row_by_primary_key(
        cursor,
        'SELECT dbid_uuid, start, reposition_source_point, '
        'reposition_dest_point,'
        'duration_id, arrival_id, immobility_id, '
        'surge_arrival_id, out_of_area_id, route_id '
        'FROM state.sessions WHERE session_id = {}'.format(
            request['session_id'],
        ),
    )
    assert session[0] == '({},{})'.format(
        request['park_id'], request['driver_profile_id'],
    )

    assert session[1] == get_datetime_from_iso(request['session_start'])
    assert session[2] == get_db_str_for_point_array(
        request['reposition_source_point'],
    )
    assert session[3] == get_db_str_for_point_array(
        request['reposition_dest_point'],
    )

    if 'duration' in settings_zones_checks:
        duration_check_validation(
            cursor, session[4], settings_zones_checks['duration'],
        )
    else:
        assert session[4] is None

    if 'arrival' in settings_zones_checks:
        arrival_check_validation(
            cursor, session[5], settings_zones_checks['arrival'],
        )
    else:
        assert session[5] is None

    if 'immobility' in settings_zones_checks:
        immobility_check_validation(
            cursor, session[6], settings_zones_checks['immobility'],
        )
    else:
        assert session[6] is None

    if 'surge_arrival_local' in settings_zones_checks:
        surge_arrival_check_validation(
            cursor, session[7], settings_zones_checks['surge_arrival_local'],
        )
    else:
        assert session[7] is None

    if 'out_of_area' in settings_zones_checks:
        out_of_area_check_validation(
            cursor, session[8], settings_zones_checks['out_of_area'],
        )
    else:
        assert session[8] is None

    if 'route' in settings_zones_checks:
        route_check_validation(
            cursor, session[9], settings_zones_checks['route'],
        )
    else:
        assert session[9] is None

    state_checks = get_existing_row_by_primary_key(
        cursor,
        'SELECT session_id FROM state.checks '
        'WHERE session_id = {}'.format(request['session_id']),
    )
    assert state_checks[0] == request['session_id']


@pytest.mark.pgsql('reposition_watcher', files=['modes_zones.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_session_add_send_push_experiment(
        taxi_reposition_watcher, pgsql, experiments3,
):
    experiments3.add_config(
        consumers=['reposition-watcher/send-push-overrides'],
        name='reposition_watcher_send_push_overrides',
        match={
            'enabled': True,
            'consumers': [{'name': 'reposition-watcher/send-push-overrides'}],
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set_elem_type': 'string',
                    'arg_name': 'park_driver_profile_id',
                    'set': ['some-dbid_some-uuid'],
                },
            },
        },
        clauses=[
            {
                'title': 'driver-fix',
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'set_elem_type': 'string',
                        'arg_name': 'work_mode',
                        'set': ['driver-fix'],
                    },
                },
                'value': {'__default__': False, 'duration': True},
            },
        ],
        default_value={'__default__': True},
    )

    request = copy.deepcopy(SESSION_10004_WITH_CHECKS)
    request['work_mode'] = 'driver-fix'

    settings_zones_checks = request['settings_zones_checks']

    settings_zones_checks['duration']['config']['send_push'] = False
    settings_zones_checks['surge_arrival_local']['config']['send_push'] = True
    settings_zones_checks['route']['config'] = {
        'send_push': True,
        'dry_run': False,
    }

    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=request,
    )
    assert response.status_code == 200

    settings_zones_checks['duration']['config']['send_push'] = True
    settings_zones_checks['arrival']['config']['send_push'] = False
    settings_zones_checks['immobility']['config']['send_push'] = False
    settings_zones_checks['surge_arrival_local']['config']['send_push'] = False
    settings_zones_checks['out_of_area']['config']['send_push'] = False
    settings_zones_checks['route']['config']['send_push'] = False

    cursor = pgsql['reposition_watcher'].cursor()
    session = get_existing_row_by_primary_key(
        cursor,
        f"""
        SELECT
            dbid_uuid,
            start,
            reposition_source_point,
            reposition_dest_point,
            duration_id,
            arrival_id,
            immobility_id,
            surge_arrival_id,
            out_of_area_id,
            route_id
        FROM
            state.sessions
        WHERE
            session_id = {request['session_id']}
        """,
    )

    assert (
        session[0] == f'({request["park_id"]},{request["driver_profile_id"]})'
    )
    assert session[1] == get_datetime_from_iso(request['session_start'])
    assert session[2] == get_db_str_for_point_array(
        request['reposition_source_point'],
    )
    assert session[3] == get_db_str_for_point_array(
        request['reposition_dest_point'],
    )

    if 'duration' in settings_zones_checks:
        duration_check_validation(
            cursor, session[4], settings_zones_checks['duration'],
        )
    else:
        assert session[4] is None

    if 'arrival' in settings_zones_checks:
        arrival_check_validation(
            cursor, session[5], settings_zones_checks['arrival'],
        )
    else:
        assert session[5] is None

    if 'immobility' in settings_zones_checks:
        immobility_check_validation(
            cursor, session[6], settings_zones_checks['immobility'],
        )
    else:
        assert session[6] is None

    if 'surge_arrival_local' in settings_zones_checks:
        surge_arrival_check_validation(
            cursor, session[7], settings_zones_checks['surge_arrival_local'],
        )
    else:
        assert session[7] is None

    if 'out_of_area' in settings_zones_checks:
        out_of_area_check_validation(
            cursor, session[8], settings_zones_checks['out_of_area'],
        )
    else:
        assert session[8] is None

    if 'route' in settings_zones_checks:
        route_check_validation(
            cursor, session[9], settings_zones_checks['route'],
        )
    else:
        assert session[9] is None

    state_checks = get_existing_row_by_primary_key(
        cursor,
        f"""
        SELECT
            session_id
        FROM
            state.checks
        WHERE
            session_id = {request['session_id']}
        """,
    )
    assert state_checks[0] == request['session_id']


@pytest.mark.pgsql(
    'reposition_watcher',
    files=[
        'check_configs.sql',
        'conditions.sql',
        'check_rules.sql',
        'sessions.sql',
    ],
)
async def test_v1_service_session_add_duplicate(
        taxi_reposition_watcher, pgsql,
):
    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=SESSION_10002_WITH_ROUTE_CHECK,
    )
    assert response.status_code == 200

    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=SESSION_10002_WITH_ROUTE_CHECK,
    )
    assert response.status_code == 200

    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=SESSION_10005_DUP_UUID,
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': 'EXISTING_SESSION',
        'message': 'Driver is being watched already',
        'existing_session_id': 10002,
    }


@pytest.mark.nofilldb()
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    'has_config_checks,enable_exp', [(True, False), (True, True)],
)
@pytest.mark.parametrize('has_send_push', [True, False])
@pytest.mark.parametrize('has_subzone', [True, False])
@pytest.mark.parametrize('is_offer_only', [True, False])
async def test_v1_service_session_add_with_config_checks(
        taxi_reposition_watcher,
        pgsql,
        load,
        has_config_checks,
        enable_exp,
        has_send_push,
        has_subzone,
        is_offer_only,
        experiments3,
        testpoint,
):
    @testpoint('session_add::compare_failed')
    def compare_failed(data):
        pass

    experiments3.add_experiment(
        consumers=['reposition-watcher'],
        name='watcher_config_checks',
        match={
            'enabled': enable_exp,
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set_elem_type': 'string',
                    'arg_name': 'zone',
                    'set': ['moscow'],
                },
            },
        },
        clauses=[
            {
                'name': 'mode_poi',
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'set_elem_type': 'string',
                        'arg_name': 'zone',
                        'set': ['moscow'],
                    },
                },
                'value': {'dry_run': False},
            },
        ],
    )
    queries = [load('modes_zones.sql'), load('config_checks.sql')]
    if has_subzone:
        queries.append(load('zone_cao.sql'))
    if has_config_checks:
        pgsql['reposition_watcher'].apply_queries(queries)

    request = copy.deepcopy(SESSION_10002_CONFIG_CHECKS)
    if has_send_push:
        request['send_push'] = True
    if is_offer_only:
        request['settings_zones_checks']['duration'] = copy.deepcopy(
            DURATION_CHECK,
        )
        cursor = pgsql['reposition_watcher'].conn.cursor()
        cursor.execute(
            'UPDATE config.modes '
            'SET offer_only = true '
            'WHERE mode_name = \'home\'',
        )
    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=request,
    )
    assert response.status_code == 200
    cursor = pgsql['reposition_watcher'].cursor()
    session = get_existing_row_by_primary_key(
        cursor,
        'SELECT dbid_uuid, start, reposition_source_point, '
        'reposition_dest_point,'
        'duration_id, arrival_id, immobility_id, '
        'surge_arrival_id, out_of_area_id, route_id, send_push '
        'FROM state.sessions WHERE session_id = {}'.format(
            request['session_id'],
        ),
    )
    assert session[0] == '({},{})'.format(
        request['park_id'], request['driver_profile_id'],
    )

    assert session[1] == get_datetime_from_iso(request['session_start'])
    assert session[2] == get_db_str_for_point_array(
        request['reposition_source_point'],
    )
    assert session[3] == get_db_str_for_point_array(
        request['reposition_dest_point'],
    )

    settings_zones_checks = request['settings_zones_checks']
    duration_check_validation(
        cursor, session[4], settings_zones_checks['duration'],
    )
    arrival_check_validation(
        cursor, session[5], settings_zones_checks['arrival'],
    )
    immobility_check_validation(
        cursor, session[6], settings_zones_checks['immobility'],
    )
    out_of_area_check_validation(
        cursor, session[8], settings_zones_checks['out_of_area'],
    )
    route_check_validation(cursor, session[9], settings_zones_checks['route'])
    if has_config_checks and enable_exp:
        # arrival_id
        assert session[5] == 1602
        # immobility_id
        assert session[6] == 1702
        # surge_arrival_id
        assert not session[7]
        # out_of_area_id
        assert session[8] == 1901

    assert session[10] is None
    assert compare_failed.times_called == 0

    state_checks = get_existing_row_by_primary_key(
        cursor,
        'SELECT session_id, immobility_state_id, '
        'out_of_area_state_id, route_state_id FROM state.checks '
        'WHERE session_id = {}'.format(request['session_id']),
    )
    assert state_checks[0] == request['session_id']
    assert state_checks[1]
    assert state_checks[2]
    assert state_checks[3]


@pytest.mark.pgsql(
    'reposition_watcher', files=['modes_zones.sql', 'config_checks.sql'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_v1_service_session_add_db_overrides(
        taxi_reposition_watcher, pgsql, load, experiments3,
):
    experiments3.add_experiment(
        consumers=['reposition-watcher'],
        name='watcher_config_checks',
        match={'enabled': True, 'predicate': {'type': 'true', 'init': {}}},
        clauses=[
            {
                'name': 'true',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'dry_run': False},
            },
        ],
    )

    experiments3.add_config(
        consumers=['reposition-watcher/send-push-overrides'],
        name='reposition_watcher_send_push_overrides',
        match={
            'enabled': True,
            'consumers': [{'name': 'reposition-watcher/send-push-overrides'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'true',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'arrival': True, 'immobility': False},
            },
        ],
        default_value={},
    )

    request = copy.deepcopy(SESSION_10002_CONFIG_CHECKS)
    request['settings_zones_checks'] = {}  # to pick'em from DB

    response = await taxi_reposition_watcher.post(
        'v1/service/session/add', json=request,
    )

    assert response.status_code == 200

    cursor = pgsql['reposition_watcher'].cursor()
    session = get_existing_row_by_primary_key(
        cursor,
        'SELECT dbid_uuid, start, reposition_source_point, '
        'reposition_dest_point,'
        'duration_id, arrival_id, immobility_id, '
        'surge_arrival_id, out_of_area_id, route_id, send_push '
        'FROM state.sessions WHERE session_id = {}'.format(
            request['session_id'],
        ),
    )

    assert session[0] == '({},{})'.format(
        request['park_id'], request['driver_profile_id'],
    )

    assert session[1] == get_datetime_from_iso(request['session_start'])
    assert session[2] == get_db_str_for_point_array(
        request['reposition_source_point'],
    )
    assert session[3] == get_db_str_for_point_array(
        request['reposition_dest_point'],
    )

    # duration_id
    assert session[4] == 1302
    # arrival_id
    assert session[5] and session[5] != 1602
    # immobility_id
    assert session[6] and session[6] != 1702
    # surge_arrival_id
    assert not session[7]
    # out_of_area_id
    assert session[8] == 1901
    # route_id
    assert session[9] == 2001

    settings_zones_checks = request['settings_zones_checks']

    settings_zones_checks['duration'] = {
        'conditions': {'is_allowed_on_order': True},
        'config': {'dry_run': True, 'send_push': False},
        'due': '2016-02-07T19:45:00.000+0000',
        'span': 600,
    }

    settings_zones_checks['arrival'] = {
        'conditions': {'is_allowed_on_order': False},
        'config': {'dry_run': False, 'send_push': True},
        'eta': 300,
        'distance': 400,
        'air_distance': 500,
    }

    settings_zones_checks['immobility'] = {
        'conditions': {'is_allowed_on_order': True},
        'config': {'dry_run': False, 'send_push': False},
        'min_track_speed': 301,
        'position_threshold': 401,
        'max_immobility_time': 501,
    }

    settings_zones_checks['out_of_area'] = {
        'conditions': {'is_allowed_on_order': True},
        'config': {
            'dry_run': False,
            'info_push_count': 3,
            'warn_push_count': 4,
            'send_push': True,
        },
        'min_distance_from_border': 200,
        'time_out_of_area': 150,
    }

    settings_zones_checks['route'] = copy.deepcopy(ROUTE_CHECK_2)
    settings_zones_checks['route']['config']['send_push'] = True

    duration_check_validation(
        cursor, session[4], settings_zones_checks['duration'],
    )
    arrival_check_validation(
        cursor, session[5], settings_zones_checks['arrival'],
    )

    immobility_check_validation(
        cursor, session[6], settings_zones_checks['immobility'],
    )

    out_of_area_check_validation(
        cursor, session[8], settings_zones_checks['out_of_area'],
    )

    route_check_validation(cursor, session[9], settings_zones_checks['route'])

    assert session[10] is None  # send_push

    state_checks = get_existing_row_by_primary_key(
        cursor,
        'SELECT session_id, immobility_state_id, '
        'out_of_area_state_id, route_state_id FROM state.checks '
        'WHERE session_id = {}'.format(request['session_id']),
    )

    assert state_checks[0] == request['session_id']
    assert state_checks[1]
    assert state_checks[2]
    assert state_checks[3]
