from datetime import datetime
from datetime import timedelta

import pytest

from .reposition_select import select_named


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
    REPOSITION_EVENTS_UPLOADER_MODE_TYPES_WHITELIST={'poi': ['stop']},
)
@pytest.mark.parametrize('with_driver_info', [False, True])
@pytest.mark.parametrize('send_push', [False, True])
@pytest.mark.now('2018-10-15T18:18:46')
def test_stop(
        taxi_reposition,
        config,
        pgsql,
        mockserver,
        now,
        with_driver_info,
        send_push,
        testpoint,
):
    config.set_values(dict(REPOSITION_DATA_UPDATE_PUSH_ENABLED=send_push))

    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    data = (
        {'type': 'driver', 'park_db_id': 'dbid777', 'driver_id': 'uuid'}
        if with_driver_info
        else {'type': 'session', 'session_id': 'QZOpnelYYgaKBzyV'}
    )

    response = taxi_reposition.post('/v1/service/session/stop', json=data)
    assert response.status_code == 200
    assert response.json() == {}

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
@pytest.mark.now('2018-10-15T18:18:46')
def test_stop_insert_to_reposition_watcher(
        taxi_reposition, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = taxi_reposition.post(
        '/v1/service/session/stop',
        json={'type': 'session', 'session_id': 'QZOpnelYYgaKBzyV'},
    )

    assert response.status_code == 200
    cursor = pgsql['reposition'].cursor()
    query = 'SELECT is_stop_action FROM state.sessions_to_reposition_watcher'
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] is True


def test_stop_non_existent(taxi_reposition, mockserver, testpoint):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = taxi_reposition.post(
        '/v1/service/session/stop',
        json={'type': 'session', 'session_id': 'QZOpnelYYgaKqqyV'},
    )
    assert response.status_code == 200
    assert response.json() == {}


def test_stop_with_additional_properties(taxi_reposition):
    response = taxi_reposition.post(
        '/v1/service/session/stop',
        json={
            'type': 'session',
            'session_id': 'QZOpnelYYgaKBzyV',
            'ugly_additional_property_author': 'Kotomord',
        },
    )
    assert response.status_code == 400


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_EVENTS_UPLOADER_MODE_TYPES_WHITELIST={'home': ['stop']},
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
def test_stop_completed_tags_assignments(
        taxi_reposition,
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
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

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

    response = taxi_reposition.post(
        '/v1/service/session/stop',
        json={'type': 'session', 'session_id': session_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

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
def test_stop_etag_data_write(
        taxi_reposition,
        config,
        pgsql,
        home_has_bonus,
        mockserver,
        load_json,
        load,
        testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    queries = [
        load('zone_default.sql'),
        load('mode_home.sql'),
        load('drivers.sql'),
        load('complete_active_sessions.sql'),
    ]
    if home_has_bonus:
        queries.append(load('home_bonus.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = taxi_reposition.post(
        '/v1/service/session/stop',
        json={'type': 'session', 'session_id': 'O3GWpmbkNEazJn4K'},
    )
    assert response.status_code == 200
    assert response.json() == {}

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
                                    '"tanker_key":"bonus.tanker"}\n'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}\n'
                                ),
                            },
                            'icon_id': 'image',
                            'session_id': 'O3GWpmbkNEazJn4K',
                            'started_at': '2018-01-14T23:30:20+00:00',
                            'subline': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}\n'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home",'
                                    '"tanker_key":"bonus.tanker"}\n'
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
@pytest.mark.parametrize('tvm_enabled', [False, True])
def test_airport(
        config,
        taxi_reposition,
        mockserver,
        load,
        pgsql,
        tvm_enabled,
        testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    config.set_values(
        dict(
            TVM_ENABLED=tvm_enabled,
            TVM_RULES=[{'src': 'dispatch-airport', 'dst': 'reposition'}],
            TVM_SERVICE_HANDLER_ACCESS_ENABLED=True,
            TVM_SERVICE_HANDLER_ACCESS={
                'reposition': {
                    '/v1/service/session/stop': ['dispatch-airport'],
                },
            },
        ),
    )

    response = taxi_reposition.post(
        '/v1/service/session/stop',
        headers={'X-Ya-Service-Ticket': load('tvm2_ticket_57_18')},
        json={'type': 'session', 'session_id': 'O3GWpmbkNEazJn4K'},
    )

    assert response.status_code == 200
    assert response.json() == {}

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


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'header_data, error_text',
    [
        ({}, 'header X-Ya-Service-Ticket is absent'),
        ({'X-Ya-Service-Ticket': ''}, 'header X-Ya-Service-Ticket is absent'),
        ({'X-Ya-Service-Ticket': 'INVALID-TOKEN-VALUE'}, 'invalid ticket'),
    ],
)
def test_check_tvm2(header_data, error_text, taxi_reposition):
    response = taxi_reposition.post(
        '/v1/service/session/stop', headers=header_data, data={},
    )
    assert response.status_code == 401
    assert response.json() == {'error': {'text': error_text}}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
    TVM_SERVICE_HANDLER_ACCESS_ENABLED=True,
)
@pytest.mark.parametrize(
    'service_access',
    [
        ({'reposition': {'/v1/service/session/stop': []}}),
        ({'reposition': {'/v1/service/session/stop': ['protocol']}}),
    ],
)
def test_check_tvm2_access_deny(taxi_reposition, config, service_access, load):
    config.set_values(dict(TVM_SERVICE_HANDLER_ACCESS=service_access))
    response = taxi_reposition.post(
        '/v1/service/session/stop',
        headers={'X-Ya-Service-Ticket': load('tvm2_ticket_19_18')},
        data={},
    )
    assert response.status_code == 401
    assert response.json() == {'error': {'text': 'Unauthorized'}}


@pytest.mark.parametrize(
    'tvm_enabled,tvm_header,service_access_enabled,service_access',
    [
        (False, True, False, None),
        (True, True, False, None),
        (True, True, True, {}),
        (True, True, True, {'reposition': {}}),
        (
            True,
            True,
            True,
            {'reposition': {'/v1/service/session/stop': ['driver_protocol']}},
        ),
    ],
)
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
    ],
)
def test_check_tvm2_access_allow(
        config,
        tvm_enabled,
        tvm_header,
        service_access_enabled,
        service_access,
        taxi_reposition,
        load,
):
    config.set_values(
        dict(
            TVM_ENABLED=tvm_enabled,
            TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
            TVM_SERVICE_HANDLER_ACCESS_ENABLED=service_access_enabled,
            TVM_SERVICE_HANDLER_ACCESS=service_access
            if service_access
            else {},
        ),
    )
    response = taxi_reposition.post(
        '/v1/service/session/stop',
        headers={'X-Ya-Service-Ticket': load('tvm2_ticket_19_18')},
        json={'type': 'session', 'session_id': 'O3GWpmbkNEazJn4K'},
    )
    assert response.status_code == 200
    assert response.json() == {}
