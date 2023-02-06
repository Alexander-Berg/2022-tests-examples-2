import pytest

DURATION_CHECK = {
    'conditions': {},
    'config': {'dry_run': False, 'send_push': True},
    'due': '2020-05-08T00:55:00+00:00',
    'span': 900,
}

ARRIVAL_CHECK = {
    'conditions': {},
    'config': {'dry_run': False, 'send_push': True},
    'distance': 25,
    'eta': 5,
}

ARRIVAL_CHECK2 = {
    'conditions': {},
    'config': {'dry_run': False, 'send_push': True},
    'distance': 35,
    'eta': 5,
}

IMMOBILITY_CHECK = {
    'conditions': {},
    'config': {'dry_run': False, 'send_push': False},
    'max_immobility_time': 33,
    'min_track_speed': 11,
    'position_threshold': 22,
}

IMMOBILITY_CHECK2 = {
    'conditions': {},
    'config': {'dry_run': False, 'send_push': True},
    'max_immobility_time': 43,
    'min_track_speed': 21,
    'position_threshold': 32,
}

SURGE_ARRIVAL_CHECK = {
    'coef_surge': 0.9,
    'conditions': {},
    'config': {'dry_run': False, 'send_push': True},
    'min_local_surge': 0.5,
    'min_ride_time': 2,
}

OUT_OF_AREA_CHECK = {
    'conditions': {'is_allowed_on_busy': False, 'is_allowed_on_order': True},
    'config': {'dry_run': False, 'send_push': True},
    'min_distance_from_border': 10,
    'time_out_of_area': 900,
}

ROUTE_CHECK = {
    'check_interval': 60,
    'conditions': {'is_allowed_on_busy': False, 'is_allowed_on_order': False},
    'config': {'dry_run': False, 'send_push': True},
    'max_last_checks_count': 4,
    'max_violations_count': 3,
    'range_checks_compose_operator': 'AND',
    'speed_checks_compose_operator': 'OR',
    'speed_dist_range': {
        'abs_range': {'maximum': 20.0, 'minimum': 1.0},
        'range': {'maximum': 20.0},
    },
    'speed_eta_range': {
        'abs_range': {'maximum': 5.0, 'minimum': 1.0},
        'range': {'maximum': 5.0, 'minimum': -2.0},
    },
}

TRANSPORTING_ARRIVAL_CHECK = {
    'conditions': {},
    'config': {'dry_run': False, 'send_push': True},
}


@pytest.mark.pgsql(
    'reposition_watcher', files=['modes_zones.sql', 'config_checks.sql'],
)
@pytest.mark.now('2020-05-08T23:55:00+00:00')
async def test_get(taxi_reposition_watcher):
    zone = '__default__'
    response = await taxi_reposition_watcher.get(
        f'v1/admin/checks/list?zone={zone}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'home': {
            'checks': {
                'arrival': ARRIVAL_CHECK2,
                'immobility': IMMOBILITY_CHECK2,
                'out_of_area': OUT_OF_AREA_CHECK,
                'route': ROUTE_CHECK,
            },
        },
        'poi': {
            'checks': {
                'arrival': ARRIVAL_CHECK,
                'duration': DURATION_CHECK,
                'immobility': IMMOBILITY_CHECK2,
                'out_of_area': OUT_OF_AREA_CHECK,
                'route': ROUTE_CHECK,
                'surge_arrival': SURGE_ARRIVAL_CHECK,
                'transporting_arrival': TRANSPORTING_ARRIVAL_CHECK,
            },
            'submodes': {
                'fast': {
                    'checks': {
                        'arrival': ARRIVAL_CHECK,
                        'duration': DURATION_CHECK,
                        'immobility': IMMOBILITY_CHECK,
                        'out_of_area': OUT_OF_AREA_CHECK,
                        'route': ROUTE_CHECK,
                        'surge_arrival': SURGE_ARRIVAL_CHECK,
                        'transporting_arrival': TRANSPORTING_ARRIVAL_CHECK,
                    },
                },
            },
        },
    }
