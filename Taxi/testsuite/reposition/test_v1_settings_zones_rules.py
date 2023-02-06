import datetime

import pytest

from .reposition_select import select_named
from .reposition_select import select_table


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_get_empty_checks(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/rules?zone=__default__')
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_zone_not_found(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/rules?zone=__default__')
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Zone \'__default__\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'submodes_home.sql',
        'zone_default.sql',
        'check_rules.sql',
        'simple_checks.sql',
    ],
)
def test_get(taxi_reposition):
    durations = [
        {
            'duration': 300,
            'left_time_deadline': 600,
            'left_time_coef': 0.1,
            'dry_run': False,
        },
        {
            'duration': 200,
            'left_time_deadline': 300,
            'left_time_coef': 0.5,
            'dry_run': False,
        },
    ]
    arrivals = [
        {'eta': 30, 'distance': 50, 'air_distance': 10, 'dry_run': False},
        {'eta': 60, 'distance': 100, 'dry_run': False},
    ]
    immobilities = [
        {
            'min_track_speed': 12,
            'position_threshold': 4,
            'max_immobility_time': 90,
            'dry_run': False,
        },
        {
            'min_track_speed': 15,
            'position_threshold': 6,
            'max_immobility_time': 80,
            'dry_run': False,
        },
    ]
    antisurge_arrival = [
        {
            'coef_surge': 0.9,
            'dry_run': False,
            'min_dest_surge': 1.2,
            'min_ride_time': 50,
        },
        {
            'coef_surge': 0.1,
            'dry_run': False,
            'min_dest_surge': 1.8,
            'min_ride_time': 80,
        },
    ]
    surge_arrival = [
        {
            'time_coeff': 0.9,
            'surge_arrival_coef': 0.9,
            'min_arrival_surge': 1.1,
            'min_arrival_eta': 50,
            'dry_run': False,
        },
        {
            'time_coeff': 0.1,
            'surge_arrival_coef': 0.1,
            'min_arrival_surge': 1.0,
            'min_arrival_eta': 80,
            'dry_run': False,
        },
    ]
    surge_arrival_local = [
        {
            'coef_surge': 0.9,
            'dry_run': True,
            'min_local_surge': 1.1,
            'min_ride_time': 50,
        },
        {
            'coef_surge': 0.9,
            'dry_run': True,
            'min_local_surge': 1.1,
            'min_ride_time': 50,
        },
    ]

    out_of_area = [
        {
            'first_warnings': 1,
            'last_warnings': 3,
            'min_distance_from_border': 50,
            'time_out_of_area': 40,
            'dry_run': False,
        },
        {
            'first_warnings': 0,
            'last_warnings': 10,
            'min_distance_from_border': 30,
            'time_out_of_area': 90,
            'dry_run': False,
        },
    ]
    route = [
        {
            'check_interval': 45,
            'max_last_checks_count': 5,
            'max_violations_count': 3,
            'first_warnings': 1,
            'last_warnings': 2,
            'speed_dist_range': {'maximum': -2.0},
            'speed_dist_abs_range': {'minimum': 0.0, 'maximum': 2.0},
            'speed_eta_range': {'maximum': 10.0},
            'speed_eta_abs_range': {'minimum': 0.0, 'maximum': 4.0},
            'range_checks_compose_operator': 'AND',
            'speed_checks_compose_operator': 'OR',
            'dry_run': False,
        },
        {
            'check_interval': 45,
            'max_last_checks_count': 3,
            'max_violations_count': 2,
            'first_warnings': 1,
            'last_warnings': 2,
            'speed_dist_range': {'maximum': -5.0},
            'speed_dist_abs_range': {'minimum': 0.0, 'maximum': 5.0},
            'speed_eta_range': {'maximum': 30.0},
            'speed_eta_abs_range': {'minimum': 0.0, 'maximum': 10.0},
            'range_checks_compose_operator': 'OR',
            'speed_checks_compose_operator': 'AND',
            'dry_run': False,
        },
    ]
    transporting_arrival = [{'dry_run': True}, {'dry_run': False}]
    response = taxi_reposition.get('/v1/settings/zones/rules?zone=__default__')
    assert response.status_code == 200
    assert response.json() == {
        'home': {
            'checks': {
                'duration': durations[0],
                'arrival': arrivals[0],
                'immobility': immobilities[0],
                'antisurge_arrival': antisurge_arrival[0],
                'surge_arrival': surge_arrival[0],
                'surge_arrival_local': surge_arrival_local[1],
                'out_of_area': out_of_area[0],
                'route': route[0],
                'transporting_arrival': transporting_arrival[0],
            },
            'submodes': {
                'fast': {
                    'checks': {
                        'duration': durations[0],
                        'arrival': arrivals[1],
                        'immobility': immobilities[0],
                        'surge_arrival_local': surge_arrival_local[0],
                        'transporting_arrival': transporting_arrival[0],
                    },
                },
                'slow': {
                    'checks': {
                        'duration': durations[1],
                        'arrival': arrivals[1],
                        'immobility': immobilities[1],
                        'antisurge_arrival': antisurge_arrival[1],
                        'surge_arrival': surge_arrival[1],
                        'surge_arrival_local': surge_arrival_local[1],
                        'out_of_area': out_of_area[1],
                        'route': route[1],
                        'transporting_arrival': transporting_arrival[1],
                    },
                },
            },
        },
    }


@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_put_mode_not_found(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/rules?mode=home&zone=__default__',
        {
            'checks': {
                'duration': {'duration': 1234},
                'arrival': {'eta': 30, 'distance': 500},
                'immobility': {
                    'min_track_speed': 12,
                    'position_threshold': 4,
                    'max_immobility_time': 90,
                    'dry_run': False,
                },
                'surge_arrival': {
                    'time_coeff': 0.9,
                    'surge_arrival_coef': 0.9,
                    'min_arrival_surge': 1.1,
                    'min_arrival_eta': 50,
                    'dry_run': False,
                },
            },
        },
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
def test_put_mode_not_offer_only(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/rules?mode=home&zone=__default__',
        {
            'checks': {
                'duration': {'duration': 1234},
                'arrival': {'eta': 30, 'distance': 500},
                'immobility': {
                    'min_track_speed': 12,
                    'position_threshold': 4,
                    'max_immobility_time': 90,
                    'dry_run': False,
                },
                'surge_arrival': {
                    'time_coeff': 0.9,
                    'surge_arrival_coef': 0.9,
                    'min_arrival_surge': 1.1,
                    'min_arrival_eta': 50,
                    'dry_run': False,
                },
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'Surge arrival is applied for backend-only mode'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
def test_put_submode_not_found(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/rules?mode=home&submode=fast&zone=__default__',
        {
            'checks': {
                'duration': {'duration': 1234},
                'arrival': {'eta': 30, 'distance': 500},
                'immobility': {
                    'min_track_speed': 12,
                    'position_threshold': 4,
                    'max_immobility_time': 90,
                    'dry_run': False,
                },
            },
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Pair mode \'home\' and submode \'fast\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'submodes_home.sql'])
def test_put_zone_not_found(taxi_reposition, submode):
    request_add = '&submode=fast' if submode is True else ''
    response = taxi_reposition.put(
        '/v1/settings/zones/rules?mode=home&zone=__default__' + request_add,
        {
            'checks': {
                'duration': {'duration': 1234},
                'arrival': {'eta': 30, 'distance': 500},
                'immobility': {
                    'min_track_speed': 12,
                    'position_threshold': 4,
                    'max_immobility_time': 90,
                    'dry_run': False,
                },
                'surge_arrival': {
                    'time_coeff': 0.9,
                    'surge_arrival_coef': 0.9,
                    'min_arrival_surge': 1.1,
                    'min_arrival_eta': 50,
                    'dry_run': False,
                },
            },
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Zone \'__default__\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.parametrize('duration', [False, True])
@pytest.mark.parametrize('arrival', [None, {}, {'straight'}])
@pytest.mark.parametrize('immobility', [False, True])
@pytest.mark.parametrize('antisurge_arrival', [False, True])
@pytest.mark.parametrize('surge_arrival_local', [False, True])
@pytest.mark.parametrize('out_of_area', [False, True])
@pytest.mark.parametrize('route', [False, True])
@pytest.mark.parametrize('transporting_arrival', [False, True])
@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.parametrize('conditions', [False, True])
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_surge.sql',
        'mode_my_district.sql',
        'submodes_surge.sql',
        'zone_default.sql',
    ],
)
def test_put(
        taxi_reposition,
        pgsql,
        mockserver,
        config,
        duration,
        arrival,
        immobility,
        antisurge_arrival,
        surge_arrival_local,
        out_of_area,
        route,
        transporting_arrival,
        submode,
        conditions,
):
    @mockserver.json_handler('/reposition_watcher/v1/admin/checks/item')
    def mock_reposition_watcher(request):
        return mockserver.make_response('{}', status=200)

    replication_enabled = submode or conditions
    config.set_values(
        dict(REPOSITION_CHECKS_REPLICATION_ENABLED=replication_enabled),
    )

    request_add = (
        '&submode=well' if submode is True and not out_of_area else ''
    )
    submode_id = 3 if submode is True and not out_of_area else None
    duration_id = None
    arrival_id = None
    immobility_id = None
    antisurge_arrival_id = None
    surge_arrival_local_id = None
    out_of_area_id = None
    route_id = None
    transporting_arrival_id = None
    air_distance = None
    query = {'checks': {}}
    if duration and not out_of_area:
        duration_id = 1
        query['checks']['duration'] = {
            'duration': 1234,
            'left_time_deadline': 600,
            'left_time_coef': 0.1,
            'dry_run': False,
        }
    if arrival and not out_of_area:
        arrival_id = 1
        query['checks']['arrival'] = {
            'eta': 30,
            'distance': 500,
            'dry_run': False,
        }
        if 'straight' in arrival:
            air_distance = 10
            query['checks']['arrival']['air_distance'] = air_distance
    if immobility and not out_of_area:
        immobility_id = 1
        query['checks']['immobility'] = {
            'min_track_speed': 11,
            'position_threshold': 5,
            'max_immobility_time': 89,
            'dry_run': False,
        }
    if antisurge_arrival and not out_of_area:
        antisurge_arrival_id = 1
        query['checks']['antisurge_arrival'] = {
            'coef_surge': 0.9,
            'min_dest_surge': 1.1,
            'min_ride_time': 50,
            'dry_run': False,
        }
    if surge_arrival_local and not out_of_area:
        surge_arrival_local_id = 1
        query['checks']['surge_arrival_local'] = {
            'coef_surge': 0.9,
            'min_local_surge': 1.1,
            'min_ride_time': 50,
            'dry_run': False,
        }
    if out_of_area:
        out_of_area_id = 1
        query['checks']['out_of_area'] = {
            'first_warnings': 2,
            'last_warnings': 4,
            'min_distance_from_border': 55,
            'time_out_of_area': 42,
            'dry_run': False,
        }
    if route and not out_of_area:
        route_id = 1
        query['checks']['route'] = {
            'check_interval': 45,
            'max_last_checks_count': 5,
            'max_violations_count': 3,
            'first_warnings': 1,
            'last_warnings': 2,
            'speed_dist_range': {'maximum': -2.0},
            'speed_dist_abs_range': {'minimum': 0.0, 'maximum': 2.0},
            'speed_eta_range': {'maximum': 10.0},
            'speed_eta_abs_range': {'minimum': 0.0, 'maximum': 4.0},
            'range_checks_compose_operator': 'AND',
            'speed_checks_compose_operator': 'OR',
            'dry_run': False,
        }
    if transporting_arrival and not out_of_area:
        transporting_arrival_id = 1
        query['checks']['transporting_arrival'] = {'dry_run': False}

    if conditions:
        conditions_checks = []
        if duration and not out_of_area:
            conditions_checks.append('duration')
        if arrival and not out_of_area:
            conditions_checks.append('arrival')
        if antisurge_arrival and not out_of_area:
            conditions_checks.append('antisurge_arrival')
        if surge_arrival_local and not out_of_area:
            conditions_checks.append('surge_arrival_local')
        if immobility and not out_of_area:
            conditions_checks.append('immobility')
        if out_of_area:
            conditions_checks.append('out_of_area')
        if route and not out_of_area:
            conditions_checks.append('route')
        if transporting_arrival and not out_of_area:
            conditions_checks.append('transporting_arrival')

        for check in conditions_checks:
            query['checks'][check]['conditions'] = {
                'is_allowed_on_order': True,
                'is_allowed_on_busy': True,
            }
    response = taxi_reposition.put(
        '/v1/settings/zones/rules?mode={}&zone=__default__{}'.format(
            'my_district' if out_of_area else 'surge', request_add,
        ),
        query,
    )
    assert response.status_code == 200
    assert mock_reposition_watcher.times_called == (
        1 if replication_enabled else 0
    )

    rows = select_table(
        'check_rules.duration', 'duration_id', pgsql['reposition'],
    )
    if duration and not out_of_area:
        assert rows == [
            (
                duration_id,
                None,
                datetime.timedelta(0, 1234),
                False,
                datetime.timedelta(seconds=600),
                0.1,
            ),
        ]
    else:
        assert rows == []

    rows = select_table(
        'check_rules.arrival', 'arrival_id', pgsql['reposition'],
    )
    if arrival and not out_of_area:
        assert rows == [
            (arrival_id, 500, datetime.timedelta(0, 30), air_distance, False),
        ]
    else:
        assert rows == []

    rows = select_table(
        'check_rules.immobility', 'immobility_id', pgsql['reposition'],
    )
    if immobility and not out_of_area:
        assert rows == [
            (immobility_id, 11, 5, datetime.timedelta(0, 89), False),
        ]
    else:
        assert rows == []

    rows = select_table(
        'check_rules.antisurge_arrival',
        'antisurge_arrival_id',
        pgsql['reposition'],
    )
    if antisurge_arrival and not out_of_area:
        assert rows == [
            (antisurge_arrival_id, 0.9, 1.1, datetime.timedelta(0, 50), False),
        ]
    else:
        assert rows == []

    rows = select_table(
        'check_rules.surge_arrival_local',
        'surge_arrival_id',
        pgsql['reposition'],
    )
    if surge_arrival_local and not out_of_area:
        assert rows == [
            (
                surge_arrival_local_id,
                0.9,
                1.1,
                datetime.timedelta(0, 50),
                False,
            ),
        ]
    else:
        assert rows == []

    rows = select_table(
        'check_rules.out_of_area', 'out_of_area_id', pgsql['reposition'],
    )
    if out_of_area:
        assert rows == [
            (out_of_area_id, 2, 4, 55, datetime.timedelta(0, 42), False),
        ]
    else:
        assert rows == []

    rows = select_table('check_rules.route', 'route_id', pgsql['reposition'])
    if route and not out_of_area:
        assert rows == [
            (
                route_id,
                datetime.timedelta(0, 45),
                5,
                3,
                1,
                2,
                '(-Infinity,-2)',
                '(0,2)',
                '(-Infinity,10)',
                '(0,4)',
                'AND',
                'OR',
                False,
            ),
        ]
    else:
        assert rows == []

    rows = select_table(
        'check_rules.transporting_arrival',
        'transporting_arrival_id',
        pgsql['reposition'],
    )
    if transporting_arrival and not out_of_area:
        assert rows == [(transporting_arrival_id, False)]
    else:
        assert rows == []

    if conditions:
        conditions_checks = []
        if duration and not out_of_area:
            conditions_checks.append(('duration', duration_id))
        if arrival and not out_of_area:
            conditions_checks.append(('arrival', arrival_id))
        if antisurge_arrival and not out_of_area:
            conditions_checks.append(
                ('antisurge_arrival', antisurge_arrival_id),
            )
        if surge_arrival_local and not out_of_area:
            conditions_checks.append(
                ('surge_arrival_local', surge_arrival_local_id),
            )
        if immobility and not out_of_area:
            conditions_checks.append(('immobility', immobility_id))
        if out_of_area:
            conditions_checks.append(('out_of_area', out_of_area_id))
        if route and not out_of_area:
            conditions_checks.append(('route', route_id))
        if transporting_arrival and not out_of_area:
            conditions_checks.append(
                ('transporting_arrival', transporting_arrival_id),
            )

        for check, check_id in conditions_checks:
            id_field = '{}_id'.format(check)
            rows = select_named(
                'SELECT {}, is_allowed_on_order, is_allowed_on_busy'
                ' from check_rules.conditions'
                ' WHERE {} = {}'.format(id_field, id_field, check_id),
                pgsql['reposition'],
            )
            assert rows == [
                {
                    id_field: check_id,
                    'is_allowed_on_order': True,
                    'is_allowed_on_busy': True,
                },
            ]

    rows = select_table('config.check_rules', 'zone_id', pgsql['reposition'])
    assert rows == [
        (
            4 if out_of_area else 3,
            1,
            duration_id,
            arrival_id,
            immobility_id,
            submode_id,
            None,
            out_of_area_id,
            route_id,
            surge_arrival_local_id,
            transporting_arrival_id,
            antisurge_arrival_id,
        ),
    ]


@pytest.mark.nofilldb()
@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.parametrize('conditions', [False, True])
@pytest.mark.parametrize('idx', range(0, 32))
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_surge.sql',
        'mode_my_district.sql',
        'submodes_surge.sql',
        'zone_default.sql',
        'check_rules.sql',
        'submode_checks.sql',
    ],
)
def test_put_override(taxi_reposition, pgsql, idx, submode, conditions):
    # TODO: test needs a rework to actual support of
    # route, transporting_arrival and surge_arrival_local
    rows = select_table('config.check_rules', 'zone_id', pgsql['reposition'])
    assert len(rows) == 2
    assert (3, 1, 2, 2, 2, None, 2, 1, 1, None, 1, 1) in rows
    assert (3, 1, 1, 1, 1, 3, 1, 2, 2, None, 2, 2) in rows

    request_add = (
        '&submode=well' if submode is True and not idx & 0b00010000 else ''
    )
    submode_id = 3 if submode is True and not idx & 0b00010000 else None
    duration_id = 4 if idx & 0b0001 and not idx & 0b00010000 else None
    arrival_id = 4 if idx & 0b0010 and not idx & 0b00010000 else None
    immobility_id = 4 if idx & 0b0100 and not idx & 0b00010000 else None
    out_of_area_id = 4 if idx & 0b00010000 else None
    route_id = 4 if idx & 0b00100000 and not idx & 0b00010000 else None
    transporting_arrival_id = (
        4 if idx & 0b01000000 and not idx & 0b00010000 else None
    )

    query = {'checks': {}}
    if idx & 0b0001 and not idx & 0b00010000:
        query['checks']['duration'] = {
            'duration': 123,
            'left_time_deadline': 600,
            'left_time_coef': 0.1,
            'dry_run': False,
        }
    if idx & 0b0010 and not idx & 0b00010000:
        query['checks']['arrival'] = {
            'eta': 300,
            'distance': 50,
            'dry_run': False,
        }
    if idx & 0b0100 and not idx & 0b00010000:
        query['checks']['immobility'] = {
            'min_track_speed': 120,
            'position_threshold': 40,
            'max_immobility_time': 100,
            'dry_run': False,
        }
    if idx & 0b00010000:
        query['checks']['out_of_area'] = {
            'first_warnings': 3,
            'last_warnings': 6,
            'min_distance_from_border': 80,
            'time_out_of_area': 120,
            'dry_run': False,
        }
    if idx & 0b00100000 and not idx & 0b00010000:
        query['checks']['route'] = {
            'check_interval': 35,
            'max_last_checks_count': 1,
            'max_violations_count': 0,
            'first_warnings': 1,
            'last_warnings': 1,
            'speed_dist_range': {'maximum': -1.0},
            'speed_dist_abs_range': {'minimum': 0.0, 'maximum': 1.0},
            'speed_eta_range': {'maximum': 20.0},
            'speed_eta_abs_range': {'minimum': 0.0, 'maximum': 3.0},
            'range_checks_compose_operator': 'AND',
            'speed_checks_compose_operator': 'OR',
            'dry_run': False,
        }
    if idx & 0b01000000 and not idx & 0b00010000:
        query['checks']['transporting_arrival'] = {'dry_run': False}

    if conditions:
        conditions_checks = []
        if idx & 0b0001 and not idx & 0b00010000:
            conditions_checks.append('duration')
        if idx & 0b0010 and not idx & 0b00010000:
            conditions_checks.append('arrival')
        if idx & 0b0100 and not idx & 0b00010000:
            conditions_checks.append('immobility')
        if idx & 0b00010000:
            conditions_checks.append('out_of_area')
        if idx & 0b00100000 and not idx & 0b00010000:
            conditions_checks.append('route')
        if idx & 0b01000000 and not idx & 0b00010000:
            conditions_checks.append('transporting_arrival')

        for check in conditions_checks:
            query['checks'][check]['conditions'] = {
                'is_allowed_on_order': True,
                'is_allowed_on_busy': True,
            }

    response = taxi_reposition.put(
        '/v1/settings/zones/rules?mode={}&zone=__default__{}'.format(
            'my_district' if idx & 0b00010000 else 'surge', request_add,
        ),
        query,
    )
    assert response.status_code == 200

    rows = select_table(
        'check_rules.duration', 'duration_id', pgsql['reposition'],
    )
    assert len(rows) == 4 if idx & 0b0001 and not idx & 0b00010000 else 3
    assert rows[0] == (
        1,
        None,
        datetime.timedelta(0, 300),
        False,
        datetime.timedelta(seconds=600),
        0.1,
    )
    assert rows[1] == (
        2,
        None,
        datetime.timedelta(0, 200),
        False,
        datetime.timedelta(seconds=300),
        0.5,
    )
    assert rows[2] == (3, None, datetime.timedelta(0, 100), False, None, None)
    if idx & 0b0001 and not idx & 0b00010000:
        assert rows[3] == (
            duration_id,
            None,
            datetime.timedelta(0, 123),
            False,
            datetime.timedelta(seconds=600),
            0.1,
        )

    rows = select_table(
        'check_rules.arrival', 'arrival_id', pgsql['reposition'],
    )
    assert len(rows) == 4 if idx & 0b0010 and not idx & 0b00010000 else 3
    assert rows[0] == (1, 50, datetime.timedelta(0, 30), 10, False)
    assert rows[1] == (2, 100, datetime.timedelta(0, 60), None, False)
    assert rows[2] == (3, 150, datetime.timedelta(0, 90), 15, False)
    if idx & 0b0010 and not idx & 0b00010000:
        assert rows[3] == (
            arrival_id,
            50,
            datetime.timedelta(0, 300),
            None,
            False,
        )

    rows = select_table(
        'check_rules.immobility', 'immobility_id', pgsql['reposition'],
    )
    assert len(rows) == 4 if idx & 0b0100 and not idx & 0b00010000 else 3
    assert rows[0] == (1, 12, 4, datetime.timedelta(0, 90), False)
    assert rows[1] == (2, 15, 6, datetime.timedelta(0, 80), False)
    assert rows[2] == (3, 18, 8, datetime.timedelta(0, 70), False)
    if idx & 0b0100 and not idx & 0b00010000:
        assert rows[3] == (
            immobility_id,
            120,
            40,
            datetime.timedelta(0, 100),
            False,
        )

    rows = select_table(
        'check_rules.surge_arrival', 'surge_arrival_id', pgsql['reposition'],
    )
    assert len(rows) == 3 if idx & 0b1000 and not idx & 0b00010000 else 3
    assert rows[0] == (1, 0.9, 0.9, 1.1, datetime.timedelta(0, 50), False)
    assert rows[1] == (2, 0.1, 0.1, 1.0, datetime.timedelta(0, 80), False)
    assert rows[2] == (3, -1.0, -1.0, -1.0, datetime.timedelta(0, 0), False)

    rows = select_table(
        'check_rules.out_of_area', 'out_of_area_id', pgsql['reposition'],
    )
    assert len(rows) == 4 if idx & 0b00010000 else 3
    assert rows[0] == (1, 1, 3, 50, datetime.timedelta(0, 40), False)
    assert rows[1] == (2, 0, 10, 30, datetime.timedelta(0, 90), False)
    assert rows[2] == (3, 20, 100, 42, datetime.timedelta(0, 0), False)
    if idx & 0b00010000:
        assert rows[3] == (
            out_of_area_id,
            3,
            6,
            80,
            datetime.timedelta(0, 120),
            False,
        )

    rows = select_table('check_rules.route', 'route_id', pgsql['reposition'])
    assert len(rows) == 4 if idx & 0b00100000 and not idx & 0b00010000 else 3
    assert rows[0] == (
        1,
        datetime.timedelta(0, 45),
        5,
        3,
        1,
        2,
        '(-Infinity,-2)',
        '(0,2)',
        '(-Infinity,10)',
        '(0,4)',
        'AND',
        'OR',
        False,
    )
    assert rows[1] == (
        2,
        datetime.timedelta(0, 45),
        3,
        2,
        1,
        2,
        '(-Infinity,-5)',
        '(0,5)',
        '(-Infinity,30)',
        '(0,10)',
        'OR',
        'AND',
        False,
    )
    assert rows[2] == (
        3,
        datetime.timedelta(0, 45),
        1,
        1,
        1,
        2,
        '(-Infinity,0)',
        '(0,1)',
        '(-Infinity,3)',
        '(0,1)',
        'OR',
        'AND',
        False,
    )
    if idx & 0b00100000 and not idx & 0b00010000:
        assert rows[3] == (
            route_id,
            datetime.timedelta(0, 35),
            1,
            0,
            1,
            1,
            '(-Infinity,-1)',
            '(0,1)',
            '(-Infinity,20)',
            '(0,3)',
            'AND',
            'OR',
            False,
        )

    rows = select_table('config.check_rules', 'zone_id', pgsql['reposition'])
    assert len(rows) == 3 if idx & 0b00010000 else 2
    assert (
        4 if idx & 0b00010000 else 3,
        1,
        duration_id,
        arrival_id,
        immobility_id,
        submode_id,
        None,
        out_of_area_id,
        route_id,
        None,
        transporting_arrival_id,
        None,
    ) in rows
    if submode and not idx & 0b00010000:
        assert (3, 1, 2, 2, 2, None, 2, 1, 1, None, 1, 1) in rows
    else:
        assert (3, 1, 1, 1, 1, 3, 1, 2, 2, None, 2, 2) in rows

    if conditions:
        conditions_checks = []
        if duration_id and not out_of_area_id:
            conditions_checks.append(('duration', duration_id))
        if arrival_id and not out_of_area_id:
            conditions_checks.append(('arrival', arrival_id))
        if immobility_id and not out_of_area_id:
            conditions_checks.append(('immobility', immobility_id))
        if out_of_area_id:
            conditions_checks.append(('out_of_area', out_of_area_id))
        if route_id and not out_of_area_id:
            conditions_checks.append(('route', route_id))
        if transporting_arrival_id and not out_of_area_id:
            conditions_checks.append(
                ('transporting_arrival', transporting_arrival_id),
            )

        for check, check_id in conditions_checks:
            id_field = '{}_id'.format(check)
            rows = select_named(
                'SELECT {}, is_allowed_on_order,is_allowed_on_busy'
                ' from check_rules.conditions'
                ' WHERE {} = {}'.format(id_field, id_field, check_id),
                pgsql['reposition'],
            )
            assert rows == [
                {
                    id_field: check_id,
                    'is_allowed_on_order': True,
                    'is_allowed_on_busy': True,
                },
            ]


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql'])
def test_delete_zone_not_found(taxi_reposition):
    response = taxi_reposition.get(
        '/v1/settings/zones/rules?zone=__default__&mode=home',
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Zone \'__default__\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_delete_mode_not_found(taxi_reposition):
    response = taxi_reposition.delete(
        '/v1/settings/zones/rules?zone=__default__&mode=home',
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
def test_delete_non_existent(taxi_reposition):
    response = taxi_reposition.delete(
        '/v1/settings/zones/rules?zone=__default__&mode=home',
    )
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.parametrize('submode', [True, False])
@pytest.mark.parametrize('replication_enabled', [True, False])
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'submodes_home.sql',
        'zone_default.sql',
        'check_rules.sql',
        'simple_checks.sql',
    ],
)
def test_delete(
        taxi_reposition,
        pgsql,
        config,
        mockserver,
        submode,
        replication_enabled,
):
    @mockserver.json_handler('/reposition_watcher/v1/admin/checks/item')
    def mock_reposition_watcher(request):
        return mockserver.make_response('{}', status=200)

    config.set_values(
        dict(REPOSITION_CHECKS_REPLICATION_ENABLED=replication_enabled),
    )

    request_add = '&submode=fast' if submode is True else ''
    response = taxi_reposition.delete(
        '/v1/settings/zones/rules?zone=__default__&mode=home' + request_add,
    )
    assert response.status_code == 200
    assert mock_reposition_watcher.times_called == (
        1 if replication_enabled else 0
    )

    rows = select_table('config.check_rules', 'zone_id', pgsql['reposition'])
    assert len(rows) == 2
    if submode:
        assert (1, 1, 1, 1, 1, None, 1, 1, 1, 1, 1, 1) in rows
        assert (1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2) in rows
    else:
        assert (1, 1, 1, 2, 1, 1, None, None, None, 1, 1, None) in rows
        assert (1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2) in rows
