# pylint: disable=import-only-modules
from datetime import datetime

import pytest

from .utils import select_named


BACKWARD_COMPATIBLE_URI = '/driver/v1/v2/reposition/stop'
NEW_URI = '/driver/v1/reposition/v2/stop'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': 'dbid777',
    'X-YaTaxi-Driver-Profile-Id': 'uuid',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}


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
        'zones_whitelist': ['moscow'],
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_stop(taxi_reposition_api, handler_uri, pgsql, mockserver, now):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    response = await taxi_reposition_api.post(
        handler_uri, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'state_etag': '"2Q5xmbmQijboKM7W"',
        'state': {
            'state': {'status': 'no_state'},
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
    }

    expected_tags_rows = [
        {
            'driver_id': '(dbid777,uuid)',
            'udid': None,
            'confirmation_token': 'reposition/QZOpnelYYgaKBzyV_remove',
            'merge_policy': 'remove',
            'tags': ['reposition_poi'],
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
                'destination_zones': ['moscow'],
                'stop_zones': ['moscow'],
            },
        },
    ]


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_stop_non_existent(taxi_reposition_api, handler_uri, mockserver):
    response = await taxi_reposition_api.post(
        handler_uri, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 404


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.pgsql('reposition', files=['drivers.sql'])
async def test_stop_no_session(taxi_reposition_api, handler_uri, mockserver):
    response = await taxi_reposition_api.post(
        handler_uri, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 410
    assert response.json() == {
        'error': 'no_session',
        'message': 'Driver has not any active session',
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2019-01-01T09:01:10')
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
        'poi_bonus.sql',
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
@pytest.mark.parametrize('feedback_exp_enabled', [False, True])
async def test_stop_has_bonus(
        taxi_reposition_api,
        handler_uri,
        mockserver,
        pgsql,
        experiments3,
        feedback_exp_enabled,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    experiments3.add_config(
        name='reposition_api_show_feedback_panel',
        consumers=['reposition-api/feedback-panel'],
        match={
            'consumers': [{'name': 'reposition-api/feedback-panel'}],
            'predicate': {'type': 'true', 'init': {}},
            'enabled': feedback_exp_enabled,
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'choices_by_disable_reason': {
                        'client_stop': {
                            'items': [
                                {
                                    'score': 1,
                                    'is_choice_required': False,
                                    'is_comment_required': False,
                                    'is_comment_available': False,
                                    'choices': ['no_orders'],
                                },
                            ],
                        },
                    },
                },
            },
        ],
    )

    response = await taxi_reposition_api.post(
        handler_uri, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'state_etag': '"2Q5xmbmQijboKM7W"',
        'state': {
            'state': {
                'bonus': {
                    'mode_id': 'poi',
                    'expires_at': '2019-01-01T10:01:10+00:00',
                    'headline': {
                        'title': 'Bonus headline title for poi',
                        'subtitle': 'Bonus headline subtitle for poi',
                    },
                    'icon_id': 'bonus_image',
                    'session_id': 'QZOpnelYYgaKBzyV',
                    'started_at': '2019-01-01T09:01:10+00:00',
                    'subline': {
                        'title': 'Bonus subline title for poi',
                        'subtitle': 'Bonus subline subtitle for poi',
                    },
                    'client_attributes': {},
                },
                'status': 'bonus',
                'state_id': 'QZOpnelYYgaKBzyV_bonus',
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
    }

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
            'occured_at': datetime(2019, 1, 1, 9, 1, 10),
            'tags': ['completed', 'poi'],
            'extra_data': {
                'session_id': 'QZOpnelYYgaKBzyV',
                'status': 'bonus',
                'state_id': 'QZOpnelYYgaKBzyV_bonus',
                'disable_reason': 'client_stop',
                'source_zones': [],
                'destination_zones': [],
                'stop_zones': [],
            },
        },
    ]

    feedback_data = select_named(
        'SELECT session_id, data FROM state.driver_feedback_data',
        pgsql['reposition'],
    )
    assert feedback_data == (
        [
            {
                'session_id': 2003,
                'data': {
                    'items': [
                        {
                            'score': 1,
                            'choices': ['no_orders'],
                            'is_choice_required': False,
                            'is_comment_available': False,
                            'is_comment_required': False,
                        },
                    ],
                },
            },
        ]
        if feedback_exp_enabled
        else []
    )

    states = select_named(
        'SELECT revision, data FROM etag_data.states', pgsql['reposition'],
    )
    assert len(states) == (5 if feedback_exp_enabled else 4)

    feedback_panel_state_rev = 0
    for state in states:
        if (
                feedback_panel_state_rev > 0
                and state['revision'] == feedback_panel_state_rev + 1
        ):
            assert 'session_score' not in state['data']['state']

        if 'session_score' in state['data']['state']:
            feedback_panel_state_rev = state['revision']

    assert (feedback_panel_state_rev > 0) == feedback_exp_enabled


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
@pytest.mark.now('2018-01-14T20:30:40')
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
        'tag_default.sql',
        'usage_rules.sql',
        'usages.sql',
    ],
)
async def test_stop_has_usages(taxi_reposition_api, handler_uri, mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    response = await taxi_reposition_api.post(
        handler_uri, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'state_etag': '"2Q5xmbmQijboKM7W"',
        'state': {
            'state': {'status': 'no_state'},
            'usages': {
                'home': {
                    'start_screen_usages': {
                        'title': '3 of 5',
                        'subtitle': 'This week',
                    },
                    'usage_allowed': False,
                    'usage_limit_dialog': {
                        'body': 'Day usages exceeded',
                        'title': 'Usages limit exceeded',
                    },
                },
                'poi': {
                    'start_screen_usages': {'title': '', 'subtitle': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'body': '', 'title': ''},
                },
            },
        },
    }


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
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
        'disabled_session.sql',
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
async def test_stop_disabled(
        taxi_reposition_api, handler_uri, pgsql, mockserver, now,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.602429, 55.759690)

    headers = dict(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-Driver-Profile-Id'] = '888'
    response = await taxi_reposition_api.post(handler_uri, headers=headers)

    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'state_etag': '"2Q5xmbmQijboKM7W"',
        'state': {
            'state': {'status': 'no_state'},
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
    }

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
            'active': False,
            'point_id': 101,
            'start': datetime(2018, 10, 11, 16, 1, 11, 540859),
            'end': datetime(2018, 10, 15, 18, 18, 46),
            'completed': False,
            'driver_id': '(dbid777,888)',
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
            'driver_id_id': 1,
            'occured_at': datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['poi'],
            'extra_data': {
                'session_id': 'q2VolejRRPejNmGQ',
                'status': 'no_state',
                'state_id': 'q2VolejRRPejNmGQ_no_state',
                'disable_reason': 'immobility',
                'source_zones': [],
                'destination_zones': [],
                'stop_zones': [],
            },
        },
    ]


@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
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
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('exp_zone', ['cao', 'moscow'])
@pytest.mark.parametrize('exp_reason', ['client_stop', '__default__'])
async def test_stop_feedback(
        taxi_reposition_api,
        handler_uri,
        pgsql,
        mockserver,
        now,
        experiments3,
        exp_zone,
        exp_reason,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_driver_position(request):
        return build_driver_position_response(37.617664, 55.752121)

    experiments3.add_config(
        name='reposition_api_show_feedback_panel',
        consumers=['reposition-api/feedback-panel'],
        match={
            'consumers': [{'name': 'reposition-api/feedback-panel'}],
            'predicate': {'type': 'true', 'init': {}},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_type': 'string',
                                    'arg_name': 'driver_profile_id',
                                    'value': 'uuid',
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_type': 'string',
                                    'arg_name': 'reposition_mode',
                                    'value': 'poi',
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_type': 'string',
                                    'arg_name': 'zone_name',
                                    'value': exp_zone,
                                },
                            },
                        ],
                    },
                },
                'value': {
                    'choices_by_disable_reason': {
                        exp_reason: {
                            'items': [
                                {
                                    'score': 1,
                                    'is_choice_required': False,
                                    'is_comment_required': False,
                                    'is_comment_available': False,
                                    'choices': ['no_orders'],
                                },
                            ],
                        },
                    },
                },
            },
        ],
        default_value={'choices_by_disable_reason': {}},
    )

    response = await taxi_reposition_api.post(
        handler_uri, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'state_etag': '"2Q5xmbmQijboKM7W"',
        'state': {
            'state': {
                'status': 'no_state',
                'session_score': {
                    'items': [
                        {
                            'choices': [
                                {
                                    'name': 'no_orders',
                                    'title': 'Got no orders',
                                },
                            ],
                            'custom_comment': {
                                'is_available': False,
                                'is_required': False,
                            },
                            'is_choice_required': False,
                            'score': 1,
                        },
                    ],
                    'session_id': 'QZOpnelYYgaKBzyV',
                    'title': 'Rate your poi trip',
                },
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
    }

    expected_tags_rows = [
        {
            'driver_id': '(dbid777,uuid)',
            'udid': None,
            'confirmation_token': 'reposition/QZOpnelYYgaKBzyV_remove',
            'merge_policy': 'remove',
            'tags': ['reposition_poi'],
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
