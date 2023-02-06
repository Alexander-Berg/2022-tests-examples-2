# pylint: disable=C5521
import datetime

import pytest

from .utils import select_named
from .utils import select_table


@pytest.mark.parametrize(
    'event,dbevent',
    [
        ('arrived', 'Arrived'),
        ('session_timeout', 'SessionTimeout'),
        ('immobility', 'Immobility'),
        ('out_of_area', 'OutOfArea'),
        ('route', 'Route'),
        ('order_in_progress', 'OrderInProgress'),
        ('order_finished', 'OrderFinished'),
        ('surge_arrived', 'SurgeArrived'),
        ('arrived_by_antisurge', 'AntiSurge'),
    ],
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
async def test_add_event(taxi_reposition_api, pgsql, event, dbevent):
    response = await taxi_reposition_api.post(
        '/v1/service/session/add_events',
        json={
            'events': [
                {
                    'session_id': 3001,
                    'type': event,
                    'occurred_at': '2018-09-01T11:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'results': [{'has_failed': False}]}

    rows = select_table('state.events', 'session_id', pgsql['reposition'])
    assert rows[0][0] == 3001
    assert rows[0][1] == dbevent
    assert rows[0][2] == datetime.datetime(2018, 9, 1, 8, 0)


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
async def test_add_event_twice(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.post(
        '/v1/service/session/add_events',
        json={
            'events': [
                {
                    'session_id': 3001,
                    'type': 'arrived',
                    'occurred_at': '2018-09-01T11:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'results': [{'has_failed': False}]}

    rows = select_table('state.events', 'session_id', pgsql['reposition'])
    assert rows[0][0] == 3001
    assert rows[0][1] == 'Arrived'
    assert rows[0][2] == datetime.datetime(2018, 9, 1, 8, 0)

    response = await taxi_reposition_api.post(
        '/v1/service/session/add_events',
        json={
            'events': [
                {
                    'session_id': 3001,
                    'type': 'arrived',
                    'occurred_at': '2018-09-01T11:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'results': [{'has_failed': False}]}

    rows = select_table('state.events', 'session_id', pgsql['reposition'])
    assert rows[0][0] == 3001
    assert rows[0][1] == 'Arrived'
    assert rows[0][2] == datetime.datetime(2018, 9, 1, 8, 0)


@pytest.mark.parametrize(
    'event,db_event',
    [
        ('order_finished', 'OrderFinished'),
        ('transporting_arrival_end', 'TransportingArrivalEnd'),
    ],
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'deferred_bonus.sql'],
)
async def test_order_finished(taxi_reposition_api, pgsql, event, db_event):
    def _fetch_events():
        return select_named(
            'SELECT session_id, event, occured_at FROM state.events',
            pgsql['reposition'],
        )

    def _fetch_sessions():
        return select_named(
            'SELECT session_id, active, completed, bonus_until '
            'FROM state.sessions',
            pgsql['reposition'],
        )

    def _fetch_states():
        return select_named(
            """
            SELECT
                driver_id_id,
                valid_since,
                data
            FROM
                etag_data.states
            ORDER BY
                valid_since
            """,
            pgsql['reposition'],
        )

    expected_events = [
        {
            'session_id': 3001,
            'event': db_event,
            'occured_at': datetime.datetime(2017, 11, 19, 17, 30, 0),
        },
    ]

    expected_sessions = [
        {
            'session_id': 3001,
            'active': False,
            'completed': True,
            'bonus_until': datetime.datetime(2017, 11, 19, 22, 0),
        },
    ]

    expected_states = [
        {
            'data': {
                'state': {
                    'bonus': {
                        'client_attributes': {'dead10cc': 'deadbeef'},
                        'expires_at': '2017-11-19T17:40:00+00:00',
                        'headline': {
                            'subtitle': (
                                '{"mode_tanker_key":"home",'
                                + '"tanker_key":"bonus.tanker"}'
                            ),
                            'title': (
                                '{"mode_tanker_key":"home",'
                                + '"tanker_key":"bonus.tanker"}'
                            ),
                        },
                        'icon_id': 'image',
                        'mode_id': 'home',
                        'session_id': 'q2VolejR9vejNmGQ',
                        'started_at': '2017-11-19T17:30:00+00:00',
                        'subline': {
                            'subtitle': (
                                '{"mode_tanker_key":"home",'
                                + '"tanker_key":"bonus.tanker"}'
                            ),
                            'title': (
                                '{"mode_tanker_key":"home",'
                                + '"tanker_key":"bonus.tanker"}'
                            ),
                        },
                    },
                    'state_id': 'q2VolejR9vejNmGQ_bonus',
                    'status': 'bonus',
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
            'valid_since': datetime.datetime(2017, 11, 19, 17, 30),
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'valid_since': datetime.datetime(2017, 11, 19, 17, 40),
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'home': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id_id': 5,
            'valid_since': datetime.datetime(2017, 11, 19, 21, 0),
        },
    ]

    assert _fetch_sessions() == expected_sessions

    response = await taxi_reposition_api.post(
        '/v1/service/session/add_events',
        json={
            'events': [
                {
                    'session_id': 3001,
                    'type': event,
                    'occurred_at': '2017-11-19T17:30:00+0000',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'results': [{'has_failed': False}]}

    assert _fetch_events() == expected_events

    if event == 'transporting_arrival_end':
        expected_sessions[0]['bonus_until'] = datetime.datetime(
            2017, 11, 19, 17, 40, 0,
        )

        assert _fetch_states() == expected_states

    assert _fetch_sessions() == expected_sessions


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'bulk.sql'],
)
async def test_bulk(taxi_reposition_api, pgsql):
    def _fetch_events():
        return select_named(
            """
            SELECT
                session_id,
                event,
                occured_at
            FROM
                state.events
            ORDER BY
                session_id,
                occured_at,
                event
            """,
            pgsql['reposition'],
        )

    def _fetch_sessions():
        return select_named(
            """
            SELECT
                session_id,
                active,
                completed,
                bonus_until
            FROM
                state.sessions
            ORDER BY
                session_id
            """,
            pgsql['reposition'],
        )

    expected_events = [
        {
            'session_id': 3001,
            'event': 'Arrived',
            'occured_at': datetime.datetime(2017, 11, 19, 17, 30, 0),
        },
        {
            'session_id': 3002,
            'event': 'OrderFinished',
            'occured_at': datetime.datetime(2017, 11, 19, 17, 30, 0),
        },
        {
            'session_id': 3002,
            'event': 'TransportingArrivalEnd',
            'occured_at': datetime.datetime(2017, 11, 19, 17, 30, 0),
        },
        {
            'session_id': 3003,
            'event': 'OrderFinished',
            'occured_at': datetime.datetime(2017, 11, 19, 17, 30, 0),
        },
    ]

    expected_sessions = [
        {
            'session_id': 3001,
            'active': True,
            'completed': False,
            'bonus_until': None,
        },
        {
            'session_id': 3002,
            'active': False,
            'completed': True,
            'bonus_until': datetime.datetime(2017, 11, 19, 22, 0),
        },
        {
            'session_id': 3003,
            'active': True,
            'completed': False,
            'bonus_until': None,
        },
    ]

    assert _fetch_sessions() == expected_sessions

    response = await taxi_reposition_api.post(
        '/v1/service/session/add_events',
        json={
            'events': [
                {
                    'session_id': 3000,  # expired
                    'type': 'arrived',
                    'occurred_at': '2017-11-19T17:30:00+0000',
                },
                {
                    'session_id': 3001,
                    'type': 'arrived',
                    'occurred_at': '2017-11-19T17:30:00+0000',
                },
                {
                    'session_id': 3002,
                    'type': 'order_finished',
                    'occurred_at': '2017-11-19T17:30:00+0000',
                },
                {
                    'session_id': 3002,
                    'type': 'transporting_arrival_end',
                    'occurred_at': '2017-11-19T17:30:00+0000',
                },
                {
                    'session_id': 3003,
                    'type': 'order_finished',
                    'occurred_at': '2017-11-19T17:30:00+0000',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'results': [
            {'has_failed': False},
            {'has_failed': False},
            {'has_failed': False},
            {'has_failed': False},
            {'has_failed': False},
        ],
    }

    expected_sessions[1]['bonus_until'] = datetime.datetime(
        2017, 11, 19, 17, 40,
    )

    assert _fetch_events() == expected_events
    assert _fetch_sessions() == expected_sessions


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'simple.sql'],
)
async def test_add_bad_enum(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/session/add_events',
        json={
            'events': [
                {
                    'session_id': 3001,
                    'type': 'kek',
                    'occurred_at': '2018-09-01T11:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 400
