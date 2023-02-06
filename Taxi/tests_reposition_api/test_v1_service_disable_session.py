# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name, import-only-modules
from datetime import datetime

import pytest

from .utils import select_named


async def test_disable_non_existing(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/service/disable_session',
        json={'session_id': 1},
    )

    assert response.status_code == 200


@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'mode_poi.sql',
        'drivers.sql',
        'sessions.sql',
        'home_bonus.sql',
    ],
)
@pytest.mark.now('2018-11-26T12:00:00+0000')
async def test_disable(taxi_reposition_api, pgsql, mockserver, testpoint):
    sessions_query = 'SELECT session_id ' 'FROM state.sessions'
    sessions_rows = select_named(sessions_query, pgsql['reposition'])
    for session_row in sessions_rows:
        session_id = session_row['session_id']
        response = await taxi_reposition_api.post(
            '/internal/reposition-api/v1/service/disable_session',
            json={'session_id': session_id},
        )

        assert response.json() == {}
        assert response.status_code == 200

        query = (
            'SELECT active FROM state.sessions '
            'WHERE session_id = ' + str(session_id)
        )

        rows = select_named(query, pgsql['reposition'])
        assert len(rows) == 1
        assert len(rows[0]) == 1
        assert not rows[0]['active']

    count = select_named(
        'SELECT count(*) FROM state.uploading_tags', pgsql['reposition'],
    )[0]['count']
    assert count == 0


@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'mode_poi.sql',
        'drivers.sql',
        'sessions.sql',
        'home_bonus.sql',
    ],
)
@pytest.mark.now('2018-11-26T12:00:00+0000')
@pytest.mark.parametrize(
    'reason,db_reason',
    [
        ('arrival', 'Arrival'),
        ('antisurge_arrival', 'AntiSurgeArrival'),
        ('surge_arrival', 'SurgeArrival'),
        ('immobility', 'Immobility'),
        ('out_of_area', 'OutOfArea'),
        ('route', 'Route'),
        ('transporting_arrival', 'TransportingArrival'),
        ('nonexistent', ''),
        ('conditional', 'Conditional'),
    ],
)
async def test_disable_with_reason(
        taxi_reposition_api,
        pgsql,
        mockserver,
        experiments3,
        reason,
        db_reason,
        testpoint,
):
    sessions_query = 'SELECT session_id ' 'FROM state.sessions'
    sessions_rows = select_named(sessions_query, pgsql['reposition'])
    for session_row in sessions_rows:
        session_id = session_row['session_id']
        response = await taxi_reposition_api.post(
            '/internal/reposition-api/v1/service/disable_session',
            json={'session_id': session_id, 'reason': reason},
        )

        if reason == 'nonexistent':
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            assert response.json() == {}

            query = (
                'SELECT active, disable_reason FROM state.sessions '
                'WHERE session_id = ' + str(session_id)
            )

            rows = select_named(query, pgsql['reposition'])
            assert len(rows) == 1
            assert len(rows[0]) == 2
            assert not rows[0]['active']

            if session_id in (1001, 1002):
                assert rows[0]['disable_reason'] == db_reason

    count = select_named(
        'SELECT count(*) FROM state.uploading_tags', pgsql['reposition'],
    )[0]['count']
    assert count == 0


@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'drivers.sql',
        'mode_home.sql',
        'submodes_home.sql',
        'test.sql',
    ],
)
@pytest.mark.now('2018-11-26T12:00:00+0000')
async def test_etag_data_write(
        taxi_reposition_api, mockserver, taxi_config, pgsql, load, testpoint,
):
    session_ids_list = ['1502', '1505', '1506', '1508']

    for session_id in session_ids_list:
        resp = await taxi_reposition_api.post(
            '/internal/reposition-api/v1/service/disable_session',
            json={'session_id': int(session_id)},
        )
        assert resp.status_code == 200

    rows = select_named(
        """
        SELECT driver_id, valid_since, data FROM etag_data.states
        INNER JOIN settings.driver_ids
        ON states.driver_id_id = driver_ids.driver_id_id
        ORDER BY driver_id, revision
        """,
        pgsql['reposition'],
    )

    assert rows == [
        {
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 26, 12, 0),
            'data': {
                'state': {
                    'status': 'disabled',
                    'session_id': 'O3GWpmbkErezJn4K',
                    'state_id': 'O3GWpmbkErezJn4K_disabled',
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 26, 21, 0),
            'data': {
                'state': {
                    'status': 'disabled',
                    'session_id': 'O3GWpmbkErezJn4K',
                    'state_id': 'O3GWpmbkErezJn4K_disabled',
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 12, 2, 21, 0),
            'data': {
                'state': {
                    'status': 'disabled',
                    'session_id': 'O3GWpmbkErezJn4K',
                    'state_id': 'O3GWpmbkErezJn4K_disabled',
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid,uuid)',
            'valid_since': datetime(2018, 11, 26, 12, 0),
            'data': {
                'state': {
                    'session_id': 'VvJ4openKYa7Az1X',
                    'state_id': 'VvJ4openKYa7Az1X_disabled',
                    'status': 'disabled',
                    'client_attributes': {'dead10cc': 'deadbeef'},
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid,uuid)',
            'valid_since': datetime(2018, 11, 26, 21, 0),
            'data': {
                'state': {
                    'session_id': 'VvJ4openKYa7Az1X',
                    'state_id': 'VvJ4openKYa7Az1X_disabled',
                    'status': 'disabled',
                    'client_attributes': {'dead10cc': 'deadbeef'},
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid,uuid)',
            'valid_since': datetime(2018, 12, 2, 21, 0),
            'data': {
                'state': {
                    'session_id': 'VvJ4openKYa7Az1X',
                    'state_id': 'VvJ4openKYa7Az1X_disabled',
                    'status': 'disabled',
                    'client_attributes': {'dead10cc': 'deadbeef'},
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid,uuid1)',
            'valid_since': datetime(2018, 11, 26, 12, 0),
            'data': {
                'state': {
                    'session_id': 'QABWJxboLAdgwOL0',
                    'state_id': 'QABWJxboLAdgwOL0_disabled',
                    'status': 'disabled',
                    'client_attributes': {'dead10cc': 'deadbeef'},
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid,uuid1)',
            'valid_since': datetime(2018, 11, 26, 21, 0),
            'data': {
                'state': {
                    'session_id': 'QABWJxboLAdgwOL0',
                    'state_id': 'QABWJxboLAdgwOL0_disabled',
                    'status': 'disabled',
                    'client_attributes': {'dead10cc': 'deadbeef'},
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid,uuid1)',
            'valid_since': datetime(2018, 12, 2, 21, 0),
            'data': {
                'state': {
                    'session_id': 'QABWJxboLAdgwOL0',
                    'state_id': 'QABWJxboLAdgwOL0_disabled',
                    'status': 'disabled',
                    'client_attributes': {'dead10cc': 'deadbeef'},
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 11, 26, 12, 0),
            'data': {
                'state': {
                    'session_id': 'M7Vl4zbqNDdprOZq',
                    'state_id': 'M7Vl4zbqNDdprOZq_disabled',
                    'status': 'disabled',
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 11, 27, 0, 0),
            'data': {
                'state': {
                    'session_id': 'M7Vl4zbqNDdprOZq',
                    'state_id': 'M7Vl4zbqNDdprOZq_disabled',
                    'status': 'disabled',
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
        {
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 12, 3, 0, 0),
            'data': {
                'state': {
                    'session_id': 'M7Vl4zbqNDdprOZq',
                    'state_id': 'M7Vl4zbqNDdprOZq_disabled',
                    'status': 'disabled',
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
                    'surge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'title': '', 'body': ''},
                    },
                },
            },
        },
    ]
