# pylint: disable=import-only-modules,too-many-lines
import datetime

import pytest

from .utils import select_named


@pytest.mark.parametrize(
    'violations',
    [
        'arrived',
        'anti_surge_arrival',
        'session_timeout',
        'immobility',
        'immobility_warning',
        'out_of_area',
        'out_of_area_warning',
        'route',
        'route_warning',
    ],
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
@pytest.mark.now('2018-09-01T07:00:00+0000')
async def test_rule_violations(taxi_reposition_api, pgsql, violations):
    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {
                    'type': violations,
                    'valid_until': '2018-09-01T11:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 200
    rows = select_named(
        'select * from etag_data.states order by valid_since',
        pgsql['reposition'],
    )

    assert rows == [
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': True,
            'revision': 1,
            'valid_since': datetime.datetime(2018, 9, 1, 7, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 2,
            'valid_since': datetime.datetime(2018, 9, 1, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 3,
            'valid_since': datetime.datetime(2018, 9, 2, 21, 0),
        },
    ]

    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {
                    'type': violations,
                    'valid_until': '2018-09-01T11:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 200
    rows = select_named(
        'select * from etag_data.states order by valid_since',
        pgsql['reposition'],
    )

    assert rows == [
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': True,
            'revision': 4,
            'valid_since': datetime.datetime(2018, 9, 1, 7, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 5,
            'valid_since': datetime.datetime(2018, 9, 1, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violations
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 6,
            'valid_since': datetime.datetime(2018, 9, 2, 21, 0),
        },
    ]


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
@pytest.mark.now('2018-09-01T07:00:00+0000')
async def test_rule_violations_twice(taxi_reposition_api, pgsql):
    violation = 'immobility'
    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {'type': violation, 'valid_until': '2018-09-01T11:00:00+0300'},
            ],
        },
    )

    assert response.status_code == 200
    rows = select_named(
        'select * from etag_data.states order by valid_since',
        pgsql['reposition'],
    )

    assert rows == [
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': True,
            'revision': 1,
            'valid_since': datetime.datetime(2018, 9, 1, 7, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 2,
            'valid_since': datetime.datetime(2018, 9, 1, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 3,
            'valid_since': datetime.datetime(2018, 9, 2, 21, 0),
        },
    ]

    violation = 'arrived'
    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {'type': violation, 'valid_until': '2018-09-01T11:00:00+0300'},
            ],
        },
    )

    assert response.status_code == 200
    rows = select_named(
        'select * from etag_data.states order by valid_since',
        pgsql['reposition'],
    )

    assert rows == [
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': True,
            'revision': 4,
            'valid_since': datetime.datetime(2018, 9, 1, 7, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 5,
            'valid_since': datetime.datetime(2018, 9, 1, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 6,
            'valid_since': datetime.datetime(2018, 9, 2, 21, 0),
        },
    ]


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
@pytest.mark.now('2018-09-01T07:00:00+0000')
async def test_rule_violations_update_valid_until(taxi_reposition_api, pgsql):
    violation = 'arrived'

    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {'type': violation, 'valid_until': '2018-09-01T11:00:00+0300'},
            ],
        },
    )

    assert response.status_code == 200
    rows = select_named('select * from etag_data.states', pgsql['reposition'])

    assert rows == [
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': True,
            'revision': 1,
            'valid_since': datetime.datetime(2018, 9, 1, 7, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 2,
            'valid_since': datetime.datetime(2018, 9, 1, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:00:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 3,
            'valid_since': datetime.datetime(2018, 9, 2, 21, 0),
        },
    ]

    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {'type': violation, 'valid_until': '2018-09-01T11:02:00+0300'},
            ],
        },
    )

    assert response.status_code == 200
    rows = select_named('select * from etag_data.states', pgsql['reposition'])

    assert rows == [
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:02:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': True,
            'revision': 4,
            'valid_since': datetime.datetime(2018, 9, 1, 7, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:02:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 5,
            'valid_since': datetime.datetime(2018, 9, 1, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {'dead10cc': 'deadbeef'},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': 'q2VolejRRPejNmGQ',
                        'point': [30.0, 60.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [],
                    'rule_violations': [
                        {
                            'expires_at': '2018-09-01T08:02:00+00:00',
                            'message': {
                                'subtitle': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                                'title': (
                                    '{"mode_tanker_key":"home","tanker_key":"'
                                    + violation
                                    + '"}'
                                ),
                            },
                        },
                    ],
                    'session_id': 'q2VolejR9vejNmGQ',
                    'started_at': '2017-11-19T16:47:54.721+00:00',
                    'state_id': 'q2VolejR9vejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'is_sequence_start': False,
            'revision': 6,
            'valid_since': datetime.datetime(2018, 9, 2, 21, 0),
        },
    ]


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
@pytest.mark.now('2018-09-01T07:00:00+0000')
async def test_add_bad_enum(taxi_reposition_api):
    response = await taxi_reposition_api.put(
        '/v1/service/session/rule_violations',
        json={
            'session_id': 3001,
            'violations': [
                {'type': 'kek', 'valid_until': '2018-09-01T11:00:00+0300'},
            ],
        },
    )

    assert response.status_code == 400
