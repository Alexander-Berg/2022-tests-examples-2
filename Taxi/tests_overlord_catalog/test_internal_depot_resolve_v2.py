import datetime

import pytest

from . import experiments

MARKERS = [
    [37.64169216156006, 55.73626835571061],  # Inside smallest zone (foot)
    [37.64164924621582, 55.74030311233403],  # Inside taxi zone
    [37.64817237854004, 55.744844734490414],  # Inside remote zone
    [37.63688564300537, 55.73764553509855],  # Outside any zone
    [37.638559341430664, 55.74424082584503],  # Inside taxi night zone
    [38.64169216156006, 56.73626835571061],  # Inside tristero foot zone
    [38.64817237854004, 56.744844734490414],  # Inside tristero remote zone
    [37.64199256896973, 55.734969655191975],  # Inside rover zone
]


def setup_gdepots_as_defaultsql(mockserver, load_json):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return load_json(
            '../test_internal_depot_resolve' '/g-depots-as-default-sql.json',
        )

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return load_json(
            '../test_internal_depot_resolve'
            '/g-depots-zones-as-default-sql.json',
        )


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, expected_code, expected_zone, expected_state, '
    'allow_parcels, external_id, working_hours_idx',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            'pedestrian',
            'open',
            False,
            '111',
            0,
            id='foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '09:00',
            200,
            'pedestrian',
            'open',
            False,
            '111',
            0,
            id='foot zone schedule start',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            False,
            '111',
            2,
            id='night zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '111',
            1,
            id='taxi zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            False,
            '111',
            2,
            id='taxi zone at night',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            404,
            'yandex_taxi_night',
            'open',
            True,
            '111',
            2,
            id='taxi zone at night 1',
        ),
        pytest.param(
            # marker no 5
            MARKERS[4],
            '10:00',
            200,
            'yandex_taxi_night',
            'closed',
            False,
            '111',
            None,
            id='night zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            200,
            'yandex_taxi_remote',
            'open',
            False,
            '111',
            3,
            id='remote zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '111',
            None,
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '10:00',
            404,
            None,
            None,
            False,
            '111',
            None,
            id='no zone at day',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '01:00',
            404,
            None,
            None,
            False,
            '111',
            2,
            id='no zone at night',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            '09:00',
            200,
            'pedestrian',
            'open',
            False,
            '112',
            0,
            id='foot zone with parcels schedule start',
        ),
        pytest.param(
            # marker no 7
            MARKERS[6],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '112',
            None,
            id='remote tristero zone at night',
        ),
        pytest.param(
            # marker no 7
            MARKERS[6],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '112',
            None,
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 8
            MARKERS[7],
            '09:00',
            200,
            'pedestrian',
            'open',
            False,
            '111',
            0,
            id='rover zone lower priority',
        ),
    ],
)
@experiments.zone_priority_config_default
async def test_depot_resolve_ok(
        taxi_overlord_catalog,
        location,
        timeofday,
        expected_code,
        expected_zone,
        expected_state,
        allow_parcels,
        external_id,
        working_hours_idx,
        mockserver,
        load_json,
):
    """
    There is a single depot in the database with 4 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    setup_gdepots_as_defaultsql(mockserver, load_json)
    working_hours_arr = [
        {'from': {'hour': 9, 'minute': 0}, 'to': {'hour': 20, 'minute': 0}},
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 0, 'minute': 0}},
        {'from': {'hour': 0, 'minute': 0}, 'to': {'hour': 7, 'minute': 0}},
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 23, 'minute': 0}},
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }
    if allow_parcels:
        request['filter'] = 'allow_parcels'

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/depot-resolve', json=request,
    )

    if external_id == '111':
        depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'
    else:
        depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011'

    working_hours = None
    if working_hours_idx is not None:
        working_hours = working_hours_arr[working_hours_idx]

    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert resp_json['depot_id'] == depot_id
        assert resp_json['depot_external_id'] == external_id
        assert 'best_zone' in resp_json.keys()
        zone = resp_json['best_zone']
        assert 'zone_type' in zone.keys()
        assert zone['zone_type'] == expected_zone
        assert 'state' in zone.keys()
        assert zone['state'] == expected_state
        assert 'switch_time' in zone.keys()
        assert zone.get('working_hours', None) == working_hours


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, expected_code, expected_zone, expected_state, '
    'allow_parcels, external_id, working_hours_idx',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '111',
            1,
            id='foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '09:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '111',
            1,
            id='foot zone schedule start',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            False,
            '111',
            2,
            id='night zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '111',
            1,
            id='taxi zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            False,
            '111',
            2,
            id='taxi zone at night',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            404,
            'yandex_taxi_night',
            'open',
            True,
            '111',
            2,
            id='taxi zone at night 1',
        ),
        pytest.param(
            # marker no 5
            MARKERS[4],
            '10:00',
            200,
            'yandex_taxi_night',
            'closed',
            False,
            '111',
            None,
            id='night zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            200,
            'yandex_taxi_remote',
            'open',
            False,
            '111',
            3,
            id='remote zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '111',
            None,
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '10:00',
            404,
            None,
            None,
            False,
            '111',
            None,
            id='no zone at day',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '01:00',
            404,
            None,
            None,
            False,
            '111',
            2,
            id='no zone at night',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            '09:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '112',
            1,
            id='foot zone with parcels schedule start',
        ),
        pytest.param(
            # marker no 7
            MARKERS[6],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '112',
            None,
            id='remote tristero zone at night',
        ),
        pytest.param(
            # marker no 7
            MARKERS[6],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '112',
            None,
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 8
            MARKERS[7],
            '09:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '111',
            1,
            id='rover zone lower priority',
        ),
    ],
)
@experiments.zone_priority_config_taxi_most_priority
async def test_depot_resolve_ok_zone_priorities_experiment(
        taxi_overlord_catalog,
        location,
        timeofday,
        expected_code,
        expected_zone,
        expected_state,
        allow_parcels,
        external_id,
        working_hours_idx,
        mock_grocery_depots,
):
    """
    There is a single depot in the database with 4 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.load_json(
        '../test_internal_depot_resolve/g-depots-as-default-sql.json',
        '../test_internal_depot_resolve/g-depots-zones-as-default-sql.json',
    )
    working_hours_arr = [
        {'from': {'hour': 9, 'minute': 0}, 'to': {'hour': 20, 'minute': 0}},
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 0, 'minute': 0}},
        {'from': {'hour': 0, 'minute': 0}, 'to': {'hour': 7, 'minute': 0}},
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 23, 'minute': 0}},
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }
    if allow_parcels:
        request['filter'] = 'allow_parcels'

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/depot-resolve', json=request,
    )

    if external_id == '111':
        depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'
    else:
        depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011'

    working_hours = None
    if working_hours_idx is not None:
        working_hours = working_hours_arr[working_hours_idx]

    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert resp_json['depot_id'] == depot_id
        assert resp_json['depot_external_id'] == external_id
        assert 'best_zone' in resp_json.keys()
        zone = resp_json['best_zone']
        assert 'zone_type' in zone.keys()
        assert zone['zone_type'] == expected_zone
        assert 'state' in zone.keys()
        assert zone['state'] == expected_state
        assert 'switch_time' in zone.keys()
        assert zone.get('working_hours', None) == working_hours


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, delta_days, expected_code, expected_zone, '
    'expected_state',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            0,
            200,
            'pedestrian',
            'open',
            id='old foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '21:00',
            0,
            200,
            'pedestrian',
            'closed',
            id='old foot zone out of working time',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            0,
            404,
            None,
            None,
            id='outside old foot zone',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            0,
            200,
            'yandex_taxi_remote',
            'open',
            id='old remote zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone - marker 2 ',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            2,  # plus two days
            404,
            None,
            None,
            id='retired remote zone',
        ),
    ],
)
async def test_zone_retiring(
        taxi_overlord_catalog,
        location,
        timeofday,
        delta_days,
        expected_code,
        expected_zone,
        expected_state,
        mock_grocery_depots,
):
    """
    There is a single depot in the database:
    * 2 foot zones, both available 07:00-20:00, first one is available till
      test time + 24h, the other one is bigger and is available
      since time + 24h
    * 1 remote zone available 07:00-23:00, retiring in test time + 24h

    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.parse_json(
        '../test_internal_depot_resolve/gdepots-depots-zone_retiring.json',
        '../test_internal_depot_resolve/gdepots-zones-zone_retiring.json',
    )
    await taxi_overlord_catalog.invalidate_caches()
    request_date = datetime.date.today() + datetime.timedelta(days=delta_days)
    request = {
        'position': {'location': location},
        'time': (
            f'{request_date.year}-{request_date.month:02d}-'
            f'{request_date.day:02d}'
            f'T{timeofday}:00+00:00'
        ),
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/depot-resolve', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert 'best_zone' in resp_json.keys()
        zone = resp_json['best_zone']
        assert 'zone_type' in zone.keys()
        assert zone['zone_type'] == expected_zone
        assert 'state' in zone.keys()
        assert zone['state'] == expected_state


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, delta_days, expected_code, expected_zone, '
    'expected_state',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            0,
            200,
            'pedestrian',
            'open',
            id='old foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '21:00',
            0,
            200,
            'pedestrian',
            'closed',
            id='old foot zone out of working time',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            0,
            404,
            None,
            None,
            id='outside old foot zone',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            0,
            200,
            'yandex_taxi_remote',
            'open',
            id='old remote zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone - marker 2 ',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            2,  # plus two days
            404,
            None,
            None,
            id='retired remote zone',
        ),
    ],
)
async def test_zone_retiring_separate_table(
        taxi_overlord_catalog,
        location,
        timeofday,
        delta_days,
        expected_code,
        expected_zone,
        expected_state,
        mock_grocery_depots,
):
    """
    There is a single depot in the database:
    * 2 foot zones, both available 07:00-20:00, first one is available till
      test time + 24h, the other one is bigger and is available
      since time + 24h
    * 1 remote zone available 07:00-23:00, retiring in test time + 24h

    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.parse_json(
        '../test_internal_depot_resolve/'
        'gdepots-depots-zone_retiring_separate_table.json',
        '../test_internal_depot_resolve/'
        'gdepots-zones-zone_retiring_separate_table.json',
    )
    await taxi_overlord_catalog.invalidate_caches()
    request_date = datetime.date.today() + datetime.timedelta(days=delta_days)
    request = {
        'position': {'location': location},
        'time': (
            f'{request_date.year}-{request_date.month:02d}-'
            f'{request_date.day:02d}'
            f'T{timeofday}:00+00:00'
        ),
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/depot-resolve', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert 'best_zone' in resp_json.keys()
        zone = resp_json['best_zone']
        assert 'zone_type' in zone.keys()
        assert zone['zone_type'] == expected_zone
        assert 'state' in zone.keys()
        assert zone['state'] == expected_state


@pytest.mark.parametrize(
    'location, timeofday, expected_code, excluded_zones, expected_zone',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            [],
            'pedestrian',
            id='Allowed pedestrian zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            ['pedestrian'],
            'yandex_taxi',
            id='Disallowed pedestrian zone',
        ),
    ],
)
async def test_exclude_zone_from_depot_resolve(
        taxi_overlord_catalog,
        location,
        timeofday,
        expected_code,
        excluded_zones,
        expected_zone,
        taxi_config,
        mock_grocery_depots,
):
    """
    There is a single depot in the database with 4 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.load_json(
        '../test_internal_depot_resolve/' 'g-depots-as-default-sql.json',
        '../test_internal_depot_resolve/' 'g-depots-zones-as-default-sql.json',
    )
    taxi_config.set_values(
        {'GROCERY_DEPOTS_CLIENT_EXCLUDED_DELIVERY_TYPES': excluded_zones},
    )
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/depot-resolve', json=request,
    )

    assert response.status_code == 200
    assert 'best_zone' in response.json().keys()
    zone = response.json()['best_zone']
    assert 'zone_type' in zone.keys()
    assert zone['zone_type'] == expected_zone


@pytest.mark.parametrize(
    'location, timeofday, expected_code, excluded_zones, best_zone, '
    'optional_zones',
    [
        pytest.param(
            # marker no 8
            MARKERS[7],
            '10:00',
            200,
            [],
            'pedestrian',
            [],
            id='Allowed rover zone',
        ),
        pytest.param(
            # marker no 8
            MARKERS[7],
            '10:00',
            200,
            ['rover'],
            'pedestrian',
            ['rover'],
            id='Disallowed rover zone',
        ),
    ],
)
@pytest.mark.parametrize('is_match_optional', [False, True])
@experiments.zone_priority_config_default
async def test_return_optional_excluded_zones_from_depot_resolve_v2(
        taxi_overlord_catalog,
        location,
        timeofday,
        expected_code,
        excluded_zones,
        best_zone,
        optional_zones,
        is_match_optional,
        taxi_config,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        '../test_internal_depot_resolve/' 'g-depots-as-default-sql.json',
        '../test_internal_depot_resolve/' 'g-depots-zones-as-default-sql.json',
    )
    taxi_config.set_values(
        {'GROCERY_DEPOTS_CLIENT_EXCLUDED_DELIVERY_TYPES': excluded_zones},
    )
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
        'is_match_optional_zones': is_match_optional,
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/depot-resolve', json=request,
    )

    assert response.status_code == 200

    assert 'best_zone' in response.json().keys()
    zone = response.json()['best_zone']
    assert 'zone_type' in zone.keys()
    assert zone['zone_type'] == best_zone

    if is_match_optional:
        assert 'optional_zones' in response.json().keys()
        assert len(response.json()['optional_zones']) == len(optional_zones)
        if optional_zones:
            opt_zone = response.json()['optional_zones'][0]

            assert 'zone_type' in opt_zone
            assert 'state' in opt_zone
            assert 'switch_time' in opt_zone
            assert 'working_hours' in opt_zone

            assert {
                zone['zone_type'] for zone in response.json()['optional_zones']
            } == set(optional_zones)
    else:
        assert 'optional_zones' not in response.json().keys()
