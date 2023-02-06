import contextlib

import pytest


def get_call_status_ids(db):
    cursor = db.cursor()
    cursor.execute(f'SELECT call_id FROM callcenter_stats.call_status')
    return {row[0] for row in cursor}


def get_agent_ids(db):
    cursor = db.cursor()
    cursor.execute(
        f'SELECT agent_id FROM callcenter_stats.operator_talking_status',
    )
    return {row[0] for row in cursor}


CALL_IDS = {
    'dm4',
    'dm2',
    'dq4',
    'dq2',
    'dt4',
    'dt2',
    'hm4',
    'hm2',
    'hq4',
    'hq2',
    'ht4',
    'ht2',
}

AGENT_IDS = {'dt4', 'dt2', 'ht4', 'ht2'}


@pytest.mark.pgsql(
    'callcenter_stats',
    files=['insert_call_status.sql', 'insert_operator_talking_status.sql'],
)
@pytest.mark.parametrize(
    ('expected_call_ids_left', 'expected_agent_ids_left'),
    [
        pytest.param(
            CALL_IDS,
            AGENT_IDS,
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {},
                    },
                ),
            ],
            id=f'rules turned off',
        ),
        pytest.param(
            CALL_IDS,
            AGENT_IDS,
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            '__default__': {
                                'talking_call_ttl_sec': 0,  # endless
                                'queued_call_ttl_sec': 5 * 3600,  # 5 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for endless ttl',
        ),
        pytest.param(
            CALL_IDS - {'dm4', 'dq4'},
            AGENT_IDS,
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=3h, disp only, queued only',
        ),
        pytest.param(
            CALL_IDS - {'dm4', 'dq4', 'dt4'},
            AGENT_IDS - {'dt4'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=3h, disp only',
        ),
        pytest.param(
            CALL_IDS - {'dm4', 'dq4', 'dt4', 'dm2', 'dq2', 'dt2'},
            AGENT_IDS - {'dt4', 'dt2'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3600,  # 1 hour
                                'queued_call_ttl_sec': 3600,  # 1 hour
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=1h, disp only',
        ),
        pytest.param(
            CALL_IDS
            - {
                'dm4',
                'dq4',
                'dt4',
                'dm2',
                'dq2',
                'hm4',
                'hq4',
                'ht4',
                'hm2',
                'hq2',
                'ht2',
            },
            AGENT_IDS - {'dt4', 'ht4', 'ht2'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                # __default__ will be used = 1 hour
                            },
                            '__default__': {
                                'talking_call_ttl_sec': 3600,  # 1 hours
                                'queued_call_ttl_sec': 3600,  # 1 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for different queues',
        ),
        pytest.param(
            CALL_IDS - {'dm4', 'dq4', 'dt4', 'hm4', 'hq4', 'ht4'},
            AGENT_IDS - {'dt4', 'ht4'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            '__default__': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for __default__ only',
        ),
    ],
)
async def test_pg_cleaner_calls(
        taxi_callcenter_stats,
        pgsql,
        expected_call_ids_left,
        expected_agent_ids_left,
):
    db = pgsql['callcenter_stats']

    await taxi_callcenter_stats.run_periodic_task('callcenter-stats-cleaner')

    assert get_call_status_ids(db) == expected_call_ids_left
    assert get_agent_ids(db) == expected_agent_ids_left


@contextlib.contextmanager
def autocommit_false(db):
    autocommit = db.conn.autocommit
    db.conn.set_session(autocommit=False)

    yield

    db.conn.set_session(autocommit=autocommit)


@pytest.mark.pgsql(
    'callcenter_stats', files=['insert_call_status_for_lock.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_CLEANER_SETTINGS={
        'period_sec': 60,
        'call_ttls_map': {
            'disp': {'queued_call_ttl_sec': 4 * 3600},  # 4 hours
        },
    },
)
async def test_pg_cleaner_skip_locked(taxi_callcenter_stats, pgsql):
    db = pgsql['callcenter_stats']

    with autocommit_false(db):
        cursor = db.conn.cursor()
        # Lock call_id = 1 (designed for deletion)
        cursor.execute(
            f'SELECT * FROM callcenter_stats.call_status'
            f' WHERE call_id = \'1\' FOR UPDATE',
        )
        await taxi_callcenter_stats.run_periodic_task(
            'callcenter-stats-cleaner',
        )
        cursor.close()
        db.conn.commit()

    # if another transaction locks a row, cleaner skips that row
    # only call_id = 2 was deleted
    assert get_call_status_ids(db) == {'1', '3'}

    await taxi_callcenter_stats.run_periodic_task('callcenter-stats-cleaner')

    # now when no transaction holds row id=1, it's deleted
    assert get_call_status_ids(db) == {'3'}


@pytest.mark.pgsql(
    'callcenter_stats', files=['insert_call_status_for_limit.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_CLEANER_SETTINGS={
        'period_sec': 60,
        'call_ttls_map': {
            'disp': {'queued_call_ttl_sec': 4 * 3600},  # 4 hours
        },
    },
)
# chunk-size is 10
async def test_pg_cleaner_calls_limit(taxi_callcenter_stats, pgsql):
    db = pgsql['callcenter_stats']

    await taxi_callcenter_stats.run_periodic_task('callcenter-stats-cleaner')

    assert len(get_call_status_ids(db)) == 1
