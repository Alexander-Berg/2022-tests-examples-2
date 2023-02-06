# pylint: disable=C5521, W0621
import pytest

from .utils import select_named
from .utils import select_table


@pytest.mark.now('2019-09-01T00:00:00')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'sessions.sql'],
)
async def test_sessions(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-sessions'},
        )
    ).status_code == 200

    rows = select_table('state.sessions', 'session_id', pgsql['reposition'])
    assert len(rows) == 1
    assert rows[0][0] == 2003
    rows = select_table(
        'state.archive_sessions', 'session_id', pgsql['reposition'],
    )
    assert len(rows) == 5
    assert rows[0][0] == 2001
    assert rows[1][0] == 2002
    assert rows[2][0] == 2004
    assert rows[3][0] == 2005
    assert rows[4][0] == 2006

    rows = select_table('state.events', 'session_id', pgsql['reposition'])
    assert len(rows) == 1
    assert rows[0][0] == 2003

    rows = select_table(
        'state.sessions_rule_violations', 'session_id', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0][0] == 2003


@pytest.mark.now('2018-10-16T16:03:11')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'archive_sessions.sql'])
async def test_archive_sessions(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-archive-sessions'},
        )
    ).status_code == 200

    rows = select_named(
        'SELECT session_id FROM state.archive_sessions ORDER BY session_id',
        pgsql['reposition'],
    )
    assert rows == [
        {'session_id': 1201},
        {'session_id': 1301},
        {'session_id': 1401},
        {'session_id': 2301},
        {'session_id': 2401},
    ]


@pytest.mark.now('2019-09-01T00:00:00')
@pytest.mark.pgsql('reposition', files=['sessions_history_operations.sql'])
async def test_sessions_history_operations(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron',
            json={'task_name': 'pg-cleaner-sessions-history-operations'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT operation_id
        FROM state.sessions_history_operations
        ORDER BY operation_id
        """,
        pgsql['reposition'],
    )

    assert rows == [{'operation_id': 'operation_id_0'}]


@pytest.mark.now('2018-10-16T16:03:11')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'points.sql'],
)
async def test_points(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-points'},
        )
    ).status_code == 200

    rows = select_table('settings.points', 'point_id', pgsql['reposition'])
    assert len(rows) == 2
    assert rows[0][0] == 101
    assert rows[1][0] == 102


@pytest.mark.now('2018-10-16T16:03:11')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'saved_points.sql'],
)
async def test_saved_points(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-saved-points'},
        )
    ).status_code == 200

    rows = select_table(
        'settings.saved_points', 'saved_point_id', pgsql['reposition'],
    )
    assert len(rows) == 3
    assert rows[0][0] == 4001
    assert rows[1][0] == 4003
    assert rows[2][0] == 4005


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'offers.sql'],
)
async def test_offers(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-offers'},
        )
    ).status_code == 200

    rows = select_table('state.offers', 'offer_id', pgsql['reposition'])
    assert len(rows) == 3
    assert rows[0][0] == 1001
    assert rows[1][0] == 1002
    assert rows[2][0] == 1004
    rows = select_table('settings.points', 'point_id', pgsql['reposition'])
    assert len(rows) == 2
    assert rows[0][0] == 101
    assert rows[1][0] == 102


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'zone_default.sql',
        'durations.sql',
    ],
)
async def test_durations(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-durations'},
        )
    ).status_code == 200

    rows = select_table(
        'check_rules.duration', 'duration_id', pgsql['reposition'],
    )
    assert len(rows) == 7
    assert rows[0][0] == 1
    assert rows[1][0] == 2
    assert rows[2][0] == 3
    assert rows[3][0] == 4
    assert rows[4][0] == 5
    assert rows[5][0] == 7
    assert rows[6][0] == 8


@pytest.mark.now('2019-09-01T13:00:00')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'reposition_events.sql'],
)
async def test_reposition_events(taxi_reposition_api, pgsql):
    rows = select_table(
        'state.uploading_reposition_events', 'event_id', pgsql['reposition'],
    )
    assert len(rows) == 3
    assert rows[0][0] == 1000  # expected to be deleted as it's been uploaded
    assert rows[1][0] == 1001  # expected to be deleted as it's expired
    assert rows[2][0] == 1002  # expected to be skipped

    assert (
        await taxi_reposition_api.post(
            '/service/cron',
            json={'task_name': 'pg-cleaner-reposition-events'},
        )
    ).status_code == 200

    rows = select_table(
        'state.uploading_reposition_events', 'event_id', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0][0] == 1002  # skipped


@pytest.mark.now('2019-09-01T13:00:00')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'tags.sql'])
async def test_tags(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-tags'},
        )
    ).status_code == 200

    rows = select_table('state.uploading_tags', 'tags_id', pgsql['reposition'])

    assert len(rows) == 1
    assert rows[0][0] == 1002


@pytest.mark.now('2019-09-01T13:00:00')
@pytest.mark.pgsql('reposition', files=['etag_update_requests.sql'])
async def test_etag_update_requests(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron',
            json={'task_name': 'pg-cleaner-etag-update-requests'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT update_request_id
        FROM etag_data.update_requests
        ORDER BY update_request_id
        """,
        pgsql['reposition'],
    )

    assert rows == [{'update_request_id': 1001}]


@pytest.mark.now('2019-09-01T13:00:00')
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'drivers.sql', 'driver_feedback_data.sql'],
)
async def test_driver_feedback_data(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron',
            json={'task_name': 'pg-cleaner-driver-feedback-data'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT session_id
        FROM state.driver_feedback_data
        ORDER BY session_id
        """,
        pgsql['reposition'],
    )

    assert rows == [{'session_id': 1001}]


@pytest.mark.now('2018-10-12T19:00:01')
@pytest.mark.config(
    REPOSITION_API_PG_CLEANER={
        '__default__': {
            'enabled': True,
            'timeout_ms': {'__default__': 500},
            'period_s': 2000,
            'age_m': 60,
            'limit': 1000,
        },
        'sessions': {
            'enabled': True,
            'timeout_ms': {'__default__': 500},
            'period_s': 2000,
            'age_m': 60,
            'limit': 1,
        },
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'sessions.sql'],
)
async def test_configs_1h_1(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-sessions'},
        )
    ).status_code == 200

    rows = select_table('state.sessions', 'session_id', pgsql['reposition'])
    assert len(rows) == 5
    assert rows[0][0] == 2002
    assert rows[1][0] == 2003
    assert rows[2][0] == 2004
    assert rows[3][0] == 2005
    assert rows[4][0] == 2006


@pytest.mark.now('2018-10-12T19:00:01')
@pytest.mark.config(
    REPOSITION_API_PG_CLEANER={
        '__default__': {
            'enabled': True,
            'timeout_ms': {'__default__': 500},
            'period_s': 2000,
            'age_m': 60,
            'limit': 1000,
        },
        'sessions': {
            'enabled': True,
            'timeout_ms': {'__default__': 500},
            'period_s': 2000,
            'age_m': 120,
            'limit': 5,
        },
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'sessions.sql'],
)
async def test_configs_2h_5(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'pg-cleaner-sessions'},
        )
    ).status_code == 200

    rows = select_table('state.sessions', 'session_id', pgsql['reposition'])
    assert len(rows) == 2
    assert rows[0][0] == 2003
    assert rows[1][0] == 2006
