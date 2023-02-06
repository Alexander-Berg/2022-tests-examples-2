# pylint: disable=import-only-modules
from datetime import datetime
from datetime import timedelta

import pytest

from .utils import select_named


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


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'check_rules.sql',
        'active_session.sql',
        'tags_assignments_poi.sql',
    ],
)
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {'poi': ['stop']},
    },
)
@pytest.mark.parametrize('with_driver_info', [False, True])
@pytest.mark.parametrize('send_push', [False, True])
async def test_stop(
        taxi_reposition_api,
        taxi_config,
        pgsql,
        mockserver,
        now,
        with_driver_info,
        send_push,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    data = (
        {'type': 'driver', 'park_id': 'dbid777', 'driver_profile_id': 'uuid'}
        if with_driver_info
        else {'type': 'session', 'session_id': 'QZOpnelYYgaKBzyV'}
    )

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/session/stop', json=data,
    )
    assert response.status_code == 200

    expected_tags_rows = [
        {
            'driver_id': '(dbid777,uuid)',
            'udid': None,
            'confirmation_token': 'reposition/QZOpnelYYgaKBzyV_remove',
            'merge_policy': 'remove',
            'tags': ['reposition_poi'],
            'ttl': None,
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

    rows = select_named(
        'SELECT session_id, active, point_id, start, "end", completed, '
        'driver_id '
        'FROM state.sessions NATURAL JOIN settings.driver_ids '
        'ORDER BY session_id',
        pgsql['reposition'],
    )

    assert rows == [
        {
            'session_id': 2001,
            'active': True,
            'point_id': 101,
            'start': datetime(2018, 10, 11, 16, 1, 11, 540859),
            'end': datetime(2018, 10, 11, 16, 2, 11, 540859),
            'completed': False,
            'driver_id': '(dbid777,888)',
        },
        {
            'session_id': 2002,
            'active': True,
            'point_id': 102,
            'start': datetime(2018, 10, 12, 15, 40, 11, 540859),
            'end': datetime(2018, 10, 12, 16, 4, 11, 540859),
            'completed': False,
            'driver_id': '(dbid777,uuid)',
        },
        {
            'session_id': 2003,
            'active': True,
            'point_id': 102,
            'start': datetime(2018, 10, 12, 16, 5, 11, 540859),
            'end': datetime(2018, 10, 15, 18, 18, 46),
            'completed': True,
            'driver_id': '(dbid777,uuid)',
        },
        {
            'session_id': 2004,
            'active': True,
            'point_id': 103,
            'start': datetime(2018, 10, 12, 16, 5, 11, 540859),
            'end': None,
            'completed': False,
            'driver_id': '(dbid777,uuid1)',
        },
        {
            'session_id': 2005,
            'active': True,
            'point_id': 104,
            'start': datetime(2018, 10, 12, 16, 5, 11, 540859),
            'end': None,
            'completed': False,
            'driver_id': '(dbid777,uuid2)',
        },
        {
            'session_id': 2006,
            'active': True,
            'point_id': 105,
            'start': datetime(2018, 10, 12, 16, 5, 11, 540859),
            'end': None,
            'completed': False,
            'driver_id': '(dbid777,uuid3)',
        },
        {
            'session_id': 2007,
            'active': True,
            'point_id': 105,
            'start': datetime(2018, 10, 12, 16, 3, 11, 540859),
            'end': datetime(2018, 10, 12, 16, 4),
            'completed': False,
            'driver_id': '(dbid777,uuid)',
        },
        {
            'session_id': 2008,
            'active': True,
            'point_id': 101,
            'start': datetime(2018, 10, 12, 15, 59, 0, 540859),
            'end': datetime(2018, 10, 12, 16, 4, 11, 540859),
            'completed': False,
            'driver_id': '(dbid777,888)',
        },
        {
            'session_id': 2009,
            'active': True,
            'point_id': 102,
            'start': datetime(2018, 10, 12, 16, 3, 45, 540859),
            'end': datetime(2018, 10, 12, 16, 4, 45, 540859),
            'completed': False,
            'driver_id': '(dbid777,uuid)',
        },
    ]

    rows = select_named(
        'SELECT event_id, event_type, driver_id_id, occured_at, tags, '
        'extra_data '
        'FROM state.uploading_reposition_events',
        pgsql['reposition'],
    )
    assert rows == [
        {
            'event_id': 1,
            'event_type': 'stop',
            'driver_id_id': 8,
            'occured_at': datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['completed', 'poi'],
            'extra_data': {
                'session_id': 'QZOpnelYYgaKBzyV',
                'status': 'no_state',
                'state_id': 'QZOpnelYYgaKBzyV_no_state',
                'disable_reason': 'client_stop',
                'source_zones': [],
                'destination_zones': [],
                'stop_zones': [],
            },
        },
    ]


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'check_rules.sql',
        'active_session.sql',
        'tags_assignments_poi.sql',
    ],
)
async def test_stop_insert_to_reposition_watcher(
        taxi_reposition_api, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/session/stop',
        json={'type': 'session', 'session_id': 'QZOpnelYYgaKBzyV'},
    )

    assert response.status_code == 200
    cursor = pgsql['reposition'].cursor()
    query = 'SELECT is_stop_action FROM state.sessions_to_reposition_watcher'
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] is True


async def test_stop_non_existent(taxi_reposition_api, mockserver, testpoint):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/session/stop',
        json={'type': 'session', 'session_id': 'QZOpnelYYgaKqqyV'},
    )
    assert response.status_code == 200


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {'home': ['stop']},
    },
)
@pytest.mark.parametrize('offer_origin', [None, 'relocator', 'atlas'])
@pytest.mark.parametrize(
    'dbid, uuid, home_has_bonus, confirmation_key, match_id, session_id',
    [
        (
            'dbid777',
            'uuid1',
            True,
            '/4q2VolejNlejNmGQ_completed_append',
            '000000000000000000000009',
            '4q2VolejNlejNmGQ',
        ),
        (
            'dbid777',
            'uuid2',
            True,
            '/O3GWpmbkNEazJn4K_completed_append',
            '000000000000000000000010',
            'O3GWpmbkNEazJn4K',
        ),
        ('dbid777', 'uuid2', False, None, None, 'O3GWpmbkNEazJn4K'),
        (
            'dbid777',
            'uuid3',
            True,
            '/PQZOpnelNrbKBzyV_completed_append',
            '000000000000000000000011',
            'PQZOpnelNrbKBzyV',
        ),
    ],
)
async def test_stop_completed_tags_assignments(
        taxi_reposition_api,
        pgsql,
        mockserver,
        load,
        offer_origin,
        dbid,
        uuid,
        home_has_bonus,
        confirmation_key,
        match_id,
        session_id,
        now,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    queries = [
        load('zone_default.sql'),
        load('mode_home.sql'),
        load('home_completed_tags_assignments.sql'),
        load('drivers.sql'),
        load(
            'complete_'
            + ((offer_origin + '_offers_') if offer_origin is not None else '')
            + 'active_sessions.sql',
        ),
        load(
            'non_complete_'
            + ((offer_origin + '_offers_') if offer_origin is not None else '')
            + 'active_sessions.sql',
        ),
    ]
    if home_has_bonus:
        queries.append(load('home_bonus.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/session/stop',
        json={'type': 'session', 'session_id': session_id},
    )
    assert response.status_code == 200

    if confirmation_key is None:
        count = select_named(
            'SELECT count(*) FROM state.uploading_tags', pgsql['reposition'],
        )[0]['count']
        assert count == 0
        return

    expected_tags_rows = [
        {
            'driver_id': '(' + dbid + ',' + uuid + ')',
            'udid': None,
            'confirmation_token': 'reposition' + confirmation_key,
            'merge_policy': 'append',
            'tags': [
                'default_home_completed_tag1',
                'default_home_completed_tag2',
            ],
            'ttl': now + timedelta(minutes=10),
            'provider': 'reposition',
            'created_at': now,
        },
    ]

    if offer_origin is not None:
        expected_tags_rows.append(
            {
                'driver_id': '(' + dbid + ',' + uuid + ')',
                'udid': None,
                'confirmation_token': (
                    'reposition-' + offer_origin + confirmation_key
                ),
                'merge_policy': 'append',
                'tags': ['offer_session_tag'],
                'ttl': now + timedelta(minutes=10),
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

    rows = select_named(
        'SELECT event_id, event_type, driver_id_id, occured_at, tags, '
        'extra_data '
        'FROM state.uploading_reposition_events',
        pgsql['reposition'],
    )
    assert rows == [
        {
            'event_id': 1,
            'event_type': 'stop',
            'driver_id_id': int(match_id),
            'occured_at': datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['completed', 'home'],
            'extra_data': {
                'session_id': session_id,
                'status': 'bonus',
                'state_id': session_id + '_bonus',
                'disable_reason': 'client_stop',
                'source_zones': [],
                'destination_zones': [],
                'stop_zones': [],
            },
        },
    ]


@pytest.mark.now('2018-01-14T23:30:20')
@pytest.mark.parametrize('home_has_bonus', [False, True])
async def test_stop_etag_data_write(
        taxi_reposition_api,
        pgsql,
        home_has_bonus,
        mockserver,
        load,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    queries = [
        load('zone_default.sql'),
        load('mode_home.sql'),
        load('drivers.sql'),
        load('complete_active_sessions.sql'),
    ]
    if home_has_bonus:
        queries.append(load('home_bonus.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/session/stop',
        json={'type': 'session', 'session_id': 'O3GWpmbkNEazJn4K'},
    )
    assert response.status_code == 200

    rows = select_named(
        """
        SELECT driver_id, valid_since, data FROM etag_data.states
        INNER JOIN settings.driver_ids
        ON states.driver_id_id = driver_ids.driver_id_id
        ORDER BY driver_id, revision
        """,
        pgsql['reposition'],
    )

    if not home_has_bonus:
        assert rows == [
            {
                'driver_id': '(dbid777,uuid2)',
                'valid_since': datetime(2018, 1, 14, 23, 30, 20),
                'data': {
                    'state': {'status': 'no_state'},
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '',
                                'subtitle': '',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {'title': '', 'body': ''},
                        },
                    },
                },
            },
            {
                'driver_id': '(dbid777,uuid2)',
                'valid_since': datetime(2018, 1, 15, 0, 0, 0),
                'data': {
                    'state': {'status': 'no_state'},
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '',
                                'subtitle': '',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {'title': '', 'body': ''},
                        },
                    },
                },
            },
        ]
    elif home_has_bonus:
        assert rows == [
            {
                'driver_id': '(dbid777,uuid2)',
                'valid_since': datetime(2018, 1, 14, 23, 30, 20),
                'data': {
                    'state': {
                        'bonus': {
                            'mode_id': 'home',
                            'expires_at': '2018-01-14T23:40:20+00:00',
                            'headline': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}'
                                ),
                            },
                            'icon_id': 'image',
                            'session_id': 'O3GWpmbkNEazJn4K',
                            'started_at': '2018-01-14T23:30:20+00:00',
                            'subline': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}'
                                ),
                            },
                            'client_attributes': {'dead10cc': 'deadbeef'},
                        },
                        'status': 'bonus',
                        'state_id': 'O3GWpmbkNEazJn4K_bonus',
                    },
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '',
                                'subtitle': '',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {'title': '', 'body': ''},
                        },
                    },
                },
            },
            {
                'driver_id': '(dbid777,uuid2)',
                'valid_since': datetime(2018, 1, 14, 23, 40, 20),
                'data': {
                    'state': {'status': 'no_state'},
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '',
                                'subtitle': '',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {'title': '', 'body': ''},
                        },
                    },
                },
            },
            {
                'driver_id': '(dbid777,uuid2)',
                'valid_since': datetime(2018, 1, 15, 0, 0),
                'data': {
                    'state': {'status': 'no_state'},
                    'usages': {
                        'home': {
                            'start_screen_usages': {
                                'title': '',
                                'subtitle': '',
                            },
                            'usage_allowed': True,
                            'usage_limit_dialog': {'title': '', 'body': ''},
                        },
                    },
                },
            },
        ]


@pytest.mark.now('2020-09-01T12:00:00')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'zone_default.sql',
        'airport_session.sql',
    ],
)
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {'home': ['stop']},
    },
)
@pytest.mark.parametrize('tvm_enabled', [False, True])
async def test_airport(
        taxi_config,
        taxi_reposition_api,
        mockserver,
        load,
        pgsql,
        tvm_enabled,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    taxi_config.set_values(
        dict(
            TVM_ENABLED=tvm_enabled,
            TVM_RULES=[{'src': 'dispatch-airport', 'dst': 'reposition-api'}],
            TVM_SERVICE_HANDLER_ACCESS_ENABLED=True,
            TVM_SERVICE_HANDLER_ACCESS={
                'reposition-api': {
                    '/internal/reposition-api/v1/service/session/stop': [
                        'dispatch-airport',
                    ],
                },
            },
        ),
    )

    # Generated by tvmknife: tvmknife unittest service -s 235 -d 2345
    ticket_dispatch_airport = (
        '3:serv:CBAQ__________9_IgYI6wEQqRI:KTU_rajrKPzMehPt7OXF8y9NXi'
        'XOZFfQTwq8u4YBEN2Kd0QL1EbUi9ZC3D3askYSUJeGQQxglnj5IcHlrAchmqw'
        '12IHO0EGyZrTTwzJjRR1qJ-B0OCYSauUrpQLVcegMnvjAVLfJaSuYwx_zuCl2'
        'wbdbZcgjJ_UgbjUUtTn0wm4'
    )

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/session/stop',
        headers={'X-Ya-Service-Ticket': ticket_dispatch_airport},
        json={'type': 'session', 'session_id': 'O3GWpmbkNEazJn4K'},
    )

    assert response.status_code == 200

    rows = select_named(
        'SELECT event, session_id FROM state.events', pgsql['reposition'],
    )

    assert rows == (
        [{'session_id': 1002, 'event': 'AirportStop'}] if tvm_enabled else []
    )

    rows = select_named(
        'SELECT session_id, completed FROM state.sessions',
        pgsql['reposition'],
    )

    assert rows == [{'session_id': 1002, 'completed': tvm_enabled}]

    rows = select_named(
        'SELECT event_id, event_type, driver_id_id, occured_at, tags, '
        'extra_data '
        'FROM state.uploading_reposition_events',
        pgsql['reposition'],
    )
    assert rows == [
        {
            'event_id': 1,
            'event_type': 'stop',
            'driver_id_id': 10,
            'occured_at': datetime(2020, 9, 1, 12, 0, 0),
            'tags': ['completed', 'home'] if tvm_enabled else ['home'],
            'extra_data': {
                'session_id': 'O3GWpmbkNEazJn4K',
                'status': 'no_state',
                'state_id': 'O3GWpmbkNEazJn4K_no_state',
                'disable_reason': 'arrival' if tvm_enabled else 'client_stop',
                'source_zones': [],
                'destination_zones': [],
                'stop_zones': [],
            },
        },
    ]
