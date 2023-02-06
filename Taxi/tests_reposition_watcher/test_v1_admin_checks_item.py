# pylint: disable=import-only-modules,invalid-name
import datetime

import pytest

from tests_reposition_watcher.utils import select_named

DURATION_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': True},
    'due': '2016-02-07T19:45:00.922+0000',
    'span': 3600,
    'left_time_deadline': 600,
    'left_time_coef': 0.1,
}

ARRIVAL_CHECK = {
    'conditions': {'is_allowed_on_order': False},
    'eta': 300,
    'distance': 400,
    'air_distance': 500,
}

IMMOBILITY_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': False, 'info_push_count': 2, 'warn_push_count': 12},
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

TRANSPORTING_ARRIVAL_CHECK = {
    'conditions': {'is_allowed_on_order': True},
    'config': {'dry_run': True},
}


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
            'SELECT is_allowed_on_order FROM checks.conditions '
            'WHERE condition_id = {}'.format(condition_id),
        )
        if 'is_allowed_on_order' in conditions:
            assert db_conditions[0] == conditions['is_allowed_on_order']

    if 'config' in check_rule:
        assert config_id is not None
        config = check_rule['config']
        db_config = get_existing_row_by_primary_key(
            cursor,
            'SELECT dry_run, info_push_count, warn_push_count '
            'FROM checks.config '
            'WHERE config_id = {}'.format(config_id),
        )
        assert db_config[0] == config['dry_run']
        if 'info_push_count' in config:
            assert db_config[1] == config['info_push_count']
        if 'warn_push_count' in config:
            assert db_config[2] == config['warn_push_count']


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
    assert db_duration_check[3] == datetime.timedelta(
        seconds=duration_check['left_time_deadline'],
    )
    assert db_duration_check[4] == duration_check['left_time_coef']

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


def transporting_arrival_check_validation(
        cursor, transporting_arrival_id, transporting_arrival_check,
):
    db_transporting_arrival_check = get_existing_row_by_primary_key(
        cursor,
        ' SELECT'
        '   condition_id,'
        '   config_id'
        ' FROM checks.transporting_arrival '
        ' WHERE check_id = {}'.format(transporting_arrival_id),
    )

    common_validation(
        cursor,
        db_transporting_arrival_check[0],
        db_transporting_arrival_check[1],
        transporting_arrival_check['conditions'],
    )


@pytest.mark.parametrize(
    'request_body',
    [
        {},
        {
            'duration': DURATION_CHECK,
            'arrival': ARRIVAL_CHECK,
            'surge_arrival': SURGE_ARRIVAL_CHECK,
            'out_of_area': OUT_OF_AREA_CHECK,
            'route': ROUTE_CHECK,
            'immobility': IMMOBILITY_CHECK,
            'transporting_arrival': TRANSPORTING_ARRIVAL_CHECK,
        },
        {
            'arrival': ARRIVAL_CHECK,
            'surge_arrival': SURGE_ARRIVAL_CHECK,
            'out_of_area': OUT_OF_AREA_CHECK,
            'route': ROUTE_CHECK,
            'immobility': IMMOBILITY_CHECK,
            'transporting_arrival': TRANSPORTING_ARRIVAL_CHECK,
        },
        {'arrival': ARRIVAL_CHECK},
        {'arrival': ARRIVAL_CHECK, 'route': ROUTE_CHECK},
    ],
)
@pytest.mark.parametrize('has_submode', [True, False])
@pytest.mark.parametrize('override', [True, False])
@pytest.mark.pgsql('reposition_watcher', files=['modes_zones.sql'])
async def test_put(
        taxi_reposition_watcher,
        pgsql,
        load,
        request_body,
        has_submode,
        override,
):
    zone = '__default__'
    mode_id = '2'
    zone_id = '1'
    submode_id = '1'
    mode = 'poi'
    submode = 'fast'
    submode_opt = f'&submode={submode}' if has_submode else ''
    queries = [load('modes_zones.sql')]
    if override:
        queries.append(load('config_checks.sql'))
    pgsql['reposition_watcher'].apply_queries(queries)
    response = await taxi_reposition_watcher.put(
        f'v1/admin/checks/item?zone={zone}&mode={mode}{submode_opt}',
        json=request_body,
    )
    assert response.status_code == 200
    cursor = pgsql['reposition_watcher'].cursor()
    submode_query = (
        f' AND submode_id = {submode_id}'
        if has_submode
        else ' AND submode_id IS NULL'
    )
    conf = get_existing_row_by_primary_key(
        cursor,
        'SELECT zone_id, mode_id, submode_id, '
        'duration_id, arrival_id, immobility_id, '
        'surge_arrival_id, out_of_area_id, transporting_arrival_id, route_id '
        f'FROM config.checks WHERE mode_id = {mode_id} AND zone_id = {zone_id}'
        f'{submode_query}',
    )

    if 'duration' in request_body:
        duration_check_validation(cursor, conf[3], request_body['duration'])
    else:
        assert conf[3] is None

    if 'arrival' in request_body:
        arrival_check_validation(cursor, conf[4], request_body['arrival'])
    else:
        assert conf[4] is None

    if 'immobility' in request_body:
        immobility_check_validation(
            cursor, conf[5], request_body['immobility'],
        )
    else:
        assert conf[5] is None

    if 'surge_arrival' in request_body:
        surge_arrival_check_validation(
            cursor, conf[6], request_body['surge_arrival'],
        )
    else:
        assert conf[6] is None

    if 'out_of_area' in request_body:
        out_of_area_check_validation(
            cursor, conf[7], request_body['out_of_area'],
        )
    else:
        assert conf[7] is None

    if 'transporting_arrival' in request_body:
        transporting_arrival_check_validation(
            cursor, conf[8], request_body['transporting_arrival'],
        )
    else:
        assert conf[8] is None

    if 'route' in request_body:
        route_check_validation(cursor, conf[9], request_body['route'])
    else:
        assert conf[9] is None


@pytest.mark.parametrize('has_submode', [False, True])
@pytest.mark.pgsql(
    'reposition_watcher', files=['modes_zones.sql', 'config_checks.sql'],
)
async def test_delete(taxi_reposition_watcher, pgsql, has_submode):
    zone = '__default__'
    mode = 'poi'
    submode = 'fast'
    zone_id = 1
    mode_id = 2
    submode_id = 1
    submode_opt = f'&submode={submode}' if has_submode else ''
    submode_cond = f' AND submode_id = {submode_id}' if has_submode else ''
    response = await taxi_reposition_watcher.delete(
        f'v1/admin/checks/item?zone={zone}&mode={mode}{submode_opt}',
    )
    assert response.status_code == 200

    checks = select_named(
        f'SELECT mode_id FROM config.checks WHERE mode_id = {mode_id}'
        f' AND zone_id = {zone_id} {submode_cond}',
        pgsql['reposition_watcher'],
    )
    assert not checks
