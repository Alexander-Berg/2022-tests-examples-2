import datetime

import pytest

# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
PEDESTRIAN_ZONE = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                {'lon': 37.64216423034668, 'lat': 55.73387629706783},
                {'lon': 37.64343023300171, 'lat': 55.734552853773316},
                {'lon': 37.64182090759277, 'lat': 55.73770593659091},
                {'lon': 37.64008283615112, 'lat': 55.73701735403676},
                {'lon': 37.64216423034668, 'lat': 55.73387629706783},
            ],
        ],
    ],
}
TAXI_ZONE = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                {'lon': 37.64216423034668, 'lat': 55.73386421559154},
                {'lon': 37.64572620391845, 'lat': 55.73615962895247},
                {'lon': 37.64167070388794, 'lat': 55.743153766729286},
                {'lon': 37.63817310333252, 'lat': 55.74206667732932},
                {'lon': 37.640061378479004, 'lat': 55.73699319302477},
                {'lon': 37.64216423034668, 'lat': 55.73386421559154},
            ],
        ],
    ],
}
TAXI_NIGHT_ZONE = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                {'lon': 37.642099857330315, 'lat': 55.73387629706783},
                {'lon': 37.648558616638184, 'lat': 55.73155658505244},
                {'lon': 37.64167070388794, 'lat': 55.743214159696876},
                {'lon': 37.63808727264404, 'lat': 55.74616122293968},
                {'lon': 37.63549089431763, 'lat': 55.744844734490414},
                {'lon': 37.642099857330315, 'lat': 55.73387629706783},
            ],
        ],
    ],
}
TAXI_REMOTE_ZONE = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                {'lon': 37.64817237854004, 'lat': 55.73788714050709},
                {'lon': 37.65426635742187, 'lat': 55.74296050860488},
                {'lon': 37.65546798706055, 'lat': 55.74979643282958},
                {'lon': 37.64066219329834, 'lat': 55.7473568941391},
                {'lon': 37.64817237854004, 'lat': 55.73788714050709},
            ],
        ],
    ],
}
ROVER_ZONE = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                {'lon': 37.6412308216095, 'lat': 55.735368330645244},
                {'lon': 37.64217495918274, 'lat': 55.73393066366496},
                {'lon': 37.64310836791992, 'lat': 55.7345709756667},
                {'lon': 37.642561197280884, 'lat': 55.73572471889124},
                {'lon': 37.6412308216095, 'lat': 55.735368330645244},
            ],
        ],
    ],
}
MARKERS = [
    [37.64169216156006, 55.73626835571061],  # 0: Inside smallest zone (foot)
    [37.64164924621582, 55.74030311233403],  # 1: Inside taxi zone
    [37.64817237854004, 55.744844734490414],  # 2: Inside remote zone
    [37.63688564300537, 55.73764553509855],  # 3: Outside any zone
    [37.638559341430664, 55.74424082584503],  # 4: Inside taxi night zone
    [37.64199256896973, 55.734969655191975],  # 5: Inside rover zone
]

ZONE_PRIORITY_CONFIG_DEFAULT = pytest.mark.experiments3(
    name='zone_priority',
    consumers=[
        'grocery-depots-client/zone_priority',
        'grocery-depots-internal/zone_priority',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'pedestrian': 100,
        'yandex_taxi': 10,
        'yandex_taxi_remote': 5,
        'yandex_taxi_night': 1,
        'rover': 0,
    },
    is_config=True,
)


def _prepare_depot(grocery_depots):
    """
    There is single depot with 5 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """

    working_hours_dict = {
        'pedestrian': {
            'from': {'hour': 9, 'minute': 0},
            'to': {'hour': 20, 'minute': 0},
        },
        'yandex_taxi': {
            'from': {'hour': 7, 'minute': 0},
            'to': {'hour': 0, 'minute': 0},
        },
        'yandex_taxi_night': {
            'from': {'hour': 0, 'minute': 0},
            'to': {'hour': 7, 'minute': 0},
        },
        'yandex_taxi_remote': {
            'from': {'hour': 7, 'minute': 0},
            'to': {'hour': 23, 'minute': 0},
        },
        'rover': {
            'from': {'hour': 9, 'minute': 0},
            'to': {'hour': 20, 'minute': 0},
        },
    }

    depot = grocery_depots.add_depot(1, auto_add_zone=False)
    depot.add_zone(
        delivery_type='pedestrian',
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': working_hours_dict['pedestrian'],
            },
        ],
    )
    depot.add_zone(
        delivery_type='yandex_taxi',
        geozone=TAXI_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': working_hours_dict['yandex_taxi'],
            },
        ],
    )
    depot.add_zone(
        delivery_type='yandex_taxi_night',
        geozone=TAXI_NIGHT_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': working_hours_dict['yandex_taxi_night'],
            },
        ],
    )
    depot.add_zone(
        delivery_type='yandex_taxi_remote',
        geozone=TAXI_REMOTE_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': working_hours_dict['yandex_taxi_remote'],
            },
        ],
    )
    depot.add_zone(
        delivery_type='rover',
        geozone=ROVER_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': working_hours_dict['rover'],
            },
        ],
    )

    return depot, working_hours_dict


@pytest.mark.parametrize(
    'location, timeofday, expected_code, expected_zone, expected_state, '
    'working_hours_in_response',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            'pedestrian',
            'open',
            True,
            id='foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '09:00',
            200,
            'pedestrian',
            'open',
            True,
            id='foot zone schedule start',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            True,
            id='night zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            200,
            'yandex_taxi',
            'open',
            True,
            id='taxi zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            True,
            id='taxi zone at night',
        ),
        pytest.param(
            # marker no 5
            MARKERS[4],
            '10:00',
            200,
            'yandex_taxi_night',
            'closed',
            False,
            id='night zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            200,
            'yandex_taxi_remote',
            'open',
            True,
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
            id='no zone at night',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            '09:00',
            200,
            'pedestrian',
            'open',
            True,
            id='rover zone lower priority',
        ),
    ],
)
@ZONE_PRIORITY_CONFIG_DEFAULT
async def test_depot_resolve_basic(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        location,
        timeofday,
        expected_code,
        expected_zone,
        expected_state,
        working_hours_in_response,
):
    depot, working_hours_dict = _prepare_depot(grocery_depots)

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }
    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )

    working_hours = None
    if working_hours_in_response:
        working_hours = working_hours_dict[expected_zone]

    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert resp_json['depot_id'] == depot.depot_id
        assert resp_json['legacy_depot_id'] == depot.legacy_depot_id
        assert 'zone_type' in resp_json.keys()
        assert resp_json['zone_type'] == expected_zone
        assert 'state' in resp_json.keys()
        assert resp_json['state'] == expected_state
        assert 'switch_time' in resp_json.keys()
        assert resp_json.get('working_hours', None) == working_hours


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
@ZONE_PRIORITY_CONFIG_DEFAULT
async def test_zone_retiring(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        location,
        timeofday,
        delta_days,
        expected_code,
        expected_zone,
        expected_state,
):
    """
    There is a single depot:
    * 2 foot zones, both available 07:00-20:00, first one is available till
      test time + 24h, the other one is bigger and is available
      since time + 24h
    * 1 remote zone available 07:00-23:00, retiring in test time + 24h

    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """

    now = datetime.datetime.now(datetime.timezone.utc)

    depot = grocery_depots.add_depot(1, auto_add_zone=False)
    depot.add_zone(
        delivery_type='pedestrian',
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
        effective_from=(now - datetime.timedelta(weeks=1)).isoformat(),
        effective_till=(now + datetime.timedelta(days=1)).isoformat(),
    )
    depot.add_zone(
        delivery_type='pedestrian',
        geozone=TAXI_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
        effective_from=(now + datetime.timedelta(days=1)).isoformat(),
        effective_till=None,
    )
    depot.add_zone(
        delivery_type='yandex_taxi_remote',
        geozone=TAXI_REMOTE_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 23, 'minute': 0},
                },
            },
        ],
        effective_from=(now - datetime.timedelta(weeks=1)).isoformat(),
        effective_till=(now + datetime.timedelta(days=1)).isoformat(),
    )

    request_date = datetime.date.today() + datetime.timedelta(days=delta_days)
    request = {
        'position': {'location': location},
        'time': (
            f'{request_date.year}-{request_date.month:02d}-'
            f'{request_date.day:02d}'
            f'T{timeofday}:00+00:00'
        ),
    }

    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert 'zone_type' in resp_json.keys()
        assert resp_json['zone_type'] == expected_zone
        assert 'state' in resp_json.keys()
        assert resp_json['state'] == expected_state


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
@ZONE_PRIORITY_CONFIG_DEFAULT
async def test_exclude_zone_from_depot_resolve(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        location,
        timeofday,
        expected_code,
        excluded_zones,
        expected_zone,
        taxi_config,
):
    _prepare_depot(grocery_depots)

    taxi_config.set_values(
        {'GROCERY_DEPOTS_CLIENT_EXCLUDED_DELIVERY_TYPES': excluded_zones},
    )

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }

    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )

    assert response.status_code == 200
    assert 'zone_type' in response.json().keys()
    assert response.json()['zone_type'] == expected_zone


@pytest.mark.parametrize(
    'depot_status, zone_status, expected_code, expected_state',
    [
        pytest.param(
            'coming_soon',
            'active',
            200,
            'coming_soon',
            id='coming_soon depot, active zone',
        ),
        pytest.param(
            'coming_soon',
            'disabled',
            404,
            None,
            id='coming_soon depot, disabled zone',
        ),
        pytest.param(
            'disabled',
            'active',
            200,
            'disabled',
            id='disabled depot, active zone',
        ),
        pytest.param(
            'disabled',
            'disabled',
            404,
            None,
            id='disabled depot, disabled zone',
        ),
    ],
)
@ZONE_PRIORITY_CONFIG_DEFAULT
async def test_resolve_coming_soon(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        depot_status,
        zone_status,
        expected_code,
        expected_state,
):
    """ Should return depot state == coming_soon for closed
    depot if open_ts is Null """

    location = MARKERS[0]

    depot = grocery_depots.add_depot(
        1, auto_add_zone=False, status=depot_status,
    )
    depot.add_zone(
        delivery_type='pedestrian',
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
        status=zone_status,
    )

    request = {
        'position': {'location': location},
        'time': '2020-09-09T12:00:00+00:00',
    }
    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )

    assert response.status_code == expected_code
    response_json = response.json()
    assert ('state' in response_json) == (expected_state is not None)
    if expected_state is not None:
        assert response_json['state'] == expected_state


@pytest.mark.parametrize(
    'expected_code, allow_parcels',
    [
        pytest.param(200, True, id='parcels allowed'),
        pytest.param(404, False, id='parcels disallowed'),
    ],
)
@ZONE_PRIORITY_CONFIG_DEFAULT
async def test_allow_parcels(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        expected_code,
        allow_parcels,
):
    """ Should return 404 if parcels are not allowed for depot """

    location = MARKERS[0]

    depot = grocery_depots.add_depot(
        1, auto_add_zone=False, allow_parcels=allow_parcels,
    )
    depot.add_zone(
        delivery_type='pedestrian',
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
    )

    request = {
        'position': {'location': location},
        'time': '2020-09-09T12:00:00+00:00',
        'filter': 'allow_parcels',
    }
    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )

    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'expected_code, allow_parcels_depot_zone, second_depot_zoze',
    [
        pytest.param(200, 'pedestrian', 'yandex_taxi', id='parcels allowed'),
        pytest.param(
            404, 'yandex_taxi', 'pedestrian', id='parcels disallowed',
        ),
    ],
)
@ZONE_PRIORITY_CONFIG_DEFAULT
async def test_allow_parcels_depot_intersection(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        expected_code,
        allow_parcels_depot_zone,
        second_depot_zoze,
):
    """
    There are two depots with zone intersections:
    * First depot can accept parcels
    * Second depot can't accept parcels

    If allow_parcels_depot is better than second_depot - we shoud get 200
    If second_depot is better - 404
    https://st.yandex-team.ru/LAVKALOGDEV-34
    """

    location = MARKERS[0]

    allow_parcels_depot = grocery_depots.add_depot(
        1, auto_add_zone=False, allow_parcels=True,
    )
    allow_parcels_depot.add_zone(
        delivery_type=allow_parcels_depot_zone,
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
    )

    second_depot = grocery_depots.add_depot(
        2, auto_add_zone=False, allow_parcels=False,
    )
    second_depot.add_zone(
        delivery_type=second_depot_zoze,
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
    )

    request = {
        'position': {'location': location},
        'time': '2020-09-09T12:00:00+00:00',
        'filter': 'allow_parcels',
    }
    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json()['depot_id'] == allow_parcels_depot.depot_id


@pytest.mark.parametrize(
    'expected_code, legacy_depot_id',
    [
        pytest.param(200, '123456', id='depot is not hidden'),
        pytest.param(404, '654321', id='depot is hidden'),
    ],
)
@ZONE_PRIORITY_CONFIG_DEFAULT
@pytest.mark.experiments3(
    name='overlord_depots_hidings',
    consumers=['grocery-depots-internal/depots_hidings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'Показать для избранных пользователей',
            'value': {
                'depots_hidings': [
                    {'depot_id': '123456', 'hidden': False},
                    {'depot_id': '654321', 'hidden': True},
                ],
            },
        },
    ],
    default_value={},
    is_config=True,
)
async def test_depot_hidings(
        taxi_grocery_caas_sample_consumer,
        grocery_depots,
        expected_code,
        legacy_depot_id,
):
    """ Should return 404 if depot is hidden in depot_hidings config """

    location = MARKERS[0]

    depot = grocery_depots.add_depot(
        1, auto_add_zone=False, legacy_depot_id=legacy_depot_id,
    )
    depot.add_zone(
        delivery_type='pedestrian',
        geozone=PEDESTRIAN_ZONE,
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
    )

    request = {
        'position': {'location': location},
        'time': '2020-09-09T12:00:00+00:00',
    }
    response = await taxi_grocery_caas_sample_consumer.post(
        '/internal/v1/sample-consumer/v1/depot-resolve', json=request,
    )

    assert response.status_code == expected_code
