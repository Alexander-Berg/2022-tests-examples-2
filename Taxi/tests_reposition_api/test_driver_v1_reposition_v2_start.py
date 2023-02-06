# pylint: disable=import-only-modules,too-many-lines
from datetime import datetime
from datetime import timedelta

import pytest

from .utils import select_named
from .utils import select_table
from .utils import select_table_named
from .utils import usages_count

BACKWARD_COMPATIBLE_URI = '/driver/v1/v2/reposition/start'
NEW_URI = '/driver/v1/reposition/v2/start'


def get_headers(dbid, uuid):
    return {
        'Accept-Language': 'en-EN',
        'X-YaTaxi-Park-Id': dbid,
        'X-YaTaxi-Driver-Profile-Id': uuid,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
    }


def check_points_table(
        db,
        mode,
        point_id=1,
        name='',
        address='',
        city='',
        driver_id='(1488,driverSS)',
):
    rows = select_named(
        """
        SELECT point_id, mode_id, updated, name, address, city, driver_id
        FROM settings.points NATURAL JOIN settings.driver_ids
        """,
        db,
    )
    for row in rows:
        if row['point_id'] == point_id:
            assert row['mode_id'] == mode
            assert not row['updated'] is None
            assert row['name'] == name
            assert row['address'] == address
            assert row['city'] == city
            assert row['driver_id'] == driver_id
            return
    assert False


def check_watcher_table(
        db,
        session_id,
        duration_id=None,
        arrival_id=None,
        immobility_id=None,
        antisurge_arrival_id=None,
        surge_arrival_id=None,
        surge_arrival_local_id=None,
        out_of_area_id=None,
        route_id=None,
        transporting_arrival_id=None,
):
    rows = select_named(
        """
        SELECT * FROM state.sessions_to_reposition_watcher
        WHERE session_id={}
        """.format(
            session_id,
        ),
        db,
    )

    for row in rows:
        del row['created_at']
        del row['session_to_watcher_id']

    assert rows == [
        {
            '_session_id': session_id,
            'session_id': session_id,
            'is_stop_action': False,
            'force_dry_run': False,
            'duration_id': duration_id,
            'arrival_id': None,
            'immobility_id': None,
            'antisurge_arrival_id': None,
            'surge_arrival_id': None,
            'surge_arrival_local_id': None,
            'out_of_area_id': None,
            'route_id': None,
            'transporting_arrival_id': None,
        },
    ]


def check_sessions_table(
        db,
        point_id=1,
        mode_id=1,
        submode_id=None,
        destination_point='(3,4)',
        destination_radius=None,
        start_point='(3.1,4.1)',
        session_deadline=None,
):
    rows = select_table_named('state.sessions', 'session_id', db)
    for row in rows:
        if row['point_id'] == point_id:
            assert row['active']
            assert not row['start'] is None
            assert row['end'] is None
            assert row['start_point'] == start_point
            assert row['mode_id'] == mode_id
            assert row['submode_id'] == submode_id
            assert row['destination_point'] == destination_point
            assert row['destination_radius'] == destination_radius
            assert row['session_deadline'] == session_deadline
            return
    assert False


def build_driver_position_response(lon, lat):
    return {
        'position': {
            'direction': 328,
            'lon': lon,
            'lat': lat,
            'speed': 30,
            'timestamp': 1502366306,
        },
        'type': 'raw',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.pgsql(
    'reposition', files=['zone_default.sql', 'mode_home.sql', 'home_poi.sql'],
)
async def test_start_input_no_points(taxi_reposition_api, handler_uri, load):
    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={'type': 'saved_point', 'mode_id': 'home'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.parametrize('point_id', ['bad-id', 'poi_id_1'])
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'mode_home.sql', 'home_poi.sql', 'drivers.sql'],
)
async def test_start_invalid_point_id(
        taxi_reposition_api, handler_uri, mockserver, point_id,
):
    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={'type': 'saved_point', 'mode_id': 'home', 'point_id': point_id},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid point_id'}


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi_offer_only.sql',
        'simple_without_sessions.sql',
        'tags_assignments_poi.sql',
    ],
)
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.experiments3(
    name='reposition_start_router_info',
    consumers=['reposition/sessions'],
    match={
        'consumers': [{'name': 'reposition/sessions'}],
        'predicate': {'type': 'true', 'init': {}},
        'enabled': True,
    },
    clauses=[
        {
            'title': 'main',
            'predicate': {'type': 'true', 'init': {}},
            'value': {'should_fetch': True},
        },
    ],
    default_value={},
)
async def test_start_affect_ignore_override_busy(
        taxi_reposition_api, handler_uri, pgsql, mockserver, now, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'offer_request',
            'mode_id': 'poi',
            'offer_id': '4q2VolejRejNmGQB',
        },
    )

    assert response.status_code == 200
    rows = select_named(
        """
        SELECT ignore_override_busy, start_router_info
        FROM state.sessions
        """,
        pgsql['reposition'],
    )
    assert rows == [
        {'ignore_override_busy': True, 'start_router_info': '(2261,15705)'},
    ]


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'zone_default.sql', 'mode_my_district.sql'],
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_ru': 'Базовая иерархия',
            'name_en': 'Basic hierarchy',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_ru': 'Россия',
            'name_en': 'Russia',
            'node_type': 'root',
            'parent_name': 'br_root',
        },
        {
            'name': 'br_moscow',
            'name_ru': 'Москва',
            'name_en': 'Moscow',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_spb',
            'name_ru': 'Санкт-Петербург',
            'name_en': 'Saint Petersburg',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['spb'],
        },
    ],
)
@pytest.mark.experiments3(
    name='reposition_check_geo_hierarchy_on_start',
    consumers=['reposition/sessions'],
    match={
        'consumers': [{'name': 'reposition/sessions'}],
        'predicate': {'type': 'true', 'init': {}},
        'enabled': True,
    },
    clauses=[
        {
            'title': 'main',
            'predicate': {'type': 'true', 'init': {}},
            'value': {'is_enabled': True, 'is_to_log': True},
        },
    ],
    default_value={'is_enabled': False, 'is_to_log': False},
)
async def test_start_geo_hierarchy_check(
        taxi_reposition_api, handler_uri, pgsql, mockserver, now, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.614883, 55.744124)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'in_area',
            'mode_id': 'my_district',
            'point': [30.362605, 59.929560],
            'radius': 3000,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'mode_home.sql', 'home_poi.sql', 'drivers.sql'],
)
async def test_start_undecodable_point_id(
        taxi_reposition_api, handler_uri, mockserver, testpoint,
):
    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'saved_point',
            'mode_id': 'home',
            'point_id': '539e4680f5fc4b33b61cdf9a632fd0f1',
        },
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid point_id'}


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.parametrize(
    'mode,point_id,result_point_id,tags_extension',
    [
        (
            'home',
            '4q2VolejRejNmGQB',
            '4q2Volej25ejNmGQ',
            timedelta(minutes=15),
        ),
        (
            'poi',
            'offer-4q2VolejRejNmGQB',
            'O3GWpmbk5XezJn4K',
            timedelta(minutes=5),
        ),
    ],
)
@pytest.mark.parametrize(
    'pedestrian,bicycle,navigation',
    [
        (False, False, None),
        (False, True, 'bicycle'),
        (True, False, 'pedestrian'),
        (True, True, 'undefined'),
    ],
)
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home_dynamic_navigation.sql',
        'mode_poi_offer_only.sql',
        'simple.sql',
        'tags_assignments_home.sql',
        'tags_assignments_poi.sql',
    ],
)
@pytest.mark.driver_tags_match(
    dbid='1488',
    uuid='driverSS',
    tags_info={'dynamic_navigation': {'topics': ['reposition']}},
)
async def test_start_postgres_point_id(
        taxi_config,
        taxi_reposition_api,
        handler_uri,
        mode,
        point_id,
        result_point_id,
        pgsql,
        mockserver,
        now,
        pedestrian,
        bicycle,
        navigation,
        tags_extension,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    taxi_config.set_values(
        dict(
            REPOSITION_API_CUSTOM_NAVIGATION_SETTINGS={
                'client_attributes_field': 'navigation',
                'pedestrian_navigation': 'pedestrian',
                'bicycle_navigation': 'bicycle',
                'undefined_navigation': 'undefined',
                'pedestrian_tags': (
                    ['dynamic_navigation'] if pedestrian else []
                ),
                'bicycle_tags': ['dynamic_navigation'] if bicycle else [],
            },
            REPOSITION_API_TAGS_TTL_EXTENSION={'__default__': 5, 'home': 15},
        ),
    )

    expected_response = {
        'state': {
            'state': {
                'mode_id': mode,
                'location': {
                    'id': result_point_id,
                    'point': [3.0, 4.0],
                    'address': {
                        'title': 'some address',
                        'subtitle': 'Postgresql',
                    },
                    'type': 'point',
                },
                'session_id': '4q2VolejRejNmGQB',
                'state_id': '4q2VolejRejNmGQB_active',
                'started_at': '2017-10-15T18:18:46+00:00',
                'finish_until': '2017-10-16T18:18:46+00:00',
                'status': 'active',
                'active_panel': {
                    'title': 'Active panel',
                    'subtitle': 'Active panel subtitle',
                },
                'finish_dialog': {
                    'title': 'Finish dialog',
                    'body': 'Finish dialog body',
                },
                'restrictions': [],
            },
            'usages': {
                'home': {
                    'start_screen_usages': {'title': '', 'subtitle': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'title': '', 'body': ''},
                },
                'poi': {
                    'start_screen_usages': {'title': '', 'subtitle': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'title': '', 'body': ''},
                },
            },
        },
        'state_etag': '"2Q5xmbmQijboKM7W"',
    }

    if mode == 'poi':
        expected_response['state']['state']['submode_id'] = 'fast'
        expected_response['state']['state']['description'] = 'description'
        expected_response['state']['state']['client_attributes'] = {}
        expected_response['state']['state']['offer'] = {
            'description': 'description',
            'destination_radius': 1000.0,
            'expires_at': '2017-10-16T18:18:46+00:00',
            'image_id': 'image',
            'offered_at': '2017-10-16T14:18:46+00:00',
            'restrictions': [],
        }
    elif mode == 'home':
        expected_response['state']['state']['client_attributes'] = {
            'dead10cc': 'deadbeef',
            'navigation': navigation,
        }

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={'type': 'saved_point', 'mode_id': mode, 'point_id': point_id},
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    expected_tags_rows = [
        {
            'driver_id': '(1488,driverSS)',
            'udid': None,
            'confirmation_token': 'reposition/4q2VolejRejNmGQB_append',
            'merge_policy': 'append',
            'tags': ['reposition_' + mode],
            'ttl': now + timedelta(days=1) + tags_extension,
            'provider': 'reposition',
            'created_at': now,
        },
    ]

    rows = select_named(
        """
        SELECT driver_id, udid, confirmation_token, merge_policy, tags, ttl,
        provider, created_at FROM state.uploading_tags
        INNER JOIN settings.driver_ids ON
        uploading_tags.driver_id_id = driver_ids.driver_id_id
        """,
        pgsql['reposition'],
    )

    assert rows == expected_tags_rows

    assert usages_count(pgsql['reposition']) == 2
    deadline = now + timedelta(days=1)
    if mode == 'home':
        check_points_table(
            pgsql['reposition'],
            1,
            101,
            'pg_point_1',
            'some address',
            'Postgresql',
        )
        check_watcher_table(
            pgsql['reposition'],
            session_id=1,
            arrival_id=1,
            antisurge_arrival_id=None,
            surge_arrival_id=1,
            duration_id=1,
            immobility_id=1,
            transporting_arrival_id=1,
        )
        check_sessions_table(
            pgsql['reposition'], 101, 1, session_deadline=deadline,
        )
    else:
        check_points_table(
            pgsql['reposition'],
            3,
            102,
            'pg_point_2',
            'some address',
            'Postgresql',
        )
        check_watcher_table(
            pgsql['reposition'],
            session_id=1,
            arrival_id=1,
            antisurge_arrival_id=1,
            surge_arrival_id=1,
            duration_id=1,
            immobility_id=1,
            transporting_arrival_id=1,
        )
        check_sessions_table(
            pgsql['reposition'], 102, 3, 1, session_deadline=deadline,
        )


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi_regular.sql',
        'simple.sql',
        'tags_assignments_poi.sql',
    ],
)
async def test_start_new_point(
        taxi_reposition_api, handler_uri, pgsql, mockserver, now, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'point': [3, 4],
            'address': {'title': 'Lenina st., 228', 'subtitle': 'Penza'},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'state': {
            'state': {
                'mode_id': 'poi',
                'submode_id': 'fast',
                'location': {
                    'id': '4q2VolejRejNmGQB',
                    'point': [3.0, 4.0],
                    'address': {
                        'title': 'Lenina st., 228',
                        'subtitle': 'Penza',
                    },
                    'type': 'point',
                },
                'session_id': '4q2VolejRejNmGQB',
                'state_id': '4q2VolejRejNmGQB_active',
                'started_at': '2017-10-15T18:18:46+00:00',
                'finish_until': '2017-10-16T18:18:46+00:00',
                'status': 'active',
                'active_panel': {
                    'title': 'Active panel',
                    'subtitle': 'Active panel subtitle',
                },
                'finish_dialog': {
                    'title': 'Finish dialog',
                    'body': 'Finish dialog body',
                },
                'description': 'Fast poi',
                'restrictions': [],
                'client_attributes': {},
            },
            'usages': {
                'home': {
                    'start_screen_usages': {'title': '', 'subtitle': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'title': '', 'body': ''},
                },
                'poi': {
                    'start_screen_usages': {'title': '', 'subtitle': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'title': '', 'body': ''},
                },
            },
        },
        'state_etag': '"2Q5xmbmQijboKM7W"',
    }

    expected_tags_rows = [
        {
            'driver_id': '(1488,driverSS)',
            'udid': None,
            'confirmation_token': 'reposition/4q2VolejRejNmGQB_append',
            'merge_policy': 'append',
            'tags': ['reposition_poi'],
            'ttl': now + timedelta(days=1),
            'provider': 'reposition',
            'created_at': now,
        },
    ]

    rows = select_named(
        """
        SELECT driver_id, udid, confirmation_token, merge_policy, tags, ttl,
        provider, created_at FROM state.uploading_tags
        INNER JOIN settings.driver_ids ON
        uploading_tags.driver_id_id = driver_ids.driver_id_id
        """,
        pgsql['reposition'],
    )

    assert rows == expected_tags_rows

    assert usages_count(pgsql['reposition']) == 2

    check_points_table(
        pgsql['reposition'], 3, city='Penza', address='Lenina st., 228',
    )
    check_watcher_table(
        pgsql['reposition'],
        session_id=1,
        arrival_id=1,
        antisurge_arrival_id=1,
        surge_arrival_id=1,
        duration_id=1,
        immobility_id=1,
        transporting_arrival_id=1,
    )
    check_sessions_table(
        pgsql['reposition'], 1, 3, 1, session_deadline=now + timedelta(days=1),
    )


@pytest.mark.now('2018-01-14T23:30:20')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.parametrize(
    'park_db_id,driver_id,clid_uuid,tag_uploads,error_code,data',
    [
        (
            'dbid777',
            '888',
            'clid777_888',
            0,
            400,
            {'error': 'no_attempts', 'message': 'Week usages exceeded'},
        ),
        (
            '1488',
            'driverSS',
            '1369_driverSS',
            1,
            200,
            {
                'state': {
                    'state': {
                        'mode_id': 'poi',
                        'location': {
                            'id': '4q2VolejRejNmGQB',
                            'point': [3.0, 4.0],
                            'address': {'title': '', 'subtitle': ''},
                            'type': 'point',
                        },
                        'session_id': '4q2VolejRejNmGQB',
                        'state_id': '4q2VolejRejNmGQB_active',
                        'started_at': '2018-01-14T23:30:20+00:00',
                        'status': 'active',
                        'active_panel': {
                            'title': 'Active panel',
                            'subtitle': 'Active panel subtitle',
                        },
                        'finish_dialog': {
                            'title': 'Finish dialog',
                            'body': 'Finish dialog body',
                        },
                        'restrictions': [],
                        'client_attributes': {},
                    },
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '0 of 2',
                                'subtitle': 'Today',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': 'Week usages exceeded',
                                'title': 'Usages limit exceeded',
                            },
                        },
                        'poi': {
                            'start_screen_usages': {
                                'title': '1 of 5',
                                'subtitle': 'This week',
                            },
                            'usage_allowed': False,
                            'usage_limit_dialog': {
                                'body': 'Day usages exceeded',
                                'title': 'Usages limit exceeded',
                            },
                        },
                    },
                },
                'state_etag': '"2Q5xmbmQijboKM7W"',
            },
        ),
        (
            '1488',
            'driverSS2',
            '1369_driverSS2',
            0,
            400,
            {'error': 'no_attempts', 'message': 'Day usages exceeded'},
        ),
    ],
)
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'home_poi.sql',
        'usages_week.sql',
        'tags_assignments_poi.sql',
    ],
)
async def test_start_around_midnight(
        taxi_reposition_api,
        handler_uri,
        park_db_id,
        driver_id,
        clid_uuid,
        tag_uploads,
        error_code,
        data,
        mockserver,
        pgsql,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers(park_db_id, driver_id),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == error_code
    assert response.json() == data

    count = select_named(
        'SELECT count(1) FROM state.uploading_tags', pgsql['reposition'],
    )[0]['count']

    assert count == tag_uploads


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2018-01-14T20:30:20')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'home_poi.sql',
        'usages.sql',
    ],
)
async def test_start_day_usages_exceeded(
        taxi_reposition_api, handler_uri, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'no_attempts',
        'message': 'Day usages exceeded',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2018-01-14T20:30:20')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'home_poi.sql',
        'usages.sql',
        'tags.sql',
        'tags_bonus_usages.sql',
        'tags_assignments_poi.sql',
    ],
)
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.driver_tags_match(
    dbid='1488',
    uuid='driverSS',
    tags_info={
        'selfemployed': {'topics': ['reposition']},
        'poi_prohibited': {'topics': ['reposition']},
    },
)
async def test_start_day_bonus_usages(
        taxi_reposition_api, handler_uri, mockserver, pgsql, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'state': {
            'state': {
                'mode_id': 'poi',
                'location': {
                    'id': '4q2VolejRejNmGQB',
                    'point': [3.0, 4.0],
                    'address': {'title': '', 'subtitle': ''},
                    'type': 'point',
                },
                'session_id': 'rm0wMvbmOeYAlO1n',
                'state_id': 'rm0wMvbmOeYAlO1n_active',
                'started_at': '2018-01-14T20:30:20+00:00',
                'status': 'active',
                'active_panel': {
                    'title': 'Active panel',
                    'subtitle': 'Active panel subtitle',
                },
                'finish_dialog': {
                    'title': 'Finish dialog',
                    'body': 'Finish dialog body',
                },
                'restrictions': [],
                'client_attributes': {},
            },
            'usages': {
                'home': {
                    'start_screen_usages': {
                        'title': '0 of 2',
                        'subtitle': 'Today',
                    },
                    'usage_allowed': True,
                    'usage_limit_dialog': {
                        'body': 'Week usages exceeded',
                        'title': 'Usages limit exceeded',
                    },
                },
                'poi': {
                    'start_screen_usages': {
                        'title': '4 of 5',
                        'subtitle': 'This week',
                    },
                    'usage_allowed': False,
                    'usage_limit_dialog': {
                        'body': 'Day usages exceeded',
                        'title': 'Usages limit exceeded',
                    },
                },
            },
        },
        'state_etag': '"2Q5xmbmQijboKM7W"',
    }

    count = select_named(
        'SELECT count(1) FROM state.uploading_tags', pgsql['reposition'],
    )[0]['count']

    assert count == 1


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'mode_home.sql', 'home_poi.sql', 'drivers.sql'],
)
async def test_start_point_too_close(
        taxi_reposition_api, handler_uri, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3, 4)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'point_too_close',
        'message': 'Requested point is too close',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2018-01-14T23:30:20')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'mode_my_district.sql', 'drivers.sql'],
)
async def test_start_point_too_close_in_area_mode(
        taxi_reposition_api, handler_uri, mockserver, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3, 4)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'in_area',
            'mode_id': 'my_district',
            'point': [3, 4],
            'radius': 5000,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'state': {
            'state': {
                'mode_id': 'my_district',
                'location': {
                    'id': '4q2VolejRejNmGQB',
                    'point': [3.0, 4.0],
                    'radius': 5000,
                    'type': 'circle',
                },
                'session_id': '4q2VolejRejNmGQB',
                'state_id': '4q2VolejRejNmGQB_active',
                'started_at': '2018-01-14T23:30:20+00:00',
                'status': 'active',
                'active_panel': {
                    'title': 'Active panel',
                    'subtitle': 'Active panel subtitle',
                },
                'finish_dialog': {
                    'title': 'Finish dialog',
                    'body': 'Finish dialog body',
                },
                'restrictions': [],
                'client_attributes': {},
            },
            'usages': {
                'my_district': {
                    'start_screen_usages': {'title': '', 'subtitle': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'title': '', 'body': ''},
                },
            },
        },
        'state_etag': '"2Q5xmbmQijboKM7W"',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'mode_home.sql', 'home_poi.sql', 'drivers.sql'],
)
async def test_start_point_too_distant(
        taxi_reposition_api, handler_uri, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(30, 40)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'point_too_distant',
        'message': 'Requested point is too distant',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'mode_home.sql', 'home_poi.sql', 'drivers.sql'],
)
async def test_start_no_coordinates(
        taxi_reposition_api, handler_uri, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return mockserver.make_response('NotFound', 404)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': 'no_coordinates',
        'message': 'Check GPS is working',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'mode_my_district_with_submodes.sql',
        'drivers.sql',
    ],
)
async def test_start_submode_duration_limit_exceed(
        taxi_reposition_api, handler_uri, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'in_area',
            'mode_id': 'my_district',
            'submode_id': '90',
            'point': [3, 4],
            'radius': 1488,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'mode_duration_exceeds_usage_limit',
        'message': 'Only submodes that are shorter than 1h are available',
    }


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.parametrize(
    'lon,lat,duration_id,arrival_id,immobility_id,surge_arrival_id,'
    'transporting_arrival_id,antisurge_arrival_id,submode',
    [
        # moscow
        (37.602429, 55.759690, None, 1, None, 1, 1, 1, None),
        (37.602429, 55.759690, None, 1, None, 1, 1, 1, 'fast'),
        (37.602429, 55.759690, None, None, 1, None, None, None, 'slow'),
        # __default__
        (3, 5, None, 1, None, 1, 1, 1, None),
        (3, 5, None, 1, None, 1, 1, 1, 'fast'),
        (3, 5, None, None, 1, None, None, None, 'slow'),
    ],
)
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'mode_home.sql',
        'submodes_home.sql',
        'start_rules.sql',
        'drivers.sql',
        'tags_assignments_home.sql',
    ],
)
async def test_start_bounded_rules(
        taxi_reposition_api,
        handler_uri,
        pgsql,
        lon,
        lat,
        duration_id,
        arrival_id,
        immobility_id,
        surge_arrival_id,
        transporting_arrival_id,
        antisurge_arrival_id,
        submode,
        mockserver,
        load,
        now,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(lon, lat)

    data = {
        'type': 'free_point',
        'mode_id': 'home',
        'address': {'title': '', 'subtitle': ''},
        'point': [lon + 0.1, lat + 0.1],
    }
    if submode:
        data['submode_id'] = submode

    response = await taxi_reposition_api.post(
        handler_uri, headers=get_headers('1488', 'driverSS'), json=data,
    )
    assert response.status_code == 200

    expected_tags_rows = [
        {
            'driver_id': '(1488,driverSS)',
            'udid': None,
            'confirmation_token': 'reposition/4q2VolejRejNmGQB_append',
            'merge_policy': 'append',
            'tags': ['reposition_home'],
            'provider': 'reposition',
            'ttl': None,
            'created_at': now,
        },
    ]

    rows = select_named(
        """
        SELECT driver_id, udid, confirmation_token, merge_policy, tags, ttl,
        provider, created_at FROM state.uploading_tags
        INNER JOIN settings.driver_ids ON
        uploading_tags.driver_id_id = driver_ids.driver_id_id
        """,
        pgsql['reposition'],
    )

    assert rows == expected_tags_rows


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'zone_default.sql', 'mode_my_district.sql'],
)
async def test_start_in_area_no_radius(
        taxi_reposition_api, handler_uri, pgsql, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'in_area',
            'mode_id': 'my_district',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 400

    actual = response.json()
    actual_message = actual['message']
    actual['message'] = actual_message[actual_message.find('Field') : :]

    expected = {'code': '400', 'message': 'Field \'radius\' is missing'}

    assert actual == expected


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'zone_default.sql', 'mode_home.sql'],
)
async def test_start_not_in_area_with_radius(
        taxi_reposition_api, handler_uri, pgsql, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'home',
            'point': [3, 4],
            'radius': 1488,
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'zone_default.sql', 'mode_my_district.sql'],
)
async def test_start_in_area(
        taxi_reposition_api, handler_uri, mockserver, pgsql, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'in_area',
            'mode_id': 'my_district',
            'point': [3, 4],
            'radius': 1488,
        },
    )
    assert response.status_code == 200

    rows = select_table_named(
        'settings.points', 'point_id', pgsql['reposition'],
    )
    assert rows[0]['area_radius'] == 1488

    check_sessions_table(
        db=pgsql['reposition'],
        point_id=1,
        mode_id=19,
        destination_radius=1488,
    )


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi_regular.sql',
        'simple.sql',
    ],
)
async def test_start_undefined_submode(
        taxi_reposition_api, handler_uri, pgsql, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'submode_id': 'undefined',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Submode \'undefined\' not found',
    }
    rows = select_table('state.sessions', 'session_id', pgsql['reposition'])
    assert len(rows) == 1


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'driver_work_modes.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi_regular.sql',
        'simple.sql',
    ],
)
async def test_start_forbidden_by_work_mode(
        taxi_reposition_api, handler_uri, pgsql, mockserver,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(32.1621, 51.127)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'point': [32.151, 51.121],
            'address': {'title': '', 'subtitle': ''},
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'error': 'temporary_blocked_mode',
        'message': 'Reposition is forbidden in your work mode',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi_regular.sql',
        'simple.sql',
    ],
)
async def test_start_existing_submode(
        taxi_reposition_api, handler_uri, pgsql, mockserver, now, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers('1488', 'driverSS2'),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'submode_id': 'fast',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == 200
    check_sessions_table(
        pgsql['reposition'], 1, 3, 1, session_deadline=now + timedelta(days=1),
    )
    check_watcher_table(
        pgsql['reposition'],
        session_id=1,
        duration_id=1,
        arrival_id=1,
        immobility_id=1,
        antisurge_arrival_id=1,
        surge_arrival_id=1,
        transporting_arrival_id=1,
    )


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.parametrize('case', range(1, 5))
@pytest.mark.parametrize('offer_origin', [None, 'relocator', 'atlas'])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_tags_assignments_match(
        taxi_reposition_api,
        handler_uri,
        mockserver,
        pgsql,
        load,
        case,
        offer_origin,
        now,
        testpoint,
):
    # case 1: tags assignments matched in zone and submode
    # case 2: tags assignments matched in zone and mode
    # case 3: tags assignments matched in __default__ and submode
    # case 4: tags assignments matched in __default__ and mode
    queries = []
    if offer_origin:
        queries.append(load('mode_poi_offer_only.sql'))
    else:
        queries.append(load('mode_poi_regular.sql'))
    queries.append(load('drivers.sql'))
    queries.append(load('default_moscow_zones.sql'))
    queries.append(load('mode_home.sql'))
    queries.append(load('simple.sql'))
    queries.append(load('offer_tags_assignments.sql'))
    queries.append(load('match_tags_assignments_case' + str(case) + '.sql'))
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.95969)

    request = {
        'type': 'offer_request' if offer_origin else 'free_point',
        'mode_id': 'poi',
        'submode_id': 'fast',
    }

    if offer_origin is not None:
        request['offer_id'] = (
            '4q2VolejNlejNmGQ'
            if offer_origin == 'relocator'
            else 'O3GWpmbkNEazJn4K'
        )
    else:
        request['address'] = {'title': '', 'subtitle': ''}
        request['point'] = [37.617664, 55.752121]

    response = await taxi_reposition_api.post(
        handler_uri, headers=get_headers('1488', 'driverSS2'), json=request,
    )
    assert response.status_code == 200

    expected_tags_rows = [
        {
            'driver_id': '(1488,driverSS2)',
            'udid': None,
            'confirmation_token': 'reposition/4q2VolejRejNmGQB_append',
            'merge_policy': 'append',
            'tags': ['expected_tag'],
            'ttl': now + timedelta(days=1),
            'provider': 'reposition',
            'created_at': now,
        },
    ]

    if offer_origin is not None:
        expected_tags_rows.append(
            {
                'driver_id': '(1488,driverSS2)',
                'udid': None,
                'confirmation_token': (
                    'reposition-' + offer_origin + '/4q2VolejRejNmGQB_append'
                ),
                'merge_policy': 'append',
                'tags': ['offer_session_tag'],
                'ttl': now + timedelta(days=1),
                'provider': 'reposition-' + offer_origin,
                'created_at': now,
            },
        )

    rows = select_named(
        """
        SELECT driver_id, udid, confirmation_token, merge_policy, tags, ttl,
        provider, created_at FROM state.uploading_tags
        INNER JOIN settings.driver_ids ON
        uploading_tags.driver_id_id = driver_ids.driver_id_id
        """,
        pgsql['reposition'],
    )

    rows.sort(key=lambda x: x['confirmation_token'])
    expected_tags_rows.sort(key=lambda x: x['confirmation_token'])

    for row in rows:
        row['tags'].sort()
    for row in expected_tags_rows:
        row['tags'].sort()

    assert rows == expected_tags_rows


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2018-01-14T23:30:20+00:00')
@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.parametrize(
    'park_db_id,driver_id,clid_uuid,expected_code,expected_response',
    [
        (
            'dbid777',
            '888',
            'clid777_888',
            400,
            {'error': 'no_attempts', 'message': 'Week usages exceeded'},
        ),
        (
            '1488',
            'driverSS',
            '1369_driverSS',
            200,
            {
                'state': {
                    'state': {
                        'mode_id': 'poi',
                        'location': {
                            'id': '4q2VolejRejNmGQB',
                            'point': [3.0, 4.0],
                            'address': {'title': '', 'subtitle': ''},
                            'type': 'point',
                        },
                        'session_id': '4q2VolejRejNmGQB',
                        'state_id': '4q2VolejRejNmGQB_active',
                        'started_at': '2018-01-14T23:30:20+00:00',
                        'status': 'active',
                        'active_panel': {
                            'title': 'Active panel',
                            'subtitle': 'Active panel subtitle',
                        },
                        'finish_dialog': {
                            'title': 'Finish dialog',
                            'body': 'Finish dialog body',
                        },
                        'restrictions': [],
                        'client_attributes': {},
                    },
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '0 of 2',
                                'subtitle': 'Today',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': 'Week usages exceeded',
                                'title': 'Usages limit exceeded',
                            },
                        },
                        'poi': {
                            'start_screen_usages': {
                                'title': '1 of 5',
                                'subtitle': 'This week',
                            },
                            'usage_allowed': False,
                            'usage_limit_dialog': {
                                'body': 'Day usages exceeded',
                                'title': 'Usages limit exceeded',
                            },
                        },
                    },
                },
                'state_etag': '"2Q5xmbmQijboKM7W"',
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'home_poi.sql',
        'usages_week.sql',
    ],
)
async def test_start_etag_data_write(
        taxi_reposition_api,
        handler_uri,
        taxi_config,
        pgsql,
        park_db_id,
        driver_id,
        clid_uuid,
        expected_code,
        expected_response,
        mockserver,
        load_json,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        handler_uri,
        headers=get_headers(park_db_id, driver_id),
        json={
            'type': 'free_point',
            'mode_id': 'poi',
            'address': {'title': '', 'subtitle': ''},
            'point': [3, 4],
        },
    )
    assert response.status_code == expected_code
    assert response.json() == expected_response

    rows = select_named(
        'SELECT driver_id, valid_since, data FROM etag_data.states '
        'INNER JOIN settings.driver_ids '
        'ON states.driver_id_id = driver_ids.driver_id_id '
        'ORDER BY driver_id, revision',
        pgsql['reposition'],
    )

    if expected_code == 200:
        assert rows == [
            {
                'data': {
                    'state': {
                        'mode_id': 'poi',
                        'location': {
                            'id': '4q2VolejRejNmGQB',
                            'point': [3.0, 4.0],
                            'address': {'title': '', 'subtitle': ''},
                            'type': 'point',
                        },
                        'session_id': '4q2VolejRejNmGQB',
                        'state_id': '4q2VolejRejNmGQB_active',
                        'started_at': '2018-01-14T23:30:20+00:00',
                        'status': 'active',
                        'active_panel': {
                            'title': '{"tanker_key":"poi"}',
                            'subtitle': '{"tanker_key":"poi"}',
                        },
                        'finish_dialog': {
                            'title': '{"tanker_key":"poi"}',
                            'body': '{"tanker_key":"poi"}',
                        },
                        'restrictions': [],
                        'client_attributes': {},
                    },
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': (
                                    '{"tanker_key":"home","period":"day",'
                                    '"used_count":0,"limit_count":2}'
                                ),
                                'subtitle': (
                                    '{"tanker_key":"home","period":"day"}'
                                ),
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': (
                                    '{"tanker_key":"home","period":"week"}'
                                ),
                                'title': '{"tanker_key":"home"}',
                            },
                        },
                        'poi': {
                            'start_screen_usages': {
                                'title': (
                                    '{"tanker_key":"poi",'
                                    '"period":"week","used_count":1,'
                                    '"limit_count":5}'
                                ),
                                'subtitle': (
                                    '{"tanker_key":"poi","period":"week"}'
                                ),
                            },
                            'usage_allowed': False,
                            'usage_limit_dialog': {
                                'body': '{"tanker_key":"poi","period":"day"}',
                                'title': '{"tanker_key":"poi"}',
                            },
                        },
                    },
                },
                'driver_id': '(1488,driverSS)',
                'valid_since': datetime(2018, 1, 14, 23, 30, 20),
            },
            {
                'data': {
                    'state': {
                        'mode_id': 'poi',
                        'location': {
                            'id': '4q2VolejRejNmGQB',
                            'point': [3.0, 4.0],
                            'address': {'title': '', 'subtitle': ''},
                            'type': 'point',
                        },
                        'session_id': '4q2VolejRejNmGQB',
                        'state_id': '4q2VolejRejNmGQB_active',
                        'started_at': '2018-01-14T23:30:20+00:00',
                        'status': 'active',
                        'active_panel': {
                            'title': '{"tanker_key":"poi"}',
                            'subtitle': '{"tanker_key":"poi"}',
                        },
                        'finish_dialog': {
                            'title': '{"tanker_key":"poi"}',
                            'body': '{"tanker_key":"poi"}',
                        },
                        'restrictions': [],
                        'client_attributes': {},
                    },
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': (
                                    '{"tanker_key":"home","period":"day",'
                                    '"used_count":0,"limit_count":2}'
                                ),
                                'subtitle': (
                                    '{"tanker_key":"home","period":"day"}'
                                ),
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': (
                                    '{"tanker_key":"home","period":"week"}'
                                ),
                                'title': '{"tanker_key":"home"}',
                            },
                        },
                        'poi': {
                            'start_screen_usages': {
                                'title': (
                                    '{"tanker_key":"poi","period":"day",'
                                    '"used_count":0,"limit_count":1}'
                                ),
                                'subtitle': (
                                    '{"tanker_key":"poi","period":"day"}'
                                ),
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': '{"tanker_key":"poi","period":"week"}',
                                'title': '{"tanker_key":"poi"}',
                            },
                        },
                    },
                },
                'driver_id': '(1488,driverSS)',
                'valid_since': datetime(2018, 1, 15, 21, 0),
            },
            {
                'data': {
                    'state': {
                        'mode_id': 'poi',
                        'location': {
                            'id': '4q2VolejRejNmGQB',
                            'point': [3.0, 4.0],
                            'address': {'title': '', 'subtitle': ''},
                            'type': 'point',
                        },
                        'session_id': '4q2VolejRejNmGQB',
                        'state_id': '4q2VolejRejNmGQB_active',
                        'started_at': '2018-01-14T23:30:20+00:00',
                        'status': 'active',
                        'active_panel': {
                            'title': '{"tanker_key":"poi"}',
                            'subtitle': '{"tanker_key":"poi"}',
                        },
                        'finish_dialog': {
                            'title': '{"tanker_key":"poi"}',
                            'body': '{"tanker_key":"poi"}',
                        },
                        'restrictions': [],
                        'client_attributes': {},
                    },
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': (
                                    '{"tanker_key":"home","period":"day",'
                                    '"used_count":0,"limit_count":2}'
                                ),
                                'subtitle': (
                                    '{"tanker_key":"home","period":"day"}'
                                ),
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': (
                                    '{"tanker_key":"home","period":"week"}'
                                ),
                                'title': '{"tanker_key":"home"}',
                            },
                        },
                        'poi': {
                            'start_screen_usages': {
                                'title': (
                                    '{"tanker_key":"poi","period":"day",'
                                    '"used_count":0,"limit_count":1}'
                                ),
                                'subtitle': (
                                    '{"tanker_key":"poi","period":"day"}'
                                ),
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {
                                'body': '{"tanker_key":"poi","period":"week"}',
                                'title': '{"tanker_key":"poi"}',
                            },
                        },
                    },
                },
                'driver_id': '(1488,driverSS)',
                'valid_since': datetime(2018, 1, 21, 21, 0),
            },
        ]
